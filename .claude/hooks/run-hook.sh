#!/usr/bin/env bash
#
# Hook wrapper: Ensures hooks always run from project root
#
# Usage: run-hook.sh <command> [args...]
#
# This wrapper:
# - Finds the project root (directory containing .claude/)
# - Changes to project root before executing command
# - Preserves command exit code
# - Provides better error messages
#

set -euo pipefail

# Find project root by looking for .claude directory
find_project_root() {
    local current_dir="$PWD"
    local max_depth=10
    local depth=0

    while [[ "$depth" -lt "$max_depth" ]]; do
        if [[ -d "$current_dir/.claude" ]]; then
            echo "$current_dir"
            return 0
        fi

        # Move up one directory
        local parent_dir="$(dirname "$current_dir")"
        if [[ "$parent_dir" == "$current_dir" ]]; then
            # Reached filesystem root
            break
        fi
        current_dir="$parent_dir"
        ((depth++))
    done

    # Fallback: try to find .claude relative to this script
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [[ -d "$script_dir/../.." ]] && [[ -d "$script_dir/../../.claude" ]]; then
        cd "$script_dir/../.." && pwd
        return 0
    fi

    echo "ERROR: Could not find project root (no .claude directory found)" >&2
    return 1
}

# Check if command provided
if [[ $# -lt 1 ]]; then
    echo "ERROR: No command specified" >&2
    echo "Usage: run-hook.sh <command> [args...]" >&2
    exit 1
fi

# Find and change to project root
PROJECT_ROOT="$(find_project_root)"
if [[ -z "$PROJECT_ROOT" ]]; then
    echo "ERROR: Could not determine project root" >&2
    exit 1
fi

cd "$PROJECT_ROOT" || {
    echo "ERROR: Could not change to project root: $PROJECT_ROOT" >&2
    exit 1
}

# Execute command with all arguments from project root
exec "$@"
