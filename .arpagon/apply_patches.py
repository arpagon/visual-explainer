#!/usr/bin/env python3
"""Apply arpagon's patches to upstream visual-explainer files.

Each patch is a function that transforms file content via string replacement.
If a replacement target isn't found, the patch warns (upstream may have changed)
and the caller can update the target string to match the new upstream text.

Usage:
    python3 .arpagon/apply_patches.py          # from repo root
    python3 .arpagon/apply_patches.py --check   # dry-run: only report status
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CHECK_ONLY = "--check" in sys.argv

# ─── Helpers ────────────────────────────────────────────────────────────


def _replace(content: str, old: str, new: str, label: str) -> tuple[str, bool]:
    """Replace exact substring. Returns (new_content, success)."""
    if old in content:
        return content.replace(old, new, 1), True
    print(f"  ⚠️  {label}: target not found — upstream may have changed")
    print(f"      Expected: {old[:80]}...")
    return content, False


def _replace_section(
    content: str, start: str, end: str, replacement: str, label: str
) -> tuple[str, bool]:
    """Replace everything from `start` to just before `end`."""
    start_idx = content.find(start)
    if start_idx == -1:
        print(f"  ⚠️  {label}: start marker not found: {start[:60]}...")
        return content, False
    end_idx = content.find(end, start_idx)
    if end_idx == -1:
        print(f"  ⚠️  {label}: end marker not found: {end[:60]}...")
        return content, False
    return content[:start_idx] + replacement + content[end_idx:], True


# ─── Patch 1: Opt-in only ──────────────────────────────────────────────


def patch_opt_in_only(content: str) -> str:
    """Remove proactive/aggressive behavior. Skill activates only on explicit request."""

    # 1a. Frontmatter description — remove proactive clause
    content, _ = _replace(
        content,
        "Use when the user asks for a diagram, architecture overview, diff review, "
        "plan review, project recap, comparison table, or any visual explanation of "
        "technical concepts. Also use proactively when you are about to render a "
        "complex ASCII table (4+ rows or 3+ columns) — present it as a styled HTML "
        "page instead.",

        "Use only when the user explicitly asks for a visual diagram, HTML page, "
        "architecture overview, diff review, plan review, project recap, or visual "
        "explanation.",
        "1a-description",
    )

    # 1b. First paragraph — remove Always/Never
    content, _ = _replace(
        content,
        "Generate self-contained HTML files for technical diagrams, visualizations, "
        "and data tables. Always open the result in the browser. Never fall back to "
        "ASCII art when this skill is loaded.",

        "Generate self-contained HTML files for technical diagrams, visualizations, "
        "and data tables when the user explicitly requests visual output.",
        "1b-always-never",
    )

    # 1c. Proactive table rendering paragraph — remove entirely
    content, _ = _replace(
        content,
        "\n**Proactive table rendering.** When you're about to present tabular data "
        "as an ASCII box-drawing table in the terminal (comparisons, audits, feature "
        "matrices, status reports, any structured rows/columns), generate an HTML page "
        "instead. The threshold: if the table has 4+ rows or 3+ columns, it belongs in "
        "the browser. Don't wait for the user to ask — render it as HTML automatically "
        "and tell them the file path. You can still include a brief text summary in the "
        "chat, but the table itself should be the HTML page.",
        "",
        "1c-proactive-tables",
    )

    # 1d. Visual is always default
    content, _ = _replace(
        content,
        "**Visual is always default.** Even essays, blog posts, and articles get "
        "visual treatment — extract structure into cards, diagrams, grids, tables.",

        "**Visual treatment when requested.** When the user asks for a visual page, "
        "essays, blog posts, and articles get full visual treatment — extract structure "
        "into cards, diagrams, grids, tables.",
        "1d-always-default",
    )

    # 1e. Use proactively in data tables section
    content, _ = _replace(
        content,
        "**Use proactively.** Any time you'd render an ASCII box-drawing table in the "
        "terminal, generate an HTML table instead. This includes:",

        "**When to use.** Generate HTML tables when the user requests visual output for:",
        "1e-proactive-tables-2",
    )

    return content


# ─── Patch 2: agent-browser replaces surf-cli ──────────────────────────


AGENT_BROWSER_SECTION = """\
**Web screenshots and captures (optional).** If `agent-browser` is available, you can capture screenshots of web pages, running applications, or rendered content and embed them in the page. Check availability with `which agent-browser`. If available:

```bash
# Navigate and capture
agent-browser open <url>
agent-browser screenshot /tmp/ve-img.png
# For full page: agent-browser screenshot /tmp/ve-img.png --full

# Base64 encode for self-containment
IMG=$(base64 -w 0 /tmp/ve-img.png)

# Embed in HTML and clean up
# <img src="data:image/png;base64,${IMG}" alt="descriptive alt text">
rm /tmp/ve-img.png
```

See `./references/css-patterns.md` for image container styles (hero banners, inline illustrations, captions).

**When to use:** Hero banners showing the current state of a system. Screenshots of web UIs being discussed. Before/after captures for visual diffs. Documentation of running applications.

**When to skip:** Anything Mermaid or CSS handles well. Generic decoration that doesn't convey meaning. Data-heavy pages where images would distract. Always degrade gracefully — if agent-browser isn't available, skip captures without erroring. The page should stand on its own with CSS and typography alone.

"""


def patch_agent_browser(content: str) -> str:
    """Replace surf-cli with agent-browser for screenshots/captures."""

    # 2a. Compatibility line in frontmatter
    content, _ = _replace(
        content,
        "Optional surf-cli for AI image generation.",
        "Optional agent-browser for web screenshots and captures.",
        "2a-compatibility",
    )

    # 2b. Main AI illustrations section → agent-browser section
    content, _ = _replace_section(
        content,
        "**AI-generated illustrations (optional).**",
        "### 3. Style",
        AGENT_BROWSER_SECTION,
        "2b-surf-section",
    )

    # 2c. Slide deck mode surf reference
    content, _ = _replace(
        content,
        "**Visual richness:** Check `which surf` at the start. If surf-cli is "
        "available, generate 2\u20134 images (title slide background, full-bleed "
        "background, optional content illustrations) before writing HTML \u2014 see "
        "the Proactive Imagery section in `slide-patterns.md` for the workflow. Also "
        "use SVG decorative accents, per-slide background gradients, inline "
        "sparklines, and small Mermaid diagrams. Visual-first, text-second.",

        "**Visual richness:** Check `which agent-browser` at the start. If "
        "agent-browser is available, capture 2\u20134 screenshots (relevant web UIs, "
        "current system state, documentation pages) before writing HTML and embed "
        "them as base64. Also use SVG decorative accents, per-slide background "
        "gradients, inline sparklines, and small Mermaid diagrams. Visual-first, "
        "text-second.",
        "2c-slide-surf",
    )

    return content


# ─── Patch 3: GCS upload replaces Vercel ────────────────────────────────

GCS_SHARING_SECTION = """\
## Sharing Pages

Upload visual explainer pages to Google Cloud Storage for instant sharing via public URL.

**Usage:**
```bash
uv run {{skill_dir}}/scripts/upload.py <html-file>
```

**Example:**
```bash
uv run {{skill_dir}}/scripts/upload.py ~/.agent/diagrams/my-diagram.html

# Output:
# https://storage.googleapis.com/your-bucket/diagrams/019538a2-....html
```

**How it works:**
1. Generates a UUIDv7-based filename for uniqueness and time-ordering
2. Uploads to the configured GCS bucket
3. Returns the public URL immediately

**Configuration (environment variables):**

| Variable | Description | Default |
|----------|-------------|---------|
| `VE_GCS_BUCKET` | GCS bucket name | *(required)* |
| `VE_GCS_PREFIX` | Blob prefix / folder | `diagrams` |
| `VE_GCS_SA_KEY` | Path to service account JSON | `scripts/gcs-sa.json` |

**Requirements:**
- `uv` (Python package runner)
- GCS service account with write access to the bucket
- Bucket configured for public read access

**Notes:**
- URLs are permanent and publicly accessible
- Files are ordered by time thanks to UUIDv7
- If env vars are not set, sharing is skipped silently

See `./commands/share.md` for the `/share` command template.

"""


def patch_gcs_upload(content: str) -> str:
    """Replace Vercel sharing with GCS upload."""

    content, _ = _replace_section(
        content,
        "## Sharing Pages",
        "## Quality Checks",
        GCS_SHARING_SECTION,
        "3-sharing-vercel-to-gcs",
    )

    return content


# ─── Orchestration ──────────────────────────────────────────────────────

SKILL_PATCHES = [
    patch_opt_in_only,
    patch_agent_browser,
    patch_gcs_upload,
]


def main() -> None:
    skill_md = REPO / "SKILL.md"
    if not skill_md.exists():
        print("❌ SKILL.md not found — run from the repo root or after syncing upstream")
        sys.exit(1)

    content = skill_md.read_text()
    total_applied = 0

    for patch_fn in SKILL_PATCHES:
        name = patch_fn.__name__
        doc = patch_fn.__doc__ or ""
        print(f"\n{'─' * 60}")
        print(f"Patch: {name}")
        print(f"  {doc.strip()}")

        old_content = content
        content = patch_fn(content)

        if content != old_content:
            print(f"  ✅ Applied")
            total_applied += 1
        else:
            print(f"  ⏭️  No changes (already applied or target changed)")

    if CHECK_ONLY:
        print(f"\n{'─' * 60}")
        print(f"Dry run complete. {total_applied} patch(es) would apply.")
    else:
        skill_md.write_text(content)
        print(f"\n{'─' * 60}")
        print(f"Done. {total_applied} patch(es) applied to SKILL.md")


if __name__ == "__main__":
    main()
