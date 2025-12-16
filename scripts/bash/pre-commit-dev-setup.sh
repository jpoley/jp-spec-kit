#!/usr/bin/env bash
#
# pre-commit-dev-setup.sh - Dev-setup validation pre-commit hook
#
# Validates .claude/commands/ structure to ensure single-source-of-truth:
# - All .md files must be symlinks (R1)
# - All symlinks must resolve (R2)
# - All symlinks must point to templates/commands/ (R3)
# - Expected subdirectories exist (R7)
#
# Usage:
#   ./scripts/bash/pre-commit-dev-setup.sh
#
# Install as git hook:
#   ln -s ../../scripts/bash/pre-commit-dev-setup.sh .git/hooks/pre-commit-dev-setup
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Running dev-setup validation...${NC}"
echo ""

# Check if we're in the root of the repository
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}Error: Must be run from repository root${NC}"
    exit 1
fi

# Track status
STATUS=0

# Key directories
CLAUDE_COMMANDS_DIR=".claude/commands"
TEMPLATES_COMMANDS_DIR="templates/commands"

# 1. Verify .claude/commands/ directory exists
echo -e "${BLUE}1. Checking .claude/commands/ directory exists...${NC}"
if [ ! -d "$CLAUDE_COMMANDS_DIR" ]; then
    echo -e "${RED}✗ Directory not found: $CLAUDE_COMMANDS_DIR${NC}"
    echo -e "${RED}  Run: uv run flowspec dev-setup${NC}"
    STATUS=1
else
    echo -e "${GREEN}✓ Directory exists${NC}"
fi
echo ""

# 2. Check expected subdirectories exist (R7)
echo -e "${BLUE}2. Checking subdirectory structure...${NC}"
EXPECTED_DIRS=("flowspec" "spec")
MISSING_DIRS=()

for dir in "${EXPECTED_DIRS[@]}"; do
    if [ ! -d "$CLAUDE_COMMANDS_DIR/$dir" ]; then
        MISSING_DIRS+=("$dir")
    fi
done

if [ ${#MISSING_DIRS[@]} -gt 0 ]; then
    echo -e "${RED}✗ Missing expected subdirectories:${NC}"
    for dir in "${MISSING_DIRS[@]}"; do
        echo -e "${RED}  - $CLAUDE_COMMANDS_DIR/$dir/${NC}"
    done
    echo -e "${RED}  Run: uv run flowspec dev-setup --force${NC}"
    STATUS=1
else
    echo -e "${GREEN}✓ All expected subdirectories exist (flowspec/, spec/)${NC}"
fi
echo ""

# Exit early if basic structure is missing
if [ $STATUS -ne 0 ]; then
    echo -e "${RED}✗ Dev-setup structure is incomplete${NC}"
    echo -e "${RED}  Please run: uv run flowspec dev-setup --force${NC}"
    echo ""
    exit 1
fi

# 3. Check all .md files are symlinks (R1)
echo -e "${BLUE}3. Checking all .md files are symlinks...${NC}"
NON_SYMLINKS=()

# Find all .md files and check if they are symlinks
while IFS= read -r -d '' file; do
    if [ ! -L "$file" ]; then
        # Get relative path from .claude/commands/
        rel_path="${file#$CLAUDE_COMMANDS_DIR/}"
        NON_SYMLINKS+=("$rel_path")
    fi
done < <(find "$CLAUDE_COMMANDS_DIR" -name "*.md" -print0)

if [ ${#NON_SYMLINKS[@]} -gt 0 ]; then
    echo -e "${RED}✗ Found ${#NON_SYMLINKS[@]} non-symlink .md file(s):${NC}"
    for file in "${NON_SYMLINKS[@]}"; do
        echo -e "${RED}  - $file${NC}"
    done
    echo -e "${RED}"
    echo -e "${RED}  All .md files must be symlinks to templates/commands/${NC}"
    echo -e "${RED}  Run: uv run flowspec dev-setup --force${NC}"
    STATUS=1
else
    echo -e "${GREEN}✓ All .md files are symlinks${NC}"
fi
echo ""

# 4. Check all symlinks resolve (R2)
echo -e "${BLUE}4. Checking all symlinks resolve...${NC}"
BROKEN_SYMLINKS=()

# Find all .md symlinks and check if they resolve
while IFS= read -r -d '' symlink; do
    if [ -L "$symlink" ]; then
        # Check if symlink resolves to an existing file
        if [ ! -e "$symlink" ]; then
            # Get relative path from .claude/commands/
            rel_path="${symlink#$CLAUDE_COMMANDS_DIR/}"
            # Get the target of the symlink
            target=$(readlink "$symlink" 2>/dev/null || echo "unknown")
            BROKEN_SYMLINKS+=("$rel_path -> $target")
        fi
    fi
done < <(find "$CLAUDE_COMMANDS_DIR" -name "*.md" -print0)

if [ ${#BROKEN_SYMLINKS[@]} -gt 0 ]; then
    echo -e "${RED}✗ Found ${#BROKEN_SYMLINKS[@]} broken symlink(s):${NC}"
    for symlink in "${BROKEN_SYMLINKS[@]}"; do
        echo -e "${RED}  - $symlink${NC}"
    done
    echo -e "${RED}"
    echo -e "${RED}  Run: uv run flowspec dev-setup --force${NC}"
    STATUS=1
else
    echo -e "${GREEN}✓ All symlinks resolve to existing files${NC}"
fi
echo ""

# 5. Check all symlinks point to templates/commands/ (R3)
echo -e "${BLUE}5. Checking all symlinks point to templates/commands/...${NC}"
MISPOINTED_SYMLINKS=()

# Find all .md symlinks and check their targets
while IFS= read -r -d '' symlink; do
    if [ -L "$symlink" ] && [ -e "$symlink" ]; then
        # Resolve symlink to absolute path
        target=$(readlink -f "$symlink" 2>/dev/null || echo "")

        if [ -n "$target" ]; then
            # Get absolute path to templates/commands/
            templates_abs=$(readlink -f "$TEMPLATES_COMMANDS_DIR" 2>/dev/null || echo "")

            # Check if target is under templates/commands/
            if [[ "$target" != "$templates_abs"/* ]]; then
                # Get relative path from .claude/commands/
                rel_path="${symlink#$CLAUDE_COMMANDS_DIR/}"
                MISPOINTED_SYMLINKS+=("$rel_path -> $target")
            fi
        fi
    fi
done < <(find "$CLAUDE_COMMANDS_DIR" -name "*.md" -print0)

if [ ${#MISPOINTED_SYMLINKS[@]} -gt 0 ]; then
    echo -e "${RED}✗ Found ${#MISPOINTED_SYMLINKS[@]} symlink(s) pointing outside templates/commands/:${NC}"
    for symlink in "${MISPOINTED_SYMLINKS[@]}"; do
        echo -e "${RED}  - $symlink${NC}"
    done
    echo -e "${RED}"
    echo -e "${RED}  All symlinks must point to $TEMPLATES_COMMANDS_DIR${NC}"
    echo -e "${RED}  Run: uv run flowspec dev-setup --force${NC}"
    STATUS=1
else
    echo -e "${GREEN}✓ All symlinks point to templates/commands/${NC}"
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
    echo -e "${YELLOW}To fix all issues:${NC}"
    echo -e "${YELLOW}  uv run flowspec dev-setup --force${NC}"
    echo ""
    exit 1
fi
