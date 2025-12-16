"""Telemetry integration helpers for flowspec commands.

This module provides decorators and helpers for integrating telemetry
into role selection, agent invocation, and handoff events.

Integration Points:
- Role selection: init command, configure command
- Agent invocation: /flow:implement, /flow:validate, /flow:plan
- Handoff clicks: VS Code Copilot agent handoffs

Example:
    from flowspec_cli.telemetry.integration import (
        track_role_selection,
        track_agent_invocation,
        track_handoff,
    )

    # In init command
    track_role_selection(role="dev")

    # In flow:implement command
    with track_agent_invocation(
        command="/flow:implement",
        agent="backend-engineer",
        role="dev"
    ):
        # Agent work here
        pass

    # On handoff click
    track_handoff(
        from_agent="backend-engineer",
        to_agent="qa-engineer",
        role="dev"
    )
"""

from __future__ import annotations

import functools
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Generator, ParamSpec, TypeVar

from .config import is_telemetry_enabled
from .events import RoleEvent
from .tracker import track_role_event

P = ParamSpec("P")
R = TypeVar("R")


def track_role_selection(
    role: str,
    *,
    command: str | None = None,
    context: dict[str, Any] | None = None,
    project_root: Path | None = None,
) -> None:
    """Track a role selection event.

    Called when user selects a role in init or configure commands.

    Args:
        role: The selected role (e.g., "dev", "pm", "qa")
        command: The command that triggered the selection
        context: Additional context
        project_root: Project root directory
    """
    if not is_telemetry_enabled(project_root):
        return

    track_role_event(
        RoleEvent.ROLE_SELECTED,
        role=role,
        command=command,
        context=context,
        project_root=project_root,
    )


def track_role_change(
    new_role: str,
    old_role: str | None = None,
    *,
    command: str | None = None,
    context: dict[str, Any] | None = None,
    project_root: Path | None = None,
) -> None:
    """Track a role change event.

    Called when user changes their role.

    Args:
        new_role: The new role
        old_role: The previous role (if known)
        command: The command that triggered the change
        context: Additional context
        project_root: Project root directory
    """
    if not is_telemetry_enabled(project_root):
        return

    ctx = context or {}
    if old_role:
        ctx["previous_role"] = old_role

    track_role_event(
        RoleEvent.ROLE_CHANGED,
        role=new_role,
        command=command,
        context=ctx,
        project_root=project_root,
    )


@contextmanager
def track_agent_invocation(
    agent: str,
    *,
    role: str | None = None,
    command: str | None = None,
    context: dict[str, Any] | None = None,
    project_root: Path | None = None,
) -> Generator[None, None, None]:
    """Context manager to track agent invocation lifecycle.

    Emits agent.started on entry and agent.completed/agent.failed on exit.

    Args:
        agent: The agent being invoked (e.g., "backend-engineer")
        role: The user's current role
        command: The command that invoked the agent
        context: Additional context
        project_root: Project root directory

    Example:
        with track_agent_invocation("backend-engineer", role="dev"):
            # Agent work here
            pass
    """
    if not is_telemetry_enabled(project_root):
        yield
        return

    # Emit agent.started
    track_role_event(
        RoleEvent.AGENT_STARTED,
        role=role,
        agent=agent,
        command=command,
        context=context,
        project_root=project_root,
    )

    try:
        yield
        # Emit agent.completed on success
        track_role_event(
            RoleEvent.AGENT_COMPLETED,
            role=role,
            agent=agent,
            command=command,
            context=context,
            project_root=project_root,
        )
    except Exception:
        # Emit agent.failed on exception
        track_role_event(
            RoleEvent.AGENT_FAILED,
            role=role,
            agent=agent,
            command=command,
            context=context,
            project_root=project_root,
        )
        raise


def track_agent_invocation_decorator(
    agent: str,
    *,
    role: str | None = None,
    command: str | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator to track agent invocation for a function.

    Args:
        agent: The agent being invoked
        role: The user's current role
        command: The command that invoked the agent

    Example:
        @track_agent_invocation_decorator("backend-engineer", role="dev")
        def implement_feature():
            # Agent work here
            pass
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            with track_agent_invocation(agent, role=role, command=command):
                return func(*args, **kwargs)

        return wrapper

    return decorator


def track_handoff(
    from_agent: str,
    to_agent: str,
    *,
    role: str | None = None,
    command: str | None = None,
    context: dict[str, Any] | None = None,
    project_root: Path | None = None,
) -> None:
    """Track a handoff click event.

    Called when user clicks a handoff link in VS Code Copilot agents.

    Args:
        from_agent: The agent handing off
        to_agent: The agent receiving the handoff
        role: The user's current role
        command: The command context
        context: Additional context
        project_root: Project root directory
    """
    if not is_telemetry_enabled(project_root):
        return

    ctx = context or {}
    ctx["from_agent"] = from_agent
    ctx["to_agent"] = to_agent

    track_role_event(
        RoleEvent.HANDOFF_CLICKED,
        role=role,
        agent=to_agent,
        command=command,
        context=ctx,
        project_root=project_root,
    )


def track_command_execution(
    command: str,
    *,
    role: str | None = None,
    context: dict[str, Any] | None = None,
    project_root: Path | None = None,
) -> None:
    """Track a command execution event.

    Called when a /flow or /spec command is executed.

    Args:
        command: The command being executed (e.g., "/flow:implement")
        role: The user's current role
        context: Additional context
        project_root: Project root directory
    """
    if not is_telemetry_enabled(project_root):
        return

    track_role_event(
        RoleEvent.COMMAND_EXECUTED,
        role=role,
        command=command,
        context=context,
        project_root=project_root,
    )


@contextmanager
def track_workflow(
    workflow_name: str,
    *,
    role: str | None = None,
    command: str | None = None,
    context: dict[str, Any] | None = None,
    project_root: Path | None = None,
) -> Generator[None, None, None]:
    """Context manager to track workflow lifecycle.

    Emits workflow.started on entry and workflow.completed/failed on exit.

    Args:
        workflow_name: Name of the workflow (e.g., "implement", "validate")
        role: The user's current role
        command: The command that started the workflow
        context: Additional context
        project_root: Project root directory
    """
    if not is_telemetry_enabled(project_root):
        yield
        return

    ctx = context or {}
    ctx["workflow"] = workflow_name

    # Emit workflow.started
    track_role_event(
        RoleEvent.WORKFLOW_STARTED,
        role=role,
        command=command,
        context=ctx,
        project_root=project_root,
    )

    try:
        yield
        # Emit workflow.completed on success
        track_role_event(
            RoleEvent.WORKFLOW_COMPLETED,
            role=role,
            command=command,
            context=ctx,
            project_root=project_root,
        )
    except Exception:
        # Emit workflow.failed on exception
        track_role_event(
            RoleEvent.WORKFLOW_FAILED,
            role=role,
            command=command,
            context=ctx,
            project_root=project_root,
        )
        raise


__all__ = [
    "track_role_selection",
    "track_role_change",
    "track_agent_invocation",
    "track_agent_invocation_decorator",
    "track_handoff",
    "track_command_execution",
    "track_workflow",
]
