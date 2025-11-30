#!/usr/bin/env python3
"""
PreToolUse hook: Git command safety validator

Warns on dangerous Git commands:
- git push --force / -f
- git reset --hard
- git rebase -i
- git clean -fd
- git push origin +branch (force push syntax)

Returns JSON decision: allow or ask for confirmation
"""

import json
import re
import sys


DANGEROUS_GIT_PATTERNS = [
    (r"git\s+push.*--force", "Force push can overwrite remote history"),
    (r"git\s+push.*\s+-f\b", "Force push can overwrite remote history"),
    (
        r"git\s+push.*\s+\+\w+",
        "Force push syntax (+branch) can overwrite remote history",
    ),
    (r"git\s+reset\s+--hard", "Hard reset will discard uncommitted changes"),
    (r"git\s+rebase\s+-i", "Interactive rebase requires manual input (not supported)"),
    (
        r"git\s+clean\s+(-[a-z]*f[a-z]*d[a-z]*|-[a-z]*d[a-z]*f[a-z]*|--force.*--directory|--directory.*--force)",
        "git clean with -f and -d will delete untracked files permanently",
    ),
]


def check_git_safety(command: str) -> tuple[bool, str, str]:
    """
    Check if git command is potentially dangerous.

    Returns:
        (is_dangerous, reason, additional_context) tuple
    """
    command_lower = command.lower().strip()

    # Only check git commands
    if not command_lower.startswith("git "):
        return False, "", ""

    # Check each dangerous pattern
    for pattern, reason in DANGEROUS_GIT_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            additional_context = f"Command: {command}\n\n"
            additional_context += f"Warning: {reason}\n\n"

            # Special guidance for interactive rebase
            if "rebase -i" in command_lower:
                additional_context += (
                    "Interactive commands are not supported in Claude Code. "
                )
                additional_context += "Consider using non-interactive alternatives."

            # Special guidance for force push to main/master
            if re.search(r"(push.*--force|push.*-f|push.*\+)", command, re.IGNORECASE):
                if re.search(r"(main|master)", command, re.IGNORECASE):
                    return (
                        True,
                        "Force push to main/master branch detected",
                        additional_context
                        + "\n\nForce pushing to main/master is highly discouraged.",
                    )

            return True, reason, additional_context

    return False, "", ""


def main():
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        # Only check Bash tool
        if tool_name != "Bash":
            print(
                json.dumps(
                    {
                        "decision": "allow",
                        "reason": f"Tool {tool_name} not subject to Git safety checks",
                    }
                )
            )
            return 0

        # Get command from tool input
        command = tool_input.get("command", "")

        if not command:
            print(json.dumps({"decision": "allow", "reason": "No command specified"}))
            return 0

        # Check if command is dangerous
        is_dangerous, reason, additional_context = check_git_safety(command)

        if is_dangerous:
            # For interactive rebase, deny instead of ask
            if "rebase -i" in command.lower():
                print(
                    json.dumps(
                        {
                            "decision": "deny",
                            "reason": "Interactive commands not supported",
                            "additionalContext": additional_context,
                        }
                    )
                )
            else:
                print(
                    json.dumps(
                        {
                            "decision": "ask",
                            "reason": reason,
                            "additionalContext": additional_context,
                        }
                    )
                )
        else:
            print(json.dumps({"decision": "allow", "reason": "Git command is safe"}))

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
