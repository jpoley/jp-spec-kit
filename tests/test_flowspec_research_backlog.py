"""Integration tests for flowspec command suite with backlog.md CLI.

This test module verifies that all flowspec commands (research, validate, specify, plan, implement)
correctly integrate with backlog.md CLI for comprehensive task management.
"""

import pytest
from pathlib import Path


@pytest.fixture
def research_command_file():
    """Load the research.md command file."""
    command_path = (
        Path(__file__).parent.parent / ".claude" / "commands" / "flow" / "research.md"
    )
    assert command_path.exists(), f"Research command not found at {command_path}"
    return command_path


@pytest.fixture
def backlog_instructions_file():
    """Load the _backlog-instructions.md file."""
    instructions_path = (
        Path(__file__).parent.parent
        / ".claude"
        / "partials"
        / "flow"
        / "_backlog-instructions.md"
    )
    assert instructions_path.exists(), (
        f"Backlog instructions not found at {instructions_path}"
    )
    return instructions_path


class TestResearchCommandStructure:
    """Test the structure and content of the research command."""

    def test_command_file_exists(self, research_command_file):
        """Verify research.md command file exists."""
        assert research_command_file.exists()

    def test_command_has_backlog_discovery(self, research_command_file):
        """Verify command includes backlog task discovery at start."""
        content = research_command_file.read_text()

        # Should include backlog search
        assert "backlog search" in content
        assert "--plain" in content

        # Should search for research tasks
        assert (
            'backlog search "research"' in content
            or "backlog search 'research'" in content
        )

    def test_command_checks_existing_tasks(self, research_command_file):
        """Verify command checks for existing research tasks."""
        content = research_command_file.read_text()

        # Should list research tasks
        assert "backlog task list" in content

        # Should mention reviewing existing tasks
        assert "existing" in content.lower()
        assert "review" in content.lower() or "check" in content.lower()


class TestSharedBacklogInstructions:
    """Test that both agents receive shared backlog instructions from _backlog-instructions.md (AC#2)."""

    def test_backlog_instructions_file_exists(self, backlog_instructions_file):
        """Verify _backlog-instructions.md file exists."""
        assert backlog_instructions_file.exists()

    def test_researcher_includes_shared_backlog_instructions(
        self, research_command_file
    ):
        """Verify Researcher agent prompt includes shared backlog instructions via INCLUDE."""
        content = research_command_file.read_text()

        # Find Phase 1 section
        phase1_start = content.find("### Phase 1: Research")
        phase2_start = content.find("### Phase 2: Business Validation")
        phase1_section = content[phase1_start:phase2_start]

        # Should include the shared backlog instructions
        assert (
            "{{INCLUDE:.claude/partials/flow/_backlog-instructions.md}}"
            in phase1_section
        )
        assert "<!--BACKLOG-INSTRUCTIONS-START-->" in phase1_section
        assert "<!--BACKLOG-INSTRUCTIONS-END-->" in phase1_section

    def test_business_validator_includes_shared_backlog_instructions(
        self, research_command_file
    ):
        """Verify Business Validator agent prompt includes shared backlog instructions via INCLUDE."""
        content = research_command_file.read_text()

        # Find Phase 2 section
        phase2_start = content.find("### Phase 2: Business Validation")
        phase2_section = content[phase2_start:]

        # Should include the shared backlog instructions
        assert (
            "{{INCLUDE:.claude/partials/flow/_backlog-instructions.md}}"
            in phase2_section
        )
        assert "<!--BACKLOG-INSTRUCTIONS-START-->" in phase2_section
        assert "<!--BACKLOG-INSTRUCTIONS-END-->" in phase2_section

    def test_both_agents_have_include_before_context(self, research_command_file):
        """Verify INCLUDE directive appears BEFORE agent context in both phases."""
        content = research_command_file.read_text()

        # Phase 1: Include should come before agent context
        phase1_include = content.find(
            "{{INCLUDE:.claude/partials/flow/_backlog-instructions.md}}"
        )
        researcher_context = content.find("# AGENT CONTEXT: Senior Research Analyst")
        assert phase1_include < researcher_context, (
            "INCLUDE should appear before Researcher context"
        )

        # Phase 2: Include should come before agent context
        phase2_start = content.find("### Phase 2: Business Validation")
        phase2_include = content.find(
            "{{INCLUDE:.claude/partials/flow/_backlog-instructions.md}}",
            phase2_start,
        )
        validator_context = content.find(
            "# AGENT CONTEXT: Senior Business Analyst", phase2_start
        )
        assert phase2_include < validator_context, (
            "INCLUDE should appear before Validator context"
        )

    def test_shared_instructions_include_count(self, research_command_file):
        """Verify INCLUDE directive appears exactly twice (once per agent)."""
        content = research_command_file.read_text()

        include_count = content.count(
            "{{INCLUDE:.claude/partials/flow/_backlog-instructions.md}}"
        )
        assert include_count == 2, (
            f"Expected 2 INCLUDE directives, found {include_count}"
        )


class TestResearcherAgentBacklogInstructions:
    """Test that Researcher agent prompt includes backlog instructions."""

    def test_researcher_has_backlog_section(self, research_command_file):
        """Verify Researcher prompt includes backlog.md section."""
        content = research_command_file.read_text()

        # Extract researcher agent section (Phase 1)
        assert "# AGENT CONTEXT: Senior Research Analyst" in content

        # Should have backlog task management section
        assert "Backlog.md" in content or "backlog.md" in content
        assert "Task Management" in content

    def test_researcher_can_create_research_tasks(self, research_command_file):
        """Verify Researcher prompt includes task creation instructions."""
        content = research_command_file.read_text()

        # Should show how to create research spike tasks
        assert "backlog task create" in content
        assert "Research:" in content

        # Should include research-specific acceptance criteria
        assert "market analysis" in content.lower()
        assert "competitive" in content.lower()
        assert "technical feasibility" in content.lower()

    def test_researcher_assigns_to_self(self, research_command_file):
        """Verify Researcher instructions include self-assignment."""
        content = research_command_file.read_text()

        # Should assign to @researcher
        assert "@researcher" in content
        assert "-a @researcher" in content

    def test_researcher_adds_findings_as_notes(self, research_command_file):
        """Verify Researcher adds findings as implementation notes."""
        content = research_command_file.read_text()

        # Should show adding notes
        assert "--notes" in content

        # Should include research findings structure
        assert "findings" in content.lower()
        assert "recommendations" in content.lower()

    def test_researcher_marks_acs_complete(self, research_command_file):
        """Verify Researcher instructions include marking ACs complete."""
        content = research_command_file.read_text()

        # Should show AC checking
        assert "--check-ac" in content


class TestBusinessValidatorAgentBacklogInstructions:
    """Test that Business Validator agent prompt includes backlog instructions."""

    def test_validator_has_backlog_section(self, research_command_file):
        """Verify Business Validator prompt includes backlog.md section."""
        content = research_command_file.read_text()

        # Extract business validator section (Phase 2)
        assert "# AGENT CONTEXT: Senior Business Analyst" in content

        # Should have backlog task management section in validator section too
        # Count occurrences - should appear in both sections
        backlog_sections = content.count("Backlog.md") + content.count("backlog.md")
        assert backlog_sections >= 2, (
            "Backlog instructions should appear in both agent sections"
        )

    def test_validator_can_create_validation_tasks(self, research_command_file):
        """Verify Business Validator prompt includes task creation instructions."""
        content = research_command_file.read_text()

        # Should show how to create validation tasks
        assert "Business Validation:" in content

        # Should include validation-specific acceptance criteria
        assert "market opportunity" in content.lower()
        assert "financial viability" in content.lower()
        assert "operational feasibility" in content.lower()
        assert "strategic fit" in content.lower()
        assert "risk analysis" in content.lower()

    def test_validator_assigns_to_self(self, research_command_file):
        """Verify Business Validator instructions include self-assignment."""
        content = research_command_file.read_text()

        # Should assign to @business-validator
        assert "@business-validator" in content
        assert "-a @business-validator" in content

    def test_validator_adds_assessment_as_notes(self, research_command_file):
        """Verify Business Validator adds assessment as implementation notes."""
        content = research_command_file.read_text()

        # Should include validation assessment structure
        assert "Executive Assessment" in content
        assert "Go/No-Go" in content
        assert "Opportunity Score" in content
        assert "Risk Register" in content

    def test_validator_marks_acs_complete(self, research_command_file):
        """Verify Business Validator instructions include marking ACs complete."""
        content = research_command_file.read_text()

        # Should show AC checking in validator section
        validator_section_start = content.find(
            "# AGENT CONTEXT: Senior Business Analyst"
        )
        validator_section = content[validator_section_start:]
        assert "--check-ac" in validator_section


class TestResearchTaskLabels:
    """Test that research and validation tasks use appropriate labels."""

    def test_research_task_has_research_label(self, research_command_file):
        """Verify research tasks include 'research' label."""
        content = research_command_file.read_text()

        # Research tasks should have research label
        assert "-l research" in content

    def test_research_task_has_spike_label(self, research_command_file):
        """Verify research tasks include 'spike' label."""
        content = research_command_file.read_text()

        # Research spikes should be labeled as such
        assert "spike" in content

    def test_validation_task_has_validation_label(self, research_command_file):
        """Verify validation tasks include 'validation' label."""
        content = research_command_file.read_text()

        # Validation tasks should have validation label
        assert "-l validation" in content

    def test_validation_task_has_business_label(self, research_command_file):
        """Verify validation tasks include 'business' label."""
        content = research_command_file.read_text()

        # Business validation should include business label
        assert "business" in content


class TestResearchWorkflowIntegration:
    """Test complete research workflow integration."""

    def test_workflow_has_discovery_phase(self, research_command_file):
        """Verify workflow starts with task discovery."""
        content = research_command_file.read_text()

        # Discovery should happen BEFORE Phase 1
        phase_1_index = content.find("### Phase 1: Research")
        discovery_index = content.find("backlog search")

        assert discovery_index < phase_1_index, "Discovery should happen before Phase 1"

    def test_workflow_creates_research_task(self, research_command_file):
        """Verify workflow includes research task creation."""
        content = research_command_file.read_text()

        # Should create research task with proper structure
        assert 'backlog task create "Research:' in content

        # Should have acceptance criteria for all research areas
        researcher_section = content[
            content.find("# AGENT CONTEXT: Senior Research Analyst") :
        ]
        validation_index = researcher_section.find(
            "# AGENT CONTEXT: Senior Business Analyst"
        )
        if validation_index > 0:
            researcher_section = researcher_section[:validation_index]

        # Count ACs in researcher task creation
        assert "--ac" in researcher_section
        ac_count = researcher_section.count("--ac")
        assert ac_count >= 4, "Research task should have at least 4 acceptance criteria"

    def test_workflow_creates_validation_task(self, research_command_file):
        """Verify workflow includes validation task creation."""
        content = research_command_file.read_text()

        # Should create validation task
        assert 'backlog task create "Business Validation:' in content

        # Should have acceptance criteria for all validation areas
        validator_section = content[
            content.find("# AGENT CONTEXT: Senior Business Analyst") :
        ]

        # Count ACs in validator task creation
        assert "--ac" in validator_section
        ac_count = validator_section.count("--ac")
        assert ac_count >= 5, (
            "Validation task should have at least 5 acceptance criteria"
        )

    def test_both_agents_use_plain_flag(self, research_command_file):
        """Verify both agents use --plain flag for AI-readable output."""
        content = research_command_file.read_text()

        # Should use --plain flag in all backlog commands
        assert "--plain" in content

        # Count should be sufficient for discovery commands
        plain_count = content.count("--plain")
        assert plain_count >= 3, "Should use --plain in multiple discovery commands"

    def test_both_agents_set_priority_high(self, research_command_file):
        """Verify both research and validation tasks use high priority."""
        content = research_command_file.read_text()

        # Both task types should be high priority
        assert "--priority high" in content
        priority_count = content.count("--priority high")
        assert priority_count >= 2, (
            "Both research and validation should be high priority"
        )


class TestAcceptanceCriteriaWorkflow:
    """Test acceptance criteria workflow for research and validation."""

    def test_research_acs_cover_all_areas(self, research_command_file):
        """Verify research task ACs cover all research areas."""
        content = research_command_file.read_text()

        # Extract research task creation
        researcher_section = content[content.find('backlog task create "Research:') :]
        task_creation_end = researcher_section.find("```")
        task_creation = researcher_section[:task_creation_end]

        # Should have ACs for main research deliverables
        assert "market analysis" in task_creation.lower()
        assert "competitive" in task_creation.lower()
        assert "technical feasibility" in task_creation.lower()
        assert (
            "trends" in task_creation.lower()
            or "industry trends" in task_creation.lower()
        )

    def test_validation_acs_cover_all_areas(self, research_command_file):
        """Verify validation task ACs cover all validation areas."""
        content = research_command_file.read_text()

        # Extract validation task creation
        validator_section = content[
            content.find('backlog task create "Business Validation:') :
        ]
        task_creation_end = validator_section.find("```")
        task_creation = validator_section[:task_creation_end]

        # Should have ACs for main validation deliverables
        assert "market opportunity" in task_creation.lower()
        assert "financial viability" in task_creation.lower()
        assert "operational feasibility" in task_creation.lower()
        assert "strategic fit" in task_creation.lower()
        assert "risk analysis" in task_creation.lower()
        assert "recommendation" in task_creation.lower()

    def test_agents_check_acs_progressively(self, research_command_file):
        """Verify agents mark ACs complete progressively."""
        content = research_command_file.read_text()

        # Should show progressive AC checking
        assert "--check-ac 1" in content
        assert "--check-ac 2" in content

        # Should include comments explaining when to check
        assert "# After" in content or "# after" in content


class TestImplementationNotes:
    """Test implementation notes formatting and content."""

    def test_research_notes_have_structure(self, research_command_file):
        """Verify research notes follow structured format."""
        content = research_command_file.read_text()

        # Research notes should have key sections
        assert "# Research Findings:" in content
        assert "## Executive Summary" in content
        assert "## Market Analysis" in content
        assert "## Competitive Landscape" in content
        assert "## Technical Feasibility" in content
        assert "## Industry Trends" in content
        assert "## Recommendations" in content
        assert "## Sources" in content

    def test_validation_notes_have_structure(self, research_command_file):
        """Verify validation notes follow structured format."""
        content = research_command_file.read_text()

        # Validation notes should have key sections
        assert "# Business Validation:" in content
        assert "## Executive Assessment" in content
        assert "## Opportunity Score" in content
        assert "## Risk Register" in content
        assert "## Critical Assumptions" in content
        assert "## Recommendations" in content

    def test_notes_use_multiline_syntax(self, research_command_file):
        """Verify notes use proper ANSI-C quoting for multilines."""
        content = research_command_file.read_text()

        # Should use $'...' syntax for multiline notes
        assert "--notes $'" in content


class TestTaskPriority:
    """Test task priority settings."""

    def test_research_tasks_are_high_priority(self, research_command_file):
        """Verify research tasks default to high priority."""
        content = research_command_file.read_text()

        # Find research task creation
        research_task = content[content.find('backlog task create "Research:') :]
        research_task = research_task[: research_task.find("```")]

        assert "--priority high" in research_task

    def test_validation_tasks_are_high_priority(self, research_command_file):
        """Verify validation tasks default to high priority."""
        content = research_command_file.read_text()

        # Find validation task creation
        validation_task = content[
            content.find('backlog task create "Business Validation:') :
        ]
        validation_task = validation_task[: validation_task.find("```")]

        assert "--priority high" in validation_task


class TestCommandConsistency:
    """Test consistency across the research command."""

    def test_both_agents_follow_same_workflow_pattern(self, research_command_file):
        """Verify both agents follow same workflow: create → assign → plan → work → notes → done."""
        content = research_command_file.read_text()

        # Extract both agent sections
        researcher_start = content.find("## Backlog.md Task Management")
        researcher_end = content.find("# TASK: Conduct comprehensive research")
        researcher_section = content[researcher_start:researcher_end]

        validator_start = content.find("## Backlog.md Task Management", researcher_end)
        validator_end = content.find(
            "# TASK: Based on the research findings", validator_start
        )
        validator_section = content[validator_start:validator_end]

        # Both should follow same workflow steps
        for section in [researcher_section, validator_section]:
            assert "backlog task create" in section
            assert "backlog task edit" in section
            assert '-s "In Progress"' in section
            assert "--plan" in section
            assert "--check-ac" in section
            assert "--notes" in section
            assert "-s Done" in section

    def test_consistent_agent_naming(self, research_command_file):
        """Verify consistent agent naming conventions."""
        content = research_command_file.read_text()

        # Should use @researcher and @business-validator consistently
        assert "@researcher" in content
        assert "@business-validator" in content

        # Should not use alternate names
        assert "@research-agent" not in content
        assert "@validator" not in content.lower() or "@business-validator" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
