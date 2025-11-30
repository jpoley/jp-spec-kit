#!/usr/bin/env python3
"""
PreToolUse hook: Sensitive file protection

Asks for confirmation when Claude attempts to modify sensitive files:
- .env files
- .secrets files
- package-lock.json
- uv.lock
- .git/ directory
- CLAUDE.md files

Returns JSON decision: allow, deny, or ask
"""

import json
import sys
from pathlib import Path


SENSITIVE_PATTERNS = [
    ".env",
    ".secrets",
    "package-lock.json",
    "uv.lock",
    ".git/",
    "CLAUDE.md",
]


def is_sensitive_file(file_path: str) -> tuple[bool, str]:
    """
    Check if file path matches sensitive patterns.

    Returns:
        (is_sensitive, reason) tuple
    """
    path = Path(file_path)

    # Check exact filename matches
    if path.name in [".env", ".secrets", "package-lock.json", "uv.lock", "CLAUDE.md"]:
        return True, f"Sensitive file: {path.name}"

    # Check if .git is a path component
    if ".git" in path.parts:
        return True, "Modifying .git/ directory"

    # Check for .env.* files
    if path.name.startswith(".env."):
        return True, f"Environment file: {path.name}"

    return False, ""


def main():
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        # Only check Write and Edit tools
        if tool_name not in ["Write", "Edit"]:
            print(
                json.dumps(
                    {
                        "decision": "allow",
                        "reason": f"Tool {tool_name} not subject to file protection",
                    }
                )
            )
            return 0

        # Get file path from tool input
        file_path = tool_input.get("file_path", "")

        if not file_path:
            print(json.dumps({"decision": "allow", "reason": "No file path specified"}))
            return 0

        # Check if file is sensitive
        is_sensitive, reason = is_sensitive_file(file_path)

        if is_sensitive:
            print(
                json.dumps(
                    {
                        "decision": "ask",
                        "reason": reason,
                        "additionalContext": f"Attempting to modify {file_path}. This file is typically auto-generated or contains sensitive data. Are you sure you want to proceed?",
                    }
                )
            )
        else:
            print(json.dumps({"decision": "allow", "reason": "File is not sensitive"}))

        return 0

    except Exception as e:
        # On error, default to "allow" to not break Claude's workflow
        print(
            json.dumps(
                {
                    "decision": "allow",
                    "reason": f"Hook error (defaulting to allow): {str(e)}",
                }
            )
        )
        return 0


if __name__ == "__main__":
    sys.exit(main())
