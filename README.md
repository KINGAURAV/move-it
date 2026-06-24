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
├── 04_starter-kit/           # Ingestion API (Flask) & ML Training (Notebook)
├── 05_model_registry/        # Model versioning & metadata
├── 06_deploy_model/          # Model deployment to Vayu ML Service
└── 07_build_app/             # Streamlit Dashboard + Integrated Simulator
```

| Step | Vayu service | Folder | What to run / open |
|------|--------------|--------|-------------------|
| 0 | **Vayu Object Storage** | `00_dataset/` | Prepare historical sensor CSVs |
| 1 | **Vayu AI Studio Workspace** | `01_vayu_workspaces/` | `README.md` — setup environment |
| 2 | **Vayu MLflow** | `02_vayu_mlflow/` | `README.md` — track training runs |
| 3 | **Vayu Kafka** | `03_vayu_kafka/` | `README.md` — provision topics |
| 4 | **Data Pipeline & ML Lab** | `04_starter-kit/` | Flask API + Jupyter training notebook |
| 5 | **Vayu Model Registry** | `05_model_registry/` | `README.md` — register trained models |
| 6 | **Vayu ML Service** | `06_deploy_model/` | `README.md` — deploy model endpoint |
| 7 | **Vayu Realtime Inference** | `07_build_app/` | Streamlit Dashboard (with built-in simulator) |

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

1. **Data Ingestion** — Flask API receives HTTP POST from simulated sensors and pushes to Kafka.
2. **ML Pipeline** — Jupyter consumer reads Kafka, processes features, and trains a Random Forest model.
3. **Dashboard** — Streamlit UI displays live telemetry and predictions. Includes a **built-in simulator** to mimic sensor data.

### Minimal run

1. **Set up the environment**
   ```bash
   cd move-it
   pip install -r requirements.txt
   ```

2. **Start the Ingestion API**
   ```bash
   # Ensure your KAFKA_BROKER env var is set
   python 04_starter-kit/ingestion_api.py
   ```

3. **Run Training**
   Open `04_starter-kit/train_model.ipynb` in Vayu AI Studio and run all cells.

4. **Launch Dashboard & Simulator**
   ```bash
   cd 07_build_app
   streamlit run app.py
   ```
   *Once open, click **▶️ Start Simulation** in the sidebar.*

---

## License

Use and modify for the **Vayu Hackathon** submission unless your team repo specifies otherwise.
