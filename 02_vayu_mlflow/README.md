# Step 2 — Vayu MLflow

**Move-It** › **Vayu MLflow** · `02_vayu_mlflow/`

| | |
|---|---|
| **Previous** | [← Step 1 — Vayu Object Storage](../01_dataset/) |
| **Next**     | [Step 3 — Vayu Kafka →](../03_vayu_kafka/) |

Deploy a managed **Vayu MLflow** instance to track training experiments, parameters, and metrics in later steps.

---

## Open MLflow

Go to [Vayu MLflow](https://ipcloud.tatacommunications.com/aistudio/#/experiment/managed-mlflow-list).

For the full create wizard (Start → Infrastructure → Compute → Object Storage → Database → Review), see the [Creating Managed MLflow guide](https://ipcloud.tatacommunications.com/docs/docs/user-docs/vayu-ai-studio/managed-mlflow/#creating-managed-mlflow).

---

## Quick Start

1. **Deploy Vayu MLflow:** Create a new managed MLflow deployment on the [Vayu MLflow](https://ipcloud.tatacommunications.com/aistudio/#/experiment/managed-mlflow-list) page. Follow the [Creating Managed MLflow guide](https://ipcloud.tatacommunications.com/docs/docs/user-docs/vayu-ai-studio/managed-mlflow/#creating-managed-mlflow) for step-by-step wizard details.
2. **Enable authentication:** In the deployment wizard, turn on **Enable Authentication** and set a **Username** and **Password**. You will need these credentials to access the MLflow UI and to populate `MLFLOW_TRACKING_USERNAME` and `MLFLOW_TRACKING_PASSWORD` in your root `.env`.
3. **Configure S3 and database:** Fill in your object storage (S3) credentials and database settings in the deployment wizard. S3 connection details are provided in the **Access Guide**. On the **Object Storage** step, add a **host alias** for object storage using the **IP** and **endpoint** from the **Access Guide**. Enter the endpoint as the hostname **only** — do not include `http://` or `https://`.
4. **Wait for Ready:** Submit the deployment and wait until the status shows **Ready**.
5. **Note the tracking URI and credentials:** Copy the host URL, username, and password into the root `.env` as `MLFLOW_TRACKING_URI`, `MLFLOW_TRACKING_USERNAME`, and `MLFLOW_TRACKING_PASSWORD` — you will use these in [Step 4](../04_starter-kit/).

---

## Navigation

| | |
|---|---|
| **Previous** | [← Step 1 — Vayu Object Storage](../01_dataset/) |
| **Next**     | [Step 3 — Vayu Kafka →](../03_vayu_kafka/) |
| **Overview** | [Move-It overview](../README.md) |
