# OP-005: Cost Budget Warnings

> **Status**: Draft
> **Priority**: Medium
> **Inspired By**: Cost awareness from opcode usage dashboard
> **Dependencies**: OP-001 (Cost/Usage Tracking)

## Executive Summary

Add configurable cost budgets with warnings when thresholds are exceeded. This prevents runaway API spending and enables teams to set cost expectations for tasks and workflow phases.

## Problem Statement

### Current State
- No budget limits or warnings
- Developers unaware of accumulating costs
- Expensive operations run without visibility
- No way to set team-wide cost expectations
- Post-hoc surprise at API bills

### Desired State
- Configurable budgets at multiple levels
- Warnings when approaching/exceeding budgets
- Optional blocking for over-budget operations
- Budget tracking per task and phase
- Clear visibility into budget status

## User Stories

### US-1: Developer warned about high-cost session
**As a** developer
**I want** warnings when my session cost exceeds a threshold
**So that** I can decide whether to continue

**Acceptance Criteria**:
- [ ] Warning displayed when session exceeds budget
- [ ] Shows current cost vs budget
- [ ] Doesn't block by default (warning only)
- [ ] Can configure blocking behavior

### US-2: Team lead sets phase budgets
**As a** team lead
**I want to** set expected budgets per workflow phase
**So that** developers have cost guidance

**Acceptance Criteria**:
- [ ] Budgets configurable in `flowspec_workflow.yml`
- [ ] Different budgets per phase (implement > plan)
- [ ] Warnings when phase exceeds budget
- [ ] Budget reports for planning

### US-3: Developer sees budget status during work
**As a** developer working on a task
**I want to** see budget status without extra commands
**So that** I stay aware of costs

**Acceptance Criteria**:
- [ ] Budget status in workflow output
- [ ] Percentage of budget used shown
- [ ] Color coding (green/yellow/red)
- [ ] Can be disabled for focused work

### US-4: Team tracks budget compliance
**As a** team lead
**I want to** see which tasks exceeded budgets
**So that** I can improve estimates

**Acceptance Criteria**:
- [ ] Report of over-budget tasks
- [ ] Shows actual vs budgeted cost
- [ ] Identifies patterns (which phases exceed)
- [ ] Exportable for review

## Technical Design

### Budget Configuration

```yaml
# flowspec_workflow.yml

budgets:
  # Enable budget tracking
  enabled: true

  # Default currency (for display)
  currency: "USD"

  # Session-level budget (entire Claude Code session)
  session:
    warn_at: 5.00      # Warn when session reaches $5
    block_at: null     # Don't block (null = no limit)

  # Task-level budget (all sessions for a task)
  task:
    warn_at: 10.00     # Warn when task reaches $10
    block_at: 25.00    # Block/confirm at $25

  # Phase-level budgets
  phases:
    assess:
      warn_at: 0.50
      expected: 0.25   # Expected cost for estimation
    specify:
      warn_at: 1.00
      expected: 0.50
    research:
      warn_at: 2.00
      expected: 1.00
    plan:
      warn_at: 2.00
      expected: 1.00
    implement:
      warn_at: 5.00
      expected: 3.00
    validate:
      warn_at: 3.00
      expected: 2.00
    operate:
      warn_at: 1.00
      expected: 0.50

  # Warning behavior
  warnings:
    # Show warning at these percentages of budget
    levels: [50, 75, 90, 100]

    # How to display warnings
    display: "banner"  # banner, inline, popup

    # Allow continuing after budget exceeded
    allow_continue: true

    # Require confirmation at block_at threshold
    require_confirmation: true
```

### Budget Checker

```python
# src/specify_cli/budget/checker.py

from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

class BudgetLevel(Enum):
    OK = "ok"           # Under 50%
    CAUTION = "caution" # 50-75%
    WARNING = "warning" # 75-90%
    CRITICAL = "critical"  # 90-100%
    EXCEEDED = "exceeded"  # Over 100%

@dataclass
class BudgetStatus:
    """Status of a budget."""
    budget_type: str      # "session", "task", "phase"
    budget_name: str      # e.g., "implement" for phase
    current_cost: float
    budget_limit: float
    warn_at: Optional[float]
    block_at: Optional[float]

    @property
    def percentage(self) -> float:
        if self.budget_limit <= 0:
            return 0
        return (self.current_cost / self.budget_limit) * 100

    @property
    def level(self) -> BudgetLevel:
        pct = self.percentage
        if pct >= 100:
            return BudgetLevel.EXCEEDED
        elif pct >= 90:
            return BudgetLevel.CRITICAL
        elif pct >= 75:
            return BudgetLevel.WARNING
        elif pct >= 50:
            return BudgetLevel.CAUTION
        return BudgetLevel.OK

    @property
    def should_warn(self) -> bool:
        if self.warn_at is None:
            return False
        return self.current_cost >= self.warn_at

    @property
    def should_block(self) -> bool:
        if self.block_at is None:
            return False
        return self.current_cost >= self.block_at

    @property
    def remaining(self) -> float:
        return max(0, self.budget_limit - self.current_cost)


class BudgetChecker:
    """Checks costs against configured budgets."""

    def __init__(self, config: dict):
        self.config = config
        self.enabled = config.get("enabled", False)

    def check_session(self, session_cost: float) -> Optional[BudgetStatus]:
        """Check session-level budget."""
        if not self.enabled:
            return None

        session_config = self.config.get("session", {})
        warn_at = session_config.get("warn_at")
        block_at = session_config.get("block_at")

        if warn_at is None and block_at is None:
            return None

        return BudgetStatus(
            budget_type="session",
            budget_name="session",
            current_cost=session_cost,
            budget_limit=warn_at or block_at or 0,
            warn_at=warn_at,
            block_at=block_at,
        )

    def check_task(self, task_id: str, task_cost: float) -> Optional[BudgetStatus]:
        """Check task-level budget."""
        if not self.enabled:
            return None

        task_config = self.config.get("task", {})
        warn_at = task_config.get("warn_at")
        block_at = task_config.get("block_at")

        if warn_at is None and block_at is None:
            return None

        return BudgetStatus(
            budget_type="task",
            budget_name=task_id,
            current_cost=task_cost,
            budget_limit=warn_at or block_at or 0,
            warn_at=warn_at,
            block_at=block_at,
        )

    def check_phase(self, phase: str, phase_cost: float) -> Optional[BudgetStatus]:
        """Check phase-level budget."""
        if not self.enabled:
            return None

        phases_config = self.config.get("phases", {})
        phase_config = phases_config.get(phase, {})

        warn_at = phase_config.get("warn_at")
        block_at = phase_config.get("block_at")
        expected = phase_config.get("expected", warn_at)

        if warn_at is None and block_at is None:
            return None

        return BudgetStatus(
            budget_type="phase",
            budget_name=phase,
            current_cost=phase_cost,
            budget_limit=expected or warn_at or block_at or 0,
            warn_at=warn_at,
            block_at=block_at,
        )

    def get_phase_expected(self, phase: str) -> Optional[float]:
        """Get expected cost for a phase."""
        phases_config = self.config.get("phases", {})
        phase_config = phases_config.get(phase, {})
        return phase_config.get("expected")
```

### Warning Display

```python
# src/specify_cli/budget/display.py

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.prompt import Confirm

from .checker import BudgetStatus, BudgetLevel

LEVEL_COLORS = {
    BudgetLevel.OK: "green",
    BudgetLevel.CAUTION: "yellow",
    BudgetLevel.WARNING: "orange1",
    BudgetLevel.CRITICAL: "red",
    BudgetLevel.EXCEEDED: "bold red",
}

LEVEL_ICONS = {
    BudgetLevel.OK: "✓",
    BudgetLevel.CAUTION: "⚠",
    BudgetLevel.WARNING: "⚠",
    BudgetLevel.CRITICAL: "⚠",
    BudgetLevel.EXCEEDED: "✗",
}

def display_budget_status(
    status: BudgetStatus,
    console: Console | None = None,
    display_mode: str = "banner",
) -> None:
    """Display budget status."""
    if console is None:
        console = Console()

    color = LEVEL_COLORS[status.level]
    icon = LEVEL_ICONS[status.level]

    if display_mode == "inline":
        # Simple inline display
        console.print(
            f"[{color}]{icon} Budget: ${status.current_cost:.2f} / "
            f"${status.budget_limit:.2f} ({status.percentage:.0f}%)[/]"
        )

    elif display_mode == "banner":
        # Banner with progress bar
        content = f"""
[{color}]{icon} {status.budget_type.upper()} BUDGET: {status.budget_name}[/]

Cost:      ${status.current_cost:.2f}
Budget:    ${status.budget_limit:.2f}
Remaining: ${status.remaining:.2f}
"""
        # Create progress bar
        pct = min(status.percentage, 100)
        bar_filled = int(pct / 5)
        bar_empty = 20 - bar_filled
        bar = f"[{color}]{'█' * bar_filled}[/][dim]{'░' * bar_empty}[/]"
        content += f"\n{bar} {status.percentage:.0f}%"

        panel = Panel(
            content,
            title=f"[{color}]Budget Status[/]",
            border_style=color,
        )
        console.print(panel)


def prompt_budget_exceeded(
    status: BudgetStatus,
    console: Console | None = None,
) -> bool:
    """Prompt user to continue after budget exceeded."""
    if console is None:
        console = Console()

    display_budget_status(status, console, display_mode="banner")

    console.print(
        f"\n[bold red]Budget exceeded![/] "
        f"Current cost (${status.current_cost:.2f}) exceeds "
        f"limit (${status.block_at:.2f})."
    )

    return Confirm.ask("Continue anyway?", default=False)


def display_budget_summary(
    statuses: list[BudgetStatus],
    console: Console | None = None,
) -> None:
    """Display summary of multiple budgets."""
    if console is None:
        console = Console()

    from rich.table import Table

    table = Table(title="Budget Summary")
    table.add_column("Type", style="cyan")
    table.add_column("Name")
    table.add_column("Cost", justify="right")
    table.add_column("Budget", justify="right")
    table.add_column("Status")

    for status in statuses:
        color = LEVEL_COLORS[status.level]
        icon = LEVEL_ICONS[status.level]

        table.add_row(
            status.budget_type,
            status.budget_name,
            f"${status.current_cost:.2f}",
            f"${status.budget_limit:.2f}",
            f"[{color}]{icon} {status.percentage:.0f}%[/]",
        )

    console.print(table)
```

### Workflow Integration

```python
# src/specify_cli/workflow/budget_integration.py

from typing import Optional
from ..budget.checker import BudgetChecker, BudgetStatus
from ..budget.display import display_budget_status, prompt_budget_exceeded
from ..usage.parser import iter_all_usage_entries
from datetime import datetime

def check_budgets_before_phase(
    phase: str,
    task_id: Optional[str],
    config: dict,
) -> bool:
    """
    Check budgets before starting a phase.
    Returns True if OK to proceed, False if should abort.
    """
    checker = BudgetChecker(config.get("budgets", {}))
    if not checker.enabled:
        return True

    warnings = []

    # Check task budget if we have a task
    if task_id:
        task_cost = get_task_cost(task_id)
        task_status = checker.check_task(task_id, task_cost)
        if task_status and task_status.should_warn:
            warnings.append(task_status)
            if task_status.should_block:
                if not prompt_budget_exceeded(task_status):
                    return False

    # Show any warnings
    for status in warnings:
        if not status.should_block:
            display_budget_status(status)

    return True


def check_budgets_during_phase(
    phase: str,
    task_id: Optional[str],
    phase_cost: float,
    config: dict,
) -> Optional[BudgetStatus]:
    """
    Check budgets during phase execution.
    Called periodically to show warnings.
    Returns status if warning should be displayed.
    """
    checker = BudgetChecker(config.get("budgets", {}))
    if not checker.enabled:
        return None

    phase_status = checker.check_phase(phase, phase_cost)
    if phase_status and phase_status.should_warn:
        return phase_status

    return None


def get_task_cost(task_id: str) -> float:
    """Get total cost for a task by searching sessions."""
    total_cost = 0.0

    # Search sessions for task mentions
    # This is a heuristic - sessions mentioning the task ID
    for entry in iter_all_usage_entries():
        # Would need session content search
        # For now, return 0 as placeholder
        pass

    return total_cost
```

### CLI Commands

```python
# src/specify_cli/commands/budget.py

import click
from rich.console import Console

@click.group()
def budget():
    """Manage cost budgets."""
    pass

@click.command()
def status():
    """Show current budget status."""
    console = Console()

    from ..budget.checker import BudgetChecker
    from ..budget.display import display_budget_summary
    from ..config import load_workflow_config

    config = load_workflow_config()
    checker = BudgetChecker(config.get("budgets", {}))

    if not checker.enabled:
        console.print("[dim]Budget tracking is disabled[/]")
        return

    # Get current costs
    from ..usage.parser import iter_all_usage_entries
    from datetime import datetime, timedelta

    session_cost = 0.0
    today = datetime.now().date()

    for entry in iter_all_usage_entries(since=datetime.combine(today, datetime.min.time())):
        session_cost += entry.cost_usd

    statuses = []

    session_status = checker.check_session(session_cost)
    if session_status:
        statuses.append(session_status)

    if statuses:
        display_budget_summary(statuses, console)
    else:
        console.print("[green]All budgets OK[/green]")

@click.command()
@click.option("--phase", type=str, help="Show budget for specific phase")
def estimate(phase):
    """Show expected costs for phases."""
    console = Console()

    from rich.table import Table
    from ..config import load_workflow_config

    config = load_workflow_config()
    phases_config = config.get("budgets", {}).get("phases", {})

    table = Table(title="Phase Cost Estimates")
    table.add_column("Phase", style="cyan")
    table.add_column("Expected", justify="right")
    table.add_column("Warn At", justify="right")
    table.add_column("Block At", justify="right")

    phases = ["assess", "specify", "research", "plan", "implement", "validate", "operate"]

    if phase:
        phases = [phase]

    for p in phases:
        p_config = phases_config.get(p, {})
        table.add_row(
            p,
            f"${p_config.get('expected', 0):.2f}",
            f"${p_config.get('warn_at', 0):.2f}" if p_config.get('warn_at') else "-",
            f"${p_config.get('block_at', 0):.2f}" if p_config.get('block_at') else "-",
        )

    console.print(table)

    # Total
    total = sum(
        phases_config.get(p, {}).get('expected', 0)
        for p in phases
    )
    console.print(f"\n[bold]Total Expected:[/bold] ${total:.2f}")

@click.command()
@click.option("--days", type=int, default=30, help="Days to analyze")
def report(days):
    """Show budget compliance report."""
    console = Console()

    from rich.table import Table
    from ..config import load_workflow_config

    config = load_workflow_config()
    phases_config = config.get("budgets", {}).get("phases", {})

    # This would analyze historical data from task notes
    # For now, show placeholder

    console.print(f"[dim]Budget compliance report for last {days} days[/dim]\n")

    table = Table(title="Over-Budget Tasks")
    table.add_column("Task")
    table.add_column("Phase")
    table.add_column("Budgeted", justify="right")
    table.add_column("Actual", justify="right")
    table.add_column("Overage", justify="right")

    # TODO: Populate from task history

    console.print(table)

budget.add_command(status)
budget.add_command(estimate)
budget.add_command(report)
```

## File Structure

```
src/specify_cli/
├── budget/
│   ├── __init__.py
│   ├── checker.py      # BudgetChecker, BudgetStatus
│   ├── display.py      # Warning/status display
│   └── integration.py  # Workflow integration
└── commands/
    └── budget.py       # CLI commands
```

## Testing Strategy

### Unit Tests
```python
# tests/test_budget.py

def test_budget_status_levels():
    status = BudgetStatus(
        budget_type="phase",
        budget_name="implement",
        current_cost=4.50,
        budget_limit=5.00,
        warn_at=4.00,
        block_at=6.00,
    )
    assert status.level == BudgetLevel.CRITICAL
    assert status.percentage == 90.0
    assert status.should_warn == True
    assert status.should_block == False

def test_budget_checker_phase():
    config = {
        "enabled": True,
        "phases": {
            "implement": {"warn_at": 5.00, "block_at": 10.00}
        }
    }
    checker = BudgetChecker(config)
    status = checker.check_phase("implement", 6.00)

    assert status is not None
    assert status.should_warn == True
    assert status.should_block == False
```

## Acceptance Criteria Summary

- [ ] Budgets configurable in `flowspec_workflow.yml`
- [ ] Session-level budget warnings
- [ ] Task-level budget warnings
- [ ] Phase-level budget warnings
- [ ] Warning display at 50%, 75%, 90%, 100%
- [ ] Color-coded budget status (green/yellow/red)
- [ ] Optional blocking at `block_at` threshold
- [ ] Confirmation prompt when budget exceeded
- [ ] `specify budget status` shows current status
- [ ] `specify budget estimate` shows expected costs
- [ ] `specify budget report` shows compliance
- [ ] Budgets shown in workflow phase output

## Security Considerations

- Budget limits are advisory, not security controls
- No sensitive data in budget configuration
- User can always bypass with `--force` flags

## Open Questions

1. Should budgets reset daily/weekly/per-session?
2. How to handle multi-user budgets (team limits)?
3. Should we integrate with billing APIs for real limits?

## References

- [opcode usage dashboard](https://github.com/winfunc/opcode/blob/main/src-tauri/src/commands/usage.rs)
- [Claude API Pricing](https://www.anthropic.com/pricing)
