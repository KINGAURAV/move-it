"""Upload model.joblib from Step 4 to Vayu Object Storage (S3).

Run from the repo root after training:

    python 05_model_registry/upload_model.py

Replace the placeholder values below with your S3 credentials and target key.
"""

from __future__ import annotations

import os
from pathlib import Path

import boto3

os.environ["AWS_REQUEST_CHECKSUM_CALCULATION"] = "when_required"
os.environ["AWS_RESPONSE_CHECKSUM_VALIDATION"] = "when_required"

AWS_KEY = "<YOUR_S3_AWS_ACCESS_KEY>"
AWS_SECRET = "<YOUR_S3_AWS_SECRET_KEY>"
S3_ENDPOINT = "<YOUR_S3_ENDPOINT>"
BUCKET = "<YOUR_S3_BUCKET_NAME>"

# Example: if the full S3 key is move-it/model.joblib, set S3_KEY to that path.
S3_KEY = "move-it/model.joblib"

REPO_ROOT = Path(__file__).resolve().parent.parent
LOCAL_FILE = REPO_ROOT / "04_starter-kit" / "model.joblib"


def upload_file(local_file: Path, bucket: str, s3_key: str) -> None:
    if not local_file.is_file():
        raise FileNotFoundError(f"Model not found: {local_file}. Run Step 4 training first.")

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
