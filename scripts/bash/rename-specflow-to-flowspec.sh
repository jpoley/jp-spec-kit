#!/usr/bin/env bash
# Rename flowspec → flowspec across entire codebase
# Usage: ./scripts/bash/rename-flowspec-to-flowspec.sh [--dry-run]

set -e

DRY_RUN=false
if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN=true
    echo "=== DRY RUN MODE ==="
fi

echo "=== Phase 1: Rename files and directories ==="

# 1. Config files (already done, but include for completeness)
rename_file() {
    local old="$1"
    local new="$2"
    if [[ -e "$old" ]]; then
        if $DRY_RUN; then
            echo "Would rename: $old → $new"
        else
            git mv "$old" "$new" 2>/dev/null || mv "$old" "$new"
            echo "Renamed: $old → $new"
        fi
    fi
}

# Config files
rename_file "flowspec_workflow.yml" "flowspec_workflow.yml"
rename_file "schemas/flowspec_workflow.schema.json" "schemas/flowspec_workflow.schema.json"
rename_file "memory/flowspec_workflow.yml" "memory/flowspec_workflow.yml"
rename_file "memory/flowspec_workflow.schema.json" "memory/flowspec_workflow.schema.json"

# 2. Template commands directory
if [[ -d "templates/commands/flowspec" ]]; then
    if $DRY_RUN; then
        echo "Would rename: templates/commands/flowspec → templates/commands/flowspec"
    else
        git mv templates/commands/flowspec templates/commands/flowspec
        echo "Renamed: templates/commands/flowspec → templates/commands/flowspec"
    fi
fi

# 3. Symlink directory - delete and recreate
if [[ -d ".claude/commands/flowspec" ]]; then
    if $DRY_RUN; then
        echo "Would recreate symlinks: .claude/commands/flowspec → .claude/commands/flowspec"
    else
        rm -rf .claude/commands/flowspec
        mkdir -p .claude/commands/flowspec
        # Create new symlinks
        for file in templates/commands/flowspec/*.md; do
            ln -s "../../../$file" ".claude/commands/flowspec/$(basename "$file")"
        done
        echo "Recreated symlinks in .claude/commands/flowspec/"
    fi
fi

# 4. GitHub agents
echo ""
echo "=== Renaming GitHub agents ==="
for f in .github/agents/flowspec-*.agent.md; do
    if [[ -e "$f" ]]; then
        newname="${f//flowspec-/flowspec-}"
        rename_file "$f" "$newname"
    fi
done

# 5. GitHub prompts
echo ""
echo "=== Renaming GitHub prompts ==="
for f in .github/prompts/flowspec.*.prompt.md .github/prompts/flowspec.*.prompt.md; do
    if [[ -e "$f" ]]; then
        newname="${f//flowspec./flowspec.}"
        rename_file "$f" "$newname"
    fi
done

# 6. Test files
echo ""
echo "=== Renaming test files ==="
for f in tests/test_flowspec_*.py; do
    if [[ -e "$f" ]]; then
        newname="${f//test_flowspec_/test_flowspec_}"
        rename_file "$f" "$newname"
    fi
done

# 7. Doc files with flowspec in name
echo ""
echo "=== Renaming doc files ==="
find docs -name "*flowspec*" -type f 2>/dev/null | while read f; do
    newname="${f//flowspec/flowspec}"
    rename_file "$f" "$newname"
done

echo ""
echo "=== Phase 2: Content replacements ==="

# Function to do sed replacement
do_replace() {
    local pattern="$1"
    local replacement="$2"
    local files="$3"

    if $DRY_RUN; then
        echo "Would replace: $pattern → $replacement in $files files"
        return
    fi

    # macOS compatible sed
    if [[ "$(uname)" == "Darwin" ]]; then
        find . -type f \( -name "*.py" -o -name "*.md" -o -name "*.yml" -o -name "*.yaml" -o -name "*.json" -o -name "*.sh" \) \
            ! -path "./.git/*" ! -path "./.venv/*" ! -path "./node_modules/*" \
            -exec sed -i '' "s|$pattern|$replacement|g" {} +
    else
        find . -type f \( -name "*.py" -o -name "*.md" -o -name "*.yml" -o -name "*.yaml" -o -name "*.json" -o -name "*.sh" \) \
            ! -path "./.git/*" ! -path "./.venv/*" ! -path "./node_modules/*" \
            -exec sed -i "s|$pattern|$replacement|g" {} +
    fi
}

# Key replacements (order matters - more specific first)
echo "Replacing /flow: → /flow:"
do_replace "/flow:" "/flow:"

echo "Replacing flowspec_workflow → flowspec_workflow"
do_replace "flowspec_workflow" "flowspec_workflow"

echo "Replacing flowspec-workflow → flowspec-workflow"
do_replace "flowspec-workflow" "flowspec-workflow"

echo "Replacing flowspec → flowspec (general)"
do_replace "flowspec" "flowspec"

echo "Replacing Flowspec → Flowspec (capitalized)"
do_replace "Flowspec" "Flowspec"

echo "Replacing FLOWSPEC → FLOWSPEC (uppercase)"
do_replace "FLOWSPEC" "FLOWSPEC"

echo ""
echo "=== Phase 3: Verification ==="

# Count remaining references
remaining=$(grep -r "flowspec" --include="*.py" --include="*.md" --include="*.yml" --include="*.json" --include="*.sh" . 2>/dev/null | grep -v ".git" | grep -v "flowspec" | grep -v "rename-flowspec" | wc -l)
echo "Remaining 'flowspec' references (excluding script): $remaining"

if [[ $remaining -gt 0 ]]; then
    echo ""
    echo "Files still containing 'flowspec':"
    grep -rl "flowspec" --include="*.py" --include="*.md" --include="*.yml" --include="*.json" --include="*.sh" . 2>/dev/null | grep -v ".git" | grep -v "rename-flowspec" | head -20
fi

echo ""
echo "=== Done ==="
if $DRY_RUN; then
    echo "This was a dry run. Run without --dry-run to apply changes."
else
    echo "Rename complete. Run 'git status' to see changes."
    echo "Then run tests: uv run pytest tests/ -x -q"
fi
