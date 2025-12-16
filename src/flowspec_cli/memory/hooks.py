"""Memory Hooks - CLI integration for task memory lifecycle.

This module provides hook functions that integrate task memory lifecycle
management with the backlog CLI. These hooks are called when task status
changes occur via CLI commands.

The hooks act as a bridge between the CLI command layer and the lifecycle
management layer, ensuring memory operations happen automatically on task
state transitions.
"""

from typing import Optional
import logging

from .lifecycle import LifecycleManager

logger = logging.getLogger(__name__)


def on_task_status_change(
    task_id: str, old_status: str, new_status: str, task_title: str = ""
) -> None:
    """Hook called when task status changes via CLI.

    This is the main integration point between the backlog CLI and the
    task memory lifecycle system. It should be called after any CLI command
    that changes a task's status.

    Args:
        task_id: Task identifier (e.g., "task-375")
        old_status: Previous task status
        new_status: New task status
        task_title: Optional task title for memory creation

    Example:
        >>> # In CLI command after updating task status
        >>> on_task_status_change("task-375", "To Do", "In Progress", "Implement feature")
        >>> # Memory file created automatically

    Note:
        This function handles all exceptions internally to avoid breaking
        CLI operations if memory operations fail. Errors are logged but
        do not propagate.
    """
    try:
        manager = LifecycleManager()
        manager.on_state_change(task_id, old_status, new_status, task_title)
        logger.debug(
            f"Task memory lifecycle hook executed: {task_id} ({old_status} → {new_status})"
        )
    except Exception as e:
        logger.error(f"Error in task memory lifecycle hook: {e}", exc_info=True)
        # Don't propagate exception - memory operations should not break CLI


def get_active_task_memory_path(task_id: str) -> Optional[str]:
    """Get the path to a task's active memory file.

    Utility function for CLI commands that need to reference or display
    the task memory file path.

    Args:
        task_id: Task identifier

    Returns:
        Absolute path to memory file as string, or None if not found

    Example:
        >>> path = get_active_task_memory_path("task-375")
        >>> if path:
        >>>     print(f"Memory file: {path}")
    """
    try:
        manager = LifecycleManager()
        memory_path = manager.store.get_path(task_id)
        if memory_path.exists():
            return str(memory_path.absolute())
        return None
    except Exception as e:
        logger.error(f"Error getting task memory path: {e}", exc_info=True)
        return None


def get_archived_task_memory_path(task_id: str) -> Optional[str]:
    """Get the path to a task's archived memory file.

    Utility function for CLI commands that need to reference archived
    memory files.

    Args:
        task_id: Task identifier

    Returns:
        Absolute path to archived memory file as string, or None if not found

    Example:
        >>> path = get_archived_task_memory_path("task-375")
        >>> if path:
        >>>     print(f"Archived memory: {path}")
    """
    try:
        manager = LifecycleManager()
        archive_path = manager.store.archive_dir / f"{task_id}.md"
        if archive_path.exists():
            return str(archive_path.absolute())
        return None
    except Exception as e:
        logger.error(f"Error getting archived memory path: {e}", exc_info=True)
        return None
