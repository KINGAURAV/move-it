"""FastAPI gateway: receive rail sensor HTTP POST and publish to Vayu Kafka."""

from __future__ import annotations

import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from kafka import KafkaProducer
from kafka.errors import KafkaError
from pydantic import BaseModel

from kafka_config import KAFKA_BROKER, KAFKA_TOPIC, producer_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [ingest] %(message)s")
log = logging.getLogger(__name__)

_producer: KafkaProducer | None = None


class RailSensorPayload(BaseModel):
    timestamp: str | None = None
    track_id: str
    section: str
    vibration_hz: float
    acoustic_emission_db: float
    rail_strain_mu: float
    track_temperature_c: float
    alignment_deviation_mm: float
    assigned_team: str
    last_maintenance_days: int
    action_taken: str


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
    title="Move-It RailOps Ingestion API",
    description="HTTP gateway for railway telemetry -> Vayu Kafka",
    version="1.0.0",
    lifespan=lifespan,
    root_path="/proxy/5000",
)


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


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
def ingest(payload: RailSensorPayload) -> IngestResponse:
    message = {
        "timestamp": payload.timestamp or time.strftime("%Y-%m-%d %H:%M:%S"),
        "track_id": payload.track_id,
        "section": payload.section,
        "vibration_hz": payload.vibration_hz,
        "acoustic_emission_db": payload.acoustic_emission_db,
        "rail_strain_mu": payload.rail_strain_mu,
        "track_temperature_c": payload.track_temperature_c,
        "alignment_deviation_mm": payload.alignment_deviation_mm,
        "assigned_team": payload.assigned_team,
        "last_maintenance_days": payload.last_maintenance_days,
        "action_taken": payload.action_taken,
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