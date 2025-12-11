#!/bin/bash
# Git post-commit hook to emit flowspec events for backlog task changes
#
# This hook runs after each git commit and:
# 1. Detects changes to backlog/tasks/*.md files
# 2. Parses task files to detect status changes, AC changes, etc.
# 3. Emits corresponding flowspec events via `specify hooks emit`
#
# Installation:
#   ln -sf ../../scripts/hooks/post-commit-backlog-events.sh .git/hooks/post-commit
#
# Requirements:
#   - specify CLI installed (uv tool install specify-cli)
#   - Git repository
#   - Backlog task files in backlog/tasks/

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get project root (git repo root)
PROJECT_ROOT=$(git rev-parse --show-toplevel)

# Check if specify is available
if ! command -v specify &> /dev/null; then
    echo -e "${YELLOW}[post-commit-backlog-events] specify CLI not found, skipping event emission${NC}" >&2
    exit 0
fi

# Get changed files in this commit
# For initial commit, compare against empty tree
if git rev-parse HEAD~1 &> /dev/null; then
    CHANGED_FILES=$(git diff --name-only HEAD~1 HEAD)
else
    # Initial commit - compare against empty tree
    CHANGED_FILES=$(git diff --name-only 4b825dc642cb6eb9a060e54bf8d69288fbee4904 HEAD)
fi

# Filter for backlog task files
TASK_FILES=$(echo "$CHANGED_FILES" | grep -E '^backlog/tasks/task-.*\.md$' || true)

if [ -z "$TASK_FILES" ]; then
    # No task files changed
    exit 0
fi

# Counter for emitted events
EVENTS_EMITTED=0

# Process each changed task file
while IFS= read -r file; do
    [ -z "$file" ] && continue

    # Extract task ID from filename
    # Format: backlog/tasks/task-123.md or task-123 - Title.md
    BASENAME=$(basename "$file" .md)
    TASK_ID=$(echo "$BASENAME" | sed -E 's/^(task-[0-9.]+)( - .*)?$/\1/')

    if [ -z "$TASK_ID" ]; then
        echo -e "${YELLOW}[post-commit-backlog-events] Could not extract task ID from: $file${NC}" >&2
        continue
    fi

    # Check if this is a new file (added in this commit)
    # Try to get the file from HEAD~1 - if it doesn't exist, this is a new file
    if ! git cat-file -e "HEAD~1:$file" 2>/dev/null; then
        # New task created (file didn't exist in previous commit)
        echo -e "${GREEN}[post-commit-backlog-events] New task detected: $TASK_ID (file=$file, HEAD~1 check failed)${NC}" >&2
        specify hooks emit task.created --task-id "$TASK_ID" --project-root "$PROJECT_ROOT" 2>&1 | sed 's/^/  /'
        EVENTS_EMITTED=$((EVENTS_EMITTED + 1))
        continue
    else
        echo -e "[post-commit-backlog-events] File $file exists in HEAD~1, checking for modifications..." >&2
    fi

    # File was modified - check for status changes and AC changes
    TASK_PATH="$PROJECT_ROOT/$file"

    if [ ! -f "$TASK_PATH" ]; then
        # File was deleted
        continue
    fi

    # Parse current task status from YAML frontmatter
    CURRENT_STATUS=$(sed -n '/^---$/,/^---$/p' "$TASK_PATH" | grep '^status:' | sed 's/^status: *//' | tr -d '"' || echo "")

    # Get previous version of file
    PREV_CONTENT=$(git show HEAD~1:"$file" 2>/dev/null || echo "")

    if [ -n "$PREV_CONTENT" ]; then
        # Extract previous status
        PREV_STATUS=$(echo "$PREV_CONTENT" | sed -n '/^---$/,/^---$/p' | grep '^status:' | sed 's/^status: *//' | tr -d '"' || echo "")

        # Check if status changed
        if [ "$CURRENT_STATUS" != "$PREV_STATUS" ]; then
            echo -e "${GREEN}[post-commit-backlog-events] Status change detected for $TASK_ID: $PREV_STATUS → $CURRENT_STATUS${NC}" >&2

            # Emit task.status_changed
            specify hooks emit task.status_changed --task-id "$TASK_ID" --project-root "$PROJECT_ROOT" 2>&1 | sed 's/^/  /'
            EVENTS_EMITTED=$((EVENTS_EMITTED + 1))

            # Also emit task.completed if status is Done
            if [ "$CURRENT_STATUS" = "Done" ] || [ "$CURRENT_STATUS" = "○ Done" ]; then
                echo -e "${GREEN}[post-commit-backlog-events] Task completed: $TASK_ID${NC}" >&2
                specify hooks emit task.completed --task-id "$TASK_ID" --project-root "$PROJECT_ROOT" 2>&1 | sed 's/^/  /'
                EVENTS_EMITTED=$((EVENTS_EMITTED + 1))
            fi
        fi

        # Check for AC checkbox changes
        # Extract AC section from current file
        CURRENT_ACS=$(sed -n '/^## Acceptance Criteria/,/^##/p' "$TASK_PATH" | grep -E '^\- \[(x| )\] #[0-9]+' || echo "")
        PREV_ACS=$(echo "$PREV_CONTENT" | sed -n '/^## Acceptance Criteria/,/^##/p' | grep -E '^\- \[(x| )\] #[0-9]+' || echo "")

        # Compare checkbox states
        if [ "$CURRENT_ACS" != "$PREV_ACS" ]; then
            # Count checked boxes in current and previous
            # Note: grep -c returns 0 (count) but exits 1 when no match, which would trigger || echo "0"
            # causing "0\n0". Use a subshell to capture only the count.
            CURRENT_CHECKED=$(echo "$CURRENT_ACS" | grep -c '^\- \[x\]' 2>/dev/null || true)
            PREV_CHECKED=$(echo "$PREV_ACS" | grep -c '^\- \[x\]' 2>/dev/null || true)
            # Ensure we have valid integers (empty becomes 0)
            CURRENT_CHECKED=${CURRENT_CHECKED:-0}
            PREV_CHECKED=${PREV_CHECKED:-0}

            if [ "$CURRENT_CHECKED" -gt "$PREV_CHECKED" ]; then
                # AC was checked
                echo -e "${GREEN}[post-commit-backlog-events] AC checked for $TASK_ID${NC}" >&2
                specify hooks emit task.ac_checked --task-id "$TASK_ID" --project-root "$PROJECT_ROOT" 2>&1 | sed 's/^/  /'
                EVENTS_EMITTED=$((EVENTS_EMITTED + 1))
            elif [ "$CURRENT_CHECKED" -lt "$PREV_CHECKED" ]; then
                # AC was unchecked
                echo -e "${GREEN}[post-commit-backlog-events] AC unchecked for $TASK_ID${NC}" >&2
                # Note: Using task.ac_checked for both check and uncheck since the event exists
                # A more complete implementation would have task.ac_unchecked
                specify hooks emit task.ac_checked --task-id "$TASK_ID" --project-root "$PROJECT_ROOT" 2>&1 | sed 's/^/  /'
                EVENTS_EMITTED=$((EVENTS_EMITTED + 1))
            fi
        fi
    fi

done <<< "$TASK_FILES"

if [ "$EVENTS_EMITTED" -gt 0 ]; then
    echo -e "${GREEN}[post-commit-backlog-events] Emitted $EVENTS_EMITTED event(s)${NC}" >&2
fi

exit 0
