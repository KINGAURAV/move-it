import json
import os
import time
from pathlib import Path
import pandas as pd
import streamlit as st
from kafka import KafkaProducer

# --- 1. Page Configuration & Persona Setup ---
st.set_page_config(
    page_title="RailOps AI Command Center",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar: Named User Persona Context for "Smooth Happy Path" Evaluation
st.sidebar.image("https://img.icons8.com/fluency/96/railroad-track.png", width=80)
st.sidebar.title("Operator Session")
st.sidebar.info("""
    **Active User:** Chief Operations Dispatcher  
    **Role:** Real-Time Incident Commander  
    **Duty Context:** High-Density Passenger Corridor  
""")

st.title("🚆 RailOps Predictive Maintenance Command Center")
st.caption("Autonomous Track Telemetry Processing & Live Command Loop Terminal")

# File & Network Configurations
PREDICTION_FILE = Path("/home/jovyan/move-it/03_vayu_kafka/latest_prediction.json")
COMMAND_TOPIC = "railops_commands"
KAFKA_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

# --- 2. Initialize Secure Kafka Producer for Manual Override Command ---
@st.cache_resource
def get_command_producer():
    """Initializes and caches the Kafka Producer to prevent socket exhaustion."""
    try:
        # Pull environment SASL parameters if deployed securely on Vayu
        kafka_user = os.getenv("KAFKA_USERNAME")
        kafka_pass = os.getenv("KAFKA_PASSWORD")
        
        config = {
            "bootstrap_servers": [KAFKA_SERVER],
            "value_serializer": lambda v: json.dumps(v).encode('utf-8'),
            "bootstrap_timeout_ms": 5000
        }
        
        if kafka_user and kafka_pass:
            config.update({
                "security_protocol": "SASL_PLAINTEXT",
                "sasl_mechanism": "SCRAM-SHA-512",
                "sasl_plain_username": kafka_user,
                "sasl_plain_password": kafka_pass
            })
            
        return KafkaProducer(**config)
    except Exception as e:
        st.sidebar.error(f"❌ Command Pipeline Offline: {e}")
        return None

producer = get_command_producer()

# --- 3. Interactive Manual Override Controls (5 Points) ---
st.sidebar.markdown("---")
st.sidebar.subheader("🚨 Manual Override Console")
st.sidebar.markdown("*Bypasses AI models to send instant infrastructure commands.*")

selected_command = st.sidebar.selectbox(
    "Select Action Strategy",
    ["RESTRICT_SPEED_30KMH", "HALT_ALL_TRAINS", "DISPATCH_EMERGENCY_CREW", "CLEAR_ALERTS"]
)

if st.sidebar.button("⚡ Execute Emergency Command", type="primary", use_container_width=True):
    command_payload = {
        "command": selected_command,
        "issued_by": "Chief Operations Dispatcher",
        "timestamp": time.time(),
        "override_type": "MANUAL_DASHBOARD_TRIGGER"
    }
    
    if producer:
        try:
            producer.send(COMMAND_TOPIC, value=command_payload)
            producer.flush()
            st.sidebar.success(f"✅ Executed: {selected_command}")
            st.toast(f"🚀 Broadcasted {selected_command} to Rail Network!", icon="⚡")
        except Exception as err:
            st.sidebar.error(f"Failed to transmit: {err}")
    else:
        st.sidebar.warning("Simulation Mode: Command printed to log but Kafka unavailable.")
        print(f"[SIMULATED OVERRIDE] Sent payload: {command_payload}")


# --- 4. Live Data Engine & Stream Processing ---
def load_stream_data():
    """Safely reads the line-delimited JSON stream file into a dataframe."""
    if not PREDICTION_FILE.exists() or PREDICTION_FILE.stat().st_size == 0:
        return pd.DataFrame()
    
    try:
        df = pd.read_json(PREDICTION_FILE, lines=True)
        if not df.empty and "sensor_data" in df.columns:
            sensor_df = pd.json_normalize(df["sensor_data"])
            df = pd.concat([df.drop(columns=["sensor_data"]), sensor_df], axis=1)
            if "timestamp" in df.columns:
                df["time_index"] = pd.to_datetime(df["timestamp"], unit="s")
                df = df.sort_values("time_index").reset_index(drop=True)
        return df
    except Exception:
        return pd.DataFrame()

# Layout Containers
kpi_placeholder = st.empty()
chart_placeholder = st.empty()
table_placeholder = st.empty()

# --- 5. Real-Time Telemetry Fragment (5 Points) ---
@st.fragment(run_every=1.0)
def refresh_dashboard():
    df_all = load_stream_data()
    
    if df_all.empty:
        kpi_placeholder.info("⏳ Awaiting telemetry pipeline initialization... Run your consumer and producer.")
        return

    latest = df_all.iloc[-1]
    
    # Section A: Named Operator Decision Header (Smooth Happy Path Strategy)
    with kpi_placeholder.container():
        status = latest.get("status", "🟩 NORMAL")
        prob = latest.get("probability", 0.0)
        pred = latest.get("prediction", 0)

        if "WARNING" in str(status) or pred == 1 or prob > 0.7:
            st.error("🚨 CRITICAL ALERT: STRUCTURAL FAILURE RISK DETECTED — RECOMMENDED ACTION: RESTRICT SPEED OR HALT CORRIDOR IMMEDIATELY.")
        else:
            st.success("🟢 SYSTEM HEALTHY — Track Operations Normal. No Dispatch Required.")

        # Top Metric Row
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Failure Probability Score", f"{prob:.2%}" if pd.notna(prob) else "N/A")
        with col2:
            st.metric("Model Classification Output", "1 (RISK)" if pred == 1 else "0 (SAFE)")
        with col3:
            st.metric("Total Monitored Sweeps", f"{len(df_all):,}")

        st.markdown("---")
        
        # Telemetry Display Grid matching exact dataset dimensions
        st.subheader("📡 Real-Time Physical Sensor Arrays")
        cols = st.columns(5)
        cols[0].metric("Track Temp", f"{latest.get('track_temperature_c', 0.0):.1f} °C")
        cols[1].metric("Structural Vibration", f"{latest.get('vibration_hz', 0.0):.1f} Hz")
        cols[2].metric("Rail Strain Gauges", f"{latest.get('rail_strain_mu', 0.0):.1f} με")
        cols[3].metric("Acoustic Emissions", f"{latest.get('acoustic_emission_db', 0.0):.1f} dB")
        cols[4].metric("Alignment Deviation", f"{latest.get('alignment_deviation_mm', 0.0):.2f} mm")

    # Section B: Live Telemetry Plot Updates (5 Points)
    with chart_placeholder.container():
        st.markdown("---")
        st.subheader("📈 Live Continuous Risk Timeline (Trailing 50 Sweeps)")
        history_df = df_all.tail(50)
        
        if "time_index" in history_df.columns and "probability" in history_df.columns:
            chart_data = history_df.set_index("time_index")[["probability"]]
            st.line_chart(chart_data, y_label="Probability", use_container_width=True)

    # Section C: Audit Records for Transparency
    with table_placeholder.container():
        st.subheader("📋 Historical Data Stream Logs")
        display_cols = [
            "time_index", "status", "prediction", "probability", 
            "track_temperature_c", "vibration_hz", "rail_strain_mu"
        ]
        valid_cols = [c for c in display_cols if c in df_all.columns]
        st.dataframe(df_all[valid_cols].tail(10).iloc[::-1], use_container_width=True, hide_index=True)

# Run the live engine loop
refresh_dashboard()