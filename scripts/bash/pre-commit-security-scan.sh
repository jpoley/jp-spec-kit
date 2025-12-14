#!/bin/bash
#
# Pre-commit hook for fast security scanning
#
# This hook runs a fast security scan on changed files before commit.
# It blocks commits with critical vulnerabilities while allowing through
# lower-severity issues (which should be addressed in CI).
#
# Usage: Called automatically by pre-commit framework
#
# Environment Variables:
#   FLOWSPEC_SECURITY_BYPASS: Set to "1" to skip scanning (logged)
#   FLOWSPEC_SECURITY_FAIL_ON: Severity threshold (default: critical)
#   FLOWSPEC_SECURITY_TIMEOUT: Timeout in seconds (default: 30)
#
# Exit codes:
#   0 - Success (no critical issues)
#   1 - Critical vulnerabilities found
#   2 - Script error
#

set -o pipefail

# Configuration
FAIL_ON="${FLOWSPEC_SECURITY_FAIL_ON:-critical}"
TIMEOUT="${FLOWSPEC_SECURITY_TIMEOUT:-30}"
BYPASS_LOG=".flowspec/security-bypass.log"

# Colors (respect NO_COLOR)
if [[ -z "${NO_COLOR:-}" ]]; then
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

# Log function
log() {
    echo -e "${BLUE}[security-scan]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[security-scan]${NC} $*"
}

log_error() {
    echo -e "${RED}[security-scan]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[security-scan]${NC} $*"
}

# Check if bypass is requested
check_bypass() {
    if [[ "${FLOWSPEC_SECURITY_BYPASS:-}" == "1" ]]; then
        log_warn "Security scan bypassed via FLOWSPEC_SECURITY_BYPASS=1"
        log_bypass "env_bypass"
        return 0
    fi
    return 1
}

# Log bypass event for audit trail
log_bypass() {
    local reason="${1:-unknown}"
    local user
    local commit_msg
    local timestamp

    # Get user info
    user="${USER:-$(whoami 2>/dev/null || echo 'unknown')}"

    # Get commit message (first line)
    commit_msg=$(git log -1 --format=%s 2>/dev/null || echo "pending commit")

    # ISO timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    # Ensure directory exists
    mkdir -p "$(dirname "$BYPASS_LOG")"

    # Append to bypass log
    echo "${timestamp}|${user}|${reason}|${commit_msg}" >> "$BYPASS_LOG"

    log_warn "Bypass logged to $BYPASS_LOG"
}

# Get staged files for scanning
get_staged_files() {
    local files
    files=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null)

    # Filter to relevant file types
    echo "$files" | grep -E '\.(py|js|ts|tsx|jsx|go|rs|java|rb|php)$' || true
}

# Run security scan on staged files
run_scan() {
    local files="$1"
    local start_time
    local end_time
    local duration
    local exit_code=0

    start_time=$(date +%s)

    # Check if specify command exists
    if ! command -v specify &>/dev/null; then
        log_warn "specify-cli not found, skipping security scan"
        log_warn "Install with: pip install specify-cli"
        return 0
    fi

    # Check if we have files to scan
    if [[ -z "$files" ]]; then
        log "No scannable files staged"
        return 0
    fi

    local file_count
    file_count=$(echo "$files" | wc -l | tr -d ' ')
    log "Scanning $file_count staged file(s)..."

    # Create temp file with staged files
    local temp_file
    temp_file=$(mktemp)
    echo "$files" > "$temp_file"

    # Run security scan with timeout
    # Uses bandit for Python, semgrep if available
    local scan_output
    local scan_exit

    # Try specify security scan if available
    if specify security scan --help &>/dev/null; then
        scan_output=$(timeout "$TIMEOUT" specify security scan \
            --fast \
            --changed-only \
            --fail-on "$FAIL_ON" \
            --files-from "$temp_file" 2>&1) || scan_exit=$?
    else
        # Fallback to basic bandit scan for Python files
        local py_files
        py_files=$(echo "$files" | grep '\.py$' || true)

        if [[ -n "$py_files" ]] && command -v bandit &>/dev/null; then
            log "Using bandit for Python security scan..."
            scan_output=$(timeout "$TIMEOUT" bandit -r -ll \
                $(echo "$py_files" | tr '\n' ' ') 2>&1) || scan_exit=$?
        else
            log "No security scanner available, skipping"
            rm -f "$temp_file"
            return 0
        fi
    fi

    rm -f "$temp_file"

    end_time=$(date +%s)
    duration=$((end_time - start_time))

    # Handle timeout
    if [[ "${scan_exit:-0}" -eq 124 ]]; then
        log_warn "Scan timed out after ${TIMEOUT}s"
        log_warn "Consider increasing FLOWSPEC_SECURITY_TIMEOUT"
        return 0  # Don't block on timeout
    fi

    # Handle scan results
    if [[ "${scan_exit:-0}" -ne 0 ]]; then
        log_error "Security scan found issues (${duration}s):"
        echo "$scan_output"
        log_error ""
        log_error "Commit blocked due to $FAIL_ON severity findings."
        log_error "Fix the issues or bypass with: git commit --no-verify"
        return 1
    fi

    log_success "Security scan passed (${duration}s)"
    return 0
}

# Main execution
main() {
    log "Starting pre-commit security scan..."

    # Check for bypass
    if check_bypass; then
        return 0
    fi

    # Get staged files
    local staged_files
    staged_files=$(get_staged_files)

    # Run the scan
    if ! run_scan "$staged_files"; then
        return 1
    fi

    return 0
}

# Run main function
main "$@"
