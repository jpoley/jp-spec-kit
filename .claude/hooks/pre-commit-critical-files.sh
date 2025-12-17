#!/bin/bash
# Pre-commit hook: ABSOLUTE BLOCK on deletion of critical files
#
# This hook prevents deletion of files essential for CI/CD pipelines.
# Added after the Dec 14, 2025 incident where docs/docfx.json was
# accidentally deleted, breaking documentation deployment for 7+ runs.
#
# THERE IS NO BYPASS. These files should NEVER be deleted.
# If you think you need to delete them, you are wrong.
# Talk to the team first.

set -euo pipefail

# Critical files that should NEVER be deleted without explicit intent
CRITICAL_FILES=(
    "user-docs/docfx.json"
    "user-docs/toc.yml"
    "user-docs/index.md"
    ".github/workflows/docs.yml"
    ".github/workflows/ci.yml"
    ".github/workflows/release.yml"
    "pyproject.toml"
    "CLAUDE.md"
)

# Check for deleted files in the staging area
DELETED_FILES=$(git diff --cached --name-only --diff-filter=D 2>/dev/null || true)

if [ -z "$DELETED_FILES" ]; then
    exit 0
fi

BLOCKED=0
BLOCKED_LIST=""

for critical in "${CRITICAL_FILES[@]}"; do
    if echo "$DELETED_FILES" | grep -qx "$critical"; then
        BLOCKED=1
        BLOCKED_LIST="${BLOCKED_LIST}\n  - $critical"
    fi
done

if [ $BLOCKED -eq 1 ]; then
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════════╗"
    echo "║  🛑 CRITICAL FILE DELETION BLOCKED                                ║"
    echo "╠═══════════════════════════════════════════════════════════════════╣"
    echo "║  You are attempting to delete files essential for CI/CD:          ║"
    echo -e "$BLOCKED_LIST"
    echo "║                                                                   ║"
    echo "║  This will break:                                                 ║"
    echo "║    - Documentation deployment                                     ║"
    echo "║    - CI pipelines                                                 ║"
    echo "║    - Release workflows                                            ║"
    echo "║                                                                   ║"
    echo "║  THERE IS NO BYPASS. You cannot delete these files.               ║"
    echo "║  If you think you need to, you are wrong. Ask the team.           ║"
    echo "║                                                                   ║"
    echo "║  History: Dec 14, 2025 - docfx.json deletion caused 7+ CI fails   ║"
    echo "║           because Claude was a fuckhead and didn't check.         ║"
    echo "╚═══════════════════════════════════════════════════════════════════╝"
    echo ""
    exit 1
fi

exit 0
