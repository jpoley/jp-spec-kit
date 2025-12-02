#!/usr/bin/env bash
# JP Spec Kit - Custom Statusline for Claude Code
# Format: [Phase] task-ID (N/M AC) | branch*
# Performance target: < 100ms total execution

set -euo pipefail

# Fast exit if not in a git repo
git rev-parse --git-dir >/dev/null 2>&1 || exit 0

# Get git branch with dirty indicator
get_git_info() {
    local branch
    branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null) || return

    # Check for uncommitted changes (staged, unstaged, or untracked)
    if ! git diff-index --quiet HEAD -- 2>/dev/null || \
       [[ -n "$(git ls-files --others --exclude-standard 2>/dev/null)" ]]; then
        echo "${branch}*"
    else
        echo "$branch"
    fi
}

# Get workflow phase from task labels
get_phase() {
    command -v backlog >/dev/null 2>&1 || return

    local task_id
    task_id=$(backlog task list --plain -s "In Progress" 2>/dev/null | head -1 | awk '{print $1}') || return
    [[ -z "$task_id" ]] && return

    local labels
    labels=$(backlog task "$task_id" --plain 2>/dev/null | grep "^Labels:" | cut -d: -f2-) || return

    # Extract workflow state from labels
    local state=""
    for label in $labels; do
        label=$(echo "$label" | xargs | tr -d ',')
        if [[ "$label" == workflow:* ]]; then
            state="${label#workflow:}"
            break
        fi
    done

    [[ -z "$state" ]] && return

    # Map to short display names
    case "$state" in
        "To Do"|"Assessed") echo "Assess" ;;
        "Specified") echo "Specify" ;;
        "Researched") echo "Research" ;;
        "Planned") echo "Plan" ;;
        "In Implementation") echo "Impl" ;;
        "Validated") echo "Valid" ;;
        "Deployed") echo "Deploy" ;;
        "Done") echo "Done" ;;
        *) echo "${state:0:8}" ;;
    esac
}

# Get active task with AC progress
get_task_info() {
    command -v backlog >/dev/null 2>&1 || return

    local task_id
    task_id=$(backlog task list --plain -s "In Progress" 2>/dev/null | head -1 | awk '{print $1}') || return
    [[ -z "$task_id" ]] && return

    local details
    details=$(backlog task "$task_id" --plain 2>/dev/null) || return

    # Count acceptance criteria
    local checked total
    checked=$(echo "$details" | grep -c '^\- \[x\]' 2>/dev/null || echo "0")
    total=$(echo "$details" | grep -c '^\- \[[ x]\]' 2>/dev/null || echo "0")

    if [[ "$total" -gt 0 ]]; then
        echo "$task_id ($checked/$total)"
    else
        echo "$task_id"
    fi
}

# Build statusline with timeouts for each component
PHASE=""
TASK=""
GIT=""

# Run with timeouts (use gtimeout on macOS if available, otherwise skip timeout)
if command -v gtimeout >/dev/null 2>&1; then
    TIMEOUT_CMD="gtimeout"
elif command -v timeout >/dev/null 2>&1; then
    TIMEOUT_CMD="timeout"
else
    TIMEOUT_CMD=""
fi

if [[ -n "$TIMEOUT_CMD" ]]; then
    PHASE=$($TIMEOUT_CMD 0.04s bash -c "$(declare -f get_phase); get_phase" 2>/dev/null || echo "")
    TASK=$($TIMEOUT_CMD 0.05s bash -c "$(declare -f get_task_info); get_task_info" 2>/dev/null || echo "")
    GIT=$($TIMEOUT_CMD 0.02s bash -c "$(declare -f get_git_info); get_git_info" 2>/dev/null || echo "")
else
    # No timeout available, run directly
    PHASE=$(get_phase 2>/dev/null || echo "")
    TASK=$(get_task_info 2>/dev/null || echo "")
    GIT=$(get_git_info 2>/dev/null || echo "")
fi

# Assemble output
OUTPUT=""

[[ -n "$PHASE" ]] && OUTPUT="[$PHASE]"
[[ -n "$TASK" ]] && OUTPUT="${OUTPUT:+$OUTPUT }$TASK"
[[ -n "$GIT" ]] && OUTPUT="${OUTPUT:+$OUTPUT | }$GIT"

# Output result (empty string if nothing to show)
echo "$OUTPUT"
