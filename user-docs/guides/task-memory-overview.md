# Task Memory: Cross-Agent Context Persistence

## Overview

**Task Memory** is a persistent, task-scoped context management system that eliminates context loss across sessions, machines, and AI coding assistants. Every task in "In Progress" state automatically maintains a markdown memory file that travels with the task through git.

### Problem Solved

Without Task Memory, developers lose 15-30 minutes at the start of each session rebuilding context:
- What decisions were made?
- What approaches were tried (and failed)?
- What blockers exist?
- What's the current state?

Task Memory reduces this to **<2 minutes** by automatically maintaining and injecting context.

---

## Core Concept

```
┌─────────────────────────────────────────────────────────────────┐
│                      Task Memory System                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐         ┌──────────────┐                    │
│   │   Backlog    │ trigger │  Lifecycle   │                    │
│   │  Task Edit   │────────▶│   Manager    │                    │
│   └──────────────┘         └──────┬───────┘                    │
│                                   │                             │
│                    ┌──────────────┼──────────────┐              │
│                    ▼              ▼              ▼              │
│            ┌───────────┐  ┌───────────┐  ┌───────────┐         │
│            │  Memory   │  │  Context  │  │   MCP     │         │
│            │   Store   │  │  Injector │  │ Resources │         │
│            └─────┬─────┘  └─────┬─────┘  └─────┬─────┘         │
│                  │              │              │                │
│                  ▼              ▼              ▼                │
│         backlog/memory/   CLAUDE.md      backlog://            │
│         task-{id}.md      @import        memory/{id}           │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                    AI Assistants                         │  │
│   ├─────────────────────┬───────────────────────────────────┤  │
│   │    Claude Code      │      GitHub Copilot               │  │
│   │    (CLAUDE.md)      │      (MCP Protocol)               │  │
│   └─────────────────────┴───────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Memory File Structure

**Location**: `backlog/memory/task-{id}.md`

```markdown
---
task_id: task-368
created: 2025-12-09 10:30:00
updated: 2025-12-09 14:22:00
---

# Task Memory: task-368

## Context
Brief description of the task and current state.

## Key Decisions
- 2025-12-09 10:30 - Use PostgreSQL for scalability
- 2025-12-09 11:15 - JWT tokens with 24hr expiry

## Approaches Tried
### Approach: SQLite for storage
**Result**: Rejected
**Reason**: p95 latency was 500ms under load

## Open Questions
- Should we add rate limiting?

## Resources
- ADR-015: Database selection
- API spec: docs/api/auth.md

## Notes
Implementation notes, code snippets, debugging info...
```

**Design Principles**:
- Append-mostly format (reduces merge conflicts)
- Timestamps on all entries (chronological tracking)
- Structured sections (searchable, parseable)
- Human-readable markdown (works without tooling)

---

## Lifecycle Triggers

Memory operations are triggered by **task state transitions**:

| State Transition | Memory Action | What Happens |
|------------------|---------------|--------------|
| To Do → In Progress | **Create** | New memory file created from template |
| In Progress → Done | **Archive** | Memory moved to `archive/` directory |
| Done → In Progress | **Restore** | Memory restored from archive |
| In Progress → To Do | **Delete** | Memory file removed |
| Done → Archived | **Delete** | Archived memory removed |

### Trigger Command

```bash
# This command triggers memory lifecycle
backlog task edit task-42 -s "In Progress"
```

The lifecycle manager intercepts the status change and performs the appropriate memory operation.

---

## Claude Code Integration

Claude Code uses the **CLAUDE.md @import mechanism** for zero-latency context injection.

### How It Works

1. **Task starts**: Memory file created, `@import` added to `backlog/CLAUDE.md`
2. **Session begins**: Claude Code loads `CLAUDE.md` into system prompt
3. **@import resolves**: Memory content injected automatically
4. **Task completes**: `@import` removed, memory archived

### Integration File

**`backlog/CLAUDE.md`** contains:

```markdown
## Active Task Context

@import ../memory/task-368.md
```

### Hook Implementation

**File**: `.claude/hooks/post-tool-use-task-memory-lifecycle.py`

```python
# Triggered after any Bash tool use
# Intercepts: backlog task edit task-X -s "Status"
# Calls: LifecycleManager.on_state_change()
```

**Execution Flow**:
```
User runs command
       ↓
Bash tool executes: backlog task edit task-42 -s "In Progress"
       ↓
Post-tool-use hook fires
       ↓
Hook parses command, extracts task_id and new_status
       ↓
LifecycleManager creates memory, updates CLAUDE.md
       ↓
Next Claude response has full task context
```

### Key Characteristics

| Aspect | Value |
|--------|-------|
| Injection method | System prompt via @import |
| Latency | Sub-millisecond (file read) |
| Update timing | Immediate on state change |
| Failure mode | Fail open (log error, continue) |

---

## GitHub Copilot Integration

GitHub Copilot uses **MCP (Model Context Protocol)** resources for on-demand context access.

### How It Works

1. **Task starts**: Memory file created (same as Claude Code)
2. **Agent needs context**: Queries MCP resource `backlog://memory/active`
3. **MCP server responds**: Returns JSON with memory content
4. **Agent uses context**: Memory available for that interaction

### MCP Resource Endpoints

```
backlog://memory/{task_id}    # Specific task memory
backlog://memory/active       # Currently active task
```

### Response Format

```json
{
  "task_id": "task-368",
  "content": "[Full memory markdown]",
  "path": "backlog/memory/task-368.md",
  "exists": true
}
```

### Agent Configuration

**File**: `.github/agents/{role}-{command}.agent.md`

Agents are generated from Claude Code commands via `sync-copilot-agents.sh`:

```bash
# Generate Copilot agents from Claude Code commands
./scripts/bash/sync-copilot-agents.sh --output .github/agents/
```

### Key Characteristics

| Aspect | Value |
|--------|-------|
| Injection method | MCP protocol request |
| Latency | Network latency (~50-200ms) |
| Update timing | On-demand when agent queries |
| Failure mode | Returns error JSON |

---

## Claude Code vs GitHub Copilot: Comparison

| Feature | Claude Code | GitHub Copilot |
|---------|-------------|----------------|
| **Primary mechanism** | CLAUDE.md @import | MCP Resources |
| **Context injection** | Automatic (system prompt) | On-demand (agent queries) |
| **Trigger** | Post-tool-use hook | Manual MCP request |
| **When context loads** | Session start | When agent requests |
| **Latency** | Sub-millisecond | Network dependent |
| **Memory updates** | Automatic on state change | Agent re-queries MCP |
| **Config location** | `.claude/hooks/` | `.github/agents/` |
| **Sync mechanism** | Native | `sync-copilot-agents.sh` |

### Practical Differences

**Claude Code Experience**:
```
1. You: backlog task edit task-42 -s "In Progress"
2. Claude: [Immediately has full task context]
3. You: "Continue where we left off"
4. Claude: [Knows decisions, approaches, blockers]
```

**GitHub Copilot Experience**:
```
1. You: Edit task status in Copilot
2. Copilot agent: [Queries backlog://memory/active]
3. MCP server: [Returns memory content]
4. Copilot: [Now has task context for this interaction]
```

---

## Architecture Components

### TaskMemoryStore (`src/specify_cli/memory/store.py`)

Physical file operations:
- `create(task_id)` - Create new memory from template
- `read(task_id)` - Read memory content
- `append(task_id, content)` - Add to memory
- `archive(task_id)` - Move to archive directory
- `restore(task_id)` - Restore from archive

### LifecycleManager (`src/specify_cli/memory/lifecycle.py`)

Orchestrates memory operations on state transitions:
- Detects transition type (start, complete, reopen, etc.)
- Calls appropriate store methods
- Updates context injection (CLAUDE.md)
- Syncs key decisions to backlog

### ContextInjector (`src/specify_cli/memory/injector.py`)

Manages context injection:
- `update_active_task(task_id)` - Add @import to CLAUDE.md
- `clear_active_task()` - Remove @import
- `get_active_task_id()` - Parse current active task
- Token-aware truncation (keeps recent context)

### MCP Resources (`src/specify_cli/memory/mcp.py`)

Model Context Protocol endpoints:
- Resource handlers for Copilot/VS Code integration
- JSON response formatting
- Error handling

---

## Security Features

1. **Path Traversal Prevention**
   - Regex validation: `^task-[a-zA-Z0-9][-a-zA-Z0-9]*$`
   - Defense-in-depth: blocks `..`, `/`, `\`
   - Resolved path verification

2. **Secret Detection**
   - Pre-commit hook scans for sensitive patterns
   - GitHub Actions gitleaks scan
   - CI blocks PRs with detected secrets

3. **Access Control**
   - Inherits repository permissions
   - Private repos: restricted to collaborators

---

## Usage Examples

### Starting a Task

```bash
# Start work (creates memory automatically)
backlog task edit task-42 -s "In Progress"

# Claude Code now has context via CLAUDE.md @import
# Copilot can query backlog://memory/task-42
```

### Adding Context During Work

```bash
# Add a decision
backlog memory append task-42 "Decision: Use JWT with 24hr expiry"

# Add an approach that failed
backlog memory append task-42 "Tried: Session cookies - rejected due to mobile app"
```

### Completing a Task

```bash
# Complete task (archives memory, syncs key decisions)
backlog task edit task-42 -s "Done"

# Memory moved to: backlog/memory/archive/task-42.md
# Key decisions synced to backlog task notes
```

### Searching Historical Context

```bash
# Search across all memories
backlog memory search "PostgreSQL"

# Search archived memories
backlog memory search "authentication" --archived
```

---

## Directory Structure

```
backlog/
├── CLAUDE.md              # Context injection file (has @import)
├── memory/
│   ├── task-368.md        # Active task memory
│   ├── task-369.md        # Active task memory
│   └── archive/           # Completed task memories
│       ├── task-245.md
│       └── task-310.md
└── tasks/                 # Backlog tasks (separate)

.claude/
├── hooks/
│   └── post-tool-use-task-memory-lifecycle.py  # Lifecycle hook
└── commands/              # Claude Code slash commands

.github/
└── agents/                # Generated Copilot agents
```

---

## Performance

| Operation | Latency |
|-----------|---------|
| Create memory | ~10ms |
| Read memory | ~5ms |
| Append to memory | ~15ms |
| Archive memory | ~5ms |
| Full lifecycle hook | <50ms (p95) |

**Scalability**: Tested with 10,000+ memories without degradation.

---

## Summary

Task Memory solves context loss by:

1. **Automatic lifecycle management** - Memory created/archived with task state
2. **Multi-agent support** - Works with Claude Code, GitHub Copilot, VS Code
3. **Git-native storage** - Simple markdown files, standard sync
4. **Zero-config injection** - Claude Code gets context automatically
5. **Structured format** - Searchable decisions, approaches, blockers

The key difference between Claude Code and GitHub Copilot integration is **push vs pull**:
- Claude Code: Context **pushed** into system prompt via @import
- GitHub Copilot: Context **pulled** on-demand via MCP resources
