"""
Move-It — Streamlit dashboard for RailOps.

Flow: Start Simulation -> POST /ingest -> Kafka -> model predict -> UI -> Command Kafka (Act)
"""

from __future__ import annotations

import os
import json
import random
import sys
import threading
import time
import builtins
from datetime import timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import numpy as np
import requests
import streamlit as st
import pydeck as pdk
from kafka import KafkaConsumer, KafkaProducer

APP_DIR = Path(__file__).resolve().parent

sys.path.insert(0, str(APP_DIR))
from kafka_config import KAFKA_BROKER, KAFKA_TOPIC, consumer_config

LOCAL_INGEST_URL = "http://127.0.0.1:5000/ingest"
DEFAULT_PREDICT_HOST = os.getenv("VAYU_PREDICT_HOST", "https://moveit-modeldeploy-ca942-paas-7250-22326-public.cloudservices.tatacommunications.com")
DEFAULT_MODEL_NAME = os.getenv("VAYU_MODEL_NAME", "model")

# Define the new command-out topic for the "Act" loop
# Change this near the top of your app.py if needed to align with your cluster's topic space
COMMAND_TOPIC = os.getenv("KAFKA_COMMAND_TOPIC", "xoxeb-kafka-topic")

def _is_full_predict_url(url: str) -> bool:
    return url.rstrip("/").endswith(":predict")


def _is_dev_proxy_ingest_url(url: str) -> bool:
    lowered = url.lower()
    if "proxy" not in lowered:
        return False
    return any(marker in lowered for marker in ("codeserver", "vscode", "jupyter", "rstudio", "/user/", "aistudio"))


def resolve_ingest_url(raw: str | None = None) -> str:
    url = (raw or os.getenv("INGEST_API_URL", LOCAL_INGEST_URL)).strip()
    if not url or _is_dev_proxy_ingest_url(url):
        return LOCAL_INGEST_URL
    if not url.rstrip("/").endswith("/ingest"):
        url = url.rstrip("/") + "/ingest"
    return url


def build_predict_url(host: str, model_name: str) -> str:
    host = host.strip().rstrip("/")
    model_name = model_name.strip()
    if not host or _is_full_predict_url(host):
        return host
    if not model_name:
        raise ValueError("Set predict host and model name.")
    if host.endswith("/v1"):
        return f"{host}/models/{model_name}:predict"
    return f"{host}/v1/models/{model_name}:predict"


def resolve_predict_url(host: str | None = None, model_name: str | None = None) -> str:
    explicit = os.getenv("PREDICT_URL", "").strip()
    if explicit:
        return explicit
    host_value = (host or DEFAULT_PREDICT_HOST).strip().rstrip("/")
    if _is_full_predict_url(host_value):
        return host_value
    return build_predict_url(host_value, model_name or DEFAULT_MODEL_NAME)


def parse_ingest_response(resp: requests.Response, payload: dict) -> dict:
    if resp.status_code != 200:
        raise ValueError(f"Ingest failed ({resp.status_code}): {resp.text[:300]}")
    if "application/json" not in resp.headers.get("Content-Type", ""):
        return payload
    try:
        return resp.json().get("data", payload)
    except ValueError:
        return payload


COLUMNS = [
    "timestamp", "track_id", "section", "latitude", "longitude", 
    "vibration_hz", "rail_strain_mu", "alignment_deviation_mm", 
    "prediction", "probability", "risk_level", "fault_type", 
    "recommended_action", "rul_days", "assigned_team", "dispatch_status",
    "command_sent", "command_status"
]

FEATURE_COLS = [
    "vibration_hz", 
    "acoustic_emission_db", 
    "rail_strain_mu", 
    "track_temperature_c", 
    "alignment_deviation_mm", 
    "last_maintenance_days"
]

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
                "commands_sent": 0,
                "last_prediction_error": None,
            },
            "seen_keys": set(),
            "seen_lock": threading.Lock(),
            "state_lock": threading.Lock(),
            "kafka_started": False,
            "predict_url": resolve_predict_url(),
            "predict_host_header": os.getenv("VAYU_HOST_HEADER", ""),
            "predict_bearer_token": os.getenv("VAYU_BEARER_TOKEN", ""),
        }
    return builtins._moveit_shared_state


_SHARED = _shared_state()
_simulating = _SHARED["simulating"]
_kafka_status = _SHARED["kafka_status"]
_seen_keys = _SHARED["seen_keys"]
_seen_lock = _SHARED["seen_lock"]
_state_lock = _SHARED["state_lock"]


# Initialize Kafka Producer for the command-out topic
@st.cache_resource
def get_kafka_producer():
    try:
        # Check if consumer_config has your credentials we can borrow for parity
        try:
            from kafka_config import consumer_config
            cfg = consumer_config()
            # Extract common authentication fields if they exist in your config file
            security_protocol = cfg.get("security_protocol", "SASL_PLAINTEXT")
            sasl_mechanism = cfg.get("sasl_mechanism", "SCRAM-SHA-256")
        except Exception:
            # Fallbacks if we need to declare them manually
            security_protocol = "SASL_PLAINTEXT"
            sasl_mechanism = "SCRAM-SHA-256"

        return KafkaProducer(
            bootstrap_servers=KAFKA_BROKER, # Maps to 100.78.64.24:9095
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            acks="all",
            retries=3,
            max_block_ms=5000,
            # Explicit SASL Configuration for the xoxeb cluster
            security_protocol=security_protocol,
            sasl_mechanism=sasl_mechanism,
            sasl_plain_username="xoxeb-kafkauser",
            sasl_plain_password="8aC5D#EasE"
        )
    except Exception as e:
        print(f"Failed to initialize Authenticated Kafka Producer: {e}")
        return None

def send_system_command(track_id: str, action: str, level: str):
    """Publishes an operational directive back to the edge via Kafka."""
    producer = get_kafka_producer()
    if not producer:
        return False
        
    command_payload = {
        "command_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "track_id": track_id,
        "directive": "SPEED_RESTRICTION" if level == "HIGH" else "EMERGENCY_SHUTDOWN" if level == "CRITICAL" else "MAINTENANCE_SCHEDULED",
        "recommended_action": action,
        "risk_severity": level
    }
    
    try:
        producer.send(COMMAND_TOPIC, value=command_payload)
        producer.flush()
        _kafka_status["commands_sent"] += 1
        return True
    except Exception as e:
        print(f"Error publishing command out: {e}")
        return False


def sync_predict_config(host: str, model_name: str, host_header: str = "", bearer_token: str = "") -> str:
    predict_url = resolve_predict_url(host, model_name)
    _SHARED["predict_url"] = predict_url
    _SHARED["predict_host_header"] = host_header.strip()
    _SHARED["predict_bearer_token"] = bearer_token.strip()
    return predict_url


def _predict_headers() -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    host_header = str(_SHARED.get("predict_host_header", "")).strip()
    if host_header:
        headers["Host"] = host_header
    token = str(_SHARED.get("predict_bearer_token", "")).strip() or os.getenv("VAYU_BEARER_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def predict_maintenance(data: dict) -> tuple[int, float]:
    predict_url = str(_SHARED.get("predict_url", "")).strip() or os.getenv("PREDICT_URL", "").strip()
    if not predict_url:
        raise ValueError("Set PREDICT_URL or configure Vayu Model Serving.")

    payload = {
        "instances": [
            [float(data.get(col, 0.0)) for col in FEATURE_COLS]
        ]
    }
    
    response = requests.post(
        predict_url,
        headers=_predict_headers(),
        json=payload,
        timeout=float(os.getenv("PREDICT_TIMEOUT", "30")),
    )
    response.raise_for_status()
    body = response.json()
    
    preds = body.get("predictions")
    if preds is None:
        raise ValueError(f"No predictions in response: {body}")

    pred = preds[0]
    if isinstance(pred, list):
        probability = float(pred[1]) if len(pred) > 1 else float(pred[0])
        prediction = int(probability >= 0.5)
    else:
        prediction = int(pred)
        probability = 0.90 if prediction == 1 else 0.10

    return prediction, probability


def _predict_row(data: dict) -> dict:
    prediction, probability = predict_maintenance(data)

    if probability < 0.30: risk_level = "LOW"
    elif probability < 0.60: risk_level = "MEDIUM"
    elif probability < 0.85: risk_level = "HIGH"
    else: risk_level = "CRITICAL"

    alignment = abs(float(data.get("alignment_deviation_mm", 0)))
    if risk_level == "LOW": fault_type = "Normal"
    elif alignment > 4: fault_type = "Track Misalignment"
    else: fault_type = "Excessive Wear"

    action_map = {"LOW": "Monitor", "MEDIUM": "Schedule Inspection", "HIGH": "Repair Soon", "CRITICAL": "Immediate Shutdown"}
    action = action_map[risk_level]

    base_rul = max(1, 365 - int(data.get("last_maintenance_days", 0)))
    rul_days = int(base_rul * (1.0 - probability))

    assigned_team = data.get("assigned_team", "Unassigned")
    if risk_level in ("HIGH", "CRITICAL"):
        dispatch_status = "Dispatched"
    elif risk_level == "MEDIUM":
        dispatch_status = "Standby"
    else:
        dispatch_status = "Idle"

    track_hash = hash(str(data.get("track_id", "TRK-001"))) % 1000
    lat = 40.7128 + (track_hash / 5000.0)
    lon = -74.0060 + (track_hash / 5000.0)

    # Automatically "Act" if the cloud model yields High/Critical anomalies
    command_sent = False
    command_status = "N/A"
    if risk_level in ["HIGH", "CRITICAL"]:
        command_sent = send_system_command(str(data.get("track_id", "UNKNOWN")), action, risk_level)
        command_status = "Dispatched via Kafka" if command_sent else "Failed to Transmit"

    return {
        "timestamp": data.get("timestamp", time.strftime("%H:%M:%S")),
        "track_id": data.get("track_id", "UNKNOWN"),
        "section": data.get("section", "UNKNOWN"),
        "latitude": lat,
        "longitude": lon,
        "vibration_hz": float(data.get("vibration_hz", 0)),
        "rail_strain_mu": float(data.get("rail_strain_mu", 0)),
        "alignment_deviation_mm": alignment,
        "prediction": prediction,
        "probability": round(probability, 3),
        "risk_level": risk_level,
        "fault_type": fault_type,
        "recommended_action": action,
        "rul_days": rul_days,
        "assigned_team": assigned_team,
        "dispatch_status": dispatch_status,
        "command_sent": command_sent,
        "command_status": command_status,
        "acoustic_emission_db": float(data.get("acoustic_emission_db", 0)),
        "track_temperature_c": float(data.get("track_temperature_c", 0)),
        "last_maintenance_days": int(data.get("last_maintenance_days", 0))
    }


def _append_prediction_row(row: dict) -> None:
    with _SHARED["rows_lock"]:
        _SHARED["prediction_buffer"].append(row)
        _SHARED["prediction_buffer"] = _SHARED["prediction_buffer"][-50:]


def enqueue_prediction(data: dict, source: str) -> None:
    key = (data.get("timestamp"), data.get("track_id"), float(data.get("vibration_hz", 0)))
    with _seen_lock:
        if key in _seen_keys:
            return
        _seen_keys.add(key)

    try:
        _append_prediction_row(_predict_row(data))
        _kafka_status["last_prediction_error"] = None
    except Exception as exc:
        _kafka_status["last_prediction_error"] = str(exc)


def kafka_consumer_worker() -> None:
    while True:
        consumer = None
        try:
            consumer = KafkaConsumer(**consumer_config())
            consumer.subscribe([KAFKA_TOPIC])
            _kafka_status["connected"] = True
            _kafka_status["error"] = None

            while True:
                msg_pack = consumer.poll(timeout_ms=1000)
                for messages in msg_pack.values():
                    for msg in messages:
                        enqueue_prediction(msg.value, "kafka")
                        _kafka_status["messages"] += 1
        except Exception as exc:
            _kafka_status["connected"] = False
            _kafka_status["error"] = str(exc)
            time.sleep(5)
        finally:
            if consumer is not None:
                consumer.close()


def ensure_kafka_consumer() -> None:
    if _SHARED["kafka_started"]:
        return
    _SHARED["kafka_started"] = True
    threading.Thread(target=kafka_consumer_worker, daemon=True).start()


def run_sensor_simulation(ingest_url: str) -> None:
    BASE_DIR = Path(__file__).resolve().parent.parent
    dataset_path = BASE_DIR / "01_dataset" / "downloaded_railway_telemetry.csv"
    if not dataset_path.exists():
        _kafka_status["last_prediction_error"] = f"Dataset path {dataset_path} missing."
        return

    df_source = pd.read_csv(dataset_path)
    
    while _simulating.is_set():
        for _, row in df_source.iterrows():
            if not _simulating.is_set():
                break
            payload = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "track_id": str(row.get("track_id", "TRK-001")),
                "section": str(row.get("section", "East")),
                "vibration_hz": float(row.get("vibration_hz", 0.0)),
                "acoustic_emission_db": float(row.get("acoustic_emission_db", 0.0)),
                "rail_strain_mu": float(row.get("rail_strain_mu", 0.0)),
                "track_temperature_c": float(row.get("track_temperature_c", 0.0)),
                "alignment_deviation_mm": float(row.get("alignment_deviation_mm", 0.0)),
                "assigned_team": str(row.get("assigned_team", "Team A")),
                "last_maintenance_days": int(row.get("last_maintenance_days", 0)),
                "action_taken": str(row.get("action_taken", "No"))
            }
            try:
                resp = requests.post(ingest_url, json=payload, timeout=5)
                data = parse_ingest_response(resp, payload)
                enqueue_prediction(data, "ingest")
            except Exception as exc:
                print(f"Simulation error: {exc}")
            time.sleep(2)


def start_simulation(ingest_url: str) -> None:
    with _state_lock:
        _simulating.set()
        st.session_state.simulation_running = True
        thread = getattr(run_sensor_simulation, "_thread", None)
        if thread is None or not thread.is_alive():
            thread = threading.Thread(target=run_sensor_simulation, args=(ingest_url,), daemon=True)
            thread.start()
            run_sensor_simulation._thread = thread


def stop_simulation() -> None:
    _simulating.clear()
    st.session_state.simulation_running = False


def sync_predictions_to_session() -> int:
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
        col1.metric("Vibration Telemetry", "-")
        col2.metric("Est. Remaining Useful Life", "-")
        col3.metric("AI Risk Assessment", "Waiting")
        col4.metric("Crew Dispatch Status", "-")
        st.info("Start Ingestion API, then hit **Start Simulation**.")
        return

    latest = df.iloc[-1]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Live Vibration", f"{latest['vibration_hz']:.2f} Hz")
    col2.metric("Remaining Useful Life (RUL)", f"{latest['rul_days']} Days")
    col3.metric("AI Risk Score", f"{latest['probability']:.0%}", delta=latest["risk_level"])
    col4.metric("Crew Dispatch Status", f"{latest['assigned_team']} ({latest['dispatch_status']})")

    # Manual Command Override Control Board
    st.markdown("### 🎛️ Operator Tactical Command Deck")
    cmd_col1, cmd_col2, cmd_col3 = st.columns([2, 2, 3])
    with cmd_col1:
        selected_track = st.selectbox("Select Target Track Segment", df["track_id"].unique())
    with cmd_col2:
        override_action = st.selectbox("Select Force Directive", ["EMERGENCY_SHUTDOWN", "SPEED_RESTRICTION", "DISPATCH_INSPECTION"])
    with cmd_col3:
        st.write("") # Padding
        st.write("") 
        if st.button("🚨 Broadcast Forced Command Over Kafka", use_container_width=True):
            success = send_system_command(selected_track, override_action, "CRITICAL")
            if success:
                st.toast(f"Forced directive successfully published to {COMMAND_TOPIC}!", icon="🚀")
            else:
                st.toast("Failed to emit Kafka payload.", icon="❌")

    st.markdown("---")
    
    st.subheader("Interactive Railway Network Spatial Map")
    map_data = df[["latitude", "longitude", "track_id", "risk_level"]].copy()
    color_map = {"LOW": [0, 200, 0, 160], "MEDIUM": [240, 200, 0, 180], "HIGH": [240, 100, 0, 200], "CRITICAL": [240, 0, 0, 225]}
    map_data["color"] = map_data["risk_level"].map(color_map)
    
    view_state = pdk.ViewState(latitude=latest["latitude"], longitude=latest["longitude"], zoom=10, pitch=30)
    layer = pdk.Layer(
        "ScatterplotLayer",
        map_data,
        get_position=["longitude", "latitude"],
        get_color="color",
        get_radius=300,
        pickable=True
    )
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "Track: {track_id} | Risk: {risk_level}"}))

    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Failure Probability Trends")
        # Ensure proper chronological sorting so Streamlit can evaluate bounds accurately
        trend_df = df.dropna(subset=["timestamp", "probability"]).sort_values("timestamp")
        if not trend_df.empty:
            st.line_chart(trend_df.set_index("timestamp")[["probability"]])
        else:
            st.caption("Waiting for stream metrics...")
    
    with c2:
        st.subheader("Explainable AI (XAI) Diagnostics")
        # Scale inputs cleanly to avoid sending extreme limits or 0 division to the bar chart axis
        vibration_contrib = float(latest.get("vibration_hz", 0)) / 50.0
        strain_contrib = float(latest.get("rail_strain_mu", 0)) / 400.0
        alignment_contrib = float(latest.get("alignment_deviation_mm", 0)) / 5.0
        temp_contrib = float(latest.get("track_temperature_c", 0)) / 60.0

        diag_metrics = {
            "Vibration Delta": max(0.01, vibration_contrib),
            "Strain Load Factor": max(0.01, strain_contrib),
            "Alignment Deviation": max(0.01, alignment_contrib),
            "Thermal Friction Coefficient": max(0.01, temp_contrib)
        }
        diag_df = pd.DataFrame(list(diag_metrics.items()), columns=["Feature Metric", "Relative Risk Contribution"])
        st.bar_chart(diag_df.set_index("Feature Metric")[["Relative Risk Contribution"]])

    st.markdown("---")

    # Command Execution Audit Log
    st.subheader("📡 Active Fleet Incidents & Closed-Loop Command Audit Logs")
    incidents = df[df["risk_level"].isin(["HIGH", "CRITICAL"])].sort_index(ascending=False)
    if not incidents.empty:
        st.dataframe(incidents[["timestamp", "track_id", "risk_level", "recommended_action", "command_status"]], use_container_width=True, hide_index=True)
    else:
        st.success("No active failure incidents detected across track assets.")

    st.subheader("All Live Telemetry Stream Logs")
    display_df = df.sort_index(ascending=False).copy()
    st.dataframe(display_df, use_container_width=True, hide_index=True)


# --- Streamlit UI Setup ---
st.set_page_config(page_title="RailOps Predictive Maintenance System", layout="wide")

if "data_stream" not in st.session_state:
    st.session_state.data_stream = pd.DataFrame(columns=COLUMNS)
if "prediction_rows" not in st.session_state:
    st.session_state.prediction_rows = []
if "simulation_running" not in st.session_state:
    st.session_state.simulation_running = _simulating.is_set()
if "ingest_api_url" not in st.session_state:
    st.session_state.ingest_api_url = resolve_ingest_url()
if "predict_host" not in st.session_state:
    st.session_state.predict_host = DEFAULT_PREDICT_HOST
if "predict_model" not in st.session_state:
    st.session_state.predict_model = DEFAULT_MODEL_NAME
if "predict_host_header" not in st.session_state:
    st.session_state.predict_host_header = os.getenv("VAYU_HOST_HEADER", "")
if "predict_bearer_token" not in st.session_state:
    st.session_state.predict_bearer_token = os.getenv("VAYU_BEARER_TOKEN", "")

st.sidebar.header("Vayu Model Serving")
st.session_state.predict_host = st.sidebar.text_input("Predict host base URL", value=st.session_state.predict_host)
st.session_state.predict_model = st.sidebar.text_input("Model name", value=st.session_state.predict_model)
st.session_state.predict_host_header = st.sidebar.text_input("Host header (optional)", value=st.session_state.predict_host_header)
st.session_state.predict_bearer_token = st.sidebar.text_input("Bearer token (optional)", value=st.session_state.predict_bearer_token, type="password")

try:
    predict_url = sync_predict_config(
        st.session_state.predict_host, st.session_state.predict_model,
        st.session_state.predict_host_header, st.session_state.predict_bearer_token
    )
    st.sidebar.success("Predict endpoint ready")
    st.sidebar.code(predict_url, language=None)
except ValueError as exc:
    predict_url = ""
    st.sidebar.error(str(exc))

ensure_kafka_consumer()

st.title("RailOps Live Operations Dashboard")
st.caption("Real-Time Telemetry Pipeline Buffered via Kafka & Audited by Cloud Inference Engines")

st.sidebar.header("Control Panel")
st.session_state.ingest_api_url = st.sidebar.text_input("Ingest API URL", value=st.session_state.ingest_api_url)
ingest_url = resolve_ingest_url(st.session_state.ingest_api_url)

if st.sidebar.button("Start Simulation"):
    if not predict_url:
        st.sidebar.error("Set predict host/model or PREDICT_URL before starting.")
    elif not _simulating.is_set():
        start_simulation(ingest_url)
        st.sidebar.success("Simulation running")
        st.rerun()

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
    st.write("Kafka Ingestion:", "Connected" if _kafka_status["connected"] else "Disconnected")
    st.write(f"Telemetry Messages Processed: {_kafka_status['messages']}")
    st.write(f"Command Directives Dispatched: {_kafka_status['commands_sent']}")
    if _kafka_status["error"]:
        st.caption(f"Kafka Error: {_kafka_status['error']}")
    if _kafka_status["last_prediction_error"]:
        st.error(f"Prediction Gateway Error: {_kafka_status['last_prediction_error']}")


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
st.sidebar.write(f"Telemetry Topic: {KAFKA_TOPIC}")
st.sidebar.write(f"Command Topic: {COMMAND_TOPIC}")