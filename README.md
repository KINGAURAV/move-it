# Move-It — Starter Template

## Problem statement and outcome

**Problem:** Traditional greenhouse irrigation often relies on manual scheduling or simple timers, leading to water waste or plant stress due to unpredictable environmental changes. Choose a real usecase (e.g., a smart greenhouse, an automated hydroponics farm, or a vertical urban farm) and a sensor set they care about. Build an end‑to‑end IoT-to-ML pipeline **using the Vayu platform**: simulate sensors (Wokwi ESP32) streaming data via HTTP to a **Flask API**, ingest data into a **Vayu Kafka** topic, process the stream in a **Vayu AI Studio** notebook to train a model, and deploy a **Streamlit** dashboard that provides real-time monitoring and automated irrigation decisions.

**Outcome:** This starter template demonstrates a complete streaming ML pipeline: sensor data $\to$ HTTP $\to$ Kafka $\to$ Streamlit $\to$ ML Inference. The UI returns real-time telemetry (Temperature, Humidity), predicts water requirements using a trained model (e.g., Random Forest), and visualizes the irrigation action (ON/OFF) in a live dashboard.

### System Architecture

```text
Wokwi ESP32 + DHT22 (Simulated)
        │
        ▼
Temperature, Humidity (Telemetry)
        │
        ▼
HTTP POST (Ingestion Gateway)
        │
        ▼
Vayu Kafka Topic (Streaming Buffer)
        │
        ▼
Jupyter Notebook Consumer (Real-time Processing)
        │
        ▼
Pandas DataFrame (Feature Engineering)
        │
        ▼
Random Forest Model (ML Inference)
        │
        ▼
Water Requirement Prediction & Irrigation Action
```

---

## Project layout (steps)

```
move-it/
├── README.md
├── requirements.txt
│
├── 00_dataset/               # Historical sensor logs for training
├── 01_vayu_workspaces/       # Vayu AI Studio workspace allocation
├── 02_vayu_mlflow/           # MLflow experiment tracking
├── 03_vayu_kafka/            # Kafka topic configuration & streaming
├── 04_starter-kit/           # ML training notebook
├── 05_model_registry/        # Model versioning & metadata
├── 06_deploy_model/          # Model deployment to Vayu ML Service
└── 07_build_app/             # FastAPI ingest + Streamlit dashboard + simulator
```

| Step | Vayu service | Folder | What to run / open |
|------|--------------|--------|-------------------|
| 0 | **Vayu Object Storage** | `00_dataset/` | Prepare historical sensor CSVs |
| 1 | **Vayu AI Studio Workspace** | `01_vayu_workspaces/` | `README.md` — setup environment |
| 2 | **Vayu MLflow** | `02_vayu_mlflow/` | `README.md` — track training runs |
| 3 | **Vayu Kafka** | `03_vayu_kafka/` | `README.md` — provision topics |
| 4 | **Data Pipeline & ML Lab** | `04_starter-kit/` | Jupyter training notebook (`train_model.ipynb`) |
| 5 | **Vayu Model Registry** | `05_model_registry/` | `README.md` — register trained models |
| 6 | **Vayu ML Service** | `06_deploy_model/` | `README.md` — deploy model endpoint |
| 7 | **Vayu Realtime Inference** | `07_build_app/` | FastAPI ingest + Streamlit dashboard (built-in simulator) |

---

## Mapping to the Vayu “Move-It — Guided Journey”

| Journey step | How to leverage Vayu ecosystem (detailed) |
|--------------|------------------------------------------|
| **Vayu Object Storage** | Store historical sensor CSVs so **Vayu AI Studio** notebooks can read them during training (`00_dataset/`). |
| **Vayu AI Studio Workspace** | Open Jupyter notebooks for Kafka consumption and Random Forest training (`04_starter-kit/`). |
| **Vayu MLflow** | Log parameters (e.g., `max_depth`) and metrics (e.g., `accuracy`) during training (`02_vayu_mlflow/`). |
| **Vayu Kafka** | Act as the high-throughput buffer between the Flask API and the ML consumer (`03_vayu_kafka/`). |
| **Vayu Model Registry** | Save and version your trained `.joblib` models (`05_model_registry/`). |
| **Vayu ML Service** | Serve the prediction model as a REST API for the dashboard/actuators (`06_deploy_model/`). |
| **Vayu Realtime Inference** | Host the Streamlit dashboard to visualize live sensor trends and predictions (`07_build_app/`). |

---

## Tech direction / tools (Vayu ecosystem)

| Layer | Vayu / stack choice |
|--------|---------------------|
| Sensors | **Wokwi ESP32 + DHT22** (Simulated) |
| Ingestion | **Flask API** $\to$ **Vayu Kafka** |
| Stream Processing | **Jupyter Notebook** (Kafka Consumer) |
| ML Framework | **Scikit-learn (Random Forest)** + **Pandas** |
| Experiment Tracking | **Vayu MLflow** |
| Deployment | **Vayu ML Service** (Model Endpoint) |
| Dashboard | **Streamlit** |

---

## Quick start

### What this code does

1. **Data Ingestion** — FastAPI gateway (`07_build_app/ingestion_api.py`) receives HTTP POST from the simulator and pushes to Kafka.
2. **ML Pipeline** — Jupyter notebook trains the model (`04_starter-kit/train_model.ipynb`).
3. **Dashboard** — Streamlit UI (`07_build_app/app.py`) consumes Kafka, runs ML inference, and shows live telemetry. Includes a **built-in simulator** (no separate ESP32 required for the demo).

### Minimal run

1. **Set up the environment**
   ```bash
   cd move-it
   pip install -r requirements.txt
   ```

2. **Run training (once)**
   Open `04_starter-kit/train_model.ipynb` in Vayu AI Studio and run all cells.

3. **Launch the realtime pipeline** (`07_build_app/`)

   **Terminal 1 — ingestion API**
   ```bash
   cd 07_build_app
   export KAFKA_BROKER="<VAYU_KAFKA_BROKER>"
   export KAFKA_USER="<VAYU_KAFKA_USER>"
   export KAFKA_PASS="<VAYU_KAFKA_PASS>"
   python ingestion_api.py
   ```

   **Terminal 2 — dashboard + simulator**
   ```bash
   cd 07_build_app
   export INGEST_API_URL="http://127.0.0.1:5000/ingest"
   export KAFKA_BROKER="<VAYU_KAFKA_BROKER>"
   export KAFKA_USER="<VAYU_KAFKA_USER>"
   export KAFKA_PASS="<VAYU_KAFKA_PASS>"
   streamlit run app.py
   ```

   Click **Start Simulation** in the Streamlit sidebar.

   **Or run both in one Docker container** — see [`07_build_app/README.md`](07_build_app/README.md).

---

## License

Use and modify for the **Vayu Hackathon** submission unless your team repo specifies otherwise.
