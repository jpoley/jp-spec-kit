#!/bin/bash
#
# Post-workflow hook: Archive tasks preview
#
# This hook runs after workflow completion (validate.completed event)
# and shows what tasks would be archived (dry-run only).
#
# Event: validate.completed (end of /flow:validate)
# Mode: Dry-run only (preview, no actual archiving)
# Exit: Always 0 (fail-open - never block workflow)
#
# Input: Event JSON on stdin with:
#   - event_type: string (e.g., "validate.completed")
#   - feature: string (spec ID)
#   - project_root: string (project directory)
#
# Output: Logs to stdout for debugging
#

set -o pipefail

# Get project directory from environment or default to current
PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
ARCHIVE_SCRIPT="${PROJECT_ROOT}/scripts/bash/archive-tasks.sh"

# Timeout for archive script (seconds)
TIMEOUT=30

# Log function
log() {
    echo "[post-workflow-archive] $*"
}

# Read event from stdin (standard hook interface)
read_event() {
    local event
    event=$(cat)
    echo "$event"
}

# Parse JSON field using Python (more reliable than jq dependency)
parse_json() {
    local json="$1"
    local field="$2"
    echo "$json" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('$field', ''))" 2>/dev/null || echo ""
}

# Main execution
main() {
    log "Starting archive preview..."

    # Read event from stdin
    local event
    event=$(read_event)

    if [[ -z "$event" ]]; then
        log "No event data received on stdin"
        exit 0  # Fail-open
    fi

    # Parse event data
    local event_type feature project_root_from_event
    event_type=$(parse_json "$event" "event_type")
    feature=$(parse_json "$event" "feature")
    project_root_from_event=$(parse_json "$event" "project_root")

    log "Event: $event_type"
    log "Feature: ${feature:-unknown}"

    # Use project_root from event if provided
    if [[ -n "$project_root_from_event" ]]; then
        PROJECT_ROOT="$project_root_from_event"
        ARCHIVE_SCRIPT="${PROJECT_ROOT}/scripts/bash/archive-tasks.sh"
    fi

    log "Project: $PROJECT_ROOT"

    # Verify event type (optional - hook can run for any event)
    if [[ "$event_type" != "validate.completed" && -n "$event_type" ]]; then
        log "Skipping: event type '$event_type' is not validate.completed"
        exit 0
    fi

    # Check if archive script exists
    if [[ ! -f "$ARCHIVE_SCRIPT" ]]; then
        log "Archive script not found: $ARCHIVE_SCRIPT"
        exit 0  # Fail-open
    fi

    if [[ ! -x "$ARCHIVE_SCRIPT" ]]; then
        log "Archive script not executable: $ARCHIVE_SCRIPT"
        exit 0  # Fail-open
    fi

    # Run archive script in dry-run mode
    log "Running archive preview (dry-run)..."
    log "Command: $ARCHIVE_SCRIPT --dry-run"

    local output exit_code
    cd "$PROJECT_ROOT" || exit 0

    # Capture output and exit code
    set +e
    output=$(timeout "$TIMEOUT" "$ARCHIVE_SCRIPT" --dry-run 2>&1)
    exit_code=$?
    set -e

    # Log output
    if [[ -n "$output" ]]; then
        log "Archive preview output:"
        echo "$output" | while IFS= read -r line; do
            log "  $line"
        done
    fi

    # Handle exit codes from archive-tasks.sh
    case $exit_code in
        0)
            log "Archive preview completed - tasks would be archived"
            ;;
        2)
            log "No tasks to archive"
            ;;
        124)
            log "Archive preview timed out after ${TIMEOUT}s"
            ;;
        *)
            log "Archive preview exited with code $exit_code"
            ;;
    esac

    # Always exit 0 (fail-open principle)
    log "Archive preview complete"
    exit 0
}

# Run main function
main "$@"
