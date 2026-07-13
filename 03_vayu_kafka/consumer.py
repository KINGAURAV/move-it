import os
import json
import time
import threading
import queue
from pathlib import Path
import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
from kafka import KafkaConsumer
from dotenv import load_dotenv

try:
    base_dir = Path(__file__).resolve().parent.parent
except NameError:
    base_dir = Path(".").resolve()

env_path = base_dir / ".env"
load_dotenv(env_path, override=True)

OUTPUT_FILE = Path("/home/jovyan/move-it/03_vayu_kafka/latest_prediction.json")
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True) # Ensure path exists

write_queue = queue.Queue()

def async_file_writer():
    while True:
        result = write_queue.get()
        if result is None:  
            break
        try:
            with open(OUTPUT_FILE, "a") as f:
                json.dump(result, f)
                f.write("\n")
                f.flush()
                os.fsync(f.fileno())
        except Exception as e:
            print(f"❌ Disk Write Error: {e}")
        finally:
            write_queue.task_done()

writer_thread = threading.Thread(target=async_file_writer, daemon=True)
writer_thread.start()

tracking_url = os.getenv("MLFLOW_TRACKING_URL")
mlflow.set_tracking_uri(tracking_url)

os.environ["MLFLOW_TRACKING_USERNAME"] = "xoxeb69158@heavty.com"
os.environ["MLFLOW_TRACKING_PASSWORD"] = "Gauravkumar007"
os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY_ID") or ""
os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("AWS_SECRET_ACCESS_KEY") or ""
os.environ["MLFLOW_S3_ENDPOINT_URL"] = os.getenv("S3_ENDPOINT") or ""

KAFKA_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
TOPIC = os.getenv("KAFKA_TELEMETRY_TOPIC")
kafka_user = os.getenv("KAFKA_USERNAME")
kafka_pass = os.getenv("KAFKA_PASSWORD")

model_uri = "models:/RailOps_Maintenance_Model/latest"
model = mlflow.sklearn.load_model(model_uri)
has_predict_proba = hasattr(model, "predict_proba")

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=[KAFKA_SERVER],
    group_id="railops_inference_workers",
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    security_protocol="SASL_PLAINTEXT",
    sasl_mechanism="SCRAM-SHA-512",
    sasl_plain_username=kafka_user,
    sasl_plain_password=kafka_pass,
    enable_auto_commit=True  
)

print(f"🎯 Authorized! Watching live tracking feeds on '{TOPIC}'...")

try:
    for message in consumer:
        try:
            sensor_data = message.value
            sensor_data.pop("timestamp_logged", None)

            input_df = pd.DataFrame([sensor_data])

            # ✨ FIX: Clean out ALL structural text fields dynamically 
            # This mirrors the select_dtypes(include=[np.number]) strategy used in model training
            metadata_fields = ["track_id", "section", "timestamp", "assigned_team", "action_taken"]
            model_input_df = input_df.drop(columns=metadata_fields, errors="ignore")
            model_input_df = model_input_df.select_dtypes(include=[np.number])

            # Inference
            prediction = model.predict(model_input_df)[0]
            prob = model.predict_proba(model_input_df)[0][1] if has_predict_proba else float(prediction)

            if prob < 0.30: risk_level = "LOW"
            elif prob < 0.60: risk_level = "MEDIUM"
            elif prob < 0.85: risk_level = "HIGH"
            else: risk_level = "CRITICAL"

            alignment = abs(sensor_data.get("alignment_deviation_mm", 0))
            vibration = sensor_data.get("vibration_hz", 0)
            strain = sensor_data.get("rail_strain_mu", 0)

            if risk_level == "LOW": fault_type = "Normal"
            elif alignment > 4: fault_type = "Track Misalignment"
            elif vibration > 80: fault_type = "Rail Crack"
            elif strain > 160: fault_type = "Structural Stress"
            else: fault_type = "Excessive Wear"

            action_map = {"LOW": "Monitor", "MEDIUM": "Schedule Inspection", "HIGH": "Repair Soon", "CRITICAL": "Immediate Shutdown"}
            recommended_action = action_map[risk_level]

            inspection_status = "Completed" if risk_level == "LOW" else ("Pending" if risk_level == "MEDIUM" else "In Progress")
            status = "🟩 NORMAL" if risk_level == "LOW" else "⚠️ WARNING"

            current_result = {
                "timestamp": sensor_data.get("timestamp"),
                "track_id": sensor_data.get("track_id"),
                "section": sensor_data.get("section"),
                "status": status,
                "prediction": int(prediction),
                "failure_probability": round(float(prob), 2),
                "risk_level": risk_level,
                "fault_type": fault_type,
                "inspection_status": inspection_status,
                "recommended_action": recommended_action,
                "assigned_team": sensor_data.get("assigned_team"),
                "last_maintenance_days": sensor_data.get("last_maintenance_days"),
                "action_taken": sensor_data.get("action_taken"), # Saved seamlessly now!
                "sensor_data": sensor_data
            }

            write_queue.put(current_result)
            print(f"[{risk_level}] {sensor_data.get('track_id')} | {fault_type} | {prob:.2%} | {recommended_action}")

        except Exception as msg_err:
            print(f"❌ Error processing record offset {message.offset}: {msg_err}")
            continue
except KeyboardInterrupt:
    print("\n🛑 Live analysis runtime suspended.")
finally:
    write_queue.put(None)
    writer_thread.join(timeout=3.0)
    consumer.close()
    print("💾 Data collection closed cleanly.")