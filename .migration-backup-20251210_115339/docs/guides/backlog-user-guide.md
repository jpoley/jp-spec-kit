# Backlog.md User Guide for jp-spec-kit

Comprehensive guide to using Backlog.md task management with jp-spec-kit's spec-driven development workflow.

## Table of Contents

- [Overview](#overview)
- [Installation and Setup](#installation-and-setup)
- [Task Generation from Specs](#task-generation-from-specs)
- [Task Management](#task-management)
- [AI Integration with MCP](#ai-integration-with-mcp)
- [Team Collaboration](#team-collaboration)
- [Advanced Features](#advanced-features)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

### What is Backlog.md Integration?

Backlog.md integration enhances jp-spec-kit with a robust task lifecycle management layer that bridges the gap between specification and execution.

**The Integration Flow**:
```
Spec.md (Requirements)
    ↓
Plan.md (Architecture)
    ↓
Tasks Generated → Backlog.md (Execution & Tracking)
    ↓
AI-Assisted Implementation
    ↓
Completed Feature
```

### Key Benefits

1. **Visual Task Management**: Terminal Kanban boards and web UI
2. **AI-Powered Execution**: Claude Code and other assistants manage tasks via MCP
3. **Git-Native Storage**: All data in your repository as markdown files
4. **Dependency Tracking**: Automatic task dependencies from spec structure
5. **Team Collaboration**: Assignees, priorities, labels, status tracking
6. **Spec Traceability**: Tasks linked to user stories and requirements

### Architecture

```
┌─────────────────────────────────────────┐
│          jp-spec-kit Layer              │
│  /jpspec:specify → spec.md              │
│  /jpspec:plan → plan.md                 │
│  /jpspec:tasks → Generate Tasks         │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│        Backlog.md Storage Layer         │
│  backlog/tasks/task-*.md files          │
│  • Labels (US1, US2, etc.)              │
│  • Dependencies (task-X blocks task-Y)  │
│  • Status (todo, in_progress, done)     │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│       Backlog.md Management Layer       │
│  • CLI: backlog board, browser, search  │
│  • Web UI: Drag-and-drop Kanban         │
│  • MCP API: AI assistant integration    │
└─────────────────────────────────────────┘
```

## Installation and Setup

### Prerequisites

- jp-spec-kit installed: `uv tool install specify-cli --from git+https://github.com/jpoley/jp-spec-kit.git`
- Node.js 18+ or npm/pnpm
- Git repository initialized
- Claude Code (optional, for AI integration)

### Step 1: Install Backlog.md

```bash
# Using npm
npm install -g backlog.md

# Or using pnpm
pnpm add -g backlog.md

# Or using yarn
yarn global add backlog.md

# Verify installation
backlog --version
# Expected: v1.20.1 or higher
```

### Step 2: Initialize Backlog in Your Project

```bash
# Navigate to your jp-spec-kit project
cd your-project

# Initialize Backlog.md
backlog init

# You'll be prompted for:
# - Project name (default: directory name)
# - Default status (default: "To Do")
# - Status columns (default: To Do, In Progress, Done)
```

This creates:
```
your-project/
├── backlog/
│   ├── config.yml          # Project configuration
│   ├── tasks/              # Task files (empty initially)
│   ├── docs/               # Documentation
│   └── decisions/          # Decision records
```

### Step 3: Configure Settings (Optional)

Edit `backlog/config.yml` to customize:

```yaml
project_name: "your-project"
default_status: "To Do"
statuses: ["To Do", "In Progress", "Done"]
labels: []                  # Add default labels like ["bug", "feature"]
milestones: []
date_format: yyyy-mm-dd
max_column_width: 20
auto_open_browser: true
default_port: 6420
remote_operations: true     # Enable Git integration
auto_commit: false          # Auto-commit task changes
bypass_git_hooks: false
check_active_branches: true
active_branch_days: 30
```

### Step 4: Configure MCP for AI Integration (Optional)

```bash
# Add Backlog.md MCP server to Claude Code
claude mcp add backlog --scope user -- backlog mcp start

# Verify configuration
cat ~/.config/claude-code/.mcp.json
# Should show backlog MCP server entry

# Restart Claude Code to load MCP server
```

## Task Generation from Specs

### Current Workflow (Manual)

**🚧 Note**: Automatic Backlog.md task generation is coming soon. For now, use this workflow:

1. **Create Spec and Plan**:
```bash
/jpspec:specify Build a user authentication system with login, signup, password reset
/jpspec:plan Use Node.js with Express, PostgreSQL, JWT tokens
```

2. **Generate tasks.md**:
```bash
/jpspec:tasks
```

3. **Manually Create Backlog Tasks** (from tasks.md):
```bash
# For each task in tasks.md, create a Backlog task
backlog task create "T001: Create User model" \
  --labels "setup,US1" \
  --status "To Do" \
  --priority "high"
```

### Future Workflow (Automated)

**Coming in v0.1.0**:

```bash
# Generate Backlog.md tasks directly from spec
specify tasks generate --format backlog-md

# This will:
# 1. Parse spec.md and plan.md
# 2. Generate backlog/tasks/task-*.md files
# 3. Set labels from user stories (US1, US2)
# 4. Build dependencies from phases
# 5. Map priorities from spec
```

### Task Format Mapping

jp-spec-kit tasks map to Backlog.md like this:

**tasks.md format**:
```markdown
- [ ] T012 [P] [US1] Create User model in src/models/user.py
```

**Backlog.md format**:
```markdown
# task-012 - Create User model.md
---
status: todo
assignees: []
labels: [US1, parallelizable, implementation]
priority: high
dependencies: [task-005]
---

## Description
Create User model in src/models/user.py

## Implementation Details
- Define User schema with authentication fields
- Add password hashing
- Create database migration

## Acceptance Criteria
- [ ] User model includes email, password_hash, created_at
- [ ] Password hashing uses bcrypt
- [ ] Migration creates users table
```

### Understanding Labels and Dependencies

**Labels** encode the structure from jp-spec-kit:

- **User Story Labels**: `US1`, `US2`, `US3` (from `[US1]` markers)
- **Phase Labels**: `setup`, `foundational`, `implementation`, `polish`
- **Parallelization**: `parallelizable` (from `[P]` markers)
- **Custom Labels**: Add your own in `backlog/config.yml`

**Dependencies** preserve execution order:

- Setup tasks (Phase 1) → No dependencies
- Foundational tasks (Phase 2) → Depend on setup
- User Story tasks (Phase 3+) → Depend on foundational
- Polish tasks (Final) → Depend on all user stories

**Example Dependency Chain**:
```
task-001 (Setup: Create project structure)
    ↓
task-005 (Foundational: Database schema)
    ↓
task-012 (US1: User model)
    ↓
task-042 (Polish: Add integration tests)
```

## Task Management

### Viewing Tasks

**Terminal Kanban Board**:
```bash
# Interactive board
backlog board

# Filter by user story
backlog board --filter US1

# Filter by label
backlog board --filter backend

# Filter by assignee
backlog board --assignee john@example.com
```

**Web UI**:
```bash
# Open browser UI
backlog browser

# Opens at http://localhost:6420
# - Drag and drop tasks between columns
# - Click tasks to edit
# - Assign users
# - Add labels and milestones
```

**Quick Overview**:
```bash
# Summary statistics
backlog overview

# Example output:
# Project: your-project
# Total Tasks: 42
# To Do: 34
# In Progress: 5
# Done: 3
```

### Creating Tasks

**Via CLI**:
```bash
# Basic task
backlog task create "Implement user login"

# With metadata
backlog task create "Implement user login" \
  --labels "backend,authentication,US1" \
  --status "To Do" \
  --priority "high" \
  --assignee "developer@example.com"

# With dependencies
backlog task create "Create login endpoint" \
  --labels "backend,US1" \
  --dependencies "task-005,task-012"
```

**Via Web UI**:
1. Open `backlog browser`
2. Click "New Task" button
3. Fill in form
4. Save

**Via AI (with MCP)**:
```text
You: "Claude, create a task for implementing password reset functionality"
Claude: [Creates task with appropriate labels and dependencies based on context]
```

### Updating Tasks

**Change Status**:
```bash
# Via CLI
backlog task edit task-12

# Via AI
# "Claude, mark task-12 as in progress"
```

**Add Assignee**:
```bash
# Via web UI (easiest)
backlog browser  # Click task, assign

# Via file edit
vim backlog/tasks/task-012*.md
# Edit assignees: [developer@example.com]
```

**Update Priority**:
```bash
# Edit task file
backlog task edit task-12
# Change priority: high → medium
```

### Searching Tasks

```bash
# Search by keyword
backlog search "authentication"

# Search in task titles
backlog search --title "user"

# Search in task content
backlog search --content "password"

# Combine searches
backlog search "login" --labels "backend"
```

### Archiving Tasks

```bash
# Archive completed task
backlog task archive task-12

# Archive moves to backlog/archive/
# Task is no longer shown in board but preserved for history
```

## AI Integration with MCP

### What is MCP?

**Model Context Protocol (MCP)** allows AI assistants like Claude Code to programmatically interact with Backlog.md through a standardized API.

**What AI Can Do**:
- List tasks with filters
- Create new tasks
- Update task status, assignees, labels
- Search tasks by keywords
- Complete tasks automatically
- Create subtasks for complex work

### Setting Up MCP

```bash
# 1. Add Backlog.md MCP server
claude mcp add backlog --scope user -- backlog mcp start

# 2. Restart Claude Code

# 3. Verify in Claude Code
# Ask: "List all MCP servers"
# Should see: backlog
```

### MCP Configuration File

MCP config is in `.mcp.json` (project) or `~/.config/claude-code/.mcp.json` (user):

```json
{
  "mcpServers": {
    "backlog": {
      "command": "backlog",
      "args": ["mcp", "start"],
      "env": {},
      "description": "Backlog.md task management"
    }
  }
}
```

### Using AI to Manage Tasks

**List Tasks**:
```text
You: "Show me all tasks for User Story 1"
Claude: [Uses MCP to filter by US1 label, displays list]

You: "What tasks are in progress?"
Claude: [Filters by status: in_progress]
```

**Create Tasks**:
```text
You: "Create a task for implementing the password reset feature"
Claude: [Creates task with title, infers labels from context, sets appropriate priority]
```

**Update Task Status**:
```text
You: "Mark task-12 as done"
Claude: [Updates status, confirms completion]

You: "I'm starting work on task-15"
Claude: [Updates status to in_progress, opens relevant files]
```

**Search and Filter**:
```text
You: "Find all authentication-related tasks"
Claude: [Searches by keyword, lists results]

You: "Show me blocked tasks"
Claude: [Filters by status: blocked, explains dependencies]
```

**Complete Complex Workflows**:
```text
You: "Complete task-12 and suggest what to work on next"
Claude:
1. [Marks task-12 as done]
2. [Checks dependencies - which tasks are now unblocked]
3. [Suggests next task based on priority and user story flow]
```

## Team Collaboration

### Assigning Tasks

**Individual Assignment**:
```bash
# Via web UI
backlog browser
# Click task → Assign to team member

# Via file edit
vim backlog/tasks/task-012*.md
# assignees: [jane@example.com]
```

**Bulk Assignment**:
```bash
# Assign all US1 tasks to Jane
for task in backlog/tasks/*US1*.md; do
  # Edit assignees field
  sed -i 's/assignees: \[\]/assignees: [jane@example.com]/' "$task"
done
```

### Team Workflows

**Daily Standup**:
```bash
# View team board
backlog browser

# Each person filters by their assignee
backlog board --assignee jane@example.com

# Share progress updates
```

**Sprint Planning**:
```bash
# View all tasks for User Story 1
backlog board --filter US1

# Assign tasks in web UI
backlog browser

# Set milestones
# Edit backlog/config.yml:
# milestones: ["Sprint 1", "Sprint 2"]
```

**Progress Tracking**:
```bash
# Check overall progress
backlog overview

# Check specific user story
backlog board --filter US1

# Export to CSV for reporting
backlog export --format csv > progress.csv
```

### Git Workflow

Backlog.md works seamlessly with Git:

**Commit Task Updates**:
```bash
# Tasks are just markdown files
git add backlog/
git commit -m "Update task status: complete US1 tasks"
git push
```

**Review Task Changes in PRs**:
```bash
# See what tasks changed
git diff main..feature-branch backlog/

# Example diff:
# -status: todo
# +status: done
```

**Branching Strategy**:
```bash
# Option 1: Separate backlog branch
git checkout -b backlog-updates
# Update tasks
git commit -m "Track progress on US1"
git push origin backlog-updates

# Option 2: Include with feature branch
git checkout -b feature/authentication
# Implement feature + update tasks
git commit -m "Implement login + update task-12"
```

## Advanced Features

### Custom Labels

Define custom labels in `backlog/config.yml`:

```yaml
labels:
  - "bug"
  - "feature"
  - "tech-debt"
  - "documentation"
  - "backend"
  - "frontend"
  - "testing"
```

Use in tasks:
```bash
backlog task create "Fix login redirect bug" \
  --labels "bug,backend,high-priority"
```

### Milestones

Track progress toward milestones:

```yaml
# backlog/config.yml
milestones:
  - "MVP Launch"
  - "Beta Release"
  - "v1.0"
```

Assign tasks to milestones:
```bash
backlog task edit task-12
# Add: milestone: "MVP Launch"
```

View milestone progress:
```bash
backlog board --milestone "MVP Launch"
```

### Dependencies and Blocking

**Define Dependencies**:
```yaml
# task-012 depends on task-005 and task-008
dependencies: [task-005, task-008]
```

**View Dependency Graph**:
```bash
backlog graph

# Shows visual dependency tree
# Identifies critical path
# Highlights blocked tasks
```

**Check What's Blocking You**:
```bash
backlog task view task-012

# Shows:
# Blocked by: task-005 (todo), task-008 (in_progress)
```

### Task Templates

Create task templates for common patterns:

```bash
# Create template
mkdir -p backlog/templates/
cat > backlog/templates/feature-task.md <<'EOF'
---
status: todo
assignees: []
labels: [feature]
priority: medium
dependencies: []
---

## Description
[Describe the feature]

## Implementation Steps
- [ ] Step 1
- [ ] Step 2
- [ ] Step 3

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Testing
- [ ] Unit tests
- [ ] Integration tests
EOF

# Use template
cp backlog/templates/feature-task.md backlog/tasks/task-042-new-feature.md
```

### Automation with Scripts

**Auto-update from CI/CD**:
```bash
#!/bin/bash
# .github/workflows/update-tasks.sh

# When tests pass, mark task as done
TASK_ID=$1
sed -i 's/status: in_progress/status: done/' "backlog/tasks/task-$TASK_ID*.md"
git add backlog/
git commit -m "Auto-complete task-$TASK_ID: tests passed"
```

**Notify on blocked tasks**:
```bash
#!/bin/bash
# scripts/check-blocked-tasks.sh

# Find blocked tasks
BLOCKED=$(grep -l "status: blocked" backlog/tasks/*.md)

if [ -n "$BLOCKED" ]; then
  echo "⚠️ Blocked tasks found:"
  echo "$BLOCKED"
  # Send Slack notification, etc.
fi
```

## Best Practices

### Task Granularity

**Good Task Size** (2-8 hours of work):
```
✅ "Implement user login endpoint"
✅ "Create User model with authentication fields"
✅ "Add password reset email template"
```

**Too Large** (requires breakdown):
```
❌ "Build entire authentication system"
❌ "Implement all API endpoints"
```

**Too Small** (combine):
```
❌ "Import bcrypt library"
❌ "Write single unit test"
```

### Labels Strategy

**Effective Labeling**:
```yaml
# User story (required for jp-spec-kit integration)
labels: [US1]

# Phase/type
labels: [setup, implementation, polish]

# Technology area
labels: [backend, frontend, database]

# Priority indicator
labels: [high-priority, blocking]

# Custom tags
labels: [needs-review, waiting-on-external]
```

### Dependency Management

**Clear Dependencies**:
```yaml
# Good: Specific, necessary dependencies
dependencies: [task-005, task-012]

# Bad: Too many dependencies (task too coupled)
dependencies: [task-001, task-002, task-003, task-004, task-005]
```

**Minimize Blocking**:
- Use `[P]` marker for parallelizable tasks
- Break down tasks to reduce dependency chains
- Prioritize unblocking tasks

### Status Transitions

**Standard Flow**:
```
todo → in_progress → done
```

**With Blocking**:
```
todo → in_progress → blocked → in_progress → done
```

**Abandoned Work**:
```
todo → archived
in_progress → archived
```

### Commit Messages

**Good Commits**:
```bash
git commit -m "Complete task-12: User login endpoint

- Implemented POST /auth/login
- Added JWT token generation
- Updated task status: in_progress → done"
```

**Bad Commits**:
```bash
git commit -m "Updated tasks"
```

## Troubleshooting

### Common Issues

**Issue**: `backlog: command not found`

**Solution**:
```bash
# Install Backlog.md
npm install -g backlog.md

# Verify PATH
echo $PATH
# Should include npm global bin directory

# Test
backlog --version
```

---

**Issue**: MCP server not connecting

**Solution**:
```bash
# 1. Verify MCP server configured
claude mcp list

# 2. Check MCP config file
cat ~/.config/claude-code/.mcp.json

# 3. Re-add MCP server
claude mcp remove backlog
claude mcp add backlog --scope user -- backlog mcp start

# 4. Restart Claude Code completely

# 5. Test connection
# Ask Claude: "List all MCP servers"
```

---

**Issue**: Tasks not showing in board

**Solution**:
```bash
# 1. Check backlog directory
ls -la backlog/tasks/

# 2. Verify config
cat backlog/config.yml

# 3. Check task file format
cat backlog/tasks/task-001*.md
# Must have valid frontmatter with status field

# 4. Re-initialize if corrupted
backlog init --force
```

---

**Issue**: Web UI won't open

**Solution**:
```bash
# 1. Check port availability
lsof -i :6420

# 2. Kill process using port
kill <PID>

# 3. Try different port
backlog browser --port 6421

# 4. Update config
# Edit backlog/config.yml:
# default_port: 6421
```

---

**Issue**: Git conflicts in backlog/

**Solution**:
```bash
# 1. Pull latest changes
git pull origin main

# 2. If conflicts, resolve manually
# Backlog files are markdown, easy to merge

# 3. For status conflicts, keep latest
git checkout --theirs backlog/tasks/task-012*.md

# 4. Commit resolution
git add backlog/
git commit -m "Resolve backlog conflicts"
```

---

**Issue**: Task dependencies not enforcing

**Solution**:
Backlog.md shows dependencies but doesn't enforce blocking. To enforce:

```bash
# Option 1: Use labels
# Add "blocked" status to dependent tasks manually

# Option 2: Script to check
#!/bin/bash
# scripts/check-dependencies.sh
TASK=$1
DEPS=$(grep "dependencies:" "backlog/tasks/task-$TASK*.md" | cut -d: -f2)

for dep in $DEPS; do
  STATUS=$(grep "status:" "backlog/tasks/$dep*.md" | cut -d: -f2)
  if [ "$STATUS" != "done" ]; then
    echo "⚠️ Cannot start task-$TASK: $dep is not complete"
    exit 1
  fi
done
```

### Performance Issues

**Large Number of Tasks** (1000+):

```bash
# 1. Archive completed tasks
backlog task archive --status done

# 2. Use filtering
backlog board --filter US1  # Instead of viewing all tasks

# 3. Consider splitting into multiple projects
# backlog-mvp/, backlog-v2/, etc.
```

### Getting Help

**Resources**:
- [Backlog.md Documentation](https://github.com/MrLesk/Backlog.md)
- [jp-spec-kit Issues](https://github.com/jpoley/jp-spec-kit/issues)
- [MCP Protocol Docs](https://modelcontextprotocol.io)

**Report Issues**:
```bash
# For jp-spec-kit integration issues
# Open issue at: https://github.com/jpoley/jp-spec-kit/issues

# For Backlog.md tool issues
# Open issue at: https://github.com/MrLesk/Backlog.md/issues
```

---

## /jpspec Command Integration

Backlog.md integrates seamlessly with the `/jpspec` workflow commands. Each command creates, discovers, or updates tasks in your backlog.

### Quick Reference

| Command | Backlog Action | Task State Change |
|---------|---------------|-------------------|
| `/jpspec:assess` | Labels with complexity | To Do → Assessed |
| `/jpspec:specify` | Creates implementation tasks | Assessed → Specified |
| `/jpspec:research` | Creates research + follow-up tasks | Specified → Researched |
| `/jpspec:plan` | Creates architecture/infra tasks | Researched → Planned |
| `/jpspec:implement` | Assigns and tracks existing tasks | Planned → In Implementation |
| `/jpspec:validate` | Validates task completion | In Implementation → Validated |
| `/jpspec:operate` | Creates operational tasks | Validated → Deployed |

### How Commands Use Backlog

**Design commands** (specify, research, plan) create tasks:

```bash
# /jpspec:specify creates tasks with acceptance criteria
backlog task create "Implement user login" \
  --ac "POST /auth/login returns JWT" \
  --ac "Invalid credentials return 401" \
  -l backend,US1
```

**Implementation commands** (implement, validate, operate) work from tasks:

```bash
# /jpspec:implement discovers and assigns tasks
backlog search "authentication" --plain
backlog task edit task-42 -s "In Progress" -a @backend-engineer
backlog task edit task-42 --check-ac 1  # Mark AC complete
```

### Task Format Requirements

For full `/jpspec` compatibility, tasks should include:

1. **Status field** - Valid workflow state (To Do, Specified, Planned, etc.)
2. **Acceptance criteria** - Numbered checkboxes for tracking
3. **Labels** - User story references (US1, US2) and categories

```markdown
---
id: task-042
status: To Do
labels: [backend, US1]
---

## Acceptance Criteria
- [ ] #1 First criterion
- [ ] #2 Second criterion
```

### Learn More

See **[JP Spec + Backlog.md Integration Guide](jpspec-backlog-workflow.md)** for:
- Complete workflow state transitions
- Task format specifications
- Command integration details
- Troubleshooting guide

---

**Status**: This integration is in active development. Some features (like automatic task generation) are coming soon.

**Feedback**: Your input helps shape this integration. Please share your experiences and suggestions!
