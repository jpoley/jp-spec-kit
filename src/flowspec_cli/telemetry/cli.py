"""CLI commands for telemetry management.

This module provides user-facing commands for:
- Enabling/disabling telemetry (consent management)
- Viewing telemetry status
- Viewing collected telemetry data
- Clearing telemetry data
- Tracking events (for slash command integration)
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .config import (
    disable_telemetry,
    enable_telemetry,
    get_config_path,
    is_telemetry_enabled,
    load_telemetry_config,
)
from .integration import (
    track_handoff,
    track_role_selection as _track_role,
)
from .events import RoleEvent
from .tracker import DEFAULT_TELEMETRY_DIR, DEFAULT_TELEMETRY_FILE, track_role_event
from .writer import TelemetryWriter

telemetry_app = typer.Typer(
    name="telemetry",
    help="Manage telemetry settings and view usage statistics",
    add_completion=False,
)

console = Console()

# Privacy notice text
PRIVACY_NOTICE = """
Flowspec Telemetry Privacy Notice (v1.0)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

What we collect:
• Role selections (dev, pm, qa, etc.)
• Agent invocations (which agents you use)
• Command usage (which /flow commands)
• Workflow transitions

What we DON'T collect:
• Project names (hashed for privacy)
• File contents or code
• Personal information (usernames hashed)
• Any data transmitted to remote servers

Your data:
• Stored locally in .flowspec/telemetry.jsonl
• You can view it anytime: flowspec telemetry view
• You can clear it anytime: flowspec telemetry clear
• You can disable anytime: flowspec telemetry disable

Purpose:
• Improve flowspec workflow recommendations
• Understand which features are most valuable
• Guide future development priorities
"""


def _read_telemetry_events(
    telemetry_path: Path,
    filter_days: int | None = None,
) -> list[dict]:
    """Read and parse telemetry events from a JSONL file.

    Args:
        telemetry_path: Path to the telemetry JSONL file.
        filter_days: If provided, only return events from the last N days.

    Returns:
        List of parsed event dictionaries.
    """
    # Use TelemetryWriter for reading events (limit=0 means read all)
    writer = TelemetryWriter(telemetry_path)
    try:
        # Read all events - TelemetryWriter returns most recent first, reverse to get chronological
        events = writer.read_events(limit=10000)
        events.reverse()
    except OSError:
        return []

    if filter_days is not None:
        cutoff = datetime.now(timezone.utc) - timedelta(days=filter_days)
        filtered_events = []
        for event in events:
            timestamp_str = event.get("timestamp", "")
            if timestamp_str:
                try:
                    ts = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                    if ts < cutoff:
                        continue
                except ValueError:
                    continue
            filtered_events.append(event)
        return filtered_events

    return events


@telemetry_app.command("enable")
def enable_command(
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Skip confirmation prompt",
    ),
    project_root: str = typer.Option(
        None,
        "--project-root",
        "-p",
        help="Project root directory",
    ),
) -> None:
    """Enable telemetry with opt-in consent.

    Shows privacy notice and asks for confirmation before enabling.
    """
    root = Path(project_root) if project_root else Path.cwd()

    if is_telemetry_enabled(root):
        console.print("[green]Telemetry is already enabled.[/green]")
        return

    if not yes:
        # Show privacy notice
        console.print(
            Panel(PRIVACY_NOTICE, title="Privacy Notice", border_style="blue")
        )
        console.print()

        # Ask for confirmation
        confirm = typer.confirm("Do you want to enable telemetry?", default=False)
        if not confirm:
            console.print("[yellow]Telemetry not enabled.[/yellow]")
            raise typer.Exit(0)

    # Enable telemetry
    if enable_telemetry(root):
        console.print("[green]✓ Telemetry enabled.[/green]")
        console.print(
            "[dim]You can disable it anytime with: flowspec telemetry disable[/dim]"
        )
    else:
        console.print("[red]Failed to enable telemetry.[/red]")
        raise typer.Exit(1)


@telemetry_app.command("disable")
def disable_command(
    project_root: str = typer.Option(
        None,
        "--project-root",
        "-p",
        help="Project root directory",
    ),
) -> None:
    """Disable telemetry and revoke consent.

    Your existing telemetry data is preserved. Use 'flowspec telemetry clear'
    to delete collected data.
    """
    root = Path(project_root) if project_root else Path.cwd()

    if not is_telemetry_enabled(root):
        console.print("[yellow]Telemetry is already disabled.[/yellow]")
        return

    if disable_telemetry(root):
        console.print("[green]✓ Telemetry disabled.[/green]")
        console.print(
            "[dim]Use 'flowspec telemetry clear' to delete existing data.[/dim]"
        )
    else:
        console.print("[red]Failed to disable telemetry.[/red]")
        raise typer.Exit(1)


@telemetry_app.command("status")
def status_command(
    project_root: str = typer.Option(
        None,
        "--project-root",
        "-p",
        help="Project root directory",
    ),
) -> None:
    """Show current telemetry status and configuration."""
    root = Path(project_root) if project_root else Path.cwd()

    config = load_telemetry_config(root)
    config_path = get_config_path(root)
    telemetry_path = root / DEFAULT_TELEMETRY_DIR / DEFAULT_TELEMETRY_FILE

    # Count events using helper function
    event_count = TelemetryWriter(telemetry_path).count_events()

    # Build status table
    table = Table(title="Telemetry Status", show_header=False, box=None)
    table.add_column("Setting", style="cyan")
    table.add_column("Value")

    enabled_str = (
        "[green]Enabled[/green]" if config.enabled else "[yellow]Disabled[/yellow]"
    )
    table.add_row("Status", enabled_str)

    if config.consent_given_at:
        table.add_row("Consent Given", config.consent_given_at)
    table.add_row("Consent Version", config.consent_version)
    table.add_row("Retention Days", str(config.data_retention_days))
    table.add_row("Events Collected", str(event_count))
    table.add_row("Config File", str(config_path))
    table.add_row("Data File", str(telemetry_path))

    console.print(table)


@telemetry_app.command("stats")
def stats_command(
    days: int = typer.Option(
        30,
        "--days",
        "-d",
        help="Number of days to analyze",
    ),
    project_root: str = typer.Option(
        None,
        "--project-root",
        "-p",
        help="Project root directory",
    ),
) -> None:
    """Show telemetry statistics and usage patterns."""
    root = Path(project_root) if project_root else Path.cwd()
    telemetry_path = root / DEFAULT_TELEMETRY_DIR / DEFAULT_TELEMETRY_FILE

    if not telemetry_path.exists():
        console.print("[yellow]No telemetry data found.[/yellow]")
        return

    # Read and parse events using helper function
    events = _read_telemetry_events(telemetry_path, filter_days=days)

    if not events:
        console.print(f"[yellow]No events in the last {days} days.[/yellow]")
        return

    # Compute statistics
    event_types: dict[str, int] = {}
    roles: dict[str, int] = {}
    agents: dict[str, int] = {}
    commands: dict[str, int] = {}

    for event in events:
        event_type = event.get("event_type", "unknown")
        event_types[event_type] = event_types.get(event_type, 0) + 1

        if role := event.get("role"):
            roles[role] = roles.get(role, 0) + 1

        if agent := event.get("agent"):
            agents[agent] = agents.get(agent, 0) + 1

        if command := event.get("command"):
            commands[command] = commands.get(command, 0) + 1

    # Display statistics
    console.print(f"\n[bold]Telemetry Statistics (last {days} days)[/bold]\n")

    # Event types
    table = Table(title="Event Types")
    table.add_column("Type", style="cyan")
    table.add_column("Count", justify="right")
    for event_type, count in sorted(event_types.items(), key=lambda x: -x[1]):
        table.add_row(event_type, str(count))
    console.print(table)

    # Roles
    if roles:
        console.print()
        table = Table(title="Roles Used")
        table.add_column("Role", style="green")
        table.add_column("Count", justify="right")
        for role, count in sorted(roles.items(), key=lambda x: -x[1]):
            table.add_row(role, str(count))
        console.print(table)

    # Agents
    if agents:
        console.print()
        table = Table(title="Agents Invoked")
        table.add_column("Agent", style="blue")
        table.add_column("Count", justify="right")
        for agent, count in sorted(agents.items(), key=lambda x: -x[1]):
            table.add_row(agent, str(count))
        console.print(table)

    # Commands
    if commands:
        console.print()
        table = Table(title="Commands Used")
        table.add_column("Command", style="magenta")
        table.add_column("Count", justify="right")
        for command, count in sorted(commands.items(), key=lambda x: -x[1])[:10]:
            table.add_row(command, str(count))
        console.print(table)

    console.print(f"\n[dim]Total events: {len(events)}[/dim]")


@telemetry_app.command("view")
def view_command(
    limit: int = typer.Option(
        20,
        "--limit",
        "-n",
        help="Number of recent events to show",
    ),
    project_root: str = typer.Option(
        None,
        "--project-root",
        "-p",
        help="Project root directory",
    ),
) -> None:
    """View recent telemetry events."""
    root = Path(project_root) if project_root else Path.cwd()
    telemetry_path = root / DEFAULT_TELEMETRY_DIR / DEFAULT_TELEMETRY_FILE

    if not telemetry_path.exists():
        console.print("[yellow]No telemetry data found.[/yellow]")
        return

    # Read all events using helper function
    events = _read_telemetry_events(telemetry_path)

    if not events:
        console.print("[yellow]No events recorded.[/yellow]")
        return

    # Show most recent events
    recent = events[-limit:] if len(events) > limit else events
    recent.reverse()  # Most recent first

    table = Table(title=f"Recent Events (showing {len(recent)} of {len(events)})")
    table.add_column("Time", style="dim")
    table.add_column("Type", style="cyan")
    table.add_column("Role", style="green")
    table.add_column("Agent", style="blue")
    table.add_column("Command", style="magenta")

    for event in recent:
        timestamp = event.get("timestamp", "")[:19]  # Truncate to datetime
        event_type = event.get("event_type", "")
        role = event.get("role", "-")
        agent = event.get("agent", "-")
        command = event.get("command", "-")
        table.add_row(timestamp, event_type, role, agent, command)

    console.print(table)


@telemetry_app.command("clear")
def clear_command(
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Skip confirmation prompt",
    ),
    project_root: str = typer.Option(
        None,
        "--project-root",
        "-p",
        help="Project root directory",
    ),
) -> None:
    """Clear all collected telemetry data.

    This permanently deletes the telemetry.jsonl file.
    Configuration settings are preserved.
    """
    root = Path(project_root) if project_root else Path.cwd()
    telemetry_path = root / DEFAULT_TELEMETRY_DIR / DEFAULT_TELEMETRY_FILE

    if not telemetry_path.exists():
        console.print("[yellow]No telemetry data to clear.[/yellow]")
        return

    # Count events using helper function
    event_count = TelemetryWriter(telemetry_path).count_events()

    if not yes:
        console.print(
            f"[yellow]This will permanently delete {event_count} events.[/yellow]"
        )
        confirm = typer.confirm("Are you sure?", default=False)
        if not confirm:
            console.print("[dim]Cancelled.[/dim]")
            raise typer.Exit(0)

    try:
        telemetry_path.unlink()
        console.print(f"[green]✓ Cleared {event_count} telemetry events.[/green]")
    except OSError as e:
        console.print(f"[red]Failed to clear telemetry data: {e}[/red]")
        raise typer.Exit(1)


@telemetry_app.command("export")
def export_command(
    output: Path = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path (default: stdout)",
    ),
    project_root: str = typer.Option(
        None,
        "--project-root",
        "-p",
        help="Project root directory",
    ),
) -> None:
    """Export telemetry data as JSON.

    Useful for reviewing all collected data or archiving.
    """
    root = Path(project_root) if project_root else Path.cwd()
    telemetry_path = root / DEFAULT_TELEMETRY_DIR / DEFAULT_TELEMETRY_FILE

    if not telemetry_path.exists():
        console.print("[yellow]No telemetry data to export.[/yellow]")
        return

    # Read all events using helper function
    events = _read_telemetry_events(telemetry_path)

    if not events:
        console.print("[yellow]No events to export.[/yellow]")
        return

    # Format as JSON
    json_output = json.dumps(events, indent=2)

    if output:
        try:
            output.write_text(json_output)
            console.print(f"[green]✓ Exported {len(events)} events to {output}[/green]")
        except OSError as e:
            console.print(f"[red]Failed to write export: {e}[/red]")
            raise typer.Exit(1)
    else:
        console.print(json_output)


# ============================================================================
# Tracking Commands - For slash command integration
# ============================================================================


@telemetry_app.command("track-role")
def track_role_command(
    role: str = typer.Argument(..., help="Role that was selected (e.g., dev, pm, qa)"),
    command: str = typer.Option(
        None,
        "--command",
        "-c",
        help="Command that triggered the selection",
    ),
    project_root: str = typer.Option(
        None,
        "--project-root",
        "-p",
        help="Project root directory",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress output (for use in scripts)",
    ),
) -> None:
    """Track a role selection event.

    Used by slash commands to record role selection events.
    Events are only recorded if telemetry is enabled.

    Examples:
        flowspec telemetry track-role dev --command /speckit:configure
        flowspec telemetry track-role pm -c /flow:init -q
    """
    root = Path(project_root) if project_root else Path.cwd()

    if not is_telemetry_enabled(root):
        if not quiet:
            console.print("[dim]Telemetry disabled, event not recorded[/dim]")
        return

    _track_role(role=role, command=command, project_root=root)

    if not quiet:
        console.print(f"[green]✓[/green] Tracked role selection: {role}")


@telemetry_app.command("track-agent")
def track_agent_command(
    agent: str = typer.Argument(..., help="Agent that was invoked"),
    command: str = typer.Option(
        None,
        "--command",
        "-c",
        help="Command that triggered the invocation",
    ),
    role: str = typer.Option(
        None,
        "--role",
        "-r",
        help="Current user role context",
    ),
    project_root: str = typer.Option(
        None,
        "--project-root",
        "-p",
        help="Project root directory",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress output (for use in scripts)",
    ),
) -> None:
    """Track an agent invocation event.

    Used by /flow commands to record agent invocations.
    Events are only recorded if telemetry is enabled.

    Examples:
        flowspec telemetry track-agent backend-engineer --command /flow:implement
        flowspec telemetry track-agent qa-engineer -c /flow:validate -r dev -q
    """
    root = Path(project_root) if project_root else Path.cwd()

    if not is_telemetry_enabled(root):
        if not quiet:
            console.print("[dim]Telemetry disabled, event not recorded[/dim]")
        return

    # Emit a single agent.invoked event (not started+completed from context manager)
    track_role_event(
        RoleEvent.AGENT_INVOKED,
        role=role,
        agent=agent,
        command=command,
        project_root=root,
    )

    if not quiet:
        console.print(f"[green]✓[/green] Tracked agent invocation: {agent}")


@telemetry_app.command("track-handoff")
def track_handoff_command(
    source: str = typer.Argument(..., help="Agent handing off"),
    target: str = typer.Argument(..., help="Agent receiving handoff"),
    role: str = typer.Option(
        None,
        "--role",
        "-r",
        help="Current user role context",
    ),
    project_root: str = typer.Option(
        None,
        "--project-root",
        "-p",
        help="Project root directory",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress output (for use in scripts)",
    ),
) -> None:
    """Track a handoff click event.

    Used to record when users accept agent handoff suggestions.
    Events are only recorded if telemetry is enabled.

    Examples:
        flowspec telemetry track-handoff orchestrator frontend-engineer
        flowspec telemetry track-handoff pm-planner backend-engineer -r dev -q
    """
    root = Path(project_root) if project_root else Path.cwd()

    if not is_telemetry_enabled(root):
        if not quiet:
            console.print("[dim]Telemetry disabled, event not recorded[/dim]")
        return

    track_handoff(
        from_agent=source,
        to_agent=target,
        role=role,
        project_root=root,
    )

    if not quiet:
        console.print(f"[green]✓[/green] Tracked handoff: {source} → {target}")


__all__ = ["telemetry_app"]
