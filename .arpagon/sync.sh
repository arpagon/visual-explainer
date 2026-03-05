#!/bin/bash
# Sync visual-explainer with upstream and apply arpagon's patches.
#
# Usage:
#   bash .arpagon/sync.sh          # Interactive (asks before proceeding)
#   bash .arpagon/sync.sh --auto   # Non-interactive (for agent use)
#
# Strategy (à la k3s):
#   1. Fetch upstream
#   2. Overwrite repo files with upstream versions
#   3. Restore .arpagon/ (our patch system)
#   4. Copy custom files from .arpagon/files/
#   5. Remove upstream-only files we replaced
#   6. Apply patches to transform upstream files

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
AUTO=false
[[ "${1:-}" == "--auto" ]] && AUTO=true

cd "$REPO_DIR"

# ─── Colors ─────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[0;33m'
NC='\033[0m'

# ─── Preflight ──────────────────────────────────────────────────────────

if ! git remote get-url upstream &>/dev/null; then
    echo -e "${RED}Error: 'upstream' remote not configured${NC}"
    echo "  git remote add upstream git@github.com:nicobailon/visual-explainer.git"
    exit 1
fi

if ! git diff --quiet HEAD 2>/dev/null; then
    if $AUTO; then
        echo -e "${YELLOW}Warning: uncommitted changes exist, proceeding anyway (--auto)${NC}"
    else
        echo -e "${YELLOW}Warning: you have uncommitted changes.${NC}"
        git status --short
        echo ""
        read -rp "Continue anyway? [y/N] " confirm
        [[ "$confirm" =~ ^[Yy]$ ]] || exit 1
    fi
fi

# ─── 1. Fetch upstream ─────────────────────────────────────────────────

echo -e "${CYAN}==> Fetching upstream...${NC}"
git fetch upstream

UPSTREAM_HEAD=$(git log upstream/main -1 --format='%h %s')
UPSTREAM_HASH=$(git log upstream/main -1 --format='%h')
echo -e "    Upstream HEAD: ${GREEN}${UPSTREAM_HEAD}${NC}"

# ─── 2. Save .arpagon/ ─────────────────────────────────────────────────

echo -e "${CYAN}==> Saving .arpagon/ and custom files...${NC}"
TEMP=$(mktemp -d)
trap 'rm -rf "$TEMP"' EXIT
cp -r .arpagon "$TEMP/"
[ -f FORK.md ] && cp FORK.md "$TEMP/"

# ─── 3. Checkout upstream files ────────────────────────────────────────

echo -e "${CYAN}==> Syncing all files from upstream/main...${NC}"
git checkout upstream/main -- .

# ─── 4. Restore .arpagon/ ──────────────────────────────────────────────

echo -e "${CYAN}==> Restoring .arpagon/ ...${NC}"
cp -r "$TEMP/.arpagon" .
[ -f "$TEMP/FORK.md" ] && cp "$TEMP/FORK.md" .

# ─── 5. Copy custom files ──────────────────────────────────────────────

echo -e "${CYAN}==> Copying custom files from .arpagon/files/ ...${NC}"
if [ -d ".arpagon/files" ]; then
    cd .arpagon/files
    find . -type f | while read -r f; do
        target="$REPO_DIR/${f#./}"
        mkdir -p "$(dirname "$target")"
        cp "$f" "$target"
        echo -e "    ${GREEN}+${NC} ${f#./}"
    done
    cd "$REPO_DIR"
fi

# ─── 6. Remove replaced upstream files ─────────────────────────────────

echo -e "${CYAN}==> Removing replaced upstream files...${NC}"

if [ -f scripts/share.sh ]; then
    rm -f scripts/share.sh
    echo -e "    ${RED}-${NC} scripts/share.sh → replaced by scripts/upload.py"
fi

if [ -d .claude-plugin ]; then
    rm -rf .claude-plugin
    echo -e "    ${RED}-${NC} .claude-plugin/"
fi

# ─── 7. Apply patches ──────────────────────────────────────────────────

echo -e "${CYAN}==> Applying patches...${NC}"
PATCH_OUTPUT=$(python3 .arpagon/apply_patches.py 2>&1)
echo "$PATCH_OUTPUT"

# Check for warnings
if echo "$PATCH_OUTPUT" | grep -q "⚠️"; then
    HAS_WARNINGS=true
else
    HAS_WARNINGS=false
fi

# ─── 8. Summary ────────────────────────────────────────────────────────

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"

if $HAS_WARNINGS; then
    echo -e "${YELLOW}  Sync complete WITH WARNINGS${NC}"
    echo -e "${YELLOW}  Some patches could not find their targets.${NC}"
    echo -e "${YELLOW}  Update .arpagon/apply_patches.py before committing.${NC}"
    EXIT_CODE=1
else
    echo -e "${GREEN}  Sync complete — all patches applied cleanly ✅${NC}"
    EXIT_CODE=0
fi

echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  Upstream: ${CYAN}${UPSTREAM_HEAD}${NC}"
echo ""

if $AUTO && ! $HAS_WARNINGS; then
    echo -e "  Ready to commit."
else
    echo -e "  Review: ${CYAN}git diff --stat${NC}"
    echo -e "  Commit: ${CYAN}git add -A && git commit -m 'chore: sync upstream ${UPSTREAM_HASH} + apply arpagon patches'${NC}"
fi

echo ""
exit $EXIT_CODE
