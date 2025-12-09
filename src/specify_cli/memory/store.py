"""Task Memory Store - Core storage and retrieval for task memory files.

This module provides the TaskMemoryStore class for managing task memory files
in the backlog/memory/ directory. Task memory files track implementation context,
decisions, approaches, and notes for individual tasks.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional


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

        # Update timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        updated_line = f"**Last Updated**: {timestamp}"

        # Replace old timestamp
        lines = current_content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("**Last Updated**:"):
                lines[i] = updated_line
                break
        current_content = "\n".join(lines)

        # Append content
        if section:
            # Find section and append there
            section_marker = f"## {section}"
            if section_marker in current_content:
                parts = current_content.split(section_marker)
                if len(parts) >= 2:
                    # Find next section or end of file
                    after_section = parts[1]
                    next_section_idx = after_section.find("\n## ")
                    if next_section_idx != -1:
                        # Insert before next section
                        section_content = after_section[:next_section_idx]
                        rest = after_section[next_section_idx:]
                        new_content = (
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
                        new_content = (
                            parts[0]
                            + section_marker
                            + after_section
                            + "\n\n"
                            + content
                            + "\n"
                        )
                    current_content = new_content
        else:
            # Append to end
            current_content = current_content.rstrip() + "\n\n" + content + "\n"

        memory_path.write_text(current_content)

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
        """
        return self.memory_dir / f"{task_id}.md"
