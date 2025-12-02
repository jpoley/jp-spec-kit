#!/usr/bin/env bash
# JP Spec Kit - Custom Statusline for Claude Code
# Format: [Phase] task-ID (N/M) | branch*
#
# Example output: [Impl] task-188 (2/5) | feature-auth*

set -euo pipefail

# Exit early if not in a git repo
git rev-parse --git-dir >/dev/null 2>&1 || exit 0

# Get git branch with dirty indicator
# Checks: staged changes, unstaged changes, untracked files
get_git_info() {
    local branch
    branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null) || return 1

    # Check for any uncommitted changes
    if ! git diff-index --quiet HEAD -- 2>/dev/null || \
       [[ -n "$(git ls-files --others --exclude-standard 2>/dev/null | head -1)" ]]; then
        printf '%s*' "$branch"
    else
        printf '%s' "$branch"
    fi
}

# Get task ID, phase, and AC progress
# Returns: phase|task_id|checked|total (pipe-delimited)
get_task_data() {
    command -v backlog >/dev/null 2>&1 || return 1

    # Parse backlog output - format is "  [PRIORITY] task-XXX - Title"
    local task_line task_id
    task_line=$(backlog task list --plain -s "In Progress" 2>/dev/null | grep -E '^\s*\[' | head -1)
    [[ -z "$task_line" ]] && return 1

    # Extract task ID (e.g., "task-188")
    task_id=$(printf '%s' "$task_line" | grep -oE 'task-[0-9]+')
    [[ -z "$task_id" ]] && return 1

    local details
    details=$(backlog task "$task_id" --plain 2>/dev/null)
    [[ -z "$details" ]] && return 1

    # Extract workflow label - handle labels with spaces correctly
    local phase=""
    local labels_line
    labels_line=$(printf '%s' "$details" | grep "^Labels:" | cut -d: -f2-)

    if [[ -n "$labels_line" ]]; then
        # Parse comma-separated labels, handling spaces within label values
        local IFS=','
        for label in $labels_line; do
            # Trim whitespace and quotes from label
            label=$(printf '%s' "$label" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | tr -d '"'"'")

            if [[ "$label" == workflow:* ]]; then
                local state="${label#workflow:}"
                case "$state" in
                    "To Do"|"Assessed")     phase="Assess" ;;
                    "Specified")            phase="Specify" ;;
                    "Researched")           phase="Research" ;;
                    "Planned")              phase="Plan" ;;
                    "In Implementation")    phase="Impl" ;;
                    "Validated")            phase="Valid" ;;
                    "Deployed")             phase="Deploy" ;;
                    "Done")                 phase="Done" ;;
                    *)                      phase="${state:0:8}" ;;
                esac
                break
            fi
        done
    fi

    # Count acceptance criteria (grep -c returns exit 1 with 0 matches)
    local checked total
    checked=$(printf '%s' "$details" | { grep -cE '^\- \[x\]' || true; })
    total=$(printf '%s' "$details" | { grep -cE '^\- \[[ x]\]' || true; })

    # Return pipe-delimited data
    printf '%s|%s|%s|%s' "$phase" "$task_id" "$checked" "$total"
}

# Main - assemble statusline
main() {
    local output=""

    # Get task data (phase, task_id, checked, total)
    local task_data phase task_id checked total
    if task_data=$(get_task_data 2>/dev/null); then
        IFS='|' read -r phase task_id checked total <<< "$task_data"

        # Add phase if present
        [[ -n "$phase" ]] && output="[$phase]"

        # Add task with AC progress
        if [[ -n "$task_id" ]]; then
            if [[ "$total" -gt 0 ]]; then
                output="${output:+$output }${task_id} (${checked}/${total})"
            else
                output="${output:+$output }${task_id}"
            fi
        fi
    fi

    # Get git info
    local git_info
    if git_info=$(get_git_info 2>/dev/null); then
        output="${output:+$output | }${git_info}"
    fi

    printf '%s\n' "$output"
}

main
