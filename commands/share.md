# Share Visual Explainer Page

Upload a visual explainer HTML file to Google Cloud Storage and get a public URL.

## Usage

```
/share <file-path>
```

**Arguments:**
- `file-path` - Path to the HTML file to share (required)

**Examples:**
```
/share ~/.agent/diagrams/my-diagram.html
/share /tmp/visual-explainer-output.html
```

## How It Works

1. Generates a UUIDv7-based filename for uniqueness and time-ordering
2. Uploads to the configured GCS bucket
3. Returns the public URL immediately

## Configuration

Set these environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `VE_GCS_BUCKET` | GCS bucket name | *(required)* |
| `VE_GCS_PREFIX` | Blob prefix / folder | `diagrams` |
| `VE_GCS_SA_KEY` | Path to SA JSON key | `scripts/gcs-sa.json` |

## Script Location

```bash
uv run {{skill_dir}}/scripts/upload.py <file>
```

## Output

```
https://storage.googleapis.com/your-bucket/diagrams/019538a2-....html
```

## Notes

- URLs are permanent and publicly accessible
- Files are time-ordered thanks to UUIDv7
- If `VE_GCS_BUCKET` is not set, the upload will fail with a clear error
