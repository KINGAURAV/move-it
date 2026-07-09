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

   Open `.env` and replace `<...>` placeholders with your values. The template in [`.env.example`](.env.example) is grouped by step — copy **S3**, **Kafka**, and **Container Registry** from the **Access Guide** as soon as you have it; add **MLflow** after [Step 2](02_vayu_mlflow/). Scripts and notebooks load this file via `load_dotenv`. For [Step 7](07_build_app/) (`app.py`, `ingestion_api.py`), set predict and ingest URLs with `export` in the terminal — see that step’s README. Do not commit `.env` to git.

   **Example** (same shape as [`.env.example`](.env.example)):

   ```bash
   # --- Vayu Object Storage (S3) — Step 1 ---
   AWS_ACCESS_KEY_ID=<your-access-key>
   AWS_SECRET_ACCESS_KEY=<your-secret-key>
   S3_ENDPOINT=<your-s3-endpoint>
   S3_BUCKET_NAME=<your-bucket-name>
   S3_DATASET_KEY=cropdata.csv
   S3_MODEL_KEY=move-it/model.joblib

   # --- Vayu MLflow — Step 2 ---
   MLFLOW_TRACKING_URL=https://<your-mlflow-host>
   MLFLOW_TRACKING_USERNAME=<your-username>
   MLFLOW_TRACKING_PASSWORD=<your-password>

   # --- Vayu Kafka — Step 3 ---
   KAFKA_BROKER=<your-kafka-broker-url>
   KAFKA_USERNAME=<your-kafka-username>
   KAFKA_PASSWORD=<your-kafka-password>
   KAFKA_TOPIC=greenhouse_telemetry

   # --- Vayu Container Registry — Step 8 ---
   IMAGE_REGISTRY=<your-image-registry>
   REGISTRY_PROJECT=<your-registry-project>
   REGISTRY_USERNAME=<container-registry-username>
   REGISTRY_PASSWORD=<container-registry-password>
   VAYU_USERNAME=<your-vayu-username>
   ```

   | Variable(s) | Where to get them |
   |-------------|-------------------|
   | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_ENDPOINT`, `S3_BUCKET_NAME` | **Access Guide** — [Step 1](01_dataset/) (`01_dataset.ipynb`) and [Step 5](05_model_registry/) (`upload_model.py`) |
   | `S3_DATASET_KEY`, `S3_MODEL_KEY` | Defaults in [`.env.example`](.env.example); change only if your team uses different S3 paths |
   | `MLFLOW_TRACKING_URL`, `MLFLOW_TRACKING_USERNAME`, `MLFLOW_TRACKING_PASSWORD` | [Step 2 — Vayu MLflow](02_vayu_mlflow/) — **Connect** page (**Public Endpoint** + credentials set at create time) |
   | `KAFKA_BROKER`, `KAFKA_USERNAME`, `KAFKA_PASSWORD` | **Access Guide** — form `KAFKA_BROKER` as `<IP>:<PORT>`; [Step 3](03_vayu_kafka/) (`create_topic.py`) |
   | `KAFKA_TOPIC` | Default `greenhouse_telemetry`; topic created in [Step 3](03_vayu_kafka/) |
   | `IMAGE_REGISTRY`, `REGISTRY_PROJECT`, `REGISTRY_USERNAME`, `REGISTRY_PASSWORD`, `VAYU_USERNAME` | **Access Guide** — [Step 8](08_deploy/) (build, sign, push images) |

   For `IMAGE_REGISTRY`, use the registry **hostname only** (e.g. `image-registry-....cloudservices.tatacommunications.com`) — no `https://`, `http://`, or trailing `/`.

3. **Deploy Vayu MLflow** (required before training)

   Complete [Step 2](02_vayu_mlflow/) — create a managed MLflow instance, wait for **Ready**, apply **firewall rules**, then on the deployment **Connect** page copy the **Public Endpoint** and credentials into your `.env` (`MLFLOW_TRACKING_URL`, `MLFLOW_TRACKING_USERNAME`, `MLFLOW_TRACKING_PASSWORD`).

4. **Run training (once)**

   Open `04_starter-kit/train_model.ipynb` in Vayu AI Studio, select the kernel, then run all cells:

   1. Open **Select Kernel** and choose **Python Environments**.

      ![Select Kernel — Python Environments](assets/kernel_select.png)

   2. Under **Select a Python Environment**, pick the **Recommended** environment (it should point to the `.venv` from [Step 0](00_vayu_workspaces/)).

      ![Select a Python Environment](assets/Select_kernerl_env.png)

   3. **Validate the path:** Confirm the selected interpreter path ends with `<your-env-name>/bin/python` (for example, `.venv/bin/python` if you created `.venv` in [Step 0](00_vayu_workspaces/)).

   See [Step 4](04_starter-kit/) for full training details.

5. **Prepare services** (complete before `app.py`)

   **Kafka** — [Step 3](03_vayu_kafka/). Skip Kafka deployment if it is already provided; create the topic once Kafka is **Ready**:

   ```bash
   cd /home/jovyan/move-it
   python 03_vayu_kafka/create_topic.py
   ```

   **Model registry** — [Step 5](05_model_registry/). Upload `model.joblib` to S3:

   ```bash
   cd /home/jovyan/move-it
   python 05_model_registry/upload_model.py
   ```

   Then register it in the [Vayu Model Registry](https://ipcloud.tatacommunications.com/aistudio/#/deploy/model-registry-list) UI — see [Step 5](05_model_registry/) for wizard inputs (framework, metadata, S3 prefix, and related settings).

   **Model Serving** — Deploy the registered model on [Vayu Model Serving](https://ipcloud.tatacommunications.com/aistudio/#/deploy/model-serving-list). See [Step 6](06_deploy_model/) for wizard inputs, firewall rules, and full endpoint setup. After the deployment is **Ready** and firewall rules are applied, open the **Connect** tab and **copy the Public Endpoint** shown there, then get `<MODEL_ID>`:

   ```bash
   curl -X GET "<MODEL_SERVING_ENDPOINT>/v1/models"
   ```

   Sample output `{"models":["model"]}` — the id here is `model`. You will `export` the predict URL when starting the dashboard in step 6 below (or set it in the Streamlit sidebar).

6. **Run the realtime pipeline** (`07_build_app/`)

   Start both processes from your workspace terminal. Export runtime variables in each terminal — `app.py` and `ingestion_api.py` do not use `load_dotenv` directly. Kafka settings are read via `kafka_config.py` (which loads root `.env`); for local runs, the Step 7 README also shows explicit `export` commands.

   **Terminal 1 — ingestion API**

   ```bash
   cd /home/jovyan/move-it/07_build_app
   source /home/jovyan/.venv/bin/activate  # (skip if already activated)
   export KAFKA_BROKER="<your-kafka-broker-url>"
   export KAFKA_USERNAME="<your-kafka-username>"
   export KAFKA_PASSWORD="<your-kafka-password>"
   export KAFKA_TOPIC="greenhouse_telemetry"
   python ingestion_api.py
   ```

   **Terminal 2 — dashboard + simulator**

   ```bash
   cd /home/jovyan/move-it/07_build_app
   source /home/jovyan/.venv/bin/activate  # (skip if already activated)
   export INGEST_API_URL="http://127.0.0.1:5000/ingest"
   export KAFKA_BROKER="<your-kafka-broker-url>"
   export KAFKA_USERNAME="<your-kafka-username>"
   export KAFKA_PASSWORD="<your-kafka-password>"
   export KAFKA_TOPIC="greenhouse_telemetry"
   export PREDICT_URL="https://<MODEL_SERVING_ENDPOINT>/v1/models/<MODEL_ID>:predict"
   streamlit run app.py
   ```

   Point the dashboard at Model Serving — pick **one** option below.

   **Option A — Sidebar (host + model name)**  
   Set **Predict host** to the endpoint **without** the trailing `/v1` (e.g. `https://<MODEL_SERVING_ENDPOINT>`) and **Model name** (`<MODEL_ID>`) in the sidebar. The dashboard builds `https://<...>/v1/models/<MODEL_ID>:predict`.

   **Option B — Export `PREDICT_URL`**  
   `export PREDICT_URL=...` before `streamlit run` (as in Terminal 2 above). Sidebar predict fields are ignored when this is set.

   **Option C — Export host + model name**  
   `export VAYU_PREDICT_HOST=...` and `export VAYU_MODEL_NAME=<MODEL_ID>` to pre-fill the sidebar instead of `PREDICT_URL`.

   > **Tip:** The Model Serving UI often copies only through `/v1` (e.g. `https://<MODEL_SERVING_ENDPOINT>/v1`). For Option A or C, drop the `/v1` suffix from the host; for Option B, append `/models/<MODEL_ID>:predict` to the copied **Public Endpoint**. Get `<MODEL_ID>` from `curl -X GET .../v1/models` — see [Step 6](06_deploy_model/) or the **Model Serving** section above.

   Confirm the resolved URL under **Predict endpoint ready** in the sidebar, then click **Start Simulation** to stream simulated sensor readings through ingest → Kafka → predictions → the live dashboard.

   **Or deploy to Vayu** — build, sign, and push Docker images in [Step 8](08_deploy/).

</details>

---

<details>
<summary><h3>📄 License</h3></summary>

Use and modify for the **Vayu Hackathon** submission unless your team repo specifies otherwise.

</details>
