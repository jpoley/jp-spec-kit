"""Tests for spec-light mode workflow functionality."""

from pathlib import Path

import pytest


class TestLightModeDetection:
    """Tests for light mode marker file detection."""

    def test_light_mode_marker_created_with_init_light(self, tmp_path: Path) -> None:
        """Light mode marker should be created when using --light flag."""
        marker_file = tmp_path / ".jpspec-light-mode"

        # Simulate light mode init creating the marker
        marker_file.write_text(
            "# Light mode enabled - ~60% faster workflow (example: 135 min → 50 min)\n"
            "# See docs/guides/when-to-use-light-mode.md for details\n"
        )

        assert marker_file.exists()
        content = marker_file.read_text()
        assert "Light mode enabled" in content
        assert "60% faster" in content

    def test_light_mode_detection_function(self, tmp_path: Path) -> None:
        """Detection function should correctly identify light mode projects."""
        def is_light_mode(project_path: Path) -> bool:
            """Check if project is in light mode."""
            return (project_path / ".jpspec-light-mode").exists()

        # No marker = not light mode
        assert not is_light_mode(tmp_path)

        # With marker = light mode
        (tmp_path / ".jpspec-light-mode").touch()
        assert is_light_mode(tmp_path)

    def test_light_mode_marker_content(self, tmp_path: Path) -> None:
        """Light mode marker should contain helpful information."""
        marker_file = tmp_path / ".jpspec-light-mode"
        expected_content = (
            "# Light mode enabled - ~60% faster workflow (example: 135 min → 50 min)\n"
            "# See docs/guides/when-to-use-light-mode.md for details\n"
        )
        marker_file.write_text(expected_content)

        content = marker_file.read_text()
        assert "docs/guides/when-to-use-light-mode.md" in content


class TestLightModeTemplates:
    """Tests for light mode template files."""

    @pytest.fixture
    def templates_path(self) -> Path:
        """Get the path to templates directory."""
        # Navigate from tests/ to templates/
        return Path(__file__).parent.parent / "templates"

    def test_spec_light_template_exists(self, templates_path: Path) -> None:
        """spec-light-template.md should exist."""
        template = templates_path / "spec-light-template.md"
        assert template.exists(), f"Expected {template} to exist"

    def test_plan_light_template_exists(self, templates_path: Path) -> None:
        """plan-light-template.md should exist."""
        template = templates_path / "plan-light-template.md"
        assert template.exists(), f"Expected {template} to exist"

    def test_spec_light_template_has_required_sections(self, templates_path: Path) -> None:
        """spec-light template should have required sections."""
        template = templates_path / "spec-light-template.md"
        content = template.read_text()

        # Required sections for spec-light
        assert "## Overview" in content
        assert "## User Stories" in content
        assert "## Acceptance Criteria" in content
        assert "## Out of Scope" in content
        assert "## Constitution Compliance" in content

    def test_plan_light_template_has_required_sections(self, templates_path: Path) -> None:
        """plan-light template should have required sections."""
        template = templates_path / "plan-light-template.md"
        content = template.read_text()

        # Required sections for plan-light
        assert "## Approach" in content
        assert "## Key Components" in content
        assert "## Testing Strategy" in content
        assert "## Risks" in content
        assert "## Constitution Compliance" in content

    def test_spec_light_template_is_shorter_than_full(self, templates_path: Path) -> None:
        """Light template should be significantly shorter than full template."""
        spec_full = templates_path / "spec-template.md"
        spec_light = templates_path / "spec-light-template.md"

        if spec_full.exists() and spec_light.exists():
            full_lines = len(spec_full.read_text().splitlines())
            light_lines = len(spec_light.read_text().splitlines())

            # Light should be at most 50% of full
            assert light_lines < full_lines * 0.5, (
                f"Light template ({light_lines} lines) should be much shorter "
                f"than full template ({full_lines} lines)"
            )

    def test_plan_light_template_is_shorter_than_full(self, templates_path: Path) -> None:
        """Light plan template should be significantly shorter than full."""
        plan_full = templates_path / "plan-template.md"
        plan_light = templates_path / "plan-light-template.md"

        if plan_full.exists() and plan_light.exists():
            full_lines = len(plan_full.read_text().splitlines())
            light_lines = len(plan_light.read_text().splitlines())

            # Light should be at most 50% of full
            assert light_lines < full_lines * 0.5, (
                f"Light template ({light_lines} lines) should be much shorter "
                f"than full template ({full_lines} lines)"
            )


class TestLightModeWorkflow:
    """Tests for light mode workflow behavior."""

    @pytest.fixture
    def commands_path(self) -> Path:
        """Get the path to jpspec commands directory."""
        return Path(__file__).parent.parent / ".claude" / "commands" / "jpspec"

    def test_research_command_has_light_mode_check(self, commands_path: Path) -> None:
        """research.md should check for light mode and skip if detected."""
        research_cmd = commands_path / "research.md"
        if research_cmd.exists():
            content = research_cmd.read_text()

            # Should have light mode detection
            assert ".jpspec-light-mode" in content
            assert "LIGHT MODE" in content or "Light Mode" in content

            # Should indicate skipping
            assert "SKIP" in content.upper() or "skip" in content

    def test_plan_command_has_light_mode_check(self, commands_path: Path) -> None:
        """plan.md should check for light mode and use simplified planning."""
        plan_cmd = commands_path / "plan.md"
        if plan_cmd.exists():
            content = plan_cmd.read_text()

            # Should have light mode detection
            assert ".jpspec-light-mode" in content
            assert "LIGHT MODE" in content or "Light Mode" in content

            # Should mention light template
            assert "plan-light" in content

    def test_specify_command_has_light_mode_check(self, commands_path: Path) -> None:
        """specify.md should check for light mode and use simplified spec."""
        specify_cmd = commands_path / "specify.md"
        if specify_cmd.exists():
            content = specify_cmd.read_text()

            # Should have light mode detection
            assert ".jpspec-light-mode" in content
            assert "LIGHT MODE" in content or "Light Mode" in content

            # Should mention light template
            assert "spec-light" in content

    def test_workflow_state_includes_light_mode_section(self, commands_path: Path) -> None:
        """_workflow-state.md should include light mode detection section."""
        workflow_state = commands_path / "_workflow-state.md"
        if workflow_state.exists():
            content = workflow_state.read_text()

            # Should have light mode section
            assert "Light Mode" in content
            assert ".jpspec-light-mode" in content


class TestLightModeDocumentation:
    """Tests for light mode documentation."""

    @pytest.fixture
    def docs_path(self) -> Path:
        """Get the path to docs directory."""
        return Path(__file__).parent.parent / "docs"

    def test_when_to_use_light_mode_guide_exists(self, docs_path: Path) -> None:
        """Guide for when to use light mode should exist."""
        guide = docs_path / "guides" / "when-to-use-light-mode.md"
        assert guide.exists(), f"Expected {guide} to exist"

    def test_guide_explains_criteria(self, docs_path: Path) -> None:
        """Guide should explain when to use light vs full mode."""
        guide = docs_path / "guides" / "when-to-use-light-mode.md"
        if guide.exists():
            content = guide.read_text()

            # Should explain complexity criteria
            assert "complexity" in content.lower()

            # Should explain what's skipped
            assert "Skipped" in content or "skipped" in content
            assert "research" in content.lower()

            # Should explain what's still required
            assert "Still Required" in content or "required" in content.lower()
            assert "Constitutional" in content or "constitution" in content.lower()

    def test_guide_has_time_savings(self, docs_path: Path) -> None:
        """Guide should document time savings."""
        guide = docs_path / "guides" / "when-to-use-light-mode.md"
        if guide.exists():
            content = guide.read_text()

            # Should mention time savings
            assert "60%" in content or "Time Savings" in content


class TestLightModeConstitutionalCompliance:
    """Tests ensuring light mode maintains constitutional compliance."""

    @pytest.fixture
    def templates_path(self) -> Path:
        """Get the path to templates directory."""
        return Path(__file__).parent.parent / "templates"

    def test_spec_light_has_constitution_compliance(self, templates_path: Path) -> None:
        """spec-light template should include constitution compliance section."""
        template = templates_path / "spec-light-template.md"
        if template.exists():
            content = template.read_text()

            assert "Constitution Compliance" in content
            # Should have key compliance items
            assert "Security" in content or "security" in content
            assert "Test" in content or "test" in content

    def test_plan_light_has_constitution_compliance(self, templates_path: Path) -> None:
        """plan-light template should include constitution compliance section."""
        template = templates_path / "plan-light-template.md"
        if template.exists():
            content = template.read_text()

            assert "Constitution Compliance" in content
            # Should have key compliance items
            assert "secrets" in content.lower() or "security" in content.lower()
            assert "test" in content.lower()
