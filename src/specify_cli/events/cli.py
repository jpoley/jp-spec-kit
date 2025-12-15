"""CLI commands for JSONL event system.

This module provides CLI commands for event emission, querying, and
management. Integrates with the main specify CLI via typer.

Commands:
- emit: Emit an event to the JSONL log
- query: Query events from the log
- cleanup: Clean up old event files
- tail: Watch events in real-time

Example:
    $ specify events emit lifecycle.started --agent-id @backend-engineer
    $ specify events query --date 2025-12-15 --type lifecycle.*
    $ specify events cleanup --days 30
    $ specify events tail
"""

from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import typer
from rich.console import Console
from rich.table import Table

if TYPE_CHECKING:
    from .query import QueryResult

from .writer import (
    DEFAULT_EVENTS_DIR,
    EventWriter,
    EventWriterConfig,
    emit_event,
)

console = Console()
events_app = typer.Typer(
    name="events",
    help="JSONL event log management and emission",
    add_completion=False,
)


@events_app.command("emit")
def events_emit(
    event_type: str = typer.Argument(
        ...,
        help="Namespaced event type (e.g., lifecycle.started, task.state_change)",
    ),
    agent_id: str = typer.Option(
        "@system",
        "--agent-id",
        "-a",
        help="Agent identifier (e.g., @backend-engineer)",
    ),
    message: Optional[str] = typer.Option(
        None,
        "--message",
        "-m",
        help="Human-readable message",
    ),
    progress: Optional[float] = typer.Option(
        None,
        "--progress",
        "-p",
        help="Progress percentage 0.0-1.0 (for activity.progress events)",
        min=0.0,
        max=1.0,
    ),
    task_id: Optional[str] = typer.Option(
        None,
        "--task-id",
        "-t",
        help="Task ID for context",
    ),
    branch: Optional[str] = typer.Option(
        None,
        "--branch",
        "-b",
        help="Git branch name for context",
    ),
    decision_id: Optional[str] = typer.Option(
        None,
        "--decision-id",
        help="Decision ID for context (e.g., ARCH-001)",
    ),
    no_validate: bool = typer.Option(
        False,
        "--no-validate",
        help="Skip schema validation",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output event as JSON instead of confirmation",
    ),
    project_root: Optional[str] = typer.Option(
        None,
        "--project-root",
        help="Project root directory (default: current directory)",
    ),
):
    """Emit an event to the JSONL event log.

    This command writes a v1.1.0 event to the daily JSONL file with
    optional schema validation. Events are persisted for observability
    and can be queried later.

    Examples:
        # Emit lifecycle.started event
        $ specify events emit lifecycle.started -a @backend-engineer -m "Starting task"

        # Emit activity.progress event
        $ specify events emit activity.progress -a @frontend-engineer -p 0.5 -m "50% complete"

        # Emit task.state_change event
        $ specify events emit task.state_change -a @pm-planner -t task-486

        # Emit without validation (for custom event types)
        $ specify events emit custom.event --no-validate

        # JSON output for scripting
        $ specify events emit lifecycle.started --json
    """
    workspace_root = Path(project_root) if project_root else Path.cwd()

    # Build context
    context: dict = {}
    if task_id:
        context["task_id"] = task_id
    if branch:
        context["branch_name"] = branch
    if decision_id:
        context["decision_id"] = decision_id

    # Emit event
    from .writer import _build_event

    event = _build_event(
        event_type=event_type,
        agent_id=agent_id,
        message=message,
        progress=progress,
        context=context if context else None,
    )

    if json_output:
        # Just output the event JSON
        print(json.dumps(event, indent=2))
        # Still write to log
        success = emit_event(
            event_type=event_type,
            agent_id=agent_id,
            message=message,
            progress=progress,
            context=context if context else None,
            project_root=workspace_root,
            validate=not no_validate,
        )
        if not success:
            raise typer.Exit(1)
    else:
        console.print(f"[cyan]Emitting event:[/cyan] {event_type}")
        console.print(f"[dim]Agent:[/dim] {agent_id}")
        if message:
            console.print(f"[dim]Message:[/dim] {message}")

        success = emit_event(
            event_type=event_type,
            agent_id=agent_id,
            message=message,
            progress=progress,
            context=context if context else None,
            project_root=workspace_root,
            validate=not no_validate,
        )

        if success:
            events_dir = workspace_root / DEFAULT_EVENTS_DIR
            today = datetime.now().strftime("%Y-%m-%d")
            console.print(
                f"\n[green]Event written to:[/green] {events_dir}/events-{today}.jsonl"
            )
        else:
            console.print("[red]Failed to write event[/red]")
            raise typer.Exit(1)


@events_app.command("query")
def events_query(
    date: Optional[str] = typer.Option(
        None,
        "--date",
        "-d",
        help="Query events for specific date (YYYY-MM-DD)",
    ),
    start_date: Optional[str] = typer.Option(
        None,
        "--start",
        help="Start date for range query (YYYY-MM-DD)",
    ),
    end_date: Optional[str] = typer.Option(
        None,
        "--end",
        help="End date for range query (YYYY-MM-DD)",
    ),
    last_days: Optional[int] = typer.Option(
        None,
        "--last",
        "-l",
        help="Query events from last N days",
    ),
    event_type: Optional[str] = typer.Option(
        None,
        "--type",
        "-t",
        help="Filter by event type (supports wildcards like lifecycle.*)",
    ),
    namespace: Optional[str] = typer.Option(
        None,
        "--namespace",
        "-N",
        help="Filter by namespace (e.g., lifecycle, git, task)",
    ),
    agent_id: Optional[str] = typer.Option(
        None,
        "--agent",
        "-a",
        help="Filter by agent ID",
    ),
    task_id: Optional[str] = typer.Option(
        None,
        "--task",
        help="Filter by task ID in context",
    ),
    limit: int = typer.Option(
        50,
        "--limit",
        "-n",
        help="Maximum number of events to return",
    ),
    count_by: Optional[str] = typer.Option(
        None,
        "--count-by",
        "-c",
        help="Count events grouped by field (e.g., event_type, agent_id)",
    ),
    group_by: Optional[str] = typer.Option(
        None,
        "--group-by",
        "-g",
        help="Group events by fields (comma-separated)",
    ),
    time_series: Optional[str] = typer.Option(
        None,
        "--time-series",
        "-T",
        help="Aggregate into time buckets (e.g., 1m, 5m, 1h, 1d)",
    ),
    output_format: str = typer.Option(
        "table",
        "--format",
        "-f",
        help="Output format: table, json, csv, markdown",
    ),
    output_file: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Write output to file instead of stdout",
    ),
    project_root: Optional[str] = typer.Option(
        None,
        "--project-root",
        help="Project root directory",
    ),
):
    """Query events from the JSONL log.

    Search and filter events by date, type, agent, or task. Supports
    date ranges, wildcard matching, aggregations, and multiple export formats.

    Examples:
        # Query today's events
        $ specify events query

        # Query specific date
        $ specify events query --date 2025-12-15

        # Query date range
        $ specify events query --start 2025-12-10 --end 2025-12-15

        # Query last 7 days
        $ specify events query --last 7

        # Filter by event type (with wildcard)
        $ specify events query --type lifecycle.*

        # Filter by namespace
        $ specify events query --namespace git

        # Filter by agent
        $ specify events query --agent @backend-engineer

        # Count by event type
        $ specify events query --count-by event_type

        # Group by agent and namespace
        $ specify events query --group-by agent_id,event_type

        # Time series (hourly buckets)
        $ specify events query --time-series 1h

        # Export to CSV
        $ specify events query --format csv --output events.csv

        # Export to JSON
        $ specify events query --format json --output events.json
    """
    from .query import EventQuery

    workspace_root = Path(project_root) if project_root else Path.cwd()
    events_dir = workspace_root / DEFAULT_EVENTS_DIR

    if not events_dir.exists():
        console.print("[yellow]No events directory found[/yellow]")
        console.print(f"[dim]Expected location: {events_dir}[/dim]")
        raise typer.Exit(0)

    # Build query
    query = EventQuery(events_dir=events_dir)

    # Date filters
    if date:
        query = query.date(date)
    elif start_date or end_date:
        query = query.date_range(start_date, end_date)
    elif last_days:
        query = query.last_n_days(last_days)
    else:
        query = query.today()

    # Content filters
    if event_type:
        query = query.filter(event_type=event_type)
    if namespace:
        query = query.filter(namespace=namespace)
    if agent_id:
        query = query.filter(agent_id=agent_id)
    if task_id:
        query = query.filter(task_id=task_id)

    # Aggregations
    if count_by:
        query = query.count_by(count_by)
    if group_by:
        fields = [f.strip() for f in group_by.split(",")]
        query = query.group_by(*fields)
    if time_series:
        query = query.time_series(time_series)

    # Limit (only if no aggregations)
    if not (count_by or group_by or time_series):
        query = query.limit(limit)

    # Execute query
    result = query.execute()

    # Handle output
    if output_file:
        output_path = Path(output_file)
        if output_format == "csv":
            output_path.write_text(result.to_csv())
        elif output_format == "markdown":
            output_path.write_text(result.to_markdown())
        else:  # json
            output_path.write_text(result.to_json())
        console.print(f"[green]Wrote {result.count} events to {output_file}[/green]")
        return

    # Console output
    if output_format == "json":
        print(result.to_json())
    elif output_format == "csv":
        print(result.to_csv())
    elif output_format == "markdown":
        print(result.to_markdown())
    else:
        # Table output
        _display_query_result(result, count_by, group_by, time_series)


def _display_query_result(
    result: "QueryResult",
    count_by: Optional[str],
    group_by: Optional[str],
    time_series: Optional[str],
) -> None:
    """Display query result as rich table."""

    # Aggregation output
    if count_by and "count_by" in result.aggregations:
        console.print(
            f"\n[bold]Count by {count_by}[/bold] ({result.count} total events)\n"
        )
        table = Table()
        table.add_column(count_by, style="cyan")
        table.add_column("Count", justify="right")

        for key, count in list(result.aggregations["count_by"].items())[:20]:
            table.add_row(key, str(count))

        console.print(table)

        if len(result.aggregations["count_by"]) > 20:
            console.print(
                f"[dim]...and {len(result.aggregations['count_by']) - 20} more[/dim]"
            )
        return

    if group_by and "group_by" in result.aggregations:
        console.print(
            f"\n[bold]Group by {group_by}[/bold] ({result.count} total events)\n"
        )
        table = Table()
        table.add_column("Group", style="cyan")
        table.add_column("Count", justify="right")

        for key, data in list(result.aggregations["group_by"].items())[:20]:
            table.add_row(key, str(data["count"]))

        console.print(table)
        return

    if time_series and "time_series" in result.aggregations:
        console.print(
            f"\n[bold]Time Series ({time_series} buckets)[/bold] ({result.count} total events)\n"
        )
        table = Table()
        table.add_column("Bucket", style="dim")
        table.add_column("Count", justify="right")

        for key, data in result.aggregations["time_series"].items():
            bucket_str = data["bucket"][:19]  # Trim timezone
            table.add_row(bucket_str, str(data["count"]))

        console.print(table)
        return

    # Event list output
    if not result.events:
        console.print("[yellow]No events found matching criteria[/yellow]")
        return

    table = Table(title=f"Events ({result.count} found)")
    table.add_column("Timestamp", style="dim", width=20)
    table.add_column("Type", style="cyan")
    table.add_column("Agent")
    table.add_column("Message", max_width=40)

    for event in result.events:
        timestamp = event.get("timestamp", "")[:19]
        table.add_row(
            timestamp,
            event.get("event_type", "?"),
            event.get("agent_id", "?"),
            (event.get("message") or "")[:40],
        )

    console.print(table)

    if result.metadata.get("query_time_ms"):
        console.print(
            f"[dim]Query completed in {result.metadata['query_time_ms']:.1f}ms[/dim]"
        )


@events_app.command("cleanup")
def events_cleanup(
    days: int = typer.Option(
        30,
        "--days",
        "-d",
        help="Retention period in days",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would be deleted without deleting",
    ),
    project_root: Optional[str] = typer.Option(
        None,
        "--project-root",
        help="Project root directory",
    ),
):
    """Clean up old event files based on retention policy.

    Removes JSONL event files older than the specified retention period.
    Default is 30 days.

    Examples:
        # Clean up files older than 30 days (default)
        $ specify events cleanup

        # Clean up files older than 7 days
        $ specify events cleanup --days 7

        # Dry run to see what would be deleted
        $ specify events cleanup --dry-run
    """
    from datetime import datetime, timedelta, timezone

    workspace_root = Path(project_root) if project_root else Path.cwd()
    events_dir = workspace_root / DEFAULT_EVENTS_DIR

    if not events_dir.exists():
        console.print("[yellow]No events directory found[/yellow]")
        raise typer.Exit(0)

    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    files_to_remove = []

    for file_path in sorted(events_dir.glob("events-*.jsonl")):
        try:
            date_str = file_path.stem.replace("events-", "")
            file_date = datetime.strptime(date_str, "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )
            if file_date < cutoff_date:
                files_to_remove.append(file_path)
        except ValueError:
            continue

    if not files_to_remove:
        console.print(f"[green]No files older than {days} days[/green]")
        raise typer.Exit(0)

    console.print(
        f"[cyan]Found {len(files_to_remove)} file(s) older than {days} days:[/cyan]"
    )
    for f in files_to_remove:
        console.print(f"  - {f.name}")

    if dry_run:
        console.print("\n[yellow]DRY RUN - no files deleted[/yellow]")
    else:
        for f in files_to_remove:
            f.unlink()
        console.print(f"\n[green]Deleted {len(files_to_remove)} file(s)[/green]")


@events_app.command("tail")
def events_tail(
    follow: bool = typer.Option(
        True,
        "--follow/--no-follow",
        "-f",
        help="Follow new events in real-time",
    ),
    lines: int = typer.Option(
        10,
        "--lines",
        "-n",
        help="Number of initial lines to show",
    ),
    project_root: Optional[str] = typer.Option(
        None,
        "--project-root",
        help="Project root directory",
    ),
):
    """Watch events in real-time (like tail -f).

    Shows recent events and optionally follows new events as they
    are written to the log.

    Examples:
        # Show last 10 events and follow
        $ specify events tail

        # Show last 20 events without following
        $ specify events tail -n 20 --no-follow

        # Follow only (no initial events)
        $ specify events tail -n 0
    """
    workspace_root = Path(project_root) if project_root else Path.cwd()
    events_dir = workspace_root / DEFAULT_EVENTS_DIR

    if not events_dir.exists():
        console.print("[yellow]No events directory found[/yellow]")
        raise typer.Exit(0)

    # Get today's file
    today = datetime.now().strftime("%Y-%m-%d")
    file_path = events_dir / f"events-{today}.jsonl"

    # Show initial lines
    if lines > 0 and file_path.exists():
        with open(file_path) as f:
            all_lines = f.readlines()
            initial_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            for line in initial_lines:
                _print_event_line(line.strip())

    if not follow:
        return

    # Follow new events
    console.print("\n[dim]Following new events... (Ctrl+C to stop)[/dim]\n")

    try:
        if file_path.exists():
            with open(file_path) as f:
                f.seek(0, 2)  # Go to end
                while True:
                    line = f.readline()
                    if line:
                        _print_event_line(line.strip())
                    else:
                        time.sleep(0.5)
        else:
            # Wait for file to be created
            while True:
                if file_path.exists():
                    with open(file_path) as f:
                        while True:
                            line = f.readline()
                            if line:
                                _print_event_line(line.strip())
                            else:
                                time.sleep(0.5)
                time.sleep(1.0)
    except KeyboardInterrupt:
        console.print("\n[dim]Stopped following[/dim]")


def _print_event_line(line: str) -> None:
    """Print a single event line with formatting."""
    if not line:
        return

    try:
        event = json.loads(line)
        timestamp = event.get("timestamp", "")[:19]
        event_type = event.get("event_type", "?")
        agent_id = event.get("agent_id", "?")
        message = event.get("message", "")

        # Color code by namespace
        namespace = event_type.split(".")[0] if "." in event_type else "unknown"
        colors = {
            "lifecycle": "green",
            "activity": "blue",
            "task": "yellow",
            "git": "magenta",
            "decision": "cyan",
            "action": "white",
            "security": "red",
        }
        color = colors.get(namespace, "white")

        console.print(
            f"[dim]{timestamp}[/dim] [{color}]{event_type}[/{color}] "
            f"[dim]{agent_id}[/dim] {message}"
        )
    except json.JSONDecodeError:
        console.print(f"[red]Invalid JSON:[/red] {line[:50]}...")


@events_app.command("stats")
def events_stats(
    date: Optional[str] = typer.Option(
        None,
        "--date",
        "-d",
        help="Statistics for specific date (YYYY-MM-DD)",
    ),
    project_root: Optional[str] = typer.Option(
        None,
        "--project-root",
        help="Project root directory",
    ),
):
    """Show event statistics.

    Displays summary statistics including event counts by type,
    namespace, and agent.

    Examples:
        # Today's statistics
        $ specify events stats

        # Statistics for specific date
        $ specify events stats --date 2025-12-15
    """
    from collections import Counter

    workspace_root = Path(project_root) if project_root else Path.cwd()
    events_dir = workspace_root / DEFAULT_EVENTS_DIR

    if not events_dir.exists():
        console.print("[yellow]No events directory found[/yellow]")
        raise typer.Exit(0)

    # Create reader
    config = EventWriterConfig(events_dir=events_dir, validate_schema=False)
    writer = EventWriter(config)

    # Read events
    events = writer.read_events(date=date) if date else writer.read_events()

    if not events:
        console.print("[yellow]No events found[/yellow]")
        raise typer.Exit(0)

    # Compute statistics
    type_counter: Counter = Counter()
    namespace_counter: Counter = Counter()
    agent_counter: Counter = Counter()

    for event in events:
        event_type = event.get("event_type", "unknown")
        type_counter[event_type] += 1

        namespace = event_type.split(".")[0] if "." in event_type else "unknown"
        namespace_counter[namespace] += 1

        agent_id = event.get("agent_id", "unknown")
        agent_counter[agent_id] += 1

    # Display
    console.print(f"\n[bold]Event Statistics[/bold] ({len(events)} total events)\n")

    # By namespace
    console.print("[cyan]By Namespace:[/cyan]")
    for namespace, count in namespace_counter.most_common(10):
        console.print(f"  {namespace}: {count}")

    console.print("\n[cyan]By Event Type:[/cyan]")
    for event_type, count in type_counter.most_common(10):
        console.print(f"  {event_type}: {count}")

    console.print("\n[cyan]By Agent:[/cyan]")
    for agent_id, count in agent_counter.most_common(10):
        console.print(f"  {agent_id}: {count}")


# Export for main CLI integration
__all__ = ["events_app"]
