#!/usr/bin/env bash
# MCP Server Health Check Script
# Tests connectivity and availability of configured MCP servers
#
# Usage: ./scripts/check-mcp-servers.sh [options]
# Options:
#   -v, --verbose    Show detailed output
#   -q, --quiet      Only show errors
#   -c, --config     Path to .mcp.json (default: .mcp.json)
#   -h, --help       Show this help message
#
# Exit codes:
#   0 - All servers healthy
#   1 - One or more servers failed
#   2 - Configuration error

set -euo pipefail

# Colors for output (disabled if not a terminal)
if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    BLUE='\033[0;34m'
    NC='\033[0m' # No Color
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
fi

# Default values
VERBOSE=false
QUIET=false
CONFIG_FILE=".mcp.json"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Counter for results
TOTAL=0
PASSED=0
FAILED=0
WARNINGS=0

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -q|--quiet)
                QUIET=true
                shift
                ;;
            -c|--config)
                if [[ -z "${2:-}" ]]; then
                    echo "Error: -c/--config requires a path argument"
                    show_help
                    exit 2
                fi
                CONFIG_FILE="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                show_help
                exit 2
                ;;
        esac
    done
}

show_help() {
    cat << EOF
MCP Server Health Check Script

Tests connectivity and availability of configured MCP servers.

Usage: $0 [options]

Options:
    -v, --verbose    Show detailed output including command paths
    -q, --quiet      Only show errors and summary
    -c, --config     Path to .mcp.json config file (default: .mcp.json)
    -h, --help       Show this help message

Exit codes:
    0 - All servers healthy
    1 - One or more servers failed
    2 - Configuration error

Examples:
    $0                          # Check all servers in .mcp.json
    $0 -v                       # Verbose output
    $0 -c ~/project/.mcp.json   # Use custom config path
EOF
}

log_info() {
    if [[ "$QUIET" != "true" ]]; then
        echo -e "${BLUE}[INFO]${NC} $1"
    fi
}

log_success() {
    if [[ "$QUIET" != "true" ]]; then
        echo -e "${GREEN}[PASS]${NC} $1"
    fi
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

log_verbose() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo -e "       $1"
    fi
}

# Check if a command exists
check_command() {
    local cmd="$1"
    if command -v "$cmd" &>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Get the path of a command
get_command_path() {
    local cmd="$1"
    command -v "$cmd" 2>/dev/null || echo "not found"
}

# Check if jq is available (required for parsing JSON)
check_dependencies() {
    if ! check_command "jq"; then
        log_error "jq is required but not installed. Install with: brew install jq"
        exit 2
    fi
}

# Parse .mcp.json and extract server information
parse_config() {
    local config_path="$1"

    # Check if config file exists
    if [[ ! -f "$config_path" ]]; then
        log_error "Config file not found: $config_path"
        exit 2
    fi

    # Validate JSON syntax
    if ! jq empty "$config_path" 2>/dev/null; then
        log_error "Invalid JSON in config file: $config_path"
        exit 2
    fi

    # Check if mcpServers key exists
    if ! jq -e '.mcpServers' "$config_path" &>/dev/null; then
        log_error "No 'mcpServers' key found in config file"
        exit 2
    fi
}

# Get list of server names
get_server_names() {
    local config_path="$1"
    jq -r '.mcpServers | keys[]' "$config_path"
}

# Get server command
get_server_command() {
    local config_path="$1"
    local server_name="$2"
    jq -r ".mcpServers[\"$server_name\"].command // empty" "$config_path"
}

# Get server description
get_server_description() {
    local config_path="$1"
    local server_name="$2"
    jq -r ".mcpServers[\"$server_name\"].description // \"No description\"" "$config_path"
}

# Get server args (as comma-separated string for display)
get_server_args() {
    local config_path="$1"
    local server_name="$2"
    jq -r ".mcpServers[\"$server_name\"].args | join(\" \")" "$config_path" 2>/dev/null || echo ""
}

# Check a single MCP server
check_server() {
    local server_name="$1"
    local config_path="$2"

    ((++TOTAL))

    local cmd
    cmd=$(get_server_command "$config_path" "$server_name")

    if [[ -z "$cmd" ]]; then
        log_error "$server_name: No command specified"
        ((++FAILED))
        return 1
    fi

    local description
    description=$(get_server_description "$config_path" "$server_name")

    local args
    args=$(get_server_args "$config_path" "$server_name")

    # Check if the base command exists
    if check_command "$cmd"; then
        local cmd_path
        cmd_path=$(get_command_path "$cmd")
        log_success "$server_name ($cmd)"
        log_verbose "Description: $description"
        log_verbose "Command path: $cmd_path"
        if [[ -n "$args" ]]; then
            log_verbose "Args: $args"
        fi

        # Additional checks for specific commands
        case "$cmd" in
            npx)
                # npx servers are installed on-demand, so we just check npx exists
                if [[ "$VERBOSE" == "true" ]]; then
                    log_verbose "npx version: $(npx --version 2>/dev/null || echo 'unknown')"
                fi
                ;;
            uvx)
                # uvx servers are installed on-demand
                if [[ "$VERBOSE" == "true" ]]; then
                    log_verbose "uvx version: $(uvx --version 2>/dev/null || echo 'unknown')"
                fi
                ;;
            backlog)
                # Check backlog is properly installed
                if ! backlog --version &>/dev/null; then
                    log_warning "$server_name: backlog command exists but may not be properly installed"
                    ((++WARNINGS))
                fi
                ;;
        esac

        ((++PASSED))
        return 0
    else
        log_error "$server_name: Command '$cmd' not found"
        log_verbose "Description: $description"
        log_verbose "Ensure '$cmd' is installed and in PATH"

        # Provide installation hints
        case "$cmd" in
            npx)
                log_verbose "Install Node.js: https://nodejs.org/"
                ;;
            uvx)
                log_verbose "Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
                ;;
            backlog)
                log_verbose "Install backlog: cargo install backlog-md"
                ;;
        esac

        ((++FAILED))
        return 1
    fi
}

# Print summary
print_summary() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "MCP Server Health Check Summary"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "Total:    ${TOTAL}"
    echo -e "Passed:   ${GREEN}${PASSED}${NC}"

    if [[ $FAILED -gt 0 ]]; then
        echo -e "Failed:   ${RED}${FAILED}${NC}"
    else
        echo -e "Failed:   ${FAILED}"
    fi

    if [[ $WARNINGS -gt 0 ]]; then
        echo -e "Warnings: ${YELLOW}${WARNINGS}${NC}"
    fi
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if [[ $FAILED -eq 0 && $WARNINGS -eq 0 ]]; then
        echo -e "${GREEN}All MCP servers are healthy!${NC}"
    elif [[ $FAILED -eq 0 ]]; then
        echo -e "${YELLOW}All servers available but some have warnings.${NC}"
    else
        echo -e "${RED}Some MCP servers are unavailable.${NC}"
        echo "Run with -v flag for installation hints."
    fi
}

# Main function
main() {
    parse_args "$@"

    # Resolve config file path
    if [[ ! "$CONFIG_FILE" = /* ]]; then
        # Relative path - try project root first, then current directory
        if [[ -f "${PROJECT_ROOT}/${CONFIG_FILE}" ]]; then
            CONFIG_FILE="${PROJECT_ROOT}/${CONFIG_FILE}"
        elif [[ -f "${CONFIG_FILE}" ]]; then
            : # File exists in current directory, use as-is
        fi
    fi

    log_info "Checking MCP server configuration: $CONFIG_FILE"
    echo ""

    # Check dependencies
    check_dependencies

    # Parse and validate config
    parse_config "$CONFIG_FILE"

    # Get list of servers and check each one
    local servers
    servers=$(get_server_names "$CONFIG_FILE")

    while IFS= read -r server; do
        check_server "$server" "$CONFIG_FILE" || true
    done < <(get_server_names "$CONFIG_FILE")

    # Print summary
    print_summary

    # Return appropriate exit code
    if [[ $FAILED -gt 0 ]]; then
        exit 1
    fi
    exit 0
}

# Run main function
main "$@"
