#!/bin/bash
# Sync Claude Code commands to GitHub Copilot agents format
# Converts .claude/commands/{namespace}/*.md -> .github/agents/{namespace}.{command}.md
# Changes frontmatter: mode: agent -> mode: {namespace}:{command}

set -e

CLAUDE_DIR=".claude/commands"
COPILOT_DIR=".github/agents"

# Create target directory
mkdir -p "$COPILOT_DIR"

# Track counts
converted=0
skipped=0

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
        
        # Convert the file: change mode: agent -> mode: {namespace}:{command}
        sed 's/^mode: agent$/mode: '"$mode_value"'/' "$cmd_file" > "$target_file"
        
        echo "✓ Converted: $cmd_file -> $target_file"
        ((converted++))
    done
done

echo ""
echo "Sync complete: $converted files converted, $skipped partials skipped"
