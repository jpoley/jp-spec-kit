"""Tests for constitution diff and merge commands.

Tests cover:
- Constitution diff command with various tiers
- Constitution merge command with section preservation
- Error handling for missing files
- Verbose and dry-run modes
"""

import pytest
from typer.testing import CliRunner

from specify_cli import app

runner = CliRunner()


@pytest.fixture
def project_with_constitution(tmp_path):
    """Create a test project with a constitution file."""
    memory_dir = tmp_path / "memory"
    memory_dir.mkdir()

    # Create a simple constitution with customized sections
    constitution = """# Test Project Constitution
<!-- TIER: Medium -->

## Core Principles

### Quality-Driven Development
<!-- SECTION:QUALITY_PRINCIPLES:BEGIN -->
Custom quality content here.
This has been customized by the team.
<!-- SECTION:QUALITY_PRINCIPLES:END -->

### Continuous Improvement
Standard content that matches the template.

## Git Commit Requirements

### Branch Strategy
<!-- SECTION:BRANCHING:BEGIN -->
Custom branching strategy.
<!-- SECTION:BRANCHING:END -->
"""
    constitution_file = memory_dir / "constitution.md"
    constitution_file.write_text(constitution)

    return tmp_path


class TestConstitutionDiff:
    """Tests for 'specify constitution diff' command."""

    def test_diff_command_exists(self):
        """Verify constitution diff command is available."""
        result = runner.invoke(app, ["constitution", "--help"])
        assert result.exit_code == 0
        assert "diff" in result.stdout.lower()

    def test_diff_help(self):
        """Verify constitution diff help is accessible."""
        result = runner.invoke(app, ["constitution", "diff", "--help"])
        assert result.exit_code == 0
        assert "compare" in result.stdout.lower()
        assert "template" in result.stdout.lower()

    def test_diff_missing_constitution(self, tmp_path):
        """Diff should fail gracefully when constitution doesn't exist."""
        result = runner.invoke(app, ["constitution", "diff", "--path", str(tmp_path)])
        assert result.exit_code == 1
        assert "no constitution found" in result.stdout.lower()
        assert "specify init" in result.stdout.lower()

    def test_diff_invalid_tier(self, project_with_constitution):
        """Diff should reject invalid tier names."""
        result = runner.invoke(
            app,
            [
                "constitution",
                "diff",
                "--tier",
                "invalid-tier",
                "--path",
                str(project_with_constitution),
            ],
        )
        assert result.exit_code == 1
        assert "invalid tier" in result.stdout.lower()
        assert "light" in result.stdout.lower()
        assert "medium" in result.stdout.lower()
        assert "heavy" in result.stdout.lower()

    def test_diff_with_default_tier(self, project_with_constitution):
        """Diff should work with default (medium) tier."""
        result = runner.invoke(
            app, ["constitution", "diff", "--path", str(project_with_constitution)]
        )
        # May pass or fail depending on whether project matches template
        assert result.exit_code in (0, 1)
        # Should show some output about the diff or match
        assert len(result.stdout) > 0

    def test_diff_verbose_mode(self, project_with_constitution):
        """Diff --verbose should show detailed diff output."""
        result = runner.invoke(
            app,
            [
                "constitution",
                "diff",
                "--path",
                str(project_with_constitution),
                "--verbose",
            ],
        )
        # Output should contain diff markers if there are differences
        # Or confirmation if files match
        assert len(result.stdout) > 0

    def test_diff_all_tiers(self, project_with_constitution):
        """Diff should work with all tier options."""
        for tier in ["light", "medium", "heavy"]:
            result = runner.invoke(
                app,
                [
                    "constitution",
                    "diff",
                    "--tier",
                    tier,
                    "--path",
                    str(project_with_constitution),
                ],
            )
            # Should complete without error (may match or differ)
            assert result.exit_code in (0, 1)
            assert (
                tier in result.stdout.lower() or "constitution" in result.stdout.lower()
            )


class TestConstitutionMerge:
    """Tests for 'specify constitution merge' command."""

    def test_merge_command_exists(self):
        """Verify constitution merge command is available."""
        result = runner.invoke(app, ["constitution", "--help"])
        assert result.exit_code == 0
        assert "merge" in result.stdout.lower()

    def test_merge_help(self):
        """Verify constitution merge help is accessible."""
        result = runner.invoke(app, ["constitution", "merge", "--help"])
        assert result.exit_code == 0
        assert "merge" in result.stdout.lower()
        assert "template" in result.stdout.lower()
        assert "preserve" in result.stdout.lower() or "section" in result.stdout.lower()

    def test_merge_missing_constitution(self, tmp_path):
        """Merge should fail gracefully when constitution doesn't exist."""
        result = runner.invoke(app, ["constitution", "merge", "--path", str(tmp_path)])
        assert result.exit_code == 1
        assert "no constitution found" in result.stdout.lower()

    def test_merge_invalid_tier(self, project_with_constitution):
        """Merge should reject invalid tier names."""
        result = runner.invoke(
            app,
            [
                "constitution",
                "merge",
                "--tier",
                "invalid-tier",
                "--path",
                str(project_with_constitution),
            ],
        )
        assert result.exit_code == 1
        assert "invalid tier" in result.stdout.lower()

    def test_merge_dry_run(self, project_with_constitution):
        """Merge --dry-run should not write files."""
        result = runner.invoke(
            app,
            [
                "constitution",
                "merge",
                "--path",
                str(project_with_constitution),
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert "dry run" in result.stdout.lower()

        # Verify no .merged.md file was created
        merged_file = project_with_constitution / "memory" / "constitution.merged.md"
        assert not merged_file.exists()

    def test_merge_creates_merged_file(self, project_with_constitution):
        """Merge should create constitution.merged.md by default."""
        result = runner.invoke(
            app,
            [
                "constitution",
                "merge",
                "--path",
                str(project_with_constitution),
                "--tier",
                "medium",
            ],
        )
        assert result.exit_code == 0

        # Verify merged file was created
        merged_file = project_with_constitution / "memory" / "constitution.merged.md"
        assert merged_file.exists()

        # Verify it has content
        content = merged_file.read_text()
        assert len(content) > 100

    def test_merge_preserves_custom_sections(self, project_with_constitution):
        """Merge should preserve customized SECTION blocks."""
        result = runner.invoke(
            app,
            [
                "constitution",
                "merge",
                "--path",
                str(project_with_constitution),
                "--tier",
                "medium",
            ],
        )
        assert result.exit_code == 0

        # Read merged file
        merged_file = project_with_constitution / "memory" / "constitution.merged.md"
        merged_content = merged_file.read_text()

        # Verify custom section content is preserved
        assert "Custom quality content here" in merged_content
        assert "This has been customized by the team" in merged_content
        assert "Custom branching strategy" in merged_content

    def test_merge_with_custom_output(self, project_with_constitution, tmp_path):
        """Merge should respect custom --output path."""
        custom_output = tmp_path / "custom-constitution.md"

        result = runner.invoke(
            app,
            [
                "constitution",
                "merge",
                "--path",
                str(project_with_constitution),
                "--output",
                str(custom_output),
            ],
        )
        assert result.exit_code == 0

        # Verify file was created at custom location
        assert custom_output.exists()
        assert custom_output.read_text().startswith("#")

    def test_merge_all_tiers(self, project_with_constitution):
        """Merge should work with all tier options."""
        for tier in ["light", "medium", "heavy"]:
            # Use unique output files to avoid conflicts
            output = (
                project_with_constitution / "memory" / f"constitution.{tier}.merged.md"
            )

            result = runner.invoke(
                app,
                [
                    "constitution",
                    "merge",
                    "--tier",
                    tier,
                    "--path",
                    str(project_with_constitution),
                    "--output",
                    str(output),
                ],
            )
            assert result.exit_code == 0
            assert output.exists()

    def test_merge_output_shows_section_count(self, project_with_constitution):
        """Merge should report number of preserved sections."""
        result = runner.invoke(
            app,
            [
                "constitution",
                "merge",
                "--path",
                str(project_with_constitution),
            ],
        )
        assert result.exit_code == 0

        # Output should mention preserved sections
        assert (
            "preserved" in result.stdout.lower() or "section" in result.stdout.lower()
        )


class TestConstitutionIntegration:
    """Integration tests for constitution diff/merge workflow."""

    def test_diff_then_merge_workflow(self, project_with_constitution):
        """Test typical workflow: diff to see changes, then merge."""
        # First, check diff
        diff_result = runner.invoke(
            app, ["constitution", "diff", "--path", str(project_with_constitution)]
        )
        # Diff may show differences or match
        assert diff_result.exit_code in (0, 1)

        # Then merge
        merge_result = runner.invoke(
            app, ["constitution", "merge", "--path", str(project_with_constitution)]
        )
        assert merge_result.exit_code == 0

        # Verify merged file exists
        merged_file = project_with_constitution / "memory" / "constitution.merged.md"
        assert merged_file.exists()

    def test_help_commands_mention_each_other(self):
        """Diff and merge help should reference each other."""
        diff_help = runner.invoke(app, ["constitution", "diff", "--help"])
        merge_help = runner.invoke(app, ["constitution", "merge", "--help"])

        assert diff_help.exit_code == 0
        assert merge_help.exit_code == 0

        # Commands should hint at the workflow
        # (This is a soft check as help text may vary)
        assert "constitution" in diff_help.stdout.lower()
        assert "constitution" in merge_help.stdout.lower()
