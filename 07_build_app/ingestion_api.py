"""FastAPI gateway: receive sensor HTTP POST and publish to Vayu Kafka."""

from __future__ import annotations

import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from kafka import KafkaProducer
from kafka.errors import KafkaError
from pydantic import BaseModel, Field

from kafka_config import KAFKA_BROKER, KAFKA_TOPIC, producer_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [ingest] %(message)s")
log = logging.getLogger(__name__)

_producer: KafkaProducer | None = None


class SensorPayload(BaseModel):
    temp: float
    humidity: float
    MOI: float = Field(default=10.0)
    timestamp: str | None = None


class IngestResponse(BaseModel):
    status: str
    topic: str
    data: dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    broker: str
    topic: str


def get_producer() -> KafkaProducer:
    global _producer
    if _producer is None:
        log.info("Connecting Kafka producer to %s (topic=%s)", KAFKA_BROKER, KAFKA_TOPIC)
        _producer = KafkaProducer(**producer_config())
    return _producer


def close_producer() -> None:
    global _producer
    if _producer is not None:
        _producer.close()
        _producer = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    log.info("Ingestion API started on port %s", os.getenv("PORT", "5000"))
    yield
    close_producer()


app = FastAPI(
    title="Move-It Ingestion API",
    description="HTTP gateway for greenhouse sensor telemetry -> Vayu Kafka",
    version="1.0.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    log.info(">>> %s %s", request.method, request.url.path)
    response = await call_next(request)
    log.info("<<< %s %s -> %s", request.method, request.url.path, response.status_code)
    return response


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", broker=KAFKA_BROKER, topic=KAFKA_TOPIC)


@app.post("/ingest", response_model=IngestResponse)
def ingest(payload: SensorPayload) -> IngestResponse:
    message = {
        "timestamp": payload.timestamp or time.strftime("%H:%M:%S"),
        "temp": payload.temp,
        "humidity": payload.humidity,
        "MOI": payload.MOI,
    }
    log.info("Received sensor data: %s", message)

    try:
        producer = get_producer()
        future = producer.send(KAFKA_TOPIC, value=message)
        future.get(timeout=10)
        log.info("Published to Kafka topic '%s': %s", KAFKA_TOPIC, message)
    except KafkaError as exc:
        log.error("Kafka publish failed: %s", exc)
        raise HTTPException(status_code=503, detail=f"Kafka publish failed: {exc}") from exc
    except Exception as exc:
        log.error("Unexpected error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return IngestResponse(status="ok", topic=KAFKA_TOPIC, data=message)


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "5000"))
    uvicorn.run("ingestion_api:app", host="0.0.0.0", port=port, reload=False)
