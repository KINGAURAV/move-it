# Move-It — Starter Template

## Problem statement and outcome

**Problem:** Traditional greenhouse irrigation often relies on manual scheduling or simple timers, leading to water waste or plant stress due to unpredictable environmental changes. Choose a real usecase (e.g., a smart greenhouse, an automated hydroponics farm, or a vertical urban farm) and a sensor set they care about. Build an end‑to‑end IoT-to-ML pipeline **using the Vayu platform**: simulate sensors (Wokwi ESP32) streaming data via HTTP to a **FastAPI** gateway, ingest data into a **Vayu Kafka** topic, process the stream in a **Vayu AI Studio Workspace** notebook to train a model, and deploy a **Streamlit** dashboard via **Vayu ML Service** that provides real-time monitoring and automated irrigation decisions.

**Outcome:** This starter template demonstrates a complete streaming ML pipeline: sensor data $\to$ HTTP $\to$ Kafka $\to$ Streamlit $\to$ ML Inference. The UI returns real-time telemetry (Temperature, Humidity), predicts water requirements using a trained model (e.g., Random Forest), and visualizes the irrigation action (ON/OFF) in a live dashboard.

---

## Project layout (steps)

```
move-it/
├── README.md
├── requirements.txt
│
├── 00_vayu_workspaces/       # Vayu AI Studio workspace allocation
├── 01_dataset/               # Historical sensor logs for training
├── 02_vayu_mlflow/           # MLflow experiment tracking
├── 03_vayu_kafka/            # Kafka deployment & create_topic.py
├── 04_starter-kit/           # train_model.ipynb — training template
├── 05_model_registry/        # upload_model.py & model registration
├── 06_deploy_model/          # Model deployment to Vayu Model Serving
├── 07_build_app/             # FastAPI ingest + Streamlit dashboard + simulator
└── 08_deploy/                # Build, sign & push container images; deploy via Vayu ML Service
```

| Step | Vayu service | Folder | What to run / open |
|------|--------------|--------|-------------------|
| 0 | **Vayu AI Studio Workspace** | `00_vayu_workspaces/` | `README.md` — create workspace (enable Docker) |
| 1 | **Vayu Object Storage** | `01_dataset/` | `01_dataset.ipynb` — pull/upload dataset from S3 |
| 2 | **Vayu MLflow** | `02_vayu_mlflow/` | `README.md` — deploy managed MLflow |
| 3 | **Vayu Kafka** | `03_vayu_kafka/` | `create_topic.py` — deploy Kafka and create topic |
| 4 | **Data Pipeline & ML Lab** | `04_starter-kit/` | `train_model.ipynb` — train and save `model.joblib` |
| 5 | **Vayu Model Registry** | `05_model_registry/` | `upload_model.py` — upload and register model |
| 6 | **Vayu Model Serving** | `06_deploy_model/` | `README.md` — deploy Predictive AI endpoint |
| 7 | **Vayu Realtime Inference** | `07_build_app/` | FastAPI ingest + Streamlit dashboard (build & run locally) |
| 8 | **Vayu ML Service** | `08_deploy/` | `README.md` — build and sign images, then deploy ingest + dashboard |

---

## Mapping to the Vayu “Move-It — Guided Journey”

| Journey step | How to leverage Vayu ecosystem (detailed) |
|--------------|------------------------------------------|
| **Vayu AI Studio Workspace** | Create your workspace with **Enable Docker in the Workspace** turned on, then clone this repo (`00_vayu_workspaces/`). |
| **Vayu Object Storage** | Pull `cropdata.csv` from S3 if needed, using upload/download snippets in `01_dataset/` (`01_dataset.ipynb`). S3 credentials are in the **Access Guide**. |
| **Vayu MLflow** | Deploy managed MLflow, configure S3 and database, and wait for **Ready** (`02_vayu_mlflow/`). |
| **Vayu Kafka** | Deploy Kafka, run `create_topic.py`, and wait for **Ready** (`03_vayu_kafka/`). Kafka credentials are in the **Access Guide**. |
| **Starter Kit (Training)** | Train with `train_model.ipynb`, log to MLflow, and save `model.joblib` (`04_starter-kit/`). |
| **Vayu Model Registry** | Upload `model.joblib` to S3 and register with sklearn metadata (`05_model_registry/`). |
| **Vayu Model Serving** | Deploy via **Predictive AI**, selecting the registered model and version (`06_deploy_model/`). |
| **Vayu Realtime Inference** | Build and run the Streamlit dashboard locally to validate live sensor trends and predictions (`07_build_app/`). |
| **Vayu ML Service** | Build and sign container images, push to the registry, and deploy ingest + dashboard as ML Services (`08_deploy/`). Container Registry credentials are in the **Access Guide**. |

---

## Tech direction / tools (Vayu ecosystem)

| Layer | Vayu / stack choice |
|--------|---------------------|
| Sensors | **Wokwi ESP32 + DHT22** (Simulated) |
| Ingestion | **FastAPI** $\to$ **Vayu Kafka** |
| Stream Processing | **Jupyter Notebook** (Kafka Consumer) |
| ML Framework | **Scikit-learn (Random Forest)** + **Pandas** |
| Experiment Tracking | **Vayu MLflow** |
| Deployment | **Vayu Model Serving** (Model Endpoint) |
| Dashboard | **Streamlit** |

---

## Quick start

### What this code does

1. **Data Ingestion** — FastAPI gateway (`07_build_app/ingestion_api.py`) receives HTTP POST from the simulator and pushes to Kafka.
2. **ML Pipeline** — Jupyter notebook trains the model (`04_starter-kit/train_model.ipynb`).
3. **Dashboard** — Streamlit UI (`07_build_app/app.py`) consumes Kafka, runs ML inference, and shows live telemetry. Includes a **built-in simulator** (no separate ESP32 required for the demo).

### Minimal run

Shared service credentials for **Vayu Object Storage**, **Vayu Kafka**, and the **Container Registry** are provided in the **Access Guide**.

1. **Set up the environment**

   Complete [Step 0](00_vayu_workspaces/) first (workspace, clone repo). From `/home/jovyan` in your workspace terminal:

   ```bash
   cd /home/jovyan
   python3 -m venv .venv
   source .venv/bin/activate
   cd move-it
   pip install -r requirements.txt
   ```

2. **Create a `.env` file** in the project root (`move-it/.env`) with your Vayu credentials:

   ```bash
   cd /home/jovyan
   cd move-it
   cp .env.example .env
   ```

   Open `.env` and replace the placeholder values with your credentials. Use the **Access Guide** for **Vayu Object Storage (S3)**, **Vayu Kafka**, and **Container Registry** values. Python scripts and notebooks load this file automatically via `load_dotenv`. Do not commit `.env` to git.

   For `IMAGE_REGISTRY`, use the registry **hostname only** (e.g. `image-registry-....cloudservices.tatacommunications.com`) — no `https://`, `http://`, or trailing `/`.

3. **Deploy Vayu MLflow** (required before training)

   Complete [Step 2](02_vayu_mlflow/) — create a managed MLflow instance, wait for **Ready**, and copy the tracking URI and credentials into your `.env` (`MLFLOW_TRACKING_URI`, `MLFLOW_TRACKING_USERNAME`, `MLFLOW_TRACKING_PASSWORD`).

4. **Run training (once)**

   Open `04_starter-kit/train_model.ipynb` in Vayu AI Studio, select the kernel, then run all cells:

   1. Open **Select Kernel** and choose **Python Environments**.

      ![Select Kernel — Python Environments](assets/kernel_select.png)

   2. Under **Select a Python Environment**, pick the **Recommended** environment (it should point to the `.venv` from [Step 0](00_vayu_workspaces/)).

      ![Select a Python Environment](assets/Select_kernerl_env.png)

   3. **Validate the path:** Confirm the selected interpreter path ends with `<your-env-name>/bin/python` (for example, `.venv/bin/python` if you created `.venv` in [Step 0](00_vayu_workspaces/)).

   See [Step 4](04_starter-kit/) for full training details.

5. **Launch the realtime pipeline** (`07_build_app/`)

   **Terminal 1 — ingestion API**
   ```bash
   cd /home/jovyan
   cd move-it/07_build_app
   python ingestion_api.py
   ```

   **Terminal 2 — dashboard + simulator**
   ```bash
   cd /home/jovyan
   cd move-it/07_build_app
   export INGEST_API_URL="http://127.0.0.1:5000/ingest"
   streamlit run app.py
   ```

   Click **Start Simulation** in the Streamlit sidebar.

   **Or deploy to Vayu** — build, sign, and push Docker images in [Step 8](08_deploy/).

---

## License

Use and modify for the **Vayu Hackathon** submission unless your team repo specifies otherwise.
