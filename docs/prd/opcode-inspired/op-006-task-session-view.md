# OP-006: Task-Centric Session View

> **Status**: Draft
> **Priority**: Medium
> **Inspired By**: [opcode session browser](https://github.com/winfunc/opcode/blob/main/src/components/SessionList.tsx)
> **Dependencies**: OP-001 (Cost/Usage Tracking), backlog.md MCP

## Executive Summary

Add the ability to view all Claude Code sessions associated with a backlog task. This bridges the gap between task management (backlog.md) and session history (Claude Code), enabling developers to understand the full conversation history that led to a task's completion.

## Problem Statement

### Current State
- Sessions and tasks are disconnected
- No way to answer "what sessions worked on task-123?"
- Cannot review conversation history for a completed task
- Task context lost after completion
- Cannot resume from a specific task's last session

### Desired State
- View all sessions that touched a task
- See session timeline with cost/duration
- Review conversation snippets per session
- Resume from task's last session
- Export task history for documentation

## User Stories

### US-1: Developer views task sessions
**As a** developer
**I want to** see all sessions associated with a task
**So that** I can understand the work history

**Acceptance Criteria**:
- [ ] `specify task sessions TASK-123` shows session list
- [ ] Each session shows timestamp, duration, cost
- [ ] Sessions ordered chronologically
- [ ] Shows total sessions and total cost

### US-2: Developer reviews session content
**As a** developer reviewing a completed task
**I want to** see conversation snippets from sessions
**So that** I can understand decisions made

**Acceptance Criteria**:
- [ ] Shows user prompts and key responses
- [ ] Indicates tool usage (file edits, commands)
- [ ] Searchable within session
- [ ] Can expand to full conversation

### US-3: Developer resumes from task
**As a** developer returning to a task
**I want to** resume the most recent session
**So that** I maintain context continuity

**Acceptance Criteria**:
- [ ] `specify task resume TASK-123` opens last session
- [ ] Session context is preserved
- [ ] Works with Claude Code's session resume

### US-4: Team documents task history
**As a** team lead documenting a feature
**I want to** export task session history
**So that** I have a record of AI interactions

**Acceptance Criteria**:
- [ ] Export to Markdown format
- [ ] Includes prompts and key responses
- [ ] Includes metrics (cost, duration)
- [ ] Privacy-aware (can redact sensitive content)

## Technical Design

### Task-Session Correlation

Sessions don't explicitly track task IDs. We use heuristics:

1. **Task ID mentions**: Search session JSONL for task ID patterns (`task-123`, `TASK-123`)
2. **Branch names**: Match git branch names to task IDs
3. **Commit messages**: Search for task ID in commits during session
4. **Explicit tracking**: Store task ID when starting work (new feature)

```python
# src/specify_cli/sessions/correlation.py

import re
import json
from pathlib import Path
from typing import List, Set, Optional
from dataclasses import dataclass
from datetime import datetime

from ..usage.parser import get_claude_projects_dir

@dataclass
class SessionInfo:
    """Information about a Claude Code session."""
    session_id: str
    project_path: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    message_count: int
    user_prompt_count: int
    tool_use_count: int
    total_cost: float
    total_tokens: int
    first_prompt: Optional[str]  # First user message (truncated)

@dataclass
class TaskSession:
    """A session associated with a task."""
    session: SessionInfo
    correlation_method: str  # "mention", "branch", "commit", "explicit"
    mention_count: int       # How many times task ID mentioned
    confidence: float        # 0-1 confidence in correlation

# Task ID patterns
TASK_ID_PATTERNS = [
    r'task-\d+',
    r'TASK-\d+',
    r'#\d+',           # GitHub issue style
    r'\[TASK-\d+\]',
]

def find_sessions_for_task(
    task_id: str,
    project_path: Optional[str] = None,
) -> List[TaskSession]:
    """Find all sessions that reference a task ID."""
    results = []
    projects_dir = get_claude_projects_dir()

    if not projects_dir.exists():
        return results

    # Normalize task ID for matching
    task_pattern = re.compile(
        rf'\b{re.escape(task_id)}\b',
        re.IGNORECASE
    )

    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue

        # Filter by project if specified
        if project_path:
            decoded_path = project_dir.name.replace("-", "/")
            if project_path not in decoded_path:
                continue

        # Search all JSONL files
        for jsonl_file in project_dir.rglob("*.jsonl"):
            session_info, mentions = analyze_session_for_task(
                jsonl_file,
                task_pattern,
                project_dir.name,
            )

            if mentions > 0:
                results.append(TaskSession(
                    session=session_info,
                    correlation_method="mention",
                    mention_count=mentions,
                    confidence=min(1.0, mentions * 0.2),  # More mentions = higher confidence
                ))

    # Sort by start time
    results.sort(key=lambda ts: ts.session.start_time or datetime.min)

    return results


def analyze_session_for_task(
    jsonl_path: Path,
    task_pattern: re.Pattern,
    project_name: str,
) -> tuple[SessionInfo, int]:
    """Analyze a session file for task mentions."""
    session_id = jsonl_path.stem
    message_count = 0
    user_prompt_count = 0
    tool_use_count = 0
    total_cost = 0.0
    total_tokens = 0
    mentions = 0
    first_prompt = None
    start_time = None
    end_time = None

    with open(jsonl_path, 'r') as f:
        for line in f:
            if not line.strip():
                continue

            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue

            message_count += 1

            # Track timestamps
            if "timestamp" in data:
                ts = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
                if start_time is None or ts < start_time:
                    start_time = ts
                if end_time is None or ts > end_time:
                    end_time = ts

            # Check for task ID mentions in content
            content_str = json.dumps(data)
            matches = task_pattern.findall(content_str)
            mentions += len(matches)

            # Track user prompts
            if data.get("type") == "user":
                user_prompt_count += 1
                if first_prompt is None:
                    # Extract first user prompt text
                    message = data.get("message", {})
                    content = message.get("content", [])
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and item.get("type") == "text":
                                first_prompt = item.get("text", "")[:100]
                                break

            # Track tool usage
            message = data.get("message", {})
            content = message.get("content", [])
            if isinstance(content, list):
                tool_use_count += sum(
                    1 for c in content
                    if isinstance(c, dict) and c.get("type") == "tool_use"
                )

            # Track usage/cost
            usage = message.get("usage", {})
            if usage:
                total_tokens += usage.get("input_tokens", 0)
                total_tokens += usage.get("output_tokens", 0)

            if "costUSD" in data:
                total_cost += data["costUSD"]

    session_info = SessionInfo(
        session_id=session_id,
        project_path=project_name.replace("-", "/"),
        start_time=start_time,
        end_time=end_time,
        message_count=message_count,
        user_prompt_count=user_prompt_count,
        tool_use_count=tool_use_count,
        total_cost=total_cost,
        total_tokens=total_tokens,
        first_prompt=first_prompt,
    )

    return session_info, mentions
```

### Explicit Task Tracking

When starting work on a task, record the session-task association:

```python
# src/specify_cli/sessions/tracking.py

import json
from pathlib import Path
from datetime import datetime
from typing import Optional

TRACKING_FILE = ".flowspec/session_tasks.json"

def record_task_session(
    task_id: str,
    session_id: str,
    project_path: Optional[Path] = None,
) -> None:
    """Record that a session is working on a task."""
    if project_path is None:
        project_path = Path.cwd()

    tracking_path = project_path / TRACKING_FILE
    tracking_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing
    tracking = {}
    if tracking_path.exists():
        with open(tracking_path) as f:
            tracking = json.load(f)

    # Add entry
    if task_id not in tracking:
        tracking[task_id] = []

    tracking[task_id].append({
        "session_id": session_id,
        "started_at": datetime.now().isoformat(),
    })

    # Save
    with open(tracking_path, 'w') as f:
        json.dump(tracking, f, indent=2)


def get_tracked_sessions(task_id: str, project_path: Optional[Path] = None) -> list[dict]:
    """Get explicitly tracked sessions for a task."""
    if project_path is None:
        project_path = Path.cwd()

    tracking_path = project_path / TRACKING_FILE
    if not tracking_path.exists():
        return []

    with open(tracking_path) as f:
        tracking = json.load(f)

    return tracking.get(task_id, [])
```

### Session Content Extraction

```python
# src/specify_cli/sessions/content.py

import json
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class ConversationTurn:
    """A turn in the conversation."""
    role: str           # "user" or "assistant"
    content: str        # Text content (truncated)
    full_content: str   # Full content
    timestamp: str
    tool_uses: List[str]  # Names of tools used
    cost: Optional[float]
    tokens: Optional[int]

def extract_conversation(
    session_id: str,
    project_path: str,
    max_turns: int = 20,
    truncate_at: int = 500,
) -> List[ConversationTurn]:
    """Extract conversation turns from a session."""
    from ..usage.parser import get_claude_projects_dir

    projects_dir = get_claude_projects_dir()
    encoded_path = project_path.replace("/", "-")
    session_file = projects_dir / encoded_path / f"{session_id}.jsonl"

    if not session_file.exists():
        return []

    turns = []

    with open(session_file, 'r') as f:
        for line in f:
            if not line.strip():
                continue

            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue

            msg_type = data.get("type")
            if msg_type not in ("user", "assistant"):
                continue

            message = data.get("message", {})
            content = message.get("content", [])

            # Extract text content
            text_parts = []
            tool_uses = []

            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict):
                        if item.get("type") == "text":
                            text_parts.append(item.get("text", ""))
                        elif item.get("type") == "tool_use":
                            tool_uses.append(item.get("name", "unknown"))
            elif isinstance(content, str):
                text_parts.append(content)

            full_text = "\n".join(text_parts)
            truncated = full_text[:truncate_at]
            if len(full_text) > truncate_at:
                truncated += "..."

            # Get usage info
            usage = message.get("usage", {})
            tokens = None
            if usage:
                tokens = usage.get("input_tokens", 0) + usage.get("output_tokens", 0)

            turns.append(ConversationTurn(
                role=msg_type,
                content=truncated,
                full_content=full_text,
                timestamp=data.get("timestamp", ""),
                tool_uses=tool_uses,
                cost=data.get("costUSD"),
                tokens=tokens,
            ))

    # Return most recent turns
    return turns[-max_turns:]
```

### CLI Commands

```python
# src/specify_cli/commands/task_sessions.py

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

@click.group("task")
def task_cmd():
    """Task-related commands."""
    pass

@task_cmd.command("sessions")
@click.argument("task_id")
@click.option("--project", type=str, help="Filter by project path")
@click.option("--details", is_flag=True, help="Show detailed conversation")
def sessions(task_id, project, details):
    """Show sessions associated with a task."""
    console = Console()

    from ..sessions.correlation import find_sessions_for_task

    task_sessions = find_sessions_for_task(task_id, project_path=project)

    if not task_sessions:
        console.print(f"[dim]No sessions found for task {task_id}[/dim]")
        return

    # Summary
    total_cost = sum(ts.session.total_cost for ts in task_sessions)
    total_tokens = sum(ts.session.total_tokens for ts in task_sessions)

    console.print(f"\n[bold]Task {task_id}[/bold]")
    console.print(f"Sessions: {len(task_sessions)} | Cost: ${total_cost:.2f} | Tokens: {total_tokens:,}\n")

    # Session table
    table = Table(title="Associated Sessions")
    table.add_column("Session ID", style="cyan")
    table.add_column("Date")
    table.add_column("Duration")
    table.add_column("Cost", justify="right")
    table.add_column("Messages", justify="right")
    table.add_column("First Prompt")

    for ts in task_sessions:
        s = ts.session
        duration = ""
        if s.start_time and s.end_time:
            secs = (s.end_time - s.start_time).total_seconds()
            if secs < 60:
                duration = f"{secs:.0f}s"
            else:
                duration = f"{int(secs // 60)}m"

        table.add_row(
            s.session_id[:8],
            s.start_time.strftime("%Y-%m-%d %H:%M") if s.start_time else "-",
            duration,
            f"${s.total_cost:.2f}",
            str(s.message_count),
            (s.first_prompt[:40] + "...") if s.first_prompt and len(s.first_prompt) > 40 else (s.first_prompt or "-"),
        )

    console.print(table)

    # Show details if requested
    if details and task_sessions:
        from ..sessions.content import extract_conversation

        console.print("\n[bold]Conversation Highlights[/bold]\n")

        for ts in task_sessions[-3:]:  # Last 3 sessions
            s = ts.session
            console.print(f"[cyan]Session {s.session_id[:8]}[/cyan] - {s.start_time}")

            turns = extract_conversation(s.session_id, s.project_path, max_turns=5)

            for turn in turns:
                role_style = "green" if turn.role == "user" else "blue"
                console.print(f"[{role_style}]{turn.role.upper()}:[/] {turn.content}")

                if turn.tool_uses:
                    console.print(f"[dim]  Tools: {', '.join(turn.tool_uses)}[/dim]")

            console.print()


@task_cmd.command("resume")
@click.argument("task_id")
def resume(task_id):
    """Resume the most recent session for a task."""
    console = Console()

    from ..sessions.correlation import find_sessions_for_task

    task_sessions = find_sessions_for_task(task_id)

    if not task_sessions:
        console.print(f"[red]No sessions found for task {task_id}[/red]")
        return

    # Get most recent session
    latest = task_sessions[-1]
    s = latest.session

    console.print(f"[bold]Resuming session for task {task_id}[/bold]")
    console.print(f"Session: {s.session_id}")
    console.print(f"Started: {s.start_time}")
    console.print(f"Messages: {s.message_count}")

    # Would invoke Claude Code with session resume
    # For now, show the command
    console.print(f"\n[dim]Run: claude --session {s.session_id}[/dim]")


@task_cmd.command("export")
@click.argument("task_id")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--format", type=click.Choice(["md", "json"]), default="md")
@click.option("--redact", is_flag=True, help="Redact sensitive content")
def export(task_id, output, format, redact):
    """Export task session history."""
    console = Console()

    from ..sessions.correlation import find_sessions_for_task
    from ..sessions.content import extract_conversation

    task_sessions = find_sessions_for_task(task_id)

    if not task_sessions:
        console.print(f"[red]No sessions found for task {task_id}[/red]")
        return

    if format == "md":
        content = export_to_markdown(task_id, task_sessions, redact)
    else:
        content = export_to_json(task_id, task_sessions, redact)

    if output:
        with open(output, 'w') as f:
            f.write(content)
        console.print(f"[green]Exported to {output}[/green]")
    else:
        console.print(content)


def export_to_markdown(task_id: str, sessions: list, redact: bool) -> str:
    """Export to Markdown format."""
    from ..sessions.content import extract_conversation

    lines = [
        f"# Task {task_id} - Session History",
        "",
        f"**Total Sessions**: {len(sessions)}",
        f"**Total Cost**: ${sum(ts.session.total_cost for ts in sessions):.2f}",
        "",
        "---",
        "",
    ]

    for ts in sessions:
        s = ts.session
        lines.append(f"## Session {s.session_id[:8]}")
        lines.append("")
        lines.append(f"- **Date**: {s.start_time}")
        lines.append(f"- **Cost**: ${s.total_cost:.2f}")
        lines.append(f"- **Messages**: {s.message_count}")
        lines.append("")
        lines.append("### Conversation")
        lines.append("")

        turns = extract_conversation(s.session_id, s.project_path)
        for turn in turns:
            role = "**User**" if turn.role == "user" else "**Assistant**"
            content = turn.content
            if redact:
                # Simple redaction of potential secrets
                import re
                content = re.sub(r'(api[_-]?key|password|secret|token)\s*[:=]\s*\S+', r'\1: [REDACTED]', content, flags=re.IGNORECASE)

            lines.append(f"{role}:")
            lines.append(f"> {content}")
            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def export_to_json(task_id: str, sessions: list, redact: bool) -> str:
    """Export to JSON format."""
    import json
    from ..sessions.content import extract_conversation

    data = {
        "task_id": task_id,
        "total_sessions": len(sessions),
        "total_cost": sum(ts.session.total_cost for ts in sessions),
        "sessions": [],
    }

    for ts in sessions:
        s = ts.session
        session_data = {
            "session_id": s.session_id,
            "start_time": s.start_time.isoformat() if s.start_time else None,
            "cost": s.total_cost,
            "message_count": s.message_count,
            "turns": [],
        }

        turns = extract_conversation(s.session_id, s.project_path)
        for turn in turns:
            session_data["turns"].append({
                "role": turn.role,
                "content": turn.content if not redact else "[content may be redacted]",
                "timestamp": turn.timestamp,
                "tool_uses": turn.tool_uses,
            })

        data["sessions"].append(session_data)

    return json.dumps(data, indent=2)
```

## Integration with Backlog.md

Add session info to task view:

```python
# src/specify_cli/backlog/task_view.py

def enhance_task_view(task: dict) -> dict:
    """Enhance task view with session information."""
    from ..sessions.correlation import find_sessions_for_task

    task_id = task.get("id")
    if not task_id:
        return task

    sessions = find_sessions_for_task(task_id)

    task["_sessions"] = {
        "count": len(sessions),
        "total_cost": sum(ts.session.total_cost for ts in sessions),
        "last_session": sessions[-1].session.start_time.isoformat() if sessions else None,
    }

    return task
```

## File Structure

```
src/specify_cli/
├── sessions/
│   ├── __init__.py
│   ├── correlation.py  # Task-session correlation
│   ├── tracking.py     # Explicit session tracking
│   └── content.py      # Conversation extraction
└── commands/
    └── task_sessions.py  # CLI commands

.flowspec/
└── session_tasks.json  # Explicit tracking data
```

## Configuration

```yaml
# flowspec_workflow.yml (additions)

sessions:
  # Enable task-session correlation
  enable_correlation: true

  # Methods to use for correlation
  correlation_methods:
    - mention      # Search for task ID in session content
    - explicit     # Explicitly recorded associations
    - branch       # Match git branch names

  # Track new sessions automatically
  auto_track: true

  # Export settings
  export:
    default_format: "md"
    redact_patterns:
      - "api[_-]?key"
      - "password"
      - "secret"
      - "token"
```

## Testing Strategy

### Unit Tests
```python
# tests/test_sessions.py

def test_find_task_mentions():
    # Create test JSONL with task mentions
    # Verify correlation finds them
    pass

def test_extract_conversation():
    # Create test JSONL
    # Verify conversation extraction
    pass

def test_export_markdown():
    # Test markdown export format
    pass
```

### Integration Tests
- Test with real Claude Code session files
- Test correlation accuracy
- Test export file generation

## Acceptance Criteria Summary

- [ ] `specify task sessions TASK-123` shows associated sessions
- [ ] Sessions found by task ID mention in content
- [ ] Session metrics shown (cost, duration, messages)
- [ ] Conversation highlights viewable
- [ ] `specify task resume TASK-123` shows resume command
- [ ] `specify task export TASK-123` creates export file
- [ ] Export supports Markdown and JSON formats
- [ ] Sensitive content redaction option
- [ ] Explicit session tracking works
- [ ] Performance acceptable for large session counts

## Privacy Considerations

- Session content may contain sensitive prompts/responses
- Redaction feature helps but isn't comprehensive
- Export files should be treated as potentially sensitive
- Consider adding project-level export restrictions

## Open Questions

1. How to handle sessions that span multiple tasks?
2. Should we support fuzzy task ID matching?
3. How to improve correlation accuracy?
4. Should session data be indexed for faster queries?

## References

- [opcode SessionList](https://github.com/winfunc/opcode/blob/main/src/components/SessionList.tsx)
- [Claude Code session format](https://docs.anthropic.com/claude-code/)
- [backlog.md API](https://github.com/backlog-md/backlog)
