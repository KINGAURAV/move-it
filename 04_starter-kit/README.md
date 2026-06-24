# Step 4 — Starter Kit (Ingestion & Training)

**Move-It** › **Starter Kit** · `04_starter-kit/`

|        |               |
|--------|---------------|
| **⬅ Previous** | [Step 3 — Vayu Kafka](../03_vayu_kafka/) |
| **Next ➡**     | [Step 5 — Model Registry](../05_model_registry/) |

This step is the core of your pipeline, providing the **Flask API** for real-time sensor data ingestion and the **Jupyter Notebook** for machine learning model training.

---

## Folder Contents

| File                  | Description                                                         |
|-----------------------|---------------------------------------------------------------------|
| `train_model.ipynb`   | Notebook for training the Random Forest model and logging to MLflow |

---

## Prerequisites

| Step | Vayu Service / Folder     | Requirements                          |
|------|--------------------------|---------------------------------------|
| 0    | `00_dataset/`            | Historical sensor CSVs                |
| 1    | `01_vayu_workspaces/`    | Active Python environment             |
| 2    | `02_vayu_mlflow/`        | MLflow Tracking URI                   |
| 3    | `03_vayu_kafka/`         | Kafka Bootstrap Servers & Topic Name  |

---

Install dependencies:

![Setting up venv and installing dependencies](../assets/install.png)

## Quick Start

1. **Run the Training Pipeline:**
   - Open `04_starter-kit/train_model.ipynb` in Vayu AI Studio and execute all cells.

---

## Navigation

|        |               |
|--------|---------------|
| **⬅ Previous** | [Step 3 — Vayu Kafka](../03_vayu_kafka/) |
| **Next ➡**     | [Step 5 — Model Registry](../05_model_registry/) |
| **🏠 Overview**| [Move-It overview](../README.md) |
