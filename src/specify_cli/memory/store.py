"""Task Memory Store - Core storage and retrieval for task memory files.

This module provides the TaskMemoryStore class for managing task memory files
in the backlog/memory/ directory. Task memory files track implementation context,
decisions, approaches, and notes for individual tasks.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class TaskMemoryStore:
    """Manages task memory files in backlog/memory/ directory.

    Task memory files provide persistent storage for:
    - Implementation context and rationale
    - Key decisions made during development
    - Approaches tried and their outcomes
    - Open questions and unresolved issues
    - Resources and references
    - Freeform implementation notes

    Attributes:
        base_path: Root directory of the project
        memory_dir: Directory containing active task memory files
        archive_dir: Directory containing archived task memory files
        template_dir: Directory containing memory templates
    """

    # Valid task ID pattern: task-<identifier> format
    # Allows alphanumeric chars and hyphens (e.g., task-42, task-bulk-001, task-feature-x)
    # Blocks path traversal characters (/, \, ..)
    TASK_ID_PATTERN = re.compile(r"^task-[a-zA-Z0-9][-a-zA-Z0-9]*$")

    def __init__(self, base_path: Optional[Path] = None):
        """Initialize store with optional custom base path.

        Args:
            base_path: Root directory of the project. Defaults to current working directory.
        """
        self.base_path = base_path or Path.cwd()
        self.memory_dir = self.base_path / "backlog" / "memory"
        self.archive_dir = self.memory_dir / "archive"
        self.template_dir = self.base_path / "templates" / "memory"

        # Ensure directories exist
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def _validate_task_id(self, task_id: str) -> None:
        """Validate task ID format to prevent path traversal attacks.

        Args:
            task_id: Task identifier to validate

        Raises:
            ValueError: If task_id is invalid or contains path traversal sequences
        """
        if not task_id:
            raise ValueError("Task ID cannot be empty")

        # Must match task-<identifier> format (alphanumeric + hyphens)
        if not self.TASK_ID_PATTERN.match(task_id):
            raise ValueError(
                f"Invalid task ID format: {task_id!r}. "
                "Must start with 'task-' followed by alphanumeric characters and hyphens"
            )

        # Defense-in-depth: Explicit check for path traversal characters.
        # While the regex above already blocks these, this provides an extra safety layer
        # in case the pattern is accidentally modified, and makes the security intent explicit.
        if ".." in task_id or "/" in task_id or "\\" in task_id:
            raise ValueError(f"Invalid characters in task ID: {task_id!r}")

    def create(
        self, task_id: str, template: str = "default", task_title: str = "", **kwargs
    ) -> Path:
        """Create a new task memory file from template.

        Args:
            task_id: Unique task identifier (e.g., "task-375")
            template: Name of template to use (default: "default")
            task_title: Optional task title for template substitution
            **kwargs: Additional variables for template substitution

        Returns:
            Path to the created memory file

        Raises:
            FileExistsError: If task memory already exists
            FileNotFoundError: If template file doesn't exist
        """
        if self.exists(task_id):
            raise FileExistsError(f"Task memory for {task_id} already exists")

        # Load template
        template_path = self.template_dir / f"{template}.md"
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        template_content = template_path.read_text()

        # Prepare substitution variables
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        variables = {
            "task_id": task_id,
            "created_date": now,
            "updated_date": now,
            "task_title": task_title,
            **kwargs,
        }

        # Substitute variables
        content = template_content
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            content = content.replace(placeholder, str(value))

        # Write memory file
        memory_path = self.get_path(task_id)
        memory_path.write_text(content)

        return memory_path

    def read(self, task_id: str) -> str:
        """Read task memory content.

        Args:
            task_id: Task identifier

        Returns:
            Content of the task memory file

        Raises:
            FileNotFoundError: If task memory doesn't exist
        """
        memory_path = self.get_path(task_id)
        if not memory_path.exists():
            raise FileNotFoundError(f"Task memory not found: {task_id}")

        return memory_path.read_text()

    def append(self, task_id: str, content: str, section: Optional[str] = None) -> None:
        """Append content to task memory.

        Args:
            task_id: Task identifier
            content: Content to append
            section: Optional section name to append to (e.g., "Notes", "Key Decisions")
                    If None, appends to end of file

        Raises:
            FileNotFoundError: If task memory doesn't exist
        """
        if not self.exists(task_id):
            raise FileNotFoundError(f"Task memory not found: {task_id}")

        memory_path = self.get_path(task_id)
        current_content = memory_path.read_text()

        # Parse frontmatter and body
        metadata, body = self._parse_frontmatter(current_content)

        # Update timestamp in metadata
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        metadata["updated"] = timestamp

        # Also handle old format (for backward compatibility)
        lines = body.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("**Last Updated**:"):
                lines[i] = f"**Last Updated**: {timestamp}"
                break
        body = "\n".join(lines)

        # Append content
        if section:
            # Find section and append there
            section_marker = f"## {section}"
            if section_marker in body:
                parts = body.split(section_marker)
                if len(parts) >= 2:
                    # Find next section or end of file
                    after_section = parts[1]
                    next_section_idx = after_section.find("\n## ")
                    if next_section_idx != -1:
                        # Insert before next section
                        section_content = after_section[:next_section_idx]
                        rest = after_section[next_section_idx:]
                        body = (
                            parts[0]
                            + section_marker
                            + section_content
                            + "\n\n"
                            + content
                            + "\n"
                            + rest
                        )
                    else:
                        # Append to end of section
                        body = (
                            parts[0]
                            + section_marker
                            + after_section
                            + "\n\n"
                            + content
                            + "\n"
                        )
        else:
            # Append to end
            body = body.rstrip() + "\n\n" + content + "\n"

        # Serialize with updated metadata
        updated_content = self._serialize_frontmatter(metadata, body)
        memory_path.write_text(updated_content)

    def archive(self, task_id: str) -> None:
        """Move task memory to archive.

        Args:
            task_id: Task identifier

        Raises:
            FileNotFoundError: If task memory doesn't exist
        """
        memory_path = self.get_path(task_id)
        if not memory_path.exists():
            raise FileNotFoundError(f"Task memory not found: {task_id}")

        archive_path = self.archive_dir / memory_path.name
        memory_path.rename(archive_path)

    def restore(self, task_id: str) -> None:
        """Restore task memory from archive.

        Args:
            task_id: Task identifier

        Raises:
            FileNotFoundError: If archived task memory doesn't exist
            FileExistsError: If active task memory already exists
        """
        archive_path = self.archive_dir / f"{task_id}.md"
        if not archive_path.exists():
            raise FileNotFoundError(f"Archived task memory not found: {task_id}")

        memory_path = self.get_path(task_id)
        if memory_path.exists():
            raise FileExistsError(f"Active task memory already exists: {task_id}")

        archive_path.rename(memory_path)

    def delete(self, task_id: str, from_archive: bool = False) -> None:
        """Permanently delete task memory.

        Args:
            task_id: Task identifier
            from_archive: If True, delete from archive instead of active directory

        Raises:
            FileNotFoundError: If task memory doesn't exist
        """
        if from_archive:
            memory_path = self.archive_dir / f"{task_id}.md"
        else:
            memory_path = self.get_path(task_id)

        if not memory_path.exists():
            location = "archive" if from_archive else "active directory"
            raise FileNotFoundError(f"Task memory not found in {location}: {task_id}")

        memory_path.unlink()

    def list_active(self) -> List[str]:
        """List all active task memory IDs.

        Returns:
            List of task IDs with active memory files
        """
        if not self.memory_dir.exists():
            return []

        memory_files = [
            f.stem
            for f in self.memory_dir.iterdir()
            if f.is_file() and f.suffix == ".md" and f.stem.startswith("task-")
        ]
        return sorted(memory_files)

    def list_archived(self) -> List[str]:
        """List all archived task memory IDs.

        Returns:
            List of task IDs with archived memory files
        """
        if not self.archive_dir.exists():
            return []

        archive_files = [
            f.stem
            for f in self.archive_dir.iterdir()
            if f.is_file() and f.suffix == ".md" and f.stem.startswith("task-")
        ]
        return sorted(archive_files)

    def exists(self, task_id: str, check_archive: bool = False) -> bool:
        """Check if task memory exists.

        Args:
            task_id: Task identifier
            check_archive: If True, also check archive directory

        Returns:
            True if task memory exists
        """
        memory_path = self.get_path(task_id)
        if memory_path.exists():
            return True

        if check_archive:
            archive_path = self.archive_dir / f"{task_id}.md"
            return archive_path.exists()

        return False

    def get_path(self, task_id: str) -> Path:
        """Get path to task memory file.

        Args:
            task_id: Task identifier

        Returns:
            Path to the task memory file (may not exist)

        Raises:
            ValueError: If task_id is invalid or contains path traversal sequences
        """
        self._validate_task_id(task_id)
        path = self.memory_dir / f"{task_id}.md"

        # Final safety check: ensure resolved path is within memory_dir
        try:
            path.resolve().relative_to(self.memory_dir.resolve())
        except ValueError:
            raise ValueError(
                f"Task ID resolves to path outside memory directory: {task_id!r}"
            )

        return path

    def _parse_frontmatter(self, content: str) -> tuple[Dict[str, str], str]:
        """Parse YAML frontmatter from markdown content.

        Args:
            content: Markdown content with optional YAML frontmatter

        Returns:
            Tuple of (frontmatter_dict, body_content)
        """
        # Match YAML frontmatter pattern: ---\n...\n---
        pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
        match = re.match(pattern, content, re.DOTALL)

        if match:
            frontmatter_text = match.group(1)
            body = match.group(2)

            # Simple YAML parsing (key: value pairs)
            frontmatter = {}
            for line in frontmatter_text.split("\n"):
                line = line.strip()
                if ":" in line:
                    key, value = line.split(":", 1)
                    frontmatter[key.strip()] = value.strip()

            return frontmatter, body
        else:
            # No frontmatter found
            return {}, content

    def _serialize_frontmatter(self, metadata: Dict[str, str], body: str) -> str:
        """Serialize metadata and body into markdown with YAML frontmatter.

        Args:
            metadata: Dictionary of metadata key-value pairs
            body: Markdown body content

        Returns:
            Complete markdown content with frontmatter
        """
        if not metadata:
            return body

        frontmatter_lines = ["---"]
        for key, value in metadata.items():
            frontmatter_lines.append(f"{key}: {value}")
        frontmatter_lines.append("---")
        frontmatter_lines.append("")  # Blank line after frontmatter

        return "\n".join(frontmatter_lines) + body

    def _update_metadata(self, task_id: str, updates: Dict[str, str]) -> None:
        """Update YAML frontmatter metadata in memory file.

        Args:
            task_id: Task identifier
            updates: Dictionary of metadata updates

        Raises:
            FileNotFoundError: If task memory doesn't exist
        """
        memory_path = self.get_path(task_id)
        if not memory_path.exists():
            raise FileNotFoundError(f"Task memory not found: {task_id}")

        content = memory_path.read_text()
        metadata, body = self._parse_frontmatter(content)

        # Apply updates
        metadata.update(updates)

        # Write back
        updated_content = self._serialize_frontmatter(metadata, body)
        memory_path.write_text(updated_content)

    def clear(self, task_id: str) -> None:
        """Clear task memory content while preserving metadata.

        Resets all sections to empty/template state but keeps YAML frontmatter
        (task_id, created, updated timestamps).

        Args:
            task_id: Task identifier

        Raises:
            FileNotFoundError: If task memory doesn't exist
        """
        memory_path = self.get_path(task_id)
        if not memory_path.exists():
            raise FileNotFoundError(f"Task memory not found: {task_id}")

        content = memory_path.read_text()
        metadata, _ = self._parse_frontmatter(content)

        # Update timestamp
        metadata["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Create empty body with sections
        empty_body = """# Task Memory: {task_id}

## Context

<!-- Brief description of what this task is about -->

## Key Decisions

<!-- Record important decisions made during implementation -->

## Approaches Tried

<!-- Document approaches attempted and their outcomes -->

## Open Questions

<!-- Track unresolved questions -->

## Resources

<!-- Links to relevant documentation, PRs, discussions -->

## Notes

<!-- Freeform notes section -->
""".format(task_id=metadata.get("task_id", task_id))

        # Write cleared content with preserved metadata
        cleared_content = self._serialize_frontmatter(metadata, empty_body)
        memory_path.write_text(cleared_content)
