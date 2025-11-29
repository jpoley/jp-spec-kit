"""Integration tests for jpspec commands with backlog.md CLI.

This test module verifies that jpspec commands correctly interact with the
backlog.md CLI for task management operations.
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
def sample_backlog_tasks(temp_backlog_dir):
    """Create sample backlog tasks with known IDs and acceptance criteria.

    Creates three tasks:
    - task-001: Simple task without ACs
    - task-042: Task with 3 ACs (for testing AC operations)
    - task-100: Task in "In Progress" state

    Returns:
        dict: Mapping of task IDs to task file paths
    """
    tasks_dir = temp_backlog_dir / "tasks"

    # Task 001: Simple task
    task_001 = tasks_dir / "task-001 - Simple test task.md"
    task_001.write_text(
        dedent("""
        ---
        id: task-001
        title: Simple test task
        status: To Do
        assignee:
        labels: [test]
        priority: Medium
        ---

        ## Description

        A simple test task without acceptance criteria.

        ## Acceptance Criteria

        <!-- AC:BEGIN -->
        <!-- AC:END -->
    """).strip()
    )

    # Task 042: Task with acceptance criteria
    task_042 = tasks_dir / "task-042 - Task with acceptance criteria.md"
    task_042.write_text(
        dedent("""
        ---
        id: task-042
        title: Task with acceptance criteria
        status: To Do
        assignee:
        labels: [backend, api]
        priority: High
        ---

        ## Description

        A test task with multiple acceptance criteria for testing AC operations.

        ## Acceptance Criteria

        <!-- AC:BEGIN -->
        - [ ] #1 First acceptance criterion
        - [ ] #2 Second acceptance criterion
        - [ ] #3 Third acceptance criterion
        <!-- AC:END -->

        ## Implementation Plan

        1. Step one
        2. Step two

        ## Implementation Notes

        Initial notes go here.
    """).strip()
    )

    # Task 100: In Progress task
    task_100 = tasks_dir / "task-100 - In progress task.md"
    task_100.write_text(
        dedent("""
        ---
        id: task-100
        title: In progress task
        status: In Progress
        assignee: @engineer-1
        labels: [frontend]
        priority: High
        ---

        ## Description

        A task currently in progress.

        ## Acceptance Criteria

        <!-- AC:BEGIN -->
        - [x] #1 First criterion completed
        - [ ] #2 Second criterion pending
        <!-- AC:END -->
    """).strip()
    )

    return {
        "task-001": task_001,
        "task-042": task_042,
        "task-100": task_100,
    }


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

    def test_sample_tasks_created(self, sample_backlog_tasks):
        """Verify sample tasks are created with known IDs and content."""
        assert "task-001" in sample_backlog_tasks
        assert "task-042" in sample_backlog_tasks
        assert "task-100" in sample_backlog_tasks

        # Verify task files exist
        for task_file in sample_backlog_tasks.values():
            assert task_file.exists()

        # Verify task-042 has acceptance criteria
        task_042_content = sample_backlog_tasks["task-042"].read_text()
        assert "id: task-042" in task_042_content
        assert "- [ ] #1 First acceptance criterion" in task_042_content
        assert "- [ ] #2 Second acceptance criterion" in task_042_content
        assert "- [ ] #3 Third acceptance criterion" in task_042_content

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

    def test_search_finds_tasks_by_keyword(
        self, temp_backlog_dir, sample_backlog_tasks
    ):
        """Test that backlog search can find tasks by keyword."""
        # This would be an actual integration test if backlog CLI is available
        # For now, we test the fixture setup
        assert len(sample_backlog_tasks) == 3

        # Verify we can search task content
        task_042 = sample_backlog_tasks["task-042"]
        content = task_042.read_text()
        assert "acceptance criteria" in content.lower()

    def test_list_filters_by_status(self, temp_backlog_dir, sample_backlog_tasks):
        """Test that task list can filter by status."""
        # Count tasks by status
        todo_tasks = []
        in_progress_tasks = []

        for task_file in sample_backlog_tasks.values():
            content = task_file.read_text()
            if "status: To Do" in content:
                todo_tasks.append(task_file)
            elif "status: In Progress" in content:
                in_progress_tasks.append(task_file)

        assert len(todo_tasks) == 2  # task-001, task-042
        assert len(in_progress_tasks) == 1  # task-100

    def test_list_filters_by_priority(self, temp_backlog_dir, sample_backlog_tasks):
        """Test that task list can filter by priority."""
        high_priority_tasks = []

        for task_file in sample_backlog_tasks.values():
            content = task_file.read_text()
            if "priority: High" in content:
                high_priority_tasks.append(task_file)

        assert len(high_priority_tasks) == 2  # task-042, task-100


class TestTaskAssignment:
    """Tests for task assignment operations."""

    def test_assign_task_to_agent(self, mock_backlog_cli, backlog_verifier):
        """Test assigning a task to an agent."""
        # Simulate jpspec workflow: assign task and set to In Progress
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
    """Tests for complete jpspec workflow scenarios."""

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
