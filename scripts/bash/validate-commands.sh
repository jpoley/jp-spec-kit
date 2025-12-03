#!/bin/bash
# Pre-commit hook to validate dev-setup consistency
# Ensures .claude/commands/ only contains symlinks to templates/

set -e

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

echo "🔍 Validating dev-setup consistency..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

VALIDATION_FAILED=0

# ============================================================
# CHECK 1: No non-symlink .md files in .claude/commands
# ============================================================
echo ""
echo "📋 Checking for non-symlink .md files in .claude/commands/..."

NON_SYMLINKS=$(find .claude/commands -name "*.md" -type f 2>/dev/null || true)

if [ -n "$NON_SYMLINKS" ]; then
    echo -e "${RED}❌ ERROR: Found non-symlink .md files in .claude/commands/${NC}"
    echo ""
    echo "Files that should be symlinks:"
    echo "$NON_SYMLINKS"
    echo ""
    echo -e "${YELLOW}All command files in .claude/commands/ must be symlinks to templates/${NC}"
    echo ""
    echo "To fix:"
    echo "  1. Move enhanced content to templates/commands/"
    echo "     Example: mv .claude/commands/jpspec/implement.md templates/commands/jpspec/"
    echo ""
    echo "  2. Run: specify dev-setup --force"
    echo "     Or: uv run specify dev-setup --force"
    echo ""
    VALIDATION_FAILED=1
else
    echo -e "${GREEN}✓ All .md files in .claude/commands/ are symlinks${NC}"
fi

# ============================================================
# CHECK 2: All symlinks resolve correctly
# ============================================================
echo ""
echo "🔗 Validating symlink targets..."

BROKEN_SYMLINKS=""
while IFS= read -r symlink; do
    if [ -n "$symlink" ] && [ ! -e "$symlink" ]; then
        TARGET=$(readlink "$symlink" 2>/dev/null || echo "unknown")
        BROKEN_SYMLINKS="${BROKEN_SYMLINKS}${symlink} -> ${TARGET}\n"
    fi
done < <(find .claude/commands -type l 2>/dev/null || true)

if [ -n "$BROKEN_SYMLINKS" ]; then
    echo -e "${RED}❌ ERROR: Found broken symlinks in .claude/commands/${NC}"
    echo ""
    echo "Broken symlinks:"
    echo -e "$BROKEN_SYMLINKS"
    echo ""
    echo "To fix:"
    echo "  1. Ensure corresponding files exist in templates/commands/"
    echo "  2. Run: specify dev-setup --force"
    echo ""
    VALIDATION_FAILED=1
else
    echo -e "${GREEN}✓ All symlinks resolve correctly${NC}"
fi

# ============================================================
# CHECK 3: Verify speckit structure
# ============================================================
echo ""
echo "📦 Checking speckit commands structure..."

SPECKIT_DIR=".claude/commands/speckit"
if [ ! -d "$SPECKIT_DIR" ]; then
    echo -e "${YELLOW}⚠ Warning: $SPECKIT_DIR directory does not exist${NC}"
    echo "Run: specify dev-setup --force"
else
    # Count symlinks vs total .md files
    SYMLINK_COUNT=$(find "$SPECKIT_DIR" -maxdepth 1 -type l -name "*.md" 2>/dev/null | wc -l)
    TOTAL_MD=$(find "$SPECKIT_DIR" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l)

    if [ "$SYMLINK_COUNT" -ne "$TOTAL_MD" ]; then
        echo -e "${RED}❌ ERROR: Not all speckit commands are symlinks${NC}"
        echo "Expected: $TOTAL_MD symlinks, Found: $SYMLINK_COUNT"
        echo ""
        echo "Non-symlink files:"
        find "$SPECKIT_DIR" -maxdepth 1 -name "*.md" -type f
        echo ""
        VALIDATION_FAILED=1
    else
        echo -e "${GREEN}✓ All speckit commands are symlinks ($SYMLINK_COUNT files)${NC}"
    fi
fi

# ============================================================
# CHECK 4: Verify jpspec structure (if exists)
# ============================================================
echo ""
echo "🎯 Checking jpspec commands structure..."

JPSPEC_DIR=".claude/commands/jpspec"
if [ ! -d "$JPSPEC_DIR" ]; then
    echo -e "${YELLOW}⚠ Note: $JPSPEC_DIR directory does not exist${NC}"
    echo "This is expected if jpspec commands haven't been migrated to templates yet"
else
    # Count symlinks vs total .md files
    JPSPEC_SYMLINKS=$(find "$JPSPEC_DIR" -maxdepth 1 -type l -name "*.md" 2>/dev/null | wc -l)
    JPSPEC_TOTAL=$(find "$JPSPEC_DIR" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l)

    if [ "$JPSPEC_SYMLINKS" -ne "$JPSPEC_TOTAL" ]; then
        echo -e "${RED}❌ ERROR: Not all jpspec commands are symlinks${NC}"
        echo "Expected: $JPSPEC_TOTAL symlinks, Found: $JPSPEC_SYMLINKS"
        echo ""
        echo "Non-symlink files:"
        find "$JPSPEC_DIR" -maxdepth 1 -name "*.md" -type f
        echo ""
        VALIDATION_FAILED=1
    else
        echo -e "${GREEN}✓ All jpspec commands are symlinks ($JPSPEC_SYMLINKS files)${NC}"
    fi
fi

# ============================================================
# FINAL RESULT
# ============================================================
echo ""
echo "=========================================="
if [ $VALIDATION_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ COMMAND VALIDATION PASSED${NC}"
    echo "=========================================="
    echo ""
    echo "All checks passed:"
    echo "  ✓ No non-symlink .md files in .claude/commands/"
    echo "  ✓ All symlinks resolve correctly"
    echo "  ✓ Command structure is correct"
    echo ""
    exit 0
else
    echo -e "${RED}❌ COMMAND VALIDATION FAILED${NC}"
    echo "=========================================="
    echo ""
    echo "Please fix the issues above before committing."
    echo ""
    echo "Quick fix command:"
    echo "  specify dev-setup --force"
    echo ""
    exit 1
fi
