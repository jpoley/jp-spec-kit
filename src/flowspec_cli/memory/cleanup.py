"""Cleanup Manager - Archive and delete old task memories.

This module provides automated cleanup of task memory files based on age.
It supports both archiving old active memories and deleting old archived memories.

Cleanup operations support dry-run mode for safe testing and provide detailed
logging for audit trails.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

from .store import TaskMemoryStore

logger = logging.getLogger(__name__)


class CleanupManager:
    """Manages cleanup of task memory files.

    The CleanupManager provides automated cleanup operations for task memory:
    - Archive active memories older than a threshold
    - Delete archived memories older than a threshold
    - Provide statistics and dry-run capabilities

    Attributes:
        store: TaskMemoryStore instance for file operations
    """

    def __init__(self, store: Optional[TaskMemoryStore] = None):
        """Initialize cleanup manager.

        Args:
            store: Optional TaskMemoryStore instance. Creates default if not provided.
        """
        self.store = store or TaskMemoryStore()

    def archive_older_than(self, days: int, dry_run: bool = False) -> List[str]:
        """Archive active memories older than specified days.

        This method finds all active task memory files that haven't been
        modified in the specified number of days and archives them.

        Args:
            days: Age threshold in days (files older than this are archived)
            dry_run: If True, only report what would be archived without making changes

        Returns:
            List of task IDs that were (or would be) archived

        Example:
            >>> manager = CleanupManager()
            >>> # Archive memories older than 30 days
            >>> archived = manager.archive_older_than(30)
            >>> print(f"Archived {len(archived)} task memories")
        """
        threshold = datetime.now() - timedelta(days=days)
        archived_tasks = []

        active_tasks = self.store.list_active()

        for task_id in active_tasks:
            memory_path = self.store.get_path(task_id)

            # Get last modified time
            try:
                mtime = datetime.fromtimestamp(memory_path.stat().st_mtime)

                if mtime < threshold:
                    if dry_run:
                        logger.info(
                            f"[DRY RUN] Would archive {task_id} (last modified: {mtime})"
                        )
                    else:
                        self.store.archive(task_id)
                        logger.info(f"Archived {task_id} (last modified: {mtime})")

                    archived_tasks.append(task_id)
            except FileNotFoundError:
                logger.warning(f"Memory file not found during cleanup: {task_id}")
                continue

        return archived_tasks

    def delete_archived_older_than(self, days: int, dry_run: bool = False) -> List[str]:
        """Delete archived memories older than specified days.

        This method permanently deletes archived task memory files that
        haven't been modified in the specified number of days.

        Args:
            days: Age threshold in days (files older than this are deleted)
            dry_run: If True, only report what would be deleted without making changes

        Returns:
            List of task IDs that were (or would be) deleted

        Warning:
            This operation is permanent and cannot be undone. Use dry_run=True
            to preview what would be deleted before running for real.

        Example:
            >>> manager = CleanupManager()
            >>> # Preview what would be deleted
            >>> to_delete = manager.delete_archived_older_than(90, dry_run=True)
            >>> print(f"Would delete {len(to_delete)} archived memories")
            >>> # Actually delete after review
            >>> deleted = manager.delete_archived_older_than(90)
        """
        threshold = datetime.now() - timedelta(days=days)
        deleted_tasks = []

        archived_tasks = self.store.list_archived()

        for task_id in archived_tasks:
            archive_path = self.store.archive_dir / f"{task_id}.md"

            # Get last modified time
            try:
                mtime = datetime.fromtimestamp(archive_path.stat().st_mtime)

                if mtime < threshold:
                    if dry_run:
                        logger.info(
                            f"[DRY RUN] Would delete {task_id} (last modified: {mtime})"
                        )
                    else:
                        self.store.delete(task_id, from_archive=True)
                        logger.info(
                            f"Deleted archived memory {task_id} (last modified: {mtime})"
                        )

                    deleted_tasks.append(task_id)
            except FileNotFoundError:
                logger.warning(
                    f"Archived memory file not found during cleanup: {task_id}"
                )
                continue

        return deleted_tasks

    def get_stats(self) -> Dict[str, int]:
        """Get cleanup statistics.

        Provides counts of active and archived task memories, along with
        age information for determining cleanup thresholds.

        Returns:
            Dictionary containing:
                - active_count: Number of active task memories
                - archived_count: Number of archived task memories
                - oldest_active_days: Age in days of oldest active memory
                - oldest_archived_days: Age in days of oldest archived memory

        Example:
            >>> manager = CleanupManager()
            >>> stats = manager.get_stats()
            >>> print(f"Active: {stats['active_count']}, Archived: {stats['archived_count']}")
        """
        now = datetime.now()

        # Get active memories
        active_tasks = self.store.list_active()
        active_count = len(active_tasks)

        oldest_active_days = 0
        if active_tasks:
            oldest_active_mtime = min(
                datetime.fromtimestamp(self.store.get_path(task_id).stat().st_mtime)
                for task_id in active_tasks
                if self.store.get_path(task_id).exists()
            )
            oldest_active_days = (now - oldest_active_mtime).days

        # Get archived memories
        archived_tasks = self.store.list_archived()
        archived_count = len(archived_tasks)

        oldest_archived_days = 0
        if archived_tasks:
            oldest_archived_mtime = min(
                datetime.fromtimestamp(
                    (self.store.archive_dir / f"{task_id}.md").stat().st_mtime
                )
                for task_id in archived_tasks
                if (self.store.archive_dir / f"{task_id}.md").exists()
            )
            oldest_archived_days = (now - oldest_archived_mtime).days

        return {
            "active_count": active_count,
            "archived_count": archived_count,
            "oldest_active_days": oldest_active_days,
            "oldest_archived_days": oldest_archived_days,
        }

    def cleanup_all(
        self,
        archive_after_days: int = 30,
        delete_after_days: int = 90,
        dry_run: bool = False,
    ) -> Dict[str, List[str]]:
        """Run full cleanup: archive old active, delete old archived.

        This is a convenience method that runs both archive and delete
        operations in a single call.

        Args:
            archive_after_days: Archive active memories older than this
            delete_after_days: Delete archived memories older than this
            dry_run: If True, only report what would be done

        Returns:
            Dictionary with 'archived' and 'deleted' keys containing task IDs

        Example:
            >>> manager = CleanupManager()
            >>> # Preview cleanup
            >>> result = manager.cleanup_all(archive_after_days=30, delete_after_days=90, dry_run=True)
            >>> print(f"Would archive: {len(result['archived'])}, delete: {len(result['deleted'])}")
            >>> # Run for real
            >>> result = manager.cleanup_all(archive_after_days=30, delete_after_days=90)
        """
        archived = self.archive_older_than(archive_after_days, dry_run=dry_run)
        deleted = self.delete_archived_older_than(delete_after_days, dry_run=dry_run)

        return {
            "archived": archived,
            "deleted": deleted,
        }
