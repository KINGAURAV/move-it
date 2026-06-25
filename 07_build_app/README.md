# Step 7 — Build App (Realtime Dashboard)

**Move-It** › **Streamlit Dashboard** · `07_build_app/`

| | |
|---|---|
| **Previous** | [Step 6 — Deploy Model](../06_deploy_model/) |
| **Next** | — (journey complete) |

The final step runs the **full real-time pipeline** locally or in Docker:

```text
Start Simulation (Streamlit)
        │
        ▼
POST /ingest  (ingestion_api.py — FastAPI, port 5000)
        │
        ▼
Vayu Kafka topic (greenhouse_telemetry)
        │
        ▼
Kafka consumer + ML predict (app.py background thread)
        │
        ▼
Live dashboard (Streamlit, port 8501)
```

This mirrors a real deployment: sensors (or the built-in simulator) POST telemetry to an HTTP gateway, data flows through Kafka, and the dashboard consumes the stream for irrigation predictions.

---

## What's In This Step?

| File | Role |
|------|------|
| `ingestion_api.py` | FastAPI gateway — `POST /ingest` publishes `{temp, humidity, MOI, timestamp}` to Kafka |
| `app.py` | Streamlit UI — built-in sensor simulator, Kafka consumer, ML inference, live charts |
| `kafka_config.py` | Shared Kafka producer/consumer settings (SASL SCRAM) |
| `Dockerfile` | Single image running **both** services |

The app trains a logistic-regression model from `../00_dataset/cropdata.csv` on first startup (cached). No pre-built `.joblib` is required in the repo.

---

## Prerequisites

- Python 3.11+
- Vayu Kafka credentials (`KAFKA_BROKER`, `KAFKA_USER`, `KAFKA_PASS`)
- Dependencies from the project root:

```bash
cd move-it
pip install -r requirements.txt
```

---

## Run locally (two terminals)

Both processes must run together — the simulator in Streamlit POSTs to the ingest API.

**Terminal 1 — Ingestion API**

```bash
cd move-it/07_build_app

export KAFKA_BROKER="<VAYU_KAFKA_BROKER>"
export KAFKA_USER="<VAYU_KAFKA_USER>"
export KAFKA_PASS="<VAYU_KAFKA_PASS>"
export KAFKA_TOPIC="greenhouse_telemetry"

python ingestion_api.py
# or: uvicorn ingestion_api:app --host 0.0.0.0 --port 5000
```

Verify: `curl http://127.0.0.1:5000/health`

**Terminal 2 — Dashboard**

```bash
cd move-it/07_build_app

# Use localhost ingest — not a codeserver/Jupyter proxy URL
export INGEST_API_URL="http://127.0.0.1:5000/ingest"
export KAFKA_BROKER="<VAYU_KAFKA_BROKER>"
export KAFKA_USER="<VAYU_KAFKA_USER>"
export KAFKA_PASS="<VAYU_KAFKA_PASS>"

streamlit run app.py
```

Open the URL Streamlit prints (usually `http://localhost:8501`), then click **Start Simulation** in the sidebar.

---

## Run with Docker (single container)

Build from the `move-it/` root (not this folder):

```bash
cd move-it
docker build -f 07_build_app/Dockerfile -t move-it:latest .
```

Run:

```bash
docker run --rm -p 8501:8501 -p 5000:5000 \
  -e KAFKA_BROKER="<VAYU_KAFKA_BROKER>" \
  -e KAFKA_USER="<VAYU_KAFKA_USER>" \
  -e KAFKA_PASS="<VAYU_KAFKA_PASS>" \
  -e KAFKA_TOPIC="greenhouse_telemetry" \
  move-it:latest
```

| Port | Service |
|------|---------|
| `8501` | Streamlit dashboard |
| `5000` | FastAPI ingest (`/ingest`, `/health`, `/docs`) |

Inside the container, `INGEST_API_URL` defaults to `http://127.0.0.1:5000/ingest` so the simulator talks to the co-located ingest API.

> **Note:** `CMD` uses `uvicorn ... & exec streamlit ...` — not `&&`. Both servers are long-running; `&&` would start only uvicorn and never reach Streamlit. The ingest API runs in the background; Streamlit stays in the foreground as PID 1.

---

## Environment variables

| Variable | Default | Used by |
|----------|---------|---------|
| `KAFKA_BROKER` | — | ingest + dashboard |
| `KAFKA_USER` | — | ingest + dashboard |
| `KAFKA_PASS` | — | ingest + dashboard |
| `KAFKA_TOPIC` | `greenhouse_telemetry` | ingest + dashboard |
| `KAFKA_GROUP_ID` | `streamlit_consumer_group` | dashboard consumer |
| `INGEST_API_URL` | `http://127.0.0.1:5000/ingest` | dashboard simulator |
| `PORT` | `5000` | ingestion API listen port |
| `DEBUG_PREDICT` | unset | set to `1` for verbose prediction logs |

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Sidebar shows **Kafka: Disconnected** | Check `KAFKA_BROKER` / credentials; confirm topic exists |
| Simulation errors / JSON parse failures | Set `INGEST_API_URL=http://127.0.0.1:5000/ingest` — avoid Jupyter/codeserver proxy URLs |
| Ingest logs missing but Streamlit says "Sent" | Ingest API is not running — start `ingestion_api.py` first |
| UI stuck on "Waiting" | Click **Start Simulation**; check sidebar **Buffered predictions** count |
| Model load error | Ensure `00_dataset/cropdata.csv` exists (included in Docker image) |

---

## Navigation

| | |
|---|---|
| **Previous** | [Step 6 — Deploy Model](../06_deploy_model/) |
| **Next** | — (journey complete) |
| **Overview** | [Move-It overview](../README.md) |
