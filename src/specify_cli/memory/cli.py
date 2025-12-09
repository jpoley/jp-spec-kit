"""Memory CLI - Commands for viewing and managing task memory.

This module provides CLI commands for task memory management:
- show: Display task memory content
- append: Append content to task memory
- list: List all task memories (active and archived)
- search: Search across task memories
- clear: Clear task memory content
- cleanup: Cleanup old task memories
- stats: Show task memory statistics

Commands are designed for both interactive use and scripting with --plain/--json options.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table

from .store import TaskMemoryStore

# Create Typer app
memory_app = typer.Typer(
    name="memory",
    help="Task memory management commands",
    add_completion=False,
)

# Rich console for formatted output
console = Console()


@memory_app.command("init")
def init(
    task_id: str = typer.Argument(..., help="Task ID (e.g., task-389)"),
    title: Optional[str] = typer.Option(
        None, "--title", "-t", help="Task title for memory header"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite existing memory"
    ),
    project_root: Optional[str] = typer.Option(
        None, "--project-root", help="Project root directory"
    ),
):
    """Initialize a new task memory file.

    Creates a new memory file from the template for tracking implementation
    context. Use this when starting work on a task.

    Examples:
        # Initialize memory for task
        specify memory init task-389

        # With title
        specify memory init task-389 --title "Implement login feature"

        # Force overwrite existing
        specify memory init task-389 --force
    """
    workspace_root = Path(project_root) if project_root else Path.cwd()
    store = TaskMemoryStore(base_path=workspace_root)

    # Check if memory already exists
    if store.exists(task_id) and not force:
        console.print(f"[yellow]Memory already exists for {task_id}[/yellow]")
        console.print("Use --force to overwrite")
        raise typer.Exit(1)

    # Delete existing if force
    if force and store.exists(task_id):
        store.delete(task_id)

    # Create memory file
    try:
        memory_path = store.create(task_id, task_title=title or "")
        console.print(f"[green]✓[/green] Created task memory: {memory_path}")

    except Exception as e:
        console.print(f"[red]Error creating memory:[/red] {e}")
        raise typer.Exit(1)


@memory_app.command("show")
def show(
    task_id: str = typer.Argument(..., help="Task ID (e.g., task-389)"),
    plain: bool = typer.Option(False, "--plain", help="Plain text output"),
    archived: bool = typer.Option(False, "--archived", help="Show archived memory"),
    project_root: Optional[str] = typer.Option(
        None, "--project-root", help="Project root directory"
    ),
):
    """Display task memory content.

    Examples:
        # Show active task memory
        specify memory show task-389

        # Show archived task memory
        specify memory show task-389 --archived

        # Plain text output
        specify memory show task-389 --plain
    """
    workspace_root = Path(project_root) if project_root else Path.cwd()
    store = TaskMemoryStore(base_path=workspace_root)

    # Determine which directory to check
    if archived:
        memory_path = store.archive_dir / f"{task_id}.md"
        location = "archive"
    else:
        memory_path = store.get_path(task_id)
        location = "active"

    # Check if memory exists
    if not memory_path.exists():
        console.print(f"[red]Task memory not found in {location}:[/red] {task_id}")
        raise typer.Exit(1)

    # Read content
    content = memory_path.read_text()

    # Output
    if plain:
        print(content)
    else:
        # Render as markdown with syntax highlighting
        console.print(f"\n[cyan]Task Memory:[/cyan] {task_id} ({location})")
        console.print(f"[dim]Path: {memory_path}[/dim]\n")
        md = Markdown(content)
        console.print(md)


@memory_app.command("append")
def append(
    task_id: str = typer.Argument(..., help="Task ID (e.g., task-389)"),
    content: str = typer.Argument(..., help="Content to append"),
    section: Optional[str] = typer.Option(
        None, "--section", "-s", help="Section name to append to (e.g., 'Notes')"
    ),
    project_root: Optional[str] = typer.Option(
        None, "--project-root", help="Project root directory"
    ),
):
    """Append content to task memory.

    Appends timestamped content to the task memory file. Content can be
    appended to a specific section or to the end of the file.

    Examples:
        # Append to end of file
        specify memory append task-389 "Implemented feature X"

        # Append to specific section
        specify memory append task-389 "Decision: Use FastAPI" --section "Key Decisions"

        # Multi-line content
        specify memory append task-389 $'Line 1\\nLine 2'
    """
    workspace_root = Path(project_root) if project_root else Path.cwd()
    store = TaskMemoryStore(base_path=workspace_root)

    # Check if task memory exists
    if not store.exists(task_id):
        console.print(f"[red]Task memory not found:[/red] {task_id}")
        console.print(f"[dim]Create it first with: backlog task edit {task_id}[/dim]")
        raise typer.Exit(1)

    # Append content
    try:
        store.append(task_id, content, section=section)
        console.print(f"[green]✓[/green] Content appended to {task_id}")
        if section:
            console.print(f"[dim]Section: {section}[/dim]")
    except Exception as e:
        console.print(f"[red]Error appending content:[/red] {e}")
        raise typer.Exit(1)


@memory_app.command("list")
def list_memories(
    archived: bool = typer.Option(False, "--archived", help="List archived memories"),
    all_memories: bool = typer.Option(
        False, "--all", "-a", help="List both active and archived"
    ),
    plain: bool = typer.Option(False, "--plain", help="Plain text output"),
    project_root: Optional[str] = typer.Option(
        None, "--project-root", help="Project root directory"
    ),
):
    """List all task memories.

    Shows task IDs with memory files, sorted by last modified time.

    Examples:
        # List active memories
        specify memory list

        # List archived memories
        specify memory list --archived

        # List all (active and archived)
        specify memory list --all

        # Plain output for scripting
        specify memory list --plain
    """
    workspace_root = Path(project_root) if project_root else Path.cwd()
    store = TaskMemoryStore(base_path=workspace_root)

    # Determine which memories to list
    if all_memories:
        active_ids = store.list_active()
        archived_ids = store.list_archived()
        memories = [(tid, "active") for tid in active_ids] + [
            (tid, "archived") for tid in archived_ids
        ]
    elif archived:
        archived_ids = store.list_archived()
        memories = [(tid, "archived") for tid in archived_ids]
    else:
        active_ids = store.list_active()
        memories = [(tid, "active") for tid in active_ids]

    if not memories:
        location = "archived" if archived else "active"
        if all_memories:
            location = "any"
        console.print(f"[yellow]No {location} task memories found[/yellow]")
        raise typer.Exit(0)

    # Get file stats for sorting
    memory_data = []
    for task_id, status in memories:
        if status == "archived":
            path = store.archive_dir / f"{task_id}.md"
        else:
            path = store.get_path(task_id)

        if path.exists():
            stat = path.stat()
            memory_data.append(
                {
                    "task_id": task_id,
                    "status": status,
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "path": path,
                }
            )

    # Sort by modified time (newest first)
    memory_data.sort(key=lambda x: x["modified"], reverse=True)

    # Output
    if plain:
        for item in memory_data:
            print(f"{item['task_id']}\t{item['status']}\t{item['size']}")
    else:
        # Create rich table
        table = Table(title=f"Task Memories ({len(memory_data)})")
        table.add_column("Task ID", style="cyan")
        table.add_column("Status")
        table.add_column("Size", justify="right")
        table.add_column("Last Modified")

        for item in memory_data:
            # Format status with color
            if item["status"] == "active":
                status_str = "[green]active[/green]"
            else:
                status_str = "[yellow]archived[/yellow]"

            # Format size
            size_bytes = item["size"]
            if size_bytes < 1024:
                size_str = f"{size_bytes}B"
            elif size_bytes < 1024 * 1024:
                size_str = f"{size_bytes / 1024:.1f}KB"
            else:
                size_str = f"{size_bytes / (1024 * 1024):.1f}MB"

            # Format modified time
            modified_dt = datetime.fromtimestamp(item["modified"])
            modified_str = modified_dt.strftime("%Y-%m-%d %H:%M")

            table.add_row(item["task_id"], status_str, size_str, modified_str)

        console.print(table)


@memory_app.command("search")
def search(
    query: str = typer.Argument(..., help="Search query (supports regex)"),
    include_archived: bool = typer.Option(
        False, "--archived", help="Include archived memories"
    ),
    limit: int = typer.Option(50, "--limit", "-n", help="Maximum number of results"),
    context: int = typer.Option(
        2, "--context", "-C", help="Lines of context around matches"
    ),
    plain: bool = typer.Option(False, "--plain", help="Plain text output"),
    project_root: Optional[str] = typer.Option(
        None, "--project-root", help="Project root directory"
    ),
):
    """Search across task memories.

    Searches for text or regex patterns across active (and optionally archived)
    task memory files. Results include context lines around matches.

    Examples:
        # Simple text search
        specify memory search "FastAPI"

        # Regex pattern
        specify memory search "implement.*feature"

        # Include archived memories
        specify memory search "bug fix" --archived

        # Limit results
        specify memory search "API" --limit 10

        # More context
        specify memory search "decision" --context 5
    """
    workspace_root = Path(project_root) if project_root else Path.cwd()
    store = TaskMemoryStore(base_path=workspace_root)

    # Get list of memories to search
    task_ids = store.list_active()
    if include_archived:
        task_ids.extend(store.list_archived())

    if not task_ids:
        console.print("[yellow]No task memories to search[/yellow]")
        raise typer.Exit(0)

    # Compile regex pattern
    try:
        pattern = re.compile(query, re.IGNORECASE)
    except re.error as e:
        console.print(f"[red]Invalid regex pattern:[/red] {e}")
        raise typer.Exit(1)

    # Search through memories
    results = []
    for task_id in task_ids:
        # Determine path
        if task_id in store.list_archived():
            path = store.archive_dir / f"{task_id}.md"
            status = "archived"
        else:
            path = store.get_path(task_id)
            status = "active"

        if not path.exists():
            continue

        # Read and search content
        try:
            content = path.read_text()
            lines = content.split("\n")

            for i, line in enumerate(lines):
                if pattern.search(line):
                    # Get context lines
                    start = max(0, i - context)
                    end = min(len(lines), i + context + 1)
                    context_lines = lines[start:end]

                    results.append(
                        {
                            "task_id": task_id,
                            "status": status,
                            "line_num": i + 1,
                            "line": line,
                            "context": context_lines,
                            "context_start": start + 1,
                        }
                    )

                    # Check limit
                    if len(results) >= limit:
                        break

            if len(results) >= limit:
                break

        except Exception as e:
            console.print(f"[dim]Warning: Error reading {task_id}: {e}[/dim]")
            continue

    # Output results
    if not results:
        console.print(f"[yellow]No matches found for:[/yellow] {query}")
        raise typer.Exit(0)

    if plain:
        for result in results:
            print(f"{result['task_id']}:{result['line_num']}:{result['line']}")
    else:
        console.print(f"\n[cyan]Found {len(results)} match(es) for:[/cyan] {query}\n")
        if len(results) >= limit:
            console.print(f"[yellow]Showing first {limit} results[/yellow]\n")

        for result in results:
            # Header
            status_color = "green" if result["status"] == "active" else "yellow"
            console.print(
                f"[{status_color}]{result['task_id']}[/{status_color}]"
                f"[dim]:{result['line_num']}[/dim]"
            )

            # Context with highlighted match
            for i, ctx_line in enumerate(result["context"]):
                line_num = result["context_start"] + i
                is_match = line_num == result["line_num"]

                if is_match:
                    # Highlight the matching line
                    highlighted = pattern.sub(
                        lambda m: f"[bold yellow]{m.group()}[/bold yellow]",
                        ctx_line,
                    )
                    console.print(f"  [bold]{line_num:4d}:[/bold] {highlighted}")
                else:
                    console.print(f"  [dim]{line_num:4d}:[/dim] {ctx_line}")

            console.print()


@memory_app.command("clear")
def clear(
    task_id: str = typer.Argument(..., help="Task ID to clear"),
    confirm: bool = typer.Option(
        False, "--confirm", "-y", help="Skip confirmation prompt"
    ),
    no_backup: bool = typer.Option(False, "--no-backup", help="Skip backup creation"),
    project_root: Optional[str] = typer.Option(
        None, "--project-root", help="Project root directory"
    ),
):
    """Clear task memory content.

    Deletes the task memory file. By default, creates a backup before deletion
    and prompts for confirmation.

    Examples:
        # Clear with confirmation prompt
        specify memory clear task-389

        # Skip confirmation
        specify memory clear task-389 --confirm

        # Skip backup
        specify memory clear task-389 --confirm --no-backup
    """
    workspace_root = Path(project_root) if project_root else Path.cwd()
    store = TaskMemoryStore(base_path=workspace_root)

    # Check if task memory exists
    if not store.exists(task_id):
        console.print(f"[red]Task memory not found:[/red] {task_id}")
        raise typer.Exit(1)

    # Get memory path
    memory_path = store.get_path(task_id)

    # Prompt for confirmation if not confirmed
    if not confirm:
        response = typer.confirm(
            f"Clear task memory for {task_id}? This cannot be undone."
        )
        if not response:
            console.print("[dim]Cancelled[/dim]")
            raise typer.Exit(0)

    # Create backup if requested
    if not no_backup:
        backup_dir = workspace_root / ".specify" / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"{task_id}.{timestamp}.bak"

        try:
            import shutil

            shutil.copy2(memory_path, backup_path)
            console.print(f"[dim]Backup created: {backup_path}[/dim]")
        except Exception as e:
            console.print(f"[yellow]Warning: Backup failed:[/yellow] {e}")
            console.print("[yellow]Continuing with deletion...[/yellow]")

    # Delete memory file
    try:
        store.delete(task_id, from_archive=False)
        console.print(f"[green]✓[/green] Task memory cleared: {task_id}")
    except Exception as e:
        console.print(f"[red]Error clearing memory:[/red] {e}")
        raise typer.Exit(1)


@memory_app.command("cleanup")
def cleanup(
    archive_older_than: Optional[int] = typer.Option(
        None,
        "--archive-older-than",
        help="Archive active memories older than N days",
    ),
    delete_older_than: Optional[int] = typer.Option(
        None,
        "--delete-older-than",
        help="Delete archived memories older than N days",
    ),
    dry_run: bool = typer.Option(
        True, "--dry-run/--execute", help="Preview operations without executing"
    ),
    project_root: Optional[str] = typer.Option(
        None, "--project-root", help="Project root directory"
    ),
):
    """Cleanup old task memories.

    Archive old active memories and delete old archived memories based on age.
    By default, runs in dry-run mode to preview operations.

    Examples:
        # Preview archival of memories older than 30 days
        specify memory cleanup --archive-older-than 30

        # Execute archival
        specify memory cleanup --archive-older-than 30 --execute

        # Delete archived memories older than 90 days
        specify memory cleanup --delete-older-than 90 --execute

        # Combined cleanup
        specify memory cleanup --archive-older-than 30 --delete-older-than 90 --execute
    """
    workspace_root = Path(project_root) if project_root else Path.cwd()
    store = TaskMemoryStore(base_path=workspace_root)

    # Calculate cutoff times
    now = datetime.now().timestamp()

    operations = []

    # Find memories to archive
    if archive_older_than is not None:
        archive_cutoff = now - (archive_older_than * 24 * 60 * 60)

        for task_id in store.list_active():
            path = store.get_path(task_id)
            if path.exists():
                modified = path.stat().st_mtime
                if modified < archive_cutoff:
                    operations.append(
                        {
                            "type": "archive",
                            "task_id": task_id,
                            "age_days": (now - modified) / (24 * 60 * 60),
                        }
                    )

    # Find memories to delete
    if delete_older_than is not None:
        delete_cutoff = now - (delete_older_than * 24 * 60 * 60)

        for task_id in store.list_archived():
            path = store.archive_dir / f"{task_id}.md"
            if path.exists():
                modified = path.stat().st_mtime
                if modified < delete_cutoff:
                    operations.append(
                        {
                            "type": "delete",
                            "task_id": task_id,
                            "age_days": (now - modified) / (24 * 60 * 60),
                        }
                    )

    # Display operations
    if not operations:
        console.print("[yellow]No cleanup operations needed[/yellow]")
        raise typer.Exit(0)

    # Summary
    archive_count = sum(1 for op in operations if op["type"] == "archive")
    delete_count = sum(1 for op in operations if op["type"] == "delete")

    console.print("\n[cyan]Cleanup Summary:[/cyan]")
    console.print(f"  Archive: {archive_count} active memories")
    console.print(f"  Delete:  {delete_count} archived memories")
    console.print()

    # Display operations
    if dry_run:
        console.print("[yellow]DRY RUN - No changes will be made[/yellow]\n")

    for op in operations:
        if op["type"] == "archive":
            icon = "[yellow]→[/yellow]"
            action = "Archive"
        else:
            icon = "[red]×[/red]"
            action = "Delete"

        console.print(
            f"{icon} {action} {op['task_id']} "
            f"[dim](age: {op['age_days']:.0f} days)[/dim]"
        )

    # Execute if not dry run
    if not dry_run:
        console.print()
        confirm = typer.confirm("Proceed with cleanup operations?")
        if not confirm:
            console.print("[dim]Cancelled[/dim]")
            raise typer.Exit(0)

        errors = []
        for op in operations:
            try:
                if op["type"] == "archive":
                    store.archive(op["task_id"])
                else:
                    store.delete(op["task_id"], from_archive=True)
            except Exception as e:
                errors.append(f"{op['task_id']}: {e}")

        if errors:
            console.print("\n[red]Errors during cleanup:[/red]")
            for error in errors:
                console.print(f"  - {error}")
            raise typer.Exit(1)
        else:
            console.print("\n[green]✓ Cleanup completed successfully[/green]")
    else:
        console.print("\n[dim]Run with --execute to perform these operations[/dim]")


@memory_app.command("stats")
def stats(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    project_root: Optional[str] = typer.Option(
        None, "--project-root", help="Project root directory"
    ),
):
    """Show task memory statistics.

    Displays analytics about task memory usage including counts, sizes,
    and age statistics.

    Examples:
        # Show statistics
        specify memory stats

        # JSON output for scripting
        specify memory stats --json
    """
    workspace_root = Path(project_root) if project_root else Path.cwd()
    store = TaskMemoryStore(base_path=workspace_root)

    # Collect statistics
    active_ids = store.list_active()
    archived_ids = store.list_archived()

    # Calculate sizes and ages
    active_sizes = []
    active_ages = []
    now = datetime.now().timestamp()

    for task_id in active_ids:
        path = store.get_path(task_id)
        if path.exists():
            stat = path.stat()
            active_sizes.append(stat.st_size)
            active_ages.append((now - stat.st_mtime) / (24 * 60 * 60))

    archived_sizes = []
    archived_ages = []

    for task_id in archived_ids:
        path = store.archive_dir / f"{task_id}.md"
        if path.exists():
            stat = path.stat()
            archived_sizes.append(stat.st_size)
            archived_ages.append((now - stat.st_mtime) / (24 * 60 * 60))

    # Compile stats
    stats_data = {
        "active": {
            "count": len(active_sizes),
            "total_size": sum(active_sizes),
            "avg_size": sum(active_sizes) / len(active_sizes) if active_sizes else 0,
            "max_size": max(active_sizes) if active_sizes else 0,
            "oldest_days": max(active_ages) if active_ages else 0,
            "newest_days": min(active_ages) if active_ages else 0,
        },
        "archived": {
            "count": len(archived_sizes),
            "total_size": sum(archived_sizes),
            "avg_size": (
                sum(archived_sizes) / len(archived_sizes) if archived_sizes else 0
            ),
            "max_size": max(archived_sizes) if archived_sizes else 0,
            "oldest_days": max(archived_ages) if archived_ages else 0,
            "newest_days": min(archived_ages) if archived_ages else 0,
        },
        "total": {
            "count": len(active_sizes) + len(archived_sizes),
            "total_size": sum(active_sizes) + sum(archived_sizes),
        },
    }

    # Output
    if json_output:
        print(json.dumps(stats_data, indent=2))
    else:
        console.print("\n[cyan]Task Memory Statistics[/cyan]\n")

        # Active memories
        console.print("[green]Active Memories[/green]")
        console.print(f"  Count:       {stats_data['active']['count']}")
        console.print(
            f"  Total Size:  {_format_bytes(stats_data['active']['total_size'])}"
        )
        if stats_data["active"]["count"] > 0:
            console.print(
                f"  Avg Size:    {_format_bytes(stats_data['active']['avg_size'])}"
            )
            console.print(
                f"  Largest:     {_format_bytes(stats_data['active']['max_size'])}"
            )
            console.print(
                f"  Oldest:      {stats_data['active']['oldest_days']:.0f} days"
            )
            console.print(
                f"  Newest:      {stats_data['active']['newest_days']:.0f} days"
            )

        console.print()

        # Archived memories
        console.print("[yellow]Archived Memories[/yellow]")
        console.print(f"  Count:       {stats_data['archived']['count']}")
        console.print(
            f"  Total Size:  {_format_bytes(stats_data['archived']['total_size'])}"
        )
        if stats_data["archived"]["count"] > 0:
            console.print(
                f"  Avg Size:    {_format_bytes(stats_data['archived']['avg_size'])}"
            )
            console.print(
                f"  Largest:     {_format_bytes(stats_data['archived']['max_size'])}"
            )
            console.print(
                f"  Oldest:      {stats_data['archived']['oldest_days']:.0f} days"
            )
            console.print(
                f"  Newest:      {stats_data['archived']['newest_days']:.0f} days"
            )

        console.print()

        # Totals
        console.print("[cyan]Total[/cyan]")
        console.print(f"  Count:       {stats_data['total']['count']}")
        console.print(
            f"  Total Size:  {_format_bytes(stats_data['total']['total_size'])}"
        )
        console.print()


def _format_bytes(size: float) -> str:
    """Format byte size in human-readable format."""
    if size < 1024:
        return f"{size:.0f}B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f}KB"
    else:
        return f"{size / (1024 * 1024):.1f}MB"


# Export for main CLI integration
__all__ = ["memory_app"]
