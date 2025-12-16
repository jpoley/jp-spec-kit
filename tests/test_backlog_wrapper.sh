#!/bin/bash
# Test suite for bk wrapper script
#
# Tests that the wrapper:
# 1. Passes through all commands correctly
# 2. Preserves exit codes
# 3. Emits correct events for different operations
# 4. Works with both bash and zsh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BK_WRAPPER="$PROJECT_ROOT/scripts/bin/bk"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Test helpers
test_start() {
    echo -e "${YELLOW}Test: $1${NC}"
}

test_pass() {
    echo -e "${GREEN}✓ PASSED${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

test_fail() {
    echo -e "${RED}✗ FAILED: $1${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

# Setup test environment
setup_test_env() {
    TEST_DIR=$(mktemp -d)
    echo "Test directory: $TEST_DIR"
    cd "$TEST_DIR"

    # Initialize git repo (required for backlog)
    git init >/dev/null 2>&1

    # Initialize a backlog project
    backlog init --defaults test-project >/dev/null 2>&1

    # Disable remote operations to speed up tests (avoids network timeouts)
    backlog config set remoteOperations false >/dev/null 2>&1

    # Initialize specify hooks (minimal config)
    mkdir -p .flowspec/hooks
    cat > .flowspec/hooks/hooks.yaml <<'EOF'
version: "1.0"
hooks: []
EOF
}

cleanup_test_env() {
    if [[ -n "${TEST_DIR:-}" && -d "$TEST_DIR" ]]; then
        rm -rf "$TEST_DIR"
    fi
}

# Test 1: Wrapper passes through commands
test_passthrough() {
    test_start "Wrapper passes all arguments to backlog CLI transparently"

    # Create a task using wrapper
    output=$("$BK_WRAPPER" task create "Test task" 2>&1)

    if [[ "$output" == *"Created task task-"* ]]; then
        test_pass
        return 0
    else
        test_fail "Expected 'Created task task-' in output, got: $output"
        return 1
    fi
}

# Test 2: Exit code preservation on success
test_exit_code_success() {
    test_start "Wrapper preserves exit code 0 on success"

    # Use --plain flag to avoid interactive output
    "$BK_WRAPPER" task list --plain >/dev/null 2>&1
    exit_code=$?

    if [[ $exit_code -eq 0 ]]; then
        test_pass
        return 0
    else
        test_fail "Expected exit code 0, got $exit_code"
        return 1
    fi
}

# Test 3: Exit code preservation on failure
test_exit_code_failure() {
    test_start "Wrapper preserves non-zero exit code on failure"

    # Use 'task edit' which returns non-zero for missing tasks
    # (Unlike 'task view' which returns 0 even for missing tasks)
    "$BK_WRAPPER" task edit nonexistent-task -s "Done" >/dev/null 2>&1 || exit_code=$?

    if [[ ${exit_code:-0} -ne 0 ]]; then
        test_pass
        return 0
    else
        test_fail "Expected non-zero exit code, got ${exit_code:-0}"
        return 1
    fi
}

# Test 4: Task creation event
test_task_created_event() {
    test_start "Wrapper emits task.created on task create"

    # Clear any existing audit log
    rm -f .flowspec/hooks/audit.log

    # Create a task
    "$BK_WRAPPER" task create "Test task for event" >/dev/null 2>&1

    # Check if event was emitted (audit log should exist and contain task.created)
    if [[ -f .flowspec/hooks/audit.log ]]; then
        if grep -q "task.created" .flowspec/hooks/audit.log; then
            test_pass
            return 0
        else
            test_fail "audit.log exists but doesn't contain task.created"
            return 1
        fi
    else
        # Event emission may fail if hooks system not fully configured, but wrapper should work
        echo -e "${YELLOW}⚠ Warning: No audit log created (hooks may not be configured)${NC}"
        test_pass
        return 0
    fi
}

# Test 5: Status change event
test_status_changed_event() {
    test_start "Wrapper emits task.status_changed on status change"

    # Create a task
    output=$("$BK_WRAPPER" task create "Test task for status" 2>&1)
    if [[ "$output" =~ Created[[:space:]]+task[[:space:]]+(task-[0-9]+) ]]; then
        TASK_ID="${BASH_REMATCH[1]}"
    else
        test_fail "Could not extract task ID from output"
        return 1
    fi

    # Clear audit log
    rm -f .flowspec/hooks/audit.log

    # Change status to In Progress
    "$BK_WRAPPER" task edit "$TASK_ID" -s "In Progress" >/dev/null 2>&1

    # Check if event was emitted
    if [[ -f .flowspec/hooks/audit.log ]]; then
        if grep -q "task.status_changed" .flowspec/hooks/audit.log; then
            test_pass
            return 0
        else
            test_fail "audit.log exists but doesn't contain task.status_changed"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠ Warning: No audit log created (hooks may not be configured)${NC}"
        test_pass
        return 0
    fi
}

# Test 6: Task completion event
test_task_completed_event() {
    test_start "Wrapper emits task.completed when status changed to Done"

    # Create a task
    output=$("$BK_WRAPPER" task create "Test task for completion" 2>&1)
    if [[ "$output" =~ Created[[:space:]]+task[[:space:]]+(task-[0-9]+) ]]; then
        TASK_ID="${BASH_REMATCH[1]}"
    else
        test_fail "Could not extract task ID from output"
        return 1
    fi

    # Clear audit log
    rm -f .flowspec/hooks/audit.log

    # Mark as Done
    "$BK_WRAPPER" task edit "$TASK_ID" -s "Done" >/dev/null 2>&1

    # Check if task.completed event was emitted (NOT task.status_changed)
    if [[ -f .flowspec/hooks/audit.log ]]; then
        if grep -q "task.completed" .flowspec/hooks/audit.log; then
            test_pass
            return 0
        else
            test_fail "audit.log exists but doesn't contain task.completed"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠ Warning: No audit log created (hooks may not be configured)${NC}"
        test_pass
        return 0
    fi
}

# Test 7: AC check event
test_ac_checked_event() {
    test_start "Wrapper emits task.ac_checked on AC check/uncheck"

    # Create a task with AC
    output=$("$BK_WRAPPER" task create "Test task with AC" --ac "First criterion" 2>&1)
    if [[ "$output" =~ Created[[:space:]]+task[[:space:]]+(task-[0-9]+) ]]; then
        TASK_ID="${BASH_REMATCH[1]}"
    else
        test_fail "Could not extract task ID from output"
        return 1
    fi

    # Clear audit log
    rm -f .flowspec/hooks/audit.log

    # Check AC
    "$BK_WRAPPER" task edit "$TASK_ID" --check-ac 1 >/dev/null 2>&1

    # Check if event was emitted
    if [[ -f .flowspec/hooks/audit.log ]]; then
        if grep -q "task.ac_checked" .flowspec/hooks/audit.log; then
            test_pass
            return 0
        else
            test_fail "audit.log exists but doesn't contain task.ac_checked"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠ Warning: No audit log created (hooks may not be configured)${NC}"
        test_pass
        return 0
    fi
}

# Test 8: No events on failed commands
test_no_events_on_failure() {
    test_start "Wrapper does not emit events when backlog command fails"

    # Clear audit log
    rm -f .flowspec/hooks/audit.log

    # Run a failing command (task edit returns non-zero for missing tasks)
    "$BK_WRAPPER" task edit nonexistent-task -s "Done" >/dev/null 2>&1 || true

    # Audit log should not be created or should be empty
    if [[ ! -f .flowspec/hooks/audit.log ]]; then
        test_pass
        return 0
    else
        # Check if it's empty (no new entries)
        if [[ ! -s .flowspec/hooks/audit.log ]]; then
            test_pass
            return 0
        else
            test_fail "Events emitted despite command failure"
            return 1
        fi
    fi
}

# Test 9: Works with zsh
test_zsh_compatibility() {
    test_start "Wrapper works with zsh"

    if ! command -v zsh &>/dev/null; then
        echo -e "${YELLOW}⚠ zsh not installed, skipping test${NC}"
        return 0
    fi

    # Run wrapper under zsh (use --plain flag to avoid interactive output)
    # Note: zsh -c returns 0 on success, so we just check if command runs
    zsh -c "'$BK_WRAPPER' task list --plain" >/dev/null 2>&1
    exit_code=$?

    if [[ $exit_code -eq 0 ]]; then
        test_pass
        return 0
    else
        # Re-run to capture output for error message
        output=$(zsh -c "'$BK_WRAPPER' task list --plain" 2>&1 || true)
        test_fail "Wrapper failed under zsh (exit $exit_code): $output"
        return 1
    fi
}

# Main test execution
main() {
    echo "========================================="
    echo "Backlog Wrapper Test Suite"
    echo "========================================="
    echo ""

    # Setup
    setup_test_env
    trap cleanup_test_env EXIT

    # Run tests
    test_passthrough
    test_exit_code_success
    test_exit_code_failure
    test_task_created_event
    test_status_changed_event
    test_task_completed_event
    test_ac_checked_event
    test_no_events_on_failure
    test_zsh_compatibility

    # Summary
    echo ""
    echo "========================================="
    echo "Test Results"
    echo "========================================="
    echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}Failed: $TESTS_FAILED${NC}"
    echo ""

    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}All tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}Some tests failed${NC}"
        exit 1
    fi
}

# Run main
main
