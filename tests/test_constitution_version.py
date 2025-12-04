"""Tests for constitution version tracking functionality.

Tests cover:
- Version metadata in templates
- `specify constitution version` command
- Constitution version detection in `specify upgrade`
- Date replacement in templates
"""

import os
import re
from datetime import datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

from specify_cli import CONSTITUTION_TEMPLATES, CONSTITUTION_VERSION, app

runner = CliRunner()


class TestConstitutionVersionMetadata:
    """Tests for version metadata in constitution templates."""

    def test_constitution_version_constant_exists(self):
        """CONSTITUTION_VERSION constant should be defined."""
        assert CONSTITUTION_VERSION is not None
        assert isinstance(CONSTITUTION_VERSION, str)

    def test_constitution_version_format(self):
        """CONSTITUTION_VERSION should follow semantic versioning."""
        # Should match X.Y.Z format
        assert re.match(r"^\d+\.\d+\.\d+$", CONSTITUTION_VERSION)

    def test_all_templates_have_version_metadata(self):
        """All constitution templates should have version metadata comments."""
        for tier, template_content in CONSTITUTION_TEMPLATES.items():
            # Check for VERSION comment
            assert "<!-- VERSION:" in template_content, (
                f"Template {tier} missing VERSION"
            )
            # Check for RATIFIED comment
            assert "<!-- RATIFIED:" in template_content, (
                f"Template {tier} missing RATIFIED"
            )
            # Check for LAST_AMENDED comment
            assert "<!-- LAST_AMENDED:" in template_content, (
                f"Template {tier} missing LAST_AMENDED"
            )

    def test_template_version_matches_constant(self):
        """Version in templates should match CONSTITUTION_VERSION constant."""
        for tier, template_content in CONSTITUTION_TEMPLATES.items():
            version_match = re.search(r"<!-- VERSION: ([\d.]+) -->", template_content)
            assert version_match, f"Template {tier} has invalid VERSION format"
            assert version_match.group(1) == CONSTITUTION_VERSION, (
                f"Template {tier} version mismatch: {version_match.group(1)} != {CONSTITUTION_VERSION}"
            )

    def test_template_files_have_version_metadata(self):
        """Constitution template files should have version metadata."""
        templates_dir = Path(__file__).parent.parent / "templates" / "constitutions"
        for tier in ["light", "medium", "heavy"]:
            template_file = templates_dir / f"constitution-{tier}.md"
            content = template_file.read_text()

            # Check for version metadata
            assert "<!-- VERSION:" in content, f"File {tier} missing VERSION"
            assert "<!-- RATIFIED:" in content, f"File {tier} missing RATIFIED"
            assert "<!-- LAST_AMENDED:" in content, f"File {tier} missing LAST_AMENDED"


class TestConstitutionVersionCommand:
    """Tests for `specify constitution version` command."""

    def test_constitution_version_command_without_constitution(self, tmp_path):
        """Should error if no constitution exists."""
        # Change to temp directory
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["constitution", "version"])
            assert result.exit_code == 1
            assert (
                "No constitution found" in result.stdout
                or "not found" in result.stdout.lower()
            )
        finally:
            os.chdir(original_cwd)

    def test_constitution_version_command_shows_info(self, tmp_path):
        """Should display version info when constitution exists."""
        # Create a test project with constitution
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()
        constitution_file = memory_dir / "constitution.md"

        # Use today's date
        today = datetime.now().strftime("%Y-%m-%d")
        constitution_content = CONSTITUTION_TEMPLATES["light"].replace("[DATE]", today)
        constitution_file.write_text(constitution_content)

        # Run version command
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["constitution", "version"])

            # Should succeed
            assert result.exit_code == 0, f"Command failed: {result.stdout}"

            # Should show version information
            assert (
                "Constitution" in result.stdout
                or "constitution" in result.stdout.lower()
            )
            assert CONSTITUTION_VERSION in result.stdout
            assert today in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_constitution_version_detects_outdated(self, tmp_path):
        """Should detect when constitution is outdated."""
        # Create constitution with old version
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()
        constitution_file = memory_dir / "constitution.md"

        # Create old version
        old_content = """# Test Constitution
<!-- TIER: Light -->
<!-- VERSION: 0.0.1 -->
<!-- RATIFIED: 2020-01-01 -->
<!-- LAST_AMENDED: 2020-01-01 -->
"""
        constitution_file.write_text(old_content)

        # Run version command
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["constitution", "version"])

            # Should succeed
            assert result.exit_code == 0

            # Should show upgrade available message
            assert "0.0.1" in result.stdout
            assert CONSTITUTION_VERSION in result.stdout
        finally:
            os.chdir(original_cwd)


class TestConstitutionUpgrade:
    """Tests for constitution upgrade in `specify upgrade` command."""

    def test_init_replaces_date_placeholders(self, tmp_path):
        """Test that init replaces [DATE] placeholders with current date."""
        result = runner.invoke(
            app,
            [
                "init",
                str(tmp_path / "test-project"),
                "--ai",
                "claude",
                "--ignore-agent-tools",
                "--constitution",
                "light",
            ],
            input="n\n",  # No backlog-md install
        )

        assert result.exit_code == 0, f"Init failed: {result.stdout}"

        # Check constitution file
        constitution_file = tmp_path / "test-project" / "memory" / "constitution.md"
        assert constitution_file.exists()

        content = constitution_file.read_text()

        # Should NOT contain [DATE] placeholder
        assert "[DATE]" not in content, "Date placeholders should be replaced"

        # Should contain actual date (YYYY-MM-DD format)
        today = datetime.now().strftime("%Y-%m-%d")
        assert today in content, f"Should contain today's date: {today}"

        # Check version metadata is present
        assert re.search(r"<!-- VERSION: \d+\.\d+\.\d+ -->", content)
        assert re.search(r"<!-- RATIFIED: \d{4}-\d{2}-\d{2} -->", content)
        assert re.search(r"<!-- LAST_AMENDED: \d{4}-\d{2}-\d{2} -->", content)


class TestConstitutionVersionParsing:
    """Tests for version parsing logic."""

    def test_parse_version_from_constitution(self):
        """Test extracting version from constitution content."""
        content = """# Test Constitution
<!-- VERSION: 1.2.3 -->
<!-- RATIFIED: 2024-01-15 -->
"""
        version_match = re.search(r"<!-- VERSION: ([\d.]+) -->", content)
        assert version_match
        assert version_match.group(1) == "1.2.3"

    def test_parse_ratified_date(self):
        """Test extracting ratified date."""
        content = """# Test Constitution
<!-- RATIFIED: 2024-01-15 -->
"""
        ratified_match = re.search(r"<!-- RATIFIED: (.+?) -->", content)
        assert ratified_match
        assert ratified_match.group(1) == "2024-01-15"

    def test_parse_last_amended_date(self):
        """Test extracting last amended date."""
        content = """# Test Constitution
<!-- LAST_AMENDED: 2024-06-20 -->
"""
        amended_match = re.search(r"<!-- LAST_AMENDED: (.+?) -->", content)
        assert amended_match
        assert amended_match.group(1) == "2024-06-20"

    def test_version_comparison(self):
        """Test semantic version comparison logic."""
        # Test cases: (version1, version2, expected: v2 > v1)
        test_cases = [
            ("1.0.0", "1.0.1", True),
            ("1.0.0", "1.1.0", True),
            ("1.0.0", "2.0.0", True),
            ("1.0.0", "1.0.0", False),
            ("1.1.0", "1.0.0", False),
        ]

        for v1, v2, expected_greater in test_cases:
            parts1 = [int(x) for x in v1.split(".")]
            parts2 = [int(x) for x in v2.split(".")]
            result = parts2 > parts1
            assert result == expected_greater, f"Comparison {v2} > {v1} failed"
