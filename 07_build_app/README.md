# Step 7 — Build App (Realtime Dashboard)

**Move-It** › **Streamlit Dashboard** · `07_build_app/`

| | |
|---|---|
| **Previous** | [Step 6 — Deploy Model](../06_deploy_model/) |
| **Next** | [Step 8 — Deploy to Vayu →](../08_deploy/) |

Run the **full real-time pipeline** locally, or build Docker images for [Step 8](../08_deploy/) (two separate ML Services: ingest first, dashboard second).

---

## Pipeline flow

```text
Start Simulation (app.py)
        │
        ▼
POST /ingest  (ingestion_api.py — FastAPI, port 5000)
        │
        ▼
Vayu Kafka topic (greenhouse_telemetry)
        │
        ▼
Kafka consumer (app.py background thread)
        │
        ▼
HTTP POST → Vayu Model Serving (predict URL from Step 6)
        │
        ▼
Live dashboard (Streamlit, port 8501)
```

---

## What each file does

### `ingestion_api.py` — HTTP → Kafka gateway

A small **FastAPI** service that receives sensor readings and publishes them to **Vayu Kafka**.

| Endpoint | Purpose |
|----------|---------|
| `POST /ingest` | Accept `{temp, humidity, MOI, timestamp?}` and publish to Kafka |
| `GET /health` | Health check (broker + topic) |
| `GET /docs` | Swagger UI |

It does **not** run ML or show a UI. Think: **HTTP in → Kafka out**.

Runs on port **5000** by default (`PORT` env var).

### `app.py` — Dashboard + simulator + Model Serving client

The **Streamlit** app users interact with. It does four things:

### Dockerfiles

| File | Deploy as | Port | Contents |
|------|-----------|------|----------|
| `Dockerfile.ingest` | **ML Service 1** — ingest API | **5000** | `ingestion_api.py`, `kafka_config.py` |
| `Dockerfile.dashboard` | **ML Service 2** — dashboard | **8501** | `app.py`, `kafka_config.py`, `cropdata.csv` |

---

## Prerequisites

Complete [Steps 0–6](../README.md) first. For this step you need:

- Python 3.11+
- **Vayu Kafka** credentials and topic ([Step 3](../03_vayu_kafka/))
- **Vayu Model Serving** predict endpoint ([Step 6](../06_deploy_model/))
- `01_dataset/cropdata.csv` (for feature preprocessing only)

```bash
cd move-it
pip install -r requirements.txt
```

---

## Run locally (two terminals)

Both processes must run together.

**Terminal 1 — Ingestion API**

```bash
cd move-it/07_build_app

export KAFKA_BROKER="<VAYU_KAFKA_BROKER>"
export KAFKA_USER="<VAYU_KAFKA_USER>"
export KAFKA_PASS="<VAYU_KAFKA_PASS>"
export KAFKA_TOPIC="greenhouse_telemetry"

python ingestion_api.py
```

Verify: `curl http://127.0.0.1:5000/health`

**Terminal 2 — Dashboard**

```bash
cd move-it/07_build_app

export INGEST_API_URL="http://127.0.0.1:5000/ingest"
export KAFKA_BROKER="<VAYU_KAFKA_BROKER>"
export KAFKA_USER="<VAYU_KAFKA_USER>"
export KAFKA_PASS="<VAYU_KAFKA_PASS>"
export KAFKA_TOPIC="greenhouse_telemetry"

# Predict URL from Step 6 (required for simulation)
export PREDICT_URL="http://<host>:<port>/v1/models/<model-name>:predict"

streamlit run app.py
```

Open the URL Streamlit prints (usually `http://localhost:8501`). You can also set **Predict host** and **Model name** in the sidebar instead of `PREDICT_URL`, then click **Start Simulation**.

---

## Build Docker images

Build from the **`move-it/`** root (not `07_build_app/`).

### Production — two images for Vayu ML Service

```bash
cd move-it

docker build -f 07_build_app/Dockerfile.ingest -t move-it-ingest:latest .
docker build -f 07_build_app/Dockerfile.dashboard -t move-it-dashboard:latest .

docker tag move-it-ingest:latest <registry-host>/move-it-ingest:latest
docker tag move-it-dashboard:latest <registry-host>/move-it-dashboard:latest
docker push <registry-host>/move-it-ingest:latest
docker push <registry-host>/move-it-dashboard:latest
```

Deploy **ingest first**, then **dashboard** with `INGEST_API_URL` set to the ingest public URL — see [Step 8](../08_deploy/).

### Local — single container (optional)

```bash
docker build -f 07_build_app/Dockerfile -t move-it-local:latest .
docker run --rm -p 8501:8501 -p 5000:5000 \
  -e KAFKA_BROKER="..." -e KAFKA_USER="..." -e KAFKA_PASS="..." \
  -e PREDICT_URL="..." \
  move-it-local:latest
```

---

## Environment variables

| Variable | Required | Default | Used by | Purpose |
|----------|----------|---------|---------|---------|
| `PREDICT_URL` | **Yes** | — | dashboard | Model Serving predict URL from [Step 6](../06_deploy_model/) |
| `KAFKA_BROKER` | **Yes** | — | ingest + dashboard | Kafka bootstrap servers |
| `KAFKA_USER` | **Yes** | — | ingest + dashboard | Kafka SASL username |
| `KAFKA_PASS` | **Yes** | — | ingest + dashboard | Kafka SASL password |
| `KAFKA_TOPIC` | No | `greenhouse_telemetry` | ingest + dashboard | Telemetry topic |
| `INGEST_API_URL` | No | `http://127.0.0.1:5000/ingest` | dashboard | Simulator POST target |
| `PORT` | No | `5000` | ingestion API | Ingest listen port |

For local testing, **Predict host** and **Model name** in the sidebar can be used instead of `PREDICT_URL` when the env var is not set.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Sidebar shows **Kafka: Disconnected** | Check `KAFKA_BROKER` / `KAFKA_USER` / `KAFKA_PASS`; confirm topic exists |
| **Set predict host/model or PREDICT_URL** | Set `PREDICT_URL` or fill **Predict host** + **Model name** in the sidebar |
| Prediction errors | Confirm Model Serving is **Ready** and the predict URL from [Step 6](../06_deploy_model/) is correct |
| Simulation errors / JSON parse failures | Set `INGEST_API_URL=http://127.0.0.1:5000/ingest` — avoid Jupyter/codeserver proxy URLs |
| Ingest logs missing but Streamlit says "Sent" | Start `ingestion_api.py` first |
| UI stuck on "Waiting" | Click **Start Simulation**; check sidebar **Buffered predictions** |
| Preprocessing error | Ensure `01_dataset/cropdata.csv` exists (included in Docker image) |

---

## Navigation

| | |
|---|---|
| **Previous** | [Step 6 — Deploy Model](../06_deploy_model/) |
| **Next** | [Step 8 — Deploy to Vayu →](../08_deploy/) |
| **Overview** | [Move-It overview](../README.md) |
