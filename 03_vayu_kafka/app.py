import os
import json
import queue
import threading
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from kafka import KafkaProducer
from dotenv import load_dotenv
from pathlib import Path

# Load configurations
base_dir = Path(__file__).resolve().parent.parent
env_path = base_dir / ".env"
load_dotenv(env_path, override=True)

KAFKA_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
TOPIC = os.getenv("KAFKA_TELEMETRY_TOPIC", "telemetry-in")
kafka_user = os.getenv("KAFKA_USERNAME")
kafka_pass = os.getenv("KAFKA_PASSWORD")

app = FastAPI(title="Vayu RailOps Telemetry Gateway")

# ⚡ Local fast in-memory queue to instantly offload requests
data_queue = queue.Queue()

def kafka_worker_loop():
    """An independent thread loop that manages its own connection isolated from Uvicorn."""
    print("📡 [Worker] Initializing dedicated Kafka connection...")
    try:
        worker_producer = KafkaProducer(
            bootstrap_servers=[KAFKA_SERVER],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            api_version=(2, 5, 0),
            security_protocol="SASL_PLAINTEXT",
            sasl_mechanism="PLAIN",
            sasl_plain_username=kafka_user,
            sasl_plain_password=kafka_pass,
            bootstrap_timeout_ms=10000,
            max_block_ms=10000
        )
        print("🟩 [Worker] Isolated Kafka Producer connected and active!")
    except Exception as e:
        print(f"❌ [Worker] Failed to connect Kafka: {e}")
        return

    while True:
        try:
            # Wait indefinitely for data to drop into the local queue
            data = data_queue.get()
            worker_producer.send(TOPIC, value=data)
            worker_producer.flush()
            data_queue.task_done()
        except Exception as ex:
            print(f"⚠️ [Worker] Streaming alert: {ex}")

# Fire up the worker thread immediately on startup
threading.Thread(target=kafka_worker_loop, daemon=True).start()

class TelemetryPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/v1/telemetry")
def receive_telemetry(payload: TelemetryPayload):
    try:
        data = payload.model_dump()
        
        # ⚡ FAST PATH: Drop data into local memory and instantly reply 200 OK
        data_queue.put(data)
        
        return {"status": "ACCEPTED", "queue_size": data_queue.qsize()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)