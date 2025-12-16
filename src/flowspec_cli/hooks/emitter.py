"""Event emitter for flowspec hooks system.

This module provides the event emission layer that workflow commands use to
publish events. The emitter is designed to be fail-safe and lightweight,
ensuring event emission never breaks workflow execution.

Features:
- Synchronous event emission with immediate hook execution
- Asynchronous event emission (fire-and-forget) for non-critical events
- Fail-safe design: errors in hooks don't break workflows
- Performance optimized: <50ms overhead per event emission
- Dry-run mode for testing without side effects

Example:
    >>> from flowspec_cli.hooks import Event, EventEmitter
    >>> emitter = EventEmitter(workspace_root=Path("/project"))
    >>> event = Event(event_type="spec.created", project_root="/project")
    >>> results = emitter.emit(event)
    >>> for result in results:
    ...     print(f"{result.hook_name}: {result.success}")
"""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .runner import HookResult

from .config import load_hooks_config
from .events import (
    Event,
    create_implement_completed_event,
    create_spec_created_event,
    create_task_completed_event,
)
from .schema import HooksConfig

logger = logging.getLogger(__name__)


class EventEmitter:
    """Emits events and triggers matching hooks.

    The emitter is the main entry point for event-driven hook execution.
    It loads hook configuration, matches events against hook definitions,
    and executes matching hooks via the HookRunner.

    Attributes:
        workspace_root: Project root directory.
        config: Hooks configuration (loaded from hooks.yaml).
        dry_run: If True, log hooks without executing them.

    Example:
        >>> emitter = EventEmitter(workspace_root=Path("/project"))
        >>> event = Event(event_type="spec.created", project_root="/project")
        >>> results = emitter.emit(event)
        >>> print(f"Executed {len(results)} hooks")
    """

    def __init__(
        self,
        workspace_root: Path,
        config: HooksConfig | None = None,
        dry_run: bool = False,
    ):
        """Initialize emitter with workspace and optional config.

        Args:
            workspace_root: Project root directory.
            config: Pre-loaded hooks configuration (optional). If not provided,
                configuration will be loaded from workspace_root/.flowspec/hooks/hooks.yaml.
            dry_run: If True, log hooks without executing them (for testing).

        Example:
            >>> emitter = EventEmitter(workspace_root=Path.cwd())
            >>> # With explicit config
            >>> config = load_hooks_config()
            >>> emitter = EventEmitter(workspace_root=Path.cwd(), config=config)
        """
        self.workspace_root = workspace_root
        self.dry_run = dry_run

        # Load config if not provided
        if config is None:
            try:
                self.config = load_hooks_config(project_root=workspace_root)
            except Exception as e:
                logger.warning(f"Failed to load hooks config: {e}")
                # Fall back to empty config (no hooks)
                from .schema import HooksConfig

                self.config = HooksConfig.empty()
        else:
            self.config = config

    def emit(self, event: Event) -> list[HookResult]:
        """Emit event and run all matching hooks synchronously.

        This is the primary method for event emission. It:
        1. Finds all hooks that match the event
        2. Executes each hook in sequence
        3. Collects and returns all results

        Hook execution errors are caught and logged but don't raise exceptions,
        ensuring one failing hook doesn't break the workflow.

        Args:
            event: Event to emit.

        Returns:
            List of HookResult instances, one per executed hook. Returns empty
            list if no hooks match or if all hooks are disabled.

        Example:
            >>> event = Event(event_type="task.completed", project_root="/tmp")
            >>> results = emitter.emit(event)
            >>> for result in results:
            ...     if not result.success:
            ...         print(f"Hook {result.hook_name} failed: {result.error}")
        """
        # Import here to avoid circular dependency
        from .runner import HookRunner

        # Find matching hooks
        matching_hooks = self.config.get_matching_hooks(event)

        if not matching_hooks:
            logger.debug(f"No hooks match event type: {event.event_type}")
            return []

        logger.info(f"Event {event.event_type}: {len(matching_hooks)} hook(s) matched")

        # Dry-run mode: log without executing
        if self.dry_run:
            logger.info("[DRY-RUN] Would execute hooks:")
            for hook in matching_hooks:
                logger.info(f"  - {hook.name}")
            return []

        # Execute hooks and collect results
        results: list[HookResult] = []
        runner = HookRunner(workspace_root=self.workspace_root)

        for hook in matching_hooks:
            try:
                result = runner.run_hook(hook, event)
                results.append(result)

                # Log result
                if result.success:
                    logger.info(
                        f"Hook '{hook.name}' completed in {result.duration_ms}ms"
                    )
                else:
                    logger.warning(
                        f"Hook '{hook.name}' failed (exit={result.exit_code}): "
                        f"{result.error or 'See stderr'}"
                    )

                # Check fail_mode: stop on first failure?
                if not result.success and hook.fail_mode == "stop":
                    logger.error(
                        f"Hook '{hook.name}' failed with fail_mode=stop. "
                        "Stopping hook execution."
                    )
                    break

            except Exception as e:
                # Catch all exceptions to ensure fail-safe behavior
                logger.error(
                    f"Unexpected error executing hook '{hook.name}': {e}",
                    exc_info=True,
                )
                # Create error result
                from .runner import HookResult

                error_result = HookResult(
                    hook_name=hook.name,
                    success=False,
                    exit_code=-1,
                    stdout="",
                    stderr="",
                    duration_ms=0,
                    error=str(e),
                )
                results.append(error_result)

        return results

    def emit_async(self, event: Event) -> None:
        """Emit event asynchronously (fire-and-forget).

        Executes hooks in a background thread without waiting for completion.
        Useful for non-critical events like logging or notifications where
        you don't want to block the workflow.

        Note: Results are not returned. Hook failures are logged but not
        raised. Use emit() if you need results or failure handling.

        Args:
            event: Event to emit.

        Example:
            >>> event = Event(event_type="task.updated", project_root="/tmp")
            >>> emitter.emit_async(event)  # Returns immediately
            >>> # Hook execution happens in background
        """

        def _emit_in_background():
            try:
                self.emit(event)
            except Exception as e:
                logger.error(
                    f"Background event emission failed for {event.event_type}: {e}",
                    exc_info=True,
                )

        thread = threading.Thread(
            target=_emit_in_background,
            name=f"hook-emit-{event.event_type}",
            daemon=True,
        )
        thread.start()
        logger.debug(f"Event {event.event_type} emitted asynchronously")


# --- Convenience functions for common events ---


def emit_event(
    event: Event,
    workspace_root: Path | None = None,
    dry_run: bool = False,
) -> list[HookResult]:
    """Emit event using default emitter.

    Convenience function that creates an emitter and emits an event.
    Use this for one-off event emissions where you don't need to reuse
    the emitter instance.

    Args:
        event: Event to emit.
        workspace_root: Project root directory. Defaults to event.project_root.
        dry_run: If True, log hooks without executing them.

    Returns:
        List of HookResult instances.

    Example:
        >>> from flowspec_cli.hooks import Event, emit_event
        >>> event = Event(event_type="spec.created", project_root="/project")
        >>> results = emit_event(event)
    """
    if workspace_root is None:
        workspace_root = Path(event.project_root)

    emitter = EventEmitter(workspace_root=workspace_root, dry_run=dry_run)
    return emitter.emit(event)


def emit_spec_created(
    spec_id: str,
    files: list[str],
    workspace_root: Path,
    agent: str = "pm-planner",
    dry_run: bool = False,
) -> list[HookResult]:
    """Convenience function for spec.created events.

    Args:
        spec_id: Feature/spec identifier.
        files: List of created spec files (relative paths).
        workspace_root: Project root directory.
        agent: Agent that created the spec (default: pm-planner).
        dry_run: If True, log hooks without executing them.

    Returns:
        List of HookResult instances.

    Example:
        >>> results = emit_spec_created(
        ...     spec_id="user-auth",
        ...     files=["docs/prd/user-auth-spec.md"],
        ...     workspace_root=Path("/project")
        ... )
    """
    event = create_spec_created_event(
        project_root=str(workspace_root),
        feature=spec_id,
        spec_path=files[0] if files else "docs/prd/spec.md",
        agent=agent,
    )
    return emit_event(event, workspace_root=workspace_root, dry_run=dry_run)


def emit_task_completed(
    task_id: str,
    task_title: str,
    workspace_root: Path,
    priority: str | None = None,
    labels: list[str] | None = None,
    dry_run: bool = False,
) -> list[HookResult]:
    """Convenience function for task.completed events.

    Args:
        task_id: Task identifier (e.g., "task-189").
        task_title: Task title.
        workspace_root: Project root directory.
        priority: Task priority (high, medium, low).
        labels: Task labels.
        dry_run: If True, log hooks without executing them.

    Returns:
        List of HookResult instances.

    Example:
        >>> results = emit_task_completed(
        ...     task_id="task-189",
        ...     task_title="Implement authentication",
        ...     workspace_root=Path("/project"),
        ...     priority="high",
        ...     labels=["backend", "security"]
        ... )
    """
    event = create_task_completed_event(
        project_root=str(workspace_root),
        task_id=task_id,
        task_title=task_title,
        priority=priority,
        labels=labels,
    )
    return emit_event(event, workspace_root=workspace_root, dry_run=dry_run)


def emit_implement_completed(
    spec_id: str,
    files: list[str],
    workspace_root: Path,
    task_id: str | None = None,
    files_changed: int | None = None,
    dry_run: bool = False,
) -> list[HookResult]:
    """Convenience function for implement.completed events.

    Args:
        spec_id: Feature/spec identifier.
        files: List of modified source files.
        workspace_root: Project root directory.
        task_id: Associated task ID (optional).
        files_changed: Number of files modified (optional).
        dry_run: If True, log hooks without executing them.

    Returns:
        List of HookResult instances.

    Example:
        >>> results = emit_implement_completed(
        ...     spec_id="user-auth",
        ...     files=["src/auth/login.py", "src/auth/signup.py"],
        ...     workspace_root=Path("/project"),
        ...     task_id="task-189",
        ...     files_changed=15
        ... )
    """
    # Determine source path from files
    source_path = "./src/"
    if files:
        # Use directory of first file
        first_file = Path(files[0])
        if len(first_file.parts) > 1:
            source_path = str(first_file.parent) + "/"

    event = create_implement_completed_event(
        project_root=str(workspace_root),
        feature=spec_id,
        task_id=task_id,
        files_changed=files_changed or len(files),
        source_path=source_path,
    )
    return emit_event(event, workspace_root=workspace_root, dry_run=dry_run)
