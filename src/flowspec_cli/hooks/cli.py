"""CLI commands for flowspec hooks system.

This module provides CLI commands for event emission, hook validation,
and hook management. Integrates with the main specify CLI via typer.

Commands:
- emit: Emit an event and trigger matching hooks
- validate: Validate hooks configuration
- list: List configured hooks
- audit: View hook execution audit log
- test: Test a specific hook with a mock event

Example:
    $ specify hooks emit spec.created --spec-id my-feature
    $ specify hooks validate
    $ specify hooks list
    $ specify hooks audit --tail 10
    $ specify hooks test run-tests implement.completed
"""

from __future__ import annotations

import json
import socket
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .config import (
    HooksConfigError,
    HooksConfigNotFoundError,
    HooksSecurityError,
    load_hooks_config,
    validate_hooks_config_file,
)
from .emitter import EventEmitter
from .events import Event
from .security import AuditLogger

console = Console()
hooks_app = typer.Typer(
    name="hooks",
    help="Hook management and event emission",
    add_completion=False,
)


@hooks_app.command("emit")
def hooks_emit(
    event_type: str = typer.Argument(
        ...,
        help="Event type to emit (e.g., spec.created, task.completed, agent.progress)",
    ),
    spec_id: Optional[str] = typer.Option(
        None,
        "--spec-id",
        help="Spec/feature ID",
    ),
    task_id: Optional[str] = typer.Option(
        None,
        "--task-id",
        help="Task ID",
    ),
    files: Optional[list[str]] = typer.Option(
        None,
        "--file",
        "-f",
        help="Files involved (can be specified multiple times)",
    ),
    progress: Optional[int] = typer.Option(
        None,
        "--progress",
        "-p",
        help="Progress percentage 0-100 (for agent.progress events)",
        min=0,
        max=100,
    ),
    message: Optional[str] = typer.Option(
        None,
        "--message",
        "-m",
        help="Status message (for agent.* events)",
    ),
    agent_id: Optional[str] = typer.Option(
        None,
        "--agent-id",
        help="Agent identifier (for agent.* events, default: claude-code@<hostname>)",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would run without executing",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results as JSON",
    ),
    project_root: Optional[str] = typer.Option(
        None,
        "--project-root",
        help="Project root directory (default: current directory)",
    ),
):
    """Emit an event and trigger matching hooks.

    This command allows manual emission of workflow events, which is useful for:
    - Testing hooks before integrating them into /flowspec commands
    - Manual triggering of quality gates
    - Integration with external tools and scripts
    - Multi-machine agent progress tracking

    Examples:
        # Emit spec.created event
        specify hooks emit spec.created --spec-id my-feature

        # Emit task.completed event
        specify hooks emit task.completed --task-id task-123 --spec-id my-feature

        # Emit implement.completed with files
        specify hooks emit implement.completed --spec-id auth -f src/auth/login.py -f src/auth/signup.py

        # Emit agent.progress for multi-machine observability
        specify hooks emit agent.progress --task-id task-229 --progress 60 --message "Implementing hooks"

        # Emit agent.started when beginning work
        specify hooks emit agent.started --task-id task-229 --spec-id agent-hooks

        # Dry run (show what would execute)
        specify hooks emit spec.created --spec-id test --dry-run

        # JSON output for scripting
        specify hooks emit task.completed --task-id task-123 --json
    """
    # Determine project root
    workspace_root = Path(project_root) if project_root else Path.cwd()

    # Build event context
    context: dict = {}
    if task_id:
        context["task_id"] = task_id
    if spec_id:
        context["feature"] = spec_id

    # Add agent-specific context for agent.* events
    if event_type.startswith("agent."):
        # Default agent_id to claude-code@<hostname>
        resolved_agent_id = agent_id or f"claude-code@{socket.gethostname()}"
        context["agent_id"] = resolved_agent_id
        context["machine"] = socket.gethostname()

        if progress is not None:
            context["progress_percent"] = progress
        if message:
            context["status_message"] = message

    # Create event
    try:
        event = Event(
            event_type=event_type,
            project_root=str(workspace_root),
            feature=spec_id,
            context=context if context else None,
        )
    except Exception as e:
        console.print(f"[red]Error creating event:[/red] {e}")
        raise typer.Exit(1)

    # Create emitter
    try:
        emitter = EventEmitter(workspace_root=workspace_root, dry_run=dry_run)
    except Exception as e:
        console.print(f"[red]Error initializing emitter:[/red] {e}")
        raise typer.Exit(1)

    if not json_output:
        console.print(
            f"[cyan]Emitting event:[/cyan] {event_type}"
            + (f" (spec: {spec_id})" if spec_id else "")
            + (f" (task: {task_id})" if task_id else "")
        )
        if dry_run:
            console.print("[yellow]DRY RUN MODE - No hooks will be executed[/yellow]\n")

    # Emit event
    try:
        results = emitter.emit(event)
    except Exception as e:
        console.print(f"[red]Error emitting event:[/red] {e}")
        raise typer.Exit(1)

    # Output results
    if json_output:
        output_data = {
            "event": event.to_dict(),
            "hooks_executed": len(results),
            "results": [r.to_dict() for r in results],
            "all_successful": all(r.success for r in results),
        }
        print(json.dumps(output_data, indent=2))
    else:
        if not results:
            console.print("[dim]No hooks matched this event[/dim]")
        else:
            console.print(f"\n[green]Executed {len(results)} hook(s):[/green]")
            for result in results:
                status = "[green]✓[/green]" if result.success else "[red]✗[/red]"
                console.print(
                    f"{status} {result.hook_name} "
                    f"(exit={result.exit_code}, {result.duration_ms}ms)"
                )
                if result.error:
                    console.print(f"  [red]Error:[/red] {result.error}")
                if result.stderr and not result.success:
                    console.print(f"  [dim]stderr:[/dim] {result.stderr[:200]}")

            # Summary
            success_count = sum(1 for r in results if r.success)
            if success_count == len(results):
                console.print("\n[green]All hooks succeeded[/green]")
            else:
                console.print(
                    f"\n[yellow]{len(results) - success_count} hook(s) failed[/yellow]"
                )


@hooks_app.command("validate")
def hooks_validate(
    file: Optional[str] = typer.Option(
        None,
        "--file",
        "-f",
        help="Config file to validate (default: .specify/hooks/hooks.yaml)",
    ),
    project_root: Optional[str] = typer.Option(
        None,
        "--project-root",
        help="Project root directory (default: current directory)",
    ),
):
    """Validate hooks configuration.

    Validates hooks.yaml against:
    - YAML syntax
    - JSON schema
    - Security constraints (script paths, timeouts, env vars)
    - Script file existence
    - Duplicate hook names

    Examples:
        # Validate default hooks.yaml
        specify hooks validate

        # Validate specific config file
        specify hooks validate -f .specify/hooks/custom.yaml

        # Validate in different project directory
        specify hooks validate --project-root /path/to/project
    """
    workspace_root = Path(project_root) if project_root else Path.cwd()

    if file:
        config_path = Path(file)
        console.print(f"[cyan]Validating:[/cyan] {config_path}")
    else:
        config_path_rel = ".specify/hooks/hooks.yaml"
        config_path = workspace_root / config_path_rel
        console.print(f"[cyan]Validating:[/cyan] {config_path_rel}")

    # Check if file exists
    if not config_path.exists():
        console.print(f"[red]Config file not found:[/red] {config_path}")
        raise typer.Exit(1)

    # Validate
    try:
        is_valid, errors, warnings = validate_hooks_config_file(
            config_path=config_path,
            project_root=workspace_root,
        )
    except Exception as e:
        console.print(f"[red]Validation error:[/red] {e}")
        raise typer.Exit(1)

    # Display results
    if errors:
        console.print(f"\n[red]✗ Validation failed with {len(errors)} error(s):[/red]")
        for error in errors:
            console.print(f"  - {error}")

    if warnings:
        console.print(f"\n[yellow]⚠ {len(warnings)} warning(s):[/yellow]")
        for warning in warnings:
            console.print(f"  - {warning}")

    if is_valid:
        console.print(
            "\n[green]✓ Validation passed: hooks configuration is valid[/green]"
        )
        raise typer.Exit(0)
    else:
        raise typer.Exit(1)


@hooks_app.command("list")
def hooks_list(
    project_root: Optional[str] = typer.Option(
        None,
        "--project-root",
        help="Project root directory (default: current directory)",
    ),
):
    """List configured hooks.

    Shows all hooks defined in hooks.yaml with their event types,
    execution methods, and configuration.

    Example:
        specify hooks list
    """
    workspace_root = Path(project_root) if project_root else Path.cwd()

    # Load config
    try:
        config = load_hooks_config(project_root=workspace_root)
    except HooksConfigNotFoundError:
        console.print("[yellow]No hooks configuration found[/yellow]")
        console.print("[dim]Create .specify/hooks/hooks.yaml to configure hooks[/dim]")
        raise typer.Exit(0)
    except (HooksConfigError, HooksSecurityError) as e:
        console.print(f"[red]Error loading hooks config:[/red] {e}")
        raise typer.Exit(1)

    if not config.hooks:
        console.print("[yellow]No hooks configured[/yellow]")
        raise typer.Exit(0)

    # Display hooks table
    table = Table(title=f"Configured Hooks ({len(config.hooks)})")
    table.add_column("Name", style="cyan")
    table.add_column("Events")
    table.add_column("Method")
    table.add_column("Timeout", justify="right")
    table.add_column("Fail Mode")

    for hook in config.hooks:
        # Get execution method
        method_type, method_value = hook.get_execution_method()
        if method_type == "script":
            method_str = f"script: {method_value}"
        elif method_type == "command":
            method_str = f"command: {method_value[:40]}..."
        else:
            method_str = f"{method_type}: {method_value}"

        # Format event types
        event_list = []
        for matcher in hook.events:
            if matcher.type:
                event_list.append(matcher.type)
            elif matcher.pattern:
                event_list.append(f"pattern: {matcher.pattern}")

        events_str = "\n".join(event_list) if event_list else "[dim]all[/dim]"

        # Add row
        table.add_row(
            hook.name,
            events_str,
            method_str,
            f"{hook.timeout}s",
            hook.fail_mode,
        )

    console.print(table)


@hooks_app.command("audit")
def hooks_audit(
    tail: int = typer.Option(
        10,
        "--tail",
        "-n",
        help="Number of recent entries to show",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output as JSON",
    ),
    project_root: Optional[str] = typer.Option(
        None,
        "--project-root",
        help="Project root directory (default: current directory)",
    ),
):
    """View hook execution audit log.

    Shows recent hook executions with timestamps, success status,
    and execution times.

    Examples:
        # Show last 10 executions
        specify hooks audit

        # Show last 20 executions
        specify hooks audit --tail 20

        # JSON output
        specify hooks audit --json
    """
    workspace_root = Path(project_root) if project_root else Path.cwd()
    audit_log_path = workspace_root / ".specify" / "hooks" / "audit.log"

    if not audit_log_path.exists():
        console.print("[yellow]No audit log found[/yellow]")
        console.print(f"[dim]Expected location: {audit_log_path}[/dim]")
        raise typer.Exit(0)

    # Load audit log
    logger = AuditLogger(audit_log_path)
    entries = logger.get_recent_entries(count=tail)

    if not entries:
        console.print("[yellow]Audit log is empty[/yellow]")
        raise typer.Exit(0)

    # Output
    if json_output:
        print(json.dumps({"entries": entries, "count": len(entries)}, indent=2))
    else:
        # Display table
        table = Table(title=f"Hook Audit Log (last {len(entries)} entries)")
        table.add_column("Timestamp", style="dim")
        table.add_column("Hook", style="cyan")
        table.add_column("Event")
        table.add_column("Status")
        table.add_column("Duration", justify="right")

        for entry in entries:
            # Format timestamp
            timestamp = entry.get("timestamp", "")[:19]  # Remove timezone

            # Format status
            success = entry.get("success", False)
            exit_code = entry.get("exit_code", -1)
            if success:
                status_str = "[green]✓[/green] success"
            else:
                status_str = f"[red]✗[/red] exit={exit_code}"
                if entry.get("error"):
                    status_str += f"\n[dim]{entry['error'][:40]}...[/dim]"

            # Format duration
            duration_ms = entry.get("duration_ms", 0)
            if duration_ms < 1000:
                duration_str = f"{duration_ms}ms"
            else:
                duration_str = f"{duration_ms / 1000:.1f}s"

            table.add_row(
                timestamp,
                entry.get("hook_name", "?"),
                entry.get("event_type", "?"),
                status_str,
                duration_str,
            )

        console.print(table)


@hooks_app.command("test")
def hooks_test(
    hook_name: str = typer.Argument(
        ...,
        help="Name of hook to test",
    ),
    event_type: str = typer.Argument(
        ...,
        help="Event type to simulate",
    ),
    spec_id: str = typer.Option(
        "test-spec",
        "--spec-id",
        help="Spec/feature ID for mock event",
    ),
    project_root: Optional[str] = typer.Option(
        None,
        "--project-root",
        help="Project root directory (default: current directory)",
    ),
):
    """Test a specific hook with a mock event.

    Executes a single hook with a mock event for testing purposes.
    Useful for validating hook scripts before committing them to
    the workflow.

    Examples:
        # Test run-tests hook with implement.completed event
        specify hooks test run-tests implement.completed

        # Test with custom spec ID
        specify hooks test quality-gate spec.created --spec-id my-feature
    """
    workspace_root = Path(project_root) if project_root else Path.cwd()

    # Load config
    try:
        config = load_hooks_config(project_root=workspace_root)
    except HooksConfigNotFoundError:
        console.print("[red]No hooks configuration found[/red]")
        raise typer.Exit(1)
    except (HooksConfigError, HooksSecurityError) as e:
        console.print(f"[red]Error loading hooks config:[/red] {e}")
        raise typer.Exit(1)

    # Find hook by name
    hook = None
    for h in config.hooks:
        if h.name == hook_name:
            hook = h
            break

    if hook is None:
        console.print(f"[red]Hook not found:[/red] {hook_name}")
        console.print(
            f"[dim]Available hooks: {', '.join(h.name for h in config.hooks)}[/dim]"
        )
        raise typer.Exit(1)

    # Create mock event
    event = Event(
        event_type=event_type,
        project_root=str(workspace_root),
        feature=spec_id,
        context={"test": True},
    )

    console.print(f"[cyan]Testing hook:[/cyan] {hook_name}")
    console.print(f"[cyan]Event type:[/cyan] {event_type}")
    console.print(f"[cyan]Spec ID:[/cyan] {spec_id}\n")

    # Execute hook
    from .runner import HookRunner

    runner = HookRunner(workspace_root=workspace_root)

    try:
        result = runner.run_hook(hook, event)
    except Exception as e:
        console.print(f"[red]Hook execution failed:[/red] {e}")
        raise typer.Exit(1)

    # Display result
    if result.success:
        console.print(
            f"[green]✓ Hook succeeded[/green] (exit={result.exit_code}, {result.duration_ms}ms)"
        )
    else:
        console.print(
            f"[red]✗ Hook failed[/red] (exit={result.exit_code}, {result.duration_ms}ms)"
        )

    if result.stdout:
        console.print("\n[cyan]stdout:[/cyan]")
        console.print(result.stdout)

    if result.stderr:
        console.print("\n[cyan]stderr:[/cyan]")
        console.print(result.stderr)

    if result.error:
        console.print(f"\n[red]Error:[/red] {result.error}")

    # Exit with hook's exit code
    raise typer.Exit(result.exit_code)


# Export for main CLI integration
__all__ = ["hooks_app"]
