"""Tests for constitution diff and merge commands."""

import pytest
from typer.testing import CliRunner

from specify_cli import app

runner = CliRunner()


@pytest.fixture
def temp_constitution(tmp_path):
    """Create a temporary constitution file."""
    memory_dir = tmp_path / "memory"
    memory_dir.mkdir()
    constitution_path = memory_dir / "constitution.md"

    # Create a light tier constitution with some customizations
    content = """# Test Project Constitution
<!-- TIER: Light - Minimal controls for startups/hobby projects -->
<!-- NEEDS_VALIDATION: Project name -->

## Core Principles

### Simplicity First
Keep things simple. Ship fast, iterate quickly. Avoid over-engineering.

### Working Software
Prioritize working software over documentation. Code that runs is better than perfect designs.

### Custom Section
This is a custom section added by the user.

## Development Workflow

### Git Practices
<!-- SECTION:GIT:BEGIN -->
- Feature branches encouraged
- Commit messages should be descriptive
- DCO sign-off required: `git commit -s`
<!-- SECTION:GIT:END -->

**Version**: 1.0.0 | **Created**: 2024-01-01
"""
    constitution_path.write_text(content)
    return tmp_path


class TestConstitutionDiff:
    """Test constitution diff command."""

    def test_diff_missing_constitution(self, tmp_path):
        """Test diff when constitution doesn't exist."""
        result = runner.invoke(
            app,
            [
                "constitution",
                "diff",
                "--path",
                str(tmp_path / "memory" / "constitution.md"),
            ],
        )
        assert result.exit_code == 1
        assert "Constitution not found" in result.stdout

    def test_diff_matching_constitution(self, tmp_path):
        """Test diff when constitution matches template."""
        # Create constitution that exactly matches light template
        from specify_cli import CONSTITUTION_TEMPLATES

        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()
        constitution_path = memory_dir / "constitution.md"
        constitution_path.write_text(CONSTITUTION_TEMPLATES["light"])

        result = runner.invoke(
            app, ["constitution", "diff", "--path", str(constitution_path)]
        )
        assert result.exit_code == 0
        assert "matches the light tier template" in result.stdout

    def test_diff_with_customizations(self, temp_constitution):
        """Test diff shows customizations."""
        constitution_path = temp_constitution / "memory" / "constitution.md"
        result = runner.invoke(
            app, ["constitution", "diff", "--path", str(constitution_path)]
        )
        assert result.exit_code == 0
        assert "Comparing light tier template" in result.stdout

    def test_diff_explicit_tier(self, temp_constitution):
        """Test diff with explicitly specified tier."""
        constitution_path = temp_constitution / "memory" / "constitution.md"
        result = runner.invoke(
            app,
            [
                "constitution",
                "diff",
                "--path",
                str(constitution_path),
                "--tier",
                "medium",
            ],
        )
        assert result.exit_code == 0
        assert "Comparing medium tier template" in result.stdout

    def test_diff_detects_heavy_tier(self, tmp_path):
        """Test diff auto-detects heavy tier."""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()
        constitution_path = memory_dir / "constitution.md"

        # Create heavy tier constitution
        content = """# Project Constitution
<!-- TIER: Heavy - Strict controls for enterprise/regulated environments -->

## Core Principles (NON-NEGOTIABLE)
Test content.
"""
        constitution_path.write_text(content)

        result = runner.invoke(
            app, ["constitution", "diff", "--path", str(constitution_path)]
        )
        assert result.exit_code == 0
        assert "Comparing heavy tier template" in result.stdout


class TestConstitutionMerge:
    """Test constitution merge command."""

    def test_merge_missing_constitution(self, tmp_path):
        """Test merge when constitution doesn't exist."""
        result = runner.invoke(
            app,
            [
                "constitution",
                "merge",
                "--path",
                str(tmp_path / "memory" / "constitution.md"),
            ],
        )
        assert result.exit_code == 1
        assert "Constitution not found" in result.stdout

    def test_merge_creates_backup(self, temp_constitution):
        """Test merge creates backup file."""
        constitution_path = temp_constitution / "memory" / "constitution.md"
        result = runner.invoke(
            app, ["constitution", "merge", "--path", str(constitution_path)]
        )
        assert result.exit_code == 0
        assert "Backup created" in result.stdout

        # Check backup file exists
        backup_files = list(constitution_path.parent.glob("constitution.backup.*.md"))
        assert len(backup_files) == 1

    def test_merge_without_backup(self, temp_constitution):
        """Test merge with --no-backup flag."""
        constitution_path = temp_constitution / "memory" / "constitution.md"
        result = runner.invoke(
            app,
            ["constitution", "merge", "--path", str(constitution_path), "--no-backup"],
        )
        assert result.exit_code == 0
        assert "Backup created" not in result.stdout

        # Check no backup files exist
        backup_files = list(constitution_path.parent.glob("constitution.backup.*.md"))
        assert len(backup_files) == 0

    def test_merge_creates_merged_file(self, temp_constitution):
        """Test merge creates merged constitution file."""
        constitution_path = temp_constitution / "memory" / "constitution.md"
        merged_path = temp_constitution / "memory" / "constitution-merged.md"

        result = runner.invoke(
            app, ["constitution", "merge", "--path", str(constitution_path)]
        )
        assert result.exit_code == 0
        assert merged_path.exists()

        # Check merged file has review header
        merged_content = merged_path.read_text()
        assert "MERGED CONSTITUTION - REVIEW REQUIRED" in merged_content
        assert "Original tier: light" in merged_content
        assert "Test Project Constitution" in merged_content

    def test_merge_custom_output_path(self, temp_constitution):
        """Test merge with custom output path."""
        constitution_path = temp_constitution / "memory" / "constitution.md"
        custom_output = temp_constitution / "custom-merged.md"

        result = runner.invoke(
            app,
            [
                "constitution",
                "merge",
                "--path",
                str(constitution_path),
                "--output",
                str(custom_output),
            ],
        )
        assert result.exit_code == 0
        assert custom_output.exists()

    def test_merge_detects_medium_tier(self, tmp_path):
        """Test merge auto-detects medium tier."""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()
        constitution_path = memory_dir / "constitution.md"

        # Create medium tier constitution
        content = """# Project Constitution
<!-- TIER: Medium - Standard controls for typical business projects -->

## Core Principles
Test content.
"""
        constitution_path.write_text(content)

        result = runner.invoke(
            app, ["constitution", "merge", "--path", str(constitution_path)]
        )
        assert result.exit_code == 0

        merged_path = memory_dir / "constitution-merged.md"
        merged_content = merged_path.read_text()
        assert "Original tier: medium" in merged_content

    def test_merge_shows_next_steps(self, temp_constitution):
        """Test merge output includes next steps."""
        constitution_path = temp_constitution / "memory" / "constitution.md"
        result = runner.invoke(
            app, ["constitution", "merge", "--path", str(constitution_path)]
        )
        assert result.exit_code == 0
        assert "Next steps:" in result.stdout
        assert "Review changes" in result.stdout
        assert "Edit merged file" in result.stdout
        assert "Replace when ready" in result.stdout
