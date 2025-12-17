# Backlog.md Quick Start Guide

Get started with Backlog.md task management integration in Flowspec in under 5 minutes.

## What is Backlog.md Integration?

Backlog.md integration extends Flowspec's spec-driven development workflow with powerful task lifecycle management:

- **Visual Task Boards**: Kanban boards in terminal and web UI
- **AI-Powered Management**: Claude Code and other AI assistants can manage tasks via MCP
- **Git-Native**: All tasks stored in your repository as markdown files
- **Dependency Tracking**: Automatic task dependencies from your spec structure
- **Team Collaboration**: Assignees, priorities, labels, and status tracking

**Key Benefit**: Go from spec to tracked, AI-managed tasks without leaving your repository.

## Prerequisites

- Flowspec installed and initialized (`flowspec init`)
- Node.js 18+ (for Backlog.md CLI)
- Claude Code (optional, for AI integration)

## 5-Minute Setup

### 1. Install Backlog.md CLI

```bash
# Using npm
npm install -g backlog.md

# Or using pnpm
pnpm add -g backlog.md

# Verify installation
backlog --version
```

### 2. Initialize Backlog in Your Project

```bash
# Navigate to your project
cd your-project

# Initialize Backlog.md
backlog init

# Configure project name and settings when prompted
```

### 3. Generate Tasks from Your Spec

```bash
# Create a spec first (if you haven't already)
/flow:specify Build a user authentication system with login, signup, and password reset

# Create a plan
/flow:plan Use Node.js with Express, PostgreSQL database, and JWT for tokens

# Generate tasks (currently creates tasks.md)
/flow:tasks

# 🚧 COMING SOON: Direct Backlog.md generation
# specify tasks generate --format backlog-md
```

### 4. View Your Tasks

```bash
# Terminal Kanban board
backlog board

# Web UI
backlog browser

# Quick overview
backlog overview
```

### 5. (Optional) Configure MCP for AI Integration

```bash
# Add Backlog.md MCP server for Claude Code
claude mcp add backlog --scope user -- backlog mcp start

# Restart Claude Code

# Now you can ask Claude:
# "List all tasks in the backlog"
# "Update task-1 to Done"
```

## Your First Task Management Session

### Create a Task Manually

```bash
backlog task create "Implement user login endpoint" \
  --labels "backend,authentication,US1" \
  --status "To Do" \
  --priority "high"
```

### View Task Details

```bash
backlog task view task-1
```

### Update Task Status

```bash
# Via CLI
backlog task edit task-1

# Or via AI (with MCP configured)
# Ask Claude: "Mark task-1 as in progress"
```

### Filter Tasks by User Story

```bash
# View only tasks for User Story 1
backlog board --filter US1
```

## Understanding Task Organization

Backlog.md organizes your tasks using **labels** and **dependencies** rather than hierarchical phases:

```yaml
# task-012 - Create User model.md
---
status: todo
assignees: []
labels: [US1, backend, implementation]
priority: high
dependencies: [task-005]  # Must complete task-005 first
---

## Description
Create User model in src/models/user.py with authentication fields
```

### Key Concepts

- **Labels**: Organize by user story (US1, US2), phase (setup, implementation), or custom tags
- **Dependencies**: Define what must complete before this task can start
- **Status**: Track lifecycle (todo, in_progress, blocked, done, archived)
- **Priority**: High, medium, low (mapped from your spec's user story priorities)

## Common Workflows

### Daily Development Flow

```bash
# Morning: Check what's in progress
backlog board

# Pick a task to work on
backlog task view task-12

# Mark as in progress (via AI or CLI)
# Claude: "Start working on task-12"

# Work on the task...

# Mark complete
# Claude: "Complete task-12"
```

### Team Workflow

```bash
# View team's tasks
backlog browser  # Opens web UI

# Assign tasks via web UI drag-and-drop

# Check who's working on what
backlog overview

# Filter by assignee
backlog board --assignee "jane@example.com"
```

### AI-Assisted Workflow (with MCP)

```text
You: "Claude, show me all tasks for User Story 1"
Claude: [Lists tasks filtered by US1 label]

You: "Start working on task-12"
Claude: [Updates status to in_progress, opens relevant files]

You: [Work together with Claude to implement]

You: "Complete task-12"
Claude: [Updates status to done, suggests next task]
```

## Troubleshooting

### Backlog.md not found

```bash
# Install it
npm install -g backlog.md

# Or check if it's in PATH
which backlog
```

### MCP connection fails

```bash
# Verify MCP server configured
claude mcp list

# Re-add if needed
claude mcp add backlog --scope user -- backlog mcp start

# Restart Claude Code
```

### Tasks not showing in board

```bash
# Check backlog directory exists
ls backlog/tasks/

# Verify config
cat backlog/config.yml

# Re-initialize if needed
backlog init
```

## Next Steps

- **Read the full user guide**: `docs/guides/backlog-user-guide.md` for comprehensive documentation
- **Explore MCP features**: See `docs/guides/backlog-user-guide.md#ai-integration`
- **Learn migration**: `docs/guides/backlog-migration.md` to convert existing tasks.md files
- **View command reference**: `docs/reference/backlog-commands.md` for all available commands

## FAQ

### Q: Can I use Backlog.md without Flowspec?
**A**: Yes! Backlog.md is a standalone tool. Flowspec integration adds automatic task generation from specs.

### Q: Do I need Claude Code?
**A**: No, you can use Backlog.md CLI and web UI manually. MCP integration just adds AI-powered task management.

### Q: Where is my task data stored?
**A**: All tasks are markdown files in `backlog/tasks/`. Everything stays in your Git repository.

### Q: Can multiple people use the same backlog?
**A**: Yes! Backlog.md is designed for team collaboration. Just commit and push `backlog/` to Git.

### Q: Will this work with GitHub Copilot / Cursor?
**A**: Yes! Any AI assistant that supports MCP can integrate with Backlog.md. See Backlog.md docs for setup.

---

**Status**: Ready to use! The integration is currently in beta for task generation.

**Feedback**: Open an issue on GitHub if you encounter problems or have suggestions.
