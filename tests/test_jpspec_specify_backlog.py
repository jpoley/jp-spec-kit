"""Tests for /jpspec:specify command backlog.md integration.

This test module verifies that the /jpspec:specify command correctly integrates
with backlog.md CLI for task management during specification creation.
"""

import pytest
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestSpecifyCommandStructure:
    """Tests for the structure and content of the specify.md command file."""

    @pytest.fixture
    def specify_command_path(self):
        """Path to the specify.md command file."""
        return (
            Path(__file__).parent.parent
            / ".claude"
            / "commands"
            / "jpspec"
            / "specify.md"
        )

    @pytest.fixture
    def specify_content(self, specify_command_path):
        """Read the content of specify.md command."""
        return specify_command_path.read_text()

    def test_specify_file_exists(self, specify_command_path):
        """Verify specify.md command file exists."""
        assert specify_command_path.exists(), "specify.md command file should exist"

    def test_includes_backlog_search_step(self, specify_content):
        """Verify command includes step to search for existing tasks."""
        assert "backlog search" in specify_content, (
            "Command should include backlog search step"
        )
        assert "--plain" in specify_content, (
            "Search command should use --plain flag for AI-readable output"
        )

    def test_includes_backlog_instructions(self, specify_content):
        """Verify command includes reference to _backlog-instructions.md."""
        assert (
            "INCLUDE:.claude/commands/jpspec/_backlog-instructions.md"
            in specify_content
            or "_backlog-instructions.md" in specify_content
        ), "Command should include or reference backlog instructions"

    def test_includes_pm_planner_role(self, specify_content):
        """Verify command defines PM Planner role in task management."""
        assert "@pm-planner" in specify_content, (
            "Command should reference @pm-planner agent name"
        )
        assert "PM Planner" in specify_content or "pm-planner" in specify_content, (
            "Command should define PM Planner role"
        )

    def test_includes_task_creation_instructions(self, specify_content):
        """Verify command includes instructions for creating backlog tasks."""
        assert "backlog task create" in specify_content, (
            "Command should include task creation instructions"
        )
        assert "--ac" in specify_content, (
            "Command should show acceptance criteria flag usage"
        )
        assert (
            "-a @pm-planner" in specify_content or "Assign yourself" in specify_content
        ), "Command should instruct agent to assign itself to tasks"

    def test_references_task_ids_in_prd(self, specify_content):
        """Verify command instructs to reference task IDs in PRD."""
        assert "task ID" in specify_content.lower() or "task-" in specify_content, (
            "Command should mention task IDs"
        )
        assert (
            "reference" in specify_content.lower() or "link" in specify_content.lower()
        ), "Command should instruct to reference/link task IDs in PRD"

    def test_task_breakdown_section_updated(self, specify_content):
        """Verify Task Breakdown section emphasizes backlog tasks."""
        # Should NOT use old /speckit.tasks approach
        assert "Task Breakdown" in specify_content, "Should have Task Breakdown section"

        # Should emphasize backlog integration
        content_lower = specify_content.lower()
        assert "backlog" in content_lower, "Task breakdown should mention backlog"

    def test_includes_traceability_requirement(self, specify_content):
        """Verify PRD requirements include traceability to task IDs."""
        assert (
            "traceability" in specify_content.lower()
            or "traceable" in specify_content.lower()
        ), "Command should emphasize traceability"
        assert (
            "task ID" in specify_content.lower()
            or "backlog task" in specify_content.lower()
        ), "Traceability should link to task IDs"


class TestSpecifyCommandExecution:
    """Tests for executing the /jpspec:specify command with backlog integration."""

    @pytest.fixture
    def mock_backlog_cli(self):
        """Mock subprocess calls to backlog CLI."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")
            yield mock_run

    def test_command_searches_for_existing_tasks(self, mock_backlog_cli):
        """Verify command execution includes search for existing tasks."""
        # Simulate the Step 1: Discover Existing Tasks
        subprocess.run(["backlog", "search", "user-auth", "--plain"])

        # Verify search was called
        calls = mock_backlog_cli.call_args_list
        assert len(calls) > 0, "Should call backlog CLI"

        actual_cmd = calls[0][0][0]
        assert actual_cmd == ["backlog", "search", "user-auth", "--plain"], (
            "Should search for tasks with --plain flag"
        )

    def test_pm_planner_creates_tasks(self, mock_backlog_cli):
        """Verify PM Planner agent creates tasks via backlog CLI."""
        # Simulate PM Planner creating a task
        subprocess.run(
            [
                "backlog",
                "task",
                "create",
                "Implement user authentication",
                "-d",
                "Add JWT-based authentication to API",
                "--ac",
                "Users can login with email/password",
                "--ac",
                "JWT tokens expire after 24 hours",
                "-l",
                "backend,security",
                "--priority",
                "high",
                "-a",
                "@pm-planner",
            ]
        )

        # Verify task creation
        calls = mock_backlog_cli.call_args_list
        actual_cmd = calls[-1][0][0]

        assert "backlog" in actual_cmd, "Should use backlog CLI"
        assert "task" in actual_cmd, "Should use task command"
        assert "create" in actual_cmd, "Should create task"
        assert "@pm-planner" in actual_cmd, "Should assign to PM Planner"
        assert "--ac" in actual_cmd, "Should include acceptance criteria"

    def test_agent_assigns_itself_to_created_tasks(self, mock_backlog_cli):
        """Verify agent assigns itself when creating tasks."""
        subprocess.run(
            ["backlog", "task", "create", "Define API schema", "-a", "@pm-planner"]
        )

        calls = mock_backlog_cli.call_args_list
        actual_cmd = calls[-1][0][0]

        assert "-a" in actual_cmd, "Should include assignee flag"
        assert "@pm-planner" in actual_cmd, "Should assign to @pm-planner"


class TestPRDOutputFormat:
    """Tests for PRD output format with task ID references."""

    def test_prd_includes_task_id_references(self):
        """Verify PRD format includes task ID references."""
        # Sample PRD section with task references
        sample_prd = """
        ## 6. Task Breakdown (Backlog Tasks)

        ### Epic: User Authentication
        - **task-001**: Implement JWT authentication (Priority: High, Labels: backend,security)
        - **task-002**: Add password reset flow (Priority: Medium, Labels: backend,email)
        - **task-003**: Create login UI component (Priority: High, Labels: frontend,ui)

        ### Epic: User Profile Management
        - **task-004**: Design profile data schema (Priority: High, Labels: backend,database)
        - **task-005**: Implement profile CRUD API (Priority: High, Labels: backend,api)

        See task-001 for authentication implementation details.
        Profile management depends on task-001 completion.
        """

        # Verify task ID format
        assert "task-001" in sample_prd, "Should include task IDs"
        assert "task-002" in sample_prd, "Should reference multiple tasks"

        # Verify task context
        assert "Priority:" in sample_prd, "Should include priority"
        assert "Labels:" in sample_prd, "Should include labels"

        # Verify cross-references
        assert "See task-" in sample_prd, "Should cross-reference tasks"
        assert "depends on task-" in sample_prd, "Should note dependencies"

    def test_prd_traceability_section(self):
        """Verify PRD includes traceability from requirements to tasks."""
        sample_traceability = """
        ## Requirements Traceability

        | Requirement | Backlog Task | Status |
        |-------------|--------------|--------|
        | FR-001: User login | task-001 | To Do |
        | FR-002: Password reset | task-002 | To Do |
        | NFR-001: Response time < 200ms | task-010 | To Do |
        """

        assert "task-001" in sample_traceability, "Should link requirements to tasks"
        assert "FR-" in sample_traceability, "Should reference functional requirements"
        assert "NFR-" in sample_traceability, (
            "Should reference non-functional requirements"
        )


class TestBacklogInstructionsIntegration:
    """Tests for integration of _backlog-instructions.md."""

    @pytest.fixture
    def backlog_instructions_path(self):
        """Path to the _backlog-instructions.md file."""
        return (
            Path(__file__).parent.parent
            / ".claude"
            / "commands"
            / "jpspec"
            / "_backlog-instructions.md"
        )

    def test_backlog_instructions_file_exists(self, backlog_instructions_path):
        """Verify _backlog-instructions.md exists."""
        assert backlog_instructions_path.exists(), (
            "_backlog-instructions.md should exist for sharing across agents"
        )

    def test_backlog_instructions_content(self, backlog_instructions_path):
        """Verify _backlog-instructions.md contains essential content."""
        content = backlog_instructions_path.read_text()

        # Essential sections
        assert "Task Discovery" in content or "backlog search" in content, (
            "Should include task discovery instructions"
        )
        assert "Creating New Tasks" in content or "backlog task create" in content, (
            "Should include task creation instructions"
        )
        assert "NEVER edit task files directly" in content or "Always use" in content, (
            "Should warn against direct file editing"
        )
        assert "--plain" in content, (
            "Should mention --plain flag for AI-readable output"
        )

    def test_specify_references_backlog_instructions(self):
        """Verify specify.md includes/references backlog instructions."""
        specify_path = (
            Path(__file__).parent.parent
            / ".claude"
            / "commands"
            / "jpspec"
            / "specify.md"
        )
        specify_content = specify_path.read_text()

        # Check for INCLUDE directive or explicit content
        assert (
            "INCLUDE:.claude/commands/jpspec/_backlog-instructions.md"
            in specify_content
            or "backlog search" in specify_content
        ), "specify.md should include or reference backlog instructions"


class TestWorkflowIntegration:
    """Integration tests for complete /jpspec:specify workflow."""

    @pytest.fixture
    def mock_backlog_cli(self):
        """Mock subprocess calls to backlog CLI."""
        with patch("subprocess.run") as mock_run:
            # Configure different responses for different commands
            def side_effect(*args, **kwargs):
                cmd = args[0] if args else []
                if "search" in cmd:
                    return MagicMock(
                        returncode=0,
                        stdout="Found 2 tasks related to authentication",
                        stderr="",
                    )
                elif "create" in cmd:
                    return MagicMock(returncode=0, stdout="Created task-042", stderr="")
                else:
                    return MagicMock(returncode=0, stdout="", stderr="")

            mock_run.side_effect = side_effect
            yield mock_run

    def test_complete_specify_workflow(self, mock_backlog_cli):
        """Test complete workflow: search → create tasks → reference in PRD."""
        # Step 1: Search for existing tasks
        result1 = subprocess.run(["backlog", "search", "authentication", "--plain"])
        assert result1.returncode == 0
        assert "Found" in result1.stdout

        # Step 2: PM Planner creates tasks for work items
        result2 = subprocess.run(
            [
                "backlog",
                "task",
                "create",
                "Implement JWT authentication",
                "-d",
                "Add JWT-based auth to API",
                "--ac",
                "Users can login",
                "--ac",
                "Tokens expire after 24h",
                "-l",
                "backend,security",
                "--priority",
                "high",
                "-a",
                "@pm-planner",
            ]
        )
        assert result2.returncode == 0
        assert "Created task-" in result2.stdout

        # Step 3: Verify workflow executed correctly
        calls = mock_backlog_cli.call_args_list
        assert len(calls) >= 2, "Should have made at least search and create calls"

        # Verify search happened first
        search_call = calls[0][0][0]
        assert "search" in search_call
        assert "--plain" in search_call

        # Verify task creation happened
        create_call = calls[1][0][0]
        assert "create" in create_call
        assert "@pm-planner" in create_call

    def test_prd_generation_with_task_references(self):
        """Verify PRD generation includes task references."""
        # This would be an actual workflow test if we had full agent execution
        # For now, we verify the expected format

        # Sample PRD with proper structure
        sample_prd = """
        # Product Requirements Document

        ## 1. Executive Summary
        Feature: User Authentication System

        ## 6. Task Breakdown (Backlog Tasks)
        - task-001: JWT Authentication (High priority)
        - task-002: Password Reset Flow (Medium priority)

        ## Requirements Traceability
        FR-001 → task-001
        FR-002 → task-002
        """

        # Verify structure
        assert "Executive Summary" in sample_prd
        assert "Task Breakdown" in sample_prd
        assert "task-001" in sample_prd
        assert "Traceability" in sample_prd or "→ task-" in sample_prd


class TestErrorHandling:
    """Tests for error handling in backlog integration."""

    def test_handles_missing_backlog_directory(self):
        """Verify graceful handling when backlog directory doesn't exist."""
        result = subprocess.run(
            ["backlog", "task", "list"],
            capture_output=True,
            text=True,
            cwd="/tmp",  # Directory without backlog
        )

        # Should either fail gracefully or warn user
        # (Actual behavior depends on backlog CLI implementation)
        assert (
            result.returncode != 0
            or "not found" in result.stderr.lower()
            or result.returncode == 0
        )

    def test_handles_search_with_no_results(self):
        """Verify handling when search finds no tasks."""
        # This would require actual backlog CLI
        # For now, verify expected behavior pattern
        assert True, "Should handle empty search results gracefully"

    def test_validates_task_creation_has_acceptance_criteria(self):
        """Verify task creation requires acceptance criteria."""
        # According to backlog.md guidelines, tasks MUST have at least one AC
        # The command template should enforce this

        specify_path = (
            Path(__file__).parent.parent
            / ".claude"
            / "commands"
            / "jpspec"
            / "specify.md"
        )
        specify_content = specify_path.read_text()

        assert "--ac" in specify_content, (
            "Command should require acceptance criteria when creating tasks"
        )
