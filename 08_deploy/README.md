# Step 8 — Deploy Move-It (Streamlit Dashboard)

**Move-It** › **Vayu ML Service** · `07_build_app/`

| | |
|---|---|
| **⬅ Previous** | [Step 7 — Build app & Docker image](../07_build_app/) |
| **🏁 Next** | — (journey complete) |
| **🏠 Overview** | [Move-It overview](../README.md) |

Deploy the **Move-It dashboard** (Streamlit + co-located ingest API) to the **Vayu platform** as an **ML Service**. After deployment you get a **public URL** where judges can run the built-in simulator, see live telemetry, and watch irrigation predictions from your **Vayu Model Serving** endpoint.

---

## What you are deploying

The Docker image from [`07_build_app/Dockerfile`](../07_build_app/Dockerfile) runs **two processes** in one container:

| Process | Port | Role |
|---------|------|------|
| **Streamlit** (`app.py`) | **8501** | Dashboard, simulator, Kafka consumer, Model Serving client |
| **FastAPI ingest** (`ingestion_api.py`) | **5000** | `POST /ingest` → Vayu Kafka (used internally by the simulator) |

| Connection | Source |
|------------|--------|
| **Predictions** | **Vayu Model Serving** — HTTP POST from `app.py` ([Step 6](../06_deploy_model/)) |
| **Telemetry stream** | **Vayu Kafka** — ingest publishes; dashboard consumes ([Step 3](../03_vayu_kafka/)) |
| **Preprocessing** | `01_dataset/cropdata.csv` baked into the image (feature encoding only; model is remote) |

---

## Prerequisites

| Step | Folder | You need |
|------|--------|----------|
| 3 | [`03_vayu_kafka/`](../03_vayu_kafka/) | Kafka **Ready**, topic created |
| 4 | [`04_starter-kit/`](../04_starter-kit/) | Model trained (`model.joblib`) |
| 5 | [`05_model_registry/`](../05_model_registry/) | Model registered in registry |
| 6 | [`06_deploy_model/`](../06_deploy_model/) | Model Serving **Ready** — predict URL |
| 7 | [`07_build_app/`](../07_build_app/) | App tested locally; image built and pushed to registry |

**Before Step 8:** Run the dashboard locally ([Step 7](../07_build_app/README.md)) with **Start Simulation** and confirm predictions reach Model Serving.

---

## Step 1 — Build and push the Docker image

Build context **must** be `move-it/` (not `07_build_app/`). Details: [`07_build_app/README.md`](../07_build_app/README.md).

```bash
cd move-it

docker build -f 07_build_app/Dockerfile -t move-it-dash:latest .

docker tag move-it-dash:latest <registry-host>/move-it-dash:latest
docker login <registry-host>
docker push <registry-host>/move-it-dash:latest
```

Note the full image reference (e.g. `<registry-host>/move-it-dash:latest`) for the ML Service wizard.

---

## Step 2 — Open Vayu ML Services

Go to [Vayu ML Services](https://ipcloud.tatacommunications.com/aistudio/#/deploy/mlops-service-list) to create a new deployment.

---

## Step 3 — Create the ML Service (wizard)

### 3.1 Start — image and runtime

| Field | Move-It value |
|-------|----------------|
| **Name** | e.g. `move-it-dashboard` |
| **Framework** | **Streamlit** |
| **Private Registry → Registry URL** | Your hackathon / Vayu registry host |
| **Private Registry → Image** | e.g. `<registry-host>/move-it-dash:latest` |
| **Private Registry → Username / Password** | Registry credentials |
| **Port** | **8501** |
| **Public Expose** | **Enable** (required for the demo) |

### 3.2 Environment variables

Set these in the ML Service wizard:

| Key | Required | Description |
|-----|----------|-------------|
| `PREDICT_URL` | **Yes** | Full predict URL from [Step 6](../06_deploy_model/), e.g. `http://<host>:<port>/v1/models/<name>:predict` |
| `KAFKA_BROKER` | **Yes** | Vayu Kafka bootstrap servers |
| `KAFKA_USER` | **Yes** | Kafka SASL username |
| `KAFKA_PASS` | **Yes** | Kafka SASL password |
| `KAFKA_TOPIC` | No | Default: `greenhouse_telemetry` |

**Example:**

```text
PREDICT_URL=http://<INGRESS_HOST>:<PORT>/v1/models/<MODEL_NAME>:predict
KAFKA_BROKER=<VAYU_KAFKA_BROKER>
KAFKA_USER=<VAYU_KAFKA_USER>
KAFKA_PASS=<VAYU_KAFKA_PASS>
KAFKA_TOPIC=greenhouse_telemetry
```

`INGEST_API_URL` defaults to `http://127.0.0.1:5000/ingest` inside the container — the simulator talks to the co-located ingest API automatically.

### 3.3 Infrastructure & compute

| Field | Guidance |
|-------|----------|
| **Resources / flavor** | Lightweight — **CPU** is sufficient |
| **Replicas** | `1` for demo |

---

## Step 4 — Verify the deployment

1. Open [Vayu ML Services](https://ipcloud.tatacommunications.com/aistudio/#/deploy/mlops-service-list) → click your service name.
2. Copy the **Public URL** and open it in a browser.
3. Confirm the **Move-It IoT Dashboard** loads.
4. Click **Start Simulation** in the sidebar.
5. Verify temperature/humidity update and **Irrigation Action** changes from Model Serving predictions.

| Symptom | What to check |
|---------|----------------|
| Page does not load | Port **8501**, **Public Expose**, pod status **Ready** |
| Predict endpoint error | `PREDICT_URL`; Model Serving status **Ready** |
| Kafka disconnected | `KAFKA_BROKER`, `KAFKA_USER`, `KAFKA_PASS`; topic exists |
| Simulation sends but no predictions | `PREDICT_URL` matches your Step 6 endpoint |
| UI stuck on "Waiting" | Click **Start Simulation**; check sidebar prediction errors |

---

## Demo checklist

- [ ] Dashboard connects to **Vayu Model Serving** via `PREDICT_URL`.
- [ ] **Live stream:** simulator running; telemetry updating.
- [ ] **Inference:** irrigation ON/OFF reflects model output.
- [ ] Docker image built from `move-it/` root and pushed to registry.
- [ ] ML Service **Ready** on port **8501** with env vars set.
- [ ] Public URL documented for judges.

---

## Pro tips

- Use the **built-in simulator** for a reliable hackathon demo; real sensors need the ingest API reachable on port 5000 inside the pod (already started by the container `CMD`).
- If predictions are slow, check **Vayu Model Serving** latency separately from the dashboard.
- Never commit secrets — set `PREDICT_URL` and Kafka credentials in the ML Service UI only.
