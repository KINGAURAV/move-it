# Step 8 — Deploy Move-It (Streamlit Dashboard)

**Move-It** › **Vayu Realtime Inference** · `07_build_app/`

| | |
|---|---|
| **⬅ Previous** | [Step 7 — Build app & Docker image](../07_build_app/) |
| **🏁 Next** | — (journey complete) |
| **🏠 Overview** | [Move-It overview](../README.md) |

This step takes the **Streamlit IoT Dashboard** you built in [Step 7](../07_build_app/) and runs it on the **Vayu platform** as an **ML Service**. After deployment, you get a **hosted endpoint URL** so judges can view live telemetry, see water requirement predictions, and watch the automated irrigation simulator in real-time without running Streamlit locally.

---

## What you are deploying

| Piece | Where it lives |
|-------|----------------|
| **IoT Dashboard UI** | Docker image (`move-it-dash:latest`) from [`07_build_app/Dockerfile`](../07_build_app/Dockerfile) |
| **Prediction Engine** | **Vayu Model Serving** — calls your hosted sklearn endpoint via HTTP POST |
| **Telemetry Stream** | **Vayu Kafka** — the dashboard consumes or simulates the sensor stream |

The dashboard is a "live monitor." It connects to your deployed model to provide real-time decision support (e.g., "Irrigation: ON") based on incoming sensor telemetry.

---

## Prerequisites

Complete these steps first:

| Step | Folder | You need |
|------|--------|----------|
| 3 | [`03_vayu_kafka/`](../03_vayu_kafka/) | Kafka topics provisioned |
| 4 | [`04_starter-kit/`](../04_starter-kit/) | Ingestion API working |
| 5 | [`05_model_registry/`](../05_model_registry/) | Model registered |
| 6 | [`06_deploy_model/`](../06_deploy_model/) | **Predict URL** (e.g., `http://<host>:<port>/v1/models/<name>:predict`) |
| 7 | [`07_build_app/`](../07_build_app/) | Image built and pushed to **Vayu Hackathon Container Registry** |

**Before Step 8:** Test your dashboard locally using the built-in simulator in [Step 7](../07_build_app/README.md) to ensure the connection to the model endpoint works.

---

## Step 1 — Build and push the Docker image

Build context **must** be `move-it/` (not `07_build_app/`). Full details: [`07_build_app/README.md](../07_build_app/README.md).

```bash
# 1. Navigate to the project root
cd vayu-hackathon/move-it

# 2. Build the image
docker build -f 07_build_app/Dockerfile -t move-it-dash:latest .

# 3. Tag and push to the registry (Replace <registry-host> with your actual host)
docker tag move-it-dash:latest <registry-host>/move-it-dash:latest
docker login <registry-host>
docker push <registry-host>/move-it-dash:latest
```

Note the full image reference you pushed (e.g. `<registry-host>/move-it-dash:latest`) — you will enter it in the ML Service wizard.

---

## Step 2 — Open Vayu ML Services

In AI Studio: **Deploy** → **ML Services** → **Create ML Service**.

---

## Step 3 — Create the ML Service (wizard)

Follow the platform wizard. Map **Move-It** settings as below.

### 3.1 Start — image and runtime

| Field | Move-It value |
|-------|----------------|
| **Name** | e.g. `move-it-dashboard` |
| **Framework** | **Streamlit** |
| **Private Registry → Registry URL** | Your hackathon / Vayu registry host |
| **Private Registry → Image** | Full image you pushed, e.g. `<registry-host>/move-it-dash:latest` |
| **Private Registry → Username / Password** | Registry credentials |
| **Port** | **8501** |
| **Public Expose** | **Enable** (essential for the demo) |

### 3.2 Environment variables (required)

Add the connection details so your dashboard can talk to the prediction engine:

| Key | Required | Source |
|-----|----------|--------|
| `PREDICT_URL` | **Yes** | [Step 6 — Deploy Model](../06_deploy_model/) |
| `KAFKA_BROKER` | Recommended | Your Vayu Kafka endpoint |

**Example Configuration:**

```text
PREDICT_URL="http://<INGRESS_HOST>:<PORT>/v1/models/<MODEL_NAME>:predict"
KAFKA_BROKER="your-vayu-kafka-broker:9092"
```

### 3.3 Infrastructure & Compute

| Field | Guidance |
|-------|----------|
| **Resources / flavor** | The dashboard is lightweight. **CPU** is sufficient. |
| **Replicas** | `1` for demo |

---

## Step 4 — Get the endpoint and verify

1.  Open **ML Services List** → click your service **Name**.
2.  On **View ML Service**, find the **Public URL**.
3.  Open the URL in a browser. You should see the **Move-It IoT Dashboard**.
4.  **Test the Monitoring**:
    *   Click **▶️ Start Simulation** in the sidebar.
    *   Verify that telemetry (Temperature/Humidity) is updating.
    *   Verify that the **Irrigation Action** (ON/OFF) changes based on the model predictions.

| Symptom | What to check |
|---------|----------------|
| Page does not load | Port **8501**, **Public Expose**, pod status **ready** |
| "Connection Error" on prediction | `PREDICT_URL` is incorrect or the Model Service is down |
| Dashboard shows no data | Check `KAFKA_BROKER` env var and ensure your ingestion API is running |
| Predictions are static | Check if the simulation is actually running in the UI |

---

## Demo Checklist (submission-ready)

- [ ] Dashboard successfully connects to the Vayu Model Serving endpoint.
- [ ] **Live Stream**: Simulator is running and displaying real-time telemetry.
- [ ] **Inference**: Predictions (Irrigation ON/OFF) are correctly displayed based on sensor data.
- [ ] Docker image built from `move-it/` and pushed to registry.
- [ ] ML Service **ready** with port **8501** and all env vars set.
- [ ] Public/demo URL opens the dashboard and is documented for judges.

---

## Pro Tips

- **Simulator vs. Real Sensors**: For the hackathon demo, use the **Built-in Simulator** to ensure consistent, clean data. If using real sensors, ensure your **Ingestion API** is running and pushing to the correct Kafka topic.
- **The "Inference Lag"**: If predictions feel slow, check the latency of your **Vayu Model Serving** endpoint.
- **Never commit secrets**: Keep your `PREDICT_URL` and Kafka credentials out of your git repo; set them in the ML Service UI.
