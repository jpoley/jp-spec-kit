"""Tests for task schema migration."""

import pytest
from pathlib import Path

from flowspec_cli.satellite.migration import TaskMigrator, MigrationError


@pytest.fixture
def sample_v1_task(tmp_path):
    """Create a sample v1 task file."""
    task_file = tmp_path / "task-001 - Example.md"
    content = """---
id: task-001
title: Example task
status: To Do
assignee:
  - '@user'
labels:
  - backend
  - api
created_date: '2025-11-24'
updated_date: '2025-11-25 10:30'
---

## Description

This is a test task.

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 First criterion
- [ ] #2 Second criterion
<!-- AC:END -->
"""
    task_file.write_text(content)
    return task_file


@pytest.fixture
def sample_v2_task(tmp_path):
    """Create a sample v2 task file."""
    task_file = tmp_path / "task-002 - Already-Migrated.md"
    content = """---
id: task-002
title: Already migrated
status: Done
schema_version: '2'
---

## Description

This task is already v2.
"""
    task_file.write_text(content)
    return task_file


@pytest.fixture
def sample_v2_with_upstream(tmp_path):
    """Create a sample v2 task with upstream fields."""
    task_file = tmp_path / "task-003 - With-Upstream.md"
    content = """---
id: task-003
title: Task with upstream
status: In Progress
schema_version: '2'
upstream:
  provider: github
  id: owner/repo#123
  url: https://github.com/owner/repo/issues/123
  synced_at: '2025-11-25T10:30:00Z'
  etag: abc123
---

## Description

This task has upstream sync data.
"""
    task_file.write_text(content)
    return task_file


@pytest.fixture
def empty_task_file(tmp_path):
    """Create an empty task file."""
    task_file = tmp_path / "task-empty.md"
    task_file.write_text("")
    return task_file


@pytest.fixture
def invalid_yaml_task(tmp_path):
    """Create a task with invalid YAML."""
    task_file = tmp_path / "task-invalid.md"
    content = """---
id: task-004
title: [invalid yaml
status: To Do
---

Body
"""
    task_file.write_text(content)
    return task_file


@pytest.fixture
def no_frontmatter_task(tmp_path):
    """Create a file without frontmatter."""
    task_file = tmp_path / "task-no-frontmatter.md"
    content = "Just some text without frontmatter"
    task_file.write_text(content)
    return task_file


class TestTaskMigrator:
    """Tests for TaskMigrator class."""

    def test_migrate_v1_to_v2(self, sample_v1_task):
        """Test migrating v1 task to v2."""
        migrator = TaskMigrator()
        result = migrator.migrate(sample_v1_task)

        assert result is True
        assert migrator.results["migrated"] == 0  # Only updated after migrate_bulk

        # Verify migrated content
        frontmatter, body = migrator._parse_frontmatter(sample_v1_task)
        assert frontmatter["schema_version"] == "2"
        assert frontmatter["id"] == "task-001"
        assert frontmatter["title"] == "Example task"
        assert "This is a test task" in body

        # Verify backup was created
        backup_path = sample_v1_task.with_suffix(".md.bak")
        assert backup_path.exists()

    def test_migrate_already_v2(self, sample_v2_task):
        """Test migrating already v2 task is skipped."""
        migrator = TaskMigrator()
        result = migrator.migrate(sample_v2_task)

        assert result is False
        assert len(migrator.migration_log) == 1
        assert migrator.migration_log[0]["status"] == "skipped"

        # Verify no backup was created
        backup_path = sample_v2_task.with_suffix(".md.bak")
        assert not backup_path.exists()

    def test_migrate_preserves_all_fields(self, sample_v1_task):
        """Test that migration preserves all original fields."""
        migrator = TaskMigrator()
        original_frontmatter, _ = migrator._parse_frontmatter(sample_v1_task)

        migrator.migrate(sample_v1_task)

        migrated_frontmatter, _ = migrator._parse_frontmatter(sample_v1_task)

        # All original fields should be preserved
        for key, value in original_frontmatter.items():
            assert key in migrated_frontmatter
            assert migrated_frontmatter[key] == value

        # Schema version should be added
        assert migrated_frontmatter["schema_version"] == "2"

    def test_migrate_preserves_body(self, sample_v1_task):
        """Test that migration preserves body content."""
        migrator = TaskMigrator()
        _, original_body = migrator._parse_frontmatter(sample_v1_task)

        migrator.migrate(sample_v1_task)

        _, migrated_body = migrator._parse_frontmatter(sample_v1_task)

        assert migrated_body == original_body

    def test_migrate_dry_run(self, sample_v1_task):
        """Test dry-run mode doesn't modify files."""
        migrator = TaskMigrator(dry_run=True)
        original_content = sample_v1_task.read_text()

        result = migrator.migrate(sample_v1_task)

        assert result is True
        assert sample_v1_task.read_text() == original_content

        # Verify log shows would_migrate
        assert len(migrator.migration_log) == 1
        assert migrator.migration_log[0]["status"] == "would_migrate"

        # Verify no backup was created
        backup_path = sample_v1_task.with_suffix(".md.bak")
        assert not backup_path.exists()

    def test_migrate_empty_file_raises_error(self, empty_task_file):
        """Test that empty file raises error."""
        migrator = TaskMigrator()

        with pytest.raises(MigrationError, match="Empty file"):
            migrator.migrate(empty_task_file)

    def test_migrate_invalid_yaml_raises_error(self, invalid_yaml_task):
        """Test that invalid YAML raises error."""
        migrator = TaskMigrator()

        with pytest.raises(MigrationError, match="Invalid YAML"):
            migrator.migrate(invalid_yaml_task)

    def test_migrate_no_frontmatter_raises_error(self, no_frontmatter_task):
        """Test that missing frontmatter raises error."""
        migrator = TaskMigrator()

        with pytest.raises(MigrationError, match="No valid frontmatter"):
            migrator.migrate(no_frontmatter_task)

    def test_migrate_nonexistent_file_raises_error(self, tmp_path):
        """Test that nonexistent file raises error."""
        migrator = TaskMigrator()
        nonexistent = tmp_path / "does-not-exist.md"

        with pytest.raises(MigrationError, match="not found"):
            migrator.migrate(nonexistent)

    def test_migrate_preserves_upstream_fields(self, sample_v2_with_upstream):
        """Test that existing upstream fields are preserved."""
        migrator = TaskMigrator()
        original_frontmatter, _ = migrator._parse_frontmatter(sample_v2_with_upstream)

        # This should be skipped since it's already v2
        result = migrator.migrate(sample_v2_with_upstream)
        assert result is False

        # But verify upstream fields are intact
        migrated_frontmatter, _ = migrator._parse_frontmatter(sample_v2_with_upstream)
        assert "upstream" in migrated_frontmatter
        assert migrated_frontmatter["upstream"]["provider"] == "github"
        assert migrated_frontmatter["upstream"]["id"] == "owner/repo#123"

    def test_migrate_bulk(self, tmp_path):
        """Test bulk migration of multiple tasks."""
        # Create multiple v1 tasks
        for i in range(1, 6):
            task_file = tmp_path / f"task-{i:03d} - Test.md"
            content = f"""---
id: task-{i:03d}
title: Test task {i}
status: To Do
---

## Description
Task {i}
"""
            task_file.write_text(content)

        # Create one v2 task (should be skipped)
        v2_task = tmp_path / "task-006 - Already-V2.md"
        v2_task.write_text("""---
id: task-006
title: Already v2
status: Done
schema_version: '2'
---

Done
""")

        migrator = TaskMigrator()
        results = migrator.migrate_bulk(tmp_path)

        assert results["migrated"] == 5
        assert results["skipped"] == 1
        assert results["errors"] == 0
        assert results["backed_up"] == 5

        # Verify all v1 tasks were migrated
        for i in range(1, 6):
            task_file = tmp_path / f"task-{i:03d} - Test.md"
            frontmatter, _ = migrator._parse_frontmatter(task_file)
            assert frontmatter["schema_version"] == "2"

    def test_migrate_bulk_with_errors(self, tmp_path, invalid_yaml_task):
        """Test bulk migration handles errors gracefully."""
        # Create one valid task
        valid_task = tmp_path / "task-001 - Valid.md"
        valid_task.write_text("""---
id: task-001
title: Valid
status: To Do
---

Body
""")

        migrator = TaskMigrator()
        results = migrator.migrate_bulk(tmp_path)

        assert results["migrated"] == 1
        assert results["errors"] == 1

        # Check error log
        error_logs = [log for log in migrator.migration_log if log["status"] == "error"]
        assert len(error_logs) == 1

    def test_migrate_bulk_dry_run(self, tmp_path):
        """Test bulk dry-run doesn't modify files."""
        # Create tasks
        for i in range(1, 4):
            task_file = tmp_path / f"task-{i:03d} - Test.md"
            task_file.write_text(f"""---
id: task-{i:03d}
title: Test {i}
status: To Do
---

Body
""")

        migrator = TaskMigrator(dry_run=True)
        results = migrator.migrate_bulk(tmp_path)

        assert results["migrated"] == 3
        assert results["backed_up"] == 0  # No backups in dry-run

        # Verify files weren't modified
        for i in range(1, 4):
            task_file = tmp_path / f"task-{i:03d} - Test.md"
            frontmatter, _ = migrator._parse_frontmatter(task_file)
            assert "schema_version" not in frontmatter

    def test_migrate_bulk_empty_directory(self, tmp_path):
        """Test bulk migration on empty directory."""
        migrator = TaskMigrator()
        results = migrator.migrate_bulk(tmp_path)

        assert results["migrated"] == 0
        assert results["skipped"] == 0
        assert results["errors"] == 0

    def test_get_migration_report(self, sample_v1_task):
        """Test migration report generation."""
        migrator = TaskMigrator()
        migrator.migrate(sample_v1_task)

        report = migrator.get_migration_report()

        assert "Task Schema Migration Report" in report
        assert "Migrated: 0" in report  # migrate() doesn't update counter
        assert "task-001" in report

    def test_get_migration_report_dry_run(self, sample_v1_task):
        """Test migration report shows dry-run mode."""
        migrator = TaskMigrator(dry_run=True)
        migrator.migrate(sample_v1_task)

        report = migrator.get_migration_report()

        assert "DRY RUN MODE" in report
        assert "No files were modified" in report

    def test_backup_restore_on_failure(self, sample_v1_task, monkeypatch):
        """Test that backup is restored on migration failure."""
        migrator = TaskMigrator()

        # Force write to fail
        def failing_write(*args, **kwargs):
            raise Exception("Simulated write failure")

        monkeypatch.setattr(Path, "write_text", failing_write)

        original_content = sample_v1_task.read_text()

        with pytest.raises(MigrationError):
            migrator.migrate(sample_v1_task)

        # Verify original content was restored
        assert sample_v1_task.read_text() == original_content

    def test_cleanup_backups(self, tmp_path):
        """Test cleanup of backup files."""
        from flowspec_cli.satellite.migration import cleanup_backups

        # Create some backup files
        for i in range(1, 4):
            backup = tmp_path / f"task-{i:03d} - Test.md.bak"
            backup.write_text("backup")

        count = cleanup_backups(tmp_path)

        assert count == 3
        assert not list(tmp_path.glob("*.bak"))

    def test_version_comparison(self):
        """Test version comparison logic."""
        migrator = TaskMigrator()

        assert migrator._version_gte("2", "1") is True
        assert migrator._version_gte("2", "2") is True
        assert migrator._version_gte("1", "2") is False
        assert migrator._version_gte("10", "2") is True

    def test_migration_log_structure(self, sample_v1_task):
        """Test migration log has correct structure."""
        migrator = TaskMigrator()
        migrator.migrate(sample_v1_task)

        assert len(migrator.migration_log) == 2  # backup + migrated
        for entry in migrator.migration_log:
            assert "timestamp" in entry
            assert "path" in entry
            assert "status" in entry
            assert "message" in entry


class TestEdgeCases:
    """Tests for edge cases and corner scenarios."""

    def test_migrate_task_with_special_characters(self, tmp_path):
        """Test migration handles special characters in content."""
        task_file = tmp_path / "task-special.md"
        content = """---
id: task-special
title: "Task with special chars: @#$%^&*()"
status: To Do
labels:
  - "tag:value"
  - "another/tag"
---

## Description

This has unicode: 日本語, emoji: 🎉, and symbols: <>&"'
"""
        task_file.write_text(content)

        migrator = TaskMigrator()
        result = migrator.migrate(task_file)

        assert result is True
        frontmatter, body = migrator._parse_frontmatter(task_file)
        assert frontmatter["schema_version"] == "2"
        assert "🎉" in body

    def test_migrate_task_with_multiline_strings(self, tmp_path):
        """Test migration handles multiline YAML strings."""
        task_file = tmp_path / "task-multiline.md"
        content = """---
id: task-multiline
title: Task with multiline
status: To Do
description: |
  This is a
  multiline
  description
---

Body
"""
        task_file.write_text(content)

        migrator = TaskMigrator()
        result = migrator.migrate(task_file)

        assert result is True
        frontmatter, _ = migrator._parse_frontmatter(task_file)
        assert "multiline" in frontmatter.get("description", "")

    def test_migrate_preserves_field_order(self, sample_v1_task):
        """Test that migration preserves field order (best effort)."""
        migrator = TaskMigrator()
        original_frontmatter, _ = migrator._parse_frontmatter(sample_v1_task)
        original_keys = list(original_frontmatter.keys())

        migrator.migrate(sample_v1_task)

        migrated_frontmatter, _ = migrator._parse_frontmatter(sample_v1_task)
        migrated_keys = list(migrated_frontmatter.keys())

        # schema_version should be added at the end
        assert migrated_keys[-1] == "schema_version"
        # Original keys should be preserved
        assert all(key in migrated_keys for key in original_keys)
