#!/usr/bin/env bash
# pre-commit-agent-sync.sh - Auto-sync Claude commands to Copilot agents
#
# This script is designed to be called by git pre-commit hooks.
# It detects staged .claude/commands files, runs sync, and auto-stages results.
#
# Usage:
#   Called automatically by pre-commit framework
#   Or manually: ./scripts/bash/pre-commit-agent-sync.sh
#
# Exit codes:
#   0 - Success (sync completed or nothing to do)
#   1 - Sync failed

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors (disabled on non-tty)
if [ -t 1 ]; then
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'
else
    GREEN='' YELLOW='' BLUE='' NC=''
fi

log_info() { echo -e "${GREEN}[agent-sync]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[agent-sync]${NC} $*" >&2; }
log_debug() { echo -e "${BLUE}[agent-sync]${NC} $*"; }

# Check if command files are staged
check_staged_commands() {
    git diff --cached --name-only 2>/dev/null | \
        grep -qE '^\.claude/commands/.*\.md$|^templates/commands/.*\.md$'
}

# Main execution
main() {
    # Only run if command files are staged
    if ! check_staged_commands; then
        exit 0  # Nothing to do - exit silently
    fi

    log_info "Detected staged command files, syncing agents..."

    # List staged command files for context
    local staged_files
    staged_files=$(git diff --cached --name-only 2>/dev/null | \
        grep -E '^\.claude/commands/.*\.md$|^templates/commands/.*\.md$' || true)

    if [[ -n "$staged_files" ]]; then
        log_debug "Staged command files:"
        echo "$staged_files" | sed 's/^/  /'
    fi

    # Run the sync script
    if ! "$SCRIPT_DIR/sync-copilot-agents.sh" --force; then
        log_warn "Agent sync failed!"
        exit 1
    fi

    # Auto-stage generated agent files
    if [ -d "$PROJECT_ROOT/.github/agents" ]; then
        # Check if there are any changes to stage
        local changes
        changes=$(git status --porcelain -- "$PROJECT_ROOT/.github/agents/" 2>/dev/null || true)

        if [[ -n "$changes" ]]; then
            git add "$PROJECT_ROOT/.github/agents/"
            log_info "Auto-staged .github/agents/ files"
        fi
    fi

    # Show what was synced
    local synced_count
    synced_count=$(git diff --cached --name-only -- '.github/agents/' 2>/dev/null | wc -l)
    if [ "$synced_count" -gt 0 ]; then
        log_info "Synced $synced_count agent files:"
        git diff --cached --name-only -- '.github/agents/' | head -5 | sed 's/^/  /'
        if [ "$synced_count" -gt 5 ]; then
            log_info "  ... and $((synced_count - 5)) more"
        fi
    else
        log_info "Agent files already in sync"
    fi

    log_info "Agent sync complete"
}

main "$@"
