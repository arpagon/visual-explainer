# Fork: arpagon/visual-explainer

## Origin

This is a fork of [nicobailon/visual-explainer](https://github.com/nicobailon/visual-explainer) — an agent skill that turns complex terminal output (diagrams, tables, diffs) into styled, self-contained HTML pages with dark/light theme support and interactive Mermaid diagrams.

## What This Fork Adds

### GCS Upload Support (`arpagon/gcs-upload` branch)

The upstream project generates HTML files locally at `~/.agent/diagrams/` and opens them in the browser. This fork adds the ability to **upload diagrams to Google Cloud Storage** and get a shareable public URL.

#### Changes

1. **`scripts/upload.py`** — New script that uploads an HTML file to a GCS bucket using a UUIDv7-based filename and prints the public URL.

2. **`SKILL.md`** — Updated workflow to automatically upload after local generation, providing both a local path and a shareable URL.

3. **Environment-based configuration** — All GCS settings are configurable via environment variables (no hardcoded values):

   | Variable | Description | Default |
   |----------|-------------|---------|
   | `VE_GCS_BUCKET` | GCS bucket name | *(required)* |
   | `VE_GCS_PREFIX` | Blob prefix / folder | `diagrams` |
   | `VE_GCS_SA_KEY` | Path to service account JSON | `scripts/gcs-sa.json` |

#### Usage

```bash
# Set the required env var
export VE_GCS_BUCKET="your-bucket-name"

# Upload a diagram
uv run scripts/upload.py ~/.agent/diagrams/my-diagram.html
# → https://storage.googleapis.com/your-bucket-name/diagrams/019538a2-...html
```

The agent handles this automatically — if the env vars are set and the SA key exists, it uploads and shares the URL. If not, it skips silently and the local file remains the primary deliverable.

## Why

The upstream skill is designed for local-only use. In a team or multi-machine setup (like our home server infrastructure), having a shareable URL makes diagrams accessible from any device without file transfers. The env var approach keeps the fork generic and avoids leaking infrastructure details.

## Branch Structure

| Branch | Description |
|--------|-------------|
| `main` | Tracks upstream `nicobailon/visual-explainer` |
| `arpagon/gcs-upload` | GCS upload feature (2 commits ahead of upstream v0.1.0) |

## Keeping Up with Upstream

```bash
git fetch upstream
git checkout main
git merge upstream/main
git push origin main

# Rebase feature branch on updated main
git checkout arpagon/gcs-upload
git rebase main
git push origin arpagon/gcs-upload --force-with-lease
```
