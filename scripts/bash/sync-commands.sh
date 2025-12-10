#!/usr/bin/env bash
# sync-commands.sh - Sync .claude/commands/ with templates/commands/
#
# This script copies command files from templates/commands/ to .claude/commands/
# to ensure they stay in sync. GitHub zipballs convert symlinks to text files,
# so we use real files instead.
#
# Usage:
#   ./scripts/bash/sync-commands.sh          # Sync all commands
#   ./scripts/bash/sync-commands.sh --check  # Check if in sync (CI mode)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

TEMPLATES_DIR="$PROJECT_ROOT/templates/commands"
CLAUDE_DIR="$PROJECT_ROOT/.claude/commands"

# Also sync skills
TEMPLATES_SKILLS_DIR="$PROJECT_ROOT/templates/skills"
CLAUDE_SKILLS_DIR="$PROJECT_ROOT/.claude/skills"

# Commands to sync (directories in templates/commands/)
COMMAND_DIRS=(arch dev ops pm qa sec specflow speckit)

# Skills to sync (directories in templates/skills/ that should be synced)
SKILL_DIRS=(constitution-checker)

check_mode=false
if [[ "${1:-}" == "--check" ]]; then
    check_mode=true
fi

errors=0

echo "Syncing commands from templates/commands/ to .claude/commands/"
echo "=============================================================="

for dir in "${COMMAND_DIRS[@]}"; do
    src="$TEMPLATES_DIR/$dir"
    dst="$CLAUDE_DIR/$dir"

    if [[ ! -d "$src" ]]; then
        echo "WARNING: Source directory $src does not exist, skipping"
        continue
    fi

    if $check_mode; then
        # Check mode - compare files
        if ! diff -rq "$src" "$dst" > /dev/null 2>&1; then
            echo "DRIFT DETECTED: $dir"
            diff -rq "$src" "$dst" || true
            ((errors++))
        else
            echo "OK: $dir"
        fi
    else
        # Sync mode - copy files
        rm -rf "$dst"
        cp -r "$src" "$dst"
        echo "Synced: $dir"
    fi
done

echo ""
echo "Syncing skills from templates/skills/ to .claude/skills/"
echo "========================================================"

for dir in "${SKILL_DIRS[@]}"; do
    src="$TEMPLATES_SKILLS_DIR/$dir"
    dst="$CLAUDE_SKILLS_DIR/$dir"

    if [[ ! -d "$src" ]]; then
        echo "WARNING: Source directory $src does not exist, skipping"
        continue
    fi

    if $check_mode; then
        # Check mode - compare files
        if ! diff -rq "$src" "$dst" > /dev/null 2>&1; then
            echo "DRIFT DETECTED: $dir"
            diff -rq "$src" "$dst" || true
            ((errors++))
        else
            echo "OK: $dir"
        fi
    else
        # Sync mode - copy files
        rm -rf "$dst"
        cp -r "$src" "$dst"
        echo "Synced: $dir"
    fi
done

echo ""

if $check_mode; then
    if [[ $errors -gt 0 ]]; then
        echo "FAILURE: $errors directories out of sync"
        echo ""
        echo "To fix, run: ./scripts/bash/sync-commands.sh"
        exit 1
    else
        echo "SUCCESS: All directories in sync"
        exit 0
    fi
else
    echo "Sync complete!"
    echo ""
    echo "Remember to commit the changes to .claude/commands/ and .claude/skills/"
fi
