# Galway Automation Infrastructure Design

**Status**: Platform Design
**Owner**: Platform Engineer
**Last Updated**: 2025-12-04

## Executive Summary

This document defines the automation architecture for all galway host tasks, implementing event-driven automation, hook systems, and intelligent scripting to maximize developer velocity and operational excellence.

## Automation Philosophy

### The Automation Pyramid

```
┌──────────────────────────────────────────────────────────────┐
│                    Automation Pyramid                         │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│                  ┌─────────────────┐                          │
│                  │   Autonomous    │                          │
│                  │   (Self-heal)   │                          │
│                  └────────┬────────┘                          │
│                           │                                   │
│              ┌────────────┴────────────┐                      │
│              │     Event-Driven        │                      │
│              │   (React to changes)    │                      │
│              └────────────┬────────────┘                      │
│                           │                                   │
│          ┌────────────────┴────────────────┐                  │
│          │         Scheduled               │                  │
│          │    (Cron-based tasks)           │                  │
│          └────────────────┬────────────────┘                  │
│                           │                                   │
│      ┌────────────────────┴────────────────────┐              │
│      │              Manual                     │              │
│      │   (Developer-initiated scripts)         │              │
│      └─────────────────────────────────────────┘              │
└──────────────────────────────────────────────────────────────┘
```

**Key Principles**:
1. **Automate Toil**: Eliminate repetitive manual work
2. **Fail Gracefully**: Automation failures should not block developers
3. **Observable**: All automation should emit events and metrics
4. **Idempotent**: Safe to run multiple times
5. **Self-Documenting**: Code as documentation

## Script Architecture and Standards

### Script Organization

```
scripts/
├── bash/                    # Bash automation scripts
│   ├── lib/                 # Shared libraries
│   │   ├── logging.sh       # Structured logging functions
│   │   ├── colors.sh        # Terminal color utilities
│   │   ├── git-utils.sh     # Git helper functions
│   │   └── task-utils.sh    # Backlog task utilities
│   ├── archive-tasks.sh     # Archive Done tasks (task-281.01)
│   ├── local-ci.sh          # Local CI simulation (task-085)
│   ├── setup-pre-commit.sh  # Pre-commit hook setup
│   └── backlog-wrapper.sh   # Event-emitting CLI wrapper (task-204.02)
├── python/                  # Python automation scripts
│   ├── validate-security-policy.py
│   ├── generate-dora-metrics.py
│   └── migrate-commands.py  # Command migration (task-276)
├── hooks/                   # Git hook scripts
│   ├── pre-commit           # Pre-commit validation
│   ├── post-commit          # Event emission (task-204.01)
│   ├── pre-push             # Pre-push checks
│   └── post-workflow-archive # Post-workflow hook (task-283)
└── ci/                      # CI-specific scripts
    ├── check-stale-tasks.sh # Stale task detection (task-285)
    └── validate-commands.sh # Command validation (task-278)
```

### Bash Script Template

**Standard Template** (`scripts/bash/template.sh`):
```bash
#!/bin/bash
#
# Script: template.sh
# Description: Brief description of what this script does
# Author: Platform Engineer
# Date: 2025-12-04
#
# Usage: ./template.sh [options] <args>
#
# Options:
#   -h, --help      Show this help message
#   -v, --verbose   Enable verbose output
#   -n, --dry-run   Dry run mode (no changes)
#
# Exit Codes:
#   0 - Success
#   1 - General error
#   2 - Invalid arguments
#   3 - Precondition failed

set -euo pipefail  # Exit on error, undefined var, pipe failure

# Load shared libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/logging.sh"
source "${SCRIPT_DIR}/lib/colors.sh"

# Configuration (with defaults)
VERBOSE=${VERBOSE:-false}
DRY_RUN=${DRY_RUN:-false}

# Function: show_help
# Display usage information
show_help() {
    cat <<EOF
Usage: $(basename "$0") [options] <args>

Brief description of what this script does.

Options:
  -h, --help      Show this help message
  -v, --verbose   Enable verbose output
  -n, --dry-run   Dry run mode (no changes)

Examples:
  $(basename "$0") --verbose arg1 arg2
  $(basename "$0") --dry-run
EOF
}

# Function: parse_args
# Parse command-line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -n|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -*)
                log_error "Unknown option: $1"
                show_help
                exit 2
                ;;
            *)
                # Positional arguments
                ARGS+=("$1")
                shift
                ;;
        esac
    done
}

# Function: check_preconditions
# Verify prerequisites before running
check_preconditions() {
    # Check if in git repo
    if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        log_error "Not in a git repository"
        exit 3
    fi

    # Check required commands
    for cmd in jq yq; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            log_error "Required command not found: $cmd"
            exit 3
        fi
    done
}

# Function: main
# Main script logic
main() {
    log_info "Starting $(basename "$0")"

    if [ "$DRY_RUN" = true ]; then
        log_warning "DRY RUN MODE - No changes will be made"
    fi

    # Main logic here
    # ...

    log_info "Completed successfully"
}

# Entry point
ARGS=()
parse_args "$@"
check_preconditions
main
```

### Structured Logging Library

**Library** (`scripts/bash/lib/logging.sh`):
```bash
#!/bin/bash
#
# Structured logging library for bash scripts
# Outputs JSON-formatted logs for easy parsing and aggregation

# ANSI color codes for terminal output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if output is to a terminal
if [ -t 1 ]; then
    USE_COLOR=true
else
    USE_COLOR=false
fi

# Function: _log
# Internal logging function
_log() {
    local level=$1
    local message=$2
    local context=${3:-"{}"}
    local color=$4

    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")
    local logger="bash.$(basename "${BASH_SOURCE[2]}")"
    local function_name="${FUNCNAME[2]}"
    local line_number="${BASH_LINENO[1]}"

    # Build JSON log entry
    local log_entry=$(cat <<EOF
{
  "timestamp": "$timestamp",
  "level": "$level",
  "logger": "$logger",
  "function": "$function_name",
  "line": $line_number,
  "message": "$message",
  "context": $context,
  "pid": $$,
  "host": "$(hostname)"
}
EOF
)

    # Output colored terminal message or JSON
    if [ "$USE_COLOR" = true ]; then
        echo -e "${color}[$level]${NC} $message" >&2
        if [ "$context" != "{}" ]; then
            echo "  Context: $context" >&2
        fi
    else
        echo "$log_entry"
    fi
}

# Public logging functions
log_debug() {
    if [ "${DEBUG:-false}" = true ]; then
        _log "DEBUG" "$1" "${2:-{}}" "$BLUE"
    fi
}

log_info() {
    _log "INFO" "$1" "${2:-{}}" "$GREEN"
}

log_warning() {
    _log "WARNING" "$1" "${2:-{}}" "$YELLOW"
}

log_error() {
    _log "ERROR" "$1" "${2:-{}}" "$RED" >&2
}

log_fatal() {
    _log "FATAL" "$1" "${2:-{}}" "$RED" >&2
    exit 1
}

# Function: log_metric
# Emit Prometheus-style metric
log_metric() {
    local metric_name=$1
    local metric_value=$2
    local labels=${3:-""}

    echo "# TYPE $metric_name gauge"
    echo "${metric_name}{${labels}} $metric_value $(date +%s)000"
}

# Function: log_event
# Emit structured event
log_event() {
    local event_type=$1
    local event_data=$2

    cat <<EOF
{
  "event_type": "$event_type",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")",
  "data": $event_data
}
EOF
}
```

### Task Utility Library

**Library** (`scripts/bash/lib/task-utils.sh`):
```bash
#!/bin/bash
#
# Backlog task utility functions

# Function: list_tasks_by_state
# List task IDs in a specific state
list_tasks_by_state() {
    local state=$1
    backlog task list -s "$state" --plain | awk -F'|' '{print $2}' | tr -d ' '
}

# Function: get_task_age_days
# Get age of task in days since last update
get_task_age_days() {
    local task_id=$1
    local updated_date=$(backlog task view "$task_id" --plain | grep "Updated:" | awk '{print $2}')

    if [ -z "$updated_date" ]; then
        echo "0"
        return
    fi

    local task_epoch=$(date -d "$updated_date" +%s)
    local now_epoch=$(date +%s)
    local age_seconds=$((now_epoch - task_epoch))
    local age_days=$((age_seconds / 86400))

    echo "$age_days"
}

# Function: archive_task
# Archive a single task
archive_task() {
    local task_id=$1
    local dry_run=${2:-false}

    if [ "$dry_run" = true ]; then
        log_info "Would archive: $task_id"
        return
    fi

    log_info "Archiving task: $task_id"
    backlog task archive "$task_id"
}

# Function: update_task_status
# Update task status with event emission
update_task_status() {
    local task_id=$1
    local new_status=$2

    log_info "Updating $task_id status to $new_status"
    backlog task edit "$task_id" -s "$new_status"

    # Emit event
    log_event "backlog.task.state_changed" "{\"task_id\": \"$task_id\", \"to_state\": \"$new_status\"}"
}
```

## Automation Workflows

### Archive Tasks Automation (task-281.01)

**Script** (`scripts/bash/archive-tasks.sh`):
```bash
#!/bin/bash
#
# Archive Done tasks older than threshold
#
# Usage: ./archive-tasks.sh [--days N] [--dry-run] [--filter STATE]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/logging.sh"
source "${SCRIPT_DIR}/lib/task-utils.sh"

# Configuration
DAYS_THRESHOLD=${DAYS_THRESHOLD:-7}
DRY_RUN=${DRY_RUN:-false}
FILTER_STATE=${FILTER_STATE:-Done}

show_help() {
    cat <<EOF
Usage: $(basename "$0") [options]

Archive backlog tasks that have been in Done state for more than N days.

Options:
  --days N         Archive tasks older than N days (default: 7)
  --dry-run        Show what would be archived without making changes
  --filter STATE   Archive tasks in specific state (default: Done)
  -h, --help       Show this help message

Examples:
  $(basename "$0") --days 14              # Archive tasks older than 14 days
  $(basename "$0") --dry-run              # Preview what would be archived
  $(basename "$0") --filter "Done,Closed" # Archive Done or Closed tasks
EOF
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --days)
                DAYS_THRESHOLD=$2
                shift 2
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --filter)
                FILTER_STATE=$2
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 2
                ;;
        esac
    done
}

main() {
    log_info "Starting archive process" "{\"days_threshold\": $DAYS_THRESHOLD, \"dry_run\": $DRY_RUN, \"filter\": \"$FILTER_STATE\"}"

    # Get all tasks in target state(s)
    local task_count=0
    local archived_count=0

    IFS=',' read -ra STATES <<< "$FILTER_STATE"
    for state in "${STATES[@]}"; do
        log_info "Processing tasks in state: $state"

        # Get task IDs in this state
        local tasks=$(list_tasks_by_state "$state")

        if [ -z "$tasks" ]; then
            log_info "No tasks found in state: $state"
            continue
        fi

        # Process each task
        while IFS= read -r task_id; do
            [ -z "$task_id" ] && continue

            task_count=$((task_count + 1))
            local age=$(get_task_age_days "$task_id")

            log_debug "Checking $task_id (age: $age days)" "{\"task_id\": \"$task_id\", \"age_days\": $age}"

            if [ "$age" -ge "$DAYS_THRESHOLD" ]; then
                archive_task "$task_id" "$DRY_RUN"
                archived_count=$((archived_count + 1))

                # Emit metric
                log_metric "backlog_tasks_archived_total" 1 "state=\"$state\",age_days=\"$age\""
            fi
        done <<< "$tasks"
    done

    log_info "Archive complete" "{\"processed\": $task_count, \"archived\": $archived_count, \"dry_run\": $DRY_RUN}"

    # Emit summary metrics
    log_metric "backlog_archive_run_total" 1 "dry_run=\"$DRY_RUN\""
    log_metric "backlog_tasks_processed" $task_count
    log_metric "backlog_tasks_archived" $archived_count
}

parse_args "$@"
main
```

**Scheduled Execution** (GitHub Actions):
```yaml
# .github/workflows/archive-tasks.yml
name: Archive Done Tasks

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday at midnight
  workflow_dispatch:
    inputs:
      days:
        description: 'Archive tasks older than N days'
        required: false
        default: '7'
      dry_run:
        description: 'Dry run (no changes)'
        type: boolean
        default: false

jobs:
  archive:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python and uv
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install backlog CLI
        run: |
          pip install uv
          uv tool install backlog-md

      - name: Run archive script
        env:
          DAYS_THRESHOLD: ${{ inputs.days || '7' }}
          DRY_RUN: ${{ inputs.dry_run || false }}
        run: |
          chmod +x scripts/bash/archive-tasks.sh
          ./scripts/bash/archive-tasks.sh

      - name: Commit changes
        if: ${{ !inputs.dry_run }}
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add backlog/
          git diff --quiet && git diff --staged --quiet || \
            (git commit -m "chore(backlog): archive Done tasks [skip ci]" && git push)
```

### Local CI Simulation (task-085)

**Script** (`scripts/bash/local-ci.sh`):
```bash
#!/bin/bash
#
# Local CI simulation - run the same checks as GitHub Actions locally
#
# Usage: ./local-ci.sh [--fast] [--skip-tests]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/logging.sh"

# Configuration
FAST_MODE=${FAST_MODE:-false}
SKIP_TESTS=${SKIP_TESTS:-false}

show_help() {
    cat <<EOF
Usage: $(basename "$0") [options]

Run CI checks locally before pushing to GitHub.

Options:
  --fast         Skip slower checks (matrix tests, full security scan)
  --skip-tests   Skip pytest execution
  -h, --help     Show this help message

Exit Codes:
  0 - All checks passed
  1 - One or more checks failed
EOF
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --fast)
                FAST_MODE=true
                shift
                ;;
            --skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 2
                ;;
        esac
    done
}

# Function: run_check
# Run a CI check and track success/failure
run_check() {
    local name=$1
    local command=$2
    local start_time=$(date +%s)

    log_info "Running: $name"

    if eval "$command"; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        log_info "✅ $name passed (${duration}s)"
        return 0
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        log_error "❌ $name failed (${duration}s)"
        return 1
    fi
}

main() {
    log_info "Starting local CI simulation" "{\"fast_mode\": $FAST_MODE, \"skip_tests\": $SKIP_TESTS}"

    local failed=0
    local total=0

    # Check 1: Formatting
    total=$((total + 1))
    run_check "ruff format check" "uv run ruff format --check ." || failed=$((failed + 1))

    # Check 2: Linting
    total=$((total + 1))
    run_check "ruff lint" "uv run ruff check ." || failed=$((failed + 1))

    # Check 3: Tests (unless skipped)
    if [ "$SKIP_TESTS" = false ]; then
        total=$((total + 1))
        if [ "$FAST_MODE" = true ]; then
            run_check "pytest (fast)" "uv run pytest tests/ -x --ff" || failed=$((failed + 1))
        else
            run_check "pytest" "uv run pytest tests/ -v --cov=src/specify_cli --cov-report=term-missing" || failed=$((failed + 1))
        fi
    fi

    # Check 4: Build
    total=$((total + 1))
    run_check "uv build" "uv build" || failed=$((failed + 1))

    # Check 5: Security scan (unless fast mode)
    if [ "$FAST_MODE" = false ]; then
        total=$((total + 1))
        run_check "bandit security scan" "uv tool run bandit -r src/ -ll" || failed=$((failed + 1))
    fi

    # Summary
    echo ""
    log_info "Local CI complete: $((total - failed))/$total checks passed"

    if [ $failed -eq 0 ]; then
        log_info "✅ All checks passed - ready to push!"
        return 0
    else
        log_error "❌ $failed check(s) failed - fix before pushing"
        return 1
    fi
}

parse_args "$@"
main
```

### Command Migration Script (task-276)

**Script** (`scripts/python/migrate-commands.py`):
```python
#!/usr/bin/env python3
"""
Migrate backlog CLI commands to new structure.

Usage:
    python migrate-commands.py --source old-format.md --dest new-format.md
"""
import argparse
import logging
from pathlib import Path
import re

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def parse_old_format(content: str) -> dict:
    """Parse old command format."""
    # Example old format:
    # ## task list [options]
    # Description here
    pass

def convert_to_new_format(old_data: dict) -> str:
    """Convert to new command format."""
    # Example new format:
    # # Command: task list
    # ## Description
    # List all tasks
    pass

def main():
    parser = argparse.ArgumentParser(description='Migrate command structure')
    parser.add_argument('--source', required=True, help='Source file')
    parser.add_argument('--dest', required=True, help='Destination file')
    parser.add_argument('--dry-run', action='store_true', help='Dry run')
    args = parser.parse_args()

    source = Path(args.source)
    dest = Path(args.dest)

    if not source.exists():
        logger.error(f"Source file not found: {source}")
        return 1

    logger.info(f"Reading source: {source}")
    content = source.read_text()

    logger.info("Parsing old format...")
    old_data = parse_old_format(content)

    logger.info("Converting to new format...")
    new_content = convert_to_new_format(old_data)

    if args.dry_run:
        logger.info("DRY RUN - would write to: {dest}")
        print(new_content)
    else:
        logger.info(f"Writing to: {dest}")
        dest.write_text(new_content)
        logger.info("✅ Migration complete")

    return 0

if __name__ == '__main__':
    exit(main())
```

## Git Hook System

### Post-commit Event Emission (task-204.01)

**Hook** (`.git/hooks/post-commit`):
```bash
#!/bin/bash
#
# Post-commit hook: Emit events for backlog task file changes

SCRIPT_DIR="$(git rev-parse --git-dir)/../scripts/bash"
source "${SCRIPT_DIR}/lib/logging.sh"

COMMIT_SHA=$(git rev-parse HEAD)
CHANGED_FILES=$(git diff-tree --no-commit-id --name-only -r HEAD)

# Check if any backlog task files changed
if echo "$CHANGED_FILES" | grep -q '^backlog/tasks/'; then
    TASK_FILES=$(echo "$CHANGED_FILES" | grep '^backlog/tasks/')

    while IFS= read -r file; do
        [ -z "$file" ] && continue

        # Extract task ID from filename
        TASK_ID=$(basename "$file" | grep -oP 'task-\d+' || echo "unknown")

        # Emit event
        log_event "backlog.task.updated_via_commit" "$(cat <<EOF
{
  "task_id": "$TASK_ID",
  "commit_sha": "$COMMIT_SHA",
  "file": "$file",
  "author": "$(git log -1 --pretty=%an)",
  "message": "$(git log -1 --pretty=%s)"
}
EOF
)"
    done <<< "$TASK_FILES"
fi
```

### Post-workflow Archive Hook (task-283)

**Hook** (`scripts/hooks/post-workflow-archive.sh`):
```bash
#!/bin/bash
#
# Post-workflow hook: Archive tasks after workflow completion

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../bash/lib/logging.sh"

# Configuration
WORKFLOW_NAME=$1  # e.g., "/jpspec:implement"
AUTO_ARCHIVE=${AUTO_ARCHIVE:-false}

log_info "Post-workflow hook triggered" "{\"workflow\": \"$WORKFLOW_NAME\"}"

# If workflow was /jpspec:validate and all tasks Done, archive
if [ "$WORKFLOW_NAME" = "/jpspec:validate" ] && [ "$AUTO_ARCHIVE" = true ]; then
    log_info "Running auto-archive for completed workflow"

    # Archive tasks that moved to Done in this workflow
    bash "${SCRIPT_DIR}/../bash/archive-tasks.sh" --filter Done --days 0
fi
```

## CI-Specific Automation

### Stale Task Detection (task-285)

**Script** (`scripts/ci/check-stale-tasks.sh`):
```bash
#!/bin/bash
#
# Detect and report stale Done tasks in CI

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../bash/lib/logging.sh"
source "${SCRIPT_DIR}/../bash/lib/task-utils.sh"

THRESHOLD_DAYS=${THRESHOLD_DAYS:-7}

main() {
    log_info "Checking for stale Done tasks (threshold: $THRESHOLD_DAYS days)"

    local stale_count=0
    local done_tasks=$(list_tasks_by_state "Done")

    if [ -z "$done_tasks" ]; then
        log_info "No Done tasks found"
        return 0
    fi

    while IFS= read -r task_id; do
        [ -z "$task_id" ] && continue

        local age=$(get_task_age_days "$task_id")

        if [ "$age" -ge "$THRESHOLD_DAYS" ]; then
            log_warning "Stale task detected: $task_id (age: $age days)"
            stale_count=$((stale_count + 1))
        fi
    done <<< "$done_tasks"

    if [ $stale_count -gt 0 ]; then
        log_warning "Found $stale_count stale Done tasks (>$THRESHOLD_DAYS days old)"
        log_info "Run: ./scripts/bash/archive-tasks.sh to clean up"

        # Emit metric
        log_metric "backlog_stale_tasks_count" $stale_count "state=\"Done\",threshold_days=\"$THRESHOLD_DAYS\""

        # Non-blocking - just warn
        return 0
    else
        log_info "✅ No stale tasks found"
        return 0
    fi
}

main
```

**CI Integration**:
```yaml
# .github/workflows/ci.yml
jobs:
  stale-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check for stale tasks
        run: |
          chmod +x scripts/ci/check-stale-tasks.sh
          ./scripts/ci/check-stale-tasks.sh

      - name: Comment on PR if stale tasks found
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            // Check if any stale tasks detected (non-blocking)
            // Post informational comment
```

### Command Structure Validation (task-278)

**Script** (`scripts/ci/validate-commands.sh`):
```bash
#!/bin/bash
#
# Validate command file structure and naming conventions

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../bash/lib/logging.sh"

COMMANDS_DIR=".claude/commands"

main() {
    log_info "Validating command structure"

    local errors=0

    # Check if commands directory exists
    if [ ! -d "$COMMANDS_DIR" ]; then
        log_error "Commands directory not found: $COMMANDS_DIR"
        return 1
    fi

    # Validate each command file
    for cmd_file in "$COMMANDS_DIR"/*.md; do
        [ ! -f "$cmd_file" ] && continue

        local filename=$(basename "$cmd_file")

        # Check naming convention: lowercase with hyphens
        if [[ ! "$filename" =~ ^[a-z0-9-]+\.md$ ]]; then
            log_error "Invalid command filename: $filename (must be lowercase-with-hyphens.md)"
            errors=$((errors + 1))
        fi

        # Check for required sections
        if ! grep -q "^# " "$cmd_file"; then
            log_error "Missing title in: $filename"
            errors=$((errors + 1))
        fi

        log_info "✅ Validated: $filename"
    done

    if [ $errors -eq 0 ]; then
        log_info "✅ All command files valid"
        return 0
    else
        log_error "❌ Found $errors validation error(s)"
        return 1
    fi
}

main
```

## Backlog CLI Wrapper (task-204.02)

**Wrapper** (`scripts/bash/backlog-wrapper.sh`):
```bash
#!/bin/bash
#
# Backlog CLI wrapper with automatic event emission

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/logging.sh"

# Find real backlog binary
BACKLOG_BIN=$(which backlog)

# Event log location
EVENT_LOG="${HOME}/.specify/events.log"
mkdir -p "$(dirname "$EVENT_LOG")"

emit_event() {
    local event_type=$1
    local event_data=$2

    log_event "$event_type" "$event_data" >> "$EVENT_LOG"
}

# Parse backlog command
COMMAND=${1:-}
shift || true

case $COMMAND in
    task)
        SUBCOMMAND=${1:-}
        shift || true

        # Execute original command and capture output
        OUTPUT=$("$BACKLOG_BIN" task "$SUBCOMMAND" "$@" 2>&1)
        EXIT_CODE=$?

        # Emit event based on subcommand
        case $SUBCOMMAND in
            create)
                if [ $EXIT_CODE -eq 0 ]; then
                    TASK_ID=$(echo "$OUTPUT" | grep -oP 'task-\d+' | head -1)
                    emit_event "backlog.task.created" "{\"task_id\": \"$TASK_ID\"}"
                fi
                ;;
            edit)
                if [ $EXIT_CODE -eq 0 ]; then
                    TASK_ID=${1:-unknown}
                    emit_event "backlog.task.updated" "{\"task_id\": \"$TASK_ID\"}"
                fi
                ;;
            archive)
                if [ $EXIT_CODE -eq 0 ]; then
                    TASK_ID=${1:-unknown}
                    emit_event "backlog.task.archived" "{\"task_id\": \"$TASK_ID\"}"
                fi
                ;;
        esac

        echo "$OUTPUT"
        exit $EXIT_CODE
        ;;
    *)
        # Pass through to original command
        "$BACKLOG_BIN" "$COMMAND" "$@"
        ;;
esac
```

**Installation**:
```bash
# Create alias in shell config
alias backlog='~/ps/jp-spec-kit/scripts/bash/backlog-wrapper.sh'
```

## Automation Metrics and Observability

**Metrics to Collect**:
```prometheus
# Script execution
automation_script_duration_seconds{script_name, status}
automation_script_runs_total{script_name, status}

# Task operations
backlog_tasks_archived_total{state, age_days}
backlog_stale_tasks_detected{threshold_days}

# CI automation
ci_local_simulation_runs_total{status}
ci_command_validation_errors_total

# Hook execution
git_hook_execution_duration_seconds{hook_name}
git_hook_events_emitted_total{hook_name, event_type}
```

## Success Metrics

**Automation Coverage**:
- **Repetitive Tasks Automated**: 90% of toil eliminated
- **Script Reliability**: > 99% success rate
- **Execution Time**: Scripts complete in < 1 minute P95

**Developer Experience**:
- **Time Saved**: 2+ hours/week per developer
- **Errors Prevented**: 80% reduction in manual mistakes
- **Onboarding Time**: New developers productive in < 1 day

## Related Tasks

| Task ID | Title | Script/Hook |
|---------|-------|-------------|
| task-281.01 | archive-tasks.sh | `scripts/bash/archive-tasks.sh` |
| task-085 | Local CI Script | `scripts/bash/local-ci.sh` |
| task-283 | Post-workflow Hook | `scripts/hooks/post-workflow-archive.sh` |
| task-276 | Command Migration | `scripts/python/migrate-commands.py` |
| task-285 | Stale Task CI Check | `scripts/ci/check-stale-tasks.sh` |
| task-278 | Command Validation | `scripts/ci/validate-commands.sh` |
| task-204.01 | Git Hook Events | `.git/hooks/post-commit` |
| task-204.02 | CLI Wrapper | `scripts/bash/backlog-wrapper.sh` |

## Appendix: Script Testing

All automation scripts should have corresponding tests:

```bash
# tests/scripts/test-archive-tasks.sh
#!/bin/bash

test_archive_dry_run() {
    OUTPUT=$(./scripts/bash/archive-tasks.sh --dry-run --days 7)
    assert_contains "$OUTPUT" "DRY RUN"
}

test_archive_filters_by_state() {
    # Create test task
    # Run archive with filter
    # Assert task archived
}
```

Run tests with:
```bash
bash tests/scripts/run-all-tests.sh
```
