"""Tests for backward compatibility of schema v2."""

import pytest

from specify_cli.satellite.migration import TaskMigrator


@pytest.fixture
def v1_task_comprehensive(tmp_path):
    """Create a comprehensive v1 task with all possible fields."""
    task_file = tmp_path / "task-v1-full.md"
    content = """---
id: task-001
title: Comprehensive v1 task
status: In Progress
assignee:
  - '@user1'
  - '@user2'
labels:
  - backend
  - api
  - P0
created_date: '2025-11-24'
updated_date: '2025-11-25 10:30'
dependencies:
  - task-002
  - task-003
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
This is a comprehensive v1 task with all typical fields.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 First criterion
- [x] #2 Second criterion (completed)
- [ ] #3 Third criterion with special chars: @#$%
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. First step
2. Second step
3. Third step
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Some implementation notes here.
<!-- SECTION:NOTES:END -->
"""
    task_file.write_text(content)
    return task_file


class TestBackwardCompatibility:
    """Tests ensuring v1 tasks remain valid and are backward compatible."""

    def test_v1_tasks_can_be_read(self, v1_task_comprehensive):
        """Test that v1 tasks can be read without migration."""
        migrator = TaskMigrator()

        # Should be able to parse v1 task
        frontmatter, body = migrator._parse_frontmatter(v1_task_comprehensive)

        assert frontmatter["id"] == "task-001"
        assert frontmatter["title"] == "Comprehensive v1 task"
        assert frontmatter["status"] == "In Progress"
        assert len(frontmatter["assignee"]) == 2
        assert len(frontmatter["labels"]) == 3
        assert "Implementation Plan" in body

    def test_v1_migration_preserves_all_fields(self, v1_task_comprehensive):
        """Test that migration preserves every field from v1."""
        migrator = TaskMigrator()
        original_fm, original_body = migrator._parse_frontmatter(v1_task_comprehensive)

        # Migrate
        migrator.migrate(v1_task_comprehensive)

        # Read migrated version
        migrated_fm, migrated_body = migrator._parse_frontmatter(v1_task_comprehensive)

        # Check all original fields preserved
        for key in original_fm.keys():
            assert key in migrated_fm, f"Field '{key}' missing after migration"
            assert migrated_fm[key] == original_fm[key], f"Field '{key}' value changed"

        # Body should be identical
        assert migrated_body == original_body

        # Schema version should be added
        assert migrated_fm["schema_version"] == "2"

    def test_v1_without_optional_fields(self, tmp_path):
        """Test v1 task with only required fields."""
        task_file = tmp_path / "task-minimal.md"
        content = """---
id: task-minimal
title: Minimal task
status: To Do
---

## Description

Just the basics.
"""
        task_file.write_text(content)

        migrator = TaskMigrator()
        result = migrator.migrate(task_file)

        assert result is True

        frontmatter, _ = migrator._parse_frontmatter(task_file)
        assert frontmatter["id"] == "task-minimal"
        assert frontmatter["schema_version"] == "2"

    def test_v1_with_multiline_assignees(self, tmp_path):
        """Test v1 task with list-style assignees."""
        task_file = tmp_path / "task-assignees.md"
        content = """---
id: task-001
title: Task with multiple assignees
status: To Do
assignee:
  - '@alice'
  - '@bob'
  - '@charlie'
---

Body
"""
        task_file.write_text(content)

        migrator = TaskMigrator()
        migrator.migrate(task_file)

        frontmatter, _ = migrator._parse_frontmatter(task_file)
        assert len(frontmatter["assignee"]) == 3
        assert "@alice" in frontmatter["assignee"]

    def test_v1_preserves_comment_markers(self, v1_task_comprehensive):
        """Test that section comment markers are preserved."""
        migrator = TaskMigrator()
        migrator.migrate(v1_task_comprehensive)

        content = v1_task_comprehensive.read_text()

        # Check all markers are still present
        assert "<!-- SECTION:DESCRIPTION:BEGIN -->" in content
        assert "<!-- SECTION:DESCRIPTION:END -->" in content
        assert "<!-- AC:BEGIN -->" in content
        assert "<!-- AC:END -->" in content
        assert "<!-- SECTION:PLAN:BEGIN -->" in content
        assert "<!-- SECTION:PLAN:END -->" in content

    def test_v1_preserves_acceptance_criteria_format(self, v1_task_comprehensive):
        """Test that AC checkboxes are preserved exactly."""
        migrator = TaskMigrator()
        original_content = v1_task_comprehensive.read_text()

        migrator.migrate(v1_task_comprehensive)

        migrated_content = v1_task_comprehensive.read_text()

        # Extract AC sections
        original_ac = original_content.split("<!-- AC:BEGIN -->")[1].split("<!-- AC:END -->")[0]
        migrated_ac = migrated_content.split("<!-- AC:BEGIN -->")[1].split("<!-- AC:END -->")[0]

        assert original_ac == migrated_ac

    def test_v1_with_empty_assignee_list(self, tmp_path):
        """Test v1 task with empty assignee field."""
        task_file = tmp_path / "task-empty-assignee.md"
        content = """---
id: task-001
title: Unassigned task
status: To Do
assignee:
---

Body
"""
        task_file.write_text(content)

        migrator = TaskMigrator()
        result = migrator.migrate(task_file)

        assert result is True

        frontmatter, _ = migrator._parse_frontmatter(task_file)
        assert frontmatter["assignee"] is None or frontmatter["assignee"] == []

    def test_v1_preserves_dependencies_list(self, v1_task_comprehensive):
        """Test that dependencies list is preserved."""
        migrator = TaskMigrator()
        migrator.migrate(v1_task_comprehensive)

        frontmatter, _ = migrator._parse_frontmatter(v1_task_comprehensive)
        assert "dependencies" in frontmatter
        assert len(frontmatter["dependencies"]) == 2
        assert "task-002" in frontmatter["dependencies"]
        assert "task-003" in frontmatter["dependencies"]

    def test_v2_optional_fields_not_added_by_default(self, tmp_path):
        """Test that migration doesn't add upstream/compliance unless needed."""
        task_file = tmp_path / "task-simple.md"
        content = """---
id: task-001
title: Simple task
status: To Do
---

Body
"""
        task_file.write_text(content)

        migrator = TaskMigrator()
        migrator.migrate(task_file)

        frontmatter, _ = migrator._parse_frontmatter(task_file)

        # These should NOT be added automatically
        assert "upstream" not in frontmatter
        assert "compliance" not in frontmatter

        # Only schema_version should be added
        assert "schema_version" in frontmatter

    def test_migration_is_idempotent(self, v1_task_comprehensive):
        """Test that migrating twice produces same result."""
        migrator = TaskMigrator()

        # First migration
        migrator.migrate(v1_task_comprehensive)
        first_content = v1_task_comprehensive.read_text()

        # Second migration (should be skipped)
        result = migrator.migrate(v1_task_comprehensive)
        assert result is False  # Skipped

        second_content = v1_task_comprehensive.read_text()

        # Content should be identical
        assert first_content == second_content
