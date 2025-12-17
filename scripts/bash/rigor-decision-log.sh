#!/usr/bin/env bash
# rigor-decision-log.sh - Log decisions with task traceability
#
# Usage:
#   ./scripts/bash/rigor-decision-log.sh \
#     --task task-542 \
#     --phase execution \
#     --decision "Selected JSONL format" \
#     --rationale "Git-friendly, append-only" \
#     --actor "@backend-engineer" \
#     --alternatives "SQLite,Plain text"
#
# Environment:
#   DECISIONS_DIR - Override default memory/decisions directory

set -euo pipefail

# Default values
DECISIONS_DIR="${DECISIONS_DIR:-memory/decisions}"
TASK_ID=""
PHASE=""
DECISION=""
RATIONALE=""
ACTOR=""
ALTERNATIVES=""
FILES_AFFECTED=""
RELATED_TASKS=""
TAGS=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Log a decision with task traceability in JSONL format.

Required Options:
  --task TASK_ID        Task ID (e.g., task-542)
  --phase PHASE         Workflow phase: setup, execution, freeze, validation, pr
  --decision TEXT       What was decided
  --rationale TEXT      Why this decision was made
  --actor ACTOR         Who made the decision (e.g., @backend-engineer)

Optional:
  --alternatives CSV    Comma-separated alternatives considered
  --files CSV           Comma-separated files affected
  --related CSV         Comma-separated related task IDs
  --tags CSV            Comma-separated tags (e.g., architecture,security)
  --dir PATH            Override decisions directory (default: memory/decisions)
  -h, --help            Show this help message

Examples:
  $(basename "$0") --task task-542 --phase execution \\
    --decision "Use JSONL for logs" --rationale "Streaming-friendly" \\
    --actor "@platform-engineer" --alternatives "SQLite,YAML"

  $(basename "$0") --task task-100 --phase setup \\
    --decision "Split into 3 subtasks" --rationale "Better parallelization" \\
    --actor "@backend-engineer" --related "task-101,task-102,task-103"
EOF
    exit 1
}

log_error() {
    echo -e "${RED}ERROR:${NC} $1" >&2
}

log_success() {
    echo -e "${GREEN}SUCCESS:${NC} $1"
}

log_info() {
    echo -e "${YELLOW}INFO:${NC} $1"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --task)
            TASK_ID="$2"
            shift 2
            ;;
        --phase)
            PHASE="$2"
            shift 2
            ;;
        --decision)
            DECISION="$2"
            shift 2
            ;;
        --rationale)
            RATIONALE="$2"
            shift 2
            ;;
        --actor)
            ACTOR="$2"
            shift 2
            ;;
        --alternatives)
            ALTERNATIVES="$2"
            shift 2
            ;;
        --files)
            FILES_AFFECTED="$2"
            shift 2
            ;;
        --related)
            RELATED_TASKS="$2"
            shift 2
            ;;
        --tags)
            TAGS="$2"
            shift 2
            ;;
        --dir)
            DECISIONS_DIR="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            ;;
    esac
done

# Validate required fields
missing_fields=()
[[ -z "$TASK_ID" ]] && missing_fields+=("--task")
[[ -z "$PHASE" ]] && missing_fields+=("--phase")
[[ -z "$DECISION" ]] && missing_fields+=("--decision")
[[ -z "$RATIONALE" ]] && missing_fields+=("--rationale")
[[ -z "$ACTOR" ]] && missing_fields+=("--actor")

if [[ ${#missing_fields[@]} -gt 0 ]]; then
    log_error "Missing required fields: ${missing_fields[*]}"
    echo ""
    usage
fi

# Validate phase
valid_phases=("setup" "execution" "freeze" "validation" "pr")
if [[ ! " ${valid_phases[*]} " =~ " ${PHASE} " ]]; then
    log_error "Invalid phase: $PHASE"
    echo "Valid phases: ${valid_phases[*]}"
    exit 1
fi

# Ensure decisions directory exists
mkdir -p "$DECISIONS_DIR"

# Generate timestamp
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Build JSON object using jq for proper escaping
json_entry=$(jq -n \
    --arg timestamp "$TIMESTAMP" \
    --arg task_id "$TASK_ID" \
    --arg phase "$PHASE" \
    --arg decision "$DECISION" \
    --arg rationale "$RATIONALE" \
    --arg actor "$ACTOR" \
    --arg alternatives "$ALTERNATIVES" \
    --arg files "$FILES_AFFECTED" \
    --arg related "$RELATED_TASKS" \
    --arg tags "$TAGS" \
    '{
        timestamp: $timestamp,
        task_id: $task_id,
        phase: $phase,
        decision: $decision,
        rationale: $rationale,
        actor: $actor
    } + (if $alternatives != "" then {alternatives: ($alternatives | split(","))} else {} end)
      + (if ($files != "" or $related != "" or $tags != "") then {
          context: (
            {}
            + (if $files != "" then {files_affected: ($files | split(","))} else {} end)
            + (if $related != "" then {related_tasks: ($related | split(","))} else {} end)
            + (if $tags != "" then {tags: ($tags | split(","))} else {} end)
          )
        } else {} end)'
)

# Append to task's decision log
log_file="${DECISIONS_DIR}/${TASK_ID}.jsonl"
echo "$json_entry" >> "$log_file"

log_success "Decision logged to $log_file"
log_info "Entry: $(echo "$json_entry" | jq -c '.')"

# Show current decision count for task
count=$(wc -l < "$log_file")
log_info "Total decisions for $TASK_ID: $count"
