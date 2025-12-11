#!/usr/bin/env bash
# Post-task-update hook for backlog.md
#
# This hook is called after backlog task status updates to trigger
# task memory lifecycle operations.
#
# Arguments:
#   $1 - Task ID (e.g., "task-370" or "370")
#   $2 - Old status (e.g., "To Do")
#   $3 - New status (e.g., "In Progress")
#
# Exit codes:
#   0 - Success (always - fail open design)
#
# Security:
#   - Uses environment variables to pass data to Python (prevents shell injection)
#   - Validates task ID format
#   - Fail open to prevent blocking task updates

set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Parse arguments
TASK_ID="${1:-}"
OLD_STATUS="${2:-}"
NEW_STATUS="${3:-}"

if [[ -z "$TASK_ID" ]] || [[ -z "$OLD_STATUS" ]] || [[ -z "$NEW_STATUS" ]]; then
    echo "Usage: $0 <task-id> <old-status> <new-status>" >&2
    exit 0  # Fail open
fi

# Validate and normalize task ID to task-XXX format
# Security: Allow alphanumeric task IDs (matching Python TaskMemoryStore validation)
# Pattern: task-<identifier> where identifier starts with alphanumeric, followed by alphanumeric/hyphens
if [[ "$TASK_ID" =~ ^task-[a-zA-Z0-9][-a-zA-Z0-9]*$ ]]; then
    : # Already in correct format (e.g., task-42, task-abc, task-feature-123)
elif [[ "$TASK_ID" =~ ^[0-9]+$ ]]; then
    # Numeric-only input: normalize to task-NNN format
    TASK_ID="task-$TASK_ID"
elif [[ "$TASK_ID" =~ ^[a-zA-Z0-9][-a-zA-Z0-9]*$ ]]; then
    # Alphanumeric without prefix: normalize to task-XXX format
    TASK_ID="task-$TASK_ID"
else
    echo "[task-memory] ERROR: Invalid task ID format: $TASK_ID" >&2
    exit 0  # Fail open
fi

# Get task title for memory creation
TASK_TITLE=""
if command -v backlog &>/dev/null; then
    # Extract task identifier (numeric or alphanumeric) for backlog command
    # The backlog CLI accepts both "42" and "task-42" formats
    TASK_IDENTIFIER="${TASK_ID#task-}"
    # Try to get task title; handles both numeric and alphanumeric task IDs
    TASK_TITLE=$(backlog task "$TASK_IDENTIFIER" --plain 2>/dev/null | \
                 grep -oP "Task task-[a-zA-Z0-9][-a-zA-Z0-9]* - \K.*" | head -1 || echo "")
fi

# Log hook execution
echo "[task-memory] Hook triggered: $TASK_ID ($OLD_STATUS → $NEW_STATUS)" >&2

# Call Python lifecycle manager
cd "$PROJECT_ROOT"

# Use python3 explicitly (compatible with Claude Code hooks)
if ! command -v python3 &>/dev/null; then
    echo "[task-memory] ERROR: python3 not found" >&2
    exit 0  # Fail open
fi

# Security: Pass data via environment variables to prevent shell injection
# Python reads these directly without any string parsing that could be exploited
export HOOK_TASK_ID="$TASK_ID"
export HOOK_OLD_STATUS="$OLD_STATUS"
export HOOK_NEW_STATUS="$NEW_STATUS"
export HOOK_TASK_TITLE="$TASK_TITLE"

# Execute lifecycle hook through Python module
python3 << 'PYTHON_SCRIPT'
import os
import sys

sys.path.insert(0, 'src')

from specify_cli.memory.lifecycle import LifecycleManager

# Read from environment variables (safe from shell injection)
task_id = os.environ.get('HOOK_TASK_ID', '')
old_status = os.environ.get('HOOK_OLD_STATUS', '')
new_status = os.environ.get('HOOK_NEW_STATUS', '')
task_title = os.environ.get('HOOK_TASK_TITLE', '')

if not task_id or not old_status or not new_status:
    print('[task-memory] ERROR: Missing required environment variables', file=sys.stderr)
    sys.exit(0)  # Fail open

manager = LifecycleManager()
manager.on_state_change(
    task_id=task_id,
    old_state=old_status,
    new_state=new_status,
    task_title=task_title
)
print('[task-memory] Lifecycle hook completed', file=sys.stderr)
PYTHON_SCRIPT

exit_code=$?
if [[ $exit_code -ne 0 ]]; then
    echo "[task-memory] ERROR: Lifecycle hook failed (exit code: $exit_code)" >&2
fi

# Always exit 0 (fail open - don't block task updates)
exit 0
