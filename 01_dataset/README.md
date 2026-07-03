# Step 1 — Vayu Object Storage (Dataset)

**Move-It** › **Vayu Object Storage** · `01_dataset/`

| | |
|---|---|
| **Previous** | [Step 0 — Vayu AI Studio Workspace](../00_vayu_workspaces/) |
| **Next** | [Step 2 — Vayu MLflow →](../02_vayu_mlflow/) |

This step contains the greenhouse crop dataset used to train the irrigation model. If you already have `cropdata.csv` in this folder, you can skip the download. Otherwise, pull it from **Vayu Object Storage (S3)** using the notebook snippets below. S3 credentials are provided in the **Access Guide**.

---

## Folder Contents

| File / Folder | Purpose |
|---------------|---------|
| `cropdata.csv` | Training dataset: soil, crop stage, MOI, temp, humidity, and irrigation label (`result`) |
| `01_dataset.ipynb` | Upload and download snippets for syncing `cropdata.csv` with S3 (boto3) |

---

## Dataset Schema (`cropdata.csv`)

| Column | Description |
|--------|-------------|
| `crop ID` | Crop type (e.g. Wheat) |
| `soil_type` | Soil category (e.g. Black Soil) |
| `Seedling Stage` | Growth stage (e.g. Germination) |
| `MOI` | Moisture of irrigation (numeric) |
| `temp` | Temperature |
| `humidity` | Humidity |
| `result` | Irrigation label (`0` = no irrigation, `1` = irrigate, `2` = excluded during training) |

---

## Quick Start

1. **Check locally:** Open `cropdata.csv` and confirm the columns above are present. If the file is already here, continue to [Step 2](../02_vayu_mlflow/).

2. **Pull from S3 (if needed):** Open [`01_dataset.ipynb`](01_dataset.ipynb), then select the notebook kernel:

   1. Open **Select Kernel** and choose **Python Environments**.

      ![Select Kernel — Python Environments](../assets/kernel_select.png)

   2. Under **Select a Python Environment**, pick the **Recommended** environment (it should point to the `.venv` from [Step 0](../00_vayu_workspaces/)).

      ![Select a Python Environment](../assets/Select_kernerl_env.png)

   3. **Validate the path:** Confirm the selected interpreter path ends with `<your-env-name>/bin/python` (for example, `.venv/bin/python` if you created `.venv` in [Step 0](../00_vayu_workspaces/)).

   Run the **Download Dataset from Vayu Object Storage** cell (credentials load from the root `.env`).

3. **Upload to S3 (optional):** Use the **Upload Dataset to Vayu Object Storage** cell in the same notebook if you want a copy stored in your bucket.

---

## Navigation

| | |
|---|---|
| **Previous** | [Step 0 — Vayu AI Studio Workspace](../00_vayu_workspaces/) |
| **Next** | [Step 2 — Vayu MLflow →](../02_vayu_mlflow/) |
| **Overview** | [Move-It overview](../README.md) |
