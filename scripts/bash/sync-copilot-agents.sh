#!/bin/bash
# Sync Claude Code commands to GitHub Copilot agents format
# Converts .claude/commands/{namespace}/*.md -> .github/agents/{namespace}.{command}.md
# Changes frontmatter: mode: agent -> mode: {namespace}:{command}
#
# Usage:
#   ./sync-copilot-agents.sh          # Sync files (default)
#   ./sync-copilot-agents.sh --check  # Check for drift without modifying (CI mode)

set -e

CLAUDE_DIR=".claude/commands"
COPILOT_DIR=".github/agents"
CHECK_MODE=false
DRIFT_FOUND=false

# Parse arguments
if [[ "$1" == "--check" ]]; then
    CHECK_MODE=true
fi

# Create target directory (skip in check mode)
if [[ "$CHECK_MODE" == false ]]; then
    mkdir -p "$COPILOT_DIR"
fi

# Track counts
converted=0
skipped=0
drifted=0

# Process each namespace (jpspec, speckit)
for namespace_dir in "$CLAUDE_DIR"/*/; do
    namespace=$(basename "$namespace_dir")

    # Skip if not a directory
    [[ ! -d "$namespace_dir" ]] && continue

    # Process each command file (skip underscore-prefixed files - they're includes)
    for cmd_file in "$namespace_dir"*.md; do
        [[ ! -f "$cmd_file" ]] && continue

        cmd_name=$(basename "$cmd_file" .md)

        # Skip underscore-prefixed files (includes/partials)
        if [[ "$cmd_name" == _* ]]; then
            ((skipped++))
            continue
        fi

        target_file="$COPILOT_DIR/${namespace}.${cmd_name}.md"
        mode_value="${namespace}:${cmd_name}"

        # Generate expected content
        expected_content=$(sed 's/^mode: agent$/mode: '"$mode_value"'/' "$cmd_file")

        if [[ "$CHECK_MODE" == true ]]; then
            # Check mode: compare with existing file
            if [[ ! -f "$target_file" ]]; then
                echo "❌ Missing: $target_file"
                DRIFT_FOUND=true
                ((drifted++))
            elif ! diff -q <(echo "$expected_content") "$target_file" > /dev/null 2>&1; then
                echo "❌ Drift detected: $target_file"
                DRIFT_FOUND=true
                ((drifted++))
            else
                ((converted++))
            fi
        else
            # Sync mode: write the file
            echo "$expected_content" > "$target_file"
            echo "✓ Converted: $cmd_file -> $target_file"
            ((converted++))
        fi
    done
done

echo ""

if [[ "$CHECK_MODE" == true ]]; then
    if [[ "$DRIFT_FOUND" == true ]]; then
        echo "❌ Sync check FAILED: $drifted files out of sync"
        echo ""
        echo "Run './scripts/bash/sync-copilot-agents.sh' to fix"
        exit 1
    else
        echo "✅ Sync check passed: $converted files in sync, $skipped partials skipped"
        exit 0
    fi
else
    echo "Sync complete: $converted files converted, $skipped partials skipped"
fi
