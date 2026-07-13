import os
import json
import time
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from kafka import KafkaProducer
from kafka.errors import KafkaError

base_dir = Path(__file__).resolve().parent.parent
env_path = base_dir / ".env"
load_dotenv(env_path, override=True)

KAFKA_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
TOPIC = os.getenv("KAFKA_TELEMETRY_TOPIC")
USERNAME = os.getenv("KAFKA_USERNAME")
PASSWORD = os.getenv("KAFKA_PASSWORD")

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_SERVER],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    security_protocol="SASL_PLAINTEXT",
    sasl_mechanism="SCRAM-SHA-512",
    sasl_plain_username=USERNAME,
    sasl_plain_password=PASSWORD,
    request_timeout_ms=15000,
    connections_max_idle_ms=60000,
    retries=3,
)

# Force metadata check
producer.partitions_for(TOPIC)

dataset_path = base_dir / "01_dataset" / "downloaded_railway_telemetry.csv"
df = pd.read_csv(dataset_path)

if "timestamp" in df.columns:
    df["timestamp"] = df["timestamp"].astype(str)

print(f"🚀 Streaming {len(df)} records to topic '{TOPIC}'...\n")

try:
    for index, row in df.iterrows():
        payload = {}
        for key, value in row.items():
            if pd.isna(value):
                payload[key] = None
            else:
                # Convert numpy types explicitly to native Python types for clean JSON encoding
                payload[key] = value.item() if hasattr(value, "item") else value

        # Tracking metrics
        payload["timestamp_logged"] = time.time()
        track_id = payload.get("track_id", "UNKNOWN")
        risk_level = payload.get("risk_level", "UNKNOWN")
        fault_type = payload.get("fault_type", "UNKNOWN")

        # ✨ FIX: We DO NOT pop structural telemetry attributes like action_taken or assigned_team.
        # We only drop pure ML output fields that the consumer recalculates.
        payload.pop("failure_probability", None)
        payload.pop("risk_level", None)
        payload.pop("fault_type", None)
        payload.pop("inspection_status", None)
        payload.pop("recommended_action", None)

        future = producer.send(TOPIC, payload)
        metadata = future.get(timeout=20)

        print(f"🚆 {track_id} | {risk_level} | {fault_type} | Partition={metadata.partition} Offset={metadata.offset}")
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\n🛑 Streaming stopped by user.")
finally:
    producer.flush()
    producer.close()