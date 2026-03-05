# Fork: arpagon/visual-explainer

## Origin

Fork of [nicobailon/visual-explainer](https://github.com/nicobailon/visual-explainer) — an agent skill that turns complex terminal output (diagrams, tables, diffs) into styled, self-contained HTML pages with dark/light theme support and interactive Mermaid diagrams.

## Patch Strategy (à la k3s)

Instead of maintaining a divergent fork, this repo uses an **automated patch system**: upstream files are synced as-is, then a set of patches transform them to match arpagon's preferences. The patches are small, surgical, and independent — when upstream changes, only the affected patch targets need updating.

```
remotes/upstream/main  (nicobailon/visual-explainer)
         │
         │  git fetch upstream
         │  git checkout upstream/main -- .
         ▼
       main             ← single branch: upstream + patches applied
         │                 (what pi reads via ~/.agents/skills/visual-explainer)
         │
         └── .arpagon/  ← patch system lives here
```

### Branching

**One branch: `main`.** That's it.

- `main` = upstream + patches applied. Always in a usable state. This is what pi reads.
- `remotes/upstream/main` = upstream reference. Exists automatically after `git fetch upstream`. Not a local branch.

No upstream-tracking local branch. No feature branches. The `.arpagon/` directory and `FORK.md` only exist on `main` — they're saved and restored during sync so they never conflict with upstream.

**To see upstream state:**
```bash
git log upstream/main                              # history
git show upstream/main:SKILL.md                    # specific file
diff <(git show upstream/main:SKILL.md) SKILL.md   # your patches vs upstream
```

### Sync from upstream

```bash
bash .arpagon/sync.sh          # interactive
bash .arpagon/sync.sh --auto   # non-interactive (for agent use)

# review → commit
git diff
git add -A && git commit -m "chore: sync upstream $(git log upstream/main -1 --format=%h) + apply arpagon patches"
```

Or just tell the agent: **"actualiza visual-explainer y aplica mis preferencias"** — the `ve-preferences` skill handles everything.

## Active Patches

| Patch | What it changes |
|-------|----------------|
| `patch_opt_in_only` | Removes proactive behavior — skill activates only on explicit user request, not automatically for tables |
| `patch_agent_browser` | Replaces surf-cli (AI image generation) with agent-browser (web screenshots and captures) |
| `patch_gcs_upload` | Replaces Vercel deploy sharing with GCS upload (UUIDv7 public URLs) |

## Custom Files

Files that don't exist in upstream (added during sync from `.arpagon/files/`):

| File | Purpose |
|------|---------|
| `.arpagon/` | Patch system (meta-skill, patches, sync script, custom files) |
| `scripts/upload.py` | GCS upload with UUIDv7 filenames |
| `commands/share.md` | Updated `/share` command for GCS |
| `FORK.md` | This file |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VE_GCS_BUCKET` | GCS bucket name | *(required for sharing)* |
| `VE_GCS_PREFIX` | Blob prefix / folder | `diagrams` |
| `VE_GCS_SA_KEY` | Path to service account JSON | `scripts/gcs-sa.json` |

## Structure

```
.arpagon/
├── SKILL.md              ← Meta-skill: tells the agent how to sync/maintain
├── sync.sh               ← Orchestration: fetch upstream + apply patches
├── apply_patches.py      ← Patch definitions (string replacements on SKILL.md)
└── files/                ← Custom files copied during sync
    ├── scripts/upload.py
    └── commands/share.md
```

## When Patches Break

If upstream changes text that a patch targets, `apply_patches.py` prints a warning:

```
⚠️  1a-description: target not found — upstream may have changed
    Expected: Use when the user asks for a diagram...
```

Fix: open `.arpagon/apply_patches.py`, find the patch, update the old string to match upstream's new wording, re-run.
