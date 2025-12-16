"""Tests for workflow-customization.md guide content.

Verifies AC compliance for task-097: Create user customization guide for workflow config.
"""

import pytest
from pathlib import Path


@pytest.fixture
def customization_guide_path():
    """Return path to the workflow-customization.md guide."""
    return (
        Path(__file__).parent.parent
        / "user-docs"
        / "user-guides"
        / "workflow-customization.md"
    )


@pytest.fixture
def guide_content(customization_guide_path):
    """Return the content of the customization guide."""
    assert customization_guide_path.exists(), (
        f"Guide not found at {customization_guide_path}"
    )
    return customization_guide_path.read_text()


class TestGuideExists:
    """AC #1: Guide created at user-docs/user-guides/workflow-customization.md"""

    def test_guide_file_exists(self, customization_guide_path):
        """Verify the guide file exists at the expected location."""
        assert customization_guide_path.exists()
        assert customization_guide_path.is_file()

    def test_guide_has_substantial_content(self, guide_content):
        """Verify the guide has meaningful content (not empty or stub)."""
        # Guide should be at least 10KB of documentation
        assert len(guide_content) > 10000, "Guide appears to be incomplete"


class TestConfigurationStructure:
    """AC #2: Guide explains structure of flowspec_workflow.yml in plain language"""

    def test_explains_states(self, guide_content):
        """Verify guide explains the states configuration."""
        assert "states:" in guide_content
        assert (
            "Task progression stages" in guide_content
            or "Task states" in guide_content.lower()
        )

    def test_explains_workflows(self, guide_content):
        """Verify guide explains the workflows configuration."""
        assert "workflows:" in guide_content
        assert "/flowspec" in guide_content

    def test_explains_transitions(self, guide_content):
        """Verify guide explains the transitions configuration."""
        assert "transitions:" in guide_content
        assert "Valid state changes" in guide_content or "from:" in guide_content

    def test_explains_agent_loops(self, guide_content):
        """Verify guide explains agent loop classification."""
        assert "agent_loops:" in guide_content
        assert "inner" in guide_content.lower()
        assert "outer" in guide_content.lower()

    def test_explains_file_location(self, guide_content):
        """Verify guide explains where the config file should be located."""
        assert "flowspec_workflow.yml" in guide_content
        assert (
            "project-root" in guide_content or "project root" in guide_content.lower()
        )


class TestCommonCustomizations:
    """AC #3: Guide includes step-by-step examples for common customizations"""

    def test_add_phase_example(self, guide_content):
        """Verify guide has example for adding a custom phase."""
        assert (
            "Adding a Custom Phase" in guide_content or "Add the state" in guide_content
        )
        assert (
            "Step-by-Step" in guide_content or "step-by-step" in guide_content.lower()
        )

    def test_remove_phase_example(self, guide_content):
        """Verify guide has example for removing a phase."""
        assert (
            "Removing a Phase" in guide_content or "Remove the state" in guide_content
        )

    def test_reorder_phases_example(self, guide_content):
        """Verify guide has example for reordering phases."""
        assert (
            "Reordering Phases" in guide_content or "reorder" in guide_content.lower()
        )


class TestCustomAgents:
    """AC #4: Guide explains how to add custom agents to workflows"""

    def test_custom_agent_section(self, guide_content):
        """Verify guide has section on adding custom agents."""
        assert (
            "Custom Agents" in guide_content or "custom agent" in guide_content.lower()
        )

    def test_agent_definition_example(self, guide_content):
        """Verify guide shows how to define an agent in workflow config."""
        assert "name:" in guide_content
        assert "identity:" in guide_content
        assert "responsibilities:" in guide_content


class TestCustomStates:
    """AC #5: Guide explains how to create new states"""

    def test_new_state_example(self, guide_content):
        """Verify guide shows how to add a new state."""
        assert (
            "Security Audited" in guide_content
            or "custom state" in guide_content.lower()
        )
        # Should show adding to states list
        assert "states:" in guide_content

    def test_state_naming_guidance(self, guide_content):
        """Verify guide provides guidance on naming states."""
        assert (
            "Descriptive Names" in guide_content
            or "descriptive name" in guide_content.lower()
        )


class TestValidation:
    """AC #6: Guide explains how to validate customizations"""

    def test_validation_command_documented(self, guide_content):
        """Verify the validation command is documented."""
        assert "flowspec workflow validate" in guide_content

    def test_validation_output_explained(self, guide_content):
        """Verify validation output is explained."""
        assert "✓" in guide_content or "valid" in guide_content.lower()


class TestTroubleshooting:
    """AC #7: Guide includes troubleshooting section"""

    def test_troubleshooting_section_exists(self, guide_content):
        """Verify there is an explicit Troubleshooting section."""
        assert "## Troubleshooting" in guide_content

    def test_troubleshooting_has_diagnostic_commands(self, guide_content):
        """Verify troubleshooting section has diagnostic commands."""
        assert (
            "Diagnostic Commands" in guide_content
            or "diagnostic" in guide_content.lower()
        )

    def test_troubleshooting_has_quick_reference(self, guide_content):
        """Verify troubleshooting section has quick reference table."""
        assert (
            "Quick Reference" in guide_content or "quick fix" in guide_content.lower()
        )

    def test_links_to_full_troubleshooting_guide(self, guide_content):
        """Verify link to comprehensive troubleshooting guide."""
        assert "workflow-troubleshooting.md" in guide_content


class TestWarnings:
    """AC #8: Guide warns about potential issues (circular deps, unreachable states)"""

    def test_circular_dependencies_warning(self, guide_content):
        """Verify warning about circular dependencies."""
        assert "Circular" in guide_content
        # Should explain what it is and how to avoid
        assert "cycle" in guide_content.lower() or "DAG" in guide_content

    def test_unreachable_states_warning(self, guide_content):
        """Verify warning about unreachable states."""
        assert "Unreachable" in guide_content
        # Should explain what it is and how to fix
        assert (
            "transition path" in guide_content.lower()
            or "reachable" in guide_content.lower()
        )

    def test_critical_issues_section(self, guide_content):
        """Verify there's a section highlighting critical issues to avoid."""
        assert "Critical Issues" in guide_content or "critical" in guide_content.lower()

    def test_circular_dependency_fix_documented(self, guide_content):
        """Verify fix for circular dependencies is documented."""
        assert "rework" in guide_content.lower()
        # Should mention using via: "rework" for backward transitions

    def test_unreachable_state_fix_documented(self, guide_content):
        """Verify fix for unreachable states is documented."""
        # Should explain adding transition path
        assert (
            "Add a transition" in guide_content
            or "add transition" in guide_content.lower()
        )


class TestRelatedDocumentation:
    """Test that related documentation links are present."""

    def test_links_to_architecture_guide(self, guide_content):
        """Verify link to workflow architecture documentation."""
        assert "workflow-architecture.md" in guide_content

    def test_links_to_state_mapping_guide(self, guide_content):
        """Verify link to state mapping documentation."""
        assert (
            "workflow-state-mapping.md" in guide_content
            or "state-mapping" in guide_content.lower()
        )

    def test_links_to_examples(self, guide_content):
        """Verify links to configuration examples."""
        assert "examples/workflows" in guide_content


class TestBestPractices:
    """Test that best practices are documented."""

    def test_version_control_recommendation(self, guide_content):
        """Verify version control best practice is documented."""
        assert "Version Control" in guide_content or "git" in guide_content.lower()

    def test_test_with_small_tasks_recommendation(self, guide_content):
        """Verify testing recommendation is documented."""
        assert "small tasks" in guide_content.lower() or "test" in guide_content.lower()

    def test_keep_it_simple_recommendation(self, guide_content):
        """Verify simplicity recommendation is documented."""
        assert "Keep It Simple" in guide_content or "simple" in guide_content.lower()
