"""Tests for /jpspec:validate backlog.md integration.

Verifies AC#1-AC#7 for task-113:
- AC#1: Command discovers tasks in In Progress or Done status for validation
- AC#2: All 4 validator agents receive shared backlog instructions from _backlog-instructions.md
- AC#3: Quality Guardian validates ACs match test results
- AC#4: Security Engineer validates security-related ACs
- AC#5: Tech Writer creates/updates documentation tasks in backlog
- AC#6: Release Manager verifies Definition of Done before marking tasks Done
- AC#7: Test: Run /jpspec:validate and verify task validation workflow
"""

import re

import pytest
from pathlib import Path


@pytest.fixture
def validate_md_path():
    """Get path to validate.md command file."""
    return (
        Path(__file__).parent.parent / ".claude" / "commands" / "jpspec" / "validate.md"
    )


@pytest.fixture
def backlog_instructions_path():
    """Get path to _backlog-instructions.md file."""
    return (
        Path(__file__).parent.parent
        / ".claude"
        / "commands"
        / "jpspec"
        / "_backlog-instructions.md"
    )


class TestTaskDiscoveryAC1:
    """AC #1: Command discovers tasks in In Progress or Done status for validation."""

    def test_validate_md_exists(self, validate_md_path):
        """Verify validate.md command file exists."""
        assert validate_md_path.exists(), "validate.md command file must exist"

    def test_has_backlog_task_discovery_section(self, validate_md_path):
        """AC #1: Validate.md includes backlog task discovery section."""
        content = validate_md_path.read_text()
        assert "## Backlog Task Discovery" in content

    def test_discovers_in_progress_tasks(self, validate_md_path):
        """AC #1: Command instructs to discover In Progress tasks."""
        content = validate_md_path.read_text()
        assert 'backlog task list -s "In Progress" --plain' in content

    def test_discovers_done_tasks(self, validate_md_path):
        """AC #1: Command instructs to discover Done tasks."""
        content = validate_md_path.read_text()
        assert 'backlog task list -s "Done" --plain' in content

    def test_view_task_details_for_validation(self, validate_md_path):
        """AC #1: Command instructs to view specific task details."""
        content = validate_md_path.read_text()
        assert "backlog task <id> --plain" in content

    def test_uses_plain_output_flag(self, validate_md_path):
        """AC #1: All discovery commands use --plain for AI-readable output."""
        content = validate_md_path.read_text()

        # Use regex to find all backlog task list commands and verify each has --plain
        list_commands = re.findall(r"backlog task list[^\n]*", content)
        assert len(list_commands) > 0, "Expected at least one backlog task list command"
        assert all("--plain" in cmd for cmd in list_commands), (
            "All backlog task list commands must include --plain flag. "
            f"Found commands: {list_commands}"
        )


class TestSharedBacklogInstructionsAC2:
    """AC #2: All 4 validator agents receive shared backlog instructions."""

    def test_has_four_agent_contexts(self, validate_md_path):
        """AC #2: Validate.md has all four agent contexts."""
        content = validate_md_path.read_text()

        assert "# AGENT CONTEXT: Quality Guardian" in content
        assert "# AGENT CONTEXT: Secure-by-Design Engineer" in content
        assert "# AGENT CONTEXT: Senior Technical Writer" in content
        assert "# AGENT CONTEXT: Senior Release Manager" in content

    def test_has_four_backlog_instructions_markers(self, validate_md_path):
        """AC #2: Each agent has {{BACKLOG_INSTRUCTIONS}} marker."""
        content = validate_md_path.read_text()

        marker_count = content.count("{{BACKLOG_INSTRUCTIONS}}")
        assert marker_count >= 4, (
            f"Expected at least 4 {{{{BACKLOG_INSTRUCTIONS}}}} markers, "
            f"found {marker_count}"
        )

    def test_all_agents_have_backlog_instructions_marker(self, validate_md_path):
        """AC #2: Verify all four agents have {{BACKLOG_INSTRUCTIONS}} marker."""
        content = validate_md_path.read_text()

        agents = [
            "Quality Guardian",
            "Secure-by-Design Engineer",
            "Senior Technical Writer",
            "Senior Release Manager",
        ]

        for agent in agents:
            agent_start = content.find(f"# AGENT CONTEXT: {agent}")
            assert agent_start != -1, f"{agent} context not found"

            # Find next agent or end of file
            next_agent_pos = len(content)
            for next_agent in agents:
                if next_agent != agent:
                    pos = content.find(
                        f"# AGENT CONTEXT: {next_agent}", agent_start + 1
                    )
                    if pos != -1 and pos < next_agent_pos:
                        next_agent_pos = pos

            agent_section = content[agent_start:next_agent_pos]
            assert "{{BACKLOG_INSTRUCTIONS}}" in agent_section, (
                f"{agent} missing {{{{BACKLOG_INSTRUCTIONS}}}} marker"
            )

    def test_backlog_instructions_file_exists(self, backlog_instructions_path):
        """AC #2: Verify _backlog-instructions.md exists for shared instructions."""
        assert backlog_instructions_path.exists(), (
            "_backlog-instructions.md must exist for shared backlog instructions"
        )

    def test_backlog_instructions_has_core_sections(self, backlog_instructions_path):
        """AC #2: Shared backlog instructions has all core sections."""
        content = backlog_instructions_path.read_text()

        assert "## Critical Rules" in content
        assert "## Task Discovery" in content
        assert "## Starting Work on a Task" in content
        assert "## Tracking Progress with Acceptance Criteria" in content
        assert "## Completing Tasks" in content
        assert "## Definition of Done Checklist" in content

    def test_backlog_instructions_has_cli_examples(self, backlog_instructions_path):
        """AC #2: Shared instructions has CLI command examples."""
        content = backlog_instructions_path.read_text()

        assert "backlog task list" in content
        assert "backlog task edit" in content
        assert "--check-ac" in content
        assert "--plain" in content

    def test_explains_template_inclusion(self, validate_md_path):
        """AC #2: Validate.md explains the {{BACKLOG_INSTRUCTIONS}} template."""
        content = validate_md_path.read_text()

        assert "{{BACKLOG_INSTRUCTIONS}}" in content
        assert "_backlog-instructions.md" in content
        assert "replaced" in content.lower() or "include" in content.lower()


class TestQualityGuardianAC3:
    """AC #3: Quality Guardian validates ACs match test results."""

    def test_qa_has_backlog_instructions_marker(self, validate_md_path):
        """AC #3: QA agent context includes backlog instructions marker."""
        content = validate_md_path.read_text()

        qa_start = content.find("# AGENT CONTEXT: Quality Guardian")
        qa_end = content.find("# AGENT CONTEXT: Secure-by-Design Engineer")
        qa_section = content[qa_start:qa_end]

        assert "{{BACKLOG_INSTRUCTIONS}}" in qa_section

    def test_qa_verifies_acceptance_criteria_met(self, validate_md_path):
        """AC #3: QA verifies all backlog task ACs are met."""
        content = validate_md_path.read_text()

        qa_start = content.find("# AGENT CONTEXT: Quality Guardian")
        qa_end = content.find("# AGENT CONTEXT: Secure-by-Design Engineer")
        qa_section = content[qa_start:qa_end]

        assert "Verify all backlog task acceptance criteria are met" in qa_section

    def test_qa_cross_references_test_results_with_acs(self, validate_md_path):
        """AC #3: QA cross-references test results with AC requirements."""
        content = validate_md_path.read_text()

        qa_start = content.find("# AGENT CONTEXT: Quality Guardian")
        qa_end = content.find("# AGENT CONTEXT: Secure-by-Design Engineer")
        qa_section = content[qa_start:qa_end]

        assert "Cross-reference test results with AC requirements" in qa_section

    def test_qa_marks_acs_complete_via_cli(self, validate_md_path):
        """AC #3: QA marks ACs complete via backlog CLI as validation succeeds."""
        content = validate_md_path.read_text()

        qa_start = content.find("# AGENT CONTEXT: Quality Guardian")
        qa_end = content.find("# AGENT CONTEXT: Secure-by-Design Engineer")
        qa_section = content[qa_start:qa_end]

        assert "Mark ACs complete via backlog CLI" in qa_section

    def test_qa_has_backlog_context_section(self, validate_md_path):
        """AC #3: QA agent has Backlog Context section for task details."""
        content = validate_md_path.read_text()

        qa_start = content.find("# AGENT CONTEXT: Quality Guardian")
        qa_end = content.find("# AGENT CONTEXT: Secure-by-Design Engineer")
        qa_section = content[qa_start:qa_end]

        assert "Backlog Context:" in qa_section


class TestSecurityEngineerAC4:
    """AC #4: Security Engineer validates security-related ACs."""

    def test_security_has_backlog_instructions_marker(self, validate_md_path):
        """AC #4: Security Engineer context includes backlog instructions marker."""
        content = validate_md_path.read_text()

        sec_start = content.find("# AGENT CONTEXT: Secure-by-Design Engineer")
        sec_end = content.find("# AGENT CONTEXT: Senior Technical Writer")
        sec_section = content[sec_start:sec_end]

        assert "{{BACKLOG_INSTRUCTIONS}}" in sec_section

    def test_security_validates_security_acs(self, validate_md_path):
        """AC #4: Security Engineer validates security-related acceptance criteria."""
        content = validate_md_path.read_text()

        sec_start = content.find("# AGENT CONTEXT: Secure-by-Design Engineer")
        sec_end = content.find("# AGENT CONTEXT: Senior Technical Writer")
        sec_section = content[sec_start:sec_end]

        assert "Validate security-related acceptance criteria" in sec_section

    def test_security_marks_acs_complete_via_cli(self, validate_md_path):
        """AC #4: Security Engineer marks security ACs complete via backlog CLI."""
        content = validate_md_path.read_text()

        sec_start = content.find("# AGENT CONTEXT: Secure-by-Design Engineer")
        sec_end = content.find("# AGENT CONTEXT: Senior Technical Writer")
        sec_section = content[sec_start:sec_end]

        assert "Mark security ACs complete via backlog CLI" in sec_section

    def test_security_cross_references_tests_with_acs(self, validate_md_path):
        """AC #4: Security Engineer cross-references security tests with task ACs."""
        content = validate_md_path.read_text()

        sec_start = content.find("# AGENT CONTEXT: Secure-by-Design Engineer")
        sec_end = content.find("# AGENT CONTEXT: Senior Technical Writer")
        sec_section = content[sec_start:sec_end]

        assert "Cross-reference security tests with task ACs" in sec_section

    def test_security_has_backlog_context_section(self, validate_md_path):
        """AC #4: Security Engineer has Backlog Context section."""
        content = validate_md_path.read_text()

        sec_start = content.find("# AGENT CONTEXT: Secure-by-Design Engineer")
        sec_end = content.find("# AGENT CONTEXT: Senior Technical Writer")
        sec_section = content[sec_start:sec_end]

        assert "Backlog Context:" in sec_section

    def test_security_updates_task_notes_with_findings(self, validate_md_path):
        """AC #4: Security Engineer updates task notes with security findings."""
        content = validate_md_path.read_text()

        sec_start = content.find("# AGENT CONTEXT: Secure-by-Design Engineer")
        sec_end = content.find("# AGENT CONTEXT: Senior Technical Writer")
        sec_section = content[sec_start:sec_end]

        assert "Update task notes with security findings" in sec_section


class TestTechWriterAC5:
    """AC #5: Tech Writer creates/updates documentation tasks in backlog."""

    def test_tech_writer_has_backlog_instructions_marker(self, validate_md_path):
        """AC #5: Tech Writer context includes backlog instructions marker."""
        content = validate_md_path.read_text()

        tw_start = content.find("# AGENT CONTEXT: Senior Technical Writer")
        tw_end = content.find("# AGENT CONTEXT: Senior Release Manager")
        tw_section = content[tw_start:tw_end]

        assert "{{BACKLOG_INSTRUCTIONS}}" in tw_section

    def test_tech_writer_creates_documentation_tasks(self, validate_md_path):
        """AC #5: Tech Writer has instructions to create documentation tasks."""
        content = validate_md_path.read_text()

        tw_start = content.find("# AGENT CONTEXT: Senior Technical Writer")
        tw_end = content.find("# AGENT CONTEXT: Senior Release Manager")
        tw_section = content[tw_start:tw_end]

        assert "Create backlog tasks for major documentation work" in tw_section or (
            "backlog task create" in tw_section
        )

    def test_tech_writer_has_documentation_task_example(self, validate_md_path):
        """AC #5: Tech Writer has example of creating documentation task."""
        content = validate_md_path.read_text()

        tw_start = content.find("# AGENT CONTEXT: Senior Technical Writer")
        tw_end = content.find("# AGENT CONTEXT: Senior Release Manager")
        tw_section = content[tw_start:tw_end]

        # Should have example backlog task creation
        assert 'backlog task create "Documentation:' in tw_section

    def test_tech_writer_documentation_task_has_acs(self, validate_md_path):
        """AC #5: Documentation task examples include acceptance criteria."""
        content = validate_md_path.read_text()

        tw_start = content.find("# AGENT CONTEXT: Senior Technical Writer")
        tw_end = content.find("# AGENT CONTEXT: Senior Release Manager")
        tw_section = content[tw_start:tw_end]

        assert '--ac "API documentation complete"' in tw_section or (
            "API documentation" in tw_section
        )

    def test_tech_writer_marks_acs_on_completion(self, validate_md_path):
        """AC #5: Tech Writer marks ACs complete as documentation sections are done."""
        content = validate_md_path.read_text()

        tw_start = content.find("# AGENT CONTEXT: Senior Technical Writer")
        tw_end = content.find("# AGENT CONTEXT: Senior Release Manager")
        tw_section = content[tw_start:tw_end]

        assert "--check-ac" in tw_section or "mark corresponding ACs" in tw_section

    def test_tech_writer_has_backlog_context_section(self, validate_md_path):
        """AC #5: Tech Writer has Backlog Context section."""
        content = validate_md_path.read_text()

        tw_start = content.find("# AGENT CONTEXT: Senior Technical Writer")
        tw_end = content.find("# AGENT CONTEXT: Senior Release Manager")
        tw_section = content[tw_start:tw_end]

        assert "Backlog Context:" in tw_section


class TestReleaseManagerAC6:
    """AC #6: Release Manager verifies Definition of Done before marking tasks Done."""

    def test_release_manager_has_backlog_instructions_marker(self, validate_md_path):
        """AC #6: Release Manager context includes backlog instructions marker."""
        content = validate_md_path.read_text()

        rm_start = content.find("# AGENT CONTEXT: Senior Release Manager")
        rm_section = content[rm_start:]

        assert "{{BACKLOG_INSTRUCTIONS}}" in rm_section

    def test_release_manager_has_dod_verification_section(self, validate_md_path):
        """AC #6: Release Manager has Definition of Done verification section."""
        content = validate_md_path.read_text()

        rm_start = content.find("# AGENT CONTEXT: Senior Release Manager")
        rm_section = content[rm_start:]

        assert "Definition of Done" in rm_section or "DoD" in rm_section

    def test_release_manager_verifies_all_acs_checked(self, validate_md_path):
        """AC #6: Release Manager verifies all acceptance criteria are checked."""
        content = validate_md_path.read_text()

        rm_start = content.find("# AGENT CONTEXT: Senior Release Manager")
        rm_section = content[rm_start:]

        assert "All acceptance criteria checked" in rm_section

    def test_release_manager_verifies_implementation_notes(self, validate_md_path):
        """AC #6: Release Manager verifies implementation notes are added."""
        content = validate_md_path.read_text()

        rm_start = content.find("# AGENT CONTEXT: Senior Release Manager")
        rm_section = content[rm_start:]

        assert "Implementation notes added" in rm_section

    def test_release_manager_marks_done_only_after_dod(self, validate_md_path):
        """AC #6: Release Manager marks tasks as Done ONLY after DoD is verified."""
        content = validate_md_path.read_text()

        rm_start = content.find("# AGENT CONTEXT: Senior Release Manager")
        rm_section = content[rm_start:]

        assert "Mark tasks as Done ONLY after" in rm_section

    def test_release_manager_uses_backlog_cli_for_status(self, validate_md_path):
        """AC #6: Release Manager uses backlog CLI to mark tasks Done."""
        content = validate_md_path.read_text()

        rm_start = content.find("# AGENT CONTEXT: Senior Release Manager")
        rm_section = content[rm_start:]

        assert "backlog task edit" in rm_section
        assert "-s Done" in rm_section

    def test_release_manager_has_backlog_context_section(self, validate_md_path):
        """AC #6: Release Manager has Backlog Context section."""
        content = validate_md_path.read_text()

        rm_start = content.find("# AGENT CONTEXT: Senior Release Manager")
        rm_section = content[rm_start:]

        assert "Backlog Context:" in rm_section


class TestValidationWorkflowAC7:
    """AC #7: Test: Run /jpspec:validate and verify task validation workflow.

    This test class verifies the complete validation workflow integration
    and validates the structural integrity of the validate.md command.
    """

    def test_validate_workflow_order(self, validate_md_path):
        """AC #7: Verify validate.md follows correct workflow order."""
        content = validate_md_path.read_text()

        # Find positions of key sections
        discovery_pos = content.find("## Backlog Task Discovery")
        qa_pos = content.find("# AGENT CONTEXT: Quality Guardian")
        security_pos = content.find("# AGENT CONTEXT: Secure-by-Design Engineer")
        tech_writer_pos = content.find("# AGENT CONTEXT: Senior Technical Writer")
        release_pos = content.find("# AGENT CONTEXT: Senior Release Manager")

        # Verify order: discovery -> QA -> security -> tech writer -> release
        assert discovery_pos < qa_pos, "Task discovery must come before QA"
        assert qa_pos < security_pos, "QA must come before Security"
        assert security_pos < tech_writer_pos, "Security must come before Tech Writer"
        assert tech_writer_pos < release_pos, (
            "Tech Writer must come before Release Manager"
        )

    def test_validate_parallel_execution_note(self, validate_md_path):
        """AC #7: Verify validate.md notes parallel execution for QA and Security."""
        content = validate_md_path.read_text()
        assert "parallel" in content.lower() or "Parallel" in content

    def test_validate_has_human_approval_gate(self, validate_md_path):
        """AC #7: Verify validate.md includes human approval gate."""
        content = validate_md_path.read_text()

        assert "human approval" in content.lower() or "Human Approval" in content
        assert "REQUEST EXPLICIT HUMAN APPROVAL" in content or (
            "require explicit human approval" in content.lower()
        )

    def test_complete_workflow_structure(self, validate_md_path):
        """AC #7: Verify complete workflow has all required phases."""
        content = validate_md_path.read_text()

        # Should have clear phase markers
        assert "Phase 1:" in content or "### Phase 1:" in content
        assert "Phase 2:" in content or "### Phase 2:" in content
        assert "Phase 3:" in content or "### Phase 3:" in content

    def test_all_four_agents_integrated(self, validate_md_path):
        """AC #7: Verify all four validator agents are integrated in workflow."""
        content = validate_md_path.read_text()

        agents = [
            "Quality Guardian",
            "Secure-by-Design Engineer",
            "Senior Technical Writer",
            "Senior Release Manager",
        ]

        for agent in agents:
            agent_start = content.find(f"# AGENT CONTEXT: {agent}")
            assert agent_start != -1, f"{agent} context not found in workflow"

            # Find next agent or end of file
            next_agent_pos = len(content)
            for next_agent in agents:
                if next_agent != agent:
                    pos = content.find(
                        f"# AGENT CONTEXT: {next_agent}", agent_start + 1
                    )
                    if pos != -1 and pos < next_agent_pos:
                        next_agent_pos = pos

            agent_section = content[agent_start:next_agent_pos]
            # Each agent should have backlog integration
            assert "{{BACKLOG_INSTRUCTIONS}}" in agent_section, (
                f"{agent} missing backlog integration"
            )
            assert "Backlog Context:" in agent_section, (
                f"{agent} missing Backlog Context section"
            )

    def test_validation_context_provided_to_agents(self, validate_md_path):
        """AC #7: Verify validation context is provided to all agents."""
        content = validate_md_path.read_text()

        assert "Validation Context" in content or "validation context" in content

    def test_deliverables_section_exists(self, validate_md_path):
        """AC #7: Verify validate.md has deliverables section."""
        content = validate_md_path.read_text()
        assert "### Deliverables" in content or "## Deliverables" in content

    def test_validate_has_frontmatter(self, validate_md_path):
        """AC #7: Verify validate.md has proper frontmatter description."""
        content = validate_md_path.read_text()
        assert "description:" in content
        assert "Execute validation and quality assurance" in content
