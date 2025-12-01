#!/usr/bin/env bash
# Custom Statusline for JP Spec Kit
# Displays: [Phase] task-ID (N/M AC) | branch
# Performance target: < 100ms

set -euo pipefail

# Get current working directory
CWD="${PWD}"

# Initialize components
PHASE=""
TASK_INFO=""
GIT_INFO=""

# Get workflow phase (fast grep-based)
get_phase() {
    local wf="${CWD}/jpspec_workflow.yml"
    [[ -f "$wf" ]] || return
    local state=$(grep -m1 "^current_state:" "$wf" 2>/dev/null | awk '{print $2}' | tr -d '\"'"'" || echo "")
    [[ -z "$state" ]] && return
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

# Get active task info
get_task() {
    command -v backlog >/dev/null 2>&1 || return
    local task=$(backlog task list --plain -s "In Progress" 2>/dev/null | head -1 | awk '{print $1}' || echo "")
    [[ -z "$task" ]] && return
    local details=$(backlog task "$task" --plain 2>/dev/null || echo "")
    local checked=$(echo "$details" | grep -c "^\- \[x\]" 2>/dev/null || echo "0")
    local total=$(echo "$details" | grep -c "^\- \[[ x]\]" 2>/dev/null || echo "0")
    [[ "$total" -gt 0 ]] && echo "$task ($checked/$total)" || echo "$task"
}

# Get git branch
get_git() {
    git rev-parse --abbrev-ref HEAD 2>/dev/null || return
}

# Build status with timeouts
PHASE=$(timeout 0.03 bash -c "$(declare -f get_phase); CWD='$CWD'; get_phase" 2>/dev/null || echo "")
TASK_INFO=$(timeout 0.05 bash -c "$(declare -f get_task); get_task" 2>/dev/null || echo "")
GIT_INFO=$(timeout 0.02 bash -c "$(declare -f get_git); get_git" 2>/dev/null || echo "")

# Assemble output
PARTS=()
[[ -n "$PHASE" ]] && PARTS+=("[$PHASE]")
[[ -n "$TASK_INFO" ]] && PARTS+=("$TASK_INFO") || { [[ -d "${CWD}/backlog" ]] && PARTS+=("No task"); }
[[ -n "$GIT_INFO" ]] && { [[ ${#PARTS[@]} -gt 0 ]] && PARTS+=("|"); PARTS+=("$GIT_INFO"); }

[[ ${#PARTS[@]} -gt 0 ]] && printf "%s\n" "${PARTS[*]}" || echo ""
