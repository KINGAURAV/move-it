"""Shared Kafka settings for Move-It ingestion, dashboard, and simulator."""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "greenhouse_telemetry")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "streamlit_consumer_group")

KAFKA_USER = os.getenv("KAFKA_USER", "")
KAFKA_PASS = os.getenv("KAFKA_PASS", "")

KAFKA_SECURITY = {
    "security_protocol": "SASL_PLAINTEXT",
    "sasl_mechanism": "SCRAM-SHA-512",
    "sasl_plain_username": KAFKA_USER,
    "sasl_plain_password": KAFKA_PASS,
}


def _json_serializer(value: object) -> bytes:
    return json.dumps(value).encode("utf-8")


def _json_deserializer(value: bytes | None) -> dict:
    if value is None:
        return {}
    return json.loads(value.decode("utf-8"))


def producer_config() -> dict:
    return {
        "bootstrap_servers": KAFKA_BROKER,
        "value_serializer": _json_serializer,
        **KAFKA_SECURITY,
    }


def consumer_config() -> dict:
    return {
        "bootstrap_servers": KAFKA_BROKER,
        "group_id": KAFKA_GROUP_ID,
        "auto_offset_reset": "latest",
        "enable_auto_commit": True,
        "value_deserializer": _json_deserializer,
        **KAFKA_SECURITY,
    }
