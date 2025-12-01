#!/usr/bin/env python3
"""
Stop hook: Backlog task quality gate

Enforces quality gate before session ends when PR creation is detected:
- Detects PR creation intent in conversation context
- Checks for In Progress backlog tasks via CLI
- Blocks session end if incomplete tasks exist
- Follows fail-open principle for reliability

Returns JSON decision: continue (allow stop) or block with guidance
"""

import json
import re
import subprocess
import sys
from pathlib import Path


# PR creation patterns (case-insensitive)
PR_PATTERNS = [
    r"create\s+(a\s+)?pr\b",
    r"open\s+(a\s+)?pr\b",
    r"make\s+(a\s+)?pr\b",
    r"create\s+a?\s*pull\s+request",
    r"open\s+a?\s*pull\s+request",
    r"gh\s+pr\s+create",
    r"pull\s+request.*create",
    r"pr\s+create",
    r"let'?s\s+pr\b",
]


def detect_pr_intent(conversation_summary: str) -> bool:
    """
    Detect if conversation involves PR creation intent.

    Args:
        conversation_summary: Conversation context from Stop hook

    Returns:
        True if PR creation detected, False otherwise
    """
    if not conversation_summary:
        return False

    conversation_lower = conversation_summary.lower()

    for pattern in PR_PATTERNS:
        if re.search(pattern, conversation_lower):
            return True

    return False


def check_in_progress_tasks() -> list[dict]:
    """
    Check for In Progress tasks via backlog CLI.

    Returns:
        List of task dictionaries with 'id' and 'title' keys
        Empty list if no tasks or on error (fail-open)
    """
    try:
        # Run backlog CLI with 5 second timeout
        result = subprocess.run(
            ["backlog", "task", "list", "--plain", "-s", "In Progress"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=Path(__file__).parent.parent.parent,
        )

        if result.returncode != 0:
            # CLI error - fail open
            return []

        # Parse plain output
        # Format:
        #   In Progress:
        #     [HIGH] task-189 - Title here
        #     task-190 - Another title
        tasks = []
        if not result.stdout.strip():
            return []
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if not line or line == "No tasks found." or line.endswith(":"):
                continue

            # Remove priority prefix if present: [HIGH], [MEDIUM], [LOW]
            line = re.sub(r"^\[(HIGH|MEDIUM|LOW)\]\s+", "", line)

            # Parse task ID and title
            # Format: task-123 - Title here
            if line.startswith("task-"):
                parts = line.split(" - ", 1)
                if len(parts) == 2:
                    task_id = parts[0].strip()
                    title = parts[1].strip()
                    tasks.append({"id": task_id, "title": title})

        return tasks

    except subprocess.TimeoutExpired:
        # Timeout - fail open
        return []
    except FileNotFoundError:
        # CLI not available - fail open
        return []
    except Exception:
        # Any other error - fail open
        return []


def detect_force_or_skip(conversation_summary: str) -> bool:
    """
    Detect if user is requesting to force/skip the quality gate.

    Args:
        conversation_summary: Conversation context from Stop hook

    Returns:
        True if force/skip detected, False otherwise
    """
    if not conversation_summary:
        return False

    conversation_lower = conversation_summary.lower()

    force_patterns = [
        r"\bforce\s+stop\b",
        r"\bskip\s+quality\s+gate\b",
        r"\bskip\s+check\b",
        r"\bbypass\s+quality\s+gate\b",
        r"\bignore\s+quality\s+gate\b",
    ]

    for pattern in force_patterns:
        if re.search(pattern, conversation_lower):
            return True

    return False


def main():
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        conversation_summary = input_data.get("conversationSummary", "")

        # Check for force/skip intent
        if detect_force_or_skip(conversation_summary):
            print(
                json.dumps(
                    {
                        "continue": True,
                        "systemMessage": "Quality gate bypassed as requested.",
                    }
                )
            )
            return 0

        # Check if PR creation is mentioned in conversation
        pr_detected = detect_pr_intent(conversation_summary)

        if not pr_detected:
            # No PR intent - allow stop
            print(
                json.dumps(
                    {
                        "continue": True,
                        "systemMessage": "No PR creation detected. Session can end.",
                    }
                )
            )
            return 0

        # PR detected - check for In Progress tasks
        in_progress_tasks = check_in_progress_tasks()

        if not in_progress_tasks:
            # No In Progress tasks or CLI error (fail-open) - allow stop
            print(
                json.dumps(
                    {
                        "continue": True,
                        "systemMessage": "No In Progress tasks found. Ready for PR creation.",
                    }
                )
            )
            return 0

        # In Progress tasks exist - block stop with guidance
        task_list = "\n".join(
            [f"  - {task['id']}: {task['title']}" for task in in_progress_tasks]
        )

        guidance = f"""Quality Gate: Incomplete Backlog Tasks Detected

You have {len(in_progress_tasks)} task(s) still marked as "In Progress":

{task_list}

Before creating a PR, please:

1. Complete all acceptance criteria for each task
2. Mark tasks as Done using:
   backlog task edit <task-id> -s Done --check-ac 1 --check-ac 2 ...

Or if work is incomplete:

1. Revert tasks to appropriate status
2. Create separate tasks for remaining work

To bypass this quality gate (not recommended):
- Use force stop or explicitly request to skip the quality gate

This ensures your backlog accurately reflects completed work.
"""

        print(
            json.dumps(
                {
                    "continue": False,
                    "stopReason": "incomplete_tasks",
                    "systemMessage": guidance,
                }
            )
        )
        return 0

    except json.JSONDecodeError:
        # Invalid JSON input - fail open
        print(
            json.dumps(
                {
                    "continue": True,
                    "systemMessage": "Hook error: Invalid JSON input (allowing stop)",
                }
            )
        )
        return 0
    except Exception as e:
        # On any error, default to "continue" to not break Claude's workflow
        print(
            json.dumps(
                {
                    "continue": True,
                    "systemMessage": f"Hook error (allowing stop): {str(e)}",
                }
            )
        )
        return 0


if __name__ == "__main__":
    sys.exit(main())
