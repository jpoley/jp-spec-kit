#!/usr/bin/env bash
# post-commit-backlog-events.sh - Emit flowspec events when backlog tasks change
#
# This git post-commit hook detects changes to backlog task files and emits
# corresponding flowspec events via `specify hooks emit`.
#
# Events emitted:
#   - task.created:        New task file added
#   - task.status_changed: Task status field changed
#   - task.completed:      Task status changed to "Done"
#   - task.ac_checked:     Acceptance criterion checkbox changed
#
# Usage:
#   Called automatically as git post-commit hook
#   Or manually: ./scripts/hooks/post-commit-backlog-events.sh
#
# Install:
#   ln -s ../../scripts/hooks/post-commit-backlog-events.sh .git/hooks/post-commit
#   Or add to install-hooks.sh
#
# Exit codes:
#   0 - Success (events emitted or nothing to do)
#   1 - Error parsing task files

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Configuration
BACKLOG_DIR="backlog/tasks"
SPECIFY_CMD="${SPECIFY_CMD:-specify}"
DRY_RUN="${DRY_RUN:-false}"
VERBOSE="${VERBOSE:-false}"

# Colors (disabled on non-tty)
if [ -t 1 ]; then
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'
else
    GREEN='' YELLOW='' BLUE='' NC=''
fi

log_info() { echo -e "${GREEN}[backlog-events]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[backlog-events]${NC} $*" >&2; }
log_debug() { [[ "$VERBOSE" == true ]] && echo -e "${BLUE}[backlog-events]${NC} $*" || true; }

# Parse task ID from filename
# Input: backlog/tasks/task-123 - Some-Title.md or task-204.01 - Title.md
# Output: task-123 or task-204.01
# Note: Malformed IDs like "task-1..2" are sanitized by extracting the valid
#       prefix "task-1". This is intentional - the function extracts the longest
#       valid task ID prefix from the filename.
parse_task_id() {
    local filename="$1"
    # Match task-N or task-N.M format - extracts valid prefix from malformed IDs
    basename "$filename" | sed -E 's/^(task-[0-9]+(\.[0-9]+)?).*/\1/'
}

# Get frontmatter field from task file
# Usage: get_field <file> <field>
get_field() {
    local file="$1"
    local field="$2"
    # Extract value from YAML frontmatter between --- markers
    # Only removes surrounding quotes, preserves quotes within values
    sed -n '/^---$/,/^---$/p' "$file" | grep -E "^${field}:" | head -1 | sed -E "s/^${field}:\s*//" | sed -E "s/^(['\"])(.*)\1$/\2/"
}

# Count checked acceptance criteria
# Returns: "checked/total"
count_ac() {
    local file="$1"
    local checked total
    # Use { grep || true; } to handle no-match case (grep returns 1 when no matches)
    # This is required with pipefail to prevent script exit on zero checked ACs
    checked=$({ grep '^\- \[x\]' "$file" 2>/dev/null || true; } | wc -l)
    total=$({ grep '^\- \[.\]' "$file" 2>/dev/null || true; } | wc -l)
    echo "${checked}/${total}"
}

# Emit event via specify hooks emit
emit_event() {
    local event_type="$1"
    local task_id="$2"
    shift 2
    local extra_args=("$@")

    log_info "Emitting: $event_type for $task_id"

    if [[ "$DRY_RUN" == true ]]; then
        log_debug "  [dry-run] $SPECIFY_CMD hooks emit $event_type --task-id $task_id ${extra_args[*]:-}"
        return 0
    fi

    if ! command -v "$SPECIFY_CMD" &>/dev/null; then
        log_warn "  specify CLI not found, skipping event emission"
        return 0
    fi

    # Run specify hooks emit
    if "$SPECIFY_CMD" hooks emit "$event_type" --task-id "$task_id" "${extra_args[@]}" 2>/dev/null; then
        log_debug "  Event emitted successfully"
    else
        log_warn "  Failed to emit event (non-fatal)"
    fi
}

# Process a new task file
process_new_task() {
    local file="$1"
    local task_id
    task_id=$(parse_task_id "$file")

    log_info "New task detected: $task_id"
    emit_event "task.created" "$task_id"
}

# Process a modified task file
# Compare current state with previous commit
process_modified_task() {
    local file="$1"
    local task_id
    task_id=$(parse_task_id "$file")

    log_debug "Processing modified task: $task_id"

    # Get current and previous status
    local current_status prev_status
    current_status=$(get_field "$file" "status")

    # Get previous status from HEAD~1
    prev_status=$(git show "HEAD~1:$file" 2>/dev/null | sed -n '/^---$/,/^---$/p' | grep -E "^status:" | head -1 | sed -E "s/^status:\s*'?([^']*)'?$/\1/" | tr -d "'" || echo "")

    log_debug "  Status: $prev_status -> $current_status"

    # Emit status change events
    if [[ "$current_status" != "$prev_status" && -n "$prev_status" ]]; then
        if [[ "$current_status" == "Done" ]]; then
            emit_event "task.completed" "$task_id" --message "Status changed from $prev_status to Done"
        else
            emit_event "task.status_changed" "$task_id" --message "Status changed from $prev_status to $current_status"
        fi
    fi

    # Check for AC changes
    local current_ac prev_ac
    current_ac=$(count_ac "$file")

    # Get previous AC count from HEAD~1
    # Use { grep || true; } to handle no-match case with pipefail
    local prev_checked prev_total_count
    prev_checked=$(git show "HEAD~1:$file" 2>/dev/null | { grep '^\- \[x\]' || true; } | wc -l)
    prev_total_count=$(git show "HEAD~1:$file" 2>/dev/null | { grep '^\- \[.\]' || true; } | wc -l)
    prev_ac="${prev_checked}/${prev_total_count}"

    log_debug "  AC: $prev_ac -> $current_ac"

    if [[ "$current_ac" != "$prev_ac" && "$prev_ac" != "0/0" ]]; then
        emit_event "task.ac_checked" "$task_id" --message "AC progress: $current_ac"
    fi
}

# Main execution
main() {
    cd "$PROJECT_ROOT"

    # Check if this is a git repository with commits
    if ! git rev-parse HEAD &>/dev/null; then
        log_debug "No commits yet, skipping"
        exit 0
    fi

    # Check if we have a parent commit to compare against
    if ! git rev-parse HEAD~1 &>/dev/null; then
        log_debug "No parent commit (initial commit), skipping comparison"
        exit 0
    fi

    # Get list of changed backlog task files in this commit
    local changed_files
    changed_files=$(git diff --name-status HEAD~1 HEAD -- "$BACKLOG_DIR/" 2>/dev/null || true)

    if [[ -z "$changed_files" ]]; then
        log_debug "No backlog task changes detected"
        exit 0
    fi

    log_info "Processing backlog task changes..."

    local events_emitted=0

    while IFS=$'\t' read -r status file; do
        [[ -z "$file" ]] && continue

        # Only process task files matching format: task-N - Title.md or task-N.M - Title.md
        if [[ ! "$file" =~ task-[0-9]+(\.[0-9]+)?( - .+)?\.md$ ]]; then
            log_debug "Skipping non-task file: $file"
            continue
        fi

        case "$status" in
            A)  # Added (new file)
                process_new_task "$file"
                ((events_emitted++)) || true
                ;;
            M)  # Modified
                process_modified_task "$file"
                ((events_emitted++)) || true
                ;;
            D)  # Deleted - no event for now
                log_debug "Task deleted: $file (no event)"
                ;;
            R*) # Renamed
                log_debug "Task renamed: $file (no event)"
                ;;
            *)
                log_debug "Unknown status $status for: $file"
                ;;
        esac
    done <<< "$changed_files"

    if [[ "$events_emitted" -gt 0 ]]; then
        log_info "Processed $events_emitted task change(s)"
    else
        log_debug "No events to emit"
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--dry-run] [--verbose]"
            echo ""
            echo "Git post-commit hook to emit flowspec events for backlog task changes."
            echo ""
            echo "Options:"
            echo "  --dry-run    Show events that would be emitted without executing"
            echo "  --verbose    Show detailed debug output"
            echo "  --help       Show this help message"
            exit 0
            ;;
        *)
            log_warn "Unknown option: $1"
            exit 1
            ;;
    esac
done

main "$@"
