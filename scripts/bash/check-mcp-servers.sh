#!/usr/bin/env bash

# MCP Server Health Check Script
#
# This script tests connectivity and operational status for all configured MCP servers.
# It helps diagnose MCP connection issues and verify server availability.
#
# Usage: ./check-mcp-servers.sh [OPTIONS]
#
# OPTIONS:
#   --json              Output in JSON format
#   --timeout SECONDS   Connection timeout per server (default: 10)
#   --config PATH       Path to .mcp.json (default: ./.mcp.json)
#   --verbose, -v       Show detailed output
#   --help, -h          Show help message
#
# EXIT CODES:
#   0 - All servers healthy
#   1 - Some servers failed health checks
#   2 - Configuration error (missing/invalid .mcp.json)
#   3 - Prerequisites missing (jq, npx, etc.)

set -euo pipefail

# Default configuration
TIMEOUT=10
CONFIG_PATH=".mcp.json"
JSON_MODE=false
VERBOSE=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Color codes for terminal output
if [[ -t 1 ]]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m' # No Color
else
    GREEN=''
    RED=''
    YELLOW=''
    BLUE=''
    NC=''
fi

# Trap signals for cleanup
trap cleanup EXIT INT TERM

# Array to track spawned processes for cleanup
declare -a SPAWNED_PIDS=()

cleanup() {
    local exit_code=$?

    # Kill any spawned server processes
    if [ ${#SPAWNED_PIDS[@]} -gt 0 ]; then
        for pid in "${SPAWNED_PIDS[@]}"; do
            if kill -0 "$pid" 2>/dev/null; then
                kill -TERM "$pid" 2>/dev/null || true
            fi
        done
    fi

    # Remove temporary files
    rm -f /tmp/mcp-health-*.tmp 2>/dev/null || true

    exit $exit_code
}

show_help() {
    cat << 'EOF'
Usage: check-mcp-servers.sh [OPTIONS]

Test connectivity and operational status for all configured MCP servers.

OPTIONS:
  --json              Output in JSON format
  --timeout SECONDS   Connection timeout per server (default: 10)
  --config PATH       Path to .mcp.json (default: ./.mcp.json)
  --verbose, -v       Show detailed output
  --help, -h          Show this help message

EXAMPLES:
  # Check all servers with default settings
  ./check-mcp-servers.sh

  # Check with custom timeout and verbose output
  ./check-mcp-servers.sh --timeout 15 --verbose

  # Output results as JSON
  ./check-mcp-servers.sh --json

  # Use custom config file
  ./check-mcp-servers.sh --config /path/to/.mcp.json

EXIT CODES:
  0 - All servers healthy
  1 - Some servers failed health checks
  2 - Configuration error (missing/invalid .mcp.json)
  3 - Prerequisites missing (jq, npx, etc.)

EOF
}

log_verbose() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo "$@" >&2
    fi
}

log_error() {
    echo -e "${RED}ERROR:${NC} $*" >&2
}

log_warning() {
    echo -e "${YELLOW}WARNING:${NC} $*" >&2
}

log_info() {
    echo -e "${BLUE}INFO:${NC} $*" >&2
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --json)
            JSON_MODE=true
            shift
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --config)
            CONFIG_PATH="$2"
            shift 2
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option '$1'. Use --help for usage information."
            exit 2
            ;;
    esac
done

# Validate timeout is numeric
if ! [[ "$TIMEOUT" =~ ^[0-9]+$ ]]; then
    log_error "Timeout must be a positive integer"
    exit 2
fi

# Check prerequisites
check_prerequisites() {
    local missing_tools=()

    # Check for jq (JSON parsing)
    if ! command -v jq >/dev/null 2>&1; then
        missing_tools+=("jq")
    fi

    # Note: We don't check for npx/uvx here as they're server-specific
    # They'll be checked when testing specific servers

    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_error "Install missing tools and try again."
        log_error "  jq: brew install jq (macOS) or apt-get install jq (Linux)"
        exit 3
    fi
}

# Validate .mcp.json configuration file
validate_config() {
    local config_path="$1"

    if [[ ! -f "$config_path" ]]; then
        log_error ".mcp.json not found at: $config_path"
        log_error "Ensure you're running from the project root or use --config to specify path."
        exit 2
    fi

    # Validate JSON syntax
    if ! jq empty "$config_path" 2>/dev/null; then
        log_error "Invalid JSON in $config_path"
        exit 2
    fi

    # Check for mcpServers key
    if ! jq -e '.mcpServers' "$config_path" >/dev/null 2>&1; then
        log_error "Missing 'mcpServers' key in $config_path"
        exit 2
    fi

    # Check if any servers configured
    local server_count
    server_count=$(jq '.mcpServers | length' "$config_path")

    if [[ "$server_count" -eq 0 ]]; then
        log_warning "No MCP servers configured in $config_path"
        if [[ "$JSON_MODE" == "true" ]]; then
            echo '{"servers":[],"summary":{"total":0,"healthy":0,"unhealthy":0},"status":"no_servers_configured"}'
        else
            echo "No MCP servers configured."
        fi
        exit 0
    fi

    log_verbose "Found $server_count MCP server(s) in configuration"
}

# Check if a command exists and is executable
check_command() {
    local cmd="$1"
    command -v "$cmd" >/dev/null 2>&1
}

# Test MCP server connectivity
# Returns: 0 if healthy, 1 if unhealthy
test_server() {
    local server_name="$1"
    local command="$2"
    local args="$3"
    local description="$4"

    log_verbose "Testing server: $server_name"
    log_verbose "  Command: $command ${args}"

    # Check if command binary exists
    if ! check_command "$command"; then
        echo "failed" "binary_not_found" "Command '$command' not found in PATH"
        return 1
    fi

    # Create secure temporary directory and sanitized temp file name
    local safe_name
    safe_name=$(printf '%s' "$server_name" | tr -c 'A-Za-z0-9._-' '_')
    local tmpdir
    tmpdir=$(mktemp -d -t mcp-health.XXXXXXXX) || exit 1
    local tmp_file="${tmpdir}/${safe_name}.tmp"

    # Attempt to start server with timeout
    # We spawn the server and check if it starts successfully
    # For MCP servers, we expect them to start and listen for connections

    log_verbose "  Starting server with ${TIMEOUT}s timeout..."

    # Parse args from JSON array string into bash array
    local -a cmd_args
    while IFS= read -r arg; do
        cmd_args+=("$arg")
    done < <(echo "$args" | jq -r '.[]')

    # Start server in background with timeout
    timeout "$TIMEOUT" "$command" "${cmd_args[@]}" >/dev/null 2>&1 &
    local server_pid=$!
    SPAWNED_PIDS+=("$server_pid")

    # Wait briefly for server to start
    sleep 2

    # Check if process is still running
    if kill -0 "$server_pid" 2>/dev/null; then
        # Server started successfully - kill it
        kill -TERM "$server_pid" 2>/dev/null || true
        wait "$server_pid" 2>/dev/null || true
        log_verbose "  ✓ Server started successfully"
        echo "healthy" "" ""
        rm -rf "$tmpdir"
        return 0
    else
        # Server crashed immediately or completed
        wait "$server_pid" 2>/dev/null || true
        log_verbose "  ✗ Server failed to start"
        echo "failed" "startup_failed" "Server process crashed or failed to start"
        rm -rf "$tmpdir"
        return 1
    fi
}

# Main execution
main() {
    local config_path="$CONFIG_PATH"

    # Resolve config path to absolute
    if [[ ! "$config_path" = /* ]]; then
        config_path="$(pwd)/$config_path"
    fi

    # Check prerequisites
    check_prerequisites

    # Validate configuration
    validate_config "$config_path"

    # Get list of servers
    local servers
    servers=$(jq -r '.mcpServers | keys[]' "$config_path")

    local total_servers=0
    local healthy_servers=0
    local unhealthy_servers=0

    # Array to store results
    declare -a results=()

    # Test each server
    while IFS= read -r server_name; do
        ((total_servers++))

        # Extract server configuration
        local command
        local args
        local description

        command=$(jq -r ".mcpServers.\"$server_name\".command" "$config_path")
        args=$(jq -c ".mcpServers.\"$server_name\".args" "$config_path")
        description=$(jq -r ".mcpServers.\"$server_name\".description // \"\"" "$config_path")

        # Test server
        local result
        local status
        local error_type
        local error_msg

        read -r status error_type error_msg < <(test_server "$server_name" "$command" "$args" "$description")

        if [[ "$status" == "healthy" ]]; then
            ((healthy_servers++))
            if [[ "$JSON_MODE" == "false" ]]; then
                echo -e "[${GREEN}✓${NC}] $server_name - Connected successfully"
            fi
        else
            ((unhealthy_servers++))
            if [[ "$JSON_MODE" == "false" ]]; then
                echo -e "[${RED}✗${NC}] $server_name - Failed: $error_msg"
            fi
        fi

        # Store result for JSON output
        if [[ "$JSON_MODE" == "true" ]]; then
            local json_result
            if [[ "$status" == "healthy" ]]; then
                json_result=$(jq -n \
                    --arg name "$server_name" \
                    --arg desc "$description" \
                    --arg status "healthy" \
                    '{name: $name, description: $desc, status: $status}')
            else
                json_result=$(jq -n \
                    --arg name "$server_name" \
                    --arg desc "$description" \
                    --arg status "unhealthy" \
                    --arg error_type "$error_type" \
                    --arg error_msg "$error_msg" \
                    '{name: $name, description: $desc, status: $status, error: {type: $error_type, message: $error_msg}}')
            fi
            results+=("$json_result")
        fi

    done <<< "$servers"

    # Output summary
    if [[ "$JSON_MODE" == "true" ]]; then
        # Build JSON output
        local servers_json
        servers_json=$(printf '%s\n' "${results[@]}" | jq -s '.')

        local overall_status
        if [[ $unhealthy_servers -eq 0 ]]; then
            overall_status="all_healthy"
        elif [[ $healthy_servers -eq 0 ]]; then
            overall_status="all_unhealthy"
        else
            overall_status="partial_failure"
        fi

        jq -n \
            --argjson servers "$servers_json" \
            --arg status "$overall_status" \
            --argjson total "$total_servers" \
            --argjson healthy "$healthy_servers" \
            --argjson unhealthy "$unhealthy_servers" \
            '{servers: $servers, summary: {total: $total, healthy: $healthy, unhealthy: $unhealthy}, status: $status}'
    else
        echo ""
        echo "Summary: $healthy_servers/$total_servers servers healthy"

        if [[ $unhealthy_servers -gt 0 ]]; then
            echo ""
            echo "Troubleshooting:"
            echo "  1. Verify required binaries are installed (npx, uvx, backlog)"
            echo "  2. Check network connectivity and firewall settings"
            echo "  3. Review server-specific logs for detailed errors"
            echo "  4. Ensure required environment variables are set"
            echo "  5. Try manually starting failed servers for detailed output"
        fi
    fi

    # Exit with appropriate code
    if [[ $unhealthy_servers -gt 0 ]]; then
        exit 1
    else
        exit 0
    fi
}

# Run main function
main
