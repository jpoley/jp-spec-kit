#!/bin/bash
#
# PostToolUse hook: Auto-lint Python files
#
# Runs 'ruff check --fix' on Python files after Edit/Write operations
# Returns JSON decision with linting results
#

set -euo pipefail

# Read JSON input from stdin
input=$(cat)

# Extract tool name and file path using jq if available, otherwise use Python
if command -v jq &> /dev/null; then
    tool_name=$(echo "$input" | jq -r '.tool_name // ""')
    file_path=$(echo "$input" | jq -r '.tool_input.file_path // ""')
else
    # Fallback to Python for JSON parsing (separate calls to handle spaces in paths)
    tool_name=$(echo "$input" | python3 -c "import json, sys; data = json.load(sys.stdin); print(data.get('tool_name', ''))")
    file_path=$(echo "$input" | python3 -c "import json, sys; data = json.load(sys.stdin); print(data.get('tool_input', {}).get('file_path', ''))")
fi

# Only process Write and Edit tools
if [[ "$tool_name" != "Write" && "$tool_name" != "Edit" ]]; then
    echo '{"decision": "allow", "reason": "Tool not subject to auto-linting"}'
    exit 0
fi

# Check if file is a Python file
if [[ ! "$file_path" =~ \.py$ ]]; then
    echo '{"decision": "allow", "reason": "Not a Python file"}'
    exit 0
fi

# Check if file exists
if [[ ! -f "$file_path" ]]; then
    echo '{"decision": "allow", "reason": "File does not exist"}'
    exit 0
fi

# Check if ruff is available
if ! command -v ruff &> /dev/null; then
    echo '{"decision": "allow", "reason": "ruff not installed (skipping lint)"}'
    exit 0
fi

# Run ruff check with auto-fix
if output=$(ruff check --fix "$file_path" 2>&1); then
    if echo "$output" | grep -q "fixed"; then
        FILE_PATH="$file_path" python3 -c "import json, os; print(json.dumps({'decision': 'allow', 'reason': 'Auto-fixed linting issues', 'additionalContext': f\"Ran 'ruff check --fix' on {os.environ['FILE_PATH']}\"}))"
    else
        echo '{"decision": "allow", "reason": "No linting issues found or fixed"}'
    fi
else
    # ruff check returns non-zero if there are unfixable issues
    if echo "$output" | grep -q "fixed"; then
        echo "$output" | python3 -c "import json, sys; print(json.dumps({'decision': 'allow', 'reason': 'Auto-fixed some issues (manual fixes may be needed)', 'additionalContext': sys.stdin.read()}))"
    else
        echo "$output" | python3 -c "import json, sys; print(json.dumps({'decision': 'allow', 'reason': 'Linting issues detected (may require manual fixes)', 'additionalContext': sys.stdin.read()}))"
    fi
fi

exit 0
