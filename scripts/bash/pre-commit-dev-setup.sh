#!/usr/bin/env bash
#
# pre-commit-dev-setup.sh - Dev-setup validation pre-commit hook
#
# This script validates that .claude/commands/ contains ONLY symlinks
# pointing to templates/commands/, preventing dev-setup drift.
#
# Part of ADR-010 dev-setup validation architecture (Tier 1).
#
# Usage:
#   ./scripts/bash/pre-commit-dev-setup.sh    # Manual execution
#   pre-commit run dev-setup-validation        # Via pre-commit framework
#
# Exit codes:
#   0 - All validations passed
#   1 - Validation failures detected

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
COMMANDS_DIR=".claude/commands"
TEMPLATES_DIR="templates/commands"

# Track validation status
STATUS=0

echo -e "${BLUE}Running dev-setup validation...${NC}"
echo ""

# Check if we're in the root of the repository
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}Error: Must be run from repository root${NC}"
    exit 1
fi

# Check 1: Detect non-symlink .md files in .claude/commands/
echo -e "${BLUE}1. Checking for non-symlink .md files...${NC}"
NON_SYMLINKS=$(find "$COMMANDS_DIR" -name "*.md" -type f 2>/dev/null || true)

if [ -n "$NON_SYMLINKS" ]; then
    echo -e "${RED}✗ Found regular files (must be symlinks):${NC}"
    echo "$NON_SYMLINKS" | while IFS= read -r file; do
        echo "  - $file"
    done
    echo ""
    echo -e "${YELLOW}To fix:${NC}"
    echo "  specify dev-setup --force"
    echo ""
    STATUS=1
else
    echo -e "${GREEN}✓ All .md files are symlinks${NC}"
fi
echo ""

# Check 2: Detect broken symlinks
echo -e "${BLUE}2. Checking for broken symlinks...${NC}"
BROKEN_SYMLINKS=$(find "$COMMANDS_DIR" -type l ! -exec test -e {} \; -print 2>/dev/null || true)

if [ -n "$BROKEN_SYMLINKS" ]; then
    echo -e "${RED}✗ Found broken symlinks:${NC}"
    echo "$BROKEN_SYMLINKS" | while IFS= read -r file; do
        if [ -n "$file" ]; then
            target=$(readlink "$file" 2>/dev/null || echo "unknown")
            echo "  - $file -> $target (missing)"
        fi
    done
    echo ""
    echo -e "${YELLOW}To fix:${NC}"
    echo "  specify dev-setup --force"
    echo ""
    STATUS=1
else
    echo -e "${GREEN}✓ All symlinks are valid${NC}"
fi
echo ""

# Summary
if [ $STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ Dev-setup validation passed${NC}"
    echo ""
else
    echo -e "${RED}✗ Dev-setup validation failed${NC}"
    echo -e "${RED}  Please fix the issues before committing${NC}"
    echo ""
    echo "For more information, see:"
    echo "  docs/adr/ADR-010-dev-setup-validation-architecture.md"
    echo ""
    exit 1
fi
