---
name: ve-maintain
description: Sync visual-explainer with upstream and apply arpagon's patches. Use when asked to update, sync, or maintain the visual-explainer skill.
---

# Maintain Visual Explainer (arpagon patches)

This skill manages the patched visual-explainer installation. It syncs upstream changes and applies arpagon's customizations automatically — like k3s rebasing patches on upstream Kubernetes.

## Quick sync

```bash
bash {{skill_dir}}/sync.sh
```

This will:
1. Fetch latest from `upstream/main`
2. Overwrite all files with upstream versions
3. Restore `.arpagon/` directory (patches and custom files)
4. Copy custom files from `.arpagon/files/` into the repo
5. Remove replaced upstream files (`scripts/share.sh`, `.claude-plugin/`)
6. Apply all patches via `python3 .arpagon/apply_patches.py`
7. Show a diff summary — review and commit manually

## Patches

Defined in `.arpagon/apply_patches.py`. Each patch is an independent function:

| Patch | What it does |
|-------|-------------|
| `patch_opt_in_only` | Removes proactive behavior — skill activates only on explicit user request |
| `patch_agent_browser` | Replaces surf-cli with agent-browser for web screenshots and captures |
| `patch_gcs_upload` | Replaces Vercel sharing with GCS upload (UUIDv7 public URLs) |

### How patches work

Each patch uses **exact string replacement** on upstream files. If upstream changes the target text, the patch prints a warning with the expected string. To fix a broken patch:

1. Run `python3 .arpagon/apply_patches.py` and read the warnings
2. Check `git diff` to see what upstream changed
3. Update the old (target) string in `apply_patches.py` to match the new upstream text
4. Re-run

### Dry run (check without applying)

```bash
python3 .arpagon/apply_patches.py --check
```

### Adding a new patch

1. Add a new function in `apply_patches.py` (follow the existing pattern)
2. Add it to the `SKILL_PATCHES` list at the bottom
3. Run `python3 .arpagon/apply_patches.py` to test

## Custom files

Files in `.arpagon/files/` are copied into the repo during sync, overwriting upstream files at the same relative path:

| Source | Destination | Replaces |
|--------|-------------|----------|
| `.arpagon/files/scripts/upload.py` | `scripts/upload.py` | `scripts/share.sh` |
| `.arpagon/files/commands/share.md` | `commands/share.md` | Upstream Vercel version |

## After syncing

```bash
# Review what changed
git diff --stat
git diff

# Commit
git add -A && git commit -m "chore: sync upstream $(git log upstream/main -1 --format=%h) + apply patches"
```
