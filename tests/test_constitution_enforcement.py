"""Tests for constitution enforcement in /flowspec commands.

Tests cover:
- Constitution existence detection
- Tier detection from TIER comment
- NEEDS_VALIDATION marker counting
- Tier-based enforcement (Light, Medium, Heavy)
- --skip-validation flag handling
- Section name extraction
"""

from textwrap import dedent

import pytest
from flowspec_cli import (
    check_constitution_tier,
    count_validation_markers,
    detect_constitution_tier,
    extract_validation_sections,
)


class TestConstitutionDetection:
    """Tests for detecting constitution file and parsing metadata."""

    @pytest.fixture
    def tmp_project(self, tmp_path):
        """Create temporary project directory with memory/ folder."""
        project_dir = tmp_path / "test-project"
        memory_dir = project_dir / "memory"
        memory_dir.mkdir(parents=True)
        return project_dir

    def test_detect_missing_constitution(self, tmp_project):
        """Should detect when constitution.md is missing."""
        constitution_file = tmp_project / "memory" / "constitution.md"
        assert not constitution_file.exists()

    def test_detect_existing_constitution(self, tmp_project):
        """Should detect when constitution.md exists."""
        constitution_file = tmp_project / "memory" / "constitution.md"
        constitution_file.write_text("# Test Constitution\n")
        assert constitution_file.exists()

    def test_detect_light_tier(self, tmp_project):
        """Should detect Light tier from TIER comment."""
        constitution_file = tmp_project / "memory" / "constitution.md"
        content = dedent(
            """
            <!-- TIER: Light -->
            # Test Constitution
            """
        )
        constitution_file.write_text(content)

        # Use helper function to detect tier
        tier = detect_constitution_tier(constitution_file)
        assert tier == "Light"

    def test_detect_medium_tier(self, tmp_project):
        """Should detect Medium tier from TIER comment."""
        constitution_file = tmp_project / "memory" / "constitution.md"
        content = dedent(
            """
            <!-- TIER: Medium -->
            # Test Constitution
            """
        )
        constitution_file.write_text(content)

        tier = detect_constitution_tier(constitution_file)
        assert tier == "Medium"

    def test_detect_heavy_tier(self, tmp_project):
        """Should detect Heavy tier from TIER comment."""
        constitution_file = tmp_project / "memory" / "constitution.md"
        content = dedent(
            """
            <!-- TIER: Heavy -->
            # Test Constitution
            """
        )
        constitution_file.write_text(content)

        tier = detect_constitution_tier(constitution_file)
        assert tier == "Heavy"

    def test_default_to_medium_when_no_tier(self, tmp_project):
        """Should default to Medium tier when TIER comment is missing."""
        constitution_file = tmp_project / "memory" / "constitution.md"
        content = dedent(
            """
            # Test Constitution
            No TIER comment here
            """
        )
        constitution_file.write_text(content)

        tier = detect_constitution_tier(constitution_file)
        assert tier == "Medium"

    def test_count_validation_markers(self, tmp_project):
        """Should count NEEDS_VALIDATION markers correctly."""
        constitution_file = tmp_project / "memory" / "constitution.md"
        content = dedent(
            """
            <!-- TIER: Light -->
            # Test Constitution

            ## Section 1
            <!-- NEEDS_VALIDATION: Project name -->

            ## Section 2
            <!-- NEEDS_VALIDATION: Technology stack -->

            ## Section 3
            <!-- NEEDS_VALIDATION: Quality standards -->
            """
        )
        constitution_file.write_text(content)

        marker_count = count_validation_markers(constitution_file)
        assert marker_count == 3

    def test_extract_section_names(self, tmp_project):
        """Should extract section names from NEEDS_VALIDATION markers."""
        constitution_file = tmp_project / "memory" / "constitution.md"
        content = dedent(
            """
            <!-- TIER: Light -->
            # Test Constitution

            <!-- NEEDS_VALIDATION: Project name and core identity -->
            <!-- NEEDS_VALIDATION: Technology stack choices -->
            <!-- NEEDS_VALIDATION: Quality standards and test coverage -->
            """
        )
        constitution_file.write_text(content)

        sections = extract_validation_sections(constitution_file)
        assert len(sections) == 3
        assert "Project name and core identity" in sections
        assert "Technology stack choices" in sections
        assert "Quality standards and test coverage" in sections


class TestLightTierEnforcement:
    """Tests for Light tier enforcement (warn only, proceed)."""

    @pytest.fixture
    def light_constitution(self, tmp_path):
        """Create Light tier constitution with unvalidated sections."""
        project_dir = tmp_path / "test-project"
        memory_dir = project_dir / "memory"
        memory_dir.mkdir(parents=True)

        constitution_file = memory_dir / "constitution.md"
        content = dedent(
            """
            <!-- TIER: Light -->
            # Test Constitution

            <!-- NEEDS_VALIDATION: Project name -->
            <!-- NEEDS_VALIDATION: Technology stack -->
            """
        )
        constitution_file.write_text(content)
        return constitution_file

    def test_light_tier_warns_but_proceeds(self, light_constitution):
        """Light tier should warn about unvalidated sections but proceed."""
        result = check_constitution_tier(light_constitution)

        assert result.tier == "Light"
        assert result.marker_count == 2
        assert result.can_proceed is True
        assert result.requires_confirmation is False
        assert result.warning is not None
        assert "Project name" in result.warning
        assert "Technology stack" in result.warning

    def test_light_tier_fully_validated_proceeds(self, tmp_path):
        """Light tier with no unvalidated sections should proceed silently."""
        project_dir = tmp_path / "test-project"
        memory_dir = project_dir / "memory"
        memory_dir.mkdir(parents=True)

        constitution_file = memory_dir / "constitution.md"
        content = dedent(
            """
            <!-- TIER: Light -->
            # Test Constitution

            Fully validated, no markers.
            """
        )
        constitution_file.write_text(content)

        result = check_constitution_tier(constitution_file)

        assert result.tier == "Light"
        assert result.marker_count == 0
        assert result.can_proceed is True
        assert result.warning is None


class TestMediumTierEnforcement:
    """Tests for Medium tier enforcement (warn and ask confirmation)."""

    @pytest.fixture
    def medium_constitution(self, tmp_path):
        """Create Medium tier constitution with unvalidated sections."""
        project_dir = tmp_path / "test-project"
        memory_dir = project_dir / "memory"
        memory_dir.mkdir(parents=True)

        constitution_file = memory_dir / "constitution.md"
        content = dedent(
            """
            <!-- TIER: Medium -->
            # Test Constitution

            <!-- NEEDS_VALIDATION: Quality standards -->
            <!-- NEEDS_VALIDATION: Security requirements -->
            """
        )
        constitution_file.write_text(content)
        return constitution_file

    def test_medium_tier_requires_confirmation(self, medium_constitution):
        """Medium tier should ask for confirmation when unvalidated."""
        result = check_constitution_tier(medium_constitution)

        assert result.tier == "Medium"
        assert result.marker_count == 2
        assert result.can_proceed is False
        assert result.requires_confirmation is True
        assert result.warning is not None
        assert "Quality standards" in result.warning
        assert "Security requirements" in result.warning

    def test_medium_tier_fully_validated_proceeds(self, tmp_path):
        """Medium tier with no unvalidated sections should proceed."""
        project_dir = tmp_path / "test-project"
        memory_dir = project_dir / "memory"
        memory_dir.mkdir(parents=True)

        constitution_file = memory_dir / "constitution.md"
        content = dedent(
            """
            <!-- TIER: Medium -->
            # Test Constitution

            Fully validated.
            """
        )
        constitution_file.write_text(content)

        result = check_constitution_tier(constitution_file)

        assert result.tier == "Medium"
        assert result.marker_count == 0
        assert result.can_proceed is True
        assert result.requires_confirmation is False
        assert result.warning is None


class TestHeavyTierEnforcement:
    """Tests for Heavy tier enforcement (block until validated)."""

    @pytest.fixture
    def heavy_constitution(self, tmp_path):
        """Create Heavy tier constitution with unvalidated sections."""
        project_dir = tmp_path / "test-project"
        memory_dir = project_dir / "memory"
        memory_dir.mkdir(parents=True)

        constitution_file = memory_dir / "constitution.md"
        content = dedent(
            """
            <!-- TIER: Heavy -->
            # Test Constitution

            <!-- NEEDS_VALIDATION: Project name and core identity -->
            <!-- NEEDS_VALIDATION: Technology stack choices -->
            <!-- NEEDS_VALIDATION: Quality standards and test coverage -->
            <!-- NEEDS_VALIDATION: Security requirements and compliance -->
            <!-- NEEDS_VALIDATION: Deployment and CI/CD requirements -->
            """
        )
        constitution_file.write_text(content)
        return constitution_file

    def test_heavy_tier_blocks_when_unvalidated(self, heavy_constitution):
        """Heavy tier should block execution when unvalidated."""
        result = check_constitution_tier(heavy_constitution)

        assert result.tier == "Heavy"
        assert result.marker_count == 5
        assert result.can_proceed is False
        assert result.requires_confirmation is False
        assert result.blocking_reason is not None
        assert "Project name and core identity" in result.blocking_reason
        assert "/spec:constitution" in result.blocking_reason

    def test_heavy_tier_fully_validated_proceeds(self, tmp_path):
        """Heavy tier with no unvalidated sections should proceed."""
        project_dir = tmp_path / "test-project"
        memory_dir = project_dir / "memory"
        memory_dir.mkdir(parents=True)

        constitution_file = memory_dir / "constitution.md"
        content = dedent(
            """
            <!-- TIER: Heavy -->
            # Test Constitution

            Fully validated, production-ready.
            """
        )
        constitution_file.write_text(content)

        result = check_constitution_tier(constitution_file)

        assert result.tier == "Heavy"
        assert result.marker_count == 0
        assert result.can_proceed is True
        assert result.blocking_reason is None


class TestSkipValidationFlag:
    """Tests for --skip-validation flag handling."""

    @pytest.fixture
    def heavy_unvalidated_constitution(self, tmp_path):
        """Create Heavy tier constitution that would normally block."""
        project_dir = tmp_path / "test-project"
        memory_dir = project_dir / "memory"
        memory_dir.mkdir(parents=True)

        constitution_file = memory_dir / "constitution.md"
        content = dedent(
            """
            <!-- TIER: Heavy -->
            # Test Constitution

            <!-- NEEDS_VALIDATION: Everything needs validation -->
            """
        )
        constitution_file.write_text(content)
        return constitution_file

    def test_skip_validation_bypasses_heavy_block(self, heavy_unvalidated_constitution):
        """--skip-validation should bypass Heavy tier block."""
        result = check_constitution_tier(
            heavy_unvalidated_constitution, skip_validation=True
        )

        assert result.can_proceed is True
        assert result.warning is not None
        assert "skip" in result.warning.lower()

    def test_skip_validation_works_with_all_tiers(self, tmp_path):
        """--skip-validation should work with any tier."""
        for tier in ["Light", "Medium", "Heavy"]:
            project_dir = tmp_path / f"test-{tier.lower()}"
            memory_dir = project_dir / "memory"
            memory_dir.mkdir(parents=True)

            constitution_file = memory_dir / "constitution.md"
            content = dedent(
                f"""
                <!-- TIER: {tier} -->
                # Test Constitution

                <!-- NEEDS_VALIDATION: Unvalidated section -->
                """
            )
            constitution_file.write_text(content)

            result = check_constitution_tier(constitution_file, skip_validation=True)

            assert result.can_proceed is True
            assert result.warning is not None


class TestEnforcementMessages:
    """Tests for enforcement message content and clarity."""

    def test_warning_message_includes_section_names(self, tmp_path):
        """Warning messages should list unvalidated section names."""
        project_dir = tmp_path / "test-project"
        memory_dir = project_dir / "memory"
        memory_dir.mkdir(parents=True)

        constitution_file = memory_dir / "constitution.md"
        content = dedent(
            """
            <!-- TIER: Light -->
            # Test Constitution

            <!-- NEEDS_VALIDATION: Project name and identity -->
            <!-- NEEDS_VALIDATION: Technology stack -->
            """
        )
        constitution_file.write_text(content)

        result = check_constitution_tier(constitution_file)

        assert "Project name and identity" in result.warning
        assert "Technology stack" in result.warning

    def test_heavy_block_message_includes_resolution_steps(self, tmp_path):
        """Heavy tier block message should include clear resolution steps."""
        project_dir = tmp_path / "test-project"
        memory_dir = project_dir / "memory"
        memory_dir.mkdir(parents=True)

        constitution_file = memory_dir / "constitution.md"
        content = dedent(
            """
            <!-- TIER: Heavy -->
            # Test Constitution

            <!-- NEEDS_VALIDATION: Everything -->
            """
        )
        constitution_file.write_text(content)

        result = check_constitution_tier(constitution_file)

        assert result.blocking_reason is not None
        assert "/spec:constitution" in result.blocking_reason
        assert "flowspec constitution validate" in result.blocking_reason
        assert "--skip-validation" in result.blocking_reason


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_malformed_tier_comment(self, tmp_path):
        """Should handle malformed TIER comments gracefully (default to Medium)."""
        project_dir = tmp_path / "test-project"
        memory_dir = project_dir / "memory"
        memory_dir.mkdir(parents=True)

        constitution_file = memory_dir / "constitution.md"
        content = dedent(
            """
            <!-- TIER: InvalidTier -->
            # Test Constitution
            """
        )
        constitution_file.write_text(content)

        tier = detect_constitution_tier(constitution_file)
        assert tier == "Medium"

    def test_multiple_tier_comments(self, tmp_path):
        """Should handle multiple TIER comments (use first one)."""
        project_dir = tmp_path / "test-project"
        memory_dir = project_dir / "memory"
        memory_dir.mkdir(parents=True)

        constitution_file = memory_dir / "constitution.md"
        content = dedent(
            """
            <!-- TIER: Light -->
            # Test Constitution

            <!-- TIER: Heavy -->  <!-- This should be ignored -->
            """
        )
        constitution_file.write_text(content)

        tier = detect_constitution_tier(constitution_file)
        assert tier == "Light"

    def test_empty_constitution_file(self, tmp_path):
        """Should handle empty constitution file."""
        project_dir = tmp_path / "test-project"
        memory_dir = project_dir / "memory"
        memory_dir.mkdir(parents=True)

        constitution_file = memory_dir / "constitution.md"
        constitution_file.write_text("")

        tier = detect_constitution_tier(constitution_file)
        assert tier == "Medium"  # Default

        marker_count = count_validation_markers(constitution_file)
        assert marker_count == 0

    def test_constitution_with_only_tier_no_content(self, tmp_path):
        """Should handle constitution with only TIER comment."""
        project_dir = tmp_path / "test-project"
        memory_dir = project_dir / "memory"
        memory_dir.mkdir(parents=True)

        constitution_file = memory_dir / "constitution.md"
        content = "<!-- TIER: Medium -->\n"
        constitution_file.write_text(content)

        result = check_constitution_tier(constitution_file)

        assert result.tier == "Medium"
        assert result.marker_count == 0
        assert result.can_proceed is True

    def test_missing_constitution_returns_warning(self, tmp_path):
        """Missing constitution should return warning but allow proceed."""
        nonexistent_file = tmp_path / "nonexistent" / "constitution.md"

        result = check_constitution_tier(nonexistent_file)

        assert result.tier == "Unknown"
        assert result.can_proceed is True
        assert result.warning is not None
        assert "not found" in result.warning.lower()
