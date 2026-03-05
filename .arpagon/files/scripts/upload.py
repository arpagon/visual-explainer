# /// script
# requires-python = ">=3.10"
# dependencies = ["google-cloud-storage", "uuid7"]
# ///
"""Upload an HTML diagram to GCS and print a public URL."""

import os
import sys
from pathlib import Path

from google.cloud import storage
from uuid_extensions import uuid7str

BUCKET = os.environ.get("VE_GCS_BUCKET", "")
PREFIX = os.environ.get("VE_GCS_PREFIX", "diagrams")
SA_KEY = Path(os.environ.get("VE_GCS_SA_KEY", Path(__file__).parent / "gcs-sa.json"))
PUBLIC_URL = f"https://storage.googleapis.com/{BUCKET}"


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: uv run {__file__} <file.html>", file=sys.stderr)
        sys.exit(1)

    local_file = Path(sys.argv[1])
    if not local_file.exists():
        print(f"Error: file not found: {local_file}", file=sys.stderr)
        sys.exit(1)

    if not BUCKET:
        print("Error: VE_GCS_BUCKET env var is not set", file=sys.stderr)
        sys.exit(1)

    if not SA_KEY.exists():
        print(f"Error: SA key not found: {SA_KEY}", file=sys.stderr)
        sys.exit(1)

    blob_name = f"{PREFIX}/{uuid7str()}.html"

    client = storage.Client.from_service_account_json(str(SA_KEY))
    blob = client.bucket(BUCKET).blob(blob_name)
    blob.upload_from_filename(str(local_file), content_type="text/html")

    print(f"{PUBLIC_URL}/{blob_name}")


if __name__ == "__main__":
    main()
