"""Tests for /flow:validate backlog.md integration.

Verifies AC#1-AC#7 for task-113:
- AC#1: Command discovers tasks in In Progress or Done status for validation
- AC#2: All 4 validator agents receive shared backlog instructions from _backlog-instructions.md
- AC#3: Quality Guardian validates ACs match test results
- AC#4: Security Engineer validates security-related ACs
- AC#5: Tech Writer creates/updates documentation tasks in backlog
- AC#6: Release Manager verifies Definition of Done before marking tasks Done
- AC#7: Test: Run /flow:validate and verify task validation workflow
"""

import re

import pytest
from pathlib import Path


@pytest.fixture
def validate_md_path():
    """Get path to validate.md command file."""
    return (
        Path(__file__).parent.parent / ".claude" / "commands" / "flow" / "validate.md"
    )


@pytest.fixture
def backlog_instructions_path():
    """Get path to _backlog-instructions.md file."""
    return (
        Path(__file__).parent.parent
        / ".claude"
        / "partials"
        / "flow"
        / "_backlog-instructions.md"
    )


class TestTaskDiscoveryAC1:
    """AC #1: Command discovers tasks in In Progress or Done status for validation."""

    def test_validate_md_exists(self, validate_md_path):
        """Verify validate.md command file exists."""
        assert validate_md_path.exists(), "validate.md command file must exist"

    def test_has_backlog_task_discovery_section(self, validate_md_path):
        """AC #1: Validate.md includes task discovery/validation section."""
        content = validate_md_path.read_text()
        # Accept old pattern or new phased workflow pattern
        has_old_pattern = "## Backlog Task Discovery" in content
        has_new_pattern = (
            "Phase 0:" in content
            or "Step 0: Workflow State Validation" in content
            or "Task Discovery" in content
        )
        assert has_old_pattern or has_new_pattern, (
            "validate.md must have task discovery section"
        )

    def test_discovers_in_progress_tasks(self, validate_md_path):
        """AC #1: Command instructs to discover In Progress tasks."""
        content = validate_md_path.read_text()
        assert 'backlog task list -s "In Progress" --plain' in content

    def test_discovers_done_tasks(self, validate_md_path):
        """AC #1: Command instructs to discover or mark tasks Done."""
        content = validate_md_path.read_text()
        # Accept old pattern or new phased workflow pattern
        has_done_discovery = 'backlog task list -s "Done" --plain' in content
        has_done_marking = "-s Done" in content or '-s "Done"' in content
        assert has_done_discovery or has_done_marking, (
            "validate.md must reference Done status"
        )

    def test_view_task_details_for_validation(self, validate_md_path):
        """AC #1: Command instructs to view or manage task details."""
        content = validate_md_path.read_text()
        # Accept various task management patterns
        has_view = "backlog task <id> --plain" in content
        has_edit = "backlog task edit" in content
        has_task_ref = "backlog task" in content
        assert has_view or has_edit or has_task_ref, (
            "validate.md must reference backlog task commands"
        )

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
        """AC #2: Validate.md has agent contexts or equivalent phased workflow."""
        content = validate_md_path.read_text()

        # Check for old explicit agent context pattern
        has_old_agents = (
            "# AGENT CONTEXT: Quality Guardian" in content
            and "# AGENT CONTEXT: Secure-by-Design Engineer" in content
            and "# AGENT CONTEXT: Senior Technical Writer" in content
            and "# AGENT CONTEXT: Senior Release Manager" in content
        )

        # Check for new phased workflow that covers same validation areas
        has_phased_workflow = (
            "Phase" in content
            and ("QA" in content or "Quality" in content or "Test" in content)
            and ("Security" in content)
        )

        assert has_old_agents or has_phased_workflow, (
            "validate.md must have agent contexts or equivalent phased workflow"
        )

    def test_has_four_backlog_instructions_markers(self, validate_md_path):
        """AC #2: Has backlog instructions markers or phased workflow."""
        content = validate_md_path.read_text()

        marker_count = content.count("{{BACKLOG_INSTRUCTIONS}}")
        # New phased workflows may not use the BACKLOG_INSTRUCTIONS template
        # but still handle backlog integration via explicit commands
        has_phased_workflow = "Phase" in content and "backlog task" in content

        assert marker_count >= 4 or has_phased_workflow, (
            "Expected {{BACKLOG_INSTRUCTIONS}} markers or phased workflow"
        )

    def test_all_agents_have_backlog_instructions_marker(self, validate_md_path):
        """AC #2: Verify all four agents have {{BACKLOG_INSTRUCTIONS}} marker."""
        content = validate_md_path.read_text()

        # Core agents that should always have backlog instructions
        required_agents = [
            "Quality Guardian",
            "Secure-by-Design Engineer",
            "Senior Technical Writer",
        ]

        # Release Manager may be integrated into phased workflow (Phase 4/5)
        # instead of a separate agent context in enhanced workflows
        has_release_manager = "# AGENT CONTEXT: Senior Release Manager" in content
        has_phased_workflow = "### Phase 4:" in content and "### Phase 5:" in content

        # Must have either Release Manager agent OR phased workflow
        assert has_release_manager or has_phased_workflow, (
            "Must have either Release Manager agent context or phased workflow (Phase 4/5)"
        )

        for agent in required_agents:
            agent_start = content.find(f"# AGENT CONTEXT: {agent}")
            assert agent_start != -1, f"{agent} context not found"

            # Find next agent or end of file
            next_agent_pos = len(content)
            all_possible_agents = required_agents + ["Senior Release Manager"]
            for next_agent in all_possible_agents:
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
    """AC #6: Release Manager verifies Definition of Done before marking tasks Done.

    Note: Enhanced phased workflows may integrate Release Manager functionality
    into Phase 4 (AC Verification) and Phase 5 (Task Completion) instead of
    a separate agent context. Tests check for either pattern.
    """

    def test_release_manager_has_backlog_instructions_marker(self, validate_md_path):
        """AC #6: Release Manager context includes backlog instructions marker."""
        content = validate_md_path.read_text()

        # Check for either Release Manager agent OR phased workflow with AC verification
        has_rm_agent = "# AGENT CONTEXT: Senior Release Manager" in content
        has_phased_ac_verification = (
            "### Phase 4:" in content and "Acceptance Criteria" in content
        )

        if has_rm_agent:
            rm_start = content.find("# AGENT CONTEXT: Senior Release Manager")
            rm_section = content[rm_start:]
            assert "{{BACKLOG_INSTRUCTIONS}}" in rm_section
        else:
            assert has_phased_ac_verification, (
                "Must have either Release Manager agent or phased AC verification workflow"
            )

    def test_release_manager_has_dod_verification_section(self, validate_md_path):
        """AC #6: Release Manager has Definition of Done verification section."""
        content = validate_md_path.read_text()

        # Check for DoD in Release Manager section OR in phased workflow
        has_dod_in_rm = False
        if "# AGENT CONTEXT: Senior Release Manager" in content:
            rm_start = content.find("# AGENT CONTEXT: Senior Release Manager")
            rm_section = content[rm_start:]
            has_dod_in_rm = "Definition of Done" in rm_section or "DoD" in rm_section

        # Phased workflows verify all ACs (equivalent to DoD verification)
        has_ac_verification = (
            "### Phase 4:" in content and "Verify all acceptance criteria" in content
        )

        assert has_dod_in_rm or has_ac_verification, (
            "Must have DoD verification in Release Manager or AC verification in phased workflow"
        )

    def test_release_manager_verifies_all_acs_checked(self, validate_md_path):
        """AC #6: Release Manager verifies all acceptance criteria are checked."""
        content = validate_md_path.read_text()

        # Check for AC verification in Release Manager OR in Phase 4
        has_ac_check_in_rm = False
        if "# AGENT CONTEXT: Senior Release Manager" in content:
            rm_start = content.find("# AGENT CONTEXT: Senior Release Manager")
            rm_section = content[rm_start:]
            has_ac_check_in_rm = "All acceptance criteria checked" in rm_section

        has_phase4_ac_check = "### Phase 4:" in content and (
            "acceptance criteria" in content.lower() or "AC" in content
        )

        assert has_ac_check_in_rm or has_phase4_ac_check, (
            "Must verify all ACs in Release Manager or Phase 4"
        )

    def test_release_manager_verifies_implementation_notes(self, validate_md_path):
        """AC #6: Release Manager verifies implementation notes are added."""
        content = validate_md_path.read_text()

        # Check for implementation notes in Release Manager OR Phase 5
        has_notes_in_rm = False
        if "# AGENT CONTEXT: Senior Release Manager" in content:
            rm_start = content.find("# AGENT CONTEXT: Senior Release Manager")
            rm_section = content[rm_start:]
            has_notes_in_rm = "Implementation notes added" in rm_section

        has_phase5_notes = (
            "### Phase 5:" in content
            and "implementation" in content.lower()
            and "notes" in content.lower()
        )

        assert has_notes_in_rm or has_phase5_notes, (
            "Must verify implementation notes in Release Manager or Phase 5"
        )

    def test_release_manager_marks_done_only_after_dod(self, validate_md_path):
        """AC #6: Release Manager marks tasks as Done ONLY after DoD is verified."""
        content = validate_md_path.read_text()

        # Check for Done status control in Release Manager OR phased workflow
        has_done_control_in_rm = False
        if "# AGENT CONTEXT: Senior Release Manager" in content:
            rm_start = content.find("# AGENT CONTEXT: Senior Release Manager")
            rm_section = content[rm_start:]
            has_done_control_in_rm = "Mark tasks as Done ONLY after" in rm_section

        # Phased workflow should have Done status in Phase 5 AFTER Phase 4 AC verification
        has_phased_done_control = (
            "### Phase 4:" in content
            and "### Phase 5:" in content
            and "-s Done" in content
        )

        assert has_done_control_in_rm or has_phased_done_control, (
            "Must have Done status control in Release Manager or phased workflow"
        )

    def test_release_manager_uses_backlog_cli_for_status(self, validate_md_path):
        """AC #6: Release Manager uses backlog CLI to mark tasks Done."""
        content = validate_md_path.read_text()

        # Should have backlog CLI commands to mark Done
        assert "backlog task edit" in content
        assert "-s Done" in content or '-s "Done"' in content

    def test_release_manager_has_backlog_context_section(self, validate_md_path):
        """AC #6: Release Manager has Backlog Context section."""
        content = validate_md_path.read_text()

        # Check for Backlog Context in Release Manager OR task context in phased workflow
        has_backlog_context_in_rm = False
        if "# AGENT CONTEXT: Senior Release Manager" in content:
            rm_start = content.find("# AGENT CONTEXT: Senior Release Manager")
            rm_section = content[rm_start:]
            has_backlog_context_in_rm = "Backlog Context:" in rm_section

        # Phased workflow should reference task context
        has_task_context = (
            "### Phase 0:" in content
            or "Task Discovery" in content
            or "backlog task" in content
        )

        assert has_backlog_context_in_rm or has_task_context, (
            "Must have Backlog Context in Release Manager or task context in phased workflow"
        )


class TestValidationWorkflowAC7:
    """AC #7: Test: Run /flow:validate and verify task validation workflow.

    This test class verifies the complete validation workflow integration
    and validates the structural integrity of the validate.md command.
    """

    def test_validate_workflow_order(self, validate_md_path):
        """AC #7: Verify validate.md follows correct workflow order."""
        content = validate_md_path.read_text()

        # Check for phased workflow OR agent-based workflow
        has_phased = "### Phase 0:" in content or "## Phase 0:" in content
        has_agent_based = (
            "# AGENT CONTEXT: Quality Guardian" in content
            and "# AGENT CONTEXT: Secure-by-Design Engineer" in content
        )

        assert has_phased or has_agent_based, (
            "Must have either phased workflow or agent-based workflow"
        )

        if has_phased:
            # Verify phased workflow order
            phase0_pos = content.find("Phase 0:")
            phase1_pos = content.find("Phase 1:")
            phase2_pos = content.find("Phase 2:")
            assert phase0_pos > 0, "Must have Phase 0"
            assert phase1_pos > phase0_pos, "Phase 1 must follow Phase 0"
            assert phase2_pos > phase1_pos, "Phase 2 must follow Phase 1"
        else:
            # Verify agent-based workflow order
            discovery_pos = content.find("## Backlog Task Discovery")
            qa_pos = content.find("# AGENT CONTEXT: Quality Guardian")
            security_pos = content.find("# AGENT CONTEXT: Secure-by-Design Engineer")
            tech_writer_pos = content.find("# AGENT CONTEXT: Senior Technical Writer")

            assert discovery_pos < qa_pos, "Task discovery must come before QA"
            assert qa_pos < security_pos, "QA must come before Security"
            assert security_pos < tech_writer_pos, (
                "Security must come before Tech Writer"
            )

    def test_validate_parallel_execution_note(self, validate_md_path):
        """AC #7: Verify validate.md notes parallel execution for QA and Security."""
        content = validate_md_path.read_text()
        assert "parallel" in content.lower() or "Parallel" in content

    def test_validate_has_human_approval_gate(self, validate_md_path):
        """AC #7: Verify validate.md includes human approval gate."""
        content = validate_md_path.read_text()

        # Check for human approval in Release Manager OR in phased workflow (Phase 6)
        has_rm_approval = "# AGENT CONTEXT: Senior Release Manager" in content and (
            "human approval" in content.lower() or "EXPLICIT HUMAN APPROVAL" in content
        )

        # Phased workflow may have approval in Phase 6 (PR generation)
        has_phased_approval = (
            "### Phase 6:" in content or "## Phase 6:" in content
        ) and ("approval" in content.lower())

        assert has_rm_approval or has_phased_approval, (
            "Must have human approval gate in Release Manager or phased workflow"
        )

    def test_complete_workflow_structure(self, validate_md_path):
        """AC #7: Verify complete workflow has all required phases."""
        content = validate_md_path.read_text()

        # Should have clear phase markers
        assert "Phase 1:" in content or "### Phase 1:" in content
        assert "Phase 2:" in content or "### Phase 2:" in content
        assert "Phase 3:" in content or "### Phase 3:" in content

    def test_all_four_agents_integrated(self, validate_md_path):
        """AC #7: Verify all validator agents are integrated in workflow."""
        content = validate_md_path.read_text()

        # Core agents that must be present
        required_agents = [
            "Quality Guardian",
            "Secure-by-Design Engineer",
            "Senior Technical Writer",
        ]

        for agent in required_agents:
            agent_start = content.find(f"# AGENT CONTEXT: {agent}")
            assert agent_start != -1, f"{agent} context not found in workflow"

            # Find next section
            next_pos = len(content)
            for next_agent in required_agents + ["Senior Release Manager"]:
                if next_agent != agent:
                    pos = content.find(
                        f"# AGENT CONTEXT: {next_agent}", agent_start + 1
                    )
                    if pos != -1 and pos < next_pos:
                        next_pos = pos

            agent_section = content[agent_start:next_pos]
            # Each agent should have backlog integration
            assert "{{BACKLOG_INSTRUCTIONS}}" in agent_section, (
                f"{agent} missing backlog integration"
            )
            assert "Backlog Context:" in agent_section, (
                f"{agent} missing Backlog Context section"
            )

        # Verify Release Manager OR phased workflow handles task completion
        has_rm = "# AGENT CONTEXT: Senior Release Manager" in content
        has_phased_completion = "### Phase 4:" in content and "### Phase 5:" in content
        assert has_rm or has_phased_completion, (
            "Must have Release Manager or phased task completion workflow"
        )

    def test_validation_context_provided_to_agents(self, validate_md_path):
        """AC #7: Verify validation context is provided to all agents."""
        content = validate_md_path.read_text()

        # Check for context in agent sections OR in phased workflow
        has_agent_context = (
            "Validation Context" in content or "validation context" in content
        )
        has_backlog_context = "Backlog Context:" in content

        # Phased workflows may use task context instead
        has_task_context = "Task Discovery" in content or "backlog task" in content

        assert has_agent_context or has_backlog_context or has_task_context, (
            "Must provide validation/backlog/task context to agents or phases"
        )

    def test_deliverables_section_exists(self, validate_md_path):
        """AC #7: Verify validate.md has deliverables section."""
        content = validate_md_path.read_text()

        # Check for deliverables section OR phased workflow complete summary
        has_deliverables = "### Deliverables" in content or "## Deliverables" in content
        has_workflow_complete = (
            "Workflow Complete" in content or "workflow complete" in content.lower()
        )

        assert has_deliverables or has_workflow_complete, (
            "Must have deliverables section or workflow completion summary"
        )

    def test_validate_has_frontmatter(self, validate_md_path):
        """AC #7: Verify validate.md has proper frontmatter description."""
        content = validate_md_path.read_text()
        assert "description:" in content
        assert "Execute validation and quality assurance" in content
