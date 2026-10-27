# Share Visual Explainer Page

Upload a visual explainer HTML file (and optional assets) to Cloudflare R2 and get public URLs.

## Usage

```
/share [--keep] <file-path> [asset ...]
```

**Arguments:**
- `file-path` - Path to the HTML file to share (required)
- `asset` - Extra files (images, videos) uploaded to the same folder
- `--keep` - Keep the files indefinitely instead of deleting them after 30 days

**Examples:**
```
/share ~/.agent/diagrams/my-diagram.html
/share ~/.agent/diagrams/my-diagram.html hero.png clip.mp4
/share --keep ~/.agent/diagrams/my-diagram.html
```

## How It Works

1. Generates one UUIDv7 folder for all files in the call
2. Uploads to `tmp/<user>/<host>/<harness>/<uuid>/` (default) or `keep/...` (`--keep`) with the correct Content-Type; user, host, and harness record who published the page, from which machine, and with which agent
3. Prints one public URL per file, in order
4. An R2 lifecycle rule deletes everything under `tmp/` after 30 days

## Script

```bash
uv run {{skill_dir}}/scripts/upload.py [--keep] <file> [asset ...]
```

## Output

```
https://ve.arpagon.co/tmp/arpagon/arpagon-01-med/pi/019538a2-.../my-diagram.html
```

## Configuration

| Variable | Description |
|----------|-------------|
| `VE_R2_ACCOUNT_ID` | Cloudflare account that owns the bucket (required) |
| `VE_R2_BUCKET` | R2 bucket name (required) |
| `VE_R2_PUBLIC_URL` | Public base URL of the bucket's custom domain (required) |
| `VE_HARNESS` | Agent name in the path: `pi`, `claude-code`, `codex`, ... (default: `pi`) |
| `CLOUDFLARE_API_TOKEN` | Token with R2 write access; S3 credentials are derived from it |
| `VE_R2_ACCESS_KEY_ID`, `VE_R2_SECRET_ACCESS_KEY` | Optional R2 S3 credentials used instead of the token |

## Notes

- URLs are public as soon as the upload finishes
- Without `--keep`, files expire after 30 days
- Folders are time-ordered thanks to UUIDv7
