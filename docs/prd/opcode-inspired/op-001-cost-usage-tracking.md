# OP-001: Cost/Usage Tracking System

> **Status**: Draft
> **Priority**: High
> **Inspired By**: [opcode/src-tauri/src/commands/usage.rs](https://github.com/winfunc/opcode/blob/main/src-tauri/src/commands/usage.rs)
> **Dependencies**: None (standalone feature)

## Executive Summary

Add comprehensive cost and usage tracking to flowspec by parsing Claude Code's JSONL session files. This enables developers to understand API spend per task, per workflow phase, per project, and over time.

## Problem Statement

### Current State
- Developers have no visibility into Claude Code API costs
- No way to know how much a task or workflow phase costs
- No budget awareness or spending alerts
- Cannot optimize workflow for cost efficiency
- Team leads cannot estimate costs for similar future work

### Desired State
- Real-time cost tracking integrated into workflow commands
- Historical cost data queryable via CLI
- Cost attribution to tasks in backlog.md
- Budget configuration with warnings
- Cost visibility without leaving the terminal

## User Stories

### US-1: Developer views session costs
**As a** developer
**I want to** see how much my current session has cost
**So that** I can be aware of my API spend in real-time

**Acceptance Criteria**:
- [ ] `specify usage` command shows current session cost
- [ ] Displays input/output/cache token breakdown
- [ ] Shows cost in USD with model pricing applied
- [ ] Works without any configuration

### US-2: Developer views task costs
**As a** developer working on a backlog task
**I want to** see how much that specific task has cost
**So that** I can track spend per feature

**Acceptance Criteria**:
- [ ] `specify usage --task TASK-123` shows cost for specific task
- [ ] Cost aggregated across all sessions mentioning that task
- [ ] Shows cost breakdown by workflow phase
- [ ] Integrates with backlog.md task metadata

### US-3: Team lead views project costs
**As a** team lead
**I want to** see total costs by project and time range
**So that** I can budget for AI-assisted development

**Acceptance Criteria**:
- [ ] `specify usage --project` shows costs for current project
- [ ] `specify usage --days 30` shows last 30 days of costs
- [ ] `specify usage --since 2025-01-01` shows costs from date
- [ ] Export to CSV/JSON for accounting

### US-4: Developer sees phase costs in workflow output
**As a** developer running `/flow:implement`
**I want to** see cost metrics when the phase completes
**So that** I understand phase-level costs without extra commands

**Acceptance Criteria**:
- [ ] Each `/flow:*` command shows cost summary on completion
- [ ] Format: `Cost: $X.XX (input: N, output: M, cache: K tokens)`
- [ ] Duration also displayed
- [ ] Can be disabled via config

## Technical Design

### Data Source

Claude Code stores session data in JSONL format:
```
~/.claude/projects/{encoded-project-path}/{session-id}.jsonl
```

Each line is a JSON object. Usage data is in assistant messages:
```json
{
  "type": "assistant",
  "timestamp": "2025-12-12T15:30:00Z",
  "message": {
    "model": "claude-sonnet-4-20250514",
    "usage": {
      "input_tokens": 15234,
      "output_tokens": 4521,
      "cache_creation_input_tokens": 8000,
      "cache_read_input_tokens": 12000
    }
  },
  "costUSD": 0.0847
}
```

### Pricing Model

Reference: [opcode pricing constants](https://github.com/winfunc/opcode/blob/main/src-tauri/src/commands/usage.rs#L66-L76)

```python
# src/specify_cli/usage/pricing.py

PRICING = {
    # Claude 4 Opus
    "claude-opus-4": {
        "input": 15.00,           # per million tokens
        "output": 75.00,
        "cache_write": 18.75,
        "cache_read": 1.50,
    },
    # Claude 4 Sonnet
    "claude-sonnet-4": {
        "input": 3.00,
        "output": 15.00,
        "cache_write": 3.75,
        "cache_read": 0.30,
    },
    # Claude 3.5 Sonnet (legacy)
    "claude-3-5-sonnet": {
        "input": 3.00,
        "output": 15.00,
        "cache_write": 3.75,
        "cache_read": 0.30,
    },
    # Haiku (for subagents)
    "claude-3-5-haiku": {
        "input": 0.80,
        "output": 4.00,
        "cache_write": 1.00,
        "cache_read": 0.08,
    },
}

def calculate_cost(model: str, usage: dict) -> float:
    """Calculate cost in USD for a usage record."""
    pricing = get_pricing_for_model(model)
    if not pricing:
        return 0.0  # Unknown model, don't guess

    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)
    cache_create = usage.get("cache_creation_input_tokens", 0)
    cache_read = usage.get("cache_read_input_tokens", 0)

    cost = (
        (input_tokens * pricing["input"] / 1_000_000) +
        (output_tokens * pricing["output"] / 1_000_000) +
        (cache_create * pricing["cache_write"] / 1_000_000) +
        (cache_read * pricing["cache_read"] / 1_000_000)
    )
    return round(cost, 6)

def get_pricing_for_model(model: str) -> dict | None:
    """Match model string to pricing tier."""
    model_lower = model.lower()
    for key, pricing in PRICING.items():
        if key in model_lower:
            return pricing
    return None
```

### JSONL Parser

```python
# src/specify_cli/usage/parser.py

from pathlib import Path
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Iterator

@dataclass
class UsageEntry:
    timestamp: datetime
    session_id: str
    project_path: str
    model: str
    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int
    cache_read_tokens: int
    cost_usd: float
    message_id: str | None = None
    request_id: str | None = None

def parse_jsonl_file(path: Path, project_path: str) -> Iterator[UsageEntry]:
    """Parse a JSONL session file for usage entries."""
    session_id = path.stem
    seen_hashes = set()  # Deduplication

    with open(path, 'r') as f:
        for line in f:
            if not line.strip():
                continue

            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Only process assistant messages with usage
            message = data.get("message", {})
            usage = message.get("usage")
            if not usage:
                continue

            # Skip entries without meaningful tokens
            if all(usage.get(k, 0) == 0 for k in [
                "input_tokens", "output_tokens",
                "cache_creation_input_tokens", "cache_read_input_tokens"
            ]):
                continue

            # Deduplication by message_id + request_id
            msg_id = message.get("id", "")
            req_id = data.get("requestId", "")
            if msg_id and req_id:
                hash_key = f"{msg_id}:{req_id}"
                if hash_key in seen_hashes:
                    continue
                seen_hashes.add(hash_key)

            # Calculate cost if not provided
            model = message.get("model", "unknown")
            cost = data.get("costUSD") or calculate_cost(model, usage)

            yield UsageEntry(
                timestamp=datetime.fromisoformat(data.get("timestamp", "").replace("Z", "+00:00")),
                session_id=session_id,
                project_path=project_path,
                model=model,
                input_tokens=usage.get("input_tokens", 0),
                output_tokens=usage.get("output_tokens", 0),
                cache_creation_tokens=usage.get("cache_creation_input_tokens", 0),
                cache_read_tokens=usage.get("cache_read_input_tokens", 0),
                cost_usd=cost,
                message_id=msg_id,
                request_id=req_id,
            )

def get_claude_projects_dir() -> Path:
    """Get the Claude projects directory."""
    return Path.home() / ".claude" / "projects"

def iter_all_usage_entries(
    project_filter: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
) -> Iterator[UsageEntry]:
    """Iterate all usage entries with optional filters."""
    projects_dir = get_claude_projects_dir()
    if not projects_dir.exists():
        return

    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue

        # Decode project path from directory name
        project_path = project_dir.name.replace("-", "/")

        if project_filter and project_filter not in project_path:
            continue

        # Find all JSONL files (including in subdirectories)
        for jsonl_file in project_dir.rglob("*.jsonl"):
            for entry in parse_jsonl_file(jsonl_file, project_path):
                if since and entry.timestamp < since:
                    continue
                if until and entry.timestamp > until:
                    continue
                yield entry
```

### Usage Statistics

```python
# src/specify_cli/usage/stats.py

from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime, date

@dataclass
class UsageStats:
    total_cost: float = 0.0
    total_tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_tokens: int = 0
    cache_read_tokens: int = 0
    session_count: int = 0
    by_model: dict = field(default_factory=dict)
    by_date: dict = field(default_factory=dict)
    by_project: dict = field(default_factory=dict)

    def add_entry(self, entry: UsageEntry):
        self.total_cost += entry.cost_usd
        self.input_tokens += entry.input_tokens
        self.output_tokens += entry.output_tokens
        self.cache_creation_tokens += entry.cache_creation_tokens
        self.cache_read_tokens += entry.cache_read_tokens
        self.total_tokens = (
            self.input_tokens + self.output_tokens +
            self.cache_creation_tokens + self.cache_read_tokens
        )
        self.session_count += 1

        # By model
        if entry.model not in self.by_model:
            self.by_model[entry.model] = {"cost": 0.0, "tokens": 0, "count": 0}
        self.by_model[entry.model]["cost"] += entry.cost_usd
        self.by_model[entry.model]["tokens"] += (
            entry.input_tokens + entry.output_tokens
        )
        self.by_model[entry.model]["count"] += 1

        # By date
        date_key = entry.timestamp.date().isoformat()
        if date_key not in self.by_date:
            self.by_date[date_key] = {"cost": 0.0, "tokens": 0}
        self.by_date[date_key]["cost"] += entry.cost_usd
        self.by_date[date_key]["tokens"] += (
            entry.input_tokens + entry.output_tokens
        )

        # By project
        if entry.project_path not in self.by_project:
            self.by_project[entry.project_path] = {
                "cost": 0.0, "tokens": 0, "sessions": set()
            }
        self.by_project[entry.project_path]["cost"] += entry.cost_usd
        self.by_project[entry.project_path]["tokens"] += (
            entry.input_tokens + entry.output_tokens
        )
        self.by_project[entry.project_path]["sessions"].add(entry.session_id)
```

### CLI Commands

```python
# src/specify_cli/commands/usage.py

import click
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table

@click.group()
def usage():
    """View Claude Code usage and costs."""
    pass

@usage.command()
@click.option("--days", type=int, help="Show last N days")
@click.option("--since", type=str, help="Show since date (YYYY-MM-DD)")
@click.option("--until", type=str, help="Show until date (YYYY-MM-DD)")
@click.option("--project", type=str, help="Filter by project path")
@click.option("--task", type=str, help="Filter by task ID (searches session content)")
@click.option("--format", type=click.Choice(["table", "json", "csv"]), default="table")
def stats(days, since, until, project, task, format):
    """Show usage statistics."""
    console = Console()

    # Parse date filters
    since_dt = None
    until_dt = None
    if days:
        since_dt = datetime.now() - timedelta(days=days)
    if since:
        since_dt = datetime.fromisoformat(since)
    if until:
        until_dt = datetime.fromisoformat(until)

    # Collect stats
    stats = UsageStats()
    for entry in iter_all_usage_entries(
        project_filter=project,
        since=since_dt,
        until=until_dt,
    ):
        stats.add_entry(entry)

    if format == "json":
        console.print_json(data=asdict(stats))
        return

    if format == "csv":
        # CSV output for export
        print("date,cost,tokens,sessions")
        for date_key in sorted(stats.by_date.keys()):
            d = stats.by_date[date_key]
            print(f"{date_key},{d['cost']:.4f},{d['tokens']},1")
        return

    # Table output
    console.print(f"\n[bold]Total Cost:[/bold] ${stats.total_cost:.2f}")
    console.print(f"[bold]Total Tokens:[/bold] {stats.total_tokens:,}")
    console.print(f"[bold]Sessions:[/bold] {stats.session_count:,}\n")

    # Token breakdown
    breakdown = Table(title="Token Breakdown")
    breakdown.add_column("Type", style="cyan")
    breakdown.add_column("Tokens", justify="right")
    breakdown.add_row("Input", f"{stats.input_tokens:,}")
    breakdown.add_row("Output", f"{stats.output_tokens:,}")
    breakdown.add_row("Cache Creation", f"{stats.cache_creation_tokens:,}")
    breakdown.add_row("Cache Read", f"{stats.cache_read_tokens:,}")
    console.print(breakdown)

    # By model
    if stats.by_model:
        model_table = Table(title="\nBy Model")
        model_table.add_column("Model", style="cyan")
        model_table.add_column("Cost", justify="right")
        model_table.add_column("Tokens", justify="right")
        for model, data in sorted(stats.by_model.items(), key=lambda x: -x[1]["cost"]):
            model_table.add_row(
                model[:40],
                f"${data['cost']:.2f}",
                f"{data['tokens']:,}"
            )
        console.print(model_table)

    # By project
    if stats.by_project:
        proj_table = Table(title="\nBy Project")
        proj_table.add_column("Project", style="cyan")
        proj_table.add_column("Cost", justify="right")
        proj_table.add_column("Sessions", justify="right")
        for proj, data in sorted(stats.by_project.items(), key=lambda x: -x[1]["cost"]):
            proj_table.add_row(
                proj.split("/")[-1][:30],
                f"${data['cost']:.2f}",
                str(len(data['sessions']))
            )
        console.print(proj_table)

@usage.command()
@click.option("--days", type=int, default=7, help="Number of days to show")
def daily(days):
    """Show daily usage breakdown."""
    console = Console()
    since = datetime.now() - timedelta(days=days)

    stats = UsageStats()
    for entry in iter_all_usage_entries(since=since):
        stats.add_entry(entry)

    table = Table(title=f"Daily Usage (Last {days} Days)")
    table.add_column("Date", style="cyan")
    table.add_column("Cost", justify="right")
    table.add_column("Tokens", justify="right")

    for date_key in sorted(stats.by_date.keys(), reverse=True):
        data = stats.by_date[date_key]
        table.add_row(
            date_key,
            f"${data['cost']:.2f}",
            f"{data['tokens']:,}"
        )

    console.print(table)
    console.print(f"\n[bold]Total:[/bold] ${stats.total_cost:.2f}")
```

### Integration with Workflow Commands

After each `/flow:*` command completes, display metrics:

```python
# src/specify_cli/workflow/metrics.py

from dataclasses import dataclass
from datetime import datetime

@dataclass
class PhaseMetrics:
    start_time: datetime
    end_time: datetime | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    cache_tokens: int = 0
    cost_usd: float = 0.0
    files_modified: int = 0

    @property
    def duration_seconds(self) -> float:
        if not self.end_time:
            return 0
        return (self.end_time - self.start_time).total_seconds()

    def format_summary(self) -> str:
        """Format metrics for display."""
        duration = self.duration_seconds
        if duration < 60:
            duration_str = f"{duration:.0f}s"
        else:
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            duration_str = f"{minutes}m {seconds}s"

        return (
            f"Duration: {duration_str} | "
            f"Cost: ${self.cost_usd:.2f} | "
            f"Tokens: {self.input_tokens + self.output_tokens:,} "
            f"(in: {self.input_tokens:,}, out: {self.output_tokens:,})"
        )

class MetricsCollector:
    """Collect metrics during workflow execution."""

    def __init__(self):
        self.metrics = PhaseMetrics(start_time=datetime.now())
        self._session_start = datetime.now()

    def finalize(self) -> PhaseMetrics:
        """Finalize metrics collection."""
        self.metrics.end_time = datetime.now()

        # Parse session JSONL for usage since start
        # (Implementation would query current session)

        return self.metrics
```

### Backlog.md Integration

Store cost metadata on tasks:

```markdown
<!-- backlog/tasks/task-123.md -->
# Task-123: Implement user authentication

**Status**: Done
**Labels**: backend, security

## Cost Tracking
- **Total Cost**: $4.27
- **Phase Costs**:
  - specify: $0.45
  - plan: $1.12
  - implement: $2.70
- **Sessions**: 3
- **Last Updated**: 2025-12-12T15:30:00Z

## Description
...
```

The backlog.md MCP server would expose:
- `task_get_cost(task_id)` - Get cost for a task
- `task_add_cost(task_id, phase, cost)` - Record phase cost

## File Structure

```
src/specify_cli/
├── usage/
│   ├── __init__.py
│   ├── pricing.py      # Model pricing constants
│   ├── parser.py       # JSONL parsing
│   ├── stats.py        # Statistics aggregation
│   └── display.py      # Rich table formatting
├── commands/
│   └── usage.py        # CLI commands
└── workflow/
    └── metrics.py      # Phase metrics collection
```

## Configuration

```yaml
# flowspec_workflow.yml (additions)

usage:
  # Show cost summary after each workflow command
  show_phase_costs: true

  # Pricing overrides (if using non-standard pricing)
  pricing_overrides: {}

  # Cost tracking in task metadata
  track_task_costs: true
```

## Testing Strategy

### Unit Tests
- `test_pricing.py`: Pricing calculations for all models
- `test_parser.py`: JSONL parsing with edge cases
- `test_stats.py`: Statistics aggregation

### Integration Tests
- Test with real Claude session files
- Test backlog.md cost updates
- Test workflow phase metrics

### Test Data
```python
# tests/fixtures/sample_session.jsonl
{"type":"user","timestamp":"2025-01-01T10:00:00Z","message":{"content":[{"type":"text","text":"Hello"}]}}
{"type":"assistant","timestamp":"2025-01-01T10:00:01Z","message":{"model":"claude-sonnet-4-20250514","usage":{"input_tokens":100,"output_tokens":50}}}
```

## Migration & Rollout

1. **Phase 1**: Core parser and CLI commands (no workflow integration)
2. **Phase 2**: Workflow phase metrics display
3. **Phase 3**: Backlog.md cost tracking integration
4. **Phase 4**: Budget warnings (see OP-005)

## Security Considerations

- JSONL files may contain sensitive prompts/responses
- Cost data is derived only (no new data stored)
- No external API calls for pricing (hardcoded)
- Cost data not sent anywhere (local only)

## Open Questions

1. Should we cache parsed JSONL data for faster repeated queries?
2. Should cost estimates include a disclaimer about accuracy?
3. How to handle sessions that span multiple tasks?

## References

- [opcode usage.rs](https://github.com/winfunc/opcode/blob/main/src-tauri/src/commands/usage.rs) - Reference implementation
- [Claude API Pricing](https://www.anthropic.com/pricing) - Official pricing
- [backlog.md MCP](https://github.com/backlog-md/backlog) - Task management integration
