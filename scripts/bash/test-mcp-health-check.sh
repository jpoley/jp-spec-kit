#!/usr/bin/env bash

# Test suite for check-mcp-servers.sh
#
# This script validates the MCP health check script functionality
# across various scenarios including valid config, missing config,
# invalid JSON, and server failures.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCP_SCRIPT="$SCRIPT_DIR/check-mcp-servers.sh"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Temporary directory for test fixtures
TEST_DIR=$(mktemp -d)
trap 'rm -rf "$TEST_DIR"' EXIT

log_test() {
    echo -e "\n${YELLOW}TEST: $1${NC}"
    ((TESTS_RUN++))
}

log_pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    ((TESTS_PASSED++))
}

log_fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    ((TESTS_FAILED++))
}

# Test 1: Valid .mcp.json with single server
test_valid_config_single_server() {
    log_test "Valid config with single server"

    cat > "$TEST_DIR/.mcp.json" << 'EOF'
{
  "mcpServers": {
    "test-sleep": {
      "command": "sleep",
      "args": ["10"],
      "description": "Test sleep server"
    }
  }
}
EOF

    cd "$TEST_DIR"
    if "$MCP_SCRIPT" --timeout 5 >/dev/null 2>&1; then
        log_pass "Script executed successfully with valid config"
    else
        log_fail "Script failed with valid config (exit code: $?)"
    fi
}

# Test 2: Missing .mcp.json
test_missing_config() {
    log_test "Missing .mcp.json file"

    cd "$TEST_DIR"
    rm -f .mcp.json

    if "$MCP_SCRIPT" 2>&1 | grep -q "not found"; then
        log_pass "Script detected missing config file"
    else
        log_fail "Script didn't detect missing config file"
    fi
}

# Test 3: Invalid JSON syntax
test_invalid_json() {
    log_test "Invalid JSON syntax"

    cat > "$TEST_DIR/.mcp.json" << 'EOF'
{
  "mcpServers": {
    "test": "missing-closing-brace"
EOF

    cd "$TEST_DIR"
    if "$MCP_SCRIPT" 2>&1 | grep -q "Invalid JSON"; then
        log_pass "Script detected invalid JSON"
    else
        log_fail "Script didn't detect invalid JSON"
    fi
}

# Test 4: Missing mcpServers key
test_missing_mcpservers_key() {
    log_test "Missing mcpServers key"

    cat > "$TEST_DIR/.mcp.json" << 'EOF'
{
  "someOtherKey": {}
}
EOF

    cd "$TEST_DIR"
    if "$MCP_SCRIPT" 2>&1 | grep -q "Missing 'mcpServers'"; then
        log_pass "Script detected missing mcpServers key"
    else
        log_fail "Script didn't detect missing mcpServers key"
    fi
}

# Test 5: Empty mcpServers
test_empty_mcpservers() {
    log_test "Empty mcpServers configuration"

    cat > "$TEST_DIR/.mcp.json" << 'EOF'
{
  "mcpServers": {}
}
EOF

    cd "$TEST_DIR"
    if "$MCP_SCRIPT" 2>&1 | grep -q "No MCP servers configured"; then
        log_pass "Script detected empty mcpServers"
    else
        log_fail "Script didn't detect empty mcpServers"
    fi
}

# Test 6: Non-existent binary
test_nonexistent_binary() {
    log_test "Server with non-existent binary"

    cat > "$TEST_DIR/.mcp.json" << 'EOF'
{
  "mcpServers": {
    "fake-server": {
      "command": "this-command-does-not-exist-12345",
      "args": [],
      "description": "Fake server"
    }
  }
}
EOF

    cd "$TEST_DIR"
    if "$MCP_SCRIPT" 2>&1 | grep -q "not found"; then
        log_pass "Script detected non-existent binary"
    else
        log_fail "Script didn't detect non-existent binary"
    fi
}

# Test 7: JSON output format
test_json_output() {
    log_test "JSON output format"

    cat > "$TEST_DIR/.mcp.json" << 'EOF'
{
  "mcpServers": {
    "test-sleep": {
      "command": "sleep",
      "args": ["10"],
      "description": "Test server"
    }
  }
}
EOF

    cd "$TEST_DIR"
    local output
    output=$("$MCP_SCRIPT" --json --timeout 3 2>/dev/null)

    if echo "$output" | jq -e '.servers' >/dev/null 2>&1 && \
       echo "$output" | jq -e '.summary' >/dev/null 2>&1 && \
       echo "$output" | jq -e '.status' >/dev/null 2>&1; then
        log_pass "JSON output has correct structure"
    else
        log_fail "JSON output missing required fields"
    fi
}

# Test 8: Help message
test_help_message() {
    log_test "Help message display"

    if "$MCP_SCRIPT" --help | grep -q "Usage:"; then
        log_pass "Help message displayed correctly"
    else
        log_fail "Help message not displayed"
    fi
}

# Test 9: Custom config path
test_custom_config_path() {
    log_test "Custom config path"

    cat > "$TEST_DIR/custom.json" << 'EOF'
{
  "mcpServers": {
    "test": {
      "command": "sleep",
      "args": ["10"],
      "description": "Test"
    }
  }
}
EOF

    cd "$TEST_DIR"
    if "$MCP_SCRIPT" --config "$TEST_DIR/custom.json" --timeout 3 >/dev/null 2>&1; then
        log_pass "Custom config path accepted"
    else
        log_fail "Custom config path not working"
    fi
}

# Test 10: Multiple servers
test_multiple_servers() {
    log_test "Multiple servers in config"

    cat > "$TEST_DIR/.mcp.json" << 'EOF'
{
  "mcpServers": {
    "server1": {
      "command": "sleep",
      "args": ["10"],
      "description": "Server 1"
    },
    "server2": {
      "command": "sleep",
      "args": ["10"],
      "description": "Server 2"
    },
    "server3": {
      "command": "sleep",
      "args": ["10"],
      "description": "Server 3"
    }
  }
}
EOF

    cd "$TEST_DIR"
    local output
    output=$("$MCP_SCRIPT" --json --timeout 3 2>/dev/null)
    local count
    count=$(echo "$output" | jq '.summary.total')

    if [[ "$count" -eq 3 ]]; then
        log_pass "All 3 servers detected and tested"
    else
        log_fail "Expected 3 servers, got $count"
    fi
}

# Main execution
main() {
    echo "MCP Health Check Script Test Suite"
    echo "===================================="

    # Check prerequisites
    if ! command -v jq >/dev/null 2>&1; then
        echo "ERROR: jq is required for tests"
        exit 1
    fi

    if [[ ! -f "$MCP_SCRIPT" ]]; then
        echo "ERROR: check-mcp-servers.sh not found at $MCP_SCRIPT"
        exit 1
    fi

    if [[ ! -x "$MCP_SCRIPT" ]]; then
        echo "ERROR: check-mcp-servers.sh is not executable"
        echo "Run: chmod +x $MCP_SCRIPT"
        exit 1
    fi

    # Run all tests
    test_valid_config_single_server
    test_missing_config
    test_invalid_json
    test_missing_mcpservers_key
    test_empty_mcpservers
    test_nonexistent_binary
    test_json_output
    test_help_message
    test_custom_config_path
    test_multiple_servers

    # Summary
    echo ""
    echo "===================================="
    echo "Test Results:"
    echo "  Total:  $TESTS_RUN"
    echo -e "  Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "  Failed: ${RED}$TESTS_FAILED${NC}"
    echo ""

    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}All tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}Some tests failed${NC}"
        exit 1
    fi
}

main
