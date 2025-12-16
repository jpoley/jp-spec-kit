"""
Backlog.md file writer for flowspec tasks.

Generates Backlog.md format task files from parsed flowspec tasks.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional
from .parser import Task


class BacklogWriter:
    """Writer for Backlog.md format task files."""

    def __init__(self, backlog_dir: Path):
        """
        Initialize the writer.

        Args:
            backlog_dir: Path to the backlog directory (e.g., ./backlog)
        """
        self.backlog_dir = Path(backlog_dir)
        self.tasks_dir = self.backlog_dir / "tasks"

    def write_task(
        self,
        task: Task,
        *,
        assignee: Optional[list[str]] = None,
        status: str = "To Do",
        notes: Optional[str] = None,
    ) -> Path:
        """
        Write a single task to Backlog.md format.

        Args:
            task: Task object to write
            assignee: Optional list of assignee names
            status: Task status (default: "To Do")
            notes: Optional additional notes to include in task body

        Returns:
            Path to the created task file
        """
        # Ensure tasks directory exists
        self.tasks_dir.mkdir(parents=True, exist_ok=True)

        # Generate task filename
        # Format: task-{id} - {title}.md
        # Example: task-001 - Create User model.md
        task_num = task.task_id.replace("T", "").zfill(3)
        filename = self._sanitize_filename(f"task-{task_num} - {task.description}")

        # Add .md extension if not present
        if not filename.endswith(".md"):
            filename += ".md"

        task_file = self.tasks_dir / filename

        # Build frontmatter
        frontmatter = self._build_frontmatter(
            task_id=f"task-{task_num}",
            title=self._clean_title(task.description),
            status=status,
            assignee=assignee or [],
            labels=task.labels,
            dependencies=task.dependencies,
        )

        # Build body
        body = self._build_body(task, notes)

        # Write file
        with open(task_file, "w", encoding="utf-8") as f:
            f.write(frontmatter)
            f.write("\n\n")
            f.write(body)

        return task_file

    def write_tasks(
        self, tasks: list[Task], *, status: str = "To Do", overwrite: bool = False
    ) -> list[Path]:
        """
        Write multiple tasks to Backlog.md format.

        Args:
            tasks: List of Task objects to write
            status: Default status for all tasks
            overwrite: Whether to overwrite existing task files

        Returns:
            List of paths to created task files
        """
        created_files = []

        for task in tasks:
            task_file = self._get_task_file_path(task)

            # Skip if file exists and overwrite is False
            if task_file.exists() and not overwrite:
                continue

            # Determine status based on task completion
            task_status = "Done" if task.is_completed else status

            file_path = self.write_task(task, status=task_status)
            created_files.append(file_path)

        return created_files

    def _build_frontmatter(
        self,
        task_id: str,
        title: str,
        status: str,
        assignee: list[str],
        labels: list[str],
        dependencies: list[str],
    ) -> str:
        """Build YAML frontmatter for Backlog.md task."""
        # Convert dependencies from T### format to task-### format
        backlog_dependencies = [
            f"task-{dep.replace('T', '').zfill(3)}" for dep in dependencies
        ]

        # Build frontmatter
        lines = [
            "---",
            f"id: {task_id}",
            f"title: {title}",
            f"status: {status}",
        ]

        # Assignee (list format)
        if assignee:
            lines.append("assignee:")
            for person in assignee:
                lines.append(f"  - {person}")
        else:
            lines.append("assignee: []")

        # Created date
        created_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        lines.append(f"created_date: '{created_date}'")

        # Labels (list format)
        if labels:
            lines.append("labels:")
            for label in labels:
                lines.append(f"  - {label}")
        else:
            lines.append("labels: []")

        # Dependencies (list format)
        if backlog_dependencies:
            lines.append("dependencies:")
            for dep in backlog_dependencies:
                lines.append(f"  - {dep}")
        else:
            lines.append("dependencies: []")

        lines.append("---")

        return "\n".join(lines)

    def _build_body(self, task: Task, notes: Optional[str] = None) -> str:
        """Build markdown body for task."""
        body_parts = []

        # Add task description as main content
        body_parts.append(f"## Description\n\n{task.description}")

        # Add file path if present
        if task.file_path:
            body_parts.append(f"\n## File\n\n`{task.file_path}`")

        # Add phase information
        if task.phase:
            body_parts.append(f"\n## Phase\n\n{task.phase}")

        # Add parallelization note
        if task.is_parallelizable:
            body_parts.append(
                "\n## Parallelizable\n\n"
                "This task can be worked on in parallel with other parallelizable tasks."
            )

        # Add additional notes
        if notes:
            body_parts.append(f"\n## Notes\n\n{notes}")

        return "\n".join(body_parts)

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename by removing/replacing invalid characters.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove or replace characters that are invalid in filenames
        invalid_chars = ["<", ">", ":", '"', "/", "\\", "|", "?", "*"]
        sanitized = filename

        for char in invalid_chars:
            sanitized = sanitized.replace(char, "-")

        # Limit length (keep reasonable filename length)
        max_length = 100
        if len(sanitized) > max_length:
            # Truncate but keep extension
            if sanitized.endswith(".md"):
                sanitized = sanitized[: max_length - 3] + ".md"
            else:
                sanitized = sanitized[:max_length]

        # Replace multiple spaces/dashes with single dash
        while "  " in sanitized:
            sanitized = sanitized.replace("  ", " ")
        while "--" in sanitized:
            sanitized = sanitized.replace("--", "-")

        return sanitized.strip()

    def _clean_title(self, description: str) -> str:
        """
        Clean task description to create a suitable title.

        Args:
            description: Full task description

        Returns:
            Cleaned title (first sentence or truncated description)
        """
        # Take first sentence or first 60 characters
        title = description.split(".")[0].strip()

        # If still too long, truncate
        max_length = 60
        if len(title) > max_length:
            title = title[:max_length].strip() + "..."

        return title

    def _get_task_file_path(self, task: Task) -> Path:
        """Get the file path for a task without creating it."""
        task_num = task.task_id.replace("T", "").zfill(3)
        filename = self._sanitize_filename(f"task-{task_num} - {task.description}")
        if not filename.endswith(".md"):
            filename += ".md"
        return self.tasks_dir / filename

    def update_task_status(
        self, task_file: Path, new_status: str, completed_date: Optional[str] = None
    ) -> None:
        """
        Update the status of an existing task file.

        Args:
            task_file: Path to the task file
            new_status: New status value
            completed_date: Optional completion date (for "Done" status)
        """
        if not task_file.exists():
            raise FileNotFoundError(f"Task file not found: {task_file}")

        # Read current content
        with open(task_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Split frontmatter and body
        if not content.startswith("---"):
            raise ValueError(f"Invalid task file format: {task_file}")

        parts = content.split("---", 2)
        if len(parts) < 3:
            raise ValueError(f"Invalid task file format: {task_file}")

        frontmatter = parts[1]
        body = parts[2]

        # Update status in frontmatter
        lines = frontmatter.split("\n")
        updated_lines = []

        for line in lines:
            if line.startswith("status:"):
                updated_lines.append(f"status: {new_status}")
                # Add completed_date if status is Done and not already present
                if (
                    new_status == "Done"
                    and completed_date
                    and "completed_date:" not in frontmatter
                ):
                    updated_lines.append(f"completed_date: '{completed_date}'")
            else:
                updated_lines.append(line)

        # Reconstruct file
        updated_content = "---\n" + "\n".join(updated_lines) + "\n---" + body

        # Write back
        with open(task_file, "w", encoding="utf-8") as f:
            f.write(updated_content)

    def get_task_stats(self) -> dict:
        """
        Get statistics about tasks in the backlog.

        Returns:
            Dictionary with task counts by status, label, etc.
        """
        if not self.tasks_dir.exists():
            return {
                "total": 0,
                "by_status": {},
                "by_label": {},
            }

        task_files = list(self.tasks_dir.glob("task-*.md"))

        stats = {
            "total": len(task_files),
            "by_status": {},
            "by_label": {},
        }

        for task_file in task_files:
            with open(task_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract status
            for line in content.split("\n"):
                if line.startswith("status:"):
                    status = line.split(":", 1)[1].strip()
                    stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

                # Extract labels
                if line.startswith("  - ") and "labels:" in content.split(line)[0]:
                    label = line.strip("- ").strip()
                    stats["by_label"][label] = stats["by_label"].get(label, 0) + 1

        return stats
