"""Tests for backlog CLI shim with automatic event emission.

This module tests the shim wrapper functions that call backlog CLI
and automatically emit flowspec events for task lifecycle operations.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from specify_cli.backlog.shim import (
    ShimResult,
    _extract_task_id_from_create_output,
    _run_backlog_command,
    check_acceptance_criteria,
    complete_task,
    start_task,
    task_archive,
    task_create,
    task_edit,
    task_list,
    task_search,
    task_view,
)


@pytest.fixture
def workspace_root(tmp_path: Path) -> Path:
    """Create temporary workspace root."""
    workspace = tmp_path / "project"
    workspace.mkdir()
    # Create hooks directory structure
    hooks_dir = workspace / ".specify" / "hooks"
    hooks_dir.mkdir(parents=True)
    # Create empty hooks.yaml
    hooks_file = hooks_dir / "hooks.yaml"
    hooks_file.write_text("version: '1.0'\nhooks: []\n")
    return workspace


class TestShimResult:
    """Test ShimResult dataclass."""

    def test_shim_result_defaults(self):
        """Test ShimResult default values."""
        result = ShimResult(
            success=True,
            exit_code=0,
            output="output",
            stderr="",
        )
        assert result.success is True
        assert result.exit_code == 0
        assert result.output == "output"
        assert result.stderr == ""
        assert result.task_id is None
        assert result.event_emitted is False
        assert result.events_emitted == []
        assert result.error is None
        assert result.metadata == {}

    def test_shim_result_with_event(self):
        """Test ShimResult with event emission."""
        result = ShimResult(
            success=True,
            exit_code=0,
            output="Created task task-123",
            stderr="",
            task_id="task-123",
            event_emitted=True,
            events_emitted=["task.created"],
        )
        assert result.task_id == "task-123"
        assert result.event_emitted is True
        assert result.events_emitted == ["task.created"]


class TestExtractTaskId:
    """Test task ID extraction from output."""

    def test_extract_simple_task_id(self):
        """Test extracting simple task ID."""
        output = "Created task task-123"
        assert _extract_task_id_from_create_output(output) == "task-123"

    def test_extract_subtask_id(self):
        """Test extracting subtask ID (with dots)."""
        output = "Created task task-123.01"
        assert _extract_task_id_from_create_output(output) == "task-123.01"

    def test_extract_deeply_nested_subtask(self):
        """Test extracting deeply nested subtask ID."""
        output = "Created task task-123.01.02"
        assert _extract_task_id_from_create_output(output) == "task-123.01.02"

    def test_extract_case_insensitive(self):
        """Test case insensitive extraction."""
        output = "CREATED TASK task-456"
        assert _extract_task_id_from_create_output(output) == "task-456"

    def test_no_match_returns_none(self):
        """Test no match returns None."""
        output = "Task creation failed"
        assert _extract_task_id_from_create_output(output) is None

    def test_multiline_output(self):
        """Test extraction from multiline output."""
        output = """
        Processing...
        Created task task-789
        Done!
        """
        assert _extract_task_id_from_create_output(output) == "task-789"


class TestRunBacklogCommand:
    """Test _run_backlog_command helper."""

    @patch("subprocess.run")
    def test_successful_command(self, mock_run):
        """Test successful backlog command execution."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Success",
            stderr="",
        )

        exit_code, stdout, stderr = _run_backlog_command(["task", "list"])

        assert exit_code == 0
        assert stdout == "Success"
        assert stderr == ""
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_failed_command(self, mock_run):
        """Test failed backlog command execution."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Error: task not found",
        )

        exit_code, stdout, stderr = _run_backlog_command(
            ["task", "view", "nonexistent"]
        )

        assert exit_code == 1
        assert stderr == "Error: task not found"

    @patch("subprocess.run")
    def test_command_timeout(self, mock_run):
        """Test command timeout handling."""
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired(cmd="backlog", timeout=30)

        exit_code, stdout, stderr = _run_backlog_command(["task", "list"])

        assert exit_code == -1
        assert "timed out" in stderr.lower()

    @patch("subprocess.run")
    def test_backlog_not_found(self, mock_run):
        """Test backlog CLI not found."""
        mock_run.side_effect = FileNotFoundError()

        exit_code, stdout, stderr = _run_backlog_command(["task", "list"])

        assert exit_code == -1
        assert "not found" in stderr.lower()


class TestTaskCreate:
    """Test task_create function."""

    @patch("specify_cli.backlog.shim._emit_event")
    @patch("specify_cli.backlog.shim._run_backlog_command")
    def test_create_task_success(self, mock_run, mock_emit, workspace_root: Path):
        """Test successful task creation with event emission."""
        mock_run.return_value = (0, "Created task task-100", "")
        mock_emit.return_value = True

        result = task_create(
            title="Test task",
            priority="high",
            workspace_root=workspace_root,
        )

        assert result.success is True
        assert result.task_id == "task-100"
        assert result.event_emitted is True
        assert result.events_emitted == ["task.created"]

        # Verify backlog command called correctly
        call_args = mock_run.call_args[0][0]
        assert "task" in call_args
        assert "create" in call_args
        assert "Test task" in call_args
        assert "--priority" in call_args
        assert "high" in call_args

        # Verify event emitted
        mock_emit.assert_called_once()

    @patch("specify_cli.backlog.shim._run_backlog_command")
    def test_create_task_failure(self, mock_run, workspace_root: Path):
        """Test task creation failure."""
        mock_run.return_value = (1, "", "Error: invalid priority")

        result = task_create(
            title="Test task",
            priority="invalid",
            workspace_root=workspace_root,
        )

        assert result.success is False
        assert result.exit_code == 1
        assert result.error is not None
        assert result.event_emitted is False

    @patch("specify_cli.backlog.shim._emit_event")
    @patch("specify_cli.backlog.shim._run_backlog_command")
    def test_create_task_with_labels(self, mock_run, mock_emit, workspace_root: Path):
        """Test task creation with labels."""
        mock_run.return_value = (0, "Created task task-101", "")
        mock_emit.return_value = True

        result = task_create(
            title="Backend feature",
            labels=["backend", "feature"],
            workspace_root=workspace_root,
        )

        assert result.success is True
        call_args = mock_run.call_args[0][0]
        assert call_args.count("--label") == 2
        assert "backend" in call_args
        assert "feature" in call_args

    @patch("specify_cli.backlog.shim._emit_event")
    @patch("specify_cli.backlog.shim._run_backlog_command")
    def test_create_task_with_acceptance_criteria(
        self, mock_run, mock_emit, workspace_root: Path
    ):
        """Test task creation with acceptance criteria."""
        mock_run.return_value = (0, "Created task task-102", "")
        mock_emit.return_value = True

        result = task_create(
            title="Feature with ACs",
            acceptance_criteria=["AC 1", "AC 2"],
            workspace_root=workspace_root,
        )

        assert result.success is True
        call_args = mock_run.call_args[0][0]
        assert call_args.count("--ac") == 2


class TestTaskEdit:
    """Test task_edit function."""

    @patch("specify_cli.backlog.shim._emit_event")
    @patch("specify_cli.backlog.shim._run_backlog_command")
    def test_edit_status_to_done(self, mock_run, mock_emit, workspace_root: Path):
        """Test editing task status to Done emits task.completed."""
        mock_run.return_value = (0, "Task updated", "")
        mock_emit.return_value = True

        result = task_edit(
            task_id="task-123",
            status="Done",
            workspace_root=workspace_root,
        )

        assert result.success is True
        assert result.event_emitted is True
        assert result.events_emitted == ["task.completed"]

        # Verify event type passed to emit
        call_args = mock_emit.call_args
        assert call_args[1]["event_type"] == "task.completed"

    @patch("specify_cli.backlog.shim._emit_event")
    @patch("specify_cli.backlog.shim._run_backlog_command")
    def test_edit_status_to_in_progress(
        self, mock_run, mock_emit, workspace_root: Path
    ):
        """Test editing task status to In Progress emits task.status_changed."""
        mock_run.return_value = (0, "Task updated", "")
        mock_emit.return_value = True

        result = task_edit(
            task_id="task-123",
            status="In Progress",
            workspace_root=workspace_root,
        )

        assert result.success is True
        assert result.event_emitted is True
        assert result.events_emitted == ["task.status_changed"]

    @patch("specify_cli.backlog.shim._emit_event")
    @patch("specify_cli.backlog.shim._run_backlog_command")
    def test_edit_check_acceptance_criteria(
        self, mock_run, mock_emit, workspace_root: Path
    ):
        """Test checking acceptance criteria emits task.ac_checked."""
        mock_run.return_value = (0, "Task updated", "")
        mock_emit.return_value = True

        result = task_edit(
            task_id="task-123",
            check_ac=[1, 2],
            workspace_root=workspace_root,
        )

        assert result.success is True
        assert result.event_emitted is True
        assert result.events_emitted == ["task.ac_checked"]

        # Verify command includes check-ac flags
        call_args = mock_run.call_args[0][0]
        assert call_args.count("--check-ac") == 2

    @patch("specify_cli.backlog.shim._emit_event")
    @patch("specify_cli.backlog.shim._run_backlog_command")
    def test_edit_uncheck_acceptance_criteria(
        self, mock_run, mock_emit, workspace_root: Path
    ):
        """Test unchecking acceptance criteria emits task.ac_checked."""
        mock_run.return_value = (0, "Task updated", "")
        mock_emit.return_value = True

        result = task_edit(
            task_id="task-123",
            uncheck_ac=[1],
            workspace_root=workspace_root,
        )

        assert result.success is True
        assert result.event_emitted is True
        assert "task.ac_checked" in result.events_emitted

    @patch("specify_cli.backlog.shim._emit_event")
    @patch("specify_cli.backlog.shim._run_backlog_command")
    def test_edit_status_and_ac_emits_multiple_events(
        self, mock_run, mock_emit, workspace_root: Path
    ):
        """Test editing both status and AC emits multiple events."""
        mock_run.return_value = (0, "Task updated", "")
        mock_emit.return_value = True

        result = task_edit(
            task_id="task-123",
            status="Done",
            check_ac=[1],
            workspace_root=workspace_root,
        )

        assert result.success is True
        assert result.event_emitted is True
        # Should contain both event types
        assert "task.completed" in result.events_emitted
        assert "task.ac_checked" in result.events_emitted

    @patch("specify_cli.backlog.shim._run_backlog_command")
    def test_edit_failure(self, mock_run, workspace_root: Path):
        """Test edit failure."""
        mock_run.return_value = (1, "", "Error: task not found")

        result = task_edit(
            task_id="nonexistent",
            status="Done",
            workspace_root=workspace_root,
        )

        assert result.success is False
        assert result.event_emitted is False


class TestTaskView:
    """Test task_view function."""

    @patch("specify_cli.backlog.shim._run_backlog_command")
    def test_view_task(self, mock_run):
        """Test viewing a task (read-only, no event)."""
        mock_run.return_value = (0, "Task details...", "")

        result = task_view("task-123")

        assert result.success is True
        assert result.task_id == "task-123"
        assert result.event_emitted is False  # Read-only, no event

    @patch("specify_cli.backlog.shim._run_backlog_command")
    def test_view_task_plain(self, mock_run):
        """Test viewing task with plain flag."""
        mock_run.return_value = (0, "Task details...", "")

        task_view("task-123", plain=True)

        call_args = mock_run.call_args[0][0]
        assert "--plain" in call_args


class TestTaskList:
    """Test task_list function."""

    @patch("specify_cli.backlog.shim._run_backlog_command")
    def test_list_tasks(self, mock_run):
        """Test listing tasks (read-only, no event)."""
        mock_run.return_value = (0, "task-1, task-2, task-3", "")

        result = task_list()

        assert result.success is True
        assert result.event_emitted is False  # Read-only, no event

    @patch("specify_cli.backlog.shim._run_backlog_command")
    def test_list_tasks_with_filters(self, mock_run):
        """Test listing tasks with filters."""
        mock_run.return_value = (0, "task-1", "")

        task_list(status="To Do", labels=["backend"])

        call_args = mock_run.call_args[0][0]
        assert "-s" in call_args
        assert "To Do" in call_args
        assert "-l" in call_args
        assert "backend" in call_args


class TestTaskSearch:
    """Test task_search function."""

    @patch("specify_cli.backlog.shim._run_backlog_command")
    def test_search_tasks(self, mock_run):
        """Test searching tasks (read-only, no event)."""
        mock_run.return_value = (0, "task-1: matching task", "")

        result = task_search("authentication")

        assert result.success is True
        assert result.event_emitted is False  # Read-only, no event


class TestTaskArchive:
    """Test task_archive function."""

    @patch("specify_cli.backlog.shim._emit_event")
    @patch("specify_cli.backlog.shim._run_backlog_command")
    def test_archive_task(self, mock_run, mock_emit, workspace_root: Path):
        """Test archiving task emits task.archived."""
        mock_run.return_value = (0, "Task archived", "")
        mock_emit.return_value = True

        result = task_archive("task-123", workspace_root=workspace_root)

        assert result.success is True
        assert result.event_emitted is True
        assert result.events_emitted == ["task.archived"]


class TestConvenienceWrappers:
    """Test convenience wrapper functions."""

    @patch("specify_cli.backlog.shim._emit_event")
    @patch("specify_cli.backlog.shim._run_backlog_command")
    def test_complete_task(self, mock_run, mock_emit, workspace_root: Path):
        """Test complete_task convenience wrapper."""
        mock_run.return_value = (0, "Task updated", "")
        mock_emit.return_value = True

        result = complete_task("task-123", workspace_root=workspace_root)

        assert result.success is True
        assert result.events_emitted == ["task.completed"]

        # Verify status was set to Done
        call_args = mock_run.call_args[0][0]
        assert "-s" in call_args
        assert "Done" in call_args

    @patch("specify_cli.backlog.shim._emit_event")
    @patch("specify_cli.backlog.shim._run_backlog_command")
    def test_start_task(self, mock_run, mock_emit, workspace_root: Path):
        """Test start_task convenience wrapper."""
        mock_run.return_value = (0, "Task updated", "")
        mock_emit.return_value = True

        result = start_task(
            "task-123",
            assignees=["@backend-engineer"],
            workspace_root=workspace_root,
        )

        assert result.success is True
        assert result.events_emitted == ["task.status_changed"]

        # Verify status was set to In Progress
        call_args = mock_run.call_args[0][0]
        assert "-s" in call_args
        assert "In Progress" in call_args
        assert "-a" in call_args
        assert "@backend-engineer" in call_args

    @patch("specify_cli.backlog.shim._emit_event")
    @patch("specify_cli.backlog.shim._run_backlog_command")
    def test_check_acceptance_criteria(self, mock_run, mock_emit, workspace_root: Path):
        """Test check_acceptance_criteria convenience wrapper."""
        mock_run.return_value = (0, "Task updated", "")
        mock_emit.return_value = True

        result = check_acceptance_criteria(
            "task-123",
            criteria_indices=[1, 2, 3],
            workspace_root=workspace_root,
        )

        assert result.success is True
        assert result.events_emitted == ["task.ac_checked"]

        # Verify check-ac flags
        call_args = mock_run.call_args[0][0]
        assert call_args.count("--check-ac") == 3


class TestEventEmissionFailure:
    """Test graceful handling of event emission failures."""

    @patch("specify_cli.backlog.shim._emit_event")
    @patch("specify_cli.backlog.shim._run_backlog_command")
    def test_event_emission_failure_doesnt_fail_operation(
        self, mock_run, mock_emit, workspace_root: Path
    ):
        """Test that event emission failure doesn't fail the operation."""
        mock_run.return_value = (0, "Created task task-123", "")
        mock_emit.return_value = False  # Event emission fails

        result = task_create(
            title="Test task",
            workspace_root=workspace_root,
        )

        # Operation should still succeed
        assert result.success is True
        assert result.task_id == "task-123"
        # But event was not emitted
        assert result.event_emitted is False


class TestBacklogModuleImports:
    """Test that shim functions are properly exported from backlog module."""

    def test_import_from_backlog_module(self):
        """Test importing shim functions from backlog module."""
        from specify_cli.backlog import (
            ShimResult,
            check_acceptance_criteria,
            complete_task,
            create_task,
            edit_task,
            start_task,
            task_archive,
            task_create,
            task_edit,
            task_list,
            task_search,
            task_view,
        )

        # All should be importable
        assert ShimResult is not None
        assert task_create is not None
        assert task_edit is not None
        assert task_view is not None
        assert task_list is not None
        assert task_search is not None
        assert task_archive is not None
        assert create_task is not None
        assert edit_task is not None
        assert complete_task is not None
        assert start_task is not None
        assert check_acceptance_criteria is not None
