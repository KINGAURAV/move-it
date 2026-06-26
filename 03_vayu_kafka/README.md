# Step 3 — Vayu Kafka

**Move-It** › **Vayu Kafka** · `03_vayu_kafka/`

| | |
|---|---|
| **Previous** | [← Step 2 — Vayu MLflow](../02_vayu_mlflow/) |
| **Next**     | [Step 4 — Starter Kit →](../04_starter-kit/) |

Deploy **Vayu Kafka** and create a topic that acts as the streaming buffer between your ingestion gateway and downstream consumers.

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
3. **Create a topic:** Replace the placeholder values in [`create_topic.py`](create_topic.py) (or export them as environment variables), then run:

   ```bash
   export KAFKA_BROKER="<VAYU_KAFKA_BROKER>"
   export KAFKA_USER="<VAYU_KAFKA_USER>"
   export KAFKA_PASS="<VAYU_KAFKA_PASS>"
   export KAFKA_TOPIC="greenhouse_telemetry"
   python 03_vayu_kafka/create_topic.py
   ```

   Default topic name is `greenhouse_telemetry`. Change `KAFKA_TOPIC` if your team uses a different name.

---

## Navigation

| | |
|---|---|
| **Previous** | [← Step 2 — Vayu MLflow](../02_vayu_mlflow/) |
| **Next**     | [Step 4 — Starter Kit →](../04_starter-kit/) |
| **Overview** | [Move-It overview](../README.md) |
