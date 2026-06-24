# Step 3 — Vayu Kafka

**Move-It** › **Vayu Kafka** · `03_vayu_kafka/`

|| |
|---|---|
| **Previous** | [← Step 2 — Vayu MLflow](../02_vayu_mlflow/) |
| **Next**     | [Step 4 — Agent starter kit →](../04_starter-kit/) |

Provision a **Vayu Kafka** topic to act as the streaming buffer between your Flask API (the sensor gateway) and your ML prediction engine (the consumer).

---

## Quick Start

1. **Provision Topic:** In the Vayu Kafka console, create a new topic (e.g., `greenhouse_telemetry`).
2. **Configure Producer:** Ensure your Flask API is configured to push data to this topic.
3. **Configure Consumer:** Ensure your training/inference notebooks are configured to listen to this topic.

---

## Navigation

|| |
|---|---|
| **Previous** | [← Step 2 — Vayu MLflow](../02_vayu_mlflow/) |
| **Next**     | [Step 4 — Agent starter kit →](../04_starter-kit/) |
| **Overview** | [Move-It overview](../README.md) |
