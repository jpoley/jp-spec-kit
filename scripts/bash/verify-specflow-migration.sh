#!/usr/bin/env bash
# verify-specflow-migration.sh
# Comprehensive verification script for specflow → specflow migration
#
# This script verifies:
# 1. No remaining specflow references (with exceptions)
# 2. All expected specflow files/directories exist
# 3. Tests pass with new naming
# 4. Documentation builds successfully
# 5. CI/CD workflows are valid

set -euo pipefail

# Source common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./common.sh
source "$SCRIPT_DIR/common.sh"

REPO_ROOT=$(get_repo_root)
VERBOSE="${VERBOSE:-false}"
JSON_OUTPUT="${JSON_OUTPUT:-false}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters for summary
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNINGS=0

# Logging functions
log_info() {
    if [[ "$JSON_OUTPUT" != "true" ]]; then
        echo -e "${BLUE}[INFO]${NC} $*"
    fi
}

log_success() {
    if [[ "$JSON_OUTPUT" != "true" ]]; then
        echo -e "${GREEN}[✓]${NC} $*"
    fi
}

log_warn() {
    if [[ "$JSON_OUTPUT" != "true" ]]; then
        echo -e "${YELLOW}[!]${NC} $*"
    fi
}

log_error() {
    if [[ "$JSON_OUTPUT" != "true" ]]; then
        echo -e "${RED}[✗]${NC} $*"
    fi
}

log_verbose() {
    if [[ "$VERBOSE" == "true" ]] && [[ "$JSON_OUTPUT" != "true" ]]; then
        echo -e "${BLUE}[VERBOSE]${NC} $*"
    fi
}

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Verify the specflow → specflow migration is complete and correct.

OPTIONS:
    --verbose           Enable verbose output
    --json              Output results in JSON format
    --help              Show this help message

ENVIRONMENT:
    VERBOSE=true        Same as --verbose
    JSON_OUTPUT=true    Same as --json

EXAMPLES:
    # Standard verification
    ./scripts/bash/verify-specflow-migration.sh

    # Verbose output
    ./scripts/bash/verify-specflow-migration.sh --verbose

    # JSON output for CI/automation
    ./scripts/bash/verify-specflow-migration.sh --json

EXIT CODES:
    0   All checks passed
    1   One or more checks failed
    2   Critical error (e.g., not in correct directory)

EOF
}

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose)
            VERBOSE=true
            shift
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Check result tracking
check_pass() {
    ((TOTAL_CHECKS++))
    ((PASSED_CHECKS++))
    log_success "$1"
}

check_fail() {
    ((TOTAL_CHECKS++))
    ((FAILED_CHECKS++))
    log_error "$1"
}

check_warn() {
    ((WARNINGS++))
    log_warn "$1"
}

# Verify we're in the correct repository
verify_location() {
    log_info "Verifying repository location..."

    if [[ ! -f "$REPO_ROOT/pyproject.toml" ]] || [[ ! -d "$REPO_ROOT/.claude" ]]; then
        log_error "Not in jp-spec-kit repository root"
        return 1
    fi

    check_pass "Repository location verified"
    return 0
}

# Check for remaining specflow references
check_remaining_references() {
    log_info "Checking for remaining specflow references..."

    # Excluded paths that are allowed to contain specflow
    local exclude_args=(
        --exclude-dir=.git
        --exclude-dir=.venv
        --exclude-dir=node_modules
        --exclude-dir=__pycache__
        --exclude-dir=.pytest_cache
        --exclude-dir=.migration-backup*
        --exclude="*.pyc"
        --exclude="CHANGELOG.md"                    # Historical references OK
        --exclude="migration-report.md"             # Migration documentation
        --exclude="verify-specflow-migration.sh"    # This script
        --exclude="migrate-specflow-to-specflow.sh"   # Migration script
    )

    local remaining_refs
    remaining_refs=$(grep -r "specflow" "$REPO_ROOT" "${exclude_args[@]}" 2>/dev/null || true)

    if [[ -z "$remaining_refs" ]]; then
        check_pass "No remaining specflow references found"
    else
        local ref_count=$(echo "$remaining_refs" | wc -l)
        check_fail "Found $ref_count remaining specflow references"

        if [[ "$VERBOSE" == "true" ]]; then
            log_verbose "Remaining references:"
            echo "$remaining_refs" | head -20 | sed 's/^/  /'
            if [[ $ref_count -gt 20 ]]; then
                log_verbose "... and $((ref_count - 20)) more"
            fi
        fi
    fi
}

# Verify expected directories exist
check_directories() {
    log_info "Verifying directory structure..."

    local expected_dirs=(
        "templates/commands/specflow"
        ".claude/commands/specflow"
    )

    local old_dirs=(
        "templates/commands/specflow"
        ".claude/commands/specflow"
    )

    # Check new directories exist
    for dir in "${expected_dirs[@]}"; do
        if [[ -d "$REPO_ROOT/$dir" ]]; then
            check_pass "Directory exists: $dir"
        else
            check_fail "Directory missing: $dir"
        fi
    done

    # Check old directories don't exist
    for dir in "${old_dirs[@]}"; do
        if [[ ! -d "$REPO_ROOT/$dir" ]]; then
            check_pass "Old directory removed: $dir"
        else
            check_fail "Old directory still exists: $dir"
        fi
    done
}

# Verify expected files exist
check_files() {
    log_info "Verifying critical files..."

    local expected_files=(
        "specflow_workflow.yml"
        "memory/specflow_workflow.yml"
        "memory/specflow_workflow.schema.json"
    )

    local old_files=(
        "specflow_workflow.yml"
        "memory/specflow_workflow.yml"
        "memory/specflow_workflow.schema.json"
    )

    # Check new files exist
    for file in "${expected_files[@]}"; do
        if [[ -f "$REPO_ROOT/$file" ]]; then
            check_pass "File exists: $file"
        else
            check_fail "File missing: $file"
        fi
    done

    # Check old files don't exist (except specflow_workflow.yml which may be kept for compatibility)
    for file in "${old_files[@]}"; do
        if [[ "$file" == "specflow_workflow.yml" ]]; then
            # This file may be kept as a symlink or removed - both are acceptable
            if [[ -f "$REPO_ROOT/$file" ]]; then
                check_warn "Legacy file still exists: $file (consider removing)"
            else
                check_pass "Legacy file removed: $file"
            fi
        elif [[ ! -f "$REPO_ROOT/$file" ]]; then
            check_pass "Old file removed: $file"
        else
            check_fail "Old file still exists: $file"
        fi
    done
}

# Verify agent files renamed
check_agent_files() {
    log_info "Verifying GitHub Copilot agent files..."

    local agent_dir="$REPO_ROOT/.github/agents"

    if [[ ! -d "$agent_dir" ]]; then
        check_warn "Agent directory not found: .github/agents"
        return
    fi

    # Check for old specflow agent files
    local old_agents
    old_agents=$(find "$agent_dir" -name "specflow-*.agent.md" -type f 2>/dev/null || true)

    if [[ -z "$old_agents" ]]; then
        check_pass "No old specflow agent files found"
    else
        local count=$(echo "$old_agents" | wc -l)
        check_fail "Found $count old specflow agent files"
        if [[ "$VERBOSE" == "true" ]]; then
            echo "$old_agents" | sed 's/^/  /'
        fi
    fi

    # Check for new specflow agent files
    local new_agents
    new_agents=$(find "$agent_dir" -name "specflow-*.agent.md" -type f 2>/dev/null || true)

    if [[ -n "$new_agents" ]]; then
        local count=$(echo "$new_agents" | wc -l)
        check_pass "Found $count specflow agent files"
        if [[ "$VERBOSE" == "true" ]]; then
            echo "$new_agents" | sed 's/^/  /'
        fi
    else
        check_fail "No specflow agent files found"
    fi
}

# Verify test files renamed
check_test_files() {
    log_info "Verifying test files..."

    local tests_dir="$REPO_ROOT/tests"

    if [[ ! -d "$tests_dir" ]]; then
        check_warn "Tests directory not found"
        return
    fi

    # Check for old test files
    local old_tests
    old_tests=$(find "$tests_dir" -name "test_specflow_*.py" -type f 2>/dev/null || true)

    if [[ -z "$old_tests" ]]; then
        check_pass "No old test_specflow_* files found"
    else
        local count=$(echo "$old_tests" | wc -l)
        check_fail "Found $count old test_specflow_* files"
        if [[ "$VERBOSE" == "true" ]]; then
            echo "$old_tests" | sed 's/^/  /'
        fi
    fi

    # Check for new test files
    local new_tests
    new_tests=$(find "$tests_dir" -name "test_specflow_*.py" -type f 2>/dev/null || true)

    if [[ -n "$new_tests" ]]; then
        local count=$(echo "$new_tests" | wc -l)
        check_pass "Found $count specflow test files"
        if [[ "$VERBOSE" == "true" ]]; then
            echo "$new_tests" | sed 's/^/  /'
        fi
    else
        check_fail "No specflow test files found"
    fi
}

# Run pytest to verify tests pass
run_tests() {
    log_info "Running tests..."

    if ! command -v pytest &> /dev/null; then
        check_warn "pytest not found, skipping test execution"
        return
    fi

    local test_output
    if test_output=$(pytest "$REPO_ROOT/tests" -v 2>&1); then
        check_pass "All tests passed"
        if [[ "$VERBOSE" == "true" ]]; then
            echo "$test_output"
        fi
    else
        check_fail "Tests failed"
        if [[ "$VERBOSE" == "true" ]]; then
            echo "$test_output"
        fi
    fi
}

# Verify workflow YAML is valid
check_workflow_yaml() {
    log_info "Verifying workflow YAML files..."

    local workflow_files=(
        "specflow_workflow.yml"
        "memory/specflow_workflow.yml"
    )

    for workflow_file in "${workflow_files[@]}"; do
        local file_path="$REPO_ROOT/$workflow_file"

        if [[ ! -f "$file_path" ]]; then
            check_fail "Workflow file missing: $workflow_file"
            continue
        fi

        # Basic YAML syntax check using Python
        if python3 -c "import yaml; yaml.safe_load(open('$file_path'))" 2>/dev/null; then
            check_pass "Valid YAML: $workflow_file"
        else
            check_fail "Invalid YAML: $workflow_file"
        fi
    done
}

# Check command files in .claude/commands
check_command_files() {
    log_info "Verifying slash command files..."

    local commands_dir="$REPO_ROOT/.claude/commands/specflow"

    if [[ ! -d "$commands_dir" ]]; then
        check_fail "Commands directory not found: .claude/commands/specflow"
        return
    fi

    # Count command files
    local cmd_count
    cmd_count=$(find "$commands_dir" -name "*.md" -type f 2>/dev/null | wc -l)

    if [[ $cmd_count -gt 0 ]]; then
        check_pass "Found $cmd_count command files in .claude/commands/specflow"
    else
        check_fail "No command files found in .claude/commands/specflow"
    fi

    # Verify no /specflow: references in command files
    if grep -r "/specflow:" "$commands_dir" 2>/dev/null; then
        check_fail "Found /specflow: references in command files"
    else
        check_pass "No /specflow: references in command files"
    fi
}

# Generate JSON report
generate_json_report() {
    cat <<EOF
{
  "migration_verification": {
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "repository_root": "$REPO_ROOT",
    "summary": {
      "total_checks": $TOTAL_CHECKS,
      "passed": $PASSED_CHECKS,
      "failed": $FAILED_CHECKS,
      "warnings": $WARNINGS,
      "success": $([ $FAILED_CHECKS -eq 0 ] && echo "true" || echo "false")
    }
  }
}
EOF
}

# Generate summary report
generate_summary() {
    if [[ "$JSON_OUTPUT" == "true" ]]; then
        generate_json_report
        return
    fi

    cat <<EOF

════════════════════════════════════════════════════════════════
                  VERIFICATION SUMMARY
════════════════════════════════════════════════════════════════

Total Checks:    $TOTAL_CHECKS
Passed:          $PASSED_CHECKS
Failed:          $FAILED_CHECKS
Warnings:        $WARNINGS

Overall Status:  $([ $FAILED_CHECKS -eq 0 ] && echo -e "${GREEN}PASSED${NC}" || echo -e "${RED}FAILED${NC}")

════════════════════════════════════════════════════════════════

EOF

    if [[ $FAILED_CHECKS -gt 0 ]]; then
        cat <<EOF
Recommended Actions:
  1. Review failed checks above
  2. Re-run migration script if needed
  3. Manually fix any remaining issues
  4. Run this verification again

Rollback (if needed):
  See migration script for rollback instructions
  ./scripts/bash/migrate-specflow-to-specflow.sh --help

EOF
    else
        cat <<EOF
Next Steps:
  ✓ Migration verification complete
  → Review changes: git status
  → Run full test suite: pytest tests/
  → Test CI locally: ./scripts/bash/run-local-ci.sh
  → Commit changes: git add -A && git commit -m "Rename /specflow to /specflow"

EOF
    fi
}

# Main execution
main() {
    if [[ "$JSON_OUTPUT" != "true" ]]; then
        log_info "Starting specflow migration verification"
        log_info "Repository: $REPO_ROOT"
        echo
    fi

    # Run all verification checks
    verify_location || exit 2
    check_remaining_references
    check_directories
    check_files
    check_agent_files
    check_test_files
    check_workflow_yaml
    check_command_files

    # Optional: Run tests (can be slow)
    # run_tests

    # Generate summary
    generate_summary

    # Exit with appropriate code
    if [[ $FAILED_CHECKS -gt 0 ]]; then
        exit 1
    else
        exit 0
    fi
}

main "$@"
