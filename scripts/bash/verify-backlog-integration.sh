#!/bin/bash
# Backlog.md Integration Verification Script
# Verifies complete setup of Backlog.md with jp-spec-kit

set -e

echo "=========================================="
echo "Backlog.md Integration Verification"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Success/failure counters
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
test_check() {
    local test_name="$1"
    local command="$2"

    echo -n "Testing: $test_name ... "

    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Test with output capture
test_check_output() {
    local test_name="$1"
    local command="$2"
    local expected="$3"

    echo -n "Testing: $test_name ... "

    output=$(eval "$command" 2>&1)

    if [[ "$output" == *"$expected"* ]]; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        echo "  Expected: $expected"
        echo "  Got: $output"
        ((TESTS_FAILED++))
        return 1
    fi
}

echo "=== 1. Prerequisites Check ==="
test_check "Backlog.md installed" "which backlog"
test_check "Node.js installed" "which node"
test_check "npm installed" "which npm"
test_check "jq installed" "which jq"
echo ""

echo "=== 2. Backlog.md Configuration ==="
test_check "backlog/ directory exists" "[ -d backlog ]"
test_check "config.yml exists" "[ -f backlog/config.yml ]"
test_check "tasks/ directory exists" "[ -d backlog/tasks ]"
test_check_output "Project name is jp-spec-kit" "grep 'project_name' backlog/config.yml" "jp-spec-kit"
echo ""

echo "=== 3. MCP Configuration ==="
test_check ".mcp.json exists" "[ -f .mcp.json ]"
test_check_output "Backlog MCP server configured" "jq -r '.mcpServers.backlog.command' .mcp.json" "backlog"
test_check_output "MCP command is 'mcp start'" "jq -r '.mcpServers.backlog.args[0]' .mcp.json" "mcp"
echo ""

echo "=== 4. Backlog.md CLI Functionality ==="
test_check "backlog --version works" "backlog --version"
test_check "backlog overview works" "backlog overview --plain"
test_check "backlog search works" "backlog search 'test'"
echo ""

echo "=== 5. Task Management ==="
test_check "Tasks exist in backlog" "[ -n \"\$(ls -A backlog/tasks/)\" ]"
test_check_output "Can read task-1" "cat 'backlog/tasks/task-1 - Integrate-Backlog.md-with-jp-spec-kit.md'" "Integrate Backlog.md"
echo ""

echo "=== 6. Git Integration ==="
test_check "backlog/ is tracked by git" "git ls-files backlog/ | grep -q config.yml"
test_check ".mcp.json is tracked by git" "git ls-files .mcp.json"
echo ""

echo "=== 7. jp-spec-kit Integration Points ==="
test_check "templates/ directory exists" "[ -d templates ]"
test_check "tasks-template.md exists" "[ -f templates/tasks-template.md ]"
test_check ".claude/commands/jpspec/ exists" "[ -d .claude/commands/jpspec ]"
echo ""

echo "=========================================="
echo "Test Results Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed! Backlog.md integration is fully configured.${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Please review the output above.${NC}"
    exit 1
fi
