"""Backlog.md integration via MCP tools."""

from .mcp_client import MCPBacklogClient
from .shim import (
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

__all__ = [
    "MCPBacklogClient",
    "ShimResult",
    "check_acceptance_criteria",
    "complete_task",
    "create_task",
    "edit_task",
    "start_task",
    "task_archive",
    "task_create",
    "task_edit",
    "task_list",
    "task_search",
    "task_view",
]
