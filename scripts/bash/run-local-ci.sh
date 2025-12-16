#!/usr/bin/env bash
#
# run-local-ci.sh - Simulate CI/CD pipeline locally (Inner Loop)
#
# This script runs the same checks that will run in GitHub Actions CI,
# allowing you to catch issues before pushing to remote.
#
# Usage:
#   ./scripts/bash/run-local-ci.sh [OPTIONS]
#
# Options:
#   --act         Use act (GitHub Actions local runner) instead of direct execution
#   --job JOB     Run specific job only (requires --act)
#   --workflow FILE Specify workflow file (optional, for disambiguation)
#   --list        List available workflow jobs (requires --act)
#   --help        Show this help message
#
# Prerequisites:
#   - Docker (required for act mode)
#   - act (auto-installed if missing when using --act)
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track overall status
OVERALL_STATUS=0

# Mode detection
USE_ACT=false
SPECIFIC_JOB=""
LIST_JOBS=false
WORKFLOW_FILE=""

# Function to show help
show_help() {
    echo "Usage: ./scripts/bash/run-local-ci.sh [OPTIONS]"
    echo ""
    echo "Simulate CI/CD pipeline locally (Inner Loop)"
    echo ""
    echo "Options:"
    echo "  --act              Use act (GitHub Actions local runner)"
    echo "  --job JOB          Run specific job only (requires --act)"
    echo "  --workflow FILE    Specify workflow file (optional, for disambiguation)"
    echo "  --list             List available workflow jobs (requires --act)"
    echo "  --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./scripts/bash/run-local-ci.sh                        # Direct execution"
    echo "  ./scripts/bash/run-local-ci.sh --act                  # Run via act"
    echo "  ./scripts/bash/run-local-ci.sh --act --job lint       # Run specific job"
    echo "  ./scripts/bash/run-local-ci.sh --act --job lint --workflow .github/workflows/ci.yml"
    echo "  ./scripts/bash/run-local-ci.sh --act --list           # List jobs"
    echo ""
    echo "Prerequisites for --act mode:"
    echo "  - Docker must be running"
    echo "  - act will be auto-installed if missing"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --act)
            USE_ACT=true
            shift
            ;;
        --job)
            if [ -z "$2" ] || [[ "$2" == --* ]]; then
                echo -e "${RED}Error: --job requires a job name${NC}"
                exit 1
            fi
            SPECIFIC_JOB="$2"
            shift 2
            ;;
        --workflow)
            if [ -z "$2" ] || [[ "$2" == --* ]]; then
                echo -e "${RED}Error: --workflow requires a file path${NC}"
                exit 1
            fi
            WORKFLOW_FILE="$2"
            shift 2
            ;;
        --list)
            LIST_JOBS=true
            USE_ACT=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
done

# Validate --job requires --act
if [ -n "$SPECIFIC_JOB" ] && [ "$USE_ACT" = false ]; then
    echo -e "${RED}Error: --job requires --act${NC}"
    exit 1
fi

# Validate --workflow requires --act
if [ -n "$WORKFLOW_FILE" ] && [ "$USE_ACT" = false ]; then
    echo -e "${RED}Error: --workflow requires --act${NC}"
    exit 1
fi

# Function to print step header
print_step() {
    echo -e "${BLUE}>>> $1${NC}"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}✗ $1${NC}"
    OVERALL_STATUS=1
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Function to check if act is installed
check_act_installed() {
    if ! command -v act &> /dev/null; then
        echo -e "${YELLOW}act is not installed${NC}"
        echo -n "Would you like to install it? (y/n): "
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            if [ -f "./scripts/bash/install-act.sh" ]; then
                ./scripts/bash/install-act.sh --auto
            else
                echo -e "${RED}Error: install-act.sh not found${NC}"
                echo "Please install act manually from: https://github.com/nektos/act"
                exit 1
            fi
        else
            echo "Please install act manually or run without --act flag"
            exit 1
        fi
    fi
}

# Function to check if Docker is running
check_docker_running() {
    if ! docker info &> /dev/null 2>&1; then
        echo -e "${RED}Docker is not running${NC}"
        echo "Please start Docker and try again"
        echo ""
        echo "act requires Docker to run GitHub Actions workflows locally."
        exit 1
    fi
}

# Function to list workflow jobs
list_workflow_jobs() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Available Workflow Jobs${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    if [ -n "$WORKFLOW_FILE" ]; then
        act -l -W "$WORKFLOW_FILE"
    else
        act -l
    fi
}

# Function to run a specific act job
run_act_job() {
    local job=$1
    local result=0
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Running job: $job${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    # Run with platform flag for compatibility (direct execution, no eval)
    if [ -n "$WORKFLOW_FILE" ]; then
        act -j "$job" --container-architecture linux/amd64 -W "$WORKFLOW_FILE" || result=$?
    else
        act -j "$job" --container-architecture linux/amd64 || result=$?
    fi

    if [ $result -eq 0 ]; then
        print_success "Job '$job' completed successfully"
    else
        print_error "Job '$job' failed"
        echo ""
        echo -e "${YELLOW}Note: Some failures may be expected for jobs requiring:${NC}"
        echo "  - GitHub secrets"
        echo "  - OIDC authentication"
        echo "  - External services"
    fi
}

# Function to run all jobs with act
run_with_act() {
    check_act_installed
    check_docker_running

    if [ "$LIST_JOBS" = true ]; then
        list_workflow_jobs
        exit 0
    fi

    if [ -n "$SPECIFIC_JOB" ]; then
        run_act_job "$SPECIFIC_JOB"
    else
        # Run all jobs
        echo -e "${BLUE}========================================${NC}"
        echo -e "${BLUE}  Running Full CI Workflow via act${NC}"
        echo -e "${BLUE}========================================${NC}"
        echo ""

        local result=0
        if [ -n "$WORKFLOW_FILE" ]; then
            act --container-architecture linux/amd64 -W "$WORKFLOW_FILE" || result=$?
        else
            act --container-architecture linux/amd64 || result=$?
        fi

        if [ $result -eq 0 ]; then
            print_success "All workflow jobs completed successfully"
        else
            print_warning "Some jobs failed - this may be expected"
            echo ""
            echo -e "${YELLOW}Common reasons for failures:${NC}"
            echo "  - Jobs requiring secrets or OIDC authentication"
            echo "  - Jobs needing external services"
            echo "  - Marketplace actions not fully supported by act"
            echo ""
            echo "To run individual jobs, use: --act --job <job-name>"
            OVERALL_STATUS=1
        fi
    fi
}

# Function to run direct CI checks (existing implementation)
run_direct() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Local CI Simulation (Inner Loop)${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    # Step 1: Check Python version
    print_step "Step 1: Checking Python version"
    PYTHON_CMD="python3"
    if ! command -v python3 &> /dev/null; then
        PYTHON_CMD="python"
    fi

    if $PYTHON_CMD --version 2>&1 | grep -q "Python 3.1[1-9]"; then
        print_success "Python version is 3.11+"
    else
        print_error "Python version must be 3.11 or higher"
        $PYTHON_CMD --version 2>&1 || echo "Python not found"
    fi
    echo ""

    # Step 2: Check dependencies
    print_step "Step 2: Checking dependencies"
    if command -v uv &> /dev/null; then
        print_success "uv is installed"
    else
        print_error "uv is not installed. Install from: https://docs.astral.sh/uv/"
    fi
    echo ""

    # Step 3: Sync dependencies
    print_step "Step 3: Syncing dependencies"
    if uv sync; then
        print_success "Dependencies synced successfully"
    else
        print_error "Failed to sync dependencies"
    fi
    echo ""

    # Step 4: Code formatting check
    print_step "Step 4: Checking code formatting (ruff format)"
    if uv run ruff format --check .; then
        print_success "Code formatting is correct"
    else
        print_warning "Code formatting issues found. Run: uv run ruff format ."
        OVERALL_STATUS=1
    fi
    echo ""

    # Step 5: Linting
    print_step "Step 5: Running linter (ruff check)"
    if uv run ruff check .; then
        print_success "Linting passed"
    else
        print_error "Linting failed. Run: uv run ruff check . --fix"
    fi
    echo ""

    # Step 6: Type checking (if mypy is configured)
    print_step "Step 6: Type checking"
    if uv run mypy src/ 2>/dev/null; then
        print_success "Type checking passed"
    else
        print_warning "mypy not configured or type checking failed, skipping"
    fi
    echo ""

    # Step 7: Run tests
    print_step "Step 7: Running tests (pytest)"
    if uv run pytest tests/ -v; then
        print_success "All tests passed"
    else
        print_error "Tests failed"
    fi
    echo ""

    # Step 8: Check test coverage
    print_step "Step 8: Checking test coverage"
    if uv run pytest tests/ --cov=src/flowspec_cli --cov-report=term-missing --cov-fail-under=0; then
        print_success "Coverage report generated"
    else
        print_warning "Coverage check had issues"
    fi
    echo ""

    # Step 9: Build package
    print_step "Step 9: Building package"
    if uv build; then
        print_success "Package built successfully"
    else
        print_error "Package build failed"
    fi
    echo ""

    # Step 10: Install and test CLI
    print_step "Step 10: Testing CLI installation"
    if uv tool install . --force; then
        print_success "CLI installed successfully"

        if flowspec --help &> /dev/null; then
            print_success "CLI is functional"
        else
            print_error "CLI installation succeeded but command failed"
        fi
    else
        print_error "CLI installation failed"
    fi
    echo ""

    # Final summary
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Summary${NC}"
    echo -e "${BLUE}========================================${NC}"

    if [ $OVERALL_STATUS -eq 0 ]; then
        echo -e "${GREEN}✓ All checks passed!${NC}"
        echo -e "${GREEN}  Your code is ready to push.${NC}"
    else
        echo -e "${RED}✗ Some checks failed.${NC}"
        echo -e "${RED}  Please fix the issues before pushing.${NC}"
    fi
    echo ""
}

# Main execution
if [ "$USE_ACT" = true ]; then
    run_with_act
else
    run_direct
fi

exit $OVERALL_STATUS
