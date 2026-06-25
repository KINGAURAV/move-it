"""
Move-It — Streamlit dashboard.

Flow: Start Simulation -> POST /ingest -> Kafka -> consumer -> ML predict -> UI
"""

from __future__ import annotations

import os
import random
import sys
import threading
import time
import builtins
from datetime import timedelta
from pathlib import Path

import joblib
import pandas as pd
import requests
import streamlit as st
from kafka import KafkaConsumer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent
DATASET_PATH = ROOT_DIR / "00_dataset" / "cropdata.csv"
LEGACY_STARTER_KIT = ROOT_DIR / "04_starter-kit"
BUNDLE_PATH = APP_DIR / "model_bundle.joblib"
MODEL_PATH = APP_DIR / "model.joblib"
if not BUNDLE_PATH.exists():
    BUNDLE_PATH = LEGACY_STARTER_KIT / "model_bundle.joblib"
if not MODEL_PATH.exists():
    MODEL_PATH = LEGACY_STARTER_KIT / "model.joblib"

sys.path.insert(0, str(APP_DIR))
from kafka_config import KAFKA_BROKER, KAFKA_TOPIC, consumer_config

LOCAL_INGEST_URL = "http://127.0.0.1:5000/ingest"


def resolve_ingest_url(raw: str | None = None) -> str:
    url = (raw or os.getenv("INGEST_API_URL", LOCAL_INGEST_URL)).strip()
    lowered = url.lower()
    if "proxy" in lowered or (
        lowered.startswith("https://") and "localhost" not in lowered and "127.0.0.1" not in lowered
    ):
        return LOCAL_INGEST_URL
    return url


def parse_ingest_response(resp: requests.Response, payload: dict) -> dict:
    if resp.status_code != 200:
        raise ValueError(f"Ingest failed ({resp.status_code}): {resp.text[:300]}")
    if "application/json" not in resp.headers.get("Content-Type", ""):
        return payload
    try:
        return resp.json().get("data", payload)
    except ValueError:
        return payload

DEFAULT_CATEGORICALS = {
    "crop ID": "Wheat",
    "soil_type": "Black Soil",
    "Seedling Stage": "Germination",
}

COLUMNS = ["timestamp", "temp", "humidity", "MOI", "prediction", "probability", "action"]

# Process-wide state survives Streamlit reruns and module reloads; threads must not touch st.session_state.
def _shared_state() -> dict:
    if not hasattr(builtins, "_moveit_shared_state"):
        builtins._moveit_shared_state = {
            "simulating": threading.Event(),
            "rows_lock": threading.Lock(),
            "prediction_buffer": [],
            "kafka_status": {
                "connected": False,
                "error": None,
                "messages": 0,
                "last_prediction_error": None,
            },
            "seen_keys": set(),
            "seen_lock": threading.Lock(),
            "state_lock": threading.Lock(),
            "kafka_started": False,
        }
    return builtins._moveit_shared_state


_SHARED = _shared_state()
_simulating = _SHARED["simulating"]
_kafka_status = _SHARED["kafka_status"]
_seen_keys = _SHARED["seen_keys"]
_seen_lock = _SHARED["seen_lock"]
_state_lock = _SHARED["state_lock"]


CAT_COLS = list(DEFAULT_CATEGORICALS.keys())
NUM_COLS = ["MOI", "temp", "humidity"]


def _encode_categoricals(df: pd.DataFrame, cat_cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in cat_cols:
        out[col] = out[col].astype("category")
    return pd.get_dummies(out, columns=cat_cols, drop_first=True)


def _train_model_from_csv(csv_path: Path) -> dict:
    raw = pd.read_csv(csv_path)
    cat_cols = list(raw.select_dtypes(include=["object"]).columns)

    df = _encode_categoricals(raw, cat_cols)
    df = df[df["result"] != 2]

    scaler = StandardScaler()
    df[NUM_COLS] = scaler.fit_transform(df[NUM_COLS])

    feature_columns = [c for c in df.columns if c != "result"]
    model = LogisticRegression(max_iter=10000, random_state=0)
    model.fit(df[feature_columns], df["result"])

    return {
        "model": model,
        "scaler": scaler,
        "feature_columns": feature_columns,
        "cat_cols": cat_cols,
        # Keep a training sample so single-row inference gets the same dummy columns.
        "raw_sample": raw.head(300),
        "source": str(csv_path),
    }


@st.cache_resource
def load_model_bundle() -> dict | None:
    if BUNDLE_PATH.exists():
        bundle = joblib.load(BUNDLE_PATH)
        if {"raw_sample", "cat_cols", "feature_columns"} <= bundle.keys():
            return bundle

    if DATASET_PATH.exists():
        return _train_model_from_csv(DATASET_PATH)

    return None


def _build_feature_row(temp: float, humidity: float, moi: float, bundle: dict) -> pd.DataFrame:
    infer_row = {**DEFAULT_CATEGORICALS, "MOI": moi, "temp": temp, "humidity": humidity}
    infer_df = pd.DataFrame([infer_row])

    sample_cols = bundle["cat_cols"] + NUM_COLS
    combined = pd.concat([bundle["raw_sample"][sample_cols], infer_df], ignore_index=True)

    encoded = _encode_categoricals(combined, bundle["cat_cols"])
    encoded[NUM_COLS] = bundle["scaler"].transform(encoded[NUM_COLS])

    row = encoded.iloc[[-1]].copy()
    for col in bundle["feature_columns"]:
        if col not in row.columns:
            row[col] = 0.0

    features = row[bundle["feature_columns"]]
    if os.getenv("DEBUG_PREDICT"):
        print("feature columns:", len(bundle["feature_columns"]))
        print("built columns:", features.columns.tolist()[:10], "...")
    return features


def predict_irrigation(temp: float, humidity: float, moi: float, bundle: dict) -> tuple[int, float]:
    features = _build_feature_row(temp, humidity, moi, bundle)
    proba = bundle["model"].predict_proba(features)[0]
    classes = list(bundle["model"].classes_)
    irrigate_idx = classes.index(1) if 1 in classes else 1
    probability = float(proba[irrigate_idx])
    prediction = 1 if probability >= 0.5 else 0
    return prediction, probability


def _predict_row(data: dict, bundle: dict) -> dict:
    temp = float(data.get("temp", 0))
    humidity = float(data.get("humidity", 0))
    moi = float(data.get("MOI", 10))

    if os.getenv("DEBUG_PREDICT"):
        print("INPUT DATA:", data)
        print("FEATURES:", temp, humidity, moi)

    prediction, probability = predict_irrigation(temp, humidity, moi, bundle)

    if os.getenv("DEBUG_PREDICT"):
        print("PRED:", prediction, probability)

    action = "Irrigation ON" if prediction == 1 else "Idle"

    row = {
        "timestamp": data.get("timestamp", time.strftime("%H:%M:%S")),
        "temp": temp,
        "humidity": humidity,
        "MOI": moi,
        "prediction": prediction,
        "probability": round(probability, 3),
        "action": action,
    }
    print(f"Predicted: {row}")
    return row


def _append_prediction_row(row: dict) -> None:
    with _SHARED["rows_lock"]:
        _SHARED["prediction_buffer"].append(row)
        _SHARED["prediction_buffer"] = _SHARED["prediction_buffer"][-20:]


def enqueue_prediction(data: dict, bundle: dict, source: str) -> None:
    key = (data.get("timestamp"), float(data.get("temp", 0)), float(data.get("humidity", 0)))
    with _seen_lock:
        if key in _seen_keys:
            return
        _seen_keys.add(key)

    try:
        _append_prediction_row(_predict_row(data, bundle))
        _kafka_status["last_prediction_error"] = None
        print(f"Queued prediction from {source}")
    except Exception as exc:
        _kafka_status["last_prediction_error"] = str(exc)
        print(f"Prediction failed ({source}): {exc}")


def kafka_consumer_worker(bundle: dict) -> None:
    while True:
        consumer = None
        try:
            consumer = KafkaConsumer(**consumer_config())
            consumer.subscribe([KAFKA_TOPIC])
            _kafka_status["connected"] = True
            _kafka_status["error"] = None
            print(f"Kafka consumer connected to {KAFKA_BROKER} / {KAFKA_TOPIC}")

            while True:
                msg_pack = consumer.poll(timeout_ms=1000)
                for messages in msg_pack.values():
                    for msg in messages:
                        enqueue_prediction(msg.value, bundle, "kafka")
                        _kafka_status["messages"] += 1
        except Exception as exc:
            _kafka_status["connected"] = False
            _kafka_status["error"] = str(exc)
            print(f"Kafka Consumer Error: {exc}. Retrying in 5s...")
            time.sleep(5)
        finally:
            if consumer is not None:
                consumer.close()


def ensure_kafka_consumer(bundle: dict) -> None:
    if _SHARED["kafka_started"]:
        return
    _SHARED["kafka_started"] = True
    threading.Thread(target=kafka_consumer_worker, args=(bundle,), daemon=True).start()


def run_sensor_simulation(bundle: dict, ingest_url: str) -> None:
    print(f"Simulation started -> {ingest_url}")
    while _simulating.is_set():
        payload = {
            "timestamp": time.strftime("%H:%M:%S"),
            "temp": round(random.uniform(22.0, 35.0), 2),
            "humidity": round(random.uniform(40.0, 85.0), 2),
            "MOI": 10,
        }
        try:
            resp = requests.post(ingest_url, json=payload, timeout=5)
            data = parse_ingest_response(resp, payload)
            print(f"Ingest OK: {data}")
            enqueue_prediction(data, bundle, "ingest")
        except Exception as exc:
            print(f"Simulation error: {exc}")
        time.sleep(2)
    print("Simulation stopped.")


def start_simulation(bundle: dict, ingest_url: str) -> None:
    with _state_lock:
        _simulating.set()
        st.session_state.simulation_running = True
        thread = getattr(run_sensor_simulation, "_thread", None)
        if thread is None or not thread.is_alive():
            thread = threading.Thread(
                target=run_sensor_simulation,
                args=(bundle, ingest_url),
                daemon=True,
            )
            thread.start()
            run_sensor_simulation._thread = thread  # type: ignore[attr-defined]


def stop_simulation() -> None:
    _simulating.clear()
    st.session_state.simulation_running = False


def sync_predictions_to_session() -> int:
    """Copy shared prediction buffer into session_state for rendering."""
    with _SHARED["rows_lock"]:
        rows = list(_SHARED["prediction_buffer"])

    if not rows:
        return 0

    st.session_state.prediction_rows = rows
    st.session_state.data_stream = pd.DataFrame(rows)
    return len(rows)


def render_dashboard() -> None:
    df = st.session_state.data_stream

    if df.empty:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Temperature", "-")
        col2.metric("Humidity", "-")
        col3.metric("ML Prediction", "Waiting")
        col4.metric("Action", "-")
        st.info("Start ingestion API, then click **Start Simulation**.")
        return

    latest = df.iloc[-1]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Temperature", f"{latest['temp']} C")
    col2.metric("Humidity", f"{latest['humidity']} %")
    col3.metric(
        "ML Prediction",
        "Irrigate" if latest["prediction"] == 1 else "No irrigation",
        delta=f"p={latest['probability']:.0%}",
    )
    col4.metric("Action", latest["action"])

    st.subheader("Live Telemetry + Predictions")
    display_df = df.sort_index(ascending=False).copy()
    display_df["prediction"] = display_df["prediction"].map({0: "No irrigation", 1: "Irrigate"})
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    c1, c2 = st.columns(2)
    with c1:
        st.line_chart(df.set_index("timestamp")[["humidity"]])
    with c2:
        st.line_chart(df.set_index("timestamp")[["probability"]])


# --- Streamlit UI ---
st.set_page_config(page_title="Smart Greenhouse Monitor", layout="wide")

if "data_stream" not in st.session_state:
    st.session_state.data_stream = pd.DataFrame(columns=COLUMNS)
if "prediction_rows" not in st.session_state:
    st.session_state.prediction_rows = []
if "simulation_running" not in st.session_state:
    st.session_state.simulation_running = _simulating.is_set()
if "ingest_api_url" not in st.session_state:
    st.session_state.ingest_api_url = resolve_ingest_url()

model_bundle = load_model_bundle()
if model_bundle is None:
    st.error(f"Could not load model. Ensure `{DATASET_PATH}` exists.")
    st.stop()

ensure_kafka_consumer(model_bundle)

with st.sidebar.expander("Model debug"):
    st.write(f"Features: {len(model_bundle['feature_columns'])}")
    if st.button("Test prediction (25C, 60% humidity)"):
        try:
            pred, prob = predict_irrigation(25.0, 60.0, 10.0, model_bundle)
            st.success(f"prediction={pred}, probability={prob:.3f}")
        except Exception as exc:
            st.error(str(exc))

st.title("Smart Greenhouse Irrigation Monitor")
st.caption("Simulation -> Ingest API -> Kafka -> ML prediction -> Dashboard")

st.sidebar.header("Control Panel")
st.session_state.ingest_api_url = st.sidebar.text_input(
    "Ingest API URL",
    value=st.session_state.ingest_api_url,
)
ingest_url = resolve_ingest_url(st.session_state.ingest_api_url)
if ingest_url != st.session_state.ingest_api_url:
    st.session_state.ingest_api_url = ingest_url
st.sidebar.code(ingest_url, language="text")

if st.sidebar.button("Start Simulation"):
    if not _simulating.is_set():
        start_simulation(model_bundle, ingest_url)
        st.sidebar.success("Simulation running")
        st.rerun()
    else:
        st.sidebar.warning("Already running")

if st.sidebar.button("Stop Simulation"):
    stop_simulation()
    st.sidebar.info("Stopped")

if st.sidebar.button("Clear Data"):
    st.session_state.data_stream = pd.DataFrame(columns=COLUMNS)
    st.session_state.prediction_rows = []
    with _SHARED["rows_lock"]:
        _SHARED["prediction_buffer"].clear()
    with _seen_lock:
        _seen_keys.clear()
    st.rerun()


def render_live_status() -> None:
    sim_running = _simulating.is_set() or st.session_state.simulation_running
    st.write("Simulation:", "Running" if sim_running else "Stopped")
    st.write("Kafka:", "Connected" if _kafka_status["connected"] else "Disconnected")
    st.write(f"Kafka messages: {_kafka_status['messages']}")
    st.write(f"UI rows: {len(st.session_state.data_stream)}")
    with _SHARED["rows_lock"]:
        buffered = len(_SHARED["prediction_buffer"])
    st.write(f"Buffered predictions: {buffered}")
    if _kafka_status["error"]:
        st.caption(f"Kafka: {_kafka_status['error']}")
    if _kafka_status["last_prediction_error"]:
        st.error(f"Prediction error: {_kafka_status['last_prediction_error']}")


@st.fragment(run_every=timedelta(seconds=2))
def live_dashboard() -> None:
    sync_predictions_to_session()
    render_dashboard()


@st.fragment(run_every=timedelta(seconds=2))
def live_status() -> None:
    sync_predictions_to_session()
    render_live_status()


live_dashboard()

with st.sidebar:
    st.divider()
    live_status()

st.sidebar.divider()
st.sidebar.write(f"Topic: {KAFKA_TOPIC}")
