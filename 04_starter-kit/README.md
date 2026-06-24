# Step 4 — Starter Kit (Ingestion & Training)

**Move-It** › **Starter Kit** · `04_starter-kit/`

|| |
|---|---|
| **⬅ Previous** | [Step 3 — Vayu Kafka](../03_vayu_kafka/) |
| **Next ➡**     | [Step 5 — Model Registry](../05_model_registry/) |

This core step contains the "brains" of your pipeline: the **Flask API** for sensor ingestion and the **Jupyter Notebook** for real-time ML processing.

---

## Folder Contents

|| File | Role |
|------|------|
| `train_model.ipynb` | Jupyter notebook for training the Random Forest model and logging to MLflow. |

---

## Prerequisites

|| Step | Vayu service / folder | Requirements |
|------|------------------------|--------------|
| 0 | `00_dataset/` | Historical sensor CSVs |
| 1 | `01_vayu_workspaces/` | Active Python environment |
| 2 | `02_vayu_mlflow/` | MLflow Tracking URI |
| 3 | `03_vayu_kafka/` | Kafka Bootstrap Servers & Topic Name |

---

## Quick Start

1. **Run Training Pipeline:**
   Open `04_starter-kit/train_model.ipynb` in Vayu AI Studio and run all cells.

---

## Navigation

|| |
|---|---|
| **⬅ Previous** | [Step 3 — Vayu Kafka](../03_vayu_kafka/) |
| **Next ➡**     | [Step 5 — Model Registry](../05_model_registry/) |
| **🏠 Overview**| [Move-It overview](../README.md) |
