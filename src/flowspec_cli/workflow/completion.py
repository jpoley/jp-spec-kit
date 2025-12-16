"""Task completion handler for workflow execution.

This module provides the TaskCompletionHandler class for managing task completion
in the workflow, including AC verification, implementation note generation, and
status updates via the backlog CLI.
"""

from __future__ import annotations

import json
import logging
import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TaskCompletionReport:
    """Report generated after completing a task.

    Attributes:
        task_id: The ID of the completed task
        completion_timestamp: When the task was marked as Done
        ac_summary: Summary of acceptance criteria completion status
        validation_summary: Summary of validation results
    """

    task_id: str
    completion_timestamp: datetime
    ac_summary: dict[str, Any]
    validation_summary: dict[str, Any]


class TaskCompletionError(Exception):
    """Raised when task completion fails."""

    pass


class TaskCompletionHandler:
    """Handles task completion workflow including AC verification and status updates.

    The completion handler ensures all acceptance criteria are verified before
    marking a task as Done, generates implementation notes, and provides an
    audit trail of all backlog CLI commands executed.

    Example:
        >>> handler = TaskCompletionHandler("task-123")
        >>> report = handler.complete(
        ...     implementation_summary="Implemented feature X",
        ...     test_summary="All tests passing",
        ... )
        >>> print(report.task_id)
        'task-123'
    """

    def __init__(self, task_id: str) -> None:
        """Initialize the completion handler.

        Args:
            task_id: The ID of the task to complete
        """
        self.task_id = task_id
        self._command_log: list[tuple[list[str], str]] = []

    def complete(
        self,
        implementation_summary: str,
        test_summary: str,
        key_decisions: str | None = None,
        validation_results: dict[str, Any] | None = None,
    ) -> TaskCompletionReport:
        """Complete a task with full verification and documentation.

        This method:
        1. Verifies 100% of ACs are checked
        2. Generates implementation notes
        3. Adds notes to the task
        4. Updates task status to Done
        5. Returns a completion report

        Args:
            implementation_summary: Summary of what was implemented
            test_summary: Summary of how it was tested
            key_decisions: Optional summary of key decisions made
            validation_results: Optional validation results to include in report

        Returns:
            TaskCompletionReport with completion details

        Raises:
            TaskCompletionError: If ACs are not 100% complete or CLI commands fail
        """
        # AC #1: Verify 100% of ACs are checked
        task_data = self._get_task_data()
        ac_status = self._verify_acceptance_criteria(task_data)

        # AC #2: If any AC unchecked, halt and report
        if not ac_status["all_complete"]:
            unchecked = ac_status["unchecked_acs"]
            raise TaskCompletionError(
                f"Cannot complete task {self.task_id}: "
                f"{len(unchecked)} acceptance criteria still need verification.\n"
                f"Unchecked ACs: {', '.join(f'#{ac}' for ac in unchecked)}"
            )

        # AC #7: Handle edge case - task already Done (idempotent)
        if task_data.get("status") == "Done":
            logger.info(f"Task {self.task_id} is already Done")
            return TaskCompletionReport(
                task_id=self.task_id,
                completion_timestamp=datetime.now(),
                ac_summary=ac_status,
                validation_summary=validation_results or {},
            )

        # AC #3: Generate implementation notes
        impl_notes = self._generate_implementation_notes(
            implementation_summary=implementation_summary,
            test_summary=test_summary,
            key_decisions=key_decisions,
        )

        # AC #4: Add implementation notes via backlog CLI
        self._add_implementation_notes(impl_notes)

        # AC #5: Update task status to Done
        self._update_task_status()

        # AC #6: Generate completion report
        completion_time = datetime.now()
        report = TaskCompletionReport(
            task_id=self.task_id,
            completion_timestamp=completion_time,
            ac_summary=ac_status,
            validation_summary=validation_results or {},
        )

        logger.info(f"Task {self.task_id} completed successfully at {completion_time}")

        return report

    def _get_task_data(self) -> dict[str, Any]:
        """Retrieve task data via backlog CLI.

        Returns:
            Parsed task data as dictionary

        Raises:
            TaskCompletionError: If CLI command fails
        """
        cmd = ["backlog", "task", self.task_id, "--plain"]
        result = self._run_cli_command(cmd)

        try:
            return json.loads(result)
        except json.JSONDecodeError as e:
            raise TaskCompletionError(
                f"Failed to parse task data for {self.task_id}: {e}"
            ) from e

    def _verify_acceptance_criteria(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """Verify acceptance criteria completion status.

        Args:
            task_data: Task data from backlog CLI

        Returns:
            Dictionary with AC verification results:
                - total_acs: Total number of ACs
                - checked_acs: Number of checked ACs
                - unchecked_acs: List of unchecked AC indices
                - all_complete: Boolean indicating 100% completion
        """
        acceptance_criteria = task_data.get("acceptanceCriteria", [])
        total_acs = len(acceptance_criteria)

        if total_acs == 0:
            # No ACs defined - consider complete
            return {
                "total_acs": 0,
                "checked_acs": 0,
                "unchecked_acs": [],
                "all_complete": True,
            }

        unchecked_acs = []
        for i, ac in enumerate(acceptance_criteria, start=1):
            if isinstance(ac, dict):
                if not ac.get("checked", False):
                    unchecked_acs.append(i)
            elif isinstance(ac, str):
                # Legacy format: plain strings are considered unchecked
                unchecked_acs.append(i)

        checked_acs = total_acs - len(unchecked_acs)

        return {
            "total_acs": total_acs,
            "checked_acs": checked_acs,
            "unchecked_acs": unchecked_acs,
            "all_complete": len(unchecked_acs) == 0,
        }

    def _generate_implementation_notes(
        self,
        implementation_summary: str,
        test_summary: str,
        key_decisions: str | None = None,
    ) -> str:
        """Generate formatted implementation notes.

        Args:
            implementation_summary: What was implemented
            test_summary: How it was tested
            key_decisions: Optional key decisions made

        Returns:
            Formatted implementation notes as markdown
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        notes = f"""## Implementation Summary ({timestamp})

### What Was Implemented
{implementation_summary}

### Testing
{test_summary}
"""

        if key_decisions:
            notes += f"""
### Key Decisions
{key_decisions}
"""

        return notes

    def _add_implementation_notes(self, notes: str) -> None:
        """Add implementation notes to task via backlog CLI.

        Args:
            notes: Implementation notes to add

        Raises:
            TaskCompletionError: If CLI command fails
        """
        cmd = ["backlog", "task", "edit", self.task_id, "--notes", notes]
        self._run_cli_command(cmd)
        logger.info(f"Added implementation notes to task {self.task_id}")

    def _update_task_status(self) -> None:
        """Update task status to Done via backlog CLI.

        Raises:
            TaskCompletionError: If CLI command fails
        """
        cmd = ["backlog", "task", "edit", self.task_id, "-s", "Done"]
        self._run_cli_command(cmd)
        logger.info(f"Updated task {self.task_id} status to Done")

    def _run_cli_command(self, cmd: list[str]) -> str:
        """Run a backlog CLI command and log it for audit trail.

        Args:
            cmd: Command and arguments to run

        Returns:
            Command stdout as string

        Raises:
            TaskCompletionError: If command fails
        """
        # AC #8: Log all backlog CLI commands for audit trail
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )
            output = result.stdout
            self._command_log.append((cmd, output))
            logger.debug(f"Executed: {' '.join(cmd)}")
            return output
        except subprocess.CalledProcessError as e:
            self._command_log.append((cmd, f"ERROR: {e.stderr}"))
            logger.error(f"Command failed: {' '.join(cmd)}\n{e.stderr}")
            raise TaskCompletionError(
                f"Backlog CLI command failed: {' '.join(cmd)}\n{e.stderr}"
            ) from e

    def get_command_log(self) -> list[tuple[list[str], str]]:
        """Get the audit trail of all CLI commands executed.

        Returns:
            List of (command, output) tuples
        """
        return self._command_log.copy()
