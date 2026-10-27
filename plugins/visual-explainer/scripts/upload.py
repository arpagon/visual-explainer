# /// script
# requires-python = ">=3.14"
# dependencies = ["boto3"]
# ///
"""Upload files to Cloudflare R2 under a shared UUID folder and print public URLs.

All files in one call land under the same UUIDv7 folder:
  r2://<bucket>/tmp/<user>/<host>/<harness>/<uuid7>/<filename>   (default, deleted after 30 days)
  r2://<bucket>/keep/<user>/<host>/<harness>/<uuid7>/<filename>  (--keep, kept indefinitely)

<user>, <host>, and <harness> record who published the page, from which
machine, and with which agent (pi, claude-code, codex, ...).

The bucket has an R2 lifecycle rule that deletes objects under `tmp/` after
30 days. R2 lifecycle rules match prefixes, not object tags.

Usage:
  uv run upload.py [--keep] <file1> [file2 ...]

Examples:
  uv run upload.py diagram.html
  uv run upload.py diagram.html screenshot.png video.mp4
  uv run upload.py --keep diagram.html assets/hero.png

Environment variables:
  VE_R2_ACCOUNT_ID   Cloudflare account that owns the bucket (required)
  VE_R2_BUCKET       bucket name (required)
  VE_R2_PUBLIC_URL   public base URL of the bucket's custom domain (required)
  VE_HARNESS         agent name for the path (default: pi)
  CLOUDFLARE_API_TOKEN
                     API token with R2 write access. S3 credentials are derived
                     from it: access key = token id, secret = sha256(token).
  VE_R2_ACCESS_KEY_ID / VE_R2_SECRET_ACCESS_KEY
                     optional R2 S3 credentials; used instead of the token
"""

import hashlib
import json
import mimetypes
import os
import socket
import sys
import urllib.request
import uuid
from pathlib import Path

import boto3

ACCOUNT_ID = os.environ.get("VE_R2_ACCOUNT_ID", "")
BUCKET     = os.environ.get("VE_R2_BUCKET", "")
PUBLIC_URL = os.environ.get("VE_R2_PUBLIC_URL", "").rstrip("/")
HARNESS    = os.environ.get("VE_HARNESS", "pi")
USER       = os.environ.get("USER") or os.environ.get("USERNAME") or "unknown"
HOST       = socket.gethostname().split(".")[0]


def fail(msg: str) -> None:
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


def credentials() -> tuple[str, str]:
    key_id = os.environ.get("VE_R2_ACCESS_KEY_ID")
    secret = os.environ.get("VE_R2_SECRET_ACCESS_KEY")
    if key_id and secret:
        return key_id, secret

    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not token:
        fail("set CLOUDFLARE_API_TOKEN or VE_R2_ACCESS_KEY_ID + VE_R2_SECRET_ACCESS_KEY")
    req = urllib.request.Request(
        "https://api.cloudflare.com/client/v4/user/tokens/verify",
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(req) as resp:
        token_id = json.load(resp)["result"]["id"]
    return token_id, hashlib.sha256(token.encode()).hexdigest()


def content_type(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    mime = mime or "application/octet-stream"
    if mime.startswith("text/") or mime in ("application/json", "application/javascript"):
        mime += "; charset=utf-8"
    return mime


def main() -> None:
    args  = sys.argv[1:]
    keep  = "--keep" in args
    paths = [Path(a) for a in args if not a.startswith("--")]

    if not paths:
        print(f"Usage: uv run {__file__} [--keep] <file1> [file2 ...]", file=sys.stderr)
        sys.exit(1)
    for name, value in (("VE_R2_ACCOUNT_ID", ACCOUNT_ID), ("VE_R2_BUCKET", BUCKET),
                        ("VE_R2_PUBLIC_URL", PUBLIC_URL)):
        if not value:
            fail(f"{name} env var is not set")
    missing = [p for p in paths if not p.is_file()]
    if missing:
        fail("file not found: " + ", ".join(map(str, missing)))

    key_id, secret = credentials()
    client = boto3.client(
        "s3",
        endpoint_url=f"https://{ACCOUNT_ID}.r2.cloudflarestorage.com",
        aws_access_key_id=key_id,
        aws_secret_access_key=secret,
        region_name="auto",
    )

    prefix = f"{'keep' if keep else 'tmp'}/{USER}/{HOST}/{HARNESS}/{uuid.uuid7()}"
    urls = []
    for path in paths:
        key = f"{prefix}/{path.name}"
        client.upload_file(str(path), BUCKET, key,
                           ExtraArgs={"ContentType": content_type(path)})
        urls.append(f"{PUBLIC_URL}/{key}")

    for url in urls:
        print(url)


if __name__ == "__main__":
    main()
