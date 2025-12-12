# OP-002: Execution Metrics per Workflow Phase

> **Status**: Draft
> **Priority**: High
> **Inspired By**: [opcode AgentRunMetrics](https://github.com/winfunc/opcode/blob/main/src-tauri/src/commands/agents.rs#L59-L66)
> **Dependencies**: OP-001 (Cost/Usage Tracking)

## Executive Summary

After each `/flow:*` workflow command completes, automatically display execution metrics including duration, token usage, cost, and files modified. This provides immediate feedback on phase costs without requiring separate commands.

## Problem Statement

### Current State
- Workflow commands complete silently (no metrics)
- No visibility into how long phases take
- Cannot compare phase costs across runs
- No data for estimating similar future work
- Must manually run `specify usage` to see costs

### Desired State
- Each `/flow:*` command shows metrics on completion
- Consistent metric format across all phases
- Metrics optionally stored in task notes
- Historical metrics queryable for estimation
- Minimal overhead (< 500ms to calculate)

## User Stories

### US-1: Developer sees phase completion metrics
**As a** developer running `/flow:implement`
**I want to** see metrics when the command completes
**So that** I understand what resources were consumed

**Acceptance Criteria**:
- [ ] Duration displayed in human-readable format
- [ ] Token usage broken down (input, output, cache)
- [ ] Cost displayed in USD
- [ ] Files modified count shown
- [ ] Displayed automatically without extra commands

### US-2: Developer compares phase metrics
**As a** developer who has run multiple tasks
**I want to** see historical metrics for workflow phases
**So that** I can estimate costs for similar work

**Acceptance Criteria**:
- [ ] Metrics stored in task implementation notes
- [ ] Can query: `specify metrics --phase implement --last 10`
- [ ] Shows min/max/avg for phase type
- [ ] Filterable by task labels (e.g., `--label backend`)

### US-3: Team lead reviews workflow efficiency
**As a** team lead
**I want to** see aggregate metrics by workflow phase
**So that** I can identify inefficient phases

**Acceptance Criteria**:
- [ ] `specify metrics summary` shows phase averages
- [ ] Identifies phases that consistently exceed budgets
- [ ] Exportable for reporting

## Technical Design

### Metrics Data Model

```python
# src/specify_cli/workflow/metrics.py

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
import json

@dataclass
class PhaseMetrics:
    """Metrics collected during a workflow phase execution."""

    # Identification
    phase: str                    # "assess", "specify", "plan", etc.
    task_id: Optional[str]        # Associated backlog task
    session_id: str               # Claude Code session ID

    # Timing
    start_time: datetime
    end_time: Optional[datetime] = None

    # Token usage
    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_tokens: int = 0
    cache_read_tokens: int = 0

    # Cost
    cost_usd: float = 0.0

    # Activity
    files_modified: int = 0
    files_created: int = 0
    files_deleted: int = 0
    tool_calls: int = 0

    # Model info
    model: str = "unknown"

    @property
    def duration_seconds(self) -> float:
        """Duration in seconds."""
        if not self.end_time:
            return 0
        return (self.end_time - self.start_time).total_seconds()

    @property
    def total_tokens(self) -> int:
        """Total tokens used."""
        return (
            self.input_tokens +
            self.output_tokens +
            self.cache_creation_tokens +
            self.cache_read_tokens
        )

    def format_duration(self) -> str:
        """Format duration for display."""
        secs = self.duration_seconds
        if secs < 60:
            return f"{secs:.0f}s"
        elif secs < 3600:
            mins = int(secs // 60)
            secs = int(secs % 60)
            return f"{mins}m {secs}s"
        else:
            hours = int(secs // 3600)
            mins = int((secs % 3600) // 60)
            return f"{hours}h {mins}m"

    def format_tokens(self) -> str:
        """Format token usage for display."""
        return (
            f"{self.total_tokens:,} "
            f"(in: {self.input_tokens:,}, out: {self.output_tokens:,})"
        )

    def format_files(self) -> str:
        """Format file changes for display."""
        parts = []
        if self.files_modified:
            parts.append(f"{self.files_modified} modified")
        if self.files_created:
            parts.append(f"{self.files_created} created")
        if self.files_deleted:
            parts.append(f"{self.files_deleted} deleted")
        return ", ".join(parts) if parts else "no changes"

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        d = asdict(self)
        d["start_time"] = self.start_time.isoformat()
        d["end_time"] = self.end_time.isoformat() if self.end_time else None
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "PhaseMetrics":
        """Create from dictionary."""
        d["start_time"] = datetime.fromisoformat(d["start_time"])
        if d["end_time"]:
            d["end_time"] = datetime.fromisoformat(d["end_time"])
        return cls(**d)
```

### Metrics Collector

```python
# src/specify_cli/workflow/collector.py

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from .metrics import PhaseMetrics
from ..usage.parser import parse_jsonl_file, get_claude_projects_dir

class MetricsCollector:
    """Collects metrics during workflow phase execution."""

    def __init__(
        self,
        phase: str,
        task_id: Optional[str] = None,
        project_path: Optional[str] = None,
    ):
        self.phase = phase
        self.task_id = task_id
        self.project_path = project_path or os.getcwd()
        self.start_time = datetime.now()
        self.session_id = self._get_current_session_id()
        self._initial_files = self._snapshot_files()

    def _get_current_session_id(self) -> str:
        """Get the current Claude Code session ID."""
        # Session ID is in environment or can be derived from JSONL
        session_id = os.environ.get("CLAUDE_SESSION_ID", "")
        if session_id:
            return session_id

        # Fall back to finding most recent session for project
        projects_dir = get_claude_projects_dir()
        encoded_path = self.project_path.replace("/", "-")
        project_dir = projects_dir / encoded_path

        if project_dir.exists():
            jsonl_files = sorted(
                project_dir.glob("*.jsonl"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            if jsonl_files:
                return jsonl_files[0].stem

        return "unknown"

    def _snapshot_files(self) -> dict:
        """Snapshot file states for change detection."""
        snapshot = {}
        project = Path(self.project_path)

        for path in project.rglob("*"):
            if path.is_file() and not self._should_ignore(path):
                try:
                    stat = path.stat()
                    snapshot[str(path.relative_to(project))] = {
                        "mtime": stat.st_mtime,
                        "size": stat.st_size,
                    }
                except (OSError, ValueError):
                    continue

        return snapshot

    def _should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored."""
        ignore_patterns = [
            ".git", "__pycache__", "node_modules", ".venv",
            ".pytest_cache", ".mypy_cache", "dist", "build",
            ".claude", ".backlog",
        ]
        parts = path.parts
        return any(p in parts for p in ignore_patterns)

    def _calculate_file_changes(self) -> tuple[int, int, int]:
        """Calculate files modified, created, deleted."""
        current_files = self._snapshot_files()

        modified = 0
        created = 0
        deleted = 0

        # Check for modified and created
        for path, state in current_files.items():
            if path not in self._initial_files:
                created += 1
            elif state != self._initial_files[path]:
                modified += 1

        # Check for deleted
        for path in self._initial_files:
            if path not in current_files:
                deleted += 1

        return modified, created, deleted

    def _parse_session_usage(self) -> tuple[int, int, int, int, float, int, str]:
        """Parse session JSONL for usage since start."""
        input_tokens = 0
        output_tokens = 0
        cache_creation = 0
        cache_read = 0
        cost = 0.0
        tool_calls = 0
        model = "unknown"

        projects_dir = get_claude_projects_dir()
        encoded_path = self.project_path.replace("/", "-")
        session_file = projects_dir / encoded_path / f"{self.session_id}.jsonl"

        if not session_file.exists():
            return input_tokens, output_tokens, cache_creation, cache_read, cost, tool_calls, model

        with open(session_file, 'r') as f:
            for line in f:
                if not line.strip():
                    continue

                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Check timestamp is after start
                timestamp_str = data.get("timestamp", "")
                if timestamp_str:
                    try:
                        ts = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                        if ts < self.start_time.replace(tzinfo=ts.tzinfo):
                            continue
                    except ValueError:
                        continue

                # Count tool calls
                message = data.get("message", {})
                content = message.get("content", [])
                if isinstance(content, list):
                    tool_calls += sum(
                        1 for c in content
                        if isinstance(c, dict) and c.get("type") == "tool_use"
                    )

                # Extract usage
                usage = message.get("usage", {})
                if usage:
                    input_tokens += usage.get("input_tokens", 0)
                    output_tokens += usage.get("output_tokens", 0)
                    cache_creation += usage.get("cache_creation_input_tokens", 0)
                    cache_read += usage.get("cache_read_input_tokens", 0)

                    # Get model
                    if message.get("model"):
                        model = message["model"]

                # Get cost
                if "costUSD" in data:
                    cost += data["costUSD"]

        # Calculate cost if not provided
        if cost == 0.0 and (input_tokens or output_tokens):
            from ..usage.pricing import calculate_cost
            cost = calculate_cost(model, {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cache_creation_input_tokens": cache_creation,
                "cache_read_input_tokens": cache_read,
            })

        return input_tokens, output_tokens, cache_creation, cache_read, cost, tool_calls, model

    def finalize(self) -> PhaseMetrics:
        """Finalize metrics collection and return results."""
        end_time = datetime.now()

        # Get usage from session
        (
            input_tokens, output_tokens,
            cache_creation, cache_read,
            cost, tool_calls, model
        ) = self._parse_session_usage()

        # Get file changes
        modified, created, deleted = self._calculate_file_changes()

        return PhaseMetrics(
            phase=self.phase,
            task_id=self.task_id,
            session_id=self.session_id,
            start_time=self.start_time,
            end_time=end_time,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_creation_tokens=cache_creation,
            cache_read_tokens=cache_read,
            cost_usd=cost,
            files_modified=modified,
            files_created=created,
            files_deleted=deleted,
            tool_calls=tool_calls,
            model=model,
        )
```

### Display Component

```python
# src/specify_cli/workflow/display.py

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from .metrics import PhaseMetrics

def display_phase_metrics(metrics: PhaseMetrics, console: Console | None = None):
    """Display phase metrics in a formatted panel."""
    if console is None:
        console = Console()

    # Build summary line
    summary_parts = [
        f"[bold green]{metrics.phase.upper()}[/bold green] completed",
    ]

    # Create detail table
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Label", style="dim")
    table.add_column("Value", style="bold")

    table.add_row("Duration", metrics.format_duration())
    table.add_row("Cost", f"${metrics.cost_usd:.2f}")
    table.add_row("Tokens", metrics.format_tokens())
    table.add_row("Files", metrics.format_files())
    table.add_row("Tool Calls", str(metrics.tool_calls))
    table.add_row("Model", metrics.model[:40])

    # Create panel
    panel = Panel(
        table,
        title=" ".join(summary_parts),
        border_style="green",
        padding=(0, 1),
    )

    console.print()
    console.print(panel)
```

### Workflow Integration

Integrate metrics collection into workflow command execution:

```python
# src/specify_cli/workflow/executor.py

from contextlib import contextmanager
from typing import Generator, Optional
from .collector import MetricsCollector
from .display import display_phase_metrics
from .storage import store_phase_metrics

@contextmanager
def collect_phase_metrics(
    phase: str,
    task_id: Optional[str] = None,
    show_on_complete: bool = True,
    store_in_task: bool = True,
) -> Generator[MetricsCollector, None, None]:
    """Context manager for collecting phase metrics.

    Usage:
        with collect_phase_metrics("implement", task_id="task-123") as collector:
            # ... execute phase ...
            pass
        # Metrics displayed and stored automatically
    """
    collector = MetricsCollector(phase=phase, task_id=task_id)

    try:
        yield collector
    finally:
        metrics = collector.finalize()

        if show_on_complete:
            display_phase_metrics(metrics)

        if store_in_task and task_id:
            store_phase_metrics(metrics)
```

### Storage in Task Notes

```python
# src/specify_cli/workflow/storage.py

from .metrics import PhaseMetrics

def store_phase_metrics(metrics: PhaseMetrics):
    """Store phase metrics in task implementation notes."""
    if not metrics.task_id:
        return

    # Format metrics for task notes
    notes_entry = f"""
## Phase Metrics: {metrics.phase}
- **Timestamp**: {metrics.end_time.isoformat() if metrics.end_time else 'N/A'}
- **Duration**: {metrics.format_duration()}
- **Cost**: ${metrics.cost_usd:.2f}
- **Tokens**: {metrics.format_tokens()}
- **Files**: {metrics.format_files()}
- **Model**: {metrics.model}
"""

    # Use backlog.md MCP to append notes
    # This integrates with existing backlog task structure
    try:
        from ..mcp.backlog import task_edit
        task_edit(
            id=metrics.task_id,
            notesAppend=[notes_entry.strip()]
        )
    except Exception as e:
        # Silently fail - metrics display is more important
        pass
```

### CLI Commands for Historical Metrics

```python
# src/specify_cli/commands/metrics.py

import click
from rich.console import Console
from rich.table import Table

@click.group()
def metrics():
    """View workflow execution metrics."""
    pass

@metrics.command()
@click.option("--phase", type=str, help="Filter by phase name")
@click.option("--task", type=str, help="Filter by task ID")
@click.option("--last", type=int, default=10, help="Show last N entries")
@click.option("--label", type=str, multiple=True, help="Filter by task label")
def history(phase, task, last, label):
    """Show historical phase metrics."""
    console = Console()

    # Query metrics from task notes
    # (Implementation would parse task files for metrics sections)

    table = Table(title="Phase Metrics History")
    table.add_column("Date", style="dim")
    table.add_column("Phase", style="cyan")
    table.add_column("Task")
    table.add_column("Duration", justify="right")
    table.add_column("Cost", justify="right")
    table.add_column("Tokens", justify="right")

    # TODO: Populate from parsed task notes

    console.print(table)

@metrics.command()
@click.option("--days", type=int, default=30, help="Days to analyze")
def summary(days):
    """Show aggregate metrics by phase."""
    console = Console()

    table = Table(title=f"Phase Metrics Summary (Last {days} Days)")
    table.add_column("Phase", style="cyan")
    table.add_column("Count", justify="right")
    table.add_column("Avg Duration", justify="right")
    table.add_column("Avg Cost", justify="right")
    table.add_column("Total Cost", justify="right")

    # Phases in workflow order
    phases = ["assess", "specify", "research", "plan", "implement", "validate", "operate"]

    for phase in phases:
        # TODO: Aggregate metrics from task notes
        table.add_row(
            phase,
            "0",
            "0s",
            "$0.00",
            "$0.00"
        )

    console.print(table)
```

## Configuration

```yaml
# flowspec_workflow.yml (additions)

metrics:
  # Display metrics after each workflow phase
  display_on_complete: true

  # Store metrics in task implementation notes
  store_in_task_notes: true

  # Include these metrics in display
  show_duration: true
  show_cost: true
  show_tokens: true
  show_files: true
  show_tool_calls: true
  show_model: true
```

## File Structure

```
src/specify_cli/
├── workflow/
│   ├── __init__.py
│   ├── metrics.py      # PhaseMetrics data class
│   ├── collector.py    # MetricsCollector
│   ├── display.py      # Rich display formatting
│   ├── storage.py      # Task notes storage
│   └── executor.py     # Context manager integration
└── commands/
    └── metrics.py      # CLI commands
```

## Testing Strategy

### Unit Tests
```python
# tests/test_metrics.py

def test_phase_metrics_duration_format():
    metrics = PhaseMetrics(
        phase="implement",
        session_id="test",
        start_time=datetime(2025, 1, 1, 10, 0, 0),
        end_time=datetime(2025, 1, 1, 10, 5, 30),
    )
    assert metrics.format_duration() == "5m 30s"

def test_phase_metrics_token_format():
    metrics = PhaseMetrics(
        phase="implement",
        session_id="test",
        start_time=datetime.now(),
        input_tokens=10000,
        output_tokens=5000,
    )
    assert "15,000" in metrics.format_tokens()

def test_collector_file_changes():
    # Create temp directory with files
    # Run collector
    # Modify files
    # Check change detection
    pass
```

### Integration Tests
- Test with real workflow execution
- Verify metrics appear after phase completion
- Verify task notes updated correctly

## Acceptance Criteria Summary

- [ ] Metrics displayed after each `/flow:*` command
- [ ] Duration formatted readably (Xs, Xm Ys, Xh Ym)
- [ ] Cost calculated and displayed in USD
- [ ] Token breakdown shown (input, output, cache)
- [ ] Files modified/created/deleted counted
- [ ] Tool calls counted
- [ ] Model used displayed
- [ ] Metrics stored in task implementation notes
- [ ] Historical metrics queryable via CLI
- [ ] Can be disabled via configuration
- [ ] Minimal performance overhead (< 500ms)

## Dependencies

- **OP-001**: Uses cost calculation from usage tracking
- **backlog.md**: Uses task edit API for storing metrics
- **rich**: For formatted console output

## Open Questions

1. Should metrics include agent-specific breakdowns?
2. Should we track metrics across session boundaries?
3. How to handle interrupted/failed phases?

## References

- [opcode AgentRunMetrics](https://github.com/winfunc/opcode/blob/main/src-tauri/src/commands/agents.rs#L59-L66)
- [rich Panel documentation](https://rich.readthedocs.io/en/stable/panel.html)
