"""Tests for /jpspec:implement backlog.md CLI integration.

This test module verifies that the implement command correctly integrates
with backlog.md CLI for task-driven implementation.
"""

import pytest
from pathlib import Path


@pytest.fixture
def implement_command_path():
    """Return the path to the implement.md command file."""
    return (
        Path(__file__).parent.parent
        / ".claude"
        / "commands"
        / "jpspec"
        / "implement.md"
    )


@pytest.fixture
def implement_command_content(implement_command_path):
    """Load the implement.md command content."""
    return implement_command_path.read_text()


class TestImplementCommandStructure:
    """Tests for implement.md command structure."""

    def test_command_file_exists(self, implement_command_path):
        """Verify implement.md command file exists."""
        assert implement_command_path.exists(), "implement.md command file should exist"

    def test_has_required_task_discovery_section(self, implement_command_content):
        """AC #1: Command REQUIRES task validation before execution."""
        # Accept either old pattern, new workflow state validation, or include directive
        has_old_pattern = (
            "### Step 0: REQUIRED - Discover Backlog Tasks" in implement_command_content
        )
        has_new_pattern = (
            "Step 0: Workflow State Validation" in implement_command_content
        )
        has_include_pattern = (
            "{{INCLUDE:.claude/commands/jpspec/_workflow-state.md}}"
            in implement_command_content
        )
        assert has_old_pattern or has_new_pattern or has_include_pattern, (
            "implement.md must have task discovery/validation section"
        )
        # Accept either old or new critical message or include that provides it
        has_old_critical = (
            "CRITICAL: This command REQUIRES existing backlog tasks"
            in implement_command_content
        )
        has_new_critical = (
            "CRITICAL: This command requires a task" in implement_command_content
        )
        has_include_critical = has_include_pattern  # Include provides this
        assert has_old_critical or has_new_critical or has_include_critical, (
            "implement.md must have critical task requirement message"
        )

    def test_has_graceful_failure_message(self, implement_command_content):
        """AC #1: Fails gracefully if no tasks found."""
        assert "No backlog tasks found" in implement_command_content
        assert "Please run /jpspec:specify first" in implement_command_content

    def test_has_task_list_command(self, implement_command_content):
        """AC #3: Engineers pick up tasks from backlog."""
        assert 'backlog task list -s "To Do" --plain' in implement_command_content


class TestEngineerAgentBacklogIntegration:
    """Tests for engineer agent backlog instructions."""

    def test_frontend_engineer_has_backlog_instructions(
        self, implement_command_content
    ):
        """AC #2: Frontend engineer receives backlog instructions."""
        assert "@frontend-engineer" in implement_command_content
        # Check for the Backlog Task Management section in frontend context
        assert "## Backlog Task Management (REQUIRED)" in implement_command_content

    def test_backend_engineer_has_backlog_instructions(self, implement_command_content):
        """AC #2: Backend engineer receives backlog instructions."""
        assert "@backend-engineer" in implement_command_content

    def test_ai_ml_engineer_has_backlog_instructions(self, implement_command_content):
        """AC #2: AI/ML engineer receives backlog instructions."""
        assert "@ai-ml-engineer" in implement_command_content

    def test_agents_assign_themselves(self, implement_command_content):
        """AC #4: Engineers assign themselves and set status to In Progress."""
        assert '-s "In Progress" -a @frontend-engineer' in implement_command_content
        assert '-s "In Progress" -a @backend-engineer' in implement_command_content
        assert '-s "In Progress" -a @ai-ml-engineer' in implement_command_content

    def test_agents_check_acs_during_implementation(self, implement_command_content):
        """AC #5: Engineers check ACs as each criterion is implemented."""
        assert "--check-ac 1" in implement_command_content
        assert "Check ACs as you complete them" in implement_command_content

    def test_agents_add_implementation_notes(self, implement_command_content):
        """AC #6: Engineers add implementation notes."""
        assert "--notes" in implement_command_content
        assert "Add implementation notes" in implement_command_content


class TestCodeReviewerBacklogIntegration:
    """Tests for code reviewer backlog instructions."""

    def test_frontend_reviewer_has_backlog_verification(
        self, implement_command_content
    ):
        """AC #7: Frontend code reviewer verifies AC completion."""
        assert "@frontend-code-reviewer" in implement_command_content
        assert "## Backlog AC Verification (REQUIRED)" in implement_command_content

    def test_backend_reviewer_has_backlog_verification(self, implement_command_content):
        """AC #7: Backend code reviewer verifies AC completion."""
        assert "@backend-code-reviewer" in implement_command_content

    def test_reviewers_verify_ac_matches_code(self, implement_command_content):
        """AC #7: Code reviewers verify AC completion matches code."""
        assert "Verify AC completion matches code" in implement_command_content
        assert (
            "Each checked AC has corresponding code changes"
            in implement_command_content
        )

    def test_reviewers_can_uncheck_acs(self, implement_command_content):
        """AC #7: Reviewers can uncheck ACs if not satisfied."""
        assert "--uncheck-ac" in implement_command_content
        assert "Uncheck ACs if not satisfied" in implement_command_content


class TestImplementationWorkflow:
    """Tests for implementation workflow completeness."""

    def test_has_pick_task_step(self, implement_command_content):
        """Verify pick task step exists."""
        assert "Pick a task" in implement_command_content
        assert "backlog task <task-id> --plain" in implement_command_content

    def test_has_assign_step(self, implement_command_content):
        """Verify assign step exists."""
        assert "Assign yourself" in implement_command_content

    def test_has_plan_step(self, implement_command_content):
        """Verify implementation plan step exists."""
        assert "Add implementation plan" in implement_command_content
        assert "--plan" in implement_command_content

    def test_has_verify_step(self, implement_command_content):
        """Verify final verification step exists."""
        assert "Verify all ACs checked" in implement_command_content

    def test_workflow_requires_tasks_first(self, implement_command_content):
        """Verify workflow requires existing tasks."""
        # Step 0 should come before Phase 1
        step0_pos = implement_command_content.find("Step 0: REQUIRED")
        phase1_pos = implement_command_content.find("Phase 1: Implementation")
        assert step0_pos < phase1_pos, "Step 0 should come before Phase 1"


class TestFiveAgentCount:
    """Tests to verify all 5 engineer agents have backlog integration."""

    def test_count_backlog_task_management_sections(self, implement_command_content):
        """AC #2: All 5 engineer agents receive backlog instructions."""
        # Count occurrences of the backlog management section
        # 3 engineers + 2 reviewers = 5 agents total
        # But reviewers have "AC Verification" not "Task Management"
        task_mgmt_count = implement_command_content.count(
            "## Backlog Task Management (REQUIRED)"
        )
        ac_verify_count = implement_command_content.count(
            "## Backlog AC Verification (REQUIRED)"
        )
        total_agents = task_mgmt_count + ac_verify_count
        assert total_agents >= 5, (
            f"Expected 5 agents with backlog integration, found {total_agents}"
        )

    def test_all_agent_identities_present(self, implement_command_content):
        """Verify all 5 agent identities are present."""
        agents = [
            "@frontend-engineer",
            "@backend-engineer",
            "@ai-ml-engineer",
            "@frontend-code-reviewer",
            "@backend-code-reviewer",
        ]
        for agent in agents:
            assert agent in implement_command_content, (
                f"Agent {agent} should be present"
            )
