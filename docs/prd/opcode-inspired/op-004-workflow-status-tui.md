# OP-004: Workflow Status TUI

> **Status**: Draft
> **Priority**: Medium
> **Inspired By**: Kanban board visualization (opcode's visual approach applied to terminal)
> **Dependencies**: backlog.md MCP server

## Executive Summary

Add a terminal-based UI (TUI) for visualizing workflow pipeline status. Unlike opcode's full GUI, this provides a focused, keyboard-driven view of tasks progressing through workflow states. Built with `textual` for rich terminal interfaces.

## Problem Statement

### Current State
- `backlog task list` shows flat list of tasks
- No visual representation of workflow pipeline
- Cannot see task distribution across phases
- Must mentally map task states to workflow stages
- No quick overview of pipeline health

### Desired State
- Visual kanban-style view of workflow pipeline
- See task distribution across all phases
- Quick navigation and status updates
- Keyboard-driven for terminal efficiency
- Real-time updates as tasks progress

## User Stories

### US-1: Developer views pipeline status
**As a** developer
**I want to** see all tasks in a pipeline view
**So that** I can understand work distribution across phases

**Acceptance Criteria**:
- [ ] Columns for each workflow state
- [ ] Tasks shown as cards in columns
- [ ] Task count per column displayed
- [ ] Color coding by priority/labels
- [ ] Scrollable within columns

### US-2: Developer navigates tasks
**As a** developer using the TUI
**I want to** navigate with keyboard
**So that** I can work efficiently in terminal

**Acceptance Criteria**:
- [ ] Arrow keys to move between columns/tasks
- [ ] Enter to view task details
- [ ] `m` to move task to next phase
- [ ] `q` to quit
- [ ] `?` for help

### US-3: Developer updates task from TUI
**As a** developer
**I want to** update task status from the TUI
**So that** I don't need separate commands

**Acceptance Criteria**:
- [ ] Move task between columns
- [ ] Quick status toggle
- [ ] Edit task details in popup
- [ ] Changes persist to backlog.md

### US-4: Developer filters view
**As a** developer with many tasks
**I want to** filter the pipeline view
**So that** I see only relevant tasks

**Acceptance Criteria**:
- [ ] Filter by label
- [ ] Filter by assignee
- [ ] Search by title
- [ ] Show/hide completed tasks

## Technical Design

### Technology Choice: Textual

**Why Textual?**
- Python-native (consistent with flowspec)
- Rich widget library (tables, panels, inputs)
- Async support (for backlog.md updates)
- Modern terminal rendering
- CSS-like styling
- Active development and community

**Alternatives Considered:**
- `rich` alone: Good for static output, limited interactivity
- `urwid`: More complex API, dated feel
- `blessed`: Lower level, more work

### Data Model

```python
# src/specify_cli/tui/models.py

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class Priority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class TaskCard:
    """Task representation for TUI display."""
    id: str
    title: str
    status: str
    priority: Optional[Priority]
    labels: List[str]
    assignee: Optional[str]
    acceptance_criteria_total: int
    acceptance_criteria_done: int

    @property
    def progress_pct(self) -> float:
        if self.acceptance_criteria_total == 0:
            return 0
        return self.acceptance_criteria_done / self.acceptance_criteria_total * 100

    @property
    def short_title(self) -> str:
        """Truncated title for display."""
        max_len = 30
        if len(self.title) <= max_len:
            return self.title
        return self.title[:max_len-3] + "..."

@dataclass
class PipelineColumn:
    """A column in the pipeline view."""
    state: str
    display_name: str
    tasks: List[TaskCard]
    color: str  # CSS color for styling

    @property
    def count(self) -> int:
        return len(self.tasks)
```

### Backlog Integration

```python
# src/specify_cli/tui/data.py

from typing import List, Dict
from .models import TaskCard, PipelineColumn, Priority

# Workflow states from flowspec_workflow.yml
WORKFLOW_STATES = [
    ("To Do", "To Do", "grey"),
    ("Assessed", "Assessed", "blue"),
    ("Specified", "Specified", "cyan"),
    ("Researched", "Research", "purple"),
    ("Planned", "Planned", "yellow"),
    ("In Implementation", "Implement", "orange"),
    ("Validated", "Validated", "green"),
    ("Deployed", "Deployed", "lime"),
    ("Done", "Done", "grey"),
]

async def load_pipeline_data(
    labels: List[str] = None,
    assignee: str = None,
    hide_done: bool = True,
) -> List[PipelineColumn]:
    """Load tasks from backlog.md and organize into pipeline columns."""
    from ..mcp.backlog import task_list

    # Fetch all tasks (with filters if provided)
    tasks = await task_list(
        labels=labels,
        assignee=assignee,
    )

    # Group by status
    tasks_by_status: Dict[str, List[TaskCard]] = {}
    for task in tasks:
        card = TaskCard(
            id=task["id"],
            title=task["title"],
            status=task.get("status", "To Do"),
            priority=Priority(task["priority"]) if task.get("priority") else None,
            labels=task.get("labels", []),
            assignee=task.get("assignee"),
            acceptance_criteria_total=len(task.get("acceptanceCriteria", [])),
            acceptance_criteria_done=sum(
                1 for ac in task.get("acceptanceCriteria", [])
                if ac.get("checked", False)
            ),
        )

        status = card.status
        if status not in tasks_by_status:
            tasks_by_status[status] = []
        tasks_by_status[status].append(card)

    # Build columns
    columns = []
    for state, display, color in WORKFLOW_STATES:
        if hide_done and state == "Done":
            continue

        columns.append(PipelineColumn(
            state=state,
            display_name=display,
            tasks=tasks_by_status.get(state, []),
            color=color,
        ))

    return columns

async def move_task(task_id: str, new_status: str) -> bool:
    """Move a task to a new status."""
    from ..mcp.backlog import task_edit

    try:
        await task_edit(id=task_id, status=new_status)
        return True
    except Exception:
        return False
```

### TUI Application

```python
# src/specify_cli/tui/app.py

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, ListView, ListItem
from textual.containers import Container, Horizontal, Vertical
from textual.binding import Binding
from textual.reactive import reactive
from textual import events

from .models import TaskCard, PipelineColumn
from .data import load_pipeline_data, move_task, WORKFLOW_STATES

class TaskCardWidget(Static):
    """Widget for a single task card."""

    def __init__(self, task: TaskCard, **kwargs):
        super().__init__(**kwargs)
        self.task = task

    def compose(self) -> ComposeResult:
        # Priority indicator
        priority_color = {
            "high": "red",
            "medium": "yellow",
            "low": "blue",
        }.get(self.task.priority.value if self.task.priority else "", "grey")

        yield Static(f"[{priority_color}]●[/] {self.task.id}", classes="task-id")
        yield Static(self.task.short_title, classes="task-title")

        # Progress bar for acceptance criteria
        if self.task.acceptance_criteria_total > 0:
            pct = self.task.progress_pct
            bar = "█" * int(pct / 10) + "░" * (10 - int(pct / 10))
            yield Static(f"[dim]{bar}[/] {pct:.0f}%", classes="task-progress")

        # Labels
        if self.task.labels:
            labels_str = " ".join(f"[{l}]" for l in self.task.labels[:3])
            yield Static(labels_str, classes="task-labels")


class PipelineColumnWidget(Container):
    """Widget for a pipeline column."""

    def __init__(self, column: PipelineColumn, **kwargs):
        super().__init__(**kwargs)
        self.column = column

    def compose(self) -> ComposeResult:
        yield Static(
            f"[bold {self.column.color}]{self.column.display_name}[/] ({self.column.count})",
            classes="column-header"
        )
        yield ListView(
            *[ListItem(TaskCardWidget(task)) for task in self.column.tasks],
            classes="task-list"
        )


class PipelineView(Container):
    """Main pipeline view container."""

    columns = reactive([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._column_widgets = []

    async def on_mount(self):
        await self.refresh_data()

    async def refresh_data(self):
        self.columns = await load_pipeline_data()
        await self.recompose()

    def compose(self) -> ComposeResult:
        with Horizontal(classes="pipeline"):
            for column in self.columns:
                yield PipelineColumnWidget(column, classes="pipeline-column")


class WorkflowStatusApp(App):
    """Workflow Status TUI Application."""

    CSS = """
    .pipeline {
        width: 100%;
        height: 100%;
    }

    .pipeline-column {
        width: 1fr;
        height: 100%;
        border: solid $primary;
        margin: 0 1;
    }

    .column-header {
        text-align: center;
        padding: 1;
        background: $surface;
    }

    .task-list {
        height: 100%;
        overflow-y: auto;
    }

    TaskCardWidget {
        padding: 1;
        margin: 1;
        border: solid $secondary;
    }

    TaskCardWidget:focus {
        border: solid $accent;
    }

    .task-id {
        text-style: dim;
    }

    .task-title {
        text-style: bold;
    }

    .task-progress {
        margin-top: 1;
    }

    .task-labels {
        margin-top: 1;
        text-style: italic;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("?", "help", "Help"),
        Binding("left", "prev_column", "Prev Column", show=False),
        Binding("right", "next_column", "Next Column", show=False),
        Binding("m", "move_task", "Move Task"),
        Binding("enter", "view_task", "View Details"),
        Binding("/", "search", "Search"),
        Binding("f", "filter", "Filter"),
    ]

    current_column = reactive(0)
    current_task = reactive(0)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield PipelineView(id="pipeline")
        yield Footer()

    def action_refresh(self):
        """Refresh pipeline data."""
        pipeline = self.query_one("#pipeline", PipelineView)
        self.run_worker(pipeline.refresh_data())

    def action_prev_column(self):
        """Move to previous column."""
        if self.current_column > 0:
            self.current_column -= 1

    def action_next_column(self):
        """Move to next column."""
        pipeline = self.query_one("#pipeline", PipelineView)
        if self.current_column < len(pipeline.columns) - 1:
            self.current_column += 1

    async def action_move_task(self):
        """Move selected task to next phase."""
        pipeline = self.query_one("#pipeline", PipelineView)
        if not pipeline.columns:
            return

        column = pipeline.columns[self.current_column]
        if not column.tasks:
            return

        task = column.tasks[self.current_task]

        # Find next state
        states = [s[0] for s in WORKFLOW_STATES]
        try:
            current_idx = states.index(column.state)
            if current_idx < len(states) - 1:
                next_state = states[current_idx + 1]
                await move_task(task.id, next_state)
                await pipeline.refresh_data()
                self.notify(f"Moved {task.id} to {next_state}")
        except ValueError:
            pass

    def action_view_task(self):
        """View task details (opens in new screen)."""
        # TODO: Implement task detail screen
        pass

    def action_search(self):
        """Open search input."""
        # TODO: Implement search
        pass

    def action_filter(self):
        """Open filter panel."""
        # TODO: Implement filter panel
        pass


def run_tui():
    """Run the workflow status TUI."""
    app = WorkflowStatusApp()
    app.run()
```

### CLI Integration

```python
# src/specify_cli/commands/status.py

import click
from rich.console import Console

@click.command()
@click.option("--tui", is_flag=True, help="Launch interactive TUI")
@click.option("--simple", is_flag=True, help="Simple text output")
@click.option("--label", multiple=True, help="Filter by label")
@click.option("--assignee", type=str, help="Filter by assignee")
def status(tui, simple, label, assignee):
    """Show workflow pipeline status."""
    if tui:
        from ..tui.app import run_tui
        run_tui()
        return

    # Non-TUI output
    import asyncio
    from ..tui.data import load_pipeline_data

    console = Console()

    columns = asyncio.run(load_pipeline_data(
        labels=list(label) if label else None,
        assignee=assignee,
    ))

    if simple:
        # Simple text output
        for col in columns:
            console.print(f"\n[bold]{col.display_name}[/] ({col.count})")
            for task in col.tasks:
                console.print(f"  - {task.id}: {task.short_title}")
    else:
        # ASCII pipeline view
        from rich.table import Table
        from rich.panel import Panel

        # Build columns
        panels = []
        for col in columns:
            content = "\n".join(
                f"[dim]{t.id}[/] {t.short_title}"
                for t in col.tasks[:5]  # Show first 5
            )
            if col.count > 5:
                content += f"\n[dim]... and {col.count - 5} more[/]"

            panels.append(Panel(
                content or "[dim]No tasks[/]",
                title=f"[bold]{col.display_name}[/] ({col.count})",
                border_style=col.color,
            ))

        # Print horizontally (best effort)
        console.print()
        for panel in panels:
            console.print(panel)
```

## Configuration

```yaml
# flowspec_workflow.yml (additions)

tui:
  # Default view mode: tui or simple
  default_mode: "simple"

  # Columns to show (subset of states)
  visible_states:
    - "To Do"
    - "Assessed"
    - "Specified"
    - "Planned"
    - "In Implementation"
    - "Validated"

  # Hide completed tasks by default
  hide_done: true

  # Refresh interval in seconds (0 = manual only)
  auto_refresh: 0

  # Color scheme
  colors:
    high_priority: "red"
    medium_priority: "yellow"
    low_priority: "blue"
```

## File Structure

```
src/specify_cli/
├── tui/
│   ├── __init__.py
│   ├── models.py       # TaskCard, PipelineColumn
│   ├── data.py         # Backlog data loading
│   ├── app.py          # Textual app
│   └── widgets.py      # Custom widgets
└── commands/
    └── status.py       # CLI command
```

## Dependencies

```toml
# pyproject.toml additions
[project.dependencies]
textual = ">=0.47.0"
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `q` | Quit |
| `r` | Refresh data |
| `?` | Show help |
| `←` / `→` | Navigate columns |
| `↑` / `↓` | Navigate tasks |
| `Enter` | View task details |
| `m` | Move task to next phase |
| `/` | Search |
| `f` | Filter panel |
| `Esc` | Close popup/cancel |

## Testing Strategy

### Unit Tests
- Test data loading from backlog
- Test task card rendering
- Test column organization

### Integration Tests
- Test TUI launches correctly
- Test keyboard navigation
- Test task movement persists

### Manual Testing
- Visual inspection of layout
- Test with various terminal sizes
- Test with large task counts

## Acceptance Criteria Summary

- [ ] `specify status --tui` launches interactive TUI
- [ ] `specify status` shows simple pipeline overview
- [ ] Tasks grouped by workflow state
- [ ] Keyboard navigation between columns/tasks
- [ ] Move task to next phase with `m`
- [ ] View task details with Enter
- [ ] Filter by label with `f`
- [ ] Search tasks with `/`
- [ ] Refresh with `r`
- [ ] Quit with `q`
- [ ] Color coding by priority
- [ ] Acceptance criteria progress shown
- [ ] Task counts per column

## Future Enhancements

1. **Drag-and-drop**: Mouse support for moving tasks
2. **Notifications**: Desktop notifications for task updates
3. **Split view**: Task details alongside pipeline
4. **Time tracking**: Show time in each phase
5. **Metrics panel**: Show cost/token usage per column

## Open Questions

1. Should TUI support multiple projects?
2. Should we cache backlog data for faster startup?
3. Should task detail view allow editing?

## References

- [Textual documentation](https://textual.textualize.io/)
- [Rich library](https://rich.readthedocs.io/)
- [backlog.md MCP](https://github.com/backlog-md/backlog)
