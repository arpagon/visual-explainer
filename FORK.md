# Fork: arpagon/visual-explainer

## Origin

Fork of [nicobailon/visual-explainer](https://github.com/nicobailon/visual-explainer) — an agent skill that turns complex terminal output into styled, self-contained HTML pages.

## How it works

```
upstream/main          ← nicobailon/visual-explainer
       │
       │  sync.sh (fetch + copy files)
       ▼
  Raw upstream SKILL.md
       │
       │  Agent reads preferences.yaml and applies changes
       ▼
     main              ← single branch: upstream + preferences applied
```

No mechanical patching. The agent reads `preferences.yaml`, understands the intent, and edits `SKILL.md` with judgment. If upstream rewrites a section, the agent adapts — no broken string matches.

### Sync

Tell the agent: **"actualiza visual-explainer y aplica mis preferencias"**

Or manually:
```bash
bash .arpagon/sync.sh   # fetch upstream
# then the agent reads preferences.yaml and applies
```

## Preferences

Defined in `.arpagon/preferences.yaml`:

| Preference | Intent |
|-----------|--------|
| `opt-in-only` | Remove all proactive behavior — only activate on explicit user request |
| `agent-browser` | Replace surf-cli with agent-browser for web screenshots |
| `gcs-upload` | Replace Vercel sharing with GCS upload |

## Custom files

Copied from `.arpagon/files/` during sync:

| File | Replaces |
|------|----------|
| `scripts/upload.py` | `scripts/share.sh` |
| `commands/share.md` | Upstream Vercel version |

## Branching

One branch: `main`. That's it.

- `main` = upstream + preferences applied (what pi reads)
- `remotes/upstream/main` = upstream reference (via `git fetch upstream`)

## Structure

```
.arpagon/
├── preferences.yaml      ← What I want (agent reads this)
├── sync.sh               ← Fetches upstream files
└── files/                 ← Custom files copied during sync
    ├── scripts/upload.py
    └── commands/share.md
```
