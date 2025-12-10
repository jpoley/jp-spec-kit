"""Tests for /jpspec:plan command backlog.md integration.

This test module verifies that the /jpspec:plan command correctly integrates
with backlog.md CLI for architecture and infrastructure task management.
"""

import pytest
from pathlib import Path


@pytest.fixture
def plan_command_path():
    """Return path to the plan.md command file."""
    return Path(__file__).parent.parent / ".claude" / "commands" / "jpspec" / "plan.md"


@pytest.fixture
def backlog_instructions_path():
    """Return path to the _backlog-instructions.md file."""
    return (
        Path(__file__).parent.parent
        / ".claude"
        / "commands"
        / "jpspec"
        / "_backlog-instructions.md"
    )


class TestPlanCommandStructure:
    """Tests for plan.md command file structure."""

    def test_plan_command_exists(self, plan_command_path):
        """Verify plan.md command file exists."""
        assert plan_command_path.exists()

    def test_plan_command_has_task_discovery_section(self, plan_command_path):
        """Verify plan.md includes task discovery/validation section."""
        content = plan_command_path.read_text()
        # Accept either old pattern, new workflow state validation, or include directive
        has_old_pattern = "Step 0: Backlog Task Discovery" in content
        has_new_pattern = "Step 0: Workflow State Validation" in content
        has_include_pattern = (
            "{{INCLUDE:.claude/commands/jpspec/_workflow-state.md}}" in content
        )
        assert has_old_pattern or has_new_pattern or has_include_pattern, (
            "plan.md must have task discovery/validation section"
        )
        # Task list command should be present in either format
        assert "backlog task list" in content

    def test_plan_includes_backlog_instructions(self, plan_command_path):
        """Verify plan.md includes backlog instructions in both agents."""
        content = plan_command_path.read_text()

        # Should have two includes (one for each agent)
        includes = content.count(
            "{{INCLUDE:.claude/commands/jpspec/_backlog-instructions.md}}"
        )
        assert includes == 2, (
            f"Expected 2 backlog instruction includes, found {includes}"
        )

    def test_architect_agent_has_backlog_section(self, plan_command_path):
        """Verify Software Architect agent has backlog task creation section."""
        content = plan_command_path.read_text()

        # Find the Software Architect section
        assert "# AGENT CONTEXT: Enterprise Software Architect" in content

        # Verify it has backlog task management requirements
        assert "Backlog Task Management Requirements" in content
        assert "Architecture Tasks to Create:" in content
        assert "Architecture Decision Records (ADRs)" in content
        assert "Design Documentation" in content
        assert "Pattern Implementation" in content

    def test_platform_engineer_has_backlog_section(self, plan_command_path):
        """Verify Platform Engineer agent has backlog task creation section."""
        content = plan_command_path.read_text()

        # Find the Platform Engineer section
        assert "# AGENT CONTEXT: Platform Engineer" in content

        # Verify it has backlog task management requirements
        assert "Infrastructure Tasks to Create:" in content
        assert "CI/CD Pipeline Setup" in content
        assert "Observability Implementation" in content
        assert "Security Controls" in content
        assert "Infrastructure as Code" in content

    def test_backlog_instructions_file_exists(self, backlog_instructions_path):
        """Verify _backlog-instructions.md file exists."""
        assert backlog_instructions_path.exists()

    def test_backlog_instructions_has_key_sections(self, backlog_instructions_path):
        """Verify _backlog-instructions.md has all required sections."""
        content = backlog_instructions_path.read_text()

        # Check for critical sections
        assert "Critical Rules" in content
        assert "Task Discovery" in content
        assert "Starting Work on a Task" in content
        assert "Tracking Progress with Acceptance Criteria" in content
        assert "Creating New Tasks" in content
        assert "Completing Tasks" in content
        assert "Definition of Done" in content


class TestTaskDiscoveryWorkflow:
    """Tests for task discovery workflow in plan command."""

    def test_discovery_searches_by_feature_name(self, plan_command_path):
        """Verify task discovery includes feature-specific search."""
        content = plan_command_path.read_text()
        assert 'backlog search "<feature-name>" --plain' in content

    def test_discovery_lists_planning_tasks(self, plan_command_path):
        """Verify task discovery lists planning-related tasks."""
        content = plan_command_path.read_text()
        assert "backlog task list -l planning --plain" in content
        assert "backlog task list -l architecture --plain" in content
        assert "backlog task list -l infrastructure --plain" in content

    def test_discovery_lists_in_progress_tasks(self, plan_command_path):
        """Verify task discovery includes in-progress tasks."""
        content = plan_command_path.read_text()
        assert 'backlog task list -s "In Progress" --plain' in content

    def test_discovery_provides_context_guidance(self, plan_command_path):
        """Verify task discovery explains what to review."""
        content = plan_command_path.read_text()
        assert "What planning work is already tracked" in content
        assert "What tasks the agents should update vs. create new" in content
        assert "Dependencies between tasks" in content


class TestArchitectTaskCreation:
    """Tests for Software Architect task creation patterns."""

    def test_architect_creates_adr_tasks(self, plan_command_path):
        """Verify architect guidance for ADR tasks."""
        content = plan_command_path.read_text()

        # Should have ADR task pattern
        assert 'Title: "ADR: [Decision topic]"' in content
        assert "architecture, adr" in content

    def test_architect_creates_design_tasks(self, plan_command_path):
        """Verify architect guidance for design documentation tasks."""
        content = plan_command_path.read_text()

        assert 'Title: "Design: [Component/System name]"' in content
        assert "architecture, design" in content

    def test_architect_creates_pattern_tasks(self, plan_command_path):
        """Verify architect guidance for pattern implementation tasks."""
        content = plan_command_path.read_text()

        assert 'Title: "Implement [Pattern name] pattern"' in content
        assert "architecture, pattern" in content

    def test_architect_has_task_creation_command(self, plan_command_path):
        """Verify architect has backlog task create command example."""
        content = plan_command_path.read_text()

        # Find architect section
        architect_section_start = content.find(
            "# AGENT CONTEXT: Enterprise Software Architect"
        )
        architect_section_end = content.find("# AGENT CONTEXT: Platform Engineer")
        architect_section = content[architect_section_start:architect_section_end]

        # Verify task creation command in architect section
        assert "backlog task create" in architect_section
        assert "--ac" in architect_section
        assert "-l architecture" in architect_section

    def test_architect_has_task_update_command(self, plan_command_path):
        """Verify architect has backlog task edit command for existing tasks."""
        content = plan_command_path.read_text()

        architect_section_start = content.find(
            "# AGENT CONTEXT: Enterprise Software Architect"
        )
        architect_section_end = content.find("# AGENT CONTEXT: Platform Engineer")
        architect_section = content[architect_section_start:architect_section_end]

        assert "backlog task edit" in architect_section
        assert "@software-architect" in architect_section


class TestPlatformEngineerTaskCreation:
    """Tests for Platform Engineer task creation patterns."""

    def test_platform_creates_cicd_tasks(self, plan_command_path):
        """Verify platform engineer guidance for CI/CD tasks."""
        content = plan_command_path.read_text()

        assert 'Title: "Setup [Pipeline stage] in CI/CD"' in content
        assert "infrastructure, cicd" in content

    def test_platform_creates_observability_tasks(self, plan_command_path):
        """Verify platform engineer guidance for observability tasks."""
        content = plan_command_path.read_text()

        assert 'Title: "Implement [Metrics/Logging/Tracing] for [Component]"' in content
        assert "infrastructure, observability" in content

    def test_platform_creates_security_tasks(self, plan_command_path):
        """Verify platform engineer guidance for security tasks."""
        content = plan_command_path.read_text()

        assert 'Title: "Implement [Security control]"' in content
        assert "infrastructure, security, devsecops" in content

    def test_platform_creates_iac_tasks(self, plan_command_path):
        """Verify platform engineer guidance for IaC tasks."""
        content = plan_command_path.read_text()

        assert 'Title: "IaC: [Infrastructure component]"' in content
        assert "infrastructure, iac" in content

    def test_platform_has_task_creation_command(self, plan_command_path):
        """Verify platform engineer has backlog task create command example."""
        content = plan_command_path.read_text()

        # Find platform engineer section
        platform_section_start = content.find("# AGENT CONTEXT: Platform Engineer")
        platform_section = content[platform_section_start:]

        # Verify task creation command in platform section
        assert "backlog task create" in platform_section
        assert "--ac" in platform_section
        assert "-l infrastructure" in platform_section

    def test_platform_has_task_update_command(self, plan_command_path):
        """Verify platform engineer has backlog task edit command."""
        content = plan_command_path.read_text()

        platform_section_start = content.find("# AGENT CONTEXT: Platform Engineer")
        platform_section = content[platform_section_start:]

        assert "backlog task edit" in platform_section
        assert "@platform-engineer" in platform_section


class TestBacklogInstructionsContent:
    """Tests for _backlog-instructions.md content."""

    def test_includes_critical_rules(self, backlog_instructions_path):
        """Verify critical rules are present."""
        content = backlog_instructions_path.read_text()

        assert "NEVER edit task files directly" in content
        assert "Use `--plain` flag" in content
        assert "Mark ACs complete as you finish them" in content

    def test_includes_task_discovery_commands(self, backlog_instructions_path):
        """Verify task discovery commands are documented."""
        content = backlog_instructions_path.read_text()

        assert "backlog search" in content
        assert "backlog task list" in content
        assert "backlog task <id> --plain" in content

    def test_includes_starting_work_workflow(self, backlog_instructions_path):
        """Verify starting work workflow is documented."""
        content = backlog_instructions_path.read_text()

        assert 'backlog task edit <id> -s "In Progress"' in content
        assert "backlog task edit <id> --plan" in content

    def test_includes_ac_management(self, backlog_instructions_path):
        """Verify AC management commands are documented."""
        content = backlog_instructions_path.read_text()

        assert "--check-ac" in content
        assert "--uncheck-ac" in content

    def test_includes_task_creation(self, backlog_instructions_path):
        """Verify task creation is documented."""
        content = backlog_instructions_path.read_text()

        assert "backlog task create" in content
        assert "Every task MUST have at least one acceptance criterion" in content

    def test_includes_definition_of_done(self, backlog_instructions_path):
        """Verify Definition of Done is documented."""
        content = backlog_instructions_path.read_text()

        assert "Definition of Done" in content
        assert "All acceptance criteria checked" in content
        assert "Implementation notes added" in content

    def test_includes_agent_identification(self, backlog_instructions_path):
        """Verify agent names are documented."""
        content = backlog_instructions_path.read_text()

        assert "@software-architect" in content
        assert "@platform-engineer" in content


class TestIntegrationScenarios:
    """Integration tests for complete planning scenarios."""

    def test_plan_command_supports_architecture_workflow(self, plan_command_path):
        """Verify plan command supports complete architecture workflow."""
        content = plan_command_path.read_text()

        # Check for task discovery/validation (accept old, new, or include pattern)
        has_task_section = (
            "Step 0: Backlog Task Discovery" in content
            or "Step 0: Workflow State Validation" in content
            or "{{INCLUDE:.claude/commands/jpspec/_workflow-state.md}}" in content
        )
        assert has_task_section, "plan.md must have task discovery/validation section"

        # Should have all components needed for architect workflow
        workflow_components = [
            "Software Architect",
            "Architecture Tasks to Create",
            "ADR:",
            "Design:",
            "backlog task create",
            "backlog task edit",
        ]

        for component in workflow_components:
            assert component in content, f"Missing workflow component: {component}"

    def test_plan_command_supports_platform_workflow(self, plan_command_path):
        """Verify plan command supports complete platform workflow."""
        content = plan_command_path.read_text()

        # Check for task discovery/validation (accept old, new, or include pattern)
        has_task_section = (
            "Step 0: Backlog Task Discovery" in content
            or "Step 0: Workflow State Validation" in content
            or "{{INCLUDE:.claude/commands/jpspec/_workflow-state.md}}" in content
        )
        assert has_task_section, "plan.md must have task discovery/validation section"

        # Should have all components needed for platform workflow
        workflow_components = [
            "Platform Engineer",
            "Infrastructure Tasks to Create",
            "CI/CD Pipeline",
            "Observability",
            "Security Controls",
            "backlog task create",
            "backlog task edit",
        ]

        for component in workflow_components:
            assert component in content, f"Missing workflow component: {component}"

    def test_both_agents_receive_shared_instructions(self, plan_command_path):
        """Verify both agents receive the same backlog instructions."""
        content = plan_command_path.read_text()

        # Count INCLUDE directives
        includes = []
        for line in content.split("\n"):
            if "{{INCLUDE:.claude/commands/jpspec/_backlog-instructions.md}}" in line:
                includes.append(line)

        # Should have exactly 2 includes (one per agent)
        assert len(includes) == 2
        # Both should be identical
        assert includes[0] == includes[1]

    def test_agents_can_update_existing_tasks(self, plan_command_path):
        """Verify agents have guidance for updating existing tasks."""
        content = plan_command_path.read_text()

        # Both agents should mention updating existing tasks
        assert content.count("Update existing tasks") >= 2
        assert content.count("if discovered in Step 0") >= 2

    def test_task_labels_are_specific_to_agent_role(self, plan_command_path):
        """Verify task labels match agent responsibilities."""
        content = plan_command_path.read_text()

        # Architect section should have architecture labels
        architect_start = content.find("# AGENT CONTEXT: Enterprise Software Architect")
        architect_end = content.find("# AGENT CONTEXT: Platform Engineer")
        architect_section = content[architect_start:architect_end]

        assert "architecture" in architect_section
        assert "adr" in architect_section
        assert "design" in architect_section

        # Platform section should have infrastructure labels
        platform_section = content[architect_end:]

        assert "infrastructure" in platform_section
        assert "cicd" in platform_section
        assert "observability" in platform_section
        assert "security" in platform_section
        assert "iac" in platform_section


class TestBacklogCLIUsagePatterns:
    """Tests for correct backlog CLI usage patterns."""

    def test_all_search_commands_use_plain_flag(self, plan_command_path):
        """Verify all backlog search commands use --plain flag."""
        content = plan_command_path.read_text()

        # Find all backlog search/list commands
        lines = content.split("\n")
        for line in lines:
            # Skip comments early
            if line.strip().startswith("#"):
                continue

            # Check if line contains backlog commands
            if "backlog search" not in line and "backlog task list" not in line:
                continue

            # Check if it's an actual command (in code block or quoted)
            if '"' not in line and "`" not in line:
                continue

            # Should have --plain flag
            assert "--plain" in line, f"Missing --plain flag in: {line}"

    def test_task_create_includes_mandatory_ac(self, plan_command_path):
        """Verify task create examples include acceptance criteria."""
        content = plan_command_path.read_text()

        # Find all backlog task create commands
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if "backlog task create" in line and not line.strip().startswith("#"):
                # Should have --ac flag within next few lines (multi-line command)
                context = "\n".join(lines[i : i + 5])
                assert "--ac" in context, (
                    f"Missing --ac in task create command starting at line: {line}"
                )

    def test_multiline_input_uses_ansi_c_quoting(self, plan_command_path):
        """Verify multiline input examples use $'...' syntax."""
        content = plan_command_path.read_text()

        # Find plan and notes examples
        lines = content.split("\n")
        for line in lines:
            if "--plan" in line and "\\n" in line:
                # Should use $'...' for newlines
                assert "$'" in line, f"Plan command should use $'...' syntax: {line}"

    def test_agent_names_match_conventions(self, plan_command_path):
        """Verify agent assignee names follow conventions."""
        content = plan_command_path.read_text()

        # Should use @agent-name format
        assert "@software-architect" in content
        assert "@platform-engineer" in content
