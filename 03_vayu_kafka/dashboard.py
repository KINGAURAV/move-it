import json
import os
import time
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
from kafka import KafkaProducer

# --- 1. PAGE CONFIGURATION & DARK CONTROL ROOM THEME ---
st.set_page_config(
    page_title="RailOps Control Center",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.stApp { background-color: #0b1220; }
[data-testid="stSidebar"] { background: #111827; }
h1, h2, h3 { color: white; font-weight: 700; margin-top: 5px; }
.kpi-card {
    background: #162032; padding: 20px; border-radius: 12px;
    border: 1px solid #24344d; text-align: center;
}
.alert-card {
    background: #1e1b1b; padding: 12px; border-radius: 8px;
    border-left: 5px solid #ef4444; margin-bottom: 8px;
}
.alert-card.high { border-left-color: #f97316; background: #221a14; }
div[data-testid="stMetricValue"] { font-size: 24px; color: white; }
</style>
""", unsafe_allow_html=True)

# --- 2. GLOBAL CONFIGS & KAFKA PRODUCER SETUP ---
PREDICTION_FILE = Path("/home/jovyan/move-it/03_vayu_kafka/latest_prediction.json")
COMMAND_TOPIC = "railops_commands"
KAFKA_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

@st.cache_resource
def get_command_producer():
    try:
        kafka_user = os.getenv("KAFKA_USERNAME")
        kafka_pass = os.getenv("KAFKA_PASSWORD")
        config = {
            "bootstrap_servers": [KAFKA_SERVER],
            "value_serializer": lambda v: json.dumps(v).encode('utf-8'),
            "bootstrap_timeout_ms": 2000
        }
        if kafka_user and kafka_pass:
            config.update({
                "security_protocol": "SASL_PLAINTEXT",
                "sasl_mechanism": "SCRAM-SHA-512",
                "sasl_plain_username": kafka_user,
                "sasl_plain_password": kafka_pass
            })
        return KafkaProducer(**config)
    except Exception:
        return None

producer = get_command_producer()

# --- 3. PERSISTENT STATE MANAGEMENT ---
if "network_state" not in st.session_state:
    track_ids = [f"TRK-{i:03d}" for i in range(1, 51)]
    sections = ["North", "South", "East", "West"]
    teams = ["Alpha", "Bravo", "Charlie", "Delta"]
    
    np.random.seed(42)
    state_df = pd.DataFrame({
        "track_id": track_ids,
        "section": [np.random.choice(sections) for _ in track_ids],
        "team": [np.random.choice(teams) for _ in track_ids],
        "inspection_status": ["Completed" if np.random.rand() > 0.3 else "Pending" for _ in track_ids],
        "action_taken": ["Yes" if np.random.rand() > 0.6 else "No" for _ in track_ids],
        "days_ago": [np.random.randint(5, 150) for _ in track_ids]
    })
    
    state_df.loc[state_df["track_id"] == "TRK-049", ["section", "team", "inspection_status", "action_taken"]] = ["East", "Charlie", "Pending", "No"]
    state_df.loc[state_df["track_id"] == "TRK-012", ["section", "team", "inspection_status", "action_taken"]] = ["North", "Alpha", "In Progress", "No"]
    
    st.session_state.network_state = state_df

if "selected_track" not in st.session_state:
    st.session_state.selected_track = "TRK-049"

if "activity_feed" not in st.session_state:
    st.session_state.activity_feed = [
        {"time": "01:50", "track": "TRK-012", "event": "High Structural Stress Handled"},
        {"time": "01:46", "track": "TRK-031", "event": "Medium Risk Logged"}
    ]

# --- 4. STREAMING ENGINE INTERFACE (Telemetry + Time Trends) ---
def get_latest_telemetry():
    if PREDICTION_FILE.exists() and PREDICTION_FILE.stat().st_size > 0:
        try:
            df = pd.read_json(PREDICTION_FILE, lines=True)
            if not df.empty and "sensor_data" in df.columns:
                s_df = pd.json_normalize(df["sensor_data"])
                df = df.drop(columns=["sensor_data"])
                df = pd.concat([df, s_df], axis=1)
                df = df.loc[:, ~df.columns.duplicated()]
                if "timestamp" in df.columns:
                    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s", errors="ignore")
                return df
        except Exception:
            pass
            
    # Simulation engine fallback logic
    t_span = 20
    timestamps = [pd.Timestamp.now() - pd.Timedelta(minutes=i) for i in range(t_span)][::-1]
    
    records = []
    for tid in st.session_state.network_state["track_id"]:
        base_seed = sum(ord(c) for c in tid)
        np.random.seed(base_seed)
        v_base = np.random.uniform(10, 30)
        t_base = np.random.uniform(20, 35)
        
        if tid == "TRK-049":
            v_trend = np.linspace(40, 84.18, t_span)
            prob_trend = np.linspace(0.4, 0.90, t_span)
            t_trend = np.linspace(45, 61.7, t_span)
            fault, risk = "Track Misalignment", "CRITICAL"
        elif tid == "TRK-012":
            v_trend = np.linspace(30, 55.2, t_span)
            prob_trend = np.linspace(0.3, 0.76, t_span)
            t_trend = np.linspace(35, 48.2, t_span)
            fault, risk = "Structural Stress", "HIGH"
        else:
            v_trend = np.random.normal(v_base, 2, t_span)
            t_trend = np.random.normal(t_base, 1, t_span)
            prob_trend = np.random.uniform(0.01, 0.15, t_span)
            fault, risk = "None", "LOW"
            
        for idx, t in enumerate(timestamps):
            records.append({
                "track_id": tid,
                "timestamp": t,
                "probability": prob_trend[idx],
                "risk_level": "CRITICAL" if prob_trend[idx] > 0.8 else ("HIGH" if prob_trend[idx] > 0.5 else ("MEDIUM" if prob_trend[idx] > 0.2 else "LOW")),
                "fault_type": fault if prob_trend[idx] > 0.2 else "None",
                "vibration_hz": v_trend[idx],
                "track_temperature_c": t_trend[idx],
                "acoustic_emission_db": 30 + (v_trend[idx] * 0.3),
                "rail_strain_mu": 10 + (prob_trend[idx] * 180),
                "alignment_deviation_mm": prob_trend[idx] * 5.0
            })
            
    return pd.DataFrame(records)

# --- SAFE DATA ASSEMBLY PIECE ---
telemetry_df = get_latest_telemetry()

# Defensive Copy of base network assets to guarantee structural parameters exist
master_df = st.session_state.network_state.copy()

if not telemetry_df.empty:
    latest_telemetry = telemetry_df.sort_values("timestamp").groupby("track_id").last().reset_index()
    # Merge only matching diagnostic elements, preserving all baseline details
    cols_to_merge = [c for c in latest_telemetry.columns if c not in ["section", "team", "inspection_status", "action_taken", "days_ago"]]
    master_df = master_df.merge(latest_telemetry[cols_to_merge], on="track_id", how="left")

# Fallback specifications matrix guard
required_columns = {
    "risk_level": "LOW",
    "probability": 0.05,
    "fault_type": "None",
    "vibration_hz": 20.0,
    "track_temperature_c": 25.0,
    "acoustic_emission_db": 35.0,
    "rail_strain_mu": 15.0,
    "alignment_deviation_mm": 0.02
}

for col, default_val in required_columns.items():
    if col not in master_df.columns:
        master_df[col] = default_val
    else:
        master_df[col] = master_df[col].fillna(default_val)

# --- 5. RENDER MAIN TOP-LEVEL KPI ROW ---
st.markdown("# 🚆 RailOps Central Network Operations Center")
st.caption("Predictive Maintenance Dispatch Room | Active Broker Sync Loop")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.markdown(f'<div class="kpi-card"><h3>🚆 Tracks Monitored</h3><h2>{len(master_df)}</h2></div>', unsafe_allow_html=True)
with kpi2:
    crit_count = len(master_df[master_df["risk_level"] == "CRITICAL"])
    st.markdown(f'<div class="kpi-card"><h3>🚨 Critical Alerts</h3><h2 style="color:#ef4444;">{crit_count}</h2></div>', unsafe_allow_html=True)
with kpi3:
    pend_count = len(master_df[master_df["inspection_status"] == "Pending"])
    st.markdown(f'<div class="kpi-card"><h3>🔧 Pending Inspections</h3><h2 style="color:#f97316;">{pend_count}</h2></div>', unsafe_allow_html=True)
with kpi4:
    done_count = len(master_df[master_df["action_taken"] == "Yes"])
    st.markdown(f'<div class="kpi-card"><h3>✅ Repairs Completed</h3><h2 style="color:#10b981;">{done_count}</h2></div>', unsafe_allow_html=True)

st.markdown("---")

# --- 6. CORE TWO-PANEL INTERACTIVE OPERATION CENTER ---
left_panel, center_panel, side_panel = st.columns([1.2, 2.5, 1.8])

# LEFT PANEL: LIVE HIGH-RISK REALTIME INCIDENT ALERTS
with left_panel:
    st.markdown("### 🛑 High & Critical Alerts")
    alert_targets = master_df[master_df["risk_level"].isin(["CRITICAL", "HIGH"])]
    
    if alert_targets.empty:
        st.success("No active anomalies across the corridor network profile.")
    else:
        for _, row in alert_targets.iterrows():
            card_class = "alert-card critical" if row["risk_level"] == "CRITICAL" else "alert-card high"
            emoji = "🔴" if row["risk_level"] == "CRITICAL" else "🟠"
            rec_action = "Immediate Shutdown" if row["risk_level"] == "CRITICAL" else "Repair Soon"
            
            st.markdown(f"""
            <div class="{card_class}">
                <strong>{emoji} {row['track_id']}</strong> | {row['section']} Corridor<br/>
                <small>Fault: {row['fault_type']}</small><br/>
                <strong>Prob: {row['probability']:.0%}</strong> → <em>{rec_action}</em>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Focus Target {row['track_id']}", key=f"focus_{row['track_id']}", use_container_width=True):
                st.session_state.selected_track = row["track_id"]
                st.rerun()

# CENTER PANEL: MAIN FILTERABLE NETWORK REGISTRY TABLE
with center_panel:
    st.markdown("### 🗺 Corridor Matrix Registry")
    
    f1, f2, f3, f4 = st.columns(4)
    risk_choice = f1.selectbox("Risk Level", ["All", "LOW", "MEDIUM", "HIGH", "CRITICAL"])
    section_choice = f2.selectbox("Section Profile", ["All", "North", "South", "East", "West"])
    team_choice = f3.selectbox("Assigned Crew", ["All", "Alpha", "Bravo", "Charlie", "Delta"])
    status_choice = f4.selectbox("Workflow Status", ["All", "Pending", "In Progress", "Completed"])
    
    search_id = st.text_input("🔍 Direct Track ID Locate Search", "").strip().upper()
    
    filtered_df = master_df.copy()
    if risk_choice != "All": filtered_df = filtered_df[filtered_df["risk_level"] == risk_choice]
    if section_choice != "All": filtered_df = filtered_df[filtered_df["section"] == section_choice]
    if team_choice != "All": filtered_df = filtered_df[filtered_df["team"] == team_choice]
    if status_choice != "All": filtered_df = filtered_df[filtered_df["inspection_status"] == status_choice]
    if search_id: filtered_df = filtered_df[filtered_df["track_id"].str.contains(search_id)]
    
    display_cols = ["track_id", "section", "risk_level", "fault_type", "team", "inspection_status"]
    ui_table_df = filtered_df[display_cols].copy()
    
    def color_risk(val):
        colors = {"CRITICAL": "🔴 Critical", "HIGH": "🟠 High", "MEDIUM": "🟡 Medium", "LOW": "🟢 Low"}
        return colors.get(val, val)
    ui_table_df["risk_level"] = ui_table_df["risk_level"].apply(color_risk)
    
    st.dataframe(
        ui_table_df, 
        hide_index=True, 
        use_container_width=True,
        column_config={"track_id": "Track", "section": "Section", "risk_level": "Risk Profile", "fault_type": "Classified Fault", "team": "Team", "inspection_status": "Status"}
    )
    
    track_select_list = list(master_df["track_id"].values)
    focused_index = track_select_list.index(st.session_state.selected_track) if st.session_state.selected_track in track_select_list else 0
    
    selected_target = st.selectbox(
        "Select an Asset for Deep Inspection & Action",
        track_select_list,
        index=focused_index
    )
    if selected_target != st.session_state.selected_track:
        st.session_state.selected_track = selected_target
        st.rerun()

# RIGHT PANEL: ASSET INSPECTION SIDE PANEL & TIME-SERIES TREND ANALYSIS
with side_panel:
    target_id = st.session_state.selected_track
    row = master_df[master_df["track_id"] == target_id].iloc[0]
    
    st.markdown(f"## 🔭 Asset Profile: **{target_id}**")
    st.divider()
    
    st.markdown("### 📊 Live Core Diagnostics")
    m1, m2, m3 = st.columns(3)
    m1.metric("Vibration", f"{row['vibration_hz']:.2f} Hz")
    m2.metric("Acoustic", f"{row['acoustic_emission_db']:.1f} dB")
    m3.metric("Temperature", f"{row['track_temperature_c']:.1f} °C")
    
    m4, m5 = st.columns(2)
    m4.metric("Strain Gauges", f"{row['rail_strain_mu']:.1f} με")
    m5.metric("Alignment Dev.", f"{row['alignment_deviation_mm']:.2f} mm")
    
    st.markdown("### 🧠 Predictive AI Assessment")
    st.metric("Failure Probability", f"{row['probability']:.1%}")
    
    rec_text = "Immediate Shutdown" if row["risk_level"] == "CRITICAL" else ("Repair Soon" if row["risk_level"] == "HIGH" else "Routine Baseline Check")
    st.info(f"**Fault Profile:** {row['fault_type']}\n\n**Recommended Action:** {rec_text}")
    
    st.markdown("### 🔧 Operations Workflow Maintenance Log")
    st.write(f"**Assigned Field Team:** Team {row['team']}")
    st.write(f"**Operational Status Tracker:** `{row['inspection_status']}`")
    st.write(f"**Last Action Sweep:** {row['days_ago']} days ago")
    st.write(f"**Action Taken:** {row['action_taken']}")
    
    st.markdown("### 🕹 Console Mitigation Controls")
    act1, act2, act3 = st.columns(3)
    
    target_idx = st.session_state.network_state[st.session_state.network_state["track_id"] == target_id].index
    
    if act1.button("🚚 Dispatch Crew", use_container_width=True):
        st.session_state.network_state.loc[target_idx, "inspection_status"] = "In Progress"
        st.session_state.activity_feed.insert(0, {"time": time.strftime("%H:%M"), "track": target_id, "event": f"Crew {row['team']} In Progress"})
        if producer:
            producer.send(COMMAND_TOPIC, value={"command": "START_INSPECTION", "asset": target_id, "timestamp": time.time()})
            producer.flush()
        st.toast(f"Dispatched Field Units to {target_id} Corridor!", icon="🚚")
        st.rerun()
        
    if act2.button("✅ Mark Restored", use_container_width=True):
        st.session_state.network_state.loc[target_idx, ["inspection_status", "action_taken"]] = ["Completed", "Yes"]
        st.session_state.activity_feed.insert(0, {"time": time.strftime("%H:%M"), "track": target_id, "event": "Structural Repair Verified"})
        if producer:
            producer.send(COMMAND_TOPIC, value={"command": "MARK_COMPLETED", "asset": target_id, "timestamp": time.time()})
            producer.flush()
        st.toast(f"Corridor Health Tag cleared successfully for {target_id}!", icon="✅")
        st.rerun()
        
    if act3.button("🔄 Reset Asset", use_container_width=True):
        st.session_state.network_state.loc[target_idx, ["inspection_status", "action_taken"]] = ["Pending", "No"]
        st.toast("Simulated parameters reloaded.", icon="🔄")
        st.rerun()

    st.markdown("### 📈 Historical Run Anomaly Trends")
    track_history = telemetry_df[telemetry_df["track_id"] == target_id].sort_values("timestamp")
    chart_data = track_history.set_index("timestamp")[["probability", "vibration_hz", "track_temperature_c"]]
    chart_data.columns = ["Failure Probability Index", "Vibration Profile (Hz)", "Base Temperature (°C)"]
    st.line_chart(chart_data, height=220)

st.markdown("---")

# --- 7. BOTTOM FOOTER SECTION: ANALYTICS & RECENT STREAM EVENTS ---
a_left, a_center, a_right = st.columns([2, 2, 2])

with a_left:
    st.markdown("### 📊 Asset Statistical Profiles")
    risk_dist = master_df["risk_level"].value_counts()
    st.write("**Risk Class Distributions:**")
    for r_lvl in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
        cnt = risk_dist.get(r_lvl, 0)
        bars = "█" * cnt
        st.text(f"{r_lvl:<10} ({cnt:02d}) {bars}")

with a_center:
    st.markdown("### 📍 Regional Section Density")
    sec_dist = master_df["section"].value_counts()
    for sec, count in sec_dist.items():
        st.progress(int(count) / 20, text=f"Corridor {sec:<10} : {count} Tracks Active")

with a_right:
    st.markdown("### 🕒 Real-Time Action & Event Log")
    for act in st.session_state.activity_feed[:4]:
        st.markdown(f"`{act['time']}` **{act['track']}** — *{act['event']}*")
        st.markdown("<hr style='margin:4px 0px; border-color:#24344d;'/>", unsafe_allow_html=True)

st.sidebar.title("Central Control")
st.sidebar.info("**Dispatcher:** Operations Room\n\n**Corridor:** Western Mainline\n\n**Status:** 🟢 ONLINE")