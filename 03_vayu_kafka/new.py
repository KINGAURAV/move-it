import os
import json
import pandas as pd
from pathlib import Path
import mlflow
import mlflow.sklearn
from kafka import KafkaConsumer
from dotenv import load_dotenv
import json
from pathlib import Path

OUTPUT_FILE = Path("latest_prediction.json")
def save_prediction(result):
    """Safely save the latest prediction to disk."""
    with open(OUTPUT_FILE, "w") as f:
        json.dump(result, f, indent=4)
        f.flush()          # Flush Python buffer
        os.fsync(f.fileno())  # Force write to disk
        
# 1. Safely resolve paths and load your provided .env parameters
base_dir = Path(__file__).resolve().parent.parent
env_path = base_dir / ".env"
load_dotenv(env_path, override=True)

# 2. Hardcode tracking parameters explicitly for the MLflow Client
tracking_url = os.getenv("MLFLOW_TRACKING_URL")
username = "xoxeb69158@heavty.com"
password = "Gauravkumar007"

# Force credentials into the process environment space
os.environ["MLFLOW_TRACKING_URI"] = tracking_url or ""
os.environ["MLFLOW_TRACKING_USERNAME"] = username
os.environ["MLFLOW_TRACKING_PASSWORD"] = password

# 3. Extract your explicit S3 Object Storage parameters from .env
s3_endpoint = os.getenv("S3_ENDPOINT")
aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

# Map them explicitly to MLflow's native backend storage requirements
os.environ["AWS_ACCESS_KEY_ID"] = aws_access_key or ""
os.environ["AWS_SECRET_ACCESS_KEY"] = aws_secret_key or ""
os.environ["MLFLOW_S3_ENDPOINT_URL"] = s3_endpoint or ""

# 4. Extract Kafka broker parameters from .env
KAFKA_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
TOPIC = os.getenv("KAFKA_TELEMETRY_TOPIC")
kafka_user = os.getenv("KAFKA_USERNAME")
kafka_pass = os.getenv("KAFKA_PASSWORD")

# 5. Connect global session tracking schema
mlflow.set_tracking_uri(tracking_url)

print(f"🛰️ Syncing connection layers with Tata Vayu Tracking Engine...")
print("🧠 Fetching inference engine layout asset from registry...")

# 6. Pull the model using the registry identifier
model_uri = "models:/RailOps_Maintenance_Model/latest"
model = mlflow.sklearn.load_model(model_uri)
print("✅ Remote production model loaded successfully into consumer memory.")

# 7. Initialize Authenticated Kafka Pipeline Consumer 
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=[KAFKA_SERVER],
    group_id="railops_inference_workers",
    auto_offset_reset='latest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    #api_version=(2, 5, 0),  
    security_protocol="SASL_PLAINTEXT",
    sasl_mechanism="SCRAM-SHA-512",
    sasl_plain_username=kafka_user,
    sasl_plain_password=kafka_pass,
    bootstrap_timeout_ms=10000
)

print(f"🎯 Authorized! Watching live tracking feeds on '{TOPIC}'...")

try:
    for message in consumer:
        sensor_data = message.value
        sensor_data.pop('timestamp_logged', None)
        
        input_df = pd.DataFrame([sensor_data])
        prediction = model.predict(input_df)[0]
        prob = model.predict_proba(input_df)[0][1] if hasattr(model, "predict_proba") else None
        
        status = "⚠️ WARNING" if prediction == 1 or (prob and prob > 0.7) else "🟩 NORMAL"
        prob_str = f" ({prob:.2%})" if prob is not None else ""
        
        print(f"[{status}] Telemetry Analyzed{prob_str} | Data: {sensor_data}")
        result = {  "status": status,
                     "probability": float(prob) if prob is not None else None,
                     "prediction": int(prediction),
                     "sensor_data": sensor_data}


        with open(OUTPUT_FILE, "w") as f:
            json.dump(result, f, indent=4)
except KeyboardInterrupt:
    print("\n🛑 Live analysis runtime suspended.")
finally:
    consumer.close()