"""Unit tests for push_rules.scaffold module.

Tests cover:
- Push rules file generation
- State directory creation
- Idempotent behavior
- Gitignore updates
"""

import json
from pathlib import Path

import pytest

from specify_cli.push_rules.scaffold import (
    DEFAULT_PUSH_RULES_CONTENT,
    get_scaffold_summary,
    get_template_content,
    scaffold_push_rules,
)


class TestGetTemplateContent:
    """Tests for get_template_content function."""

    def test_returns_string(self) -> None:
        """Test that template content is returned as string."""
        content = get_template_content()
        assert isinstance(content, str)
        assert len(content) > 0

    def test_contains_frontmatter(self) -> None:
        """Test that template contains YAML frontmatter."""
        content = get_template_content()
        assert content.startswith("---")
        assert "version:" in content
        assert "rebase_policy:" in content

    def test_contains_required_sections(self) -> None:
        """Test that template contains required configuration sections."""
        content = get_template_content()
        assert "lint:" in content
        assert "test:" in content
        assert "janitor_settings:" in content
        assert "branch_naming_pattern:" in content


class TestScaffoldPushRules:
    """Tests for scaffold_push_rules function."""

    def test_creates_push_rules_file(self, tmp_path: Path) -> None:
        """Test that push-rules.md is created."""
        result = scaffold_push_rules(tmp_path)

        push_rules = tmp_path / "push-rules.md"
        assert push_rules.exists()
        assert push_rules in result["created"]

    def test_creates_state_directory(self, tmp_path: Path) -> None:
        """Test that .specify/state/ directory is created."""
        scaffold_push_rules(tmp_path)

        state_dir = tmp_path / ".specify" / "state"
        assert state_dir.exists()
        assert state_dir.is_dir()

    def test_creates_janitor_timestamp(self, tmp_path: Path) -> None:
        """Test that janitor-last-run file is created."""
        result = scaffold_push_rules(tmp_path)

        timestamp_file = tmp_path / ".specify" / "state" / "janitor-last-run"
        assert timestamp_file.exists()
        assert timestamp_file in result["created"]

        # Verify it contains an ISO timestamp
        content = timestamp_file.read_text()
        assert "T" in content  # ISO format contains T

    def test_creates_pending_cleanup_json(self, tmp_path: Path) -> None:
        """Test that pending-cleanup.json is created."""
        result = scaffold_push_rules(tmp_path)

        cleanup_file = tmp_path / ".specify" / "state" / "pending-cleanup.json"
        assert cleanup_file.exists()
        assert cleanup_file in result["created"]

        # Verify it's valid JSON with expected structure
        data = json.loads(cleanup_file.read_text())
        assert "last_updated" in data
        assert "merged_branches" in data
        assert "orphaned_worktrees" in data
        assert data["merged_branches"] == []

    def test_creates_gitignore_if_missing(self, tmp_path: Path) -> None:
        """Test that .gitignore is created if it doesn't exist."""
        result = scaffold_push_rules(tmp_path)

        gitignore = tmp_path / ".gitignore"
        assert gitignore.exists()
        content = gitignore.read_text()
        assert ".specify/state/" in content

    def test_updates_existing_gitignore(self, tmp_path: Path) -> None:
        """Test that .gitignore is updated if it exists."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("node_modules/\n")

        scaffold_push_rules(tmp_path)

        content = gitignore.read_text()
        assert "node_modules/" in content
        assert ".specify/state/" in content

    def test_does_not_duplicate_gitignore_entry(self, tmp_path: Path) -> None:
        """Test that .gitignore entry is not duplicated."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("node_modules/\n.specify/state/\n")

        scaffold_push_rules(tmp_path)

        content = gitignore.read_text()
        # Should only appear once
        assert content.count(".specify/state/") == 1


class TestIdempotentBehavior:
    """Tests for idempotent behavior of scaffold."""

    def test_skips_existing_push_rules(self, tmp_path: Path) -> None:
        """Test that existing push-rules.md is not overwritten."""
        push_rules = tmp_path / "push-rules.md"
        push_rules.write_text("# Existing content\n")

        result = scaffold_push_rules(tmp_path)

        assert push_rules in result["skipped"]
        assert push_rules not in result["created"]
        assert push_rules.read_text() == "# Existing content\n"

    def test_skips_existing_janitor_timestamp(self, tmp_path: Path) -> None:
        """Test that existing janitor-last-run is not overwritten."""
        state_dir = tmp_path / ".specify" / "state"
        state_dir.mkdir(parents=True)
        timestamp_file = state_dir / "janitor-last-run"
        timestamp_file.write_text("2024-01-01T00:00:00Z")

        result = scaffold_push_rules(tmp_path)

        assert timestamp_file in result["skipped"]
        assert timestamp_file.read_text() == "2024-01-01T00:00:00Z"

    def test_skips_existing_pending_cleanup(self, tmp_path: Path) -> None:
        """Test that existing pending-cleanup.json is not overwritten."""
        state_dir = tmp_path / ".specify" / "state"
        state_dir.mkdir(parents=True)
        cleanup_file = state_dir / "pending-cleanup.json"
        original_data = {"custom": "data"}
        cleanup_file.write_text(json.dumps(original_data))

        result = scaffold_push_rules(tmp_path)

        assert cleanup_file in result["skipped"]
        assert json.loads(cleanup_file.read_text()) == original_data

    def test_force_overwrites_files(self, tmp_path: Path) -> None:
        """Test that force=True overwrites existing files."""
        push_rules = tmp_path / "push-rules.md"
        push_rules.write_text("# Old content\n")

        state_dir = tmp_path / ".specify" / "state"
        state_dir.mkdir(parents=True)
        timestamp_file = state_dir / "janitor-last-run"
        timestamp_file.write_text("2024-01-01T00:00:00Z")

        result = scaffold_push_rules(tmp_path, force=True)

        # All files should be in created, not skipped
        assert push_rules in result["created"]
        assert timestamp_file in result["created"]
        assert push_rules.read_text() != "# Old content\n"

    def test_second_run_reports_skipped(self, tmp_path: Path) -> None:
        """Test that running twice reports files as skipped."""
        # First run creates files
        result1 = scaffold_push_rules(tmp_path)
        assert len(result1["created"]) > 0
        assert len(result1["skipped"]) == 0

        # Second run skips existing files
        result2 = scaffold_push_rules(tmp_path)
        assert len(result2["created"]) == 0
        assert len(result2["skipped"]) > 0


class TestCustomTemplateContent:
    """Tests for custom template content support."""

    def test_accepts_custom_template(self, tmp_path: Path) -> None:
        """Test that custom template content is used."""
        custom_content = "---\nversion: '2.0'\n---\n# Custom Rules\n"

        scaffold_push_rules(tmp_path, template_content=custom_content)

        push_rules = tmp_path / "push-rules.md"
        assert push_rules.read_text() == custom_content


class TestGetScaffoldSummary:
    """Tests for get_scaffold_summary function."""

    def test_summary_created_only(self) -> None:
        """Test summary when only files are created."""
        result = {
            "created": [Path("a.md"), Path("b.md")],
            "skipped": [],
        }

        summary = get_scaffold_summary(result)
        assert "created 2 files" in summary
        assert "skipped" not in summary

    def test_summary_skipped_only(self) -> None:
        """Test summary when only files are skipped."""
        result = {
            "created": [],
            "skipped": [Path("a.md")],
        }

        summary = get_scaffold_summary(result)
        assert "skipped 1 existing" in summary
        assert "created" not in summary

    def test_summary_mixed(self) -> None:
        """Test summary with both created and skipped."""
        result = {
            "created": [Path("a.md")],
            "skipped": [Path("b.md"), Path("c.md")],
        }

        summary = get_scaffold_summary(result)
        assert "created 1 files" in summary
        assert "skipped 2 existing" in summary

    def test_summary_empty(self) -> None:
        """Test summary when nothing to do."""
        result = {"created": [], "skipped": []}

        summary = get_scaffold_summary(result)
        assert summary == "nothing to do"


class TestValidation:
    """Tests that created files are valid."""

    def test_created_push_rules_is_valid(self, tmp_path: Path) -> None:
        """Test that created push-rules.md passes validation."""
        from specify_cli.push_rules import load_push_rules

        scaffold_push_rules(tmp_path)

        push_rules_path = tmp_path / "push-rules.md"
        config = load_push_rules(push_rules_path)

        assert config.version == "1.0"
        assert config.enabled is True
        assert config.rebase_policy.enforcement.value == "strict"

    def test_pending_cleanup_json_valid(self, tmp_path: Path) -> None:
        """Test that pending-cleanup.json is valid JSON."""
        scaffold_push_rules(tmp_path)

        cleanup_path = tmp_path / ".specify" / "state" / "pending-cleanup.json"
        data = json.loads(cleanup_path.read_text())

        # Verify expected structure
        assert isinstance(data["merged_branches"], list)
        assert isinstance(data["orphaned_worktrees"], list)
        assert isinstance(data["non_compliant_branches"], dict)
        assert data["last_updated"] is not None


class TestEdgeCases:
    """Tests for edge cases."""

    def test_handles_readonly_gitignore(self, tmp_path: Path) -> None:
        """Test handling when .gitignore might have issues."""
        # Create gitignore without trailing newline
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("node_modules/")  # No newline

        scaffold_push_rules(tmp_path)

        content = gitignore.read_text()
        # Should have proper separation
        assert "node_modules/" in content
        assert ".specify/state/" in content

    def test_deep_nested_state_directory(self, tmp_path: Path) -> None:
        """Test creation of nested .specify/state/ structure."""
        scaffold_push_rules(tmp_path)

        # Verify full path exists
        state_dir = tmp_path / ".specify" / "state"
        assert state_dir.exists()

        # Verify parent .specify exists
        specify_dir = tmp_path / ".specify"
        assert specify_dir.exists()

    def test_works_with_existing_specify_dir(self, tmp_path: Path) -> None:
        """Test scaffold works when .specify/ already exists."""
        specify_dir = tmp_path / ".specify"
        specify_dir.mkdir()
        (specify_dir / "other_file.txt").write_text("existing content")

        scaffold_push_rules(tmp_path)

        # Original file should still exist
        assert (specify_dir / "other_file.txt").exists()
        # State directory should be created
        assert (specify_dir / "state").exists()
