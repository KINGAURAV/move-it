"""Create a Vayu Kafka topic for Move-It telemetry.

Run from the repo root after your Kafka deployment is Ready:

    cd /home/jovyan/move-it
    python 03_vayu_kafka/create_topic.py

Set Kafka variables in the project root `.env` file.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from kafka import KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "")
KAFKA_USER = os.getenv("KAFKA_USER", "")
KAFKA_PASS = os.getenv("KAFKA_PASS", "")
TOPIC_NAME = os.getenv("KAFKA_TOPIC", "greenhouse_telemetry")
NUM_PARTITIONS = int(os.getenv("KAFKA_TOPIC_PARTITIONS", "1"))
REPLICATION_FACTOR = int(os.getenv("KAFKA_TOPIC_REPLICATION_FACTOR", "1"))

KAFKA_SECURITY = {
    "security_protocol": "SASL_PLAINTEXT",
    "sasl_mechanism": "SCRAM-SHA-512",
    "sasl_plain_username": KAFKA_USER,
    "sasl_plain_password": KAFKA_PASS,
}


def main() -> None:
    if not all([KAFKA_BROKER, KAFKA_USER, KAFKA_PASS]):
        raise ValueError("Set KAFKA_BROKER, KAFKA_USER, and KAFKA_PASS in .env")

    admin = KafkaAdminClient(
        bootstrap_servers=KAFKA_BROKER,
        **KAFKA_SECURITY,
    )
    topic = NewTopic(
        name=TOPIC_NAME,
        num_partitions=NUM_PARTITIONS,
        replication_factor=REPLICATION_FACTOR,
    )

    try:
        admin.create_topics([topic])
        print(f"Created topic: {TOPIC_NAME}")
    except TopicAlreadyExistsError:
        print(f"Topic already exists: {TOPIC_NAME}")
    finally:
        admin.close()


if __name__ == "__main__":
    main()
