# Two-Tier Task Management: Backlog.md + Beads

This guide explains flowspec's recommended approach to task management using two complementary systems: **Backlog.md** for human-facing tasks and **Beads** for detailed agent work tracking.

## Overview

Flowspec uses a hierarchical task management approach:

| Layer | Tool | Purpose | Audience |
|-------|------|---------|----------|
| **Feature/Task** | Backlog.md | High-level work items, acceptance criteria, status | Humans, planning |
| **Agent Work** | Beads | Detailed implementation steps, dependencies, blockers | Agents, execution |

```
┌─────────────────────────────────────────────────────┐
│                   BACKLOG.MD                        │
│  Human-facing tasks, features, acceptance criteria  │
│                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │   task-42   │  │   task-43   │  │   task-44   │ │
│  │  Feature X  │  │  Bug Fix Y  │  │  Refactor Z │ │
│  └──────┬──────┘  └─────────────┘  └─────────────┘ │
│         │                                           │
└─────────┼───────────────────────────────────────────┘
          │ (optional, for complex tasks)
          ▼
┌─────────────────────────────────────────────────────┐
│                     BEADS                           │
│    Detailed agent work, dependencies, blockers      │
│                                                     │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐       │
│  │ beads-001 │  │ beads-002 │  │ beads-003 │       │
│  │ API impl  │──│   Tests   │  │  Docs     │       │
│  └───────────┘  └───────────┘  └───────────┘       │
│        └── depends on ──┘                           │
└─────────────────────────────────────────────────────┘
```

## When to Use Each System

### Use Backlog.md For

- **All user-facing tasks** - features, bugs, improvements
- **Acceptance criteria** - testable requirements
- **Sprint/milestone planning** - human coordination
- **Status communication** - what's done, what's next
- **Single-session work** - tasks completable in one sitting

### Use Beads For (Optional)

- **Multi-session agent work** - complex implementations spanning conversations
- **Dependency tracking** - when task B must wait for task A
- **Discovered subtasks** - work that emerges during implementation
- **Agent coordination** - multiple agents working on related pieces
- **Detailed progress** - granular tracking beyond backlog notes

## Workflow

### 1. Create Tasks in Backlog

All work starts in Backlog.md:

```bash
# Create a feature task
backlog task create "Implement user authentication" \
  --ac "Users can register with email" \
  --ac "Users can log in with password" \
  --ac "Sessions persist across browser restarts" \
  -l backend -l auth
```

### 2. Start Work - Update Backlog Status

When beginning work:

```bash
# Move to In Progress and assign
backlog task edit task-42 -s "In Progress" -a @myself
```

### 3. Simple Tasks: Stay in Backlog

For straightforward tasks, track everything in backlog notes:

```bash
# Add implementation notes as you work
backlog task edit task-42 --notes-append "Implemented JWT token generation"
backlog task edit task-42 --check-ac 1  # Mark first AC done

# Complete when finished
backlog task edit task-42 -s Done
```

### 4. Complex Tasks: Add Beads for Agent Work

For complex multi-step implementations, create beads issues:

```bash
# Create detailed agent tasks that reference the parent backlog task
bd create "Implement JWT token service"
bd create "Create login endpoint"
bd create "Add session persistence"

# Set up dependencies
bd dep add beads-002 beads-001  # Login depends on JWT service
bd dep add beads-003 beads-002  # Session depends on login
```

### 5. Track Agent Progress in Beads

As agents work:

```bash
# Start work on available tasks
bd ready                           # See what's unblocked
bd update beads-001 --status=in_progress

# Complete and move to next
bd close beads-001
bd update beads-002 --status=in_progress
```

### 6. Roll Up to Backlog

When beads work completes, update the parent backlog task:

```bash
# Update backlog with summary of completed work
backlog task edit task-42 --notes-append "Agent work complete: JWT service, login endpoint, session persistence implemented"

# Check off acceptance criteria
backlog task edit task-42 --check-ac 1 --check-ac 2 --check-ac 3

# Mark task done
backlog task edit task-42 -s Done
```

## Decision Framework

```
Is this a new piece of work?
    │
    ▼
Create in Backlog.md
    │
    ▼
Is it a simple, single-session task?
    │
    ├── YES → Track entirely in Backlog
    │         (notes, AC checks, status)
    │
    └── NO → Consider Beads for:
              • Multi-session work
              • Complex dependencies
              • Multiple agents
              • Discovered subtasks
```

## Best Practices

### Linking Beads to Backlog Tasks

Reference the parent backlog task in beads issue titles or descriptions:

```bash
bd create "[task-42] Implement JWT token service"
```

### Keeping Backlog Updated

Even when using beads, keep the backlog task current:

- Update status when starting/pausing work
- Add summary notes periodically
- Check acceptance criteria as they're satisfied
- Don't let backlog go stale while working in beads

### Session Boundaries

At session end:

```bash
# Sync beads work
bd sync

# Update backlog with session summary
backlog task edit task-42 --notes-append "Session complete: beads-001 done, beads-002 in progress"
```

### When Beads Isn't Needed

Skip beads for:
- Bug fixes with clear scope
- Documentation updates
- Small features (< 2 hours work)
- Tasks without dependencies
- Solo work without agent coordination

## Integration with Flowspec Workflows

### /flow:implement Integration

When running `/flow:implement` on complex tasks:

1. The workflow reads the backlog task and its acceptance criteria
2. Optionally creates beads issues for implementation subtasks
3. Tracks detailed progress in beads
4. Updates backlog task notes with progress summaries
5. Checks acceptance criteria as they're satisfied

### /flow:validate Integration

Validation can check:
- All beads issues for the task are closed
- Acceptance criteria in backlog are checked
- Implementation notes are present

## Quick Reference

| Action | Backlog Command | Beads Command |
|--------|-----------------|---------------|
| Create work | `backlog task create "..."` | `bd create --title="..."` |
| Start work | `backlog task edit ID -s "In Progress"` | `bd update ID --status=in_progress` |
| Add notes | `backlog task edit ID --notes-append "..."` | (in issue description) |
| Check progress | `backlog task view ID --plain` | `bd show ID` |
| See available | `backlog task list -s "To Do"` | `bd ready` |
| Complete | `backlog task edit ID -s Done` | `bd close ID` |
| Sync | (auto via MCP) | `bd sync` |

## Summary

- **Backlog.md**: Source of truth for human-visible work
- **Beads**: Optional layer for detailed agent orchestration
- **Simple tasks**: Backlog only
- **Complex tasks**: Backlog + Beads, with beads rolling up to backlog
- **Always**: Keep backlog current, even when using beads
