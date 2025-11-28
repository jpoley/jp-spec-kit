"""Integration tests for /jpspec:validate command with backlog.md CLI.

This test module verifies that the validate command correctly integrates with
backlog.md task management for QA, Security, Tech Writer, and Release Manager agents.
"""

import pytest
import subprocess
from pathlib import Path
from textwrap import dedent
from unittest.mock import patch, MagicMock
import json


@pytest.fixture
def validate_md_path():
    """Get path to validate.md command file."""
    return Path(__file__).parent.parent / ".claude" / "commands" / "jpspec" / "validate.md"


@pytest.fixture
def backlog_instructions_path():
    """Get path to _backlog-instructions.md file."""
    return Path(__file__).parent.parent / ".claude" / "commands" / "jpspec" / "_backlog-instructions.md"


class TestValidateCommandStructure:
    """Test validate.md command structure and backlog integration."""

    def test_validate_md_exists(self, validate_md_path):
        """Verify validate.md command file exists."""
        assert validate_md_path.exists(), "validate.md command file must exist"

    def test_validate_includes_task_discovery(self, validate_md_path):
        """Verify validate.md includes backlog task discovery section."""
        content = validate_md_path.read_text()

        # Check for task discovery section
        assert "## Backlog Task Discovery" in content
        assert 'backlog task list -s "In Progress" --plain' in content
        assert 'backlog task list -s "Done" --plain' in content
        assert "backlog task <id> --plain" in content

    def test_validate_includes_backlog_instructions_marker(self, validate_md_path):
        """Verify validate.md includes {{BACKLOG_INSTRUCTIONS}} markers in agent contexts."""
        content = validate_md_path.read_text()

        # Should have at least 4 occurrences (one per agent: QA, Security, Tech Writer, Release Manager)
        marker_count = content.count("{{BACKLOG_INSTRUCTIONS}}")
        assert marker_count >= 4, f"Expected at least 4 {{{{BACKLOG_INSTRUCTIONS}}}} markers, found {marker_count}"

    def test_validate_has_all_four_agent_contexts(self, validate_md_path):
        """Verify validate.md has all four agent contexts."""
        content = validate_md_path.read_text()

        # Check for all four agent contexts
        assert "# AGENT CONTEXT: Quality Guardian" in content
        assert "# AGENT CONTEXT: Secure-by-Design Engineer" in content
        assert "# AGENT CONTEXT: Senior Technical Writer" in content
        assert "# AGENT CONTEXT: Senior Release Manager" in content


class TestQualityGuardianBacklogIntegration:
    """Test Quality Guardian agent backlog integration."""

    def test_qa_has_backlog_instructions_marker(self, validate_md_path):
        """Verify QA agent context includes backlog instructions marker."""
        content = validate_md_path.read_text()

        # Extract QA section
        qa_start = content.find("# AGENT CONTEXT: Quality Guardian")
        qa_end = content.find("# AGENT CONTEXT: Secure-by-Design Engineer")
        qa_section = content[qa_start:qa_end]

        assert "{{BACKLOG_INSTRUCTIONS}}" in qa_section

    def test_qa_has_ac_validation_requirements(self, validate_md_path):
        """Verify QA agent has acceptance criteria validation requirements."""
        content = validate_md_path.read_text()

        # Extract QA section
        qa_start = content.find("# AGENT CONTEXT: Quality Guardian")
        qa_end = content.find("# AGENT CONTEXT: Secure-by-Design Engineer")
        qa_section = content[qa_start:qa_end]

        # Check for AC validation requirements
        assert "Verify all backlog task acceptance criteria are met" in qa_section
        assert "Cross-reference test results with AC requirements" in qa_section
        assert "Mark ACs complete via backlog CLI" in qa_section

    def test_qa_has_backlog_context_section(self, validate_md_path):
        """Verify QA agent has Backlog Context section."""
        content = validate_md_path.read_text()

        qa_start = content.find("# AGENT CONTEXT: Quality Guardian")
        qa_end = content.find("# AGENT CONTEXT: Secure-by-Design Engineer")
        qa_section = content[qa_start:qa_end]

        assert "Backlog Context:" in qa_section


class TestSecurityEngineerBacklogIntegration:
    """Test Security Engineer agent backlog integration."""

    def test_security_has_backlog_instructions_marker(self, validate_md_path):
        """Verify Security Engineer context includes backlog instructions marker."""
        content = validate_md_path.read_text()

        # Extract Security section
        sec_start = content.find("# AGENT CONTEXT: Secure-by-Design Engineer")
        sec_end = content.find("# AGENT CONTEXT: Senior Technical Writer")
        sec_section = content[sec_start:sec_end]

        assert "{{BACKLOG_INSTRUCTIONS}}" in sec_section

    def test_security_has_ac_validation_requirements(self, validate_md_path):
        """Verify Security Engineer has security AC validation requirements."""
        content = validate_md_path.read_text()

        # Extract Security section
        sec_start = content.find("# AGENT CONTEXT: Secure-by-Design Engineer")
        sec_end = content.find("# AGENT CONTEXT: Senior Technical Writer")
        sec_section = content[sec_start:sec_end]

        # Check for security AC validation
        assert "Validate security-related acceptance criteria" in sec_section
        assert "Mark security ACs complete via backlog CLI" in sec_section

    def test_security_has_backlog_context_section(self, validate_md_path):
        """Verify Security Engineer has Backlog Context section."""
        content = validate_md_path.read_text()

        sec_start = content.find("# AGENT CONTEXT: Secure-by-Design Engineer")
        sec_end = content.find("# AGENT CONTEXT: Senior Technical Writer")
        sec_section = content[sec_start:sec_end]

        assert "Backlog Context:" in sec_section


class TestTechWriterBacklogIntegration:
    """Test Technical Writer agent backlog integration."""

    def test_tech_writer_has_backlog_instructions_marker(self, validate_md_path):
        """Verify Tech Writer context includes backlog instructions marker."""
        content = validate_md_path.read_text()

        # Extract Tech Writer section
        tw_start = content.find("# AGENT CONTEXT: Senior Technical Writer")
        tw_end = content.find("# AGENT CONTEXT: Senior Release Manager")
        tw_section = content[tw_start:tw_end]

        assert "{{BACKLOG_INSTRUCTIONS}}" in tw_section

    def test_tech_writer_has_task_creation_instructions(self, validate_md_path):
        """Verify Tech Writer has backlog task creation instructions."""
        content = validate_md_path.read_text()

        # Extract Tech Writer section
        tw_start = content.find("# AGENT CONTEXT: Senior Technical Writer")
        tw_end = content.find("# AGENT CONTEXT: Senior Release Manager")
        tw_section = content[tw_start:tw_end]

        # Check for task creation instructions
        assert "Create backlog tasks for major documentation work" in tw_section or \
               "backlog task create" in tw_section

    def test_tech_writer_has_documentation_task_example(self, validate_md_path):
        """Verify Tech Writer has example of creating documentation task."""
        content = validate_md_path.read_text()

        tw_start = content.find("# AGENT CONTEXT: Senior Technical Writer")
        tw_end = content.find("# AGENT CONTEXT: Senior Release Manager")
        tw_section = content[tw_start:tw_end]

        # Should have example backlog task creation
        assert 'backlog task create "Documentation:' in tw_section
        assert '--ac "API documentation complete"' in tw_section or \
               "API documentation" in tw_section

    def test_tech_writer_has_backlog_context_section(self, validate_md_path):
        """Verify Tech Writer has Backlog Context section."""
        content = validate_md_path.read_text()

        tw_start = content.find("# AGENT CONTEXT: Senior Technical Writer")
        tw_end = content.find("# AGENT CONTEXT: Senior Release Manager")
        tw_section = content[tw_start:tw_end]

        assert "Backlog Context:" in tw_section


class TestReleaseManagerBacklogIntegration:
    """Test Release Manager agent backlog integration."""

    def test_release_manager_has_backlog_instructions_marker(self, validate_md_path):
        """Verify Release Manager context includes backlog instructions marker."""
        content = validate_md_path.read_text()

        # Extract Release Manager section
        rm_start = content.find("# AGENT CONTEXT: Senior Release Manager")
        rm_section = content[rm_start:]

        assert "{{BACKLOG_INSTRUCTIONS}}" in rm_section

    def test_release_manager_has_dod_verification(self, validate_md_path):
        """Verify Release Manager has Definition of Done verification requirements."""
        content = validate_md_path.read_text()

        # Extract Release Manager section
        rm_start = content.find("# AGENT CONTEXT: Senior Release Manager")
        rm_section = content[rm_start:]

        # Check for DoD verification
        assert "Definition of Done" in rm_section or "DoD" in rm_section
        assert "All acceptance criteria checked" in rm_section
        assert "Implementation notes added" in rm_section
        assert "Mark tasks as Done ONLY after" in rm_section

    def test_release_manager_has_backlog_context_section(self, validate_md_path):
        """Verify Release Manager has Backlog Context section."""
        content = validate_md_path.read_text()

        rm_start = content.find("# AGENT CONTEXT: Senior Release Manager")
        rm_section = content[rm_start:]

        assert "Backlog Context:" in rm_section


class TestBacklogInstructionsContent:
    """Test that backlog instructions file has required content."""

    def test_backlog_instructions_file_exists(self, backlog_instructions_path):
        """Verify _backlog-instructions.md exists."""
        assert backlog_instructions_path.exists(), \
            "_backlog-instructions.md must exist"

    def test_backlog_instructions_has_core_sections(self, backlog_instructions_path):
        """Verify backlog instructions has all core sections."""
        content = backlog_instructions_path.read_text()

        # Check for key sections
        assert "## Critical Rules" in content
        assert "## Task Discovery" in content
        assert "## Starting Work on a Task" in content
        assert "## Tracking Progress with Acceptance Criteria" in content
        assert "## Completing Tasks" in content
        assert "## Definition of Done Checklist" in content

    def test_backlog_instructions_has_cli_examples(self, backlog_instructions_path):
        """Verify backlog instructions has CLI command examples."""
        content = backlog_instructions_path.read_text()

        # Check for essential CLI commands
        assert "backlog task list" in content
        assert "backlog task edit" in content
        assert "--check-ac" in content
        assert "--plain" in content


class TestValidateWorkflowIntegration:
    """Test complete validate workflow integration."""

    def test_validate_workflow_order(self, validate_md_path):
        """Verify validate.md follows correct workflow order."""
        content = validate_md_path.read_text()

        # Find positions of key sections
        discovery_pos = content.find("## Backlog Task Discovery")
        qa_pos = content.find("# AGENT CONTEXT: Quality Guardian")
        security_pos = content.find("# AGENT CONTEXT: Secure-by-Design Engineer")
        tech_writer_pos = content.find("# AGENT CONTEXT: Senior Technical Writer")
        release_pos = content.find("# AGENT CONTEXT: Senior Release Manager")

        # Verify order: discovery → QA → security → tech writer → release
        assert discovery_pos < qa_pos, "Task discovery must come before QA"
        assert qa_pos < security_pos, "QA must come before Security"
        assert security_pos < tech_writer_pos, "Security must come before Tech Writer"
        assert tech_writer_pos < release_pos, "Tech Writer must come before Release Manager"

    def test_validate_parallel_execution_note(self, validate_md_path):
        """Verify validate.md notes parallel execution for QA and Security."""
        content = validate_md_path.read_text()

        # Should mention parallel execution
        assert "parallel" in content.lower() or "Parallel" in content

    def test_validate_has_human_approval_gate(self, validate_md_path):
        """Verify validate.md includes human approval gate."""
        content = validate_md_path.read_text()

        # Should have human approval requirements
        assert "human approval" in content.lower() or "Human Approval" in content
        assert "REQUEST EXPLICIT HUMAN APPROVAL" in content or \
               "require explicit human approval" in content.lower()


class TestValidateCommandUsage:
    """Test validate command usage scenarios."""

    def test_validate_discovers_in_progress_tasks(self, validate_md_path):
        """Verify command instructs to discover In Progress tasks."""
        content = validate_md_path.read_text()
        assert 'backlog task list -s "In Progress"' in content

    def test_validate_discovers_done_tasks(self, validate_md_path):
        """Verify command instructs to discover Done tasks."""
        content = validate_md_path.read_text()
        assert 'backlog task list -s "Done"' in content

    def test_validate_uses_plain_output(self, validate_md_path):
        """Verify command uses --plain flag for AI-readable output."""
        content = validate_md_path.read_text()

        # All backlog commands should use --plain
        list_commands = content.count("backlog task list")
        plain_flags = content.count("--plain")

        # Should have at least as many --plain flags as list commands
        assert plain_flags >= list_commands, \
            "All backlog task list commands should use --plain flag"


class TestAgentConsistency:
    """Test consistency across all four agent contexts."""

    def test_all_agents_have_backlog_instructions(self, validate_md_path):
        """Verify all four agents have {{BACKLOG_INSTRUCTIONS}} marker."""
        content = validate_md_path.read_text()

        agents = [
            "Quality Guardian",
            "Secure-by-Design Engineer",
            "Senior Technical Writer",
            "Senior Release Manager"
        ]

        for agent in agents:
            agent_start = content.find(f"# AGENT CONTEXT: {agent}")
            assert agent_start != -1, f"{agent} context not found"

            # Find next agent or end of file
            next_agent_pos = len(content)
            for next_agent in agents:
                if next_agent != agent:
                    pos = content.find(f"# AGENT CONTEXT: {next_agent}", agent_start + 1)
                    if pos != -1 and pos < next_agent_pos:
                        next_agent_pos = pos

            agent_section = content[agent_start:next_agent_pos]
            assert "{{BACKLOG_INSTRUCTIONS}}" in agent_section, \
                f"{agent} missing {{{{BACKLOG_INSTRUCTIONS}}}} marker"

    def test_all_agents_have_backlog_context(self, validate_md_path):
        """Verify all four agents have Backlog Context section."""
        content = validate_md_path.read_text()

        agents = [
            "Quality Guardian",
            "Secure-by-Design Engineer",
            "Senior Technical Writer",
            "Senior Release Manager"
        ]

        for agent in agents:
            agent_start = content.find(f"# AGENT CONTEXT: {agent}")

            # Find next agent or end of file
            next_agent_pos = len(content)
            for next_agent in agents:
                if next_agent != agent:
                    pos = content.find(f"# AGENT CONTEXT: {next_agent}", agent_start + 1)
                    if pos != -1 and pos < next_agent_pos:
                        next_agent_pos = pos

            agent_section = content[agent_start:next_agent_pos]
            assert "Backlog Context:" in agent_section, \
                f"{agent} missing Backlog Context section"


class TestDocumentationQuality:
    """Test documentation quality and completeness."""

    def test_validate_has_description(self, validate_md_path):
        """Verify validate.md has proper frontmatter description."""
        content = validate_md_path.read_text()
        assert "description:" in content
        assert "Execute validation and quality assurance" in content

    def test_validate_explains_backlog_template(self, validate_md_path):
        """Verify validate.md explains the {{BACKLOG_INSTRUCTIONS}} template."""
        content = validate_md_path.read_text()

        # Should explain what to do with the template marker
        assert "{{BACKLOG_INSTRUCTIONS}}" in content
        assert "_backlog-instructions.md" in content
        assert "replaced" in content.lower() or "include" in content.lower()

    def test_validate_has_clear_phase_structure(self, validate_md_path):
        """Verify validate.md has clear phase structure."""
        content = validate_md_path.read_text()

        # Should have clear phase markers
        assert "Phase 1:" in content or "### Phase 1:" in content
        assert "Phase 2:" in content or "### Phase 2:" in content
        assert "Phase 3:" in content or "### Phase 3:" in content
