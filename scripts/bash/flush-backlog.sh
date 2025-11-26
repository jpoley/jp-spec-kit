#!/usr/bin/env bash
set -euo pipefail

# flush-backlog.sh - Archive Done tasks and generate summary
# Usage: ./scripts/bash/flush-backlog.sh [--dry-run] [--no-summary] [--auto-commit] [--help]

# Configuration
BACKLOG_DIR="backlog"
ARCHIVE_DIR="backlog/archive"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Flags
DRY_RUN=false
NO_SUMMARY=false
AUTO_COMMIT=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Statistics
TOTAL_ARCHIVED=0
FAILED_TASKS=()

#######################################
# Display usage information
#######################################
show_help() {
    cat <<EOF
flush-backlog.sh - Archive Done tasks and generate summary

USAGE:
    ./scripts/bash/flush-backlog.sh [OPTIONS]

OPTIONS:
    --dry-run       Show what would be archived without making changes
    --no-summary    Skip generating the flush summary report
    --auto-commit   Automatically commit changes after flushing
    --help          Show this help message

DESCRIPTION:
    Archives all tasks with status "Done" to backlog/archive/ and generates
    a timestamped summary report with metadata and statistics.

EXIT CODES:
    0 - Success (tasks archived or no tasks found)
    1 - Validation error (backlog CLI not installed)
    2 - No tasks to archive
    3 - Partial failures (some tasks failed to archive)

EXAMPLES:
    # Dry run to see what would be archived
    ./scripts/bash/flush-backlog.sh --dry-run

    # Archive and skip summary generation
    ./scripts/bash/flush-backlog.sh --no-summary

    # Archive and auto-commit changes
    ./scripts/bash/flush-backlog.sh --auto-commit

ENVIRONMENT VARIABLES:
    TRIGGER_SOURCE - Optional metadata for summary (e.g., "manual", "ci", "cron")

EOF
}

#######################################
# Print colored message
# Arguments:
#   $1 - color code
#   $2 - message
#######################################
print_color() {
    local color="$1"
    local message="$2"
    echo -e "${color}${message}${NC}"
}

#######################################
# Check prerequisites
# Returns:
#   0 if all prerequisites met, 1 otherwise
#######################################
check_prerequisites() {
    print_color "${BLUE}" "==> Checking prerequisites..."

    # Check if backlog CLI is installed
    if ! command -v backlog &> /dev/null; then
        print_color "${RED}" "ERROR: backlog CLI not found"
        print_color "${RED}" "Please install backlog.md: pnpm install -g @backlog-md/cli"
        return 1
    fi

    # Check if backlog directory exists
    if [[ ! -d "${PROJECT_ROOT}/${BACKLOG_DIR}" ]]; then
        print_color "${RED}" "ERROR: Backlog directory not found: ${BACKLOG_DIR}"
        return 1
    fi

    # Ensure archive directory exists
    mkdir -p "${PROJECT_ROOT}/${ARCHIVE_DIR}"

    print_color "${GREEN}" "✓ Prerequisites check passed"
    return 0
}

#######################################
# Get list of Done task IDs
# Outputs:
#   Task IDs, one per line
# Returns:
#   0 if successful, 1 otherwise
#######################################
get_done_tasks() {
    local output
    local task_ids=()

    # Query Done tasks
    output=$(cd "${PROJECT_ROOT}" && backlog task list -s Done --plain 2>&1) || {
        print_color "${RED}" "ERROR: Failed to query Done tasks"
        return 1
    }

    # Parse task IDs from output
    # Format: "  [HIGH] task-67 - Title" or "  task-013 - Title"
    while IFS= read -r line; do
        # Skip empty lines and section headers
        [[ -z "$line" || "$line" == "Done:" ]] && continue

        # Extract task ID using regex
        if [[ "$line" =~ [[:space:]]*(task-[0-9]+) ]]; then
            task_ids+=("${BASH_REMATCH[1]}")
        fi
    done <<< "$output"

    # Output task IDs (only if array is not empty)
    if [[ ${#task_ids[@]} -gt 0 ]]; then
        printf '%s\n' "${task_ids[@]}"
    fi
}

#######################################
# Archive a single task
# Arguments:
#   $1 - task ID (e.g., "task-67")
# Returns:
#   0 if successful, 1 otherwise
#######################################
archive_task() {
    local task_id="$1"
    # Extract numeric ID for backlog CLI (task-67 -> 67)
    local numeric_id="${task_id#task-}"

    if [[ "$DRY_RUN" == true ]]; then
        print_color "${YELLOW}" "  [DRY RUN] Would archive: ${task_id}"
        return 0
    fi

    # Archive the task using numeric ID
    local output
    if output=$(cd "${PROJECT_ROOT}" && backlog task archive "${numeric_id}" 2>&1); then
        if [[ "$output" =~ [Aa]rchived ]]; then
            print_color "${GREEN}" "  ✓ Archived: ${task_id}"
            ((TOTAL_ARCHIVED++))
            return 0
        fi
    fi

    print_color "${RED}" "  ✗ Failed to archive: ${task_id}"
    FAILED_TASKS+=("${task_id}")
    return 1
}

#######################################
# Get task metadata for summary
# Arguments:
#   $1 - task ID
# Outputs:
#   Task metadata in plain text format
#######################################
get_task_metadata() {
    local task_id="$1"
    local archive_tasks_dir="${PROJECT_ROOT}/${ARCHIVE_DIR}/tasks"

    # Find the archived task file
    local task_file
    task_file=$(find "$archive_tasks_dir" -maxdepth 1 -name "${task_id} - *.md" -type f 2>/dev/null | head -1)

    if [[ -z "$task_file" || ! -f "$task_file" ]]; then
        echo "ERROR: Archived task file not found for ${task_id}"
        return 1
    fi

    # Read the task file and extract metadata
    local content
    content=$(cat "$task_file")

    # Extract title from filename
    local title
    title=$(basename "$task_file" .md | sed "s/^${task_id} - //")

    # Extract fields from YAML frontmatter
    local priority assignee labels status
    priority=$(echo "$content" | grep -E "^priority:" | sed 's/^priority:[[:space:]]*//' | head -1)
    assignee=$(echo "$content" | grep -E "^assignee:" | sed 's/^assignee:[[:space:]]*//' | head -1)
    labels=$(echo "$content" | grep -E "^labels:" | sed 's/^labels:[[:space:]]*//' | head -1)
    status=$(echo "$content" | grep -E "^status:" | sed 's/^status:[[:space:]]*//' | head -1)

    # Format labels (remove brackets)
    labels=$(echo "$labels" | tr -d '[]' | sed 's/,/, /g')

    # Output in a parseable format
    cat <<EOF
Task ${task_id} - ${title}
Status: ${status:-Done}
Priority: ${priority:-None}
Assignee: ${assignee:-None}
Labels: ${labels:-None}

${content}
EOF
}

#######################################
# Extract field value from task metadata
# Arguments:
#   $1 - field name (e.g., "Priority", "Assignee")
#   $2 - task metadata text
# Outputs:
#   Field value or "None"
#######################################
extract_field() {
    local field="$1"
    local metadata="$2"
    local value

    value=$(echo "$metadata" | grep -E "^${field}:" | sed -E "s/^${field}:[[:space:]]*//" | head -1)

    if [[ -z "$value" || "$value" == "None" ]]; then
        echo "None"
    else
        echo "$value"
    fi
}

#######################################
# Count completed acceptance criteria
# Arguments:
#   $1 - task metadata text
# Outputs:
#   Format: "X/Y completed"
#######################################
count_acceptance_criteria() {
    local metadata="$1"
    local total=0
    local completed=0

    # Count [x] and [ ] checkboxes
    completed=$(echo "$metadata" | grep -cE '^\s*- \[x\]' || echo 0)
    total=$(echo "$metadata" | grep -cE '^\s*- \[[x ]\]' || echo 0)

    if [[ $total -eq 0 ]]; then
        echo "None"
    else
        echo "${completed}/${total} completed"
    fi
}

#######################################
# Generate flush summary report
# Arguments:
#   $1 - array of archived task IDs
#######################################
generate_summary() {
    local -n task_ids_ref=$1
    local timestamp
    local summary_file
    local trigger_source="${TRIGGER_SOURCE:-manual}"

    timestamp=$(date +"%Y-%m-%d-%H%M%S")
    summary_file="${PROJECT_ROOT}/${ARCHIVE_DIR}/flush-${timestamp}.md"

    print_color "${BLUE}" "==> Generating flush summary..."

    # Start building summary
    cat > "$summary_file" <<EOF
# Backlog Flush Summary

**Date:** $(date +"%Y-%m-%d %H:%M:%S")
**Archived Tasks:** ${#task_ids_ref[@]}
**Trigger Source:** ${trigger_source}

---

## Archived Tasks

EOF

    # Collect statistics
    local -A priority_counts
    local -A label_counts

    # Add details for each task
    for task_id in "${task_ids_ref[@]}"; do
        local metadata
        metadata=$(get_task_metadata "$task_id")

        local title
        title=$(echo "$metadata" | grep -E "^Task ${task_id}" | sed -E "s/^Task ${task_id} - //")

        local priority
        priority=$(extract_field "Priority" "$metadata")

        local assignee
        assignee=$(extract_field "Assignee" "$metadata")

        local labels
        labels=$(extract_field "Labels" "$metadata")

        local ac_status
        ac_status=$(count_acceptance_criteria "$metadata")

        # Update statistics
        priority_counts["$priority"]=$((${priority_counts["$priority"]:-0} + 1))

        # Parse labels for statistics
        if [[ "$labels" != "None" ]]; then
            IFS=',' read -ra label_array <<< "$labels"
            for label in "${label_array[@]}"; do
                label=$(echo "$label" | xargs) # trim whitespace
                label_counts["$label"]=$((${label_counts["$label"]:-0} + 1))
            done
        fi

        # Write task details
        cat >> "$summary_file" <<EOF
### ${task_id}: ${title}

- **Priority:** ${priority}
- **Assignee:** ${assignee}
- **Labels:** ${labels}
- **Acceptance Criteria:** ${ac_status}

EOF
    done

    # Add statistics section
    cat >> "$summary_file" <<EOF
---

## Statistics

### Total Archived
- **Count:** ${#task_ids_ref[@]}

### By Priority
EOF

    for priority in High Medium Low None; do
        local count="${priority_counts[$priority]:-0}"
        if [[ $count -gt 0 ]]; then
            echo "- **${priority}:** ${count}" >> "$summary_file"
        fi
    done

    cat >> "$summary_file" <<EOF

### Common Labels
EOF

    if [[ -z "${!label_counts[*]:-}" ]]; then
        echo "- None" >> "$summary_file"
    else
        # Sort labels by count (descending)
        for label in "${!label_counts[@]}"; do
            echo "${label_counts[$label]} $label"
        done | sort -rn | head -10 | while read -r count label; do
            echo "- **${label}:** ${count}" >> "$summary_file"
        done
    fi

    cat >> "$summary_file" <<EOF

---

*Generated by flush-backlog.sh*
EOF

    print_color "${GREEN}" "✓ Summary saved to: ${summary_file}"
}

#######################################
# Main function
#######################################
main() {
    local task_ids=()

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --no-summary)
                NO_SUMMARY=true
                shift
                ;;
            --auto-commit)
                AUTO_COMMIT=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                print_color "${RED}" "ERROR: Unknown option: $1"
                echo ""
                show_help
                exit 1
                ;;
        esac
    done

    # Check prerequisites
    if ! check_prerequisites; then
        exit 1
    fi

    # Get Done tasks
    print_color "${BLUE}" "==> Querying Done tasks..."
    mapfile -t task_ids < <(get_done_tasks)

    if [[ ${#task_ids[@]} -eq 0 ]]; then
        print_color "${YELLOW}" "No Done tasks to archive."
        exit 2
    fi

    print_color "${GREEN}" "Found ${#task_ids[@]} Done task(s)"

    if [[ "$DRY_RUN" == true ]]; then
        print_color "${YELLOW}" "==> DRY RUN MODE - No changes will be made"
    fi

    # Archive tasks
    print_color "${BLUE}" "==> Archiving tasks..."
    for task_id in "${task_ids[@]}"; do
        archive_task "$task_id" || true  # Continue even if one fails
    done

    # Report results
    echo ""
    if [[ "$DRY_RUN" == true ]]; then
        print_color "${YELLOW}" "==> DRY RUN completed"
        print_color "${YELLOW}" "Would archive ${#task_ids[@]} task(s)"
        exit 0
    fi

    if [[ ${#FAILED_TASKS[@]} -gt 0 ]]; then
        print_color "${RED}" "==> Completed with errors"
        print_color "${RED}" "Successfully archived: ${TOTAL_ARCHIVED}"
        print_color "${RED}" "Failed to archive: ${#FAILED_TASKS[@]} (${FAILED_TASKS[*]})"
        exit_code=3
    else
        print_color "${GREEN}" "==> Successfully archived ${TOTAL_ARCHIVED} task(s)"
        exit_code=0
    fi

    # Generate summary unless disabled
    if [[ "$NO_SUMMARY" == false ]]; then
        # Use original task_ids list for summary (before archival)
        generate_summary task_ids
    fi

    # Auto-commit if requested
    if [[ "$AUTO_COMMIT" == true && "$DRY_RUN" == false ]]; then
        print_color "${BLUE}" "==> Auto-committing changes..."
        cd "${PROJECT_ROOT}"

        if git diff --quiet && git diff --cached --quiet; then
            print_color "${YELLOW}" "No changes to commit"
        else
            git add "${BACKLOG_DIR}"
            git commit -m "chore(backlog): flush ${TOTAL_ARCHIVED} Done tasks to archive

Archived tasks: ${task_ids[*]}

Signed-off-by: flush-backlog.sh <noreply@backlog.md>"
            print_color "${GREEN}" "✓ Changes committed"
        fi
    fi

    exit $exit_code
}

# Run main function
main "$@"
