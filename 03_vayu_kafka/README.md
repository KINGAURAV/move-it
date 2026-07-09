# 📡 Step 3 — Vayu Kafka

**Move-It** › **Vayu Kafka** · `03_vayu_kafka/`

| [← Previous — Step 2 — Vayu MLflow](../02_vayu_mlflow/) | [Next — Step 4 — Starter Kit →](../04_starter-kit/) |
|:---|---:|

Deploy **Vayu Kafka** and create a topic that acts as the streaming buffer between your ingestion gateway and downstream consumers. Kafka connection details are provided in the **Access Guide**.

---

<details>
<summary><h3>🔗 Open Kafka</h3></summary>

Go to [Vayu Kafka](https://ipcloud.tatacommunications.com/cloud/console/vks/#/ms/list/kafka) to deploy Kafka.

</details>

---

<details>
<summary><h3>📂 Folder contents</h3></summary>

| File | Purpose |
|------|---------|
| `create_topic.py` | Script to create the telemetry topic after Kafka is Ready |

</details>

---

<details>
<summary><h3>🚀 Quick start</h3></summary>

1. **Deploy Vayu Kafka**

   > **Skip this step** if Vayu Kafka has already been provided to you — continue with step 2 below.

   - Create a new Kafka deployment on the [Vayu Kafka](https://ipcloud.tatacommunications.com/cloud/console/vks/#/ms/list/kafka) page.
   - **Wait for Ready:** Submit the deployment and wait until the status shows **Ready**.

2. **Create a topic:** Ensure your project root [`.env`](../README.md) includes `KAFKA_BROKER`, `KAFKA_USERNAME`, `KAFKA_PASSWORD`, and `KAFKA_TOPIC` — use the **Access Guide** for credentials. Form `KAFKA_BROKER` as `<IP>:<PORT>`. Then run:

   ```bash
   cd /home/jovyan/move-it
   source /home/jovyan/.venv/bin/activate  # (skip if already activated)
   python 03_vayu_kafka/create_topic.py
   ```

   [`create_topic.py`](create_topic.py) loads Kafka settings from `.env` automatically and creates a topic with the name in `KAFKA_TOPIC` (default: `greenhouse_telemetry`).

</details>

---

| [← Previous — Step 2 — Vayu MLflow](../02_vayu_mlflow/) | [Overview](../README.md) | [Next — Step 4 — Starter Kit →](../04_starter-kit/) |
|:---|:---:|---:|
