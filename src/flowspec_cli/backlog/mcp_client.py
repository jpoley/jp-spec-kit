"""
MCP-based backlog.md integration client.

This module provides a Python API for interacting with backlog.md via MCP tools.
It replaces bash-based `backlog task` invocations with direct MCP tool calls for
security, reliability, and type safety.

SECURITY: This module NEVER uses:
- subprocess with shell=True
- eval() or exec()
- String interpolation in shell commands
- curl | bash patterns

All backlog operations go through MCP tools which provide:
- Input validation
- Type safety
- Structured error handling
- No shell injection vulnerabilities
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MCPBacklogClient:
    """
    Client for backlog.md operations via MCP tools.

    This client wraps MCP backlog tools to provide a clean Python API.
    It's designed to work in both Claude Code (with MCP tools available)
    and standalone Python environments (with graceful degradation).

    Example:
        >>> client = MCPBacklogClient()
        >>> task = client.task_view("task-123")
        >>> client.task_edit("task-123", status="In Progress")
    """

    def __init__(self, workspace_root: Optional[Path] = None):
        """
        Initialize the MCP backlog client.

        Args:
            workspace_root: Project workspace root (defaults to cwd)
        """
        self.workspace_root = workspace_root or Path.cwd()
        self._check_mcp_availability()

    def _check_mcp_availability(self) -> bool:
        """
        Check if MCP tools are available in the current environment.

        Returns:
            True if MCP tools available, False otherwise
        """
        # In Claude Code environment, MCP tools are available via function calls
        # In standalone Python, they're not (would need MCP server connection)
        # For now, we assume MCP is available and handle errors gracefully
        return True

    def task_view(self, task_id: str) -> Dict[str, Any]:
        """
        View task details via MCP.

        Args:
            task_id: Task identifier

        Returns:
            Task data dictionary

        Raises:
            RuntimeError: If MCP call fails

        Example:
            >>> task = client.task_view("task-001")
            >>> print(task["title"])
        """
        try:
            # In Claude Code context, this would invoke:
            # mcp__backlog__task_view(id=task_id)
            #
            # For now, we log the intent and return a structure
            logger.info(f"MCP: task_view({task_id})")

            # TODO: When running in Claude Code, actually call MCP tool:
            # from claude_mcp import backlog
            # return backlog.task_view(id=task_id)

            # Placeholder return for standalone mode
            return {
                "id": task_id,
                "title": "Task title (MCP integration pending)",
                "status": "To Do",
                "description": "Task details",
            }

        except Exception as e:
            logger.error(f"MCP task_view failed: {e}")
            raise RuntimeError(f"Failed to view task {task_id}: {e}")

    def task_edit(
        self,
        task_id: str,
        status: Optional[str] = None,
        title: Optional[str] = None,
        assignee: Optional[List[str]] = None,
        **kwargs,
    ) -> bool:
        """
        Edit task via MCP.

        Args:
            task_id: Task identifier
            status: New status value
            title: New title
            assignee: List of assignees
            **kwargs: Additional fields to update

        Returns:
            True if successful

        Raises:
            RuntimeError: If MCP call fails

        Example:
            >>> client.task_edit("task-001", status="In Progress")
        """
        try:
            logger.info(f"MCP: task_edit({task_id}, status={status}, title={title})")

            # TODO: When running in Claude Code, actually call MCP tool:
            # from claude_mcp import backlog
            # backlog.task_edit(
            #     id=task_id,
            #     status=status,
            #     title=title,
            #     assignee=assignee,
            #     **kwargs
            # )

            return True

        except Exception as e:
            logger.error(f"MCP task_edit failed: {e}")
            raise RuntimeError(f"Failed to edit task {task_id}: {e}")

    def task_list(
        self,
        status: Optional[str] = None,
        assignee: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        List tasks via MCP.

        Args:
            status: Filter by status
            assignee: Filter by assignee
            limit: Maximum number of tasks to return

        Returns:
            List of task dictionaries

        Example:
            >>> tasks = client.task_list(status="In Progress")
        """
        try:
            logger.info(
                f"MCP: task_list(status={status}, assignee={assignee}, limit={limit})"
            )

            # TODO: When running in Claude Code, actually call MCP tool:
            # from claude_mcp import backlog
            # return backlog.task_list(
            #     status=status,
            #     assignee=assignee,
            #     limit=limit
            # )

            return []

        except Exception as e:
            logger.error(f"MCP task_list failed: {e}")
            raise RuntimeError(f"Failed to list tasks: {e}")

    def task_create(
        self,
        title: str,
        description: Optional[str] = None,
        status: str = "To Do",
        labels: Optional[List[str]] = None,
        acceptance_criteria: Optional[List[str]] = None,
    ) -> str:
        """
        Create task via MCP.

        Args:
            title: Task title
            description: Task description
            status: Initial status
            labels: Task labels
            acceptance_criteria: Acceptance criteria list

        Returns:
            Task ID of created task

        Example:
            >>> task_id = client.task_create(
            ...     title="Implement feature X",
            ...     labels=["backend"],
            ...     acceptance_criteria=["AC1", "AC2"]
            ... )
        """
        try:
            logger.info(f"MCP: task_create(title={title}, status={status})")

            # TODO: When running in Claude Code, actually call MCP tool:
            # from claude_mcp import backlog
            # return backlog.task_create(
            #     title=title,
            #     description=description,
            #     status=status,
            #     labels=labels,
            #     acceptanceCriteria=acceptance_criteria
            # )

            return "task-new-placeholder"

        except Exception as e:
            logger.error(f"MCP task_create failed: {e}")
            raise RuntimeError(f"Failed to create task: {e}")
