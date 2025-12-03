#!/usr/bin/env python3
"""PreToolUse hook: Auto-approve safe read operations.

This hook automatically approves Read operations in safe directories
to reduce friction for common documentation and task management operations.

Approved Directories:
- docs/           - Documentation files
- backlog/        - Task management files
- templates/      - Template files
- .specify/       - JP Spec Kit configuration

Also approves:
- Bash commands using the 'backlog' CLI tool

All other operations require normal approval flow.
"""

import json
import re
import sys

# Directories where Read is always safe
SAFE_READ_DIRECTORIES = [
    "docs/",
    "backlog/",
    "templates/",
    ".specify/",
    ".github/prompts/",  # GitHub prompts for slash commands
    "memory/",  # Memory/constitution files
]

# Bash command patterns that are safe to auto-approve
SAFE_BASH_PATTERNS = [
    r"^backlog\s+",  # Any backlog CLI command
    r"^specify\s+hooks\s+(list|audit|validate)",  # Read-only hooks commands
    r"^git\s+status",  # Git status is read-only
    r"^git\s+log\b",  # Git log is read-only
    r"^git\s+diff\b",  # Git diff is read-only
    r"^git\s+branch\s+--?(list|show)",  # Git branch listing
]


def allow(reason: str = "") -> None:
    """Output allow decision and exit."""
    result = {"decision": "allow"}
    if reason:
        result["reason"] = reason
    print(json.dumps(result))
    sys.exit(0)


def pass_through(reason: str = "") -> None:
    """Let the default permission flow handle this."""
    result = {"decision": "pass"}
    if reason:
        result["reason"] = reason
    print(json.dumps(result))
    sys.exit(0)


def is_safe_read_path(file_path: str) -> bool:
    """Check if the file path is in a safe directory for reading."""
    # Normalize path - remove leading ./ but keep leading . for hidden dirs
    normalized = file_path
    if normalized.startswith("./"):
        normalized = normalized[2:]
    normalized = normalized.lstrip("/")

    for safe_dir in SAFE_READ_DIRECTORIES:
        if normalized.startswith(safe_dir):
            return True

    return False


def is_safe_bash_command(command: str) -> bool:
    """Check if the bash command is safe to auto-approve."""
    # Trim and normalize command
    cmd = command.strip()

    for pattern in SAFE_BASH_PATTERNS:
        if re.match(pattern, cmd, re.IGNORECASE):
            return True

    return False


def main():
    """Main entry point for the hook."""
    # Read JSON input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        pass_through("Invalid JSON input")
        return

    # Get tool name and input
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Handle Read tool
    if tool_name == "Read":
        file_path = tool_input.get("file_path", "")
        if is_safe_read_path(file_path):
            allow(f"Auto-approved Read in safe directory: {file_path}")
            return

    # Handle Bash tool
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        if is_safe_bash_command(command):
            allow(f"Auto-approved safe command: {command}")
            return

    # Handle Glob tool in safe directories
    if tool_name == "Glob":
        path = tool_input.get("path", "")
        if path and is_safe_read_path(path):
            allow(f"Auto-approved Glob in safe directory: {path}")
            return

    # Handle Grep tool in safe directories
    if tool_name == "Grep":
        path = tool_input.get("path", "")
        if path and is_safe_read_path(path):
            allow(f"Auto-approved Grep in safe directory: {path}")
            return

    # Let everything else go through normal flow
    pass_through("Not a safe operation, using normal approval")


if __name__ == "__main__":
    main()
