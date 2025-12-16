#!/bin/bash
# aggregate-progress.sh - Aggregate agent progress to a central summary file
#
# This hook aggregates agent.* events to track multi-machine progress.
# Place in .specify/hooks/aggregate-progress.sh
#
# Configuration in hooks.yaml:
#   - name: aggregate-progress
#     events:
#       - pattern: "agent.*"
#     script: aggregate-progress.sh
#     enabled: true
#
# Dependencies: jq, flock (util-linux)
# Install: apt-get install jq util-linux (Debian/Ubuntu)
#          brew install jq (macOS - flock is built-in)
#
set -e

# Parse event data from HOOK_EVENT environment variable
EVENT_TYPE=$(echo "$HOOK_EVENT" | jq -r '.event_type')
AGENT_ID=$(echo "$HOOK_EVENT" | jq -r '.context.agent_id // "unknown"')
MACHINE=$(echo "$HOOK_EVENT" | jq -r '.context.machine // "unknown"')
TASK_ID=$(echo "$HOOK_EVENT" | jq -r '.context.task_id // "none"')
PROGRESS=$(echo "$HOOK_EVENT" | jq -r '.context.progress_percent // "n/a"')
MESSAGE=$(echo "$HOOK_EVENT" | jq -r '.context.status_message // ""')
FEATURE=$(echo "$HOOK_EVENT" | jq -r '.feature // "unknown"')
TIMESTAMP=$(echo "$HOOK_EVENT" | jq -r '.timestamp')

# Determine project root from trusted source (current working directory)
# Do not trust event-provided paths to prevent path traversal attacks
PROJECT_ROOT="$PWD"
SUMMARY_FILE="$PROJECT_ROOT/.specify/hooks/progress-summary.log"

# Create summary directory if needed
mkdir -p "$(dirname "$SUMMARY_FILE")"

# Format progress string
if [ "$PROGRESS" != "n/a" ]; then
    PROGRESS_STR="${PROGRESS}%"
else
    PROGRESS_STR="-"
fi

# Format log entry
LOG_ENTRY="[$TIMESTAMP] $MACHINE: $EVENT_TYPE | agent=$AGENT_ID | task=$TASK_ID | feature=$FEATURE | progress=$PROGRESS_STR"
if [ -n "$MESSAGE" ]; then
    LOG_ENTRY="$LOG_ENTRY | $MESSAGE"
fi

# Use flock to ensure atomic append and truncate operations
LOCK_FILE="$SUMMARY_FILE.lock"
(
    flock -x 200
    echo "$LOG_ENTRY" >> "$SUMMARY_FILE"
    # Keep only last 100 entries to prevent unbounded growth
    if [ -f "$SUMMARY_FILE" ]; then
        tail -100 "$SUMMARY_FILE" > "$SUMMARY_FILE.tmp" && mv "$SUMMARY_FILE.tmp" "$SUMMARY_FILE"
    fi
) 200>"$LOCK_FILE"

# Optional: Print to stdout for debugging
echo "Logged: $EVENT_TYPE from $MACHINE"
