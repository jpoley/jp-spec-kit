"""Task schema migration utilities for upgrading Backlog.md tasks from v1 to v2."""

import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import yaml


class MigrationError(Exception):
    """Base exception for migration errors."""
    pass


class TaskMigrator:
    """
    Migrate task files from schema v1 to v2.

    Schema v2 adds optional fields:
    - upstream: sync metadata (provider, id, url, synced_at, etag)
    - compliance: audit trail (spec_version, spec_ref, pr_url, audit_trail)
    - schema_version: version identifier

    All migrations are atomic with backup files created before modification.
    """

    CURRENT_VERSION = "2"
    FRONTMATTER_PATTERN = re.compile(
        r'^---\s*\n(.*?)\n---\s*\n(.*)$',
        re.DOTALL
    )

    def __init__(self, dry_run: bool = False):
        """
        Initialize migrator.

        Args:
            dry_run: If True, only report what would change without modifying files
        """
        self.dry_run = dry_run
        self.results = {
            "migrated": 0,
            "skipped": 0,
            "errors": 0,
            "backed_up": 0
        }
        self.migration_log: List[Dict[str, str]] = []

    def migrate(self, task_path: Path) -> bool:
        """
        Migrate a single task to current schema version.

        Args:
            task_path: Path to task markdown file

        Returns:
            True if migration was performed, False if skipped

        Raises:
            MigrationError: If migration fails
        """
        if not task_path.exists():
            raise MigrationError(f"Task file not found: {task_path}")

        if not task_path.is_file():
            raise MigrationError(f"Not a file: {task_path}")

        # Parse current frontmatter and body
        try:
            frontmatter, body = self._parse_frontmatter(task_path)
        except Exception as e:
            raise MigrationError(f"Failed to parse {task_path}: {e}") from e

        # Check current schema version
        current_version = str(frontmatter.get("schema_version", "1"))

        if self._version_gte(current_version, self.CURRENT_VERSION):
            self._log_migration(task_path, "skipped", f"Already at v{current_version}")
            return False

        # Perform migration
        migrated_frontmatter = self._migrate_v1_to_v2(frontmatter)

        # Create backup and write new version
        if not self.dry_run:
            try:
                self._backup_file(task_path)
                self._write_task(task_path, migrated_frontmatter, body)
                self._verify_migration(task_path, migrated_frontmatter)
            except Exception as e:
                # Restore from backup on failure
                self._restore_backup(task_path)
                raise MigrationError(f"Migration failed for {task_path}: {e}") from e

        self._log_migration(
            task_path,
            "migrated" if not self.dry_run else "would_migrate",
            f"v{current_version} → v{self.CURRENT_VERSION}"
        )
        return True

    def migrate_bulk(self, tasks_dir: Path) -> Dict[str, int]:
        """
        Migrate all tasks in a directory.

        Args:
            tasks_dir: Directory containing task files

        Returns:
            Dictionary with migration statistics
        """
        if not tasks_dir.exists():
            raise MigrationError(f"Tasks directory not found: {tasks_dir}")

        if not tasks_dir.is_dir():
            raise MigrationError(f"Not a directory: {tasks_dir}")

        # Reset results
        self.results = {"migrated": 0, "skipped": 0, "errors": 0, "backed_up": 0}
        self.migration_log = []

        # Find all task files
        task_files = sorted(tasks_dir.glob("task-*.md"))

        if not task_files:
            self._log_migration(tasks_dir, "warning", "No task files found")
            return self.results

        # Migrate each task
        for task_file in task_files:
            try:
                if self.migrate(task_file):
                    self.results["migrated"] += 1
                else:
                    self.results["skipped"] += 1
            except MigrationError as e:
                self.results["errors"] += 1
                self._log_migration(task_file, "error", str(e))

        return self.results

    def get_migration_report(self) -> str:
        """
        Generate a human-readable migration report.

        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 60)
        lines.append("Task Schema Migration Report")
        lines.append("=" * 60)
        lines.append("")

        if self.dry_run:
            lines.append("DRY RUN MODE - No files were modified")
            lines.append("")

        lines.append("Summary:")
        lines.append(f"  Migrated: {self.results['migrated']}")
        lines.append(f"  Skipped:  {self.results['skipped']}")
        lines.append(f"  Errors:   {self.results['errors']}")
        lines.append(f"  Total:    {sum(self.results.values())}")
        lines.append("")

        if self.migration_log:
            lines.append("Details:")
            for entry in self.migration_log:
                status = entry["status"].upper()
                path = entry["path"]
                message = entry["message"]
                lines.append(f"  [{status}] {path}: {message}")

        lines.append("=" * 60)
        return "\n".join(lines)

    # Private methods

    def _parse_frontmatter(self, task_path: Path) -> Tuple[Dict, str]:
        """
        Parse YAML frontmatter and body from markdown file.

        Args:
            task_path: Path to task file

        Returns:
            Tuple of (frontmatter_dict, body_text)

        Raises:
            MigrationError: If parsing fails
        """
        content = task_path.read_text(encoding="utf-8")

        # Handle empty files
        if not content.strip():
            raise MigrationError("Empty file")

        # Match frontmatter pattern
        match = self.FRONTMATTER_PATTERN.match(content)
        if not match:
            raise MigrationError("No valid frontmatter found")

        frontmatter_text, body = match.groups()

        # Parse YAML
        try:
            frontmatter = yaml.safe_load(frontmatter_text)
            if frontmatter is None:
                frontmatter = {}
            if not isinstance(frontmatter, dict):
                raise MigrationError("Frontmatter is not a dictionary")
        except yaml.YAMLError as e:
            raise MigrationError(f"Invalid YAML: {e}") from e

        return frontmatter, body

    def _migrate_v1_to_v2(self, frontmatter: Dict) -> Dict:
        """
        Migrate frontmatter from v1 to v2.

        Changes:
        - Add schema_version field
        - Upstream and compliance blocks are optional, don't add unless needed

        Args:
            frontmatter: v1 frontmatter dictionary

        Returns:
            v2 frontmatter dictionary
        """
        # Create a copy to avoid mutating input
        migrated = frontmatter.copy()

        # Add schema version
        migrated["schema_version"] = self.CURRENT_VERSION

        # Don't add upstream/compliance blocks unless they're present
        # They're optional in v2

        return migrated

    def _write_task(self, task_path: Path, frontmatter: Dict, body: str) -> None:
        """
        Write frontmatter and body back to task file.

        Args:
            task_path: Path to task file
            frontmatter: Frontmatter dictionary
            body: Body text
        """
        # Serialize frontmatter to YAML
        yaml_text = yaml.dump(
            frontmatter,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False
        )

        # Construct full content
        content = f"---\n{yaml_text}---\n{body}"

        # Write to file
        task_path.write_text(content, encoding="utf-8")

    def _backup_file(self, task_path: Path) -> None:
        """
        Create backup of task file before migration.

        Args:
            task_path: Path to task file
        """
        backup_path = task_path.with_suffix(task_path.suffix + ".bak")
        shutil.copy2(task_path, backup_path)
        self.results["backed_up"] += 1
        self._log_migration(task_path, "backup", f"Created {backup_path.name}")

    def _restore_backup(self, task_path: Path) -> None:
        """
        Restore task file from backup.

        Args:
            task_path: Path to task file
        """
        backup_path = task_path.with_suffix(task_path.suffix + ".bak")
        if backup_path.exists():
            shutil.copy2(backup_path, task_path)
            self._log_migration(task_path, "restore", "Restored from backup")

    def _verify_migration(self, task_path: Path, expected_frontmatter: Dict) -> None:
        """
        Verify migration was successful.

        Args:
            task_path: Path to migrated task file
            expected_frontmatter: Expected frontmatter after migration

        Raises:
            MigrationError: If verification fails
        """
        try:
            actual_frontmatter, _ = self._parse_frontmatter(task_path)
        except Exception as e:
            raise MigrationError(f"Verification failed: {e}") from e

        # Check schema version
        if actual_frontmatter.get("schema_version") != expected_frontmatter.get("schema_version"):
            raise MigrationError("Schema version mismatch after migration")

        # Check all original fields are preserved
        for key, value in expected_frontmatter.items():
            if key not in actual_frontmatter:
                raise MigrationError(f"Field '{key}' missing after migration")

    def _cleanup_backups(self, tasks_dir: Path) -> int:
        """
        Remove backup files after successful migration.

        Args:
            tasks_dir: Directory containing task files

        Returns:
            Number of backup files removed
        """
        backup_files = list(tasks_dir.glob("task-*.md.bak"))
        count = 0
        for backup_file in backup_files:
            backup_file.unlink()
            count += 1
        return count

    def _version_gte(self, version1: str, version2: str) -> bool:
        """
        Compare version strings (greater than or equal).

        Args:
            version1: First version string
            version2: Second version string

        Returns:
            True if version1 >= version2
        """
        try:
            v1 = int(version1)
            v2 = int(version2)
            return v1 >= v2
        except ValueError:
            # Fallback to string comparison
            return version1 >= version2

    def _log_migration(self, path: Path, status: str, message: str) -> None:
        """
        Log migration event.

        Args:
            path: Path to file
            status: Status string (migrated, skipped, error, etc.)
            message: Log message
        """
        self.migration_log.append({
            "timestamp": datetime.now().isoformat(),
            "path": str(path),
            "status": status,
            "message": message
        })


def cleanup_backups(tasks_dir: Path) -> int:
    """
    Utility function to clean up backup files after successful migration.

    Args:
        tasks_dir: Directory containing task files

    Returns:
        Number of backup files removed
    """
    migrator = TaskMigrator()
    return migrator._cleanup_backups(tasks_dir)


def migrate_tasks_cli(
    tasks_dir: str | Path,
    dry_run: bool = False,
    verbose: bool = False,
    cleanup: bool = False
) -> int:
    """
    CLI-friendly bulk migration function.

    Args:
        tasks_dir: Path to tasks directory (string or Path)
        dry_run: If True, only report what would change
        verbose: If True, print detailed output
        cleanup: If True, remove backup files after successful migration

    Returns:
        Exit code (0 for success, 1 for errors)
    """
    tasks_path = Path(tasks_dir)

    if not tasks_path.exists():
        print(f"Error: Directory not found: {tasks_path}")
        return 1

    migrator = TaskMigrator(dry_run=dry_run)

    if verbose:
        print(f"Migrating tasks in: {tasks_path}")
        if dry_run:
            print("DRY RUN MODE - No files will be modified")
        print()

    try:
        results = migrator.migrate_bulk(tasks_path)
    except Exception as e:
        print(f"Error during migration: {e}")
        return 1

    # Print report
    if verbose:
        print(migrator.get_migration_report())
    else:
        # Compact summary
        print(f"Migrated: {results['migrated']}")
        print(f"Skipped:  {results['skipped']}")
        print(f"Errors:   {results['errors']}")

    # Cleanup backups if requested and no errors
    if cleanup and not dry_run and results['errors'] == 0:
        count = cleanup_backups(tasks_path)
        if verbose:
            print(f"\nCleaned up {count} backup files")

    return 1 if results['errors'] > 0 else 0
