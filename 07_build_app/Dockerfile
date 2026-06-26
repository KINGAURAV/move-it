# Move-It — real-time greenhouse pipeline in one container:
#   FastAPI ingest (port 5000) + Streamlit dashboard (port 8501)
#
# Build from move-it/ root:
#   docker build -f 07_build_app/Dockerfile -t move-it:latest .
#
# Run:
#   docker run -p 8501:8501 -p 5000:5000 \
#     -e KAFKA_BROKER=host:9095 \
#     -e KAFKA_USER=... \
#     -e PREDICT_URL=http://host:port/v1/models/name:predict \
#     move-it:latest
FROM python:3.11-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    INGEST_API_URL=http://127.0.0.1:5000/ingest \
    PORT=5000

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# cropdata.csv is used for feature encoding (matches training notebook preprocessing)
COPY 00_dataset/cropdata.csv ./00_dataset/cropdata.csv
COPY 07_build_app/app.py \
     07_build_app/ingestion_api.py \
     07_build_app/kafka_config.py \
     ./07_build_app/

WORKDIR /app/07_build_app

EXPOSE 5000 8501

# `&&` would block on uvicorn; start ingest in background, keep Streamlit as PID 1.
CMD ["sh", "-c", "uvicorn ingestion_api:app --host 0.0.0.0 --port ${PORT:-5000} & exec streamlit run app.py --server.address=0.0.0.0 --server.port=8501"]
