# Step 3 — Vayu Kafka

**Move-It** › **Vayu Kafka** · `03_vayu_kafka/`

| | |
|---|---|
| **Previous** | [← Step 2 — Vayu MLflow](../02_vayu_mlflow/) |
| **Next**     | [Step 4 — Starter Kit →](../04_starter-kit/) |

Deploy **Vayu Kafka** and create a topic that acts as the streaming buffer between your ingestion gateway and downstream consumers. Kafka connection details are provided in the **Access Guide**.

---

## Open Kafka

Go to [Vayu Kafka](https://ipcloud.tatacommunications.com/cloud/console/vks/#/ms/list/kafka) to deploy Kafka.

---

## Folder Contents

| File | Purpose |
|------|---------|
| `create_topic.py` | Script to create the telemetry topic after Kafka is Ready |

---

## Quick Start

1. **Deploy Vayu Kafka:** Create a new Kafka deployment on the [Vayu Kafka](https://ipcloud.tatacommunications.com/cloud/console/vks/#/ms/list/kafka) page.
2. **Wait for Ready:** Submit the deployment and wait until the status shows **Ready**.
3. **Create a topic:** Ensure your project root [`.env`](../README.md) includes `KAFKA_BROKER`, `KAFKA_USER`, `KAFKA_PASS`, and optionally `KAFKA_TOPIC` (default: `greenhouse_telemetry`) — use the values from the **Access Guide**. Then run:

   ```bash
   cd /home/jovyan
   cd move-it
   python 03_vayu_kafka/create_topic.py
   ```

   [`create_topic.py`](create_topic.py) loads Kafka settings from `.env` automatically. Change `KAFKA_TOPIC` in `.env` if your team uses a different topic name.

---

## Navigation

| | |
|---|---|
| **Previous** | [← Step 2 — Vayu MLflow](../02_vayu_mlflow/) |
| **Next**     | [Step 4 — Starter Kit →](../04_starter-kit/) |
| **Overview** | [Move-It overview](../README.md) |
