# /// script
# requires-python = ">=3.10"
# dependencies = ["boto3", "uuid7"]
# ///
"""Upload files to S3 under a shared UUID folder and print public URLs.

All files land under the same UUID prefix:
  s3://<bucket>/<user>/<hostname>/<harness>/<uuid7>/<filename>

Lifecycle:
  By default every object is tagged ttl=30d and deleted after 30 days.
  Pass --keep to suppress the tag and keep objects indefinitely.

Usage:
  uv run upload.py [--keep] <file1> [file2 ...]

Examples:
  uv run upload.py diagram.html
  uv run upload.py diagram.html screenshot.png video.mp4
  uv run upload.py --keep diagram.html assets/hero.png

Environment variables:
  VE_S3_BUCKET   — bucket name (required)
  VE_S3_REGION   — AWS region (default: us-east-1)
  VE_HARNESS     — harness name for path segment (default: pi)
"""

import mimetypes
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
TTL_TAG    = "ttl=30d"  # matches lifecycle rule on the bucket


def guess_content_type(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    return mime or "application/octet-stream"


def main() -> None:
    args  = sys.argv[1:]
    keep  = "--keep" in args
    paths = [Path(a) for a in args if not a.startswith("--")]

    if not paths:
        print(f"Usage: uv run {__file__} [--keep] <file1> [file2 ...]", file=sys.stderr)
        sys.exit(1)

    if not BUCKET:
        print("Error: VE_S3_BUCKET env var is not set", file=sys.stderr)
        sys.exit(1)

    missing = [p for p in paths if not p.exists()]
    if missing:
        for p in missing:
            print(f"Error: file not found: {p}", file=sys.stderr)
        sys.exit(1)

    uid    = uuid7str()
    prefix = f"{USER}/{HOST}/{HARNESS}/{uid}"
    client = boto3.client("s3", region_name=REGION)

    extra_common: dict = {}
    if not keep:
        extra_common["Tagging"] = TTL_TAG

    urls = []
    for path in paths:
        key = f"{prefix}/{path.name}"
        client.upload_file(
            str(path),
            BUCKET,
            key,
            ExtraArgs={"ContentType": guess_content_type(path), **extra_common},
        )
        urls.append(f"{PUBLIC_URL}/{key}")

    for url in urls:
        print(url)


if __name__ == "__main__":
    main()
