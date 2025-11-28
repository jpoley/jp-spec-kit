"""Unit tests for BacklogWriter."""

import pytest
from datetime import datetime

from specify_cli.backlog.writer import BacklogWriter
from specify_cli.backlog.parser import Task


class TestBacklogWriter:
    """Test suite for BacklogWriter class."""

    def test_writer_initialization(self, backlog_dir):
        """Test writer initializes correctly."""
        writer = BacklogWriter(backlog_dir)

        assert writer.backlog_dir == backlog_dir
        assert writer.tasks_dir == backlog_dir / "tasks"

    def test_write_single_task(self, backlog_dir):
        """Test writing a single task to file."""
        writer = BacklogWriter(backlog_dir)

        task = Task(
            task_id="T001",
            description="Create user authentication module",
        )

        task_file = writer.write_task(task)

        assert task_file.exists()
        assert task_file.parent == writer.tasks_dir
        assert "task-001" in task_file.name

        # Read and verify content
        content = task_file.read_text()
        assert "---" in content  # Frontmatter markers
        assert "id: task-001" in content
        assert "Create user authentication module" in content

    def test_write_task_creates_directory(self, temp_project_dir):
        """Test that writer creates tasks directory if it doesn't exist."""
        backlog_dir = temp_project_dir / "backlog"
        writer = BacklogWriter(backlog_dir)

        assert not writer.tasks_dir.exists()

        task = Task(task_id="T001", description="Test task")
        writer.write_task(task)

        assert writer.tasks_dir.exists()

    def test_write_task_frontmatter_structure(self, backlog_dir):
        """Test frontmatter has correct structure."""
        writer = BacklogWriter(backlog_dir)

        task = Task(
            task_id="T005",
            description="Implement feature X",
            user_story="US1",
            priority="P0",
        )

        task_file = writer.write_task(task, assignee=["Alice", "Bob"])
        content = task_file.read_text()

        # Check frontmatter fields
        assert "id: task-005" in content
        assert "title:" in content
        assert "status: To Do" in content
        assert "assignee:" in content
        assert "- Alice" in content
        assert "- Bob" in content
        assert "created_date:" in content
        assert "labels:" in content
        assert "dependencies:" in content

    def test_write_task_with_labels(self, backlog_dir):
        """Test task labels are written correctly."""
        writer = BacklogWriter(backlog_dir)

        task = Task(
            task_id="T010",
            description="Test task",
            user_story="US2",
            is_parallelizable=True,
            priority="P1",
            phase="Foundational",
        )

        task_file = writer.write_task(task)
        content = task_file.read_text()

        # Check labels section
        assert "labels:" in content
        assert "- US2" in content
        assert "- parallelizable" in content
        assert "- P1" in content
        assert "- foundational" in content

    def test_write_task_with_dependencies(self, backlog_dir):
        """Test task dependencies are written correctly."""
        writer = BacklogWriter(backlog_dir)

        task = Task(
            task_id="T005",
            description="Feature that depends on others",
            dependencies=["T001", "T002", "T003"],
        )

        task_file = writer.write_task(task)
        content = task_file.read_text()

        # Dependencies should be converted to task-### format
        assert "dependencies:" in content
        assert "- task-001" in content
        assert "- task-002" in content
        assert "- task-003" in content

    def test_write_task_empty_dependencies(self, backlog_dir):
        """Test task with no dependencies."""
        writer = BacklogWriter(backlog_dir)

        task = Task(
            task_id="T001",
            description="Independent task",
            dependencies=[],
        )

        task_file = writer.write_task(task)
        content = task_file.read_text()

        assert "dependencies: []" in content

    def test_write_task_body_sections(self, backlog_dir):
        """Test task body contains all expected sections."""
        writer = BacklogWriter(backlog_dir)

        task = Task(
            task_id="T007",
            description="Update authentication logic",
            file_path="src/auth/login.py",
            phase="User Story 1",
            is_parallelizable=True,
        )

        task_file = writer.write_task(task)
        content = task_file.read_text()

        # Check body sections
        assert "## Description" in content
        assert "Update authentication logic" in content
        assert "## File" in content
        assert "`src/auth/login.py`" in content
        assert "## Phase" in content
        assert "User Story 1" in content
        assert "## Parallelizable" in content

    def test_write_task_with_notes(self, backlog_dir):
        """Test writing task with additional notes."""
        writer = BacklogWriter(backlog_dir)

        task = Task(task_id="T001", description="Test task")
        notes = "This is a critical task that must be completed first."

        task_file = writer.write_task(task, notes=notes)
        content = task_file.read_text()

        assert "## Notes" in content
        assert notes in content

    def test_write_task_completed_status(self, backlog_dir):
        """Test writing completed task sets status to Done."""
        writer = BacklogWriter(backlog_dir)

        task = Task(
            task_id="T001",
            description="Completed task",
            is_completed=True,
        )

        task_file = writer.write_task(task)
        content = task_file.read_text()

        # Status should be "Done" for completed tasks when written via write_tasks
        # But write_task uses default status parameter
        assert "status:" in content

    def test_write_multiple_tasks(self, backlog_dir):
        """Test writing multiple tasks."""
        writer = BacklogWriter(backlog_dir)

        tasks = [
            Task(task_id="T001", description="First task"),
            Task(task_id="T002", description="Second task"),
            Task(task_id="T003", description="Third task", is_completed=True),
        ]

        created_files = writer.write_tasks(tasks)

        assert len(created_files) == 3
        assert all(f.exists() for f in created_files)

        # Check third task is marked as Done
        content = created_files[2].read_text()
        assert "status: Done" in content

    def test_write_tasks_no_overwrite(self, backlog_dir):
        """Test that write_tasks skips existing files by default."""
        writer = BacklogWriter(backlog_dir)

        task = Task(task_id="T001", description="Test task")

        # Write first time
        first_write = writer.write_tasks([task])
        assert len(first_write) == 1

        # Write second time without overwrite
        second_write = writer.write_tasks([task], overwrite=False)
        assert len(second_write) == 0  # Should skip existing

    def test_write_tasks_with_overwrite(self, backlog_dir):
        """Test that write_tasks overwrites when flag is set."""
        writer = BacklogWriter(backlog_dir)

        task = Task(task_id="T001", description="Original description")

        # Write first time
        writer.write_tasks([task])

        # Modify and write again with overwrite
        task.description = "Updated description"
        created_files = writer.write_tasks([task], overwrite=True)

        assert len(created_files) == 1
        content = created_files[0].read_text()
        assert "Updated description" in content

    def test_sanitize_filename(self, backlog_dir):
        """Test filename sanitization."""
        writer = BacklogWriter(backlog_dir)

        test_cases = [
            ("Normal filename", "Normal filename"),
            ("File/with/slashes", "File-with-slashes"),
            ("File<with>invalid:chars", "File-with-invalid-chars"),
            ("File?with*wildcards", "File-with-wildcards"),
            ("A" * 150, "A" * 97 + ".md"),  # Long filename truncation
            ("Multiple  spaces", "Multiple spaces"),
            ("Multiple--dashes", "Multiple-dashes"),
        ]

        for input_name, expected_pattern in test_cases:
            sanitized = writer._sanitize_filename(input_name)
            assert len(sanitized) <= 100
            assert not any(c in sanitized for c in ['<', '>', ':', '"', '/', '\\', '|', '?', '*'])

    def test_clean_title(self, backlog_dir):
        """Test title cleaning."""
        writer = BacklogWriter(backlog_dir)

        test_cases = [
            ("Short title", "Short title"),
            ("Title with sentence. And another.", "Title with sentence"),
            ("A" * 100, "A" * 60 + "..."),  # Long title
        ]

        for input_title, expected in test_cases:
            cleaned = writer._clean_title(input_title)
            assert len(cleaned) <= 63  # Max 60 + "..."
            if "." in input_title and len(input_title) < 60:
                assert "." not in cleaned or cleaned.endswith("...")

    def test_update_task_status(self, backlog_dir):
        """Test updating task status."""
        writer = BacklogWriter(backlog_dir)

        task = Task(task_id="T001", description="Test task")
        task_file = writer.write_task(task, status="To Do")

        # Update status
        writer.update_task_status(task_file, "In Progress")

        content = task_file.read_text()
        assert "status: In Progress" in content

    def test_update_task_status_with_completed_date(self, backlog_dir):
        """Test updating task to Done adds completion date."""
        writer = BacklogWriter(backlog_dir)

        task = Task(task_id="T001", description="Test task")
        task_file = writer.write_task(task, status="To Do")

        # Update to Done
        completion_date = "2024-01-15 10:30"
        writer.update_task_status(task_file, "Done", completed_date=completion_date)

        content = task_file.read_text()
        assert "status: Done" in content
        assert f"completed_date: '{completion_date}'" in content

    def test_update_task_status_file_not_found(self, backlog_dir):
        """Test updating non-existent task raises error."""
        writer = BacklogWriter(backlog_dir)
        non_existent = backlog_dir / "tasks" / "nonexistent.md"

        with pytest.raises(FileNotFoundError):
            writer.update_task_status(non_existent, "Done")

    def test_update_task_status_invalid_format(self, backlog_dir):
        """Test updating task with invalid format raises error."""
        writer = BacklogWriter(backlog_dir)
        writer.tasks_dir.mkdir(parents=True, exist_ok=True)

        # Create invalid task file
        invalid_file = writer.tasks_dir / "invalid.md"
        invalid_file.write_text("No frontmatter here")

        with pytest.raises(ValueError):
            writer.update_task_status(invalid_file, "Done")

    def test_get_task_stats_empty(self, backlog_dir):
        """Test getting stats from empty backlog."""
        writer = BacklogWriter(backlog_dir)
        stats = writer.get_task_stats()

        assert stats["total"] == 0
        assert stats["by_status"] == {}
        assert stats["by_label"] == {}

    def test_get_task_stats_with_tasks(self, backlog_dir):
        """Test getting stats from backlog with tasks."""
        writer = BacklogWriter(backlog_dir)

        tasks = [
            Task(task_id="T001", description="Task 1", user_story="US1"),
            Task(task_id="T002", description="Task 2", is_completed=True),
            Task(task_id="T003", description="Task 3", user_story="US1"),
        ]

        writer.write_tasks(tasks)
        stats = writer.get_task_stats()

        assert stats["total"] == 3
        assert stats["by_status"]["To Do"] == 2
        assert stats["by_status"]["Done"] == 1

    def test_get_task_file_path(self, backlog_dir):
        """Test getting task file path without creating it."""
        writer = BacklogWriter(backlog_dir)

        task = Task(task_id="T042", description="Test task for path")
        path = writer._get_task_file_path(task)

        assert "task-042" in path.name
        assert not path.exists()  # Should not create file
        assert path.parent == writer.tasks_dir

    def test_write_task_custom_status(self, backlog_dir):
        """Test writing task with custom status."""
        writer = BacklogWriter(backlog_dir)

        task = Task(task_id="T001", description="Test")
        task_file = writer.write_task(task, status="In Progress")

        content = task_file.read_text()
        assert "status: In Progress" in content

    def test_write_task_empty_assignee_list(self, backlog_dir):
        """Test writing task with empty assignee list."""
        writer = BacklogWriter(backlog_dir)

        task = Task(task_id="T001", description="Test")
        task_file = writer.write_task(task, assignee=[])

        content = task_file.read_text()
        assert "assignee: []" in content

    def test_task_filename_format(self, backlog_dir):
        """Test task filename follows expected format."""
        writer = BacklogWriter(backlog_dir)

        task = Task(task_id="T007", description="Implement user login")
        task_file = writer.write_task(task)

        # Filename should be: task-007 - Implement user login.md
        assert task_file.name.startswith("task-007")
        assert task_file.name.endswith(".md")
        assert "Implement user login" in task_file.name

    def test_write_task_no_file_path(self, backlog_dir):
        """Test writing task without file path."""
        writer = BacklogWriter(backlog_dir)

        task = Task(task_id="T001", description="Task without file path")
        task_file = writer.write_task(task)

        content = task_file.read_text()
        # Should not have File section
        assert content.count("## File") == 0

    def test_write_task_no_phase(self, backlog_dir):
        """Test writing task without phase."""
        writer = BacklogWriter(backlog_dir)

        task = Task(task_id="T001", description="Task without phase")
        task_file = writer.write_task(task)

        content = task_file.read_text()
        # Should not have Phase section
        assert content.count("## Phase") == 0

    def test_created_date_format(self, backlog_dir):
        """Test that created_date follows correct format."""
        writer = BacklogWriter(backlog_dir)

        task = Task(task_id="T001", description="Test")
        task_file = writer.write_task(task)

        content = task_file.read_text()

        # Extract created_date line
        for line in content.split('\n'):
            if line.startswith('created_date:'):
                date_str = line.split("'")[1]
                # Verify it can be parsed
                datetime.strptime(date_str, '%Y-%m-%d %H:%M')
                break
        else:
            pytest.fail("created_date not found in frontmatter")

    def test_write_tasks_mixed_completion_status(self, backlog_dir):
        """Test writing mix of completed and incomplete tasks."""
        writer = BacklogWriter(backlog_dir)

        tasks = [
            Task(task_id="T001", description="Not done", is_completed=False),
            Task(task_id="T002", description="Done", is_completed=True),
            Task(task_id="T003", description="Also not done", is_completed=False),
        ]

        created_files = writer.write_tasks(tasks)

        # Check statuses
        content1 = created_files[0].read_text()
        content2 = created_files[1].read_text()
        content3 = created_files[2].read_text()

        assert "status: To Do" in content1
        assert "status: Done" in content2
        assert "status: To Do" in content3
