#!/usr/bin/env bash
# Integration test for post-commit-backlog-events.sh
#
# This test creates a temporary git repository with backlog task files
# and verifies the hook correctly detects changes and emits events.
#
# Usage: ./tests/integration/test_post_commit_backlog_events.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HOOK_SCRIPT="$PROJECT_ROOT/scripts/hooks/post-commit-backlog-events.sh"

# Test tracking
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Colors
if [ -t 1 ]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[0;33m'
    NC='\033[0m'
else
    GREEN='' RED='' YELLOW='' NC=''
fi

log_test() { echo -e "${YELLOW}TEST:${NC} $*"; }
log_pass() { echo -e "${GREEN}PASS:${NC} $*"; ((TESTS_PASSED++)); }
log_fail() { echo -e "${RED}FAIL:${NC} $*"; ((TESTS_FAILED++)); }

# Setup temporary test directory
TEST_DIR=""
ORIG_DIR="$(pwd)"

setup_test_repo() {
    TEST_DIR=$(mktemp -d)
    cd "$TEST_DIR"

    git init --quiet
    git config user.email "test@example.com"
    git config user.name "Test User"

    mkdir -p backlog/tasks

    # Create initial commit
    echo "# Test Project" > README.md
    git add README.md
    git commit --quiet -m "Initial commit"

    # Copy hook script
    mkdir -p scripts/hooks
    cp "$HOOK_SCRIPT" scripts/hooks/
    chmod +x scripts/hooks/post-commit-backlog-events.sh
}

cleanup_test_repo() {
    cd "$ORIG_DIR"
    if [[ -n "$TEST_DIR" && -d "$TEST_DIR" ]]; then
        rm -rf "$TEST_DIR"
    fi
    TEST_DIR=""
}

# Ensure cleanup on exit
trap cleanup_test_repo EXIT

# Create a task file
create_task_file() {
    local task_id="$1"
    local status="${2:-To Do}"
    local checked_count="${3:-0}"

    local filename="backlog/tasks/${task_id} - Test-Task.md"

    cat > "$filename" << EOF
---
id: ${task_id}
title: Test Task
status: ${status}
assignee:
  - '@test'
created_date: '2025-01-01 00:00'
updated_date: '2025-01-01 00:00'
labels:
  - test
dependencies: []
priority: medium
---

## Description

Test task description

## Acceptance Criteria
<!-- AC:BEGIN -->
EOF

    # Add acceptance criteria (5 total, checked_count are checked)
    for i in 1 2 3 4 5; do
        if [[ $i -le $checked_count ]]; then
            echo "- [x] #$i AC $i" >> "$filename"
        else
            echo "- [ ] #$i AC $i" >> "$filename"
        fi
    done

    echo "<!-- AC:END -->" >> "$filename"

    echo "$filename"
}

# Test 1: Detect new task file
test_new_task_detection() {
    log_test "New task detection"
    ((TESTS_RUN++))

    setup_test_repo

    # Create a new task file
    create_task_file "task-001"
    git add backlog/tasks/
    git commit --quiet -m "Add task-001"

    # Run hook and capture output
    output=$(DRY_RUN=true ./scripts/hooks/post-commit-backlog-events.sh 2>&1 || true)

    if echo "$output" | grep -q "task.created"; then
        log_pass "New task detection"
    else
        log_fail "New task detection - expected task.created event"
        echo "  Output: $output"
    fi

    cleanup_test_repo
}

# Test 2: Detect status change
test_status_change_detection() {
    log_test "Status change detection"
    ((TESTS_RUN++))

    setup_test_repo

    # Create task with "To Do" status
    create_task_file "task-002" "To Do"
    git add backlog/tasks/
    git commit --quiet -m "Add task-002"

    # Change status to "In Progress"
    create_task_file "task-002" "In Progress"
    git add backlog/tasks/
    git commit --quiet -m "Update task-002 status"

    # Run hook
    output=$(DRY_RUN=true ./scripts/hooks/post-commit-backlog-events.sh 2>&1 || true)

    if echo "$output" | grep -q "task.status_changed"; then
        log_pass "Status change detection"
    else
        log_fail "Status change detection - expected task.status_changed event"
        echo "  Output: $output"
    fi

    cleanup_test_repo
}

# Test 3: Detect task completion
test_task_completion_detection() {
    log_test "Task completion detection"
    ((TESTS_RUN++))

    setup_test_repo

    # Create task with "In Progress" status
    create_task_file "task-003" "In Progress"
    git add backlog/tasks/
    git commit --quiet -m "Add task-003"

    # Change status to "Done"
    create_task_file "task-003" "Done"
    git add backlog/tasks/
    git commit --quiet -m "Complete task-003"

    # Run hook
    output=$(DRY_RUN=true ./scripts/hooks/post-commit-backlog-events.sh 2>&1 || true)

    if echo "$output" | grep -q "task.completed"; then
        log_pass "Task completion detection"
    else
        log_fail "Task completion detection - expected task.completed event"
        echo "  Output: $output"
    fi

    cleanup_test_repo
}

# Test 4: Detect AC checkbox changes
test_ac_change_detection() {
    log_test "AC checkbox change detection"
    ((TESTS_RUN++))

    setup_test_repo

    # Create task with 0 checked
    create_task_file "task-004" "In Progress" 0
    git add backlog/tasks/
    git commit --quiet -m "Add task-004"

    # Check 3 ACs
    create_task_file "task-004" "In Progress" 3
    git add backlog/tasks/
    git commit --quiet -m "Check ACs for task-004"

    # Run hook
    output=$(DRY_RUN=true ./scripts/hooks/post-commit-backlog-events.sh 2>&1 || true)

    if echo "$output" | grep -q "task.ac_checked"; then
        log_pass "AC checkbox change detection"
    else
        log_fail "AC checkbox change detection - expected task.ac_checked event"
        echo "  Output: $output"
    fi

    cleanup_test_repo
}

# Test 5: Idempotent (no changes)
test_idempotent_no_changes() {
    log_test "Idempotent (no task changes)"
    ((TESTS_RUN++))

    setup_test_repo

    # Create task
    create_task_file "task-005"
    git add backlog/tasks/
    git commit --quiet -m "Add task-005"

    # Make a commit that doesn't change tasks
    echo "# Updated" >> README.md
    git add README.md
    git commit --quiet -m "Update README"

    # Run hook
    output=$(DRY_RUN=true VERBOSE=true ./scripts/hooks/post-commit-backlog-events.sh 2>&1 || true)

    if echo "$output" | grep -q "No backlog task changes"; then
        log_pass "Idempotent (no task changes)"
    else
        log_fail "Idempotent - expected no events for non-task changes"
        echo "  Output: $output"
    fi

    cleanup_test_repo
}

# Test 6: Parse task ID correctly
test_task_id_parsing() {
    log_test "Task ID parsing"
    ((TESTS_RUN++))

    setup_test_repo

    # Create task with decimal ID (task-N.M format)
    create_task_file "task-204.01"
    git add backlog/tasks/
    git commit --quiet -m "Add task-204.01"

    # Run hook
    output=$(DRY_RUN=true ./scripts/hooks/post-commit-backlog-events.sh 2>&1 || true)

    # Verify:
    # 1. task.created event is emitted
    # 2. Task ID is correctly parsed as "task-204.01" (not truncated)
    if echo "$output" | grep -q "task.created" && echo "$output" | grep -q "task-204.01"; then
        log_pass "Task ID parsing"
    else
        log_fail "Task ID parsing - expected task.created event with task-204.01"
        echo "  Output: $output"
    fi

    cleanup_test_repo
}

# Test 7: Reject malformed task files (multiple consecutive dots)
test_reject_malformed_task_file() {
    log_test "Reject malformed task file"
    ((TESTS_RUN++))

    setup_test_repo

    # Create a file with malformed ID (task-1..2 - multiple consecutive dots)
    # The stricter regex should reject files that don't match the expected format
    mkdir -p backlog/tasks
    printf '%s\n' "---" "id: task-1..2" "status: To Do" "---" "Test" > "backlog/tasks/task-1..2 - Bad-Task.md"
    git add backlog/tasks/
    git commit --quiet -m "Add malformed task"

    # Run hook with verbose to see debug output
    output=$(DRY_RUN=true VERBOSE=true ./scripts/hooks/post-commit-backlog-events.sh 2>&1 || true)

    # Should skip the malformed file (doesn't match task-N or task-N.M format)
    if echo "$output" | grep -q "Skipping non-task file"; then
        log_pass "Reject malformed task file"
    else
        log_fail "Reject malformed task file - should skip files with invalid IDs"
        echo "  Output: $output"
    fi

    cleanup_test_repo
}

# Run all tests
main() {
    echo "==========================================="
    echo "Post-commit Backlog Events Hook Test Suite"
    echo "==========================================="
    echo ""

    # Check hook script exists
    if [[ ! -f "$HOOK_SCRIPT" ]]; then
        echo "ERROR: Hook script not found at $HOOK_SCRIPT"
        exit 1
    fi

    # Run tests
    test_new_task_detection
    test_status_change_detection
    test_task_completion_detection
    test_ac_change_detection
    test_idempotent_no_changes
    test_task_id_parsing
    test_reject_malformed_task_file

    echo ""
    echo "==========================================="
    echo "Results: $TESTS_PASSED/$TESTS_RUN passed, $TESTS_FAILED failed"
    echo "==========================================="

    if [[ $TESTS_FAILED -gt 0 ]]; then
        exit 1
    fi
}

main "$@"
