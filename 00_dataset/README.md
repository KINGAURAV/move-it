# Step 0 — Vayu Object Storage (Dataset)

**Move-It** › **Vayu Object Storage** · `00_dataset/`

| | |
|---|---|
| **Previous** | [Move-It overview](../README.md) |
| **Next** | [Step 1 — Vayu AI Studio Workspace →](../01_vayu_workspaces/) |

Welcome to the **Move-It** project! This step contains the greenhouse crop dataset used to train the irrigation model, plus a notebook to sync it with **Vayu Object Storage**.

---

## Folder Contents

| File / Folder | Purpose |
|---------------|---------|
| `cropdata.csv` | Training dataset: soil, crop stage, MOI, temp, humidity, and irrigation label (`result`) |
| `00_dataset.ipynb` | Jupyter notebook: upload/download `cropdata.csv` to/from an S3 bucket (boto3) |

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

Live telemetry in later steps only streams `temp`, `humidity`, and `MOI`; categorical fields use defaults at inference time in `07_build_app/app.py`.

---

## Quick Start

1. **Review the dataset locally:**
   Open `cropdata.csv` and confirm the columns above are present.

2. **Sync to Vayu Object Storage (optional):**
   Open `00_dataset.ipynb`, set your S3 credentials and bucket, then run the upload cell. The notebook uploads `cropdata.csv` as `s3://<bucket>/cropdata.csv`.

3. **Continue to training:**
   The training notebook at `04_starter-kit/train_model.ipynb` reads the dataset from `../00_dataset/cropdata.csv`.

---

## Navigation

| | |
|---|---|
| **Previous** | [Move-It overview](../README.md) |
| **Next** | [Step 1 — Vayu AI Studio Workspace →](../01_vayu_workspaces/) |
| **Overview** | [Move-It overview](../README.md) |
