# 🧪 Step 4 — Starter Kit (Training)

**Move-It** › **Starter Kit** · `04_starter-kit/`

| [← Previous — Step 3 — Vayu Kafka](../03_vayu_kafka/) | [Next — Step 5 — Model Registry →](../05_model_registry/) |
|:---|---:|

This step provides a training template to build your irrigation model, log metrics and parameters to **Vayu MLflow**, and save the trained artifact locally.

---

<details>
<summary><h3>📂 Folder contents</h3></summary>

| File | Description |
|------|-------------|
| `train_model.ipynb` | Train a logistic regression model, log to MLflow, save `model.joblib` |

</details>

---

<details>
<summary><h3>📋 Prerequisites</h3></summary>

| Step | Vayu Service / Folder | Requirements |
|------|-----------------------|--------------|
| 0 | `00_vayu_workspaces/` | Active Python environment |
| 1 | `01_dataset/` | `cropdata.csv` available locally |
| 2 | `02_vayu_mlflow/` | MLflow deployment **Ready** |
| 3 | `03_vayu_kafka/` | Kafka deployment **Ready** (optional for training) |

Install dependencies:

![Setting up venv and installing dependencies](../assets/install.png)

</details>

---

<details>
<summary><h3>🚀 Quick start</h3></summary>

1. **Open the training notebook:** `04_starter-kit/train_model.ipynb` in your Vayu AI Studio workspace, then select the kernel:

   1. Open **Select Kernel** and choose **Python Environments**.

      ![Select Kernel — Python Environments](../assets/kernel_select.png)

   2. Under **Select a Python Environment**, pick the **Recommended** environment (it should point to the `.venv` from [Step 0](../00_vayu_workspaces/)).

      ![Select a Python Environment](../assets/Select_kernerl_env.png)

   3. **Validate the path:** Confirm the selected interpreter path ends with `<your-env-name>/bin/python` (for example, `.venv/bin/python` if you created `.venv` in [Step 0](../00_vayu_workspaces/)).

2. **Configure MLflow in `.env`:** Set `MLFLOW_TRACKING_URI`, `MLFLOW_TRACKING_USERNAME`, and `MLFLOW_TRACKING_PASSWORD` in the root `.env` (see [overview](../README.md)).
3. **Run all cells:** The notebook trains the model, logs parameters and metrics to MLflow, and saves the artifact to `04_starter-kit/model.joblib`.
4. **Continue to registration:** Proceed to [Step 5](../05_model_registry/) to upload and register the model.

</details>

---

| [← Previous — Step 3 — Vayu Kafka](../03_vayu_kafka/) | [Overview](../README.md) | [Next — Step 5 — Model Registry →](../05_model_registry/) |
|:---|:---:|---:|
