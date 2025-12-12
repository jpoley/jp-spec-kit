# SK-001: Real-time Kanban Dashboard

**Inspired by:** [spec-kitty](https://github.com/Priivacy-ai/spec-kitty) dashboard feature
**Priority:** P1 - High Impact
**Complexity:** High (estimated 2-3 weeks implementation)
**Dependencies:** backlog.md MCP server

---

## 1. Problem Statement

Flowspec users have no visual way to track development progress. Unlike spec-kitty which provides a live kanban dashboard showing task status, agent assignments, and completion metrics in real-time, flowspec users must rely on CLI commands and manual file inspection to understand project state.

**Current Pain Points:**
- No visibility into what agents are working on
- No completion metrics or progress tracking
- Cannot demonstrate progress to stakeholders
- Bottlenecks are invisible until manually discovered
- Multi-feature projects have no overview

**Why This Matters:**
- Engineering managers can't coordinate multiple AI agents
- Solo developers lose context across long sessions
- Agencies can't show clients live development progress
- Teams can't identify stuck or blocked tasks

---

## 2. Solution Overview

Build a real-time dashboard that visualizes backlog.md tasks using flowspec's existing state machine model. Unlike spec-kitty which uses simple 4-lane kanban, flowspec's dashboard will leverage the richer 9-state model and acceptance criteria tracking.

### Key Differentiators from Spec-Kitty

| Aspect | Spec-Kitty | Flowspec Dashboard |
|--------|-----------|-------------------|
| Data Source | File system scan (`tasks/` dirs) | Backlog.md via MCP |
| States | 4 lanes (Planned/Doing/Review/Done) | 9 states from workflow config |
| Progress | Task count only | AC completion % + task count |
| Task Metadata | Frontmatter parsing | Rich backlog.md fields |
| Updates | Filesystem polling | WebSocket + MCP events |

### Architecture Decision: Backlog.md Integration

**Backlog.md stays.** It is MORE sophisticated than spec-kitty's approach:
- MCP server integration (AI-native access)
- Acceptance criteria with progressive tracking
- Dependencies between tasks
- Labels, filtering, search
- Richer metadata

The dashboard READS from backlog.md - it does not replace it.

---

## 3. User Stories

### US-1: View Project Dashboard
**As a** developer using flowspec
**I want to** see a visual kanban board of all tasks
**So that** I can understand project progress at a glance

**Acceptance Criteria:**
- [ ] Dashboard accessible via `specify dashboard` command
- [ ] Dashboard accessible via `/flow:dashboard` slash command
- [ ] Shows all tasks from backlog.md grouped by state
- [ ] Auto-refreshes at least every 2 seconds
- [ ] Works in browser at `http://localhost:<port>`

### US-2: Track Acceptance Criteria Progress
**As a** developer working on a feature
**I want to** see AC completion percentage for each task
**So that** I know how close tasks are to completion

**Acceptance Criteria:**
- [ ] Each task card shows `X/Y ACs completed (Z%)`
- [ ] Progress bar visualization
- [ ] ACs visible in task detail view
- [ ] Clicking task expands to show full AC list

### US-3: Filter by State
**As a** project manager
**I want to** filter tasks by workflow state
**So that** I can focus on specific stages (e.g., "In Implementation")

**Acceptance Criteria:**
- [ ] Dropdown or tabs for each state from flowspec_workflow.yml
- [ ] Quick filters: "My Tasks", "Blocked", "Ready for Review"
- [ ] URL reflects filter state (shareable links)
- [ ] Filter persists across page refreshes

### US-4: View Agent Assignments
**As a** team lead coordinating multiple AI agents
**I want to** see which agent is assigned to each task
**So that** I can prevent duplicate work and balance load

**Acceptance Criteria:**
- [ ] Agent name displayed on task card (from `assignee` field)
- [ ] Filter by agent/assignee
- [ ] Tasks without assignee visually distinct
- [ ] Agent activity indicator (last update timestamp)

### US-5: Multi-Feature Overview
**As a** developer working on multiple features
**I want to** see all features and their progress
**So that** I can prioritize and context-switch effectively

**Acceptance Criteria:**
- [ ] Feature selector dropdown
- [ ] Summary view showing all features with completion %
- [ ] Click feature to drill into its tasks
- [ ] Feature labels from task metadata

### US-6: Background Dashboard Lifecycle
**As a** developer
**I want** the dashboard to start automatically and run in background
**So that** I don't have to manage it manually

**Acceptance Criteria:**
- [ ] `specify init` optionally starts dashboard
- [ ] Dashboard runs as background process
- [ ] `specify dashboard --kill` stops it
- [ ] `specify dashboard` opens existing or starts new
- [ ] Port auto-detection (start at 9237, find free port)

---

## 4. Technical Design

### 4.1 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Browser (Dashboard UI)                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  React/Preact SPA (or vanilla JS for simplicity)          │  │
│  │  - Kanban board component                                  │  │
│  │  - Task card component                                     │  │
│  │  - Filter/search bar                                       │  │
│  │  - Feature selector                                        │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │ WebSocket / Polling
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Dashboard HTTP Server (Python)                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  HTTPServer + Custom Router                                │  │
│  │  Endpoints:                                                 │  │
│  │    GET /                    → Dashboard HTML               │  │
│  │    GET /api/tasks           → All tasks JSON               │  │
│  │    GET /api/tasks/:id       → Single task detail           │  │
│  │    GET /api/features        → Feature summary              │  │
│  │    GET /api/health          → Health check                 │  │
│  │    GET /api/workflow-config → States from YAML             │  │
│  │    POST /api/shutdown       → Graceful shutdown            │  │
│  │    WebSocket /ws/updates    → Real-time events (optional)  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Layer (Backlog.md)                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Option A: Direct File Access                              │  │
│  │    - Parse backlog/tasks/*.md files directly               │  │
│  │    - Watch for filesystem changes (watchdog)               │  │
│  │                                                             │  │
│  │  Option B: MCP Server Integration                          │  │
│  │    - Use existing backlog MCP server                       │  │
│  │    - Call mcp__backlog__task_list for data                 │  │
│  │    - Subscribe to MCP events for updates                   │  │
│  │                                                             │  │
│  │  RECOMMENDED: Option A for simplicity, B for future        │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 flowspec_workflow.yml                            │
│  - States configuration                                          │
│  - Workflow transitions                                          │
│  - Role-based namespaces                                         │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 File Structure

```
src/specify_cli/dashboard/
├── __init__.py           # Module exports
├── server.py             # HTTP server bootstrap, port detection
├── lifecycle.py          # Start/stop/background process management
├── scanner.py            # Backlog.md task scanner
├── workflow_config.py    # Parse flowspec_workflow.yml for states
├── handlers/
│   ├── __init__.py
│   ├── base.py           # Base HTTP handler
│   ├── router.py         # URL routing
│   ├── api.py            # JSON API endpoints
│   ├── static.py         # Static file serving
│   └── websocket.py      # WebSocket handler (optional)
├── templates/
│   ├── __init__.py
│   └── dashboard.html    # Main HTML template
└── static/
    ├── css/
    │   └── dashboard.css
    └── js/
        └── dashboard.js   # Kanban board JS
```

### 4.3 API Endpoints

#### GET /api/tasks
Returns all tasks from backlog.md with state grouping:

```json
{
  "tasks": [
    {
      "id": "task-42",
      "title": "Implement user authentication",
      "status": "In Implementation",
      "priority": "high",
      "assignee": ["@backend-engineer"],
      "labels": ["backend", "security"],
      "acceptance_criteria": {
        "total": 5,
        "completed": 3,
        "percentage": 60
      },
      "dependencies": ["task-41"],
      "created_at": "2025-12-10T10:00:00Z",
      "updated_at": "2025-12-12T14:30:00Z"
    }
  ],
  "by_state": {
    "To Do": [...],
    "Assessed": [...],
    "Specified": [...],
    "In Implementation": [...],
    ...
  },
  "summary": {
    "total": 25,
    "by_state": {
      "To Do": 5,
      "In Implementation": 8,
      "Done": 12
    },
    "completion_percentage": 48
  }
}
```

#### GET /api/workflow-config
Returns states from flowspec_workflow.yml:

```json
{
  "states": [
    "To Do",
    "Assessed",
    "Specified",
    "Researched",
    "Planned",
    "In Implementation",
    "Validated",
    "Deployed",
    "Done"
  ],
  "transitions": [...],
  "roles": {...}
}
```

### 4.4 Scanner Implementation

```python
# src/specify_cli/dashboard/scanner.py

from pathlib import Path
from typing import Dict, List, Any
import yaml
import re

def scan_backlog_tasks(project_dir: Path) -> List[Dict[str, Any]]:
    """
    Scan backlog/tasks/*.md for task data.

    Backlog.md format:
    ---
    id: task-42
    title: Implement feature X
    status: In Implementation
    priority: high
    assignee:
      - @backend-engineer
    labels:
      - backend
    dependencies:
      - task-41
    ---

    ## Acceptance Criteria
    - [x] AC 1 complete
    - [ ] AC 2 pending
    - [ ] AC 3 pending
    """
    tasks = []
    tasks_dir = project_dir / "backlog" / "tasks"

    if not tasks_dir.exists():
        return tasks

    for task_file in tasks_dir.glob("*.md"):
        content = task_file.read_text(encoding="utf-8")
        task = parse_task_file(content, task_file.stem)
        if task:
            tasks.append(task)

    return tasks

def parse_task_file(content: str, task_id: str) -> Dict[str, Any]:
    """Parse a single task file into structured data."""
    # Parse YAML frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if not frontmatter_match:
        return None

    frontmatter = yaml.safe_load(frontmatter_match.group(1))
    body = content[frontmatter_match.end():]

    # Parse acceptance criteria
    ac_total = 0
    ac_completed = 0
    for line in body.split('\n'):
        if re.match(r'^- \[[ x]\]', line):
            ac_total += 1
            if re.match(r'^- \[x\]', line, re.IGNORECASE):
                ac_completed += 1

    return {
        "id": frontmatter.get("id", task_id),
        "title": frontmatter.get("title", "Untitled"),
        "status": frontmatter.get("status", "To Do"),
        "priority": frontmatter.get("priority", "medium"),
        "assignee": frontmatter.get("assignee", []),
        "labels": frontmatter.get("labels", []),
        "dependencies": frontmatter.get("dependencies", []),
        "acceptance_criteria": {
            "total": ac_total,
            "completed": ac_completed,
            "percentage": int(ac_completed / ac_total * 100) if ac_total > 0 else 0
        }
    }
```

### 4.5 CLI Integration

```python
# Addition to src/specify_cli/cli/commands/dashboard.py

import typer
from pathlib import Path
from ..dashboard.server import find_free_port, start_dashboard
from ..dashboard.lifecycle import kill_dashboard, get_dashboard_status

app = typer.Typer()

@app.command()
def dashboard(
    port: int = typer.Option(None, help="Preferred port (auto-detect if unavailable)"),
    kill: bool = typer.Option(False, "--kill", help="Stop running dashboard"),
    background: bool = typer.Option(True, "--background/--foreground", help="Run in background"),
):
    """Open or manage the flowspec dashboard."""
    project_dir = Path.cwd()

    if kill:
        kill_dashboard(project_dir)
        typer.echo("Dashboard stopped.")
        return

    status = get_dashboard_status(project_dir)
    if status.get("running"):
        typer.echo(f"Dashboard already running at http://localhost:{status['port']}")
        # Open in browser
        import webbrowser
        webbrowser.open(f"http://localhost:{status['port']}")
        return

    actual_port, pid = start_dashboard(
        project_dir=project_dir,
        port=port,
        background_process=background
    )

    typer.echo(f"Dashboard started at http://localhost:{actual_port}")
    if pid:
        typer.echo(f"Background process PID: {pid}")

    # Open in browser
    import webbrowser
    webbrowser.open(f"http://localhost:{actual_port}")
```

### 4.6 Slash Command

Create `.claude/commands/flow/dashboard.md`:

```markdown
---
description: Open the flowspec real-time kanban dashboard
---

# /flow:dashboard

Open the flowspec dashboard to visualize task progress.

## Actions

1. Check if dashboard is already running
2. If not, start it on an available port
3. Open the dashboard URL in the default browser
4. Report the URL for manual access

## Usage

```bash
specify dashboard           # Start/open dashboard
specify dashboard --kill    # Stop dashboard
specify dashboard --port 4000  # Prefer specific port
```

## What You'll See

- Kanban board with tasks grouped by workflow state
- Acceptance criteria completion percentages
- Agent assignments and task priorities
- Filter by state, label, or assignee
- Multi-feature overview
```

---

## 5. Implementation Plan

### Phase 1: Core Server (Week 1)
1. Create `src/specify_cli/dashboard/` module structure
2. Implement HTTP server with port detection
3. Implement backlog.md scanner
4. Create basic HTML template with inline CSS/JS
5. API endpoints: `/api/tasks`, `/api/health`

### Phase 2: UI Components (Week 2)
1. Kanban board layout (CSS Grid or Flexbox)
2. Task card component with AC progress
3. State column headers from workflow config
4. Polling-based auto-refresh (2s interval)
5. Task detail modal/drawer

### Phase 3: Advanced Features (Week 3)
1. Filter by state, assignee, label
2. Feature selector for multi-feature projects
3. WebSocket support for instant updates (optional)
4. Background process management
5. CLI command integration

### Phase 4: Polish & Testing
1. E2E tests for dashboard
2. Performance optimization
3. Documentation
4. Browser compatibility testing

---

## 6. Success Metrics

| Metric | Target |
|--------|--------|
| Dashboard load time | < 1 second |
| Auto-refresh interval | 2 seconds |
| Task render time | < 100ms per task |
| Memory footprint | < 50MB |
| Browser support | Chrome, Firefox, Safari, Edge (latest) |

---

## 7. Out of Scope (Future Enhancements)

- Task editing from dashboard (read-only v1)
- Drag-and-drop state changes
- Time tracking / burndown charts
- Team collaboration features
- Mobile-responsive design (desktop-first v1)
- Dark mode (system preference detection v2)

---

## 8. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Backlog.md format changes | Low | High | Abstract scanner, version detection |
| Performance with many tasks | Medium | Medium | Pagination, virtual scrolling |
| Port conflicts | Low | Low | Auto-port detection (like spec-kitty) |
| Browser compatibility | Low | Medium | Use vanilla JS, minimal dependencies |

---

## 9. References

- [spec-kitty dashboard implementation](https://github.com/Priivacy-ai/spec-kitty/tree/main/src/specify_cli/dashboard)
- [spec-kitty scanner.py](https://github.com/Priivacy-ai/spec-kitty/blob/main/src/specify_cli/dashboard/scanner.py)
- [backlog.md MCP server](./backlog/)
- [flowspec_workflow.yml](../../flowspec_workflow.yml)

---

## 10. Appendix: Spec-Kitty Dashboard Analysis

Spec-kitty's dashboard strengths to preserve:
- Auto-port detection starting from 9237
- Background process with daemon mode
- Simple HTTP server (no heavy frameworks)
- Real-time filesystem scanning
- Clean kanban UI with task cards

Improvements for flowspec:
- Use backlog.md instead of file directories
- Support 9 states instead of 4 lanes
- Show AC completion percentages
- Integrate with workflow state machine
- WebSocket for instant updates (optional)
