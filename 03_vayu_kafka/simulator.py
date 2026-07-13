import time
import pandas as pd
import requests

# Target the local FastAPI gateway endpoint
GATEWAY_URL = "http://localhost:8000/api/v1/telemetry"
CSV_PATH = "/home/jovyan/move-it/01_dataset/downloaded_railway_telemetry.csv"

print(f"📖 Reading dataset telemetry from: {CSV_PATH}")
df = pd.read_csv(CSV_PATH)

if 'failure_probability' in df.columns:
    df = df.drop(columns=['failure_probability'])

print(f"🎬 Commencing HTTP telemetry stream to gateway: {GATEWAY_URL}...")

try:
    for idx, row in df.iterrows():
        payload = row.to_dict()
        payload['timestamp_logged'] = time.time()
        
        try:
            # Post data to FastAPI instead of direct Kafka link
            response = requests.post(GATEWAY_URL, json=payload, timeout=5)
            if response.status_code == 200:
                print(f"🚀 Sent via Gateway -> Frame {idx} | Vibration: {payload.get('vibration_hz', 'N/A')}")
            else:
                print(f"⚠️ Gateway rejected packet: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Gateway unreachable: {e}")
            
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\n🛑 Telemetry stream simulator suspended.")