#!/bin/bash
#
# SessionStart hook: Environment setup and context display
#
# This hook runs when starting or resuming a Claude Code session.
# It verifies key dependencies and displays active backlog tasks.
#
# Output: JSON with decision "allow" and contextual information
# Exit code: Always 0 (fail-open principle - never block sessions)
#

set -euo pipefail

# Get project directory (fallback to current directory if not set)
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"

# Timeout for subprocess calls (in seconds)
TIMEOUT=5

# ANSI color codes for pretty output (only if terminal supports it)
if [[ -t 1 ]]; then
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    RED='\033[0;31m'
    BLUE='\033[0;34m'
    NC='\033[0m' # No Color
else
    GREEN=''
    YELLOW=''
    RED=''
    BLUE=''
    NC=''
fi

# Initialize output arrays
warnings=()
info=()

# Helper function to run command with timeout
run_with_timeout() {
    local timeout_duration="$1"
    shift
    timeout "$timeout_duration" "$@" 2>/dev/null || true
}

# Check for uv
if ! command -v uv &> /dev/null; then
    warnings+=("uv not installed - Python package management may not work")
else
    info+=("uv: $(uv --version 2>/dev/null | head -n1 || echo 'installed')")
fi

# Check for backlog CLI
if ! command -v backlog &> /dev/null; then
    warnings+=("backlog CLI not installed - task management unavailable")
else
    # Get backlog version
    backlog_version=$(backlog --version 2>/dev/null || echo "unknown")
    info+=("backlog: $backlog_version")

    # Get active "In Progress" tasks
    cd "$PROJECT_DIR" || true
    tasks_output=$(run_with_timeout "$TIMEOUT" backlog task list --plain -s "In Progress" 2>/dev/null || echo "")

    if [[ -n "$tasks_output" ]]; then
        # Count tasks (each task is one line in --plain output)
        task_count=$(echo "$tasks_output" | grep -c "^" || echo "0")

        if [[ "$task_count" -gt 0 ]]; then
            info+=("Active tasks: $task_count in progress")
            # Add task details
            while IFS= read -r task_line; do
                # Extract task ID and title from plain output
                # Expected format: "task-XXX | Status | Title | ..."
                if [[ "$task_line" =~ ^([a-zA-Z0-9_-]+)[[:space:]]*\|[[:space:]]*[^|]+[[:space:]]*\|[[:space:]]*(.+)[[:space:]]*\| ]]; then
                    task_id="${BASH_REMATCH[1]}"
                    task_title="${BASH_REMATCH[2]}"
                    info+=("  - $task_id: $task_title")
                fi
            done <<< "$tasks_output"
        else
            info+=("No active tasks")
        fi
    else
        # Empty output or error - check if backlog.md exists
        if [[ -f "$PROJECT_DIR/backlog/backlog.md" ]]; then
            info+=("No tasks in 'In Progress' status")
        else
            warnings+=("backlog.md not found in project - task tracking not initialized")
        fi
    fi
fi

# Check for pending janitor cleanup
STATE_DIR="$PROJECT_DIR/.specify/state"
PENDING_CLEANUP="$STATE_DIR/pending-cleanup.json"

if [[ -f "$PENDING_CLEANUP" ]]; then
    # Use Python to parse JSON and count pending items
    janitor_warning=$(python3 -c "
import json
import sys

try:
    with open('$PENDING_CLEANUP', 'r') as f:
        data = json.load(f)

    merged = len(data.get('merged_branches', []))
    worktrees = len(data.get('orphaned_worktrees', []))
    non_compliant = len(data.get('non_compliant_branches', {}))

    total = merged + worktrees
    if total > 0 or non_compliant > 0:
        parts = []
        if merged > 0:
            parts.append(f'{merged} branch(es) to prune')
        if worktrees > 0:
            parts.append(f'{worktrees} worktree(s) to clean')
        if non_compliant > 0:
            parts.append(f'{non_compliant} branch(es) with naming issues')
        print(', '.join(parts))
except (json.JSONDecodeError, FileNotFoundError, KeyError):
    pass
" 2>/dev/null || echo "")

    if [[ -n "$janitor_warning" ]]; then
        warnings+=("Repository cleanup pending: $janitor_warning")
        warnings+=("  Run '/jpspec:github-janitor prune' to clean up")
    fi
fi

# Build context message for display
context_lines=()

if [[ ${#warnings[@]} -gt 0 ]]; then
    context_lines+=("${YELLOW}Environment Warnings:${NC}")
    for warning in "${warnings[@]}"; do
        context_lines+=("  ${YELLOW}⚠${NC} $warning")
    done
fi

if [[ ${#info[@]} -gt 0 ]]; then
    context_lines+=("")
    context_lines+=("${BLUE}Session Context:${NC}")
    for info_item in "${info[@]}"; do
        context_lines+=("  ${GREEN}✓${NC} $info_item")
    done
fi

# Format output as JSON
# Build additionalContext as a string with newlines
additional_context=""
if [[ ${#context_lines[@]} -gt 0 ]]; then
    for line in "${context_lines[@]}"; do
        # Remove color codes for JSON (they don't display well in notifications)
        clean_line=$(echo -e "$line" | sed 's/\x1b\[[0-9;]*m//g')
        if [[ -n "$additional_context" ]]; then
            additional_context="${additional_context}\n${clean_line}"
        else
            additional_context="$clean_line"
        fi
    done
fi

# Output JSON decision
python3 <<EOF
import json
import sys

decision = {
    "decision": "allow",
    "reason": "Session started - environment verified",
}

additional_context = """$additional_context"""
if additional_context.strip():
    decision["additionalContext"] = additional_context

print(json.dumps(decision))
EOF

# Always exit 0 (fail-open principle)
exit 0
