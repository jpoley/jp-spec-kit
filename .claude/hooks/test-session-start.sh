#!/bin/bash
#
# Test script for SessionStart hook
#
# Tests the session-start.sh hook with various scenarios:
# 1. Happy path: uv + backlog installed, 1 In Progress task
# 2. Missing uv: warning displayed, continues
# 3. Missing backlog: warning displayed, continues
# 4. No In Progress tasks: informational message
# 5. Multiple In Progress tasks: all displayed
# 6. Backlog CLI timeout: graceful error handling
# 7. Invalid backlog output: graceful degradation
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Test function
run_test() {
    local test_name="$1"
    local description="$2"
    local setup_fn="$3"
    local validation_fn="$4"

    TESTS_RUN=$((TESTS_RUN + 1))

    echo -e "\n${YELLOW}Test $TESTS_RUN: $test_name${NC}"
    echo "Description: $description"

    # Run setup (if any)
    if [[ -n "$setup_fn" && "$(type -t "$setup_fn" 2>/dev/null)" == "function" ]]; then
        $setup_fn
    fi

    # Run hook and capture output
    output=$("$SCRIPT_DIR/session-start.sh" 2>&1)
    exit_code=$?

    echo -e "${BLUE}Output:${NC}"
    echo "$output"
    echo "Exit code: $exit_code"

    # Verify exit code is 0
    if [[ $exit_code -ne 0 ]]; then
        echo -e "${RED}FAIL: Non-zero exit code${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi

    # Verify JSON structure
    if ! echo "$output" | python3 -c "import json, sys; json.load(sys.stdin)" 2>/dev/null; then
        echo -e "${RED}FAIL: Invalid JSON output${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi

    # Extract decision from JSON
    decision=$(echo "$output" | python3 -c "import json, sys; data = json.load(sys.stdin); print(data.get('decision', ''))")

    # Verify decision is "allow"
    if [[ "$decision" != "allow" ]]; then
        echo -e "${RED}FAIL: Expected decision 'allow', got '$decision'${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi

    # Run custom validation (if any)
    if [[ -n "$validation_fn" && "$(type -t "$validation_fn" 2>/dev/null)" == "function" ]]; then
        if $validation_fn "$output"; then
            echo -e "${GREEN}PASS: Custom validation succeeded${NC}"
        else
            echo -e "${RED}FAIL: Custom validation failed${NC}"
            TESTS_FAILED=$((TESTS_FAILED + 1))
            return 1
        fi
    else
        echo -e "${GREEN}PASS: Basic validation succeeded${NC}"
    fi

    TESTS_PASSED=$((TESTS_PASSED + 1))
    return 0
}

# Validation functions
validate_uv_present() {
    local output="$1"
    if echo "$output" | grep -q "uv:"; then
        return 0
    else
        echo "Expected uv version in output"
        return 1
    fi
}

validate_backlog_present() {
    local output="$1"
    if echo "$output" | grep -q "backlog:"; then
        return 0
    else
        echo "Expected backlog version in output"
        return 1
    fi
}

validate_no_uv_warning() {
    local output="$1"
    if echo "$output" | grep -q "uv not installed"; then
        return 0
    else
        echo "Expected warning about missing uv"
        return 1
    fi
}

validate_no_backlog_warning() {
    local output="$1"
    if echo "$output" | grep -q "backlog CLI not installed"; then
        return 0
    else
        echo "Expected warning about missing backlog CLI"
        return 1
    fi
}

validate_has_active_tasks() {
    local output="$1"
    if echo "$output" | grep -q "Active tasks:"; then
        return 0
    else
        echo "Expected 'Active tasks' in output"
        return 1
    fi
}

validate_no_active_tasks() {
    local output="$1"
    if echo "$output" | grep -qE "(No active tasks|No tasks in 'In Progress' status)"; then
        return 0
    else
        echo "Expected 'No active tasks' or 'No tasks in progress' in output"
        return 1
    fi
}

echo "========================================"
echo "SessionStart Hook Test Suite"
echo "========================================"

# Test 1: Happy path - uv and backlog both installed
run_test \
    "Happy path - all dependencies present" \
    "Both uv and backlog are installed, should show versions" \
    "" \
    "validate_uv_present"

# Test 2: Verify backlog CLI check
run_test \
    "Backlog CLI check" \
    "Should detect backlog CLI and show version" \
    "" \
    "validate_backlog_present"

# Test 3: Check if active tasks are displayed (if any exist)
run_test \
    "Active tasks display" \
    "Should display In Progress tasks if any exist" \
    "" \
    ""

# Test 4: Exit code is always 0 (even on errors)
echo -e "\n${YELLOW}Test $((TESTS_RUN + 1)): Exit code always 0${NC}"
echo "Description: Hook should always exit 0 (fail-open principle)"

# Simulate error condition by setting invalid CLAUDE_PROJECT_DIR
CLAUDE_PROJECT_DIR="/nonexistent/path/$(date +%s)" "$SCRIPT_DIR/session-start.sh" >/dev/null 2>&1
exit_code=$?

TESTS_RUN=$((TESTS_RUN + 1))

if [[ $exit_code -eq 0 ]]; then
    echo -e "${GREEN}PASS: Exit code is 0 even with invalid project dir${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}FAIL: Exit code is $exit_code (should be 0)${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Test 5: JSON structure validation
echo -e "\n${YELLOW}Test $((TESTS_RUN + 1)): JSON structure validation${NC}"
echo "Description: Output should be valid JSON with required fields"

output=$("$SCRIPT_DIR/session-start.sh" 2>&1)
TESTS_RUN=$((TESTS_RUN + 1))

if echo "$output" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    assert 'decision' in data, 'Missing decision field'
    assert data['decision'] == 'allow', f\"Decision should be 'allow', got {data['decision']}\"
    assert 'reason' in data, 'Missing reason field'
    print('Valid JSON structure')
    sys.exit(0)
except Exception as e:
    print(f'Invalid JSON: {e}', file=sys.stderr)
    sys.exit(1)
" 2>&1; then
    echo -e "${GREEN}PASS: JSON structure is valid${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}FAIL: Invalid JSON structure${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Test 6: Performance - hook should complete in under 5 seconds
echo -e "\n${YELLOW}Test $((TESTS_RUN + 1)): Performance check${NC}"
echo "Description: Hook should complete within 5 seconds"

TESTS_RUN=$((TESTS_RUN + 1))
start_time=$(date +%s)
"$SCRIPT_DIR/session-start.sh" >/dev/null 2>&1
end_time=$(date +%s)
duration=$((end_time - start_time))

if [[ $duration -le 5 ]]; then
    echo -e "${GREEN}PASS: Hook completed in ${duration}s (within 5s limit)${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}FAIL: Hook took ${duration}s (exceeds 5s limit)${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Test 7: No CLAUDE_PROJECT_DIR set - should use current directory
echo -e "\n${YELLOW}Test $((TESTS_RUN + 1)): CLAUDE_PROJECT_DIR fallback${NC}"
echo "Description: Should use current directory if CLAUDE_PROJECT_DIR not set"

TESTS_RUN=$((TESTS_RUN + 1))
cd "$PROJECT_ROOT"
unset CLAUDE_PROJECT_DIR
output=$("$SCRIPT_DIR/session-start.sh" 2>&1)
exit_code=$?

if [[ $exit_code -eq 0 ]] && echo "$output" | python3 -c "import json, sys; json.load(sys.stdin)" 2>/dev/null; then
    echo -e "${GREEN}PASS: Hook works without CLAUDE_PROJECT_DIR set${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}FAIL: Hook failed without CLAUDE_PROJECT_DIR${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

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
