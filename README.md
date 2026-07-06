# 🌱 Move-It — Starter Template

![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![FastAPI](https://img.shields.io/badge/Gateway-FastAPI-009688?logo=fastapi&logoColor=white)
![Kafka](https://img.shields.io/badge/Streaming-Kafka-231F20?logo=apachekafka&logoColor=white)
![scikit-learn](https://img.shields.io/badge/Model-scikit--learn-F7931E?logo=scikitlearn&logoColor=white)
![Docker](https://img.shields.io/badge/Container-Docker-2496ED?logo=docker&logoColor=white)
![Deploy](https://img.shields.io/badge/Deploy-Vayu%20ML%20Service-0EA5E9)

## 🎯 Problem statement and outcome

**Problem:** Traditional greenhouse irrigation often relies on manual scheduling or simple timers, leading to water waste or plant stress due to unpredictable environmental changes. Choose a real usecase (e.g., a smart greenhouse, an automated hydroponics farm, or a vertical urban farm) and a sensor set they care about. Build an end‑to‑end IoT-to-ML pipeline **using the Vayu platform**: simulate sensors (Wokwi ESP32) streaming data via HTTP to a **FastAPI** gateway, ingest data into a **Vayu Kafka** topic, process the stream in a **Vayu AI Studio Workspace** notebook to train a model, and deploy a **Streamlit** dashboard via **Vayu ML Service** that provides real-time monitoring and automated irrigation decisions.

**Outcome:** This starter template demonstrates a complete streaming ML pipeline: sensor data $\to$ HTTP $\to$ Kafka $\to$ Streamlit $\to$ ML Inference. The UI returns real-time telemetry (Temperature, Humidity), predicts water requirements using a trained model (e.g., Random Forest), and visualizes the irrigation action (ON/OFF) in a live dashboard.

---

## 🗺️ Journey at a glance

Shared service credentials for **Vayu Object Storage**, **Vayu Kafka**, and the **Container Registry** are provided in the **Access Guide**.

| Step | Vayu service | Folder | Role in the stack | How you wire it up |
|------|--------------|--------|-------------------|--------------------|
| 0 | **Vayu AI Studio Workspace** | [`00_vayu_workspaces/`](00_vayu_workspaces/) | Compute environment (Vayu AI Studio notebooks) | Create the workspace with **Enable Docker** turned on, then clone this repo — see the folder `README.md`. |
| 1 | **Vayu Object Storage** | [`01_dataset/`](01_dataset/) | Data — historical greenhouse sensor logs (`cropdata.csv`) | Pull or upload `cropdata.csv` from S3 with `01_dataset.ipynb`; S3 credentials in the Access Guide. |
| 2 | **Vayu MLflow** | [`02_vayu_mlflow/`](02_vayu_mlflow/) | Experiment tracking | Deploy managed MLflow, configure S3 + database, and wait for **Ready** — see the folder `README.md`. |
| 3 | **Vayu Kafka** | [`03_vayu_kafka/`](03_vayu_kafka/) | Ingestion buffer — **FastAPI → Vayu Kafka** streaming | Deploy Kafka, run `create_topic.py`, and wait for **Ready**; Kafka credentials in the Access Guide. |
| 4 | **Data Pipeline & ML Lab** | [`04_starter-kit/`](04_starter-kit/) | ML training — **Scikit-learn (Random Forest)** + **Pandas** in Jupyter | Train with `train_model.ipynb`, log to MLflow, and save `model.joblib`. |
| 5 | **Vayu Model Registry** | [`05_model_registry/`](05_model_registry/) | Model versioning | Upload `model.joblib` to S3 and register with sklearn metadata via `upload_model.py`. |
| 6 | **Vayu Model Serving** | [`06_deploy_model/`](06_deploy_model/) | Deployment — model prediction endpoint | Deploy via **Predictive AI**, selecting the registered model and version — see the folder `README.md`. |
| 7 | **Vayu Realtime Inference** | [`07_build_app/`](07_build_app/) | Sensors (**Wokwi ESP32 + DHT22**, simulated), ingest gateway (**FastAPI**), Kafka consumer, and **Streamlit** dashboard | Build and run the FastAPI ingest + Streamlit dashboard locally to validate live sensor trends and predictions. |
| 8 | **Vayu ML Service** | [`08_deploy/`](08_deploy/) | Hosting — two **Vayu ML Services** | Build and sign container images, push to the registry, then deploy ingest + dashboard as ML Services; Container Registry credentials in the Access Guide. |

---

<details>
<summary><h3>🧱 Project layout</h3></summary>

```text
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

</details>

---

<details>
<summary><h3>⚡ Quick start</h3></summary>

### What this code does

1. **Data Ingestion** — FastAPI gateway (`07_build_app/ingestion_api.py`) receives HTTP POST from the simulator and pushes to Kafka.
2. **ML Pipeline** — Jupyter notebook trains the model (`04_starter-kit/train_model.ipynb`).
3. **Dashboard** — Streamlit UI (`07_build_app/app.py`) consumes Kafka, runs ML inference, and shows live telemetry. Includes a **built-in simulator** (no separate ESP32 required for the demo).

### Minimal run

Shared service credentials for **Vayu Object Storage**, **Vayu Kafka**, and the **Container Registry** are provided in the **Access Guide**.

1. **Set up the environment**

   Complete [Step 0](00_vayu_workspaces/) first (create workspace, enable Docker). From `/home/jovyan` in your workspace terminal:

   ```bash
   cd /home/jovyan
   git clone https://ailab.cloudservices.tatacommunications.com/code/vayu-hackathon/move-it.git
   python3 -m venv .venv
   source .venv/bin/activate
   cd move-it
   pip install -r requirements.txt
   ```

   Skip `git clone` if the repo is already present under `/home/jovyan/move-it`.

2. **Create a `.env` file** in the project root (`move-it/.env`) with your Vayu credentials:

   ```bash
   cd /home/jovyan/move-it
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
   cd /home/jovyan/move-it/07_build_app
   python ingestion_api.py
   ```

   **Terminal 2 — dashboard + simulator**
   ```bash
   cd /home/jovyan/move-it/07_build_app
   export INGEST_API_URL="http://127.0.0.1:5000/ingest"
   streamlit run app.py
   ```

   Click **Start Simulation** in the Streamlit sidebar.

   **Or deploy to Vayu** — build, sign, and push Docker images in [Step 8](08_deploy/).

</details>

---

<details>
<summary><h3>📄 License</h3></summary>

Use and modify for the **Vayu Hackathon** submission unless your team repo specifies otherwise.

</details>
