#!/bin/bash
# Pre-PR Quality Check Script
# Run this before creating any PR to ensure CI will pass

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "  Pre-PR Quality Check"
echo "=========================================="
echo ""

# Track overall status
FAILED=0

# 1. DCO Sign-off Check
echo -n "1. Checking DCO sign-off... "
if git log -1 --format="%B" | grep -qi "signed-off-by"; then
    echo -e "${GREEN}✓ Present${NC}"
else
    echo -e "${RED}✗ MISSING${NC}"
    echo "   Fix: git commit --amend -s --no-edit"
    FAILED=1
fi

# 2. Ruff Lint Check
echo -n "2. Running ruff check... "
if ruff check . --quiet 2>/dev/null; then
    echo -e "${GREEN}✓ Passed${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    echo "   Fix: ruff check . --fix"
    FAILED=1
fi

# 3. Ruff Format Check
echo -n "3. Checking ruff format... "
if ruff format --check . --quiet 2>/dev/null; then
    echo -e "${GREEN}✓ Passed${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    echo "   Fix: ruff format ."
    FAILED=1
fi

# 4. Test Check
echo -n "4. Running tests... "
if uv run pytest tests/ -q --tb=no 2>/dev/null; then
    echo -e "${GREEN}✓ Passed${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    echo "   Fix: Review test failures with: uv run pytest tests/ -v"
    FAILED=1
fi

echo ""
echo "=========================================="

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All checks passed! Ready for PR.${NC}"
    echo ""
    echo "Create PR with:"
    echo "  gh pr create --title \"...\" --body \"...\""
    exit 0
else
    echo -e "${RED}Some checks failed. Fix issues before creating PR.${NC}"
    echo ""
    echo "Quick fix all:"
    echo "  ruff check . --fix && ruff format . && git add -A && git commit --amend -s --no-edit"
    echo "  Note: This only adds DCO sign-off to the most recent commit."
    echo "  For multiple commits without sign-off, use: git rebase -i HEAD~N and add '-s' to each commit."
    exit 1
fi
