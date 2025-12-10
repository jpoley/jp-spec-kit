"""Tests for constitution tier functionality in specify init command.

Tests cover:
- Constitution tier choices constant
- Invalid constitution tier validation
- Constitution help text in init command
- Constitution template file existence
"""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from specify_cli import CONSTITUTION_TIER_CHOICES, app

runner = CliRunner()


class TestConstitutionTierChoices:
    """Tests for CONSTITUTION_TIER_CHOICES constant."""

    def test_constitution_tiers_exist(self):
        """Verify all expected tiers are defined."""
        assert "light" in CONSTITUTION_TIER_CHOICES
        assert "medium" in CONSTITUTION_TIER_CHOICES
        assert "heavy" in CONSTITUTION_TIER_CHOICES

    def test_constitution_tier_count(self):
        """Verify exactly 3 tiers are defined."""
        assert len(CONSTITUTION_TIER_CHOICES) == 3

    def test_constitution_tier_descriptions(self):
        """Verify tier descriptions are non-empty strings."""
        for tier, description in CONSTITUTION_TIER_CHOICES.items():
            assert isinstance(description, str)
            assert len(description) > 0


class TestConstitutionTemplateFiles:
    """Tests for constitution template file existence."""

    @pytest.fixture
    def templates_dir(self):
        """Get the templates directory path."""
        return Path(__file__).parent.parent / "templates" / "constitutions"

    def test_light_template_exists(self, templates_dir):
        """Light tier template file should exist."""
        template_file = templates_dir / "constitution-light.md"
        assert template_file.exists(), f"Missing: {template_file}"

    def test_medium_template_exists(self, templates_dir):
        """Medium tier template file should exist."""
        template_file = templates_dir / "constitution-medium.md"
        assert template_file.exists(), f"Missing: {template_file}"

    def test_heavy_template_exists(self, templates_dir):
        """Heavy tier template file should exist."""
        template_file = templates_dir / "constitution-heavy.md"
        assert template_file.exists(), f"Missing: {template_file}"

    def test_templates_have_content(self, templates_dir):
        """All constitution templates should have content."""
        for tier in CONSTITUTION_TIER_CHOICES:
            template_file = templates_dir / f"constitution-{tier}.md"
            content = template_file.read_text()
            assert len(content) > 100, f"Template {tier} seems too short"

    def test_templates_have_section_markers(self, templates_dir):
        """Constitution templates should include SECTION markers for customization."""
        for tier in CONSTITUTION_TIER_CHOICES:
            template_file = templates_dir / f"constitution-{tier}.md"
            content = template_file.read_text()
            # At least one section marker should exist
            assert "SECTION:" in content, f"Template {tier} missing SECTION markers"

    def test_templates_have_validation_markers(self, templates_dir):
        """Constitution templates should include NEEDS_VALIDATION markers."""
        for tier in CONSTITUTION_TIER_CHOICES:
            template_file = templates_dir / f"constitution-{tier}.md"
            content = template_file.read_text()
            # At least one validation marker should exist
            assert "NEEDS_VALIDATION" in content, (
                f"Template {tier} missing NEEDS_VALIDATION markers"
            )


class TestConstitutionHelpText:
    """Tests for constitution flag in CLI help."""

    def test_init_help_shows_constitution_flag(self):
        """Verify --constitution flag appears in init help."""
        result = runner.invoke(app, ["init", "--help"])
        assert result.exit_code == 0
        # Check for 'constitution' - ANSI codes may split '--' from 'constitution'
        assert "constitution" in result.stdout.lower()

    def test_init_help_shows_tier_options(self):
        """Verify tier options are mentioned in help."""
        result = runner.invoke(app, ["init", "--help"])
        assert result.exit_code == 0
        # Check help mentions the tiers
        assert "light" in result.stdout.lower()
        assert "medium" in result.stdout.lower()
        assert "heavy" in result.stdout.lower()

    def test_init_examples_show_constitution(self):
        """Verify constitution examples are in init help."""
        result = runner.invoke(app, ["init", "--help"])
        assert result.exit_code == 0
        # Check for constitution examples - use lower() to handle ANSI codes
        stdout_lower = result.stdout.lower()
        assert "constitution" in stdout_lower
        # Verify all tier descriptions are present
        assert (
            "light" in stdout_lower
            and "medium" in stdout_lower
            and "heavy" in stdout_lower
        )


class TestConstitutionValidation:
    """Tests for constitution tier validation."""

    def test_invalid_constitution_tier_error(self):
        """Invalid constitution tier should show error."""
        # Need to provide --ai and --ignore-agent-tools for CI environment
        result = runner.invoke(
            app,
            [
                "init",
                "test-project",
                "--ai",
                "claude",
                "--ignore-agent-tools",
                "--constitution",
                "invalid-tier",
            ],
        )
        # Should fail with error about invalid tier
        assert result.exit_code != 0
        assert "invalid" in result.stdout.lower() or "Invalid" in result.stdout
        assert "constitution" in result.stdout.lower()
        # Error message should mention valid choices
        assert any(
            tier in result.stdout.lower() for tier in ["light", "medium", "heavy"]
        )

    def test_valid_constitution_tier_copies_file(self, tmp_path):
        """Test that valid constitution tier copies file to memory/constitution.md."""
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
            input="n\n",  # Answer 'no' to backlog-md install prompt
        )
        assert result.exit_code == 0, (
            f"Expected exit code 0, got {result.exit_code}. Output: {result.stdout}"
        )
        constitution_file = tmp_path / "test-project" / "memory" / "constitution.md"
        assert constitution_file.exists(), "constitution.md should be created"
        # Verify content matches light tier template
        content = constitution_file.read_text()
        assert len(content) > 100, "constitution.md should have substantial content"
