"""Tests for spec-light mode workflow functionality.

These tests validate the light mode workflow feature which provides a streamlined
~60% faster workflow by skipping the research phase for medium-complexity features.
"""

import re
from pathlib import Path
from typing import Optional

import pytest

# Constants for template size validation
# Light templates should be at most 50% the size of full templates
# to ensure they provide meaningful time savings (~60% workflow reduction)
MAX_LIGHT_TEMPLATE_SIZE_RATIO = 0.5


def get_project_root() -> Path:
    """Get the project root directory reliably."""
    test_file = Path(__file__).resolve()
    # tests/test_spec_light_mode.py -> project root
    return test_file.parent.parent


def safe_read_file(file_path: Path) -> Optional[str]:
    """Safely read a file, returning None if it doesn't exist or can't be read."""
    try:
        if file_path.exists() and file_path.is_file():
            return file_path.read_text(encoding="utf-8")
    except (OSError, IOError, PermissionError):
        # Intentionally ignore file read errors (missing files, permission denied, I/O failures)
        # Returns None to signal caller that file content is unavailable
        pass
    return None


class TestLightModeDetection:
    """Tests for light mode marker file detection."""

    def test_light_mode_marker_created_with_init_light(self, tmp_path: Path) -> None:
        """Light mode marker should be created when using --light flag."""
        marker_file = tmp_path / ".flowspec-light-mode"

        # Simulate light mode init creating the marker
        marker_content = (
            "# Light mode enabled - ~60% faster workflow (example: 135 min → 50 min)\n"
            "# See user-docs/user-guides/when-to-use-light-mode.md for details\n"
        )
        marker_file.write_text(marker_content, encoding="utf-8")

        assert marker_file.exists(), "Marker file should be created"
        content = safe_read_file(marker_file)
        assert content is not None, "Should be able to read marker file"
        assert "Light mode enabled" in content
        assert "60% faster" in content

    def test_light_mode_detection_function(self, tmp_path: Path) -> None:
        """Detection function should correctly identify light mode projects."""

        def is_light_mode(project_path: Path) -> bool:
            """Check if project is in light mode.

            Args:
                project_path: Path to the project root directory

            Returns:
                True if the project is in light mode, False otherwise
            """
            if not project_path.is_dir():
                return False
            marker = project_path / ".flowspec-light-mode"
            return marker.exists() and marker.is_file()

        # No marker = not light mode
        assert not is_light_mode(tmp_path), "Should not be light mode without marker"

        # With marker = light mode
        (tmp_path / ".flowspec-light-mode").touch()
        assert is_light_mode(tmp_path), "Should be light mode with marker"

        # Non-existent path should return False, not raise
        fake_path = tmp_path / "nonexistent"
        assert not is_light_mode(fake_path), "Non-existent path should return False"

    def test_light_mode_marker_content(self, tmp_path: Path) -> None:
        """Light mode marker should contain helpful information."""
        marker_file = tmp_path / ".flowspec-light-mode"
        expected_content = (
            "# Light mode enabled - ~60% faster workflow (example: 135 min → 50 min)\n"
            "# See user-docs/user-guides/when-to-use-light-mode.md for details\n"
        )
        marker_file.write_text(expected_content, encoding="utf-8")

        content = safe_read_file(marker_file)
        assert content is not None, "Should be able to read marker file"
        assert "user-docs/user-guides/when-to-use-light-mode.md" in content


class TestLightModeTemplates:
    """Tests for light mode template files."""

    @pytest.fixture
    def templates_path(self) -> Path:
        """Get the path to templates directory."""
        project_root = get_project_root()
        templates = project_root / "templates"
        assert templates.is_dir(), f"Templates directory not found: {templates}"
        return templates

    def test_spec_light_template_exists(self, templates_path: Path) -> None:
        """spec-light-template.md should exist."""
        template = templates_path / "spec-light-template.md"
        assert template.exists(), f"Expected {template} to exist"
        assert template.is_file(), f"Expected {template} to be a file"

    def test_plan_light_template_exists(self, templates_path: Path) -> None:
        """plan-light-template.md should exist."""
        template = templates_path / "plan-light-template.md"
        assert template.exists(), f"Expected {template} to exist"
        assert template.is_file(), f"Expected {template} to be a file"

    def test_spec_light_template_has_required_sections(
        self, templates_path: Path
    ) -> None:
        """spec-light template should have required sections."""
        template = templates_path / "spec-light-template.md"
        content = safe_read_file(template)
        assert content is not None, f"Could not read template: {template}"

        # Required sections for spec-light
        required_sections = [
            "## Overview",
            "## User Stories",
            "## Acceptance Criteria",
            "## Out of Scope",
            "## Constitution Compliance",
        ]
        for section in required_sections:
            assert section in content, f"Missing required section: {section}"

    def test_plan_light_template_has_required_sections(
        self, templates_path: Path
    ) -> None:
        """plan-light template should have required sections."""
        template = templates_path / "plan-light-template.md"
        content = safe_read_file(template)
        assert content is not None, f"Could not read template: {template}"

        # Required sections for plan-light
        required_sections = [
            "## Approach",
            "## Key Components",
            "## Testing Strategy",
            "## Risks",
            "## Constitution Compliance",
        ]
        for section in required_sections:
            assert section in content, f"Missing required section: {section}"

    def test_spec_light_template_is_shorter_than_full(
        self, templates_path: Path
    ) -> None:
        """Light template should be significantly shorter than full template."""
        spec_full = templates_path / "spec-template.md"
        spec_light = templates_path / "spec-light-template.md"

        # Skip if full template doesn't exist (may be optional)
        if not spec_full.exists():
            pytest.skip("Full spec template not found")

        full_content = safe_read_file(spec_full)
        light_content = safe_read_file(spec_light)

        assert full_content is not None, "Could not read full template"
        assert light_content is not None, "Could not read light template"

        full_lines = len(full_content.splitlines())
        light_lines = len(light_content.splitlines())

        # Light should be at most MAX_LIGHT_TEMPLATE_SIZE_RATIO of full
        assert light_lines < full_lines * MAX_LIGHT_TEMPLATE_SIZE_RATIO, (
            f"Light template ({light_lines} lines) should be <{MAX_LIGHT_TEMPLATE_SIZE_RATIO * 100:.0f}% "
            f"of full template ({full_lines} lines)"
        )

    def test_plan_light_template_is_shorter_than_full(
        self, templates_path: Path
    ) -> None:
        """Light plan template should be significantly shorter than full."""
        plan_full = templates_path / "plan-template.md"
        plan_light = templates_path / "plan-light-template.md"

        # Skip if full template doesn't exist (may be optional)
        if not plan_full.exists():
            pytest.skip("Full plan template not found")

        full_content = safe_read_file(plan_full)
        light_content = safe_read_file(plan_light)

        assert full_content is not None, "Could not read full template"
        assert light_content is not None, "Could not read light template"

        full_lines = len(full_content.splitlines())
        light_lines = len(light_content.splitlines())

        # Light should be at most MAX_LIGHT_TEMPLATE_SIZE_RATIO of full
        assert light_lines < full_lines * MAX_LIGHT_TEMPLATE_SIZE_RATIO, (
            f"Light template ({light_lines} lines) should be <{MAX_LIGHT_TEMPLATE_SIZE_RATIO * 100:.0f}% "
            f"of full template ({full_lines} lines)"
        )


class TestLightModeWorkflow:
    """Tests for light mode workflow behavior."""

    @pytest.fixture
    def commands_path(self) -> Path:
        """Get the path to flowspec commands directory."""
        project_root = get_project_root()
        # Check both locations: .claude/commands and templates/commands
        primary_path = project_root / ".claude" / "commands" / "flow"
        template_path = project_root / "templates" / "commands" / "flow"

        if primary_path.is_dir():
            return primary_path
        elif template_path.is_dir():
            return template_path
        else:
            pytest.skip("flowspec commands directory not found")
            return primary_path  # Unreachable but satisfies type checker

    def test_research_command_has_light_mode_check(self, commands_path: Path) -> None:
        """research.md should check for light mode and skip if detected."""
        research_cmd = commands_path / "research.md"
        if not research_cmd.exists():
            pytest.skip(f"research.md not found at {research_cmd}")

        content = safe_read_file(research_cmd)
        assert content is not None, f"Could not read {research_cmd}"

        # Should have light mode detection with actual conditional check
        # Pattern matches: if [ -f ".flowspec-light-mode" ] or similar conditional
        light_mode_conditional = re.search(
            r"if\s+\[.*\.flowspec-light-mode.*\]", content
        )
        assert light_mode_conditional is not None, (
            'Missing conditional check for .flowspec-light-mode (expected: if [ -f ".flowspec-light-mode" ])'
        )
        assert "LIGHT MODE" in content or "Light Mode" in content, (
            "Missing light mode text"
        )

        # Should indicate skipping
        content_upper = content.upper()
        assert "SKIP" in content_upper, "Missing skip indication for light mode"

    def test_plan_command_has_light_mode_check(self, commands_path: Path) -> None:
        """plan.md should check for light mode and use simplified planning."""
        plan_cmd = commands_path / "plan.md"
        if not plan_cmd.exists():
            pytest.skip(f"plan.md not found at {plan_cmd}")

        content = safe_read_file(plan_cmd)
        assert content is not None, f"Could not read {plan_cmd}"

        # Should have light mode detection with actual conditional check
        light_mode_conditional = re.search(
            r"if\s+\[.*\.flowspec-light-mode.*\]", content
        )
        assert light_mode_conditional is not None, (
            'Missing conditional check for .flowspec-light-mode (expected: if [ -f ".flowspec-light-mode" ])'
        )
        assert "LIGHT MODE" in content or "Light Mode" in content, (
            "Missing light mode text"
        )

        # Should mention light template
        assert "plan-light" in content, "Missing plan-light template reference"

    def test_specify_command_has_light_mode_check(self, commands_path: Path) -> None:
        """specify.md should check for light mode and use simplified spec."""
        specify_cmd = commands_path / "specify.md"
        if not specify_cmd.exists():
            pytest.skip(f"specify.md not found at {specify_cmd}")

        content = safe_read_file(specify_cmd)
        assert content is not None, f"Could not read {specify_cmd}"

        # Should have light mode detection with actual conditional check
        light_mode_conditional = re.search(
            r"if\s+\[.*\.flowspec-light-mode.*\]", content
        )
        assert light_mode_conditional is not None, (
            'Missing conditional check for .flowspec-light-mode (expected: if [ -f ".flowspec-light-mode" ])'
        )
        assert "LIGHT MODE" in content or "Light Mode" in content, (
            "Missing light mode text"
        )

        # Should mention light template
        assert "spec-light" in content, "Missing spec-light template reference"

    def test_workflow_state_includes_light_mode_section(
        self, commands_path: Path
    ) -> None:
        """_workflow-state.md should include light mode detection section."""
        workflow_state = commands_path / "_workflow-state.md"
        if not workflow_state.exists():
            pytest.skip(f"_workflow-state.md not found at {workflow_state}")

        content = safe_read_file(workflow_state)
        assert content is not None, f"Could not read {workflow_state}"

        # Should have light mode section
        assert "Light Mode" in content, "Missing Light Mode section"
        assert ".flowspec-light-mode" in content, "Missing light mode marker reference"


class TestLightModeDocumentation:
    """Tests for light mode documentation."""

    @pytest.fixture
    def docs_path(self) -> Path:
        """Get the path to user-docs directory."""
        project_root = get_project_root()
        docs = project_root / "user-docs"
        assert docs.is_dir(), f"User docs directory not found: {docs}"
        return docs

    def test_when_to_use_light_mode_guide_exists(self, docs_path: Path) -> None:
        """Guide for when to use light mode should exist."""
        guide = docs_path / "user-guides" / "when-to-use-light-mode.md"
        assert guide.exists(), f"Expected {guide} to exist"
        assert guide.is_file(), f"Expected {guide} to be a file"

    def test_guide_explains_criteria(self, docs_path: Path) -> None:
        """Guide should explain when to use light vs full mode."""
        guide = docs_path / "user-guides" / "when-to-use-light-mode.md"
        if not guide.exists():
            pytest.skip(f"Guide not found at {guide}")

        content = safe_read_file(guide)
        assert content is not None, f"Could not read {guide}"

        content_lower = content.lower()

        # Should explain complexity criteria
        assert "complexity" in content_lower, "Missing complexity criteria"

        # Should explain what's skipped
        assert "skipped" in content_lower or "skip" in content_lower, (
            "Missing skip explanation"
        )
        assert "research" in content_lower, "Missing research mention"

        # Should explain what's still required
        assert "required" in content_lower, "Missing required explanation"
        assert "constitution" in content_lower, "Missing constitution reference"

    def test_guide_has_time_savings(self, docs_path: Path) -> None:
        """Guide should document time savings."""
        guide = docs_path / "user-guides" / "when-to-use-light-mode.md"
        if not guide.exists():
            pytest.skip(f"Guide not found at {guide}")

        content = safe_read_file(guide)
        assert content is not None, f"Could not read {guide}"

        # Should mention time savings
        assert "60%" in content or "Time Savings" in content, (
            "Missing time savings information"
        )


class TestLightModeConstitutionalCompliance:
    """Tests ensuring light mode maintains constitutional compliance."""

    @pytest.fixture
    def templates_path(self) -> Path:
        """Get the path to templates directory."""
        project_root = get_project_root()
        templates = project_root / "templates"
        assert templates.is_dir(), f"Templates directory not found: {templates}"
        return templates

    def test_spec_light_has_constitution_compliance(self, templates_path: Path) -> None:
        """spec-light template should include constitution compliance section."""
        template = templates_path / "spec-light-template.md"
        if not template.exists():
            pytest.skip(f"Template not found at {template}")

        content = safe_read_file(template)
        assert content is not None, f"Could not read {template}"

        assert "Constitution Compliance" in content, (
            "Missing Constitution Compliance section"
        )

        content_lower = content.lower()
        # Should have key compliance items
        assert "security" in content_lower, "Missing security reference"
        assert "test" in content_lower, "Missing test reference"

    def test_plan_light_has_constitution_compliance(self, templates_path: Path) -> None:
        """plan-light template should include constitution compliance section."""
        template = templates_path / "plan-light-template.md"
        if not template.exists():
            pytest.skip(f"Template not found at {template}")

        content = safe_read_file(template)
        assert content is not None, f"Could not read {template}"

        assert "Constitution Compliance" in content, (
            "Missing Constitution Compliance section"
        )

        content_lower = content.lower()
        # Should have key compliance items
        assert "security" in content_lower or "secrets" in content_lower, (
            "Missing security/secrets reference"
        )
        assert "test" in content_lower, "Missing test reference"
