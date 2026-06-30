# Step 8 — Deploy Move-It (Two ML Services)

**Move-It** › **Vayu ML Service** · `07_build_app/`

| | |
|---|---|
| **⬅ Previous** | [Step 7 — Build app](../07_build_app/) |
| **🏁 Next** | — (journey complete) |
| **🏠 Overview** | [Move-It overview](../README.md) |

Deploy the **Move-It dashboard** (Streamlit + co-located ingest API) to the **Vayu platform** as an **ML Service**. After deployment you get a **public URL** where judges can run the built-in simulator, see live telemetry, and watch irrigation predictions from your **Vayu Model Serving** endpoint.

1. **Ingest API** (`ingestion_api.py`) — HTTP → Kafka  
2. **Dashboard** (`app.py`) — simulator, Kafka consumer, Model Serving client, Streamlit UI  

Deploy **ingest first**, copy its public URL, then deploy the dashboard with `INGEST_API_URL` pointing at it.

---

## Architecture

```text
ML Service 2 — Dashboard (:8501)     app.py · simulator
        │
        │  POST /ingest
        ▼
ML Service 1 — Ingest (:5000)        ingestion_api.py
        │
        ▼
Vayu Kafka — greenhouse_telemetry (Step 3)
        │
        │  Kafka consumer (app.py)
        ▼
ML Service 2 — Dashboard (:8501)
        │
        │  POST predict
        ▼
Vayu Model Serving (Step 6)
```

| Service | Image | Port | Framework |
|---------|-------|------|-----------|
| **move-it-ingest** | `Dockerfile.ingest` | **5000** | **Python3** (CMD runs uvicorn) |
| **move-it-dashboard** | `Dockerfile.dashboard` | **8501** | **Streamlit** |

---

## Prerequisites

| Step | Folder | You need |
|------|--------|----------|
| 3 | [`03_vayu_kafka/`](../03_vayu_kafka/) | Kafka **Ready**, topic created |
| 6 | [`06_deploy_model/`](../06_deploy_model/) | Model Serving **Ready** — predict URL |
| 7 | [`07_build_app/`](../07_build_app/) | Tested locally |
| — | Container registry | Registry username and CLI secret ([Container Registry guide](https://ipcloud.tatacommunications.com/docs/docs/user-docs/vayu-ai-studio/registry/)) |

**Before Step 8:** Run locally with two terminals ([Step 7](../07_build_app/README.md)) and confirm **Start Simulation** works.

---

## Folder Contents

| File | Purpose |
|------|---------|
| [`sign_image.py`](sign_image.py) | Download `tcl-cosign`, fetch signing certs, sign or verify an image |

---

## Step 1 — Build and push both images

Build context **must** be `move-it/` (not `07_build_app/`). You build **two images** — one per ML Service:

| Image tag | Dockerfile | Port | Purpose |
|-----------|------------|------|---------|
| `<image-registry>/<project>/move-it-ingest:latest` | `Dockerfile.ingest` | **5000** | **Ingest API** — FastAPI (`ingestion_api.py`) publishes sensor readings to **Vayu Kafka**. Deploy **first**. |
| `<image-registry>/<project>/move-it-dashboard:latest` | `Dockerfile.dashboard` | **8501** | **Dashboard** — Streamlit (`app.py`) with simulator, Kafka consumer, and Model Serving client. Deploy **second**. |

For registry login and push details, see the [Container Registry guide](https://ipcloud.tatacommunications.com/docs/docs/user-docs/vayu-ai-studio/registry/). Set `IMAGE_REGISTRY`, `REGISTRY_PROJECT`, `REGISTRY_USERNAME`, and `REGISTRY_PASSWORD` in the root [`.env`](../README.md). Image tags use the form `$IMAGE_REGISTRY/$REGISTRY_PROJECT/<image-name>:latest`.

```bash
cd move-it
set -a && source .env && set +a && echo "$REGISTRY_PASSWORD" | docker login "$IMAGE_REGISTRY" -u "$REGISTRY_USERNAME" --password-stdin

docker build -f 07_build_app/Dockerfile.ingest -t $IMAGE_REGISTRY/$REGISTRY_PROJECT/move-it-ingest:latest --push .
docker build -f 07_build_app/Dockerfile.dashboard -t $IMAGE_REGISTRY/$REGISTRY_PROJECT/move-it-dashboard:latest --push .
```

---

## Step 2 — Sign both images

Vayu ML Services require **signed** container images. Sign **each** image after push — repeat this step once for ingest and once for dashboard.

See the [Container Registry guide](https://ipcloud.tatacommunications.com/docs/docs/user-docs/vayu-ai-studio/registry/) for background (credentials, OIDC flow, and troubleshooting).

[`sign_image.py`](sign_image.py) automates the setup: it downloads `tcl-cosign` to the repo root, creates `08_deploy/image-signing/`, fetches the Sigstore certificates, and runs `tcl-cosign`.

[`sign_image.py`](sign_image.py) loads registry credentials from the root `.env` via `load_dotenv`. Export `IMAGE` for the image you are signing (ingest or dashboard).

**Sign the ingest image:**

```bash
cd move-it
set -a && source .env && set +a

export IMAGE=$IMAGE_REGISTRY/$REGISTRY_PROJECT/move-it-ingest:latest

python 08_deploy/sign_image.py sign
```

**Sign the dashboard image:**

```bash
export IMAGE=$IMAGE_REGISTRY/$REGISTRY_PROJECT/move-it-dashboard:latest
python 08_deploy/sign_image.py sign
```

Follow the browser prompt during signing (copy the authorization code when redirected).

**Verify (optional, repeat per image):**

```bash
export IMAGE=$IMAGE_REGISTRY/$REGISTRY_PROJECT/move-it-ingest:latest
python 08_deploy/sign_image.py verify
```

| Variable | Used for | Source |
|----------|----------|--------|
| `IMAGE_REGISTRY` | build + sign + verify | Root `.env` — registry host from your Vayu user profile |
| `REGISTRY_PROJECT` | build + sign + verify | Root `.env` — registry project name (between host and image repo) |
| `IMAGE` | sign + verify | Export per run: `$IMAGE_REGISTRY/$REGISTRY_PROJECT/move-it-ingest:latest` or `.../move-it-dashboard:latest` |
| `REGISTRY_USERNAME` | sign + verify + `docker login` | Root `.env` — container registry username |
| `REGISTRY_PASSWORD` | sign + verify + `docker login` | Root `.env` — container registry CLI secret |
| `VAYU_USERNAME` | verify only | Root `.env` — your Vayu username (certificate identity) |

---

## Step 3 — Open Vayu ML Services

Go to [Vayu ML Services](https://ipcloud.tatacommunications.com/aistudio/#/deploy/mlops-service-list).

For the full create wizard (Start → Infrastructure → Configure Compute → Observability → Review), see the [Creating ML Service guide](https://ipcloud.tatacommunications.com/docs/docs/user-docs/vayu-ai-studio/ml-service/#creating-ml-service).

---

## Phase A — Deploy ingest API (first)

### A.1 Start — image and runtime

| Field | Value |
|-------|-------|
| **Name** | e.g. `move-it-ingest` |
| **Framework** | **Python3** |
| **Image** | `<image-registry>/<project>/move-it-ingest:latest` |
| **Port** | **5000** |
| **Public Expose** | **Enable** |

### A.2 Environment variables

| Key | Required |
|-----|----------|
| `KAFKA_BROKER` | Yes |
| `KAFKA_USER` | Yes |
| `KAFKA_PASS` | Yes |
| `KAFKA_TOPIC` | No (default `greenhouse_telemetry`) |

### A.3 Verify ingest

When status is **Ready**, note the **Public URL** (call it `<INGEST_PUBLIC_URL>`).

```bash
curl -s "<INGEST_PUBLIC_URL>/health"
curl -s -X POST "<INGEST_PUBLIC_URL>/ingest" \
  -H "Content-Type: application/json" \
  -d '{"temp": 25.0, "humidity": 60.0, "MOI": 10.0}'
```

Both should return JSON with `"status": "ok"`. Swagger UI: `<INGEST_PUBLIC_URL>/docs`.

Set **`INGEST_API_URL=<INGEST_PUBLIC_URL>/ingest`** for Phase B (include the `/ingest` path).

---

## Phase B — Deploy dashboard (second)

### B.1 Start — image and runtime

| Field | Value |
|-------|-------|
| **Name** | e.g. `move-it-dashboard` |
| **Framework** | **Streamlit** |
| **Image** | `<image-registry>/<project>/move-it-dashboard:latest` |
| **Port** | **8501** |
| **Public Expose** | **Enable** |

### B.2 Environment variables

| Key | Required | Description |
|-----|----------|-------------|
| `INGEST_API_URL` | **Yes** | Phase A URL, e.g. `https://<ingest-host>/ingest` |
| `PREDICT_URL` | **Yes** | From [Step 6](../06_deploy_model/) |
| `KAFKA_BROKER` | Yes | Same broker as ingest |
| `KAFKA_USER` | Yes | |
| `KAFKA_PASS` | Yes | |
| `KAFKA_TOPIC` | No | Default `greenhouse_telemetry` |

**Example:**

```text
INGEST_API_URL=https://<INGEST_PUBLIC_HOST>/ingest
PREDICT_URL=http://<INGRESS_HOST>:<PORT>/v1/models/<MODEL_NAME>:predict
KAFKA_BROKER=<VAYU_KAFKA_BROKER>
KAFKA_USER=<VAYU_KAFKA_USER>
KAFKA_PASS=<VAYU_KAFKA_PASS>
KAFKA_TOPIC=greenhouse_telemetry
```

### B.3 Infrastructure

| Field | Guidance |
|-------|----------|
| **Resources** | CPU is sufficient |
| **Replicas** | `1` for demo |

---

## Step 4 — Verify end-to-end

1. Open the **dashboard** public URL (port 8501).
2. Sidebar should show your **ingest public URL** (not `127.0.0.1`).
3. Confirm **Kafka: Connected**.
4. Click **Start Simulation**.
5. Verify temperature/humidity update and **Irrigation Action** from Model Serving.

| Symptom | What to check |
|---------|----------------|
| Ingest `/health` fails | Port **5000**, **Public Expose**, pod **Ready** |
| Dashboard page won't load | Port **8501**, **Public Expose** |
| Simulation error / JSON parse | `INGEST_API_URL` must be the **ingest public URL** from Phase A |
| Sidebar still shows `127.0.0.1` | `INGEST_API_URL` not set on dashboard ML Service |
| Kafka disconnected | Same `KAFKA_*` on both services; topic exists |
| No predictions | `PREDICT_URL`; Model Serving **Ready** |

---

## Demo checklist

- [ ] **Ingest** ML Service **Ready** on port **5000**; `/health` and `/ingest` work publicly  
- [ ] **Dashboard** ML Service **Ready** on port **8501** with `INGEST_API_URL` + `PREDICT_URL`  
- [ ] **Start Simulation** updates telemetry and irrigation predictions  
- [ ] Both images pushed and **signed** from `move-it/` root  
- [ ] Public URLs documented for judges  

---

## Pro tips

- Use the **built-in simulator** for a reliable hackathon demo; real sensors need the ingest API reachable on port 5000 inside the pod (already started by the container `CMD`).
- If predictions are slow, check **Vayu Model Serving** latency separately from the dashboard.
- Never commit secrets — set `PREDICT_URL` and Kafka credentials in the ML Service UI only.
