"""Tests for CLI migration function."""

import pytest

from specify_cli.satellite.migration import migrate_tasks_cli


@pytest.fixture
def sample_tasks_dir(tmp_path):
    """Create a directory with sample v1 tasks."""
    # Create v1 tasks
    for i in range(1, 4):
        task_file = tmp_path / f"task-{i:03d} - Test-Task-{i}.md"
        content = f"""---
id: task-{i:03d}
title: Test task {i}
status: To Do
labels:
  - test
---

## Description
Task {i} description
"""
        task_file.write_text(content)

    # Create one v2 task
    v2_task = tmp_path / "task-004 - Already-V2.md"
    v2_task.write_text("""---
id: task-004
title: Already v2
status: Done
schema_version: '2'
---

Body
""")

    return tmp_path


class TestMigrateTasksCLI:
    """Tests for migrate_tasks_cli function."""

    def test_cli_basic_migration(self, sample_tasks_dir, capsys):
        """Test basic CLI migration."""
        exit_code = migrate_tasks_cli(sample_tasks_dir)

        assert exit_code == 0

        # Check output
        captured = capsys.readouterr()
        assert "Migrated: 3" in captured.out
        assert "Skipped:  1" in captured.out
        assert "Errors:   0" in captured.out

        # Verify files were migrated
        for i in range(1, 4):
            task_file = sample_tasks_dir / f"task-{i:03d} - Test-Task-{i}.md"
            content = task_file.read_text()
            assert "schema_version: '2'" in content

    def test_cli_dry_run(self, sample_tasks_dir, capsys):
        """Test dry-run doesn't modify files."""
        exit_code = migrate_tasks_cli(sample_tasks_dir, dry_run=True)

        assert exit_code == 0

        # Check output
        captured = capsys.readouterr()
        assert "Migrated: 3" in captured.out

        # Verify files weren't modified
        for i in range(1, 4):
            task_file = sample_tasks_dir / f"task-{i:03d} - Test-Task-{i}.md"
            content = task_file.read_text()
            assert "schema_version" not in content

    def test_cli_verbose_output(self, sample_tasks_dir, capsys):
        """Test verbose output."""
        exit_code = migrate_tasks_cli(sample_tasks_dir, verbose=True)

        assert exit_code == 0

        captured = capsys.readouterr()
        assert "Task Schema Migration Report" in captured.out
        assert "Migrating tasks in:" in captured.out

    def test_cli_with_cleanup(self, sample_tasks_dir, capsys):
        """Test cleanup of backup files."""
        exit_code = migrate_tasks_cli(sample_tasks_dir, cleanup=True)

        assert exit_code == 0

        # Verify no backup files remain
        backup_files = list(sample_tasks_dir.glob("*.bak"))
        assert len(backup_files) == 0

    def test_cli_nonexistent_directory(self, tmp_path, capsys):
        """Test error handling for nonexistent directory."""
        nonexistent = tmp_path / "does-not-exist"
        exit_code = migrate_tasks_cli(nonexistent)

        assert exit_code == 1

        captured = capsys.readouterr()
        assert "Error: Directory not found" in captured.out

    def test_cli_accepts_string_path(self, sample_tasks_dir):
        """Test that CLI accepts string paths."""
        exit_code = migrate_tasks_cli(str(sample_tasks_dir))

        assert exit_code == 0

    def test_cli_accepts_path_object(self, sample_tasks_dir):
        """Test that CLI accepts Path objects."""
        exit_code = migrate_tasks_cli(sample_tasks_dir)

        assert exit_code == 0

    def test_cli_preserves_backups_on_error(self, tmp_path, capsys):
        """Test that backups are preserved when errors occur."""
        # Create valid task
        valid = tmp_path / "task-001 - Valid.md"
        valid.write_text("""---
id: task-001
title: Valid
status: To Do
---

Body
""")

        # Create invalid task
        invalid = tmp_path / "task-002 - Invalid.md"
        invalid.write_text("""---
id: task-002
title: [invalid yaml
status: To Do
---

Body
""")

        exit_code = migrate_tasks_cli(tmp_path)

        # Should fail due to error
        assert exit_code == 1

        # Valid task should have backup
        backup = valid.with_suffix(".md.bak")
        assert backup.exists()

    def test_cli_cleanup_not_run_on_errors(self, tmp_path):
        """Test that cleanup is not run when errors occur."""
        # Create tasks
        for i in range(1, 3):
            task = tmp_path / f"task-{i:03d}.md"
            task.write_text(f"""---
id: task-{i:03d}
title: Task {i}
status: To Do
---

Body
""")

        # Create invalid task
        invalid = tmp_path / "task-999.md"
        invalid.write_text("---\ninvalid\n---")

        exit_code = migrate_tasks_cli(tmp_path, cleanup=True)

        # Should have errors
        assert exit_code == 1

        # Backups should still exist (cleanup not run)
        backups = list(tmp_path.glob("*.bak"))
        assert len(backups) > 0
