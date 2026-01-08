"""Deprecated file and directory cleanup for upgrade operations.

This module provides functionality to detect and remove deprecated files and
directories during repository upgrades. It ensures proper backups are created
before removal and provides detailed reporting to users.
"""

from dataclasses import dataclass, field
from pathlib import Path
import logging
import shutil

logger = logging.getLogger(__name__)

# Deprecated directories that should be removed during upgrade
DEPRECATED_DIRECTORIES = [
    ".specify",  # Legacy directory, replaced by .flowspec/
]

# Deprecated file patterns that should be removed during upgrade
# These patterns are searched in common command locations
DEPRECATED_FILE_PATTERNS = [
    "_DEPRECATED_*.md",  # Deprecated command files
]

# Deprecated file patterns specifically for .github/agents/
# These patterns identify files that should be REMOVED during upgrade:
# 1. Hyphenated agent files (old naming convention before ADR-001)
# 2. Legacy spec.* patterns from older versions
DEPRECATED_GITHUB_AGENT_PATTERNS = [
    "flow-*.agent.md",  # Old: flow-specify.agent.md -> flow.specify.agent.md
    "spec.*.agent.md",  # Legacy spec agent files
    "spec-*.agent.md",  # Legacy hyphenated spec agent files
]


@dataclass
class DeprecatedCleanupResult:
    """Result of a deprecated files/directories cleanup operation.

    Attributes:
        directories_removed: List of directories that were removed
        files_removed: List of files that were removed
        directories_backed_up: Map of removed directories to their backup paths
        files_backed_up: Map of removed files to their backup paths
        errors: List of error messages encountered during cleanup
    """

    directories_removed: list[str] = field(default_factory=list)
    files_removed: list[str] = field(default_factory=list)
    directories_backed_up: dict[str, Path] = field(default_factory=dict)
    files_backed_up: dict[str, Path] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        """Check if any cleanup was performed."""
        return bool(self.directories_removed or self.files_removed)

    @property
    def total_removed(self) -> int:
        """Total count of items removed."""
        return len(self.directories_removed) + len(self.files_removed)

    def summary(self) -> str:
        """Generate a human-readable summary of the cleanup."""
        if not self.has_changes:
            return "no deprecated items found"

        parts = []
        if self.directories_removed:
            dir_names = ", ".join(self.directories_removed)
            parts.append(f"dirs: {dir_names}")
        if self.files_removed:
            parts.append(f"{len(self.files_removed)} files")

        return f"removed {', '.join(parts)}"


def detect_deprecated_items(
    project_path: Path,
) -> tuple[list[Path], list[Path]]:
    """Detect deprecated directories and files in the project.

    Args:
        project_path: Root path of the project to check.

    Returns:
        Tuple of (deprecated_directories, deprecated_files) found.
    """
    deprecated_dirs = []
    deprecated_files = []

    # Check for deprecated directories
    for dir_name in DEPRECATED_DIRECTORIES:
        dir_path = project_path / dir_name
        if dir_path.exists() and dir_path.is_dir():
            deprecated_dirs.append(dir_path)
            logger.debug(f"Found deprecated directory: {dir_path}")

    # Check for deprecated file patterns in common command locations
    command_locations = [
        project_path / ".claude" / "commands",
        project_path / ".github" / "copilot" / "commands",
        project_path / ".cursor" / "commands",
    ]

    for location in command_locations:
        if location.exists():
            for pattern in DEPRECATED_FILE_PATTERNS:
                for file_path in location.glob(pattern):
                    deprecated_files.append(file_path)
                    logger.debug(f"Found deprecated file: {file_path}")

    # Check for deprecated agent files in .github/agents/
    # These are hyphenated agent files replaced by dot-notation (ADR-001)
    github_agents_dir = project_path / ".github" / "agents"
    if github_agents_dir.exists():
        for pattern in DEPRECATED_GITHUB_AGENT_PATTERNS:
            for file_path in github_agents_dir.glob(pattern):
                deprecated_files.append(file_path)
                logger.debug(f"Found deprecated agent file: {file_path}")

    return deprecated_dirs, deprecated_files


def cleanup_deprecated_files(
    project_path: Path,
    backup_dir: Path,
    dry_run: bool = False,
) -> DeprecatedCleanupResult:
    """Remove deprecated files and directories, creating backups first.

    This function detects deprecated items (legacy directories like .specify/
    and deprecated command files), creates backups, and removes them.

    Args:
        project_path: Root path of the project.
        backup_dir: Directory where backups will be stored.
        dry_run: If True, only detect but don't actually remove anything.

    Returns:
        DeprecatedCleanupResult with details of what was removed/backed up.
    """
    result = DeprecatedCleanupResult()

    # Detect deprecated items
    deprecated_dirs, deprecated_files = detect_deprecated_items(project_path)

    if not deprecated_dirs and not deprecated_files:
        logger.debug("No deprecated items found")
        return result

    # Ensure backup directory exists
    deprecated_backup_dir = backup_dir / "_deprecated"
    if not dry_run:
        deprecated_backup_dir.mkdir(parents=True, exist_ok=True)

    # Process deprecated directories
    for dir_path in deprecated_dirs:
        rel_path = dir_path.relative_to(project_path)
        dir_name = str(rel_path)

        if dry_run:
            result.directories_removed.append(dir_name)
            logger.info(f"[DRY RUN] Would remove directory: {dir_name}")
            continue

        try:
            # Create backup
            backup_path = deprecated_backup_dir / rel_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(dir_path, backup_path, dirs_exist_ok=True)
            result.directories_backed_up[dir_name] = backup_path

            # Remove the directory
            shutil.rmtree(dir_path)
            result.directories_removed.append(dir_name)
            logger.info(f"Removed deprecated directory: {dir_name}")

        except OSError as e:
            error_msg = f"Failed to remove directory {dir_name}: {e}"
            result.errors.append(error_msg)
            logger.error(error_msg)

    # Process deprecated files
    for file_path in deprecated_files:
        rel_path = file_path.relative_to(project_path)
        file_name = str(rel_path)

        if dry_run:
            result.files_removed.append(file_name)
            logger.info(f"[DRY RUN] Would remove file: {file_name}")
            continue

        try:
            # Create backup
            backup_path = deprecated_backup_dir / rel_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
            result.files_backed_up[file_name] = backup_path

            # Remove the file
            file_path.unlink()
            result.files_removed.append(file_name)
            logger.info(f"Removed deprecated file: {file_name}")

        except OSError as e:
            error_msg = f"Failed to remove file {file_name}: {e}"
            result.errors.append(error_msg)
            logger.error(error_msg)

    return result
