# 📈 Step 2 — Vayu MLflow

**Move-It** › **Vayu MLflow** · `02_vayu_mlflow/`

| [← Previous — Step 1 — Vayu Object Storage](../01_dataset/) | [Next — Step 3 — Vayu Kafka →](../03_vayu_kafka/) |
|:---|---:|

Deploy a managed **Vayu MLflow** instance to track training experiments, parameters, and metrics in later steps.

---

<details>
<summary><h3>🔗 Open MLflow</h3></summary>

Go to [Vayu MLflow](https://ipcloud.tatacommunications.com/aistudio/#/experiment/managed-mlflow-list).

For the full create wizard (Start → Infrastructure → Compute → Object Storage → Database → Review), see the [Creating Managed MLflow guide](https://ipcloud.tatacommunications.com/docs/docs/user-docs/vayu-ai-studio/managed-mlflow/#creating-managed-mlflow).

</details>

---

<details>
<summary><h3>🚀 Quick start</h3></summary>

1. **Deploy Vayu MLflow:** Create a new managed MLflow deployment on the [Vayu MLflow](https://ipcloud.tatacommunications.com/aistudio/#/experiment/managed-mlflow-list) page. Follow the [Creating Managed MLflow guide](https://ipcloud.tatacommunications.com/docs/docs/user-docs/vayu-ai-studio/managed-mlflow/#creating-managed-mlflow) for step-by-step wizard details. During creation:
   - **Object storage host alias:** On the **Object Storage** step, add a **host alias** for object storage using the **IP** and **endpoint** from the **Access Guide**. Enter the endpoint as the hostname **only** — do not include `http://` or `https://`.
   - **Public Expose:** Enable **Public Expose** in the deployment wizard.
   - **Enable authentication:** Turn on **Enable Authentication** and set a **Username** and **Password**. You will need these credentials to access the MLflow UI and to populate `MLFLOW_TRACKING_USERNAME` and `MLFLOW_TRACKING_PASSWORD` in your root `.env`.
   - **Configure S3 and database:** Fill in your object storage (S3) credentials and database settings. S3 connection details are provided in the **Access Guide**.
2. **Wait for Ready:** Submit the deployment and wait until the status shows **Ready**.
3. **Note the tracking URI and credentials:** On the deployment **Connect** page, copy the **Public Endpoint**, username, and password into the root `.env` as `MLFLOW_TRACKING_URL`, `MLFLOW_TRACKING_USERNAME`, and `MLFLOW_TRACKING_PASSWORD` — you will use these in [Step 4](../04_starter-kit/).
4. **Firewall rules:** Configure firewall rules so external clients can reach the MLflow **Public Endpoint**. Follow the **Firewall rules SOP** shared with your team.

</details>

---

#### Resources

- [Creating Managed MLflow guide](https://ipcloud.tatacommunications.com/docs/docs/user-docs/vayu-ai-studio/managed-mlflow/#creating-managed-mlflow)
- **Firewall rules SOP** — follow the SOP shared with your team

---

| [← Previous — Step 1 — Vayu Object Storage](../01_dataset/) | [Overview](../README.md) | [Next — Step 3 — Vayu Kafka →](../03_vayu_kafka/) |
|:---|:---:|---:|
