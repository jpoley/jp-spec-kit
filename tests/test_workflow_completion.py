"""Unit tests for workflow completion handler."""

from __future__ import annotations

import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from specify_cli.workflow.completion import (
    TaskCompletionError,
    TaskCompletionHandler,
    TaskCompletionReport,
)


@pytest.fixture
def task_id():
    """Sample task ID for testing."""
    return "task-123"


@pytest.fixture
def mock_task_data_complete():
    """Mock task data with all ACs checked."""
    return {
        "id": "task-123",
        "title": "Test Task",
        "status": "In Progress",
        "acceptanceCriteria": [
            {"text": "AC 1", "checked": True},
            {"text": "AC 2", "checked": True},
            {"text": "AC 3", "checked": True},
        ],
    }


@pytest.fixture
def mock_task_data_incomplete():
    """Mock task data with some ACs unchecked."""
    return {
        "id": "task-123",
        "title": "Test Task",
        "status": "In Progress",
        "acceptanceCriteria": [
            {"text": "AC 1", "checked": True},
            {"text": "AC 2", "checked": False},
            {"text": "AC 3", "checked": True},
        ],
    }


@pytest.fixture
def mock_task_data_done():
    """Mock task data that is already Done."""
    return {
        "id": "task-123",
        "title": "Test Task",
        "status": "Done",
        "acceptanceCriteria": [
            {"text": "AC 1", "checked": True},
            {"text": "AC 2", "checked": True},
        ],
    }


@pytest.fixture
def mock_task_data_no_acs():
    """Mock task data with no acceptance criteria."""
    return {
        "id": "task-123",
        "title": "Test Task",
        "status": "In Progress",
        "acceptanceCriteria": [],
    }


class TestTaskCompletionHandler:
    """Test suite for TaskCompletionHandler."""

    def test_init(self, task_id):
        """Test handler initialization."""
        handler = TaskCompletionHandler(task_id)
        assert handler.task_id == task_id
        assert handler._command_log == []

    @patch("specify_cli.workflow.completion.subprocess.run")
    def test_complete_success(self, mock_run, task_id, mock_task_data_complete):
        """Test successful task completion with all ACs checked."""
        # Mock subprocess calls
        mock_run.side_effect = [
            # First call: get task data
            MagicMock(
                returncode=0,
                stdout=json.dumps(mock_task_data_complete),
                stderr="",
            ),
            # Second call: add notes
            MagicMock(returncode=0, stdout="Notes added", stderr=""),
            # Third call: update status
            MagicMock(returncode=0, stdout="Status updated", stderr=""),
        ]

        handler = TaskCompletionHandler(task_id)
        report = handler.complete(
            implementation_summary="Implemented feature X",
            test_summary="All tests passing",
            key_decisions="Used approach Y",
        )

        # Verify report
        assert isinstance(report, TaskCompletionReport)
        assert report.task_id == task_id
        assert isinstance(report.completion_timestamp, datetime)
        assert report.ac_summary["all_complete"] is True
        assert report.ac_summary["total_acs"] == 3
        assert report.ac_summary["checked_acs"] == 3
        assert report.ac_summary["unchecked_acs"] == []

        # Verify subprocess calls
        assert mock_run.call_count == 3

        # Verify command log
        log = handler.get_command_log()
        assert len(log) == 3
        assert log[0][0] == ["backlog", "task", task_id, "--plain"]
        # Second command is notes - check first 5 elements (notes content is element 5)
        assert log[1][0][:5] == ["backlog", "task", "edit", task_id, "--notes"]
        assert log[2][0] == ["backlog", "task", "edit", task_id, "-s", "Done"]

    @patch("specify_cli.workflow.completion.subprocess.run")
    def test_complete_with_incomplete_acs(
        self, mock_run, task_id, mock_task_data_incomplete
    ):
        """Test completion fails when ACs are not all checked."""
        # Mock subprocess call for getting task data
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps(mock_task_data_incomplete),
            stderr="",
        )

        handler = TaskCompletionHandler(task_id)

        with pytest.raises(TaskCompletionError) as exc_info:
            handler.complete(
                implementation_summary="Test",
                test_summary="Test",
            )

        error_msg = str(exc_info.value)
        assert "Cannot complete task" in error_msg
        assert "1 acceptance criteria still need verification" in error_msg
        assert "#2" in error_msg

        # Should only have called subprocess once (to get task data)
        assert mock_run.call_count == 1

    @patch("specify_cli.workflow.completion.subprocess.run")
    def test_complete_idempotent_already_done(
        self, mock_run, task_id, mock_task_data_done
    ):
        """Test completion is idempotent when task is already Done."""
        # Mock subprocess call for getting task data
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps(mock_task_data_done),
            stderr="",
        )

        handler = TaskCompletionHandler(task_id)
        report = handler.complete(
            implementation_summary="Test",
            test_summary="Test",
        )

        # Should return report without error
        assert isinstance(report, TaskCompletionReport)
        assert report.task_id == task_id

        # Should only have called subprocess once (to get task data)
        assert mock_run.call_count == 1

    @patch("specify_cli.workflow.completion.subprocess.run")
    def test_complete_no_acs(self, mock_run, task_id, mock_task_data_no_acs):
        """Test completion succeeds when task has no ACs."""
        # Mock subprocess calls
        mock_run.side_effect = [
            # Get task data
            MagicMock(
                returncode=0,
                stdout=json.dumps(mock_task_data_no_acs),
                stderr="",
            ),
            # Add notes
            MagicMock(returncode=0, stdout="Notes added", stderr=""),
            # Update status
            MagicMock(returncode=0, stdout="Status updated", stderr=""),
        ]

        handler = TaskCompletionHandler(task_id)
        report = handler.complete(
            implementation_summary="Test",
            test_summary="Test",
        )

        # Should succeed with 0 ACs
        assert report.ac_summary["all_complete"] is True
        assert report.ac_summary["total_acs"] == 0

    @patch("specify_cli.workflow.completion.subprocess.run")
    def test_verify_acceptance_criteria_legacy_format(self, mock_run, task_id):
        """Test AC verification with legacy string format."""
        # Legacy format: plain strings (considered unchecked)
        legacy_task_data = {
            "id": "task-123",
            "status": "In Progress",
            "acceptanceCriteria": ["AC 1", "AC 2", "AC 3"],
        }

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps(legacy_task_data),
            stderr="",
        )

        handler = TaskCompletionHandler(task_id)

        with pytest.raises(TaskCompletionError) as exc_info:
            handler.complete(
                implementation_summary="Test",
                test_summary="Test",
            )

        error_msg = str(exc_info.value)
        assert "3 acceptance criteria still need verification" in error_msg

    @patch("specify_cli.workflow.completion.subprocess.run")
    def test_cli_command_failure(self, mock_run, task_id):
        """Test handling of CLI command failures."""
        # Mock subprocess failure
        from subprocess import CalledProcessError

        mock_run.side_effect = CalledProcessError(
            returncode=1,
            cmd=["backlog", "task", task_id, "--plain"],
            stderr="Command failed",
        )

        handler = TaskCompletionHandler(task_id)

        with pytest.raises(TaskCompletionError) as exc_info:
            handler._get_task_data()

        assert "Backlog CLI command failed" in str(exc_info.value)

    @patch("specify_cli.workflow.completion.subprocess.run")
    def test_json_parse_error(self, mock_run, task_id):
        """Test handling of invalid JSON from CLI."""
        # Mock subprocess with invalid JSON
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Not valid JSON",
            stderr="",
        )

        handler = TaskCompletionHandler(task_id)

        with pytest.raises(TaskCompletionError) as exc_info:
            handler._get_task_data()

        assert "Failed to parse task data" in str(exc_info.value)

    def test_generate_implementation_notes(self, task_id):
        """Test implementation notes generation."""
        handler = TaskCompletionHandler(task_id)

        notes = handler._generate_implementation_notes(
            implementation_summary="Implemented feature X",
            test_summary="Added unit tests",
            key_decisions="Used pattern Y",
        )

        assert "## Implementation Summary" in notes
        assert "### What Was Implemented" in notes
        assert "Implemented feature X" in notes
        assert "### Testing" in notes
        assert "Added unit tests" in notes
        assert "### Key Decisions" in notes
        assert "Used pattern Y" in notes

    def test_generate_implementation_notes_no_decisions(self, task_id):
        """Test implementation notes without key decisions."""
        handler = TaskCompletionHandler(task_id)

        notes = handler._generate_implementation_notes(
            implementation_summary="Test",
            test_summary="Test",
            key_decisions=None,
        )

        assert "## Implementation Summary" in notes
        assert "### Key Decisions" not in notes

    @patch("specify_cli.workflow.completion.subprocess.run")
    def test_command_log_audit_trail(self, mock_run, task_id, mock_task_data_complete):
        """Test that all CLI commands are logged for audit trail."""
        # Mock subprocess calls
        mock_run.side_effect = [
            MagicMock(
                returncode=0,
                stdout=json.dumps(mock_task_data_complete),
                stderr="",
            ),
            MagicMock(returncode=0, stdout="Notes added", stderr=""),
            MagicMock(returncode=0, stdout="Status updated", stderr=""),
        ]

        handler = TaskCompletionHandler(task_id)
        handler.complete(
            implementation_summary="Test",
            test_summary="Test",
        )

        # Verify audit trail
        log = handler.get_command_log()
        assert len(log) == 3

        # Check each command is logged with output
        assert isinstance(log[0], tuple)
        assert len(log[0]) == 2
        assert isinstance(log[0][0], list)
        assert isinstance(log[0][1], str)

    @patch("specify_cli.workflow.completion.subprocess.run")
    def test_complete_with_validation_results(
        self, mock_run, task_id, mock_task_data_complete
    ):
        """Test completion with validation results included."""
        mock_run.side_effect = [
            MagicMock(
                returncode=0,
                stdout=json.dumps(mock_task_data_complete),
                stderr="",
            ),
            MagicMock(returncode=0, stdout="Notes added", stderr=""),
            MagicMock(returncode=0, stdout="Status updated", stderr=""),
        ]

        handler = TaskCompletionHandler(task_id)
        validation_results = {"tests_passed": True, "coverage": 95.5}

        report = handler.complete(
            implementation_summary="Test",
            test_summary="Test",
            validation_results=validation_results,
        )

        assert report.validation_summary == validation_results
