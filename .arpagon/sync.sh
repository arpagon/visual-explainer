#!/bin/bash
# Sync visual-explainer with upstream (fetch files only, no patching).
# The agent applies preferences after this script runs.
#
# Usage:
#   bash .arpagon/sync.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_DIR"

# ─── Colors ─────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

# ─── Preflight ──────────────────────────────────────────────────────────

if ! git remote get-url upstream &>/dev/null; then
    echo -e "${RED}Error: 'upstream' remote not configured${NC}"
    echo "  git remote add upstream git@github.com:nicobailon/visual-explainer.git"
    exit 1
fi

# ─── 1. Fetch upstream ─────────────────────────────────────────────────

echo -e "${CYAN}==> Fetching upstream...${NC}"
git fetch upstream

UPSTREAM_HEAD=$(git log upstream/main -1 --format='%h %s')
echo -e "    Upstream HEAD: ${GREEN}${UPSTREAM_HEAD}${NC}"

# ─── 2. Save our stuff ─────────────────────────────────────────────────

echo -e "${CYAN}==> Saving .arpagon/ and custom files...${NC}"
TEMP=$(mktemp -d)
trap 'rm -rf "$TEMP"' EXIT
cp -r .arpagon "$TEMP/"
[ -f FORK.md ] && cp FORK.md "$TEMP/"

# ─── 3. Checkout upstream files ────────────────────────────────────────

echo -e "${CYAN}==> Syncing all files from upstream/main...${NC}"
git checkout upstream/main -- .

# ─── 4. Restore our stuff ──────────────────────────────────────────────

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
[ -f scripts/share.sh ] && rm -f scripts/share.sh && echo -e "    ${RED}-${NC} scripts/share.sh"
[ -d .claude-plugin ]   && rm -rf .claude-plugin   && echo -e "    ${RED}-${NC} .claude-plugin/"

# ─── 7. Done — agent applies preferences next ──────────────────────────

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Upstream synced. SKILL.md is raw upstream.${NC}"
echo -e "${GREEN}  Now read .arpagon/preferences.yaml and apply.${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  Upstream: ${CYAN}${UPSTREAM_HEAD}${NC}"
echo ""
