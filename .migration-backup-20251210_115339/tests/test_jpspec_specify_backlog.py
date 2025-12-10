"""Tests for /jpspec:specify backlog.md CLI integration.

This test module verifies that the specify command correctly integrates
with backlog.md CLI for task discovery and creation.
"""

import pytest
from pathlib import Path


@pytest.fixture
def specify_command_path():
    """Return the path to the specify.md command file."""
    return (
        Path(__file__).parent.parent / ".claude" / "commands" / "jpspec" / "specify.md"
    )


@pytest.fixture
def specify_command_content(specify_command_path):
    """Load the specify.md command content."""
    return specify_command_path.read_text()


class TestSpecifyCommandStructure:
    """Tests for specify.md command structure."""

    def test_command_file_exists(self, specify_command_path):
        """Verify specify.md command file exists."""
        assert specify_command_path.exists(), "specify.md command file should exist"

    def test_has_task_discovery_section(self, specify_command_content):
        """AC #1: Command checks for existing backlog tasks (backlog search)."""
        assert "### Step 1: Discover Existing Tasks" in specify_command_content
        assert 'backlog search "$ARGUMENTS" --plain' in specify_command_content
        assert "backlog task list" in specify_command_content

    def test_has_backlog_cli_integration_in_agent_prompt(self, specify_command_content):
        """AC #2: PM planner agent receives backlog instructions."""
        assert "## Backlog.md CLI Integration" in specify_command_content
        assert "backlog.md CLI for task management" in specify_command_content

    def test_agent_creates_tasks_via_cli(self, specify_command_content):
        """AC #3: Agent creates new tasks via backlog task create."""
        assert "backlog task create" in specify_command_content
        # Check for task creation example with proper flags
        assert "--ac" in specify_command_content
        assert "-d" in specify_command_content

    def test_agent_assigns_itself_to_tasks(self, specify_command_content):
        """AC #4: Agent assigns itself to tasks it creates."""
        assert "@pm-planner" in specify_command_content
        assert "-a @pm-planner" in specify_command_content

    def test_prd_includes_task_ids(self, specify_command_content):
        """AC #5: Generated PRD includes backlog task IDs."""
        assert "Task Breakdown (Backlog Tasks)" in specify_command_content
        assert "task-XXX" in specify_command_content
        assert "Backlog task ID" in specify_command_content


class TestBacklogInstructionsIntegration:
    """Tests for backlog instructions integration in agent prompt."""

    def test_has_key_commands_section(self, specify_command_content):
        """Verify key commands are documented for the agent."""
        assert "**Key Commands**:" in specify_command_content
        assert "Search tasks:" in specify_command_content
        assert "Create task:" in specify_command_content
        assert "View task:" in specify_command_content

    def test_has_critical_instruction(self, specify_command_content):
        """Verify CRITICAL instruction for task creation."""
        assert "**CRITICAL**:" in specify_command_content
        assert "use the backlog CLI to actually create them" in specify_command_content

    def test_task_creation_patterns_included(self, specify_command_content):
        """Verify task creation patterns are included."""
        # Check for backend task pattern
        assert "implement,backend" in specify_command_content
        # Check for frontend task pattern
        assert "implement,frontend" in specify_command_content
        # Check for priority setting
        assert "--priority high" in specify_command_content


class TestDesignImplementWorkflow:
    """Tests for design→implement workflow compliance."""

    def test_has_design_implement_section(self, specify_command_content):
        """Verify design→implement workflow section exists."""
        assert "Design→Implement Workflow" in specify_command_content

    def test_verification_command_included(self, specify_command_content):
        """Verify task creation verification is documented."""
        assert "Verify tasks were created" in specify_command_content
        assert "backlog task list --plain" in specify_command_content

    def test_failure_warning_included(self, specify_command_content):
        """Verify failure warning is present."""
        assert "Failure to create implementation tasks" in specify_command_content


class TestOutputSection:
    """Tests for output section documentation."""

    def test_output_includes_task_creation(self, specify_command_content):
        """Verify output section mentions task creation."""
        assert "Actual backlog tasks" in specify_command_content
        assert "created via CLI" in specify_command_content

    def test_output_mentions_traceability(self, specify_command_content):
        """Verify output mentions traceability."""
        assert "task IDs" in specify_command_content
        assert "traceability" in specify_command_content


class TestTaskCreationRequirements:
    """Tests for task creation requirements."""

    def test_minimum_acceptance_criteria_requirement(self, specify_command_content):
        """Verify minimum AC requirement is documented."""
        assert "minimum 2 per task" in specify_command_content

    def test_dependency_flag_documented(self, specify_command_content):
        """Verify dependency flag is documented."""
        assert "--dep" in specify_command_content

    def test_priority_levels_documented(self, specify_command_content):
        """Verify priority levels are documented."""
        assert (
            "P0=high" in specify_command_content
            or "priority high" in specify_command_content.lower()
        )

    def test_complexity_labels_documented(self, specify_command_content):
        """Verify complexity labels are documented."""
        assert (
            "size-s" in specify_command_content or "size-m" in specify_command_content
        )
