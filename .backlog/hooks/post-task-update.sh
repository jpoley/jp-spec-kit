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
#   0 - Success
#   Non-zero - Error (fail open, does not block task update)

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
    exit 1
fi

# Normalize task ID to task-XXX format
if [[ ! "$TASK_ID" =~ ^task- ]]; then
    TASK_ID="task-$TASK_ID"
fi

# Get task title for memory creation
TASK_TITLE=""
if command -v backlog &>/dev/null; then
    TASK_TITLE=$(backlog task "${TASK_ID#task-}" --plain 2>/dev/null | \
                 grep -oP "Task task-\d+ - \K.*" | head -1 || echo "")
fi

# Log hook execution
echo "[task-memory] Hook triggered: $TASK_ID ($OLD_STATUS → $NEW_STATUS)" >&2

# Call Python lifecycle manager
cd "$PROJECT_ROOT"

# Use python3 explicitly (compatible with Claude Code hooks)
if ! command -v python3 &>/dev/null; then
    echo "[task-memory] ERROR: python3 not found" >&2
    exit 1
fi

# Execute lifecycle hook through Python module
python3 -c "
import sys
sys.path.insert(0, 'src')

from specify_cli.memory.lifecycle import LifecycleManager

manager = LifecycleManager()
manager.on_state_change(
    task_id='$TASK_ID',
    old_state='$OLD_STATUS',
    new_state='$NEW_STATUS',
    task_title='$TASK_TITLE'
)
print('[task-memory] Lifecycle hook completed', file=sys.stderr)
" || {
    echo "[task-memory] ERROR: Lifecycle hook failed (exit code: $?)" >&2
    # Fail open - don't block task updates
    exit 0
}

exit 0
