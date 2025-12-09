"""Lifecycle Manager - Orchestrates task memory operations on state changes.

This module provides the LifecycleManager class that hooks into task state
transitions and manages the lifecycle of task memory files. It automatically
creates, archives, restores, and deletes memory files based on task status changes.

State Transition Logic:
    To Do → In Progress: Create new memory file from template
    In Progress → Done: Archive memory file (task complete)
    Done → Archive: Delete memory file permanently
    Done → In Progress: Restore memory file from archive (task reopened)
    In Progress → To Do: Delete memory file (task reset)
"""

from pathlib import Path
from typing import Optional
import logging

from .store import TaskMemoryStore

logger = logging.getLogger(__name__)


class LifecycleManager:
    """Manages task memory lifecycle based on task state transitions.

    The LifecycleManager orchestrates all memory operations triggered by
    task status changes. It ensures memory files are created when work begins,
    archived when tasks complete, and cleaned up appropriately.

    Attributes:
        store: TaskMemoryStore instance for file operations
    """

    def __init__(self, store: Optional[TaskMemoryStore] = None):
        """Initialize lifecycle manager.

        Args:
            store: Optional TaskMemoryStore instance. Creates default if not provided.
        """
        self.store = store or TaskMemoryStore()

    def on_state_change(
        self, task_id: str, old_state: str, new_state: str, task_title: str = ""
    ) -> None:
        """Handle task state transition and manage memory accordingly.

        This is the main entry point for lifecycle management. It determines
        what memory operations to perform based on the state transition.

        Args:
            task_id: Task identifier (e.g., "task-375")
            old_state: Previous task state
            new_state: New task state
            task_title: Optional task title for memory creation

        State Transitions:
            - To Do → In Progress: Create memory
            - In Progress → Done: Archive memory
            - Done → Archive: Delete memory
            - Done → In Progress: Restore memory
            - In Progress → To Do: Delete memory
        """
        logger.info(f"Task {task_id} state change: {old_state} → {new_state}")

        # Normalize state names (handle variations)
        old_state = self._normalize_state(old_state)
        new_state = self._normalize_state(new_state)

        # Handle state transitions
        if old_state == "to_do" and new_state == "in_progress":
            self._on_task_start(task_id, task_title)
        elif old_state == "in_progress" and new_state == "done":
            self._on_task_complete(task_id)
        elif old_state == "done" and new_state == "archive":
            self._on_task_archive(task_id)
        elif old_state == "done" and new_state == "in_progress":
            self._on_task_reopen(task_id)
        elif old_state == "in_progress" and new_state == "to_do":
            self._on_task_reset(task_id)
        else:
            logger.debug(
                f"No memory operation for transition: {old_state} → {new_state}"
            )

        # Update CLAUDE.md import if task is now in progress
        if new_state == "in_progress":
            self.update_active_task_import(task_id)
        elif old_state == "in_progress" and new_state != "in_progress":
            # Task is no longer active, clear the import
            self.update_active_task_import(None)

    def _normalize_state(self, state: str) -> str:
        """Normalize state name to lowercase with underscores.

        Args:
            state: Raw state string (e.g., "In Progress", "To Do", "Done")

        Returns:
            Normalized state (e.g., "in_progress", "to_do", "done")
        """
        return state.lower().replace(" ", "_").replace("-", "_")

    def _on_task_start(self, task_id: str, task_title: str = "") -> Path:
        """Create memory when task transitions to In Progress.

        Args:
            task_id: Task identifier
            task_title: Optional task title for template substitution

        Returns:
            Path to the created memory file

        Raises:
            FileExistsError: If memory already exists (safe to ignore)
        """
        try:
            memory_path = self.store.create(
                task_id=task_id,
                template="default",
                task_title=task_title,
            )
            logger.info(f"Created task memory: {memory_path}")
            return memory_path
        except FileExistsError:
            logger.warning(
                f"Task memory already exists for {task_id}, skipping creation"
            )
            return self.store.get_path(task_id)

    def _on_task_complete(self, task_id: str) -> None:
        """Archive memory when task moves to Done.

        Args:
            task_id: Task identifier
        """
        try:
            self.store.archive(task_id)
            logger.info(f"Archived task memory: {task_id}")
        except FileNotFoundError:
            logger.warning(f"No memory to archive for {task_id}")

    def _on_task_archive(self, task_id: str) -> None:
        """Delete memory when task is archived.

        Args:
            task_id: Task identifier
        """
        try:
            self.store.delete(task_id, from_archive=True)
            logger.info(f"Deleted archived memory: {task_id}")
        except FileNotFoundError:
            logger.warning(f"No archived memory to delete for {task_id}")

    def _on_task_reopen(self, task_id: str) -> None:
        """Restore memory when task is reopened.

        Args:
            task_id: Task identifier
        """
        try:
            self.store.restore(task_id)
            logger.info(f"Restored task memory: {task_id}")
        except FileNotFoundError:
            logger.warning(f"No archived memory to restore for {task_id}")
        except FileExistsError:
            logger.warning(f"Active memory already exists for {task_id}")

    def _on_task_reset(self, task_id: str) -> None:
        """Delete memory when task is reset to To Do.

        Args:
            task_id: Task identifier
        """
        try:
            self.store.delete(task_id, from_archive=False)
            logger.info(f"Deleted task memory (reset): {task_id}")
        except FileNotFoundError:
            logger.warning(f"No memory to delete for {task_id}")

    def update_active_task_import(self, task_id: Optional[str] = None) -> None:
        """Update backlog/CLAUDE.md with current active task's @import.

        This method updates the CLAUDE.md file in the backlog directory to
        include an @import directive for the active task's memory file. This
        ensures agents have context about the current task.

        Args:
            task_id: Task ID to import, or None to clear the import
        """
        claude_md_path = self.store.base_path / "backlog" / "CLAUDE.md"

        # Create CLAUDE.md if it doesn't exist
        if not claude_md_path.exists():
            claude_md_path.parent.mkdir(parents=True, exist_ok=True)
            claude_md_path.write_text("# Backlog Context\n\n")

        content = claude_md_path.read_text()

        # Remove any existing task memory import
        lines = content.split("\n")
        filtered_lines = [
            line for line in lines if not line.startswith("@import memory/task-")
        ]

        # Add new import if task_id provided
        if task_id:
            # Find the position to insert (after header, before any other content)
            insert_pos = 0
            for i, line in enumerate(filtered_lines):
                if line.startswith("#"):
                    insert_pos = i + 1
                    # Skip any blank lines after header
                    while (
                        insert_pos < len(filtered_lines)
                        and not filtered_lines[insert_pos].strip()
                    ):
                        insert_pos += 1
                    break

            import_line = f"@import memory/{task_id}.md"
            filtered_lines.insert(insert_pos, import_line)
            filtered_lines.insert(insert_pos + 1, "")  # Add blank line after import

            logger.info(f"Updated CLAUDE.md with @import for {task_id}")
        else:
            logger.info("Cleared task memory @import from CLAUDE.md")

        # Write updated content
        new_content = "\n".join(filtered_lines)
        claude_md_path.write_text(new_content)
