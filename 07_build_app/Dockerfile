# Move-It — Streamlit IoT dashboard (Kafka consumer + built-in simulator).
# Build from move-it/ (not this folder):
#   docker build -f 07_build_app/Dockerfile -t move-it-dash:latest .
# Runtime env: KAFKA_BROKER, KAFKA_TOPIC, KAFKA_USER, KAFKA_PASS, INGEST_API_URL.
FROM python:3.11-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY 04_starter-kit/ ./04_starter-kit/
COPY 07_build_app/app.py ./07_build_app/

WORKDIR /app/07_build_app

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
