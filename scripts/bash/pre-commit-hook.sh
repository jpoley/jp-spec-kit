#!/usr/bin/env bash
#
# pre-commit-hook.sh - Pre-commit validation hook (Inner Loop)
#
# This script runs fast validation checks before allowing a commit.
# Install it as a git hook with: ln -s ../../scripts/bash/pre-commit-hook.sh .git/hooks/pre-commit
#
# Or use the install script: ./scripts/bash/install-pre-commit-hook.sh
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Running pre-commit checks...${NC}"
echo ""

# Check if we're in the root of the repository
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}Error: Must be run from repository root${NC}"
    exit 1
fi

# Track status
STATUS=0

# 1. Format check (fast)
echo -e "${BLUE}1. Checking code formatting...${NC}"
if ruff format --check . > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Formatting is correct${NC}"
else
    echo -e "${YELLOW}⚠ Formatting issues detected. Auto-fixing...${NC}"
    ruff format .
    echo -e "${GREEN}✓ Code formatted${NC}"
fi
echo ""

# 2. Linting (fast)
echo -e "${BLUE}2. Running linter...${NC}"
if ruff check . --fix > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Linting passed${NC}"
else
    echo -e "${RED}✗ Linting failed${NC}"
    echo "Run: ruff check . --fix"
    STATUS=1
fi
echo ""

# 3. Code quality validation (staged Python files only)
# Addresses issues from PR #379 where encoding was fixed inconsistently
# NOTE: Known limitations:
#   - Multi-line function calls are not detected (grep is line-based)
#   - Nested parentheses in arguments may confuse pattern matching
#   - "encoding=" in comments may cause false negatives (rare)
echo -e "${BLUE}3. Running code quality validation on staged files...${NC}"

# Helper to safely print untrusted content (prevents terminal escape injection)
# Strips control characters including CR (\r) which could be used to overwrite output lines
safe_print() {
    printf '%s\n' "$1" | tr -d '\000-\010\013-\037\177'
}

# Get staged Python files using null delimiter for spaces in filenames
STAGED_FILES=()
while IFS= read -r -d '' file; do
    if [[ "$file" == *.py ]]; then
        STAGED_FILES+=("$file")
    fi
done < <(git diff --cached --name-only --diff-filter=ACM -z 2>/dev/null)

if [ "${#STAGED_FILES[@]}" -gt 0 ]; then
    ENCODING_ISSUES=""
    OPEN_ISSUES=""
    SHADOW_WARNINGS=""

    # Process each file only once (N ops instead of 3N)
    for file in "${STAGED_FILES[@]}"; do
        if [ -f "$file" ]; then
            # Get staged content once per file
            CONTENT=$(git show ":$file" 2>/dev/null || true)

            if [ -n "$CONTENT" ]; then
                # Check 1: write_text/read_text without encoding (require dot prefix)
                # Pattern: .write_text( or .read_text( without encoding=
                # Uses -E for extended regex (alternation with |)
                ISSUES=$(echo "$CONTENT" | grep -nE '\.(write_text|read_text)\(' | grep -v 'encoding=' || true)
                if [ -n "$ISSUES" ]; then
                    ENCODING_ISSUES="${ENCODING_ISSUES}${file}:\n${ISSUES}\n"
                fi

                # Check 2: open() without encoding - comprehensive binary mode detection
                # Uses word boundary \b to avoid matching .reopen(), file.open(), etc.
                OPEN_LINES=$(echo "$CONTENT" | grep -nE '\bopen\(' | grep -v 'encoding=' || true)
                while IFS= read -r line; do
                    if [ -n "$line" ]; then
                        # Extract the actual source content (after line number:)
                        LINE_CONTENT="${line#*:}"

                        # Skip if mode argument contains 'b' for binary (handles rb, wb, r+b, rb+, br, etc.)
                        # Matches both positional ('rb') and keyword (mode='rb') arguments
                        # Note: [^)]* may not work with nested parens like open(get_file(), 'rb')
                        if echo "$line" | grep -qE "['\"][rwax+]*b[rwax+]*['\"]|mode\s*=\s*['\"][rwax+]*b"; then
                            continue
                        fi
                        # Skip if actual source line is a comment (starts with #)
                        if echo "$LINE_CONTENT" | grep -qE '^\s*#'; then
                            continue
                        fi
                        # Skip function definitions named exactly 'open'
                        if echo "$line" | grep -qE 'def\s+open\s*\('; then
                            continue
                        fi
                        OPEN_ISSUES="${OPEN_ISSUES}${file}:${line}\n"
                    fi
                done <<< "$OPEN_LINES"

                # Check 3: Shadowed Python built-ins - match complete parameter names only
                # Two-step approach: first find def lines, then check for parameter patterns
                # Pattern matches builtins as standalone parameters preceded by ( or ,
                # and followed by , : = ) - prevents matching 'user_id' for 'id'
                SHADOW_LINES=$(echo "$CONTENT" | grep -nE '^\s*def\s+\w+\s*\(' | grep -E '[(,]\s*(id|type|list|dict|input|filter|map|hash|format|range|len|sum|min|max|open|file|dir|help|vars|iter|next|set|str|int|float|bool|bytes|tuple|object|super|property|classmethod|staticmethod)\s*[,:)=]' || true)
                if [ -n "$SHADOW_LINES" ]; then
                    SHADOW_WARNINGS="${SHADOW_WARNINGS}${file}:\n${SHADOW_LINES}\n"
                fi
            fi
        fi
    done

    # Report encoding issues (blocking)
    if [ -n "$ENCODING_ISSUES" ]; then
        echo -e "${RED}✗ File I/O missing encoding=\"utf-8\":${NC}"
        safe_print "$ENCODING_ISSUES"
        STATUS=1
    else
        echo -e "${GREEN}✓ All write_text/read_text have encoding${NC}"
    fi

    # Report open() issues (blocking)
    if [ -n "$OPEN_ISSUES" ]; then
        echo -e "${RED}✗ open() calls missing encoding=\"utf-8\" (text mode):${NC}"
        safe_print "$OPEN_ISSUES"
        STATUS=1
    else
        echo -e "${GREEN}✓ All text-mode open() calls have encoding${NC}"
    fi

    # Report shadowing warnings (non-blocking)
    if [ -n "$SHADOW_WARNINGS" ]; then
        echo -e "${YELLOW}⚠ Possible shadowed Python built-ins (review manually):${NC}"
        safe_print "$SHADOW_WARNINGS"
    fi
else
    echo -e "${GREEN}✓ No Python files staged, skipping validation${NC}"
fi
echo ""

# 4. Dev-setup validation (fast)
echo -e "${BLUE}4. Validating dev-setup structure...${NC}"
if [ -f "scripts/bash/pre-commit-dev-setup.sh" ]; then
    if ./scripts/bash/pre-commit-dev-setup.sh > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Dev-setup validation passed${NC}"
    else
        echo -e "${RED}✗ Dev-setup validation failed${NC}"
        echo "Run: ./scripts/bash/pre-commit-dev-setup.sh"
        STATUS=1
    fi
else
    echo -e "${YELLOW}⚠ Dev-setup validation script not found, skipping${NC}"
fi
echo ""

# 5. Quick test run (only fast tests if marked)
echo -e "${BLUE}5. Running quick tests...${NC}"
if command -v pytest &> /dev/null; then
    # Run tests marked as 'quick' or all tests if no markers
    if pytest tests/ -m quick --tb=short > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Quick tests passed${NC}"
    elif pytest tests/ -x --tb=short > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Tests passed${NC}"
    else
        echo -e "${RED}✗ Tests failed${NC}"
        echo "Run: pytest tests/ -v"
        STATUS=1
    fi
else
    echo -e "${YELLOW}⚠ pytest not installed, skipping tests${NC}"
fi
echo ""

# Summary
if [ $STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ Pre-commit checks passed${NC}"
    echo ""
else
    echo -e "${RED}✗ Pre-commit checks failed${NC}"
    echo -e "${RED}  Please fix the issues before committing${NC}"
    echo ""
    exit 1
fi
