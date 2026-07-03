"""Upload model.joblib from Step 4 to Vayu Object Storage (S3).

Run from the repo root after training:

    cd /home/jovyan/move-it
    python 05_model_registry/upload_model.py

Set AWS and S3 variables in the project root `.env` file.
"""

from __future__ import annotations

import os
from pathlib import Path

import boto3
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env")

os.environ["AWS_REQUEST_CHECKSUM_CALCULATION"] = "when_required"
os.environ["AWS_RESPONSE_CHECKSUM_VALIDATION"] = "when_required"

AWS_KEY = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY", "")
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "")
BUCKET = os.getenv("S3_BUCKET_NAME", "")
S3_KEY = os.getenv("S3_MODEL_KEY", "move-it/model.joblib")

LOCAL_FILE = REPO_ROOT / "04_starter-kit" / "model.joblib"


def upload_file(local_file: Path, bucket: str, s3_key: str) -> None:
    if not local_file.is_file():
        raise FileNotFoundError(f"Model not found: {local_file}. Run Step 4 training first.")
    if not all([AWS_KEY, AWS_SECRET, S3_ENDPOINT, bucket]):
        raise ValueError("Set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_ENDPOINT, and S3_BUCKET_NAME in .env")

    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_KEY,
        aws_secret_access_key=AWS_SECRET,
        endpoint_url=S3_ENDPOINT,
    )

    print(f"Uploading {local_file} → s3://{bucket}/{s3_key}")
    s3.upload_file(str(local_file), bucket, s3_key)
    print("DONE: model.joblib uploaded successfully")


if __name__ == "__main__":
    upload_file(LOCAL_FILE, BUCKET, S3_KEY)
