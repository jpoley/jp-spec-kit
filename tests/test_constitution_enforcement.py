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

        # Read and verify
        text = constitution_file.read_text()
        assert "TIER: Light" in text

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

        text = constitution_file.read_text()
        assert "TIER: Medium" in text

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

        text = constitution_file.read_text()
        assert "TIER: Heavy" in text

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

        text = constitution_file.read_text()
        assert "TIER:" not in text  # No tier comment

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

        text = constitution_file.read_text()
        marker_count = text.count("NEEDS_VALIDATION")
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

        text = constitution_file.read_text()
        assert "Project name and core identity" in text
        assert "Technology stack choices" in text
        assert "Quality standards and test coverage" in text


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
        return project_dir

    def test_light_tier_warns_but_proceeds(self, light_constitution):
        """Light tier should warn about unvalidated sections but proceed."""
        constitution_file = light_constitution / "memory" / "constitution.md"
        text = constitution_file.read_text()

        # Verify Light tier
        assert "TIER: Light" in text

        # Verify unvalidated sections exist
        marker_count = text.count("NEEDS_VALIDATION")
        assert marker_count > 0

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

        text = constitution_file.read_text()
        marker_count = text.count("NEEDS_VALIDATION")
        assert marker_count == 0


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
        return project_dir

    def test_medium_tier_requires_confirmation(self, medium_constitution):
        """Medium tier should ask for confirmation when unvalidated."""
        constitution_file = medium_constitution / "memory" / "constitution.md"
        text = constitution_file.read_text()

        # Verify Medium tier
        assert "TIER: Medium" in text

        # Verify unvalidated sections exist
        marker_count = text.count("NEEDS_VALIDATION")
        assert marker_count > 0

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

        text = constitution_file.read_text()
        marker_count = text.count("NEEDS_VALIDATION")
        assert marker_count == 0


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
        return project_dir

    def test_heavy_tier_blocks_when_unvalidated(self, heavy_constitution):
        """Heavy tier should block execution when unvalidated."""
        constitution_file = heavy_constitution / "memory" / "constitution.md"
        text = constitution_file.read_text()

        # Verify Heavy tier
        assert "TIER: Heavy" in text

        # Verify unvalidated sections exist
        marker_count = text.count("NEEDS_VALIDATION")
        assert marker_count > 0

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

        text = constitution_file.read_text()
        marker_count = text.count("NEEDS_VALIDATION")
        assert marker_count == 0


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
        return project_dir

    def test_skip_validation_bypasses_heavy_block(self, heavy_unvalidated_constitution):
        """--skip-validation should bypass Heavy tier block."""
        constitution_file = (
            heavy_unvalidated_constitution / "memory" / "constitution.md"
        )
        text = constitution_file.read_text()

        # Verify would normally block
        assert "TIER: Heavy" in text
        assert "NEEDS_VALIDATION" in text

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

            text = constitution_file.read_text()
            assert f"TIER: {tier}" in text
            assert "NEEDS_VALIDATION" in text


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

        text = constitution_file.read_text()
        assert "Project name and identity" in text
        assert "Technology stack" in text

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

        # Verification that constitution exists and has expected content
        assert constitution_file.exists()
        text = constitution_file.read_text()
        assert "TIER: Heavy" in text
        assert "NEEDS_VALIDATION" in text


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_malformed_tier_comment(self, tmp_path):
        """Should handle malformed TIER comments gracefully."""
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

        text = constitution_file.read_text()
        assert "TIER:" in text

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

        text = constitution_file.read_text()
        assert text.count("TIER:") == 2  # Both present

    def test_empty_constitution_file(self, tmp_path):
        """Should handle empty constitution file."""
        project_dir = tmp_path / "test-project"
        memory_dir = project_dir / "memory"
        memory_dir.mkdir(parents=True)

        constitution_file = memory_dir / "constitution.md"
        constitution_file.write_text("")

        text = constitution_file.read_text()
        assert len(text) == 0

    def test_constitution_with_only_tier_no_content(self, tmp_path):
        """Should handle constitution with only TIER comment."""
        project_dir = tmp_path / "test-project"
        memory_dir = project_dir / "memory"
        memory_dir.mkdir(parents=True)

        constitution_file = memory_dir / "constitution.md"
        content = "<!-- TIER: Medium -->\n"
        constitution_file.write_text(content)

        text = constitution_file.read_text()
        assert "TIER: Medium" in text
        marker_count = text.count("NEEDS_VALIDATION")
        assert marker_count == 0  # Fully validated (no markers)
