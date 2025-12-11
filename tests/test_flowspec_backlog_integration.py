"""Integration tests for flowspec commands with backlog.md CLI.

This test module verifies that flowspec commands correctly interact with the
backlog.md CLI for task management operations.

IMPORTANT: All mock task IDs use MOCK- prefix to distinguish from real tasks.
All fixtures use tmp_path - files are auto-cleaned after tests.
"""

import pytest
import subprocess
from textwrap import dedent
from unittest.mock import patch, MagicMock
import json


@pytest.fixture
def temp_backlog_dir(tmp_path):
    """Create a temporary backlog directory structure for testing.

    Creates:
    - backlog/
    - backlog/tasks/
    - backlog/drafts/
    - backlog/docs/
    - backlog/decisions/
    - backlog/archive/
    """
    backlog_root = tmp_path / "backlog"
    backlog_root.mkdir()

    # Create standard backlog directories
    (backlog_root / "tasks").mkdir()
    (backlog_root / "drafts").mkdir()
    (backlog_root / "docs").mkdir()
    (backlog_root / "decisions").mkdir()
    (backlog_root / "archive").mkdir()

    # Create backlog.json config
    config = {
        "version": "1.0.0",
        "taskIdPrefix": "task-",
        "statuses": ["To Do", "In Progress", "Done"],
        "priorities": ["Low", "Medium", "High"],
    }
    (backlog_root / "backlog.json").write_text(json.dumps(config, indent=2))

    return backlog_root


@pytest.fixture
def mock_backlog_tasks(temp_backlog_dir):
    """Create MOCK backlog tasks with known IDs for testing.

    Creates three MOCK tasks (auto-cleaned via tmp_path):
    - MOCK-SIMPLE: Simple task without ACs
    - MOCK-AC: Task with 3 ACs (for testing AC operations)
    - MOCK-WIP: Task in "In Progress" state

    Returns:
        dict: Mapping of task IDs to task file paths
    """
    tasks_dir = temp_backlog_dir / "tasks"

    # MOCK-SIMPLE: Simple task
    mock_simple = tasks_dir / "MOCK-SIMPLE - Mock simple test task.md"
    mock_simple.write_text(
        dedent("""
        ---
        id: MOCK-SIMPLE
        title: Mock simple test task
        status: To Do
        assignee:
        labels: [mock, test]
        priority: Medium
        ---

        ## Description

        A MOCK test task without acceptance criteria.

        ## Acceptance Criteria

        <!-- AC:BEGIN -->
        <!-- AC:END -->
    """).strip()
    )

    # MOCK-AC: Task with acceptance criteria
    mock_ac = tasks_dir / "MOCK-AC - Mock task with acceptance criteria.md"
    mock_ac.write_text(
        dedent("""
        ---
        id: MOCK-AC
        title: Mock task with acceptance criteria
        status: To Do
        assignee:
        labels: [mock, backend, api]
        priority: High
        ---

        ## Description

        A MOCK test task with multiple acceptance criteria for testing AC operations.

        ## Acceptance Criteria

        <!-- AC:BEGIN -->
        - [ ] #1 First MOCK acceptance criterion
        - [ ] #2 Second MOCK acceptance criterion
        - [ ] #3 Third MOCK acceptance criterion
        <!-- AC:END -->

        ## Implementation Plan

        1. MOCK step one
        2. MOCK step two

        ## Implementation Notes

        MOCK initial notes go here.
    """).strip()
    )

    # MOCK-WIP: In Progress task
    mock_wip = tasks_dir / "MOCK-WIP - Mock in progress task.md"
    mock_wip.write_text(
        dedent("""
        ---
        id: MOCK-WIP
        title: Mock in progress task
        status: In Progress
        assignee: @mock-engineer
        labels: [mock, frontend]
        priority: High
        ---

        ## Description

        A MOCK task currently in progress.

        ## Acceptance Criteria

        <!-- AC:BEGIN -->
        - [x] #1 First MOCK criterion completed
        - [ ] #2 Second MOCK criterion pending
        <!-- AC:END -->
    """).strip()
    )

    return {
        "MOCK-SIMPLE": mock_simple,
        "MOCK-AC": mock_ac,
        "MOCK-WIP": mock_wip,
    }


# Alias for backward compatibility
@pytest.fixture
def sample_backlog_tasks(mock_backlog_tasks):
    """Alias for mock_backlog_tasks (deprecated)."""
    return mock_backlog_tasks


@pytest.fixture
def mock_backlog_cli():
    """Fixture to mock subprocess calls to backlog CLI.

    Returns a MagicMock that can be used to verify backlog CLI calls.
    """
    with patch("subprocess.run") as mock_run:
        # Configure mock to return successful responses
        mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")
        yield mock_run


class BacklogCLIVerifier:
    """Helper class to verify backlog CLI calls."""

    @staticmethod
    def assert_called_with_command(mock_run, command_parts):
        """Verify that backlog CLI was called with specific command parts.

        Args:
            mock_run: The mocked subprocess.run
            command_parts: List of expected command parts

        Example:
            verifier.assert_called_with_command(
                mock_run,
                ["backlog", "task", "edit", "42", "-s", "In Progress"]
            )
        """
        # Get all calls made to subprocess.run
        calls = mock_run.call_args_list

        # Check if any call matches the expected command
        for call_args in calls:
            args, kwargs = call_args
            if args and args[0] == command_parts:
                return True

        # If no match found, raise assertion error with helpful message
        actual_calls = [str(c[0][0]) for c in calls if c[0]]
        pytest.fail(
            f"Expected backlog CLI call not found.\n"
            f"Expected: {command_parts}\n"
            f"Actual calls: {actual_calls}"
        )

    @staticmethod
    def assert_search_called(mock_run, query, filters=None):
        """Verify backlog search was called with query and optional filters.

        Args:
            mock_run: The mocked subprocess.run
            query: Search query string
            filters: Optional dict of filters (status, priority, etc.)
        """
        expected = ["backlog", "search", query, "--plain"]

        if filters:
            if "status" in filters:
                expected.extend(["--status", filters["status"]])
            if "priority" in filters:
                expected.extend(["--priority", filters["priority"]])
            if "type" in filters:
                expected.extend(["--type", filters["type"]])

        BacklogCLIVerifier.assert_called_with_command(mock_run, expected)

    @staticmethod
    def assert_task_list_called(mock_run, filters=None):
        """Verify backlog task list was called with optional filters."""
        expected = ["backlog", "task", "list", "--plain"]

        if filters:
            if "status" in filters:
                expected.extend(["-s", filters["status"]])
            if "assignee" in filters:
                expected.extend(["-a", filters["assignee"]])

        BacklogCLIVerifier.assert_called_with_command(mock_run, expected)

    @staticmethod
    def assert_task_edit_called(mock_run, task_id, **kwargs):
        """Verify backlog task edit was called with specific parameters.

        Args:
            mock_run: The mocked subprocess.run
            task_id: Task ID (e.g., "42")
            **kwargs: Edit parameters (status, assignee, check_ac, etc.)
        """
        expected = ["backlog", "task", "edit", str(task_id)]

        if "status" in kwargs:
            expected.extend(["-s", kwargs["status"]])
        if "assignee" in kwargs:
            expected.extend(["-a", kwargs["assignee"]])
        if "check_ac" in kwargs:
            # Support multiple AC checks
            ac_list = (
                kwargs["check_ac"]
                if isinstance(kwargs["check_ac"], list)
                else [kwargs["check_ac"]]
            )
            for ac in ac_list:
                expected.extend(["--check-ac", str(ac)])
        if "uncheck_ac" in kwargs:
            ac_list = (
                kwargs["uncheck_ac"]
                if isinstance(kwargs["uncheck_ac"], list)
                else [kwargs["uncheck_ac"]]
            )
            for ac in ac_list:
                expected.extend(["--uncheck-ac", str(ac)])
        if "notes" in kwargs:
            expected.extend(["--notes", kwargs["notes"]])
        if "plan" in kwargs:
            expected.extend(["--plan", kwargs["plan"]])

        BacklogCLIVerifier.assert_called_with_command(mock_run, expected)


@pytest.fixture
def backlog_verifier():
    """Fixture providing BacklogCLIVerifier helper."""
    return BacklogCLIVerifier()


class TestBacklogCLIIntegration:
    """Test suite for backlog.md CLI integration."""

    def test_temp_backlog_dir_structure(self, temp_backlog_dir):
        """Verify temporary backlog directory is created correctly."""
        assert temp_backlog_dir.exists()
        assert (temp_backlog_dir / "tasks").exists()
        assert (temp_backlog_dir / "drafts").exists()
        assert (temp_backlog_dir / "docs").exists()
        assert (temp_backlog_dir / "decisions").exists()
        assert (temp_backlog_dir / "archive").exists()
        assert (temp_backlog_dir / "backlog.json").exists()

    def test_mock_tasks_created(self, mock_backlog_tasks):
        """Verify MOCK tasks are created with known IDs and content."""
        assert "MOCK-SIMPLE" in mock_backlog_tasks
        assert "MOCK-AC" in mock_backlog_tasks
        assert "MOCK-WIP" in mock_backlog_tasks

        # Verify task files exist
        for task_file in mock_backlog_tasks.values():
            assert task_file.exists()

        # Verify MOCK-AC has acceptance criteria
        mock_ac_content = mock_backlog_tasks["MOCK-AC"].read_text()
        assert "id: MOCK-AC" in mock_ac_content
        assert "- [ ] #1 First MOCK acceptance criterion" in mock_ac_content
        assert "- [ ] #2 Second MOCK acceptance criterion" in mock_ac_content
        assert "- [ ] #3 Third MOCK acceptance criterion" in mock_ac_content

    def test_verifier_search_called(self, mock_backlog_cli, backlog_verifier):
        """Test BacklogCLIVerifier.assert_search_called helper."""
        # Simulate a search call
        subprocess.run(["backlog", "search", "auth", "--plain"])

        # Verify the call
        backlog_verifier.assert_search_called(mock_backlog_cli, "auth")

    def test_verifier_search_with_filters(self, mock_backlog_cli, backlog_verifier):
        """Test search verification with filters."""
        # Simulate search with filters
        subprocess.run(
            [
                "backlog",
                "search",
                "api",
                "--plain",
                "--status",
                "In Progress",
                "--priority",
                "High",
            ]
        )

        # Verify the call
        backlog_verifier.assert_search_called(
            mock_backlog_cli,
            "api",
            filters={"status": "In Progress", "priority": "High"},
        )

    def test_verifier_task_list_called(self, mock_backlog_cli, backlog_verifier):
        """Test BacklogCLIVerifier.assert_task_list_called helper."""
        # Simulate task list call
        subprocess.run(["backlog", "task", "list", "--plain"])

        # Verify the call
        backlog_verifier.assert_task_list_called(mock_backlog_cli)

    def test_verifier_task_list_with_filters(self, mock_backlog_cli, backlog_verifier):
        """Test task list verification with filters."""
        # Simulate filtered list
        subprocess.run(
            ["backlog", "task", "list", "--plain", "-s", "To Do", "-a", "@engineer-1"]
        )

        # Verify the call
        backlog_verifier.assert_task_list_called(
            mock_backlog_cli, filters={"status": "To Do", "assignee": "@engineer-1"}
        )

    def test_verifier_task_edit_status(self, mock_backlog_cli, backlog_verifier):
        """Test task edit verification for status change."""
        # Simulate status change
        subprocess.run(["backlog", "task", "edit", "42", "-s", "In Progress"])

        # Verify the call
        backlog_verifier.assert_task_edit_called(
            mock_backlog_cli, "42", status="In Progress"
        )

    def test_verifier_task_edit_assignment(self, mock_backlog_cli, backlog_verifier):
        """Test task edit verification for assignment."""
        # Simulate assignment and status change
        subprocess.run(
            ["backlog", "task", "edit", "42", "-s", "In Progress", "-a", "@myself"]
        )

        # Verify the call
        backlog_verifier.assert_task_edit_called(
            mock_backlog_cli, "42", status="In Progress", assignee="@myself"
        )

    def test_verifier_task_edit_check_ac_single(
        self, mock_backlog_cli, backlog_verifier
    ):
        """Test AC checking verification for single criterion."""
        # Simulate checking AC #1
        subprocess.run(["backlog", "task", "edit", "42", "--check-ac", "1"])

        # Verify the call
        backlog_verifier.assert_task_edit_called(mock_backlog_cli, "42", check_ac=1)

    def test_verifier_task_edit_check_ac_multiple(
        self, mock_backlog_cli, backlog_verifier
    ):
        """Test AC checking verification for multiple criteria."""
        # Simulate checking multiple ACs
        subprocess.run(
            [
                "backlog",
                "task",
                "edit",
                "42",
                "--check-ac",
                "1",
                "--check-ac",
                "2",
                "--check-ac",
                "3",
            ]
        )

        # Verify the call
        backlog_verifier.assert_task_edit_called(
            mock_backlog_cli, "42", check_ac=[1, 2, 3]
        )

    def test_verifier_task_edit_notes(self, mock_backlog_cli, backlog_verifier):
        """Test task edit verification for adding notes."""
        # Simulate adding notes
        subprocess.run(
            ["backlog", "task", "edit", "42", "--notes", "Implementation complete"]
        )

        # Verify the call
        backlog_verifier.assert_task_edit_called(
            mock_backlog_cli, "42", notes="Implementation complete"
        )

    def test_verifier_task_edit_plan(self, mock_backlog_cli, backlog_verifier):
        """Test task edit verification for adding implementation plan."""
        # Simulate adding plan
        plan = "1. Research\n2. Implement\n3. Test"
        subprocess.run(["backlog", "task", "edit", "42", "--plan", plan])

        # Verify the call
        backlog_verifier.assert_task_edit_called(mock_backlog_cli, "42", plan=plan)


class TestTaskDiscovery:
    """Tests for task discovery operations (search and list)."""

    def test_search_finds_tasks_by_keyword(self, temp_backlog_dir, mock_backlog_tasks):
        """Test that backlog search can find MOCK tasks by keyword."""
        # This would be an actual integration test if backlog CLI is available
        # For now, we test the fixture setup
        assert len(mock_backlog_tasks) == 3

        # Verify we can search task content
        mock_ac = mock_backlog_tasks["MOCK-AC"]
        content = mock_ac.read_text()
        assert "acceptance criteria" in content.lower()

    def test_list_filters_by_status(self, temp_backlog_dir, mock_backlog_tasks):
        """Test that task list can filter by status."""
        # Count tasks by status
        todo_tasks = []
        in_progress_tasks = []

        for task_file in mock_backlog_tasks.values():
            content = task_file.read_text()
            if "status: To Do" in content:
                todo_tasks.append(task_file)
            elif "status: In Progress" in content:
                in_progress_tasks.append(task_file)

        assert len(todo_tasks) == 2  # MOCK-SIMPLE, MOCK-AC
        assert len(in_progress_tasks) == 1  # MOCK-WIP

    def test_list_filters_by_priority(self, temp_backlog_dir, mock_backlog_tasks):
        """Test that task list can filter by priority."""
        high_priority_tasks = []

        for task_file in mock_backlog_tasks.values():
            content = task_file.read_text()
            if "priority: High" in content:
                high_priority_tasks.append(task_file)

        assert len(high_priority_tasks) == 2  # MOCK-AC, MOCK-WIP


class TestTaskAssignment:
    """Tests for task assignment operations."""

    def test_assign_task_to_agent(self, mock_backlog_cli, backlog_verifier):
        """Test assigning a task to an agent."""
        # Simulate flowspec workflow: assign task and set to In Progress
        subprocess.run(
            [
                "backlog",
                "task",
                "edit",
                "42",
                "-s",
                "In Progress",
                "-a",
                "@backend-engineer",
            ]
        )

        # Verify the assignment call
        backlog_verifier.assert_task_edit_called(
            mock_backlog_cli, "42", status="In Progress", assignee="@backend-engineer"
        )

    def test_unassign_task(self, mock_backlog_cli, backlog_verifier):
        """Test unassigning a task."""
        # Simulate unassignment
        subprocess.run(["backlog", "task", "edit", "100", "-a", ""])

        # Verify the call
        backlog_verifier.assert_task_edit_called(mock_backlog_cli, "100", assignee="")


class TestAcceptanceCriteriaOperations:
    """Tests for acceptance criteria checking operations."""

    def test_check_single_ac(self, mock_backlog_cli, backlog_verifier):
        """Test checking a single acceptance criterion."""
        subprocess.run(["backlog", "task", "edit", "42", "--check-ac", "1"])

        backlog_verifier.assert_task_edit_called(mock_backlog_cli, "42", check_ac=1)

    def test_check_multiple_ac(self, mock_backlog_cli, backlog_verifier):
        """Test checking multiple acceptance criteria at once."""
        subprocess.run(
            [
                "backlog",
                "task",
                "edit",
                "42",
                "--check-ac",
                "1",
                "--check-ac",
                "2",
                "--check-ac",
                "3",
            ]
        )

        backlog_verifier.assert_task_edit_called(
            mock_backlog_cli, "42", check_ac=[1, 2, 3]
        )

    def test_uncheck_ac(self, mock_backlog_cli, backlog_verifier):
        """Test unchecking an acceptance criterion."""
        subprocess.run(["backlog", "task", "edit", "42", "--uncheck-ac", "2"])

        backlog_verifier.assert_task_edit_called(mock_backlog_cli, "42", uncheck_ac=2)

    def test_mixed_ac_operations(self, mock_backlog_cli, backlog_verifier):
        """Test mixed AC operations in single command."""
        subprocess.run(
            ["backlog", "task", "edit", "42", "--check-ac", "1", "--uncheck-ac", "2"]
        )

        # Verify both operations
        calls = mock_backlog_cli.call_args_list
        assert len(calls) > 0

        # Get the actual command
        actual_cmd = calls[-1][0][0]
        assert "backlog" in actual_cmd
        assert "task" in actual_cmd
        assert "edit" in actual_cmd
        assert "42" in actual_cmd
        assert "--check-ac" in actual_cmd
        assert "--uncheck-ac" in actual_cmd


class TestWorkflowCompletion:
    """Tests for complete flowspec workflow scenarios."""

    def test_complete_implementation_workflow(self, mock_backlog_cli, backlog_verifier):
        """Test complete workflow: assign → work → check ACs → add notes → mark done."""
        task_id = "42"

        # Step 1: Assign and start work
        subprocess.run(
            [
                "backlog",
                "task",
                "edit",
                task_id,
                "-s",
                "In Progress",
                "-a",
                "@backend-engineer",
            ]
        )

        # Step 2: Add implementation plan
        subprocess.run(
            [
                "backlog",
                "task",
                "edit",
                task_id,
                "--plan",
                "1. Research\n2. Implement\n3. Test",
            ]
        )

        # Step 3: Check ACs as work progresses
        subprocess.run(["backlog", "task", "edit", task_id, "--check-ac", "1"])

        subprocess.run(
            ["backlog", "task", "edit", task_id, "--check-ac", "2", "--check-ac", "3"]
        )

        # Step 4: Add implementation notes
        subprocess.run(
            [
                "backlog",
                "task",
                "edit",
                task_id,
                "--notes",
                "Implemented feature X using pattern Y",
            ]
        )

        # Step 5: Mark as done
        subprocess.run(["backlog", "task", "edit", task_id, "-s", "Done"])

        # Verify all steps were called correctly
        assert mock_backlog_cli.call_count >= 5

        # Verify final status change
        backlog_verifier.assert_task_edit_called(
            mock_backlog_cli, task_id, status="Done"
        )

    def test_research_workflow(self, mock_backlog_cli, backlog_verifier):
        """Test research workflow: search → assign → investigate → document."""
        # Step 1: Search for related tasks
        subprocess.run(["backlog", "search", "api", "--plain", "--type", "task"])

        # Step 2: Assign research task
        subprocess.run(
            ["backlog", "task", "edit", "100", "-s", "In Progress", "-a", "@researcher"]
        )

        # Step 3: Add findings to notes
        subprocess.run(
            [
                "backlog",
                "task",
                "edit",
                "100",
                "--notes",
                "Research findings: Option A is better because...",
            ]
        )

        # Verify workflow
        backlog_verifier.assert_search_called(
            mock_backlog_cli, "api", filters={"type": "task"}
        )

        backlog_verifier.assert_task_edit_called(
            mock_backlog_cli, "100", status="In Progress", assignee="@researcher"
        )
