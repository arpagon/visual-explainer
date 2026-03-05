---
name: ve-preferences
description: Sync visual-explainer with upstream and apply arpagon's preferences. Use when asked to update, sync, or apply preferences to visual-explainer.
---

# Visual Explainer — Arpagon Preferences

Sync visual-explainer with upstream and apply arpagon's preferences.

## When to use

When the user says: "actualiza visual-explainer", "aplica mis preferencias", "sync upstream", "update visual-explainer".

## Steps

### 1. Sync upstream

```bash
bash {{skill_dir}}/sync.sh
```

This merges latest upstream, restores `.arpagon/`, copies custom files, and removes replaced files. After this, `SKILL.md` is raw upstream — preferences have NOT been applied yet.

### 2. Read preferences

```
{{skill_dir}}/preferences.yaml
```

Each preference has a `name` and an `intent` describing what to change.

### 3. Apply preferences

Edit `SKILL.md` directly using the edit tool. For each preference, find the relevant text and rewrite it according to the intent. Use judgment — the intents describe WHAT to change, not exact strings.

### 4. Verify

After applying, verify zero matches for:
- `surf-cli`, `surf`, `which surf` → should be `agent-browser`
- `Vercel`, `vercel-deploy`, `share.sh` → should be GCS/`upload.py`
- `proactively`, `always default`, `Never fall back`, `Don't wait for the user`

### 5. Commit

```bash
cd {{skill_dir}}/.. && git add -A && git commit -m "chore: sync upstream $(git log upstream/main -1 --format=%h) + apply preferences"
```
