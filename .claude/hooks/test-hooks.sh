#!/bin/bash
#
# Test script for Claude Code hooks
#
# Tests each hook with various scenarios to ensure correct behavior
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Test function
run_test() {
    local test_name="$1"
    local hook_script="$2"
    local input_json="$3"
    local expected_decision="$4"
    local description="$5"

    TESTS_RUN=$((TESTS_RUN + 1))

    echo -e "\n${YELLOW}Test $TESTS_RUN: $test_name${NC}"
    echo "Description: $description"
    echo "Input: $input_json"

    # Run hook and capture output
    output=$(echo "$input_json" | "$SCRIPT_DIR/$hook_script" 2>&1)
    exit_code=$?

    echo "Output: $output"
    echo "Exit code: $exit_code"

    # Verify exit code is 0
    if [[ $exit_code -ne 0 ]]; then
        echo -e "${RED}FAIL: Non-zero exit code${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi

    # Extract decision from JSON output
    decision=$(echo "$output" | python3 -c "import json, sys; print(json.load(sys.stdin).get('decision', ''))" 2>/dev/null || echo "")

    # Verify decision matches expected
    if [[ "$decision" == "$expected_decision" ]]; then
        echo -e "${GREEN}PASS: Decision = $decision${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}FAIL: Expected '$expected_decision', got '$decision'${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

echo "========================================"
echo "Claude Code Hooks Test Suite"
echo "========================================"

# Test 1: Sensitive file protection - .env file
run_test \
    "Sensitive file - .env" \
    "pre-tool-use-sensitive-files.py" \
    '{"session_id": "test", "hook_event_name": "PreToolUse", "tool_name": "Write", "tool_input": {"file_path": "/path/to/.env"}}' \
    "ask" \
    "Should ask for confirmation when modifying .env file"

# Test 2: Sensitive file protection - normal Python file
run_test \
    "Normal file - app.py" \
    "pre-tool-use-sensitive-files.py" \
    '{"session_id": "test", "hook_event_name": "PreToolUse", "tool_name": "Write", "tool_input": {"file_path": "/path/to/src/app.py"}}' \
    "allow" \
    "Should allow modification of normal Python files"

# Test 3: Sensitive file protection - CLAUDE.md
run_test \
    "Sensitive file - CLAUDE.md" \
    "pre-tool-use-sensitive-files.py" \
    '{"session_id": "test", "hook_event_name": "PreToolUse", "tool_name": "Edit", "tool_input": {"file_path": "/path/to/CLAUDE.md"}}' \
    "ask" \
    "Should ask for confirmation when modifying CLAUDE.md"

# Test 4: Sensitive file protection - package-lock.json
run_test \
    "Sensitive file - package-lock.json" \
    "pre-tool-use-sensitive-files.py" \
    '{"session_id": "test", "hook_event_name": "PreToolUse", "tool_name": "Write", "tool_input": {"file_path": "/path/to/package-lock.json"}}' \
    "ask" \
    "Should ask for confirmation when modifying package-lock.json"

# Test 5: Sensitive file protection - uv.lock
run_test \
    "Sensitive file - uv.lock" \
    "pre-tool-use-sensitive-files.py" \
    '{"session_id": "test", "hook_event_name": "PreToolUse", "tool_name": "Write", "tool_input": {"file_path": "/path/to/uv.lock"}}' \
    "ask" \
    "Should ask for confirmation when modifying uv.lock"

# Test 6: Sensitive file protection - .git/ directory
run_test \
    "Sensitive path - .git/" \
    "pre-tool-use-sensitive-files.py" \
    '{"session_id": "test", "hook_event_name": "PreToolUse", "tool_name": "Write", "tool_input": {"file_path": "/path/to/.git/config"}}' \
    "ask" \
    "Should ask for confirmation when modifying .git/ directory"

# Test 7: Git safety - force push
run_test \
    "Dangerous git - force push" \
    "pre-tool-use-git-safety.py" \
    '{"session_id": "test", "hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": "git push --force origin main"}}' \
    "ask" \
    "Should ask for confirmation on force push"

# Test 8: Git safety - force push with -f
run_test \
    "Dangerous git - push -f" \
    "pre-tool-use-git-safety.py" \
    '{"session_id": "test", "hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": "git push -f origin feature"}}' \
    "ask" \
    "Should ask for confirmation on push -f"

# Test 9: Git safety - hard reset
run_test \
    "Dangerous git - hard reset" \
    "pre-tool-use-git-safety.py" \
    '{"session_id": "test", "hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": "git reset --hard HEAD~1"}}' \
    "ask" \
    "Should ask for confirmation on hard reset"

# Test 10: Git safety - interactive rebase (should deny)
run_test \
    "Dangerous git - rebase -i" \
    "pre-tool-use-git-safety.py" \
    '{"session_id": "test", "hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": "git rebase -i HEAD~3"}}' \
    "deny" \
    "Should deny interactive rebase (not supported)"

# Test 11: Git safety - clean -fd
run_test \
    "Dangerous git - clean -fd" \
    "pre-tool-use-git-safety.py" \
    '{"session_id": "test", "hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": "git clean -fd"}}' \
    "ask" \
    "Should ask for confirmation on clean -fd"

# Test 12: Git safety - safe command (git status)
run_test \
    "Safe git - status" \
    "pre-tool-use-git-safety.py" \
    '{"session_id": "test", "hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": "git status"}}' \
    "allow" \
    "Should allow safe git commands"

# Test 13: Git safety - safe command (git log)
run_test \
    "Safe git - log" \
    "pre-tool-use-git-safety.py" \
    '{"session_id": "test", "hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": "git log --oneline -5"}}' \
    "allow" \
    "Should allow safe git commands"

# Test 14: Git safety - safe command (git diff)
run_test \
    "Safe git - diff" \
    "pre-tool-use-git-safety.py" \
    '{"session_id": "test", "hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": "git diff HEAD~1"}}' \
    "allow" \
    "Should allow safe git commands"

# Test 15: Git safety - non-git command
run_test \
    "Non-git command" \
    "pre-tool-use-git-safety.py" \
    '{"session_id": "test", "hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": "ls -la"}}' \
    "allow" \
    "Should allow non-git commands"

# Summary
echo ""
echo "========================================"
echo "Test Summary"
echo "========================================"
echo "Tests run: $TESTS_RUN"
echo -e "${GREEN}Tests passed: $TESTS_PASSED${NC}"
if [[ $TESTS_FAILED -gt 0 ]]; then
    echo -e "${RED}Tests failed: $TESTS_FAILED${NC}"
    exit 1
else
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
fi
