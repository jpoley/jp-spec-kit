#!/usr/bin/env python3
"""Post-tool-use hook for task memory lifecycle management.

This hook intercepts 'backlog task edit' Bash commands and triggers
task memory lifecycle operations when task status changes are detected.

Hook Integration:
    - Type: PostToolUse
    - Triggers on: Bash tool with 'backlog task edit' command
    - Actions: Create/archive task memory based on status transitions

State Transitions:
    - To Do → In Progress: Create memory file
    - In Progress → Done: Archive memory file
    - Done → In Progress: Restore memory file from archive
"""

import json
import logging
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from flowspec_cli.memory.lifecycle import LifecycleManager  # noqa: E402

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_backlog_command(command: str) -> Optional[Dict[str, Any]]:
    """Parse backlog task edit command to extract status change information.

    Args:
        command: Full bash command string

    Returns:
        Dict with task_id, old_status, new_status if status change detected,
        None otherwise

    Example:
        >>> parse_backlog_command("backlog task edit 370 -s 'In Progress'")
        {'task_id': 'task-370', 'new_status': 'In Progress'}
    """
    # Pattern: backlog task edit <task-id> ... -s "status" or --status "status"
    task_edit_pattern = r"backlog\s+task\s+edit\s+(\d+|task-\d+)"
    status_pattern = r"(?:-s|--status)\s+['\"]?([^'\"]+)['\"]?"

    # Check if this is a task edit command
    task_match = re.search(task_edit_pattern, command)
    if not task_match:
        return None

    task_id = task_match.group(1)
    # Normalize to task-XXX format
    if not task_id.startswith("task-"):
        task_id = f"task-{task_id}"

    # Check for status change
    status_match = re.search(status_pattern, command)
    if not status_match:
        return None

    new_status = status_match.group(1)

    return {
        "task_id": task_id,
        "new_status": new_status,
    }


def infer_old_status(new_status: str, memory_exists: bool) -> Optional[str]:
    """Infer the previous status based on new status and memory state.

    Since PostToolUse runs AFTER the command, we can't get the true old status.
    Instead, we infer it based on:
    - The new target status
    - Whether a task memory file exists

    Args:
        new_status: The new status being set
        memory_exists: Whether task memory file exists

    Returns:
        Inferred old status for lifecycle management
    """
    new_lower = new_status.lower().strip()

    # Case 1: Moving to "In Progress"
    # - If memory exists, was probably already In Progress (no action needed)
    # - If no memory, was probably To Do (create memory)
    if new_lower == "in progress":
        return "To Do" if not memory_exists else "In Progress"

    # Case 2: Moving to "Done"
    # - If memory exists, was probably In Progress (archive memory)
    # - If no memory, was probably already Done or never started
    if new_lower == "done":
        return "In Progress" if memory_exists else "Done"

    # Case 3: Moving to "To Do"
    # - If memory exists, was probably In Progress (delete memory)
    # - If no memory, was probably already To Do
    if new_lower == "to do":
        return "In Progress" if memory_exists else "To Do"

    return None


def get_task_current_status(task_id: str) -> Optional[str]:
    """Get current status of a task (after the edit).

    Note: Since this runs in PostToolUse, this returns the NEW status.
    We use infer_old_status() instead to determine lifecycle actions.

    Args:
        task_id: Task identifier (e.g., "task-370")

    Returns:
        Current task status or None if task not found
    """
    try:
        result = subprocess.run(
            ["backlog", "task", task_id.replace("task-", ""), "--plain"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode != 0:
            logger.warning(f"Failed to get task status: {result.stderr}")
            return None

        # Parse status from output - looks for "Status: ..." line
        status_match = re.search(r"Status:\s*([^\n]+)", result.stdout)
        if status_match:
            status = status_match.group(1).strip()
            # Remove status icons (◯, ◒, ●)
            status = re.sub(r"^[◯◒●✔✓]", "", status).strip()
            return status

        return None

    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        logger.error(f"Error getting task status: {e}")
        return None


def get_task_title(task_id: str) -> str:
    """Get task title for memory file creation.

    Args:
        task_id: Task identifier

    Returns:
        Task title or empty string if not found
    """
    try:
        result = subprocess.run(
            ["backlog", "task", task_id.replace("task-", ""), "--plain"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode != 0:
            return ""

        # Parse title from output - looks for "Task task-XXX - <title>" line
        title_match = re.search(r"Task\s+task-\d+\s+-\s+(.+)", result.stdout)
        if title_match:
            return title_match.group(1).strip()

        return ""

    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        logger.error(f"Error getting task title: {e}")
        return ""


def main() -> None:
    """Main hook entry point.

    Reads tool use event from stdin, checks for backlog task edit with
    status change, and triggers lifecycle management if detected.

    Exit codes:
        0: Success (always - fail open)
    """
    try:
        # Read tool use event from stdin
        event_data = json.load(sys.stdin)

        tool_name = event_data.get("tool_name", "")
        tool_input = event_data.get("tool_input", {})

        # Only process Bash tool commands
        if tool_name != "Bash":
            logger.debug("Not a Bash command, skipping")
            return

        command = tool_input.get("command", "")
        if not command:
            logger.debug("Empty command, skipping")
            return

        # Parse the command
        parsed = parse_backlog_command(command)
        if not parsed:
            logger.debug("Not a backlog task edit with status change, skipping")
            return

        task_id = parsed["task_id"]
        new_status = parsed["new_status"]

        logger.info(f"Detected status change for {task_id} → {new_status}")

        # Check if memory exists to infer old status
        # Import here to avoid issues if flowspec_cli not installed
        from flowspec_cli.memory.store import TaskMemoryStore

        store = TaskMemoryStore()
        memory_exists = store.exists(task_id)

        # Infer old status based on new status and memory state
        old_status = infer_old_status(new_status, memory_exists)
        if old_status is None:
            logger.warning(
                f"Could not infer status transition for {task_id} → {new_status}"
            )
            return

        logger.info(
            f"Inferred transition: {old_status} → {new_status} (memory_exists={memory_exists})"
        )

        # Only trigger lifecycle if status actually changed
        if old_status.lower() == new_status.lower():
            logger.debug(
                "No lifecycle action needed (status unchanged or no memory impact)"
            )
            return

        # Get task title for memory creation
        task_title = get_task_title(task_id)

        # Trigger lifecycle manager
        manager = LifecycleManager()
        manager.on_state_change(task_id, old_status, new_status, task_title)

        logger.info(
            f"Task memory lifecycle hook completed for {task_id} ({old_status} → {new_status})"
        )

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse tool use event: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in lifecycle hook: {e}", exc_info=True)
    finally:
        # Always succeed - fail open to avoid breaking Claude workflow
        sys.exit(0)


if __name__ == "__main__":
    main()
