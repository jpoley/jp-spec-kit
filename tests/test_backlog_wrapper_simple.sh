#!/bin/bash
# Quick smoke test for bk wrapper

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BK_WRAPPER="$PROJECT_ROOT/scripts/bin/bk"

echo "========== BK Wrapper Smoke Test =========="

# Setup
TEST_DIR=$(mktemp -d)
cd "$TEST_DIR"
git init -q
backlog init --defaults test-project >/dev/null 2>&1

echo "✓ Test environment created"

# Test 1: Passthrough
output=$("$BK_WRAPPER" task create "Test task" 2>&1)
if [[ "$output" == *"Created task task-"* ]]; then
    echo "✓ Test 1: Passthrough works"
else
    echo "✗ Test 1 FAILED: $output"
    exit 1
fi

# Test 2: Exit code on success
if "$BK_WRAPPER" task list >/dev/null 2>&1; then
    echo "✓ Test 2: Exit code preserved (success)"
else
    echo "✗ Test 2 FAILED"
    exit 1
fi

# Test 3: Exit code on failure
if ! "$BK_WRAPPER" task view nonexistent >/dev/null 2>&1; then
    echo "✓ Test 3: Exit code preserved (failure)"
else
    echo "✗ Test 3 FAILED"
    exit 1
fi

# Test 4: Zsh compatibility
if command -v zsh &>/dev/null; then
    if zsh -c "'$BK_WRAPPER' task list" >/dev/null 2>&1; then
        echo "✓ Test 4: Zsh compatibility"
    else
        echo "✗ Test 4 FAILED"
        exit 1
    fi
else
    echo "⚠ Test 4: Zsh not installed (skipped)"
fi

# Cleanup
cd /tmp
rm -rf "$TEST_DIR"

echo ""
echo "=========================================="
echo "All smoke tests PASSED!"
echo "=========================================="
