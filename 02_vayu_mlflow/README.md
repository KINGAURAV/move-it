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

For the full create wizard (Start → Infrastructure → Compute → Object Storage → Database → Review), see the [Managed MLflow documentation](https://ipcloud.tatacommunications.com/docs/docs/user-docs/vayu-ai-studio/managed-mlflow/#creating-managed-mlflow).

---

## Quick Start

1. **Deploy Vayu MLflow:** Create a new managed MLflow deployment on the [Vayu MLflow](https://ipcloud.tatacommunications.com/aistudio/#/experiment/managed-mlflow-list) page. Follow the [creating Managed MLflow guide](https://ipcloud.tatacommunications.com/docs/docs/user-docs/vayu-ai-studio/managed-mlflow/#creating-managed-mlflow) for step-by-step wizard details.
2. **Configure S3 and database:** Fill in your object storage (S3) credentials and database settings in the deployment wizard.
3. **Wait for Ready:** Submit the deployment and wait until the status shows **Ready**.
4. **Note the tracking URI:** You will use this URI in [Step 4](../04_starter-kit/) when training and logging runs.

---

## Navigation

| | |
|---|---|
| **Previous** | [← Step 1 — Vayu Object Storage](../01_dataset/) |
| **Next**     | [Step 3 — Vayu Kafka →](../03_vayu_kafka/) |
| **Overview** | [Move-It overview](../README.md) |
