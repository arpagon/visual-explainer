# /// script
# requires-python = ">=3.10"
# dependencies = ["boto3", "uuid7"]
# ///
"""Upload an HTML diagram to S3 and print a public URL.

Path structure:
  s3://<bucket>/<user>/<hostname>/<harness>/<uuid7>/<slug>.html

Environment variables:
  VE_S3_BUCKET   — bucket name (required)
  VE_S3_REGION   — AWS region (default: us-east-1)
  VE_HARNESS     — harness name for path segment (default: pi)
"""

import os
import socket
import sys
from pathlib import Path

import boto3
from uuid_extensions import uuid7str

BUCKET  = os.environ.get("VE_S3_BUCKET", "")
REGION  = os.environ.get("VE_S3_REGION", "us-east-1")
HARNESS = os.environ.get("VE_HARNESS", "pi")
USER    = os.environ.get("USER") or os.environ.get("USERNAME") or "unknown"
HOST    = socket.gethostname()

PUBLIC_URL = f"https://{BUCKET}.s3.amazonaws.com"


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: uv run {__file__} <file.html>", file=sys.stderr)
        sys.exit(1)

    local_file = Path(sys.argv[1])

    if not local_file.exists():
        print(f"Error: file not found: {local_file}", file=sys.stderr)
        sys.exit(1)

    if not BUCKET:
        print("Error: VE_S3_BUCKET env var is not set", file=sys.stderr)
        sys.exit(1)

    slug = local_file.stem
    key  = f"{USER}/{HOST}/{HARNESS}/{uuid7str()}/{slug}.html"

    client = boto3.client("s3", region_name=REGION)
    client.upload_file(
        str(local_file),
        BUCKET,
        key,
        ExtraArgs={"ContentType": "text/html"},
    )

    print(f"{PUBLIC_URL}/{key}")


if __name__ == "__main__":
    main()
