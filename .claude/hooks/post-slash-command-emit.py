#!/usr/bin/env python3
"""PostToolUse hook: Auto-emit flowspec events when /flowspec commands complete.

This hook intercepts SlashCommand tool completions and emits corresponding
flowspec events to trigger user-configured hooks in .flowspec/hooks/.

Event Mapping:
    /flow:assess    → workflow.assessed
    /flow:specify   → spec.created
    /flow:research  → research.completed
    /flow:plan      → plan.created
    /flow:implement → implement.completed
    /flow:validate  → validate.completed
    /flow:operate   → deploy.completed

The hook operates in a fail-open mode - errors are logged but don't block workflow.
"""

import json
import re
import subprocess
import sys

# Event type mapping for /flowspec commands
COMMAND_EVENT_MAP = {
    "/flow:assess": "workflow.assessed",
    "/flow:specify": "spec.created",
    "/flow:research": "research.completed",
    "/flow:plan": "plan.created",
    "/flow:implement": "implement.completed",
    "/flow:validate": "validate.completed",
    "/flow:operate": "deploy.completed",
}


def allow(reason: str, context: str | None = None) -> None:
    """Output allow decision and exit."""
    result = {"decision": "allow", "reason": reason}
    if context:
        result["additionalContext"] = context
    print(json.dumps(result))
    sys.exit(0)


def extract_feature_id(text: str, is_command: bool = False) -> str | None:
    """Extract feature/spec ID from command arguments or output.

    Args:
        text: Text to search for feature ID
        is_command: If True, only match explicit flags (not "Feature:" patterns)

    Looks for patterns like:
    - --spec-id feature-name
    - spec: feature-name (output only)
    - feature: feature-name (output only)
    - Feature: feature-name (output only)
    """
    # Always check explicit flag first
    flag_match = re.search(r"--spec-id\s+(\S+)", text)
    if flag_match:
        return flag_match.group(1)

    # Only check output patterns if not parsing a command
    if not is_command:
        patterns = [
            r"spec:\s*([\w][\w.-]*[\w]|[\w]+)",
            r"[Ff]eature:\s*([\w][\w.-]*[\w]|[\w]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)

    return None


def extract_task_id(text: str) -> str | None:
    """Extract task ID from command arguments or output.

    Looks for patterns like:
    - task-123
    - --task-id task-123
    """
    patterns = [
        r"--task-id\s+(task-\d+)",
        r"\b(task-\d+)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None


def emit_event(
    event_type: str, feature_id: str | None, task_id: str | None
) -> tuple[bool, str]:
    """Call flowspec hooks emit to trigger user-configured hooks.

    Returns:
        Tuple of (success, message)
    """
    cmd = ["specify", "hooks", "emit", event_type]

    if feature_id:
        cmd.extend(["--spec-id", feature_id])
    if task_id:
        cmd.extend(["--task-id", task_id])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

        if result.returncode == 0:
            return True, f"Emitted {event_type} event"
        else:
            return False, f"Failed to emit event: {result.stderr}"

    except subprocess.TimeoutExpired:
        return False, "Event emission timed out"
    except FileNotFoundError:
        return False, "flowspec CLI not found"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def main():
    """Main entry point for the hook."""
    # Read JSON input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        allow("Invalid JSON input")
        return

    # Get tool name
    tool_name = input_data.get("tool_name", "")

    # Only process SlashCommand tool
    if tool_name != "SlashCommand":
        allow("Not a SlashCommand tool")
        return

    # Get command from tool_input
    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "")

    # Check if this is a /flowspec command
    flowspec_command = None
    for cmd_prefix in COMMAND_EVENT_MAP:
        if command.startswith(cmd_prefix):
            flowspec_command = cmd_prefix
            break

    if not flowspec_command:
        allow("Not a /flowspec command")
        return

    # Get event type
    event_type = COMMAND_EVENT_MAP[flowspec_command]

    # Extract feature and task IDs from command arguments (with is_command=True)
    feature_id = extract_feature_id(command, is_command=True)
    task_id = extract_task_id(command)

    # Also try to extract from tool output if available (is_command=False)
    tool_output = input_data.get("tool_output", "")
    if not feature_id:
        feature_id = extract_feature_id(tool_output, is_command=False)
    if not task_id:
        task_id = extract_task_id(tool_output)

    # Emit the event
    success, message = emit_event(event_type, feature_id, task_id)

    # Always allow (fail-open) but report results
    context_parts = [f"Command: {flowspec_command}", f"Event: {event_type}"]
    if feature_id:
        context_parts.append(f"Feature: {feature_id}")
    if task_id:
        context_parts.append(f"Task: {task_id}")
    context_parts.append(f"Emission: {'Success' if success else 'Failed'}")
    if not success:
        context_parts.append(f"Details: {message}")

    allow(message, "\n".join(context_parts))


if __name__ == "__main__":
    main()
