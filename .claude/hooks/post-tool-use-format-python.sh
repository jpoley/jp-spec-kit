#!/bin/bash
#
# PostToolUse hook: Auto-format Python files
#
# Runs 'ruff format' on Python files after Edit/Write operations
# Returns JSON decision with formatting results
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
    echo '{"decision": "allow", "reason": "Tool not subject to auto-formatting"}'
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
    echo '{"decision": "allow", "reason": "ruff not installed (skipping format)"}'
    exit 0
fi

# Run ruff format
if ruff format "$file_path" 2>&1 | grep -q "reformatted"; then
    FILE_PATH="$file_path" python3 -c "import json, os; print(json.dumps({'decision': 'allow', 'reason': 'Auto-formatted Python file', 'additionalContext': f\"Ran 'ruff format' on {os.environ['FILE_PATH']}\"}))"
else
    echo '{"decision": "allow", "reason": "File already formatted or no changes needed"}'
fi

exit 0
