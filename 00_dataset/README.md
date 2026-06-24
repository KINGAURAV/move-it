# Step 0 — Vayu Object Storage (Dataset)

**Move-It** › **Vayu Object Storage** · `00_dataset/`

|| |
|---|---|
| **Previous** | [Move-It overview](../README.md) |
| **Next**     | [Step 1 — Vayu AI Studio Workspace →](../01_vayu_workspaces/) |

Welcome to the **Move-It** project! This step focuses on preparing your historical sensor datasets for model training.

---

## Folder Contents

|| File / Folder         | Purpose                                                    |
|----------------------|------------------------------------------------------------|
| `sensor_logs/`       | Historical CSV files containing Temp/Humidity telemetry |
| `training_data.csv`  | Prepared dataset for Random Forest training               |

---

## Quick Start

1. **Upload Historical Data:**
   Upload your `.csv` sensor logs to the Vayu Object Storage bucket to be used by the training notebook in `04_starter-kit/`.

2. **Verify Data:**
   Ensure your CSV files have the expected columns: `timestamp`, `temp`, `humidity`.

---

## Navigation

|| |
|---|---|
| **Previous** | [Move-It overview](../README.md) |
| **Next**     | [Step 1 — Vayu AI Studio Workspace →](../01_vayu_workspaces/) |
| **Overview** | [Move-It overview](../README.md) |
