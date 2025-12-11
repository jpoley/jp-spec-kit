# Backlog.md Command Reference for Flowspec

Complete reference for all Backlog.md commands available in Flowspec projects.

## Table of Contents

- [Core Commands](#core-commands)
- [Task Management](#task-management)
- [Viewing and Filtering](#viewing-and-filtering)
- [Search and Query](#search-and-query)
- [Configuration](#configuration)
- [MCP Integration](#mcp-integration)
- [Git Integration](#git-integration)
- [Import/Export](#importexport)
- [Advanced Usage](#advanced-usage)

## Core Commands

### `backlog init`

Initialize Backlog.md in current project.

**Usage**:
```bash
backlog init [options]
```

**Options**:
- `--project-name <name>` - Set project name
- `--force` - Reinitialize existing backlog
- `--template <template>` - Use custom template

**Examples**:
```bash
# Basic initialization
backlog init

# Set project name
backlog init --project-name "my-project"

# Reinitialize
backlog init --force
```

**Creates**:
```
backlog/
├── config.yml
├── tasks/
├── docs/
└── decisions/
```

---

### `backlog board`

Display interactive Kanban board in terminal.

**Usage**:
```bash
backlog board [options]
```

**Options**:
- `--filter <label>` - Filter by label (e.g., US1, backend)
- `--assignee <email>` - Filter by assignee
- `--status <status>` - Filter by status
- `--milestone <name>` - Filter by milestone
- `--sort <field>` - Sort by: priority, created, updated
- `--reverse` - Reverse sort order

**Examples**:
```bash
# View all tasks
backlog board

# Filter by user story
backlog board --filter US1

# Filter by assignee
backlog board --assignee jane@example.com

# Filter by status
backlog board --status "In Progress"

# Combine filters
backlog board --filter backend --status todo --sort priority
```

**Navigation**:
- Arrow keys: Move between tasks
- Enter: View task details
- q: Quit

---

### `backlog browser`

Open web UI for visual task management.

**Usage**:
```bash
backlog browser [options]
```

**Options**:
- `--port <port>` - Port number (default: 6420)
- `--no-open` - Don't auto-open browser
- `--host <host>` - Bind to specific host (default: localhost)

**Examples**:
```bash
# Open browser UI
backlog browser

# Use different port
backlog browser --port 8080

# Don't auto-open browser
backlog browser --no-open
```

**Web UI Features**:
- Drag-and-drop tasks between columns
- Click tasks to edit inline
- Assign team members
- Add/remove labels
- Set priorities and milestones

---

### `backlog overview`

Display project summary and statistics.

**Usage**:
```bash
backlog overview [options]
```

**Options**:
- `--format <format>` - Output format: text, json, csv
- `--detailed` - Show detailed breakdown

**Examples**:
```bash
# Basic overview
backlog overview

# JSON output
backlog overview --format json

# Detailed breakdown
backlog overview --detailed
```

**Output**:
```
Project: your-project
Total Tasks: 42
━━━━━━━━━━━━━━━━━━━━━━
To Do:        34 (81%)
In Progress:   5 (12%)
Done:          3 (7%)

By User Story:
  US1: 15 tasks (5 done)
  US2: 12 tasks (0 done)
  US3: 10 tasks (0 done)

By Priority:
  High:   20 tasks
  Medium: 15 tasks
  Low:     7 tasks
```

## Task Management

### `backlog task create`

Create a new task.

**Usage**:
```bash
backlog task create <title> [options]
```

**Options**:
- `--labels <labels>` - Comma-separated labels
- `--status <status>` - Initial status (default: To Do)
- `--priority <priority>` - high, medium, low
- `--assignee <email>` - Assign to team member
- `--dependencies <ids>` - Comma-separated task IDs
- `--milestone <name>` - Assign to milestone
- `--description <text>` - Task description
- `--template <template>` - Use task template

**Examples**:
```bash
# Simple task
backlog task create "Implement user login"

# Full metadata
backlog task create "Create User model" \
  --labels "backend,US1,implementation" \
  --status "To Do" \
  --priority "high" \
  --assignee "dev@example.com" \
  --dependencies "task-005,task-008" \
  --milestone "MVP Launch"

# With description
backlog task create "Setup database" \
  --description "Initialize PostgreSQL database with authentication schema"

# From template
backlog task create "New feature" --template feature-task
```

**Returns**:
```
✅ Created task-042: Implement user login
   📁 backlog/tasks/task-042-implement-user-login.md
```

---

### `backlog task edit`

Edit existing task (opens in $EDITOR).

**Usage**:
```bash
backlog task edit <task-id> [options]
```

**Options**:
- `--field <field>` - Edit specific field only
- `--value <value>` - Set field to value (with --field)

**Examples**:
```bash
# Open in editor
backlog task edit task-012

# Update specific field
backlog task edit task-012 --field status --value "In Progress"
backlog task edit task-012 --field priority --value high
backlog task edit task-012 --field assignee --value "jane@example.com"
```

---

### `backlog task view`

Display task details.

**Usage**:
```bash
backlog task view <task-id> [options]
```

**Options**:
- `--format <format>` - Output format: text, json, yaml
- `--show-dependencies` - Show dependency tree

**Examples**:
```bash
# View task
backlog task view task-012

# JSON output
backlog task view task-012 --format json

# Show what blocks this task
backlog task view task-012 --show-dependencies
```

**Output**:
```
Task: task-012
Title: Create User model
Status: In Progress
Priority: High
Assignee: dev@example.com
Labels: backend, US1, implementation
Dependencies: task-005 (✅ done), task-008 (⏳ in_progress)

Description:
Create User model in src/models/user.py with authentication fields

Acceptance Criteria:
- [ ] Model includes email, password_hash, created_at
- [ ] Password hashing with bcrypt
- [ ] Migration creates users table
```

---

### `backlog task delete`

Delete a task (moves to archive).

**Usage**:
```bash
backlog task delete <task-id> [options]
```

**Options**:
- `--permanent` - Permanently delete (no archive)
- `--force` - Skip confirmation

**Examples**:
```bash
# Archive task
backlog task delete task-012

# Permanently delete
backlog task delete task-012 --permanent --force
```

---

### `backlog task archive`

Archive completed or irrelevant tasks.

**Usage**:
```bash
backlog task archive <task-id> [options]
```

**Options**:
- `--status <status>` - Archive all tasks with status
- `--before <date>` - Archive tasks completed before date

**Examples**:
```bash
# Archive single task
backlog task archive task-012

# Archive all done tasks
backlog task archive --status done

# Archive old tasks
backlog task archive --before 2025-01-01
```

**Note**: Archived tasks move to `backlog/archive/` and are excluded from board views.

## Viewing and Filtering

### `backlog list`

List tasks with filtering and sorting.

**Usage**:
```bash
backlog list [options]
```

**Options**:
- `--filter <label>` - Filter by label
- `--status <status>` - Filter by status
- `--assignee <email>` - Filter by assignee
- `--priority <priority>` - Filter by priority
- `--sort <field>` - Sort by: id, title, priority, created, updated
- `--format <format>` - Output format: text, json, csv, table

**Examples**:
```bash
# List all tasks
backlog list

# Filter by user story
backlog list --filter US1

# High priority todos
backlog list --status todo --priority high

# Sort by creation date
backlog list --sort created

# CSV export
backlog list --format csv > tasks.csv

# Combine filters
backlog list --filter backend --assignee dev@example.com --sort priority
```

---

### `backlog graph`

Display dependency graph.

**Usage**:
```bash
backlog graph [options]
```

**Options**:
- `--format <format>` - Output format: ascii, dot, mermaid
- `--filter <label>` - Show only tasks with label
- `--critical-path` - Highlight critical path

**Examples**:
```bash
# ASCII graph
backlog graph

# Mermaid diagram
backlog graph --format mermaid > dependencies.mmd

# DOT format (for Graphviz)
backlog graph --format dot | dot -Tpng > graph.png

# Critical path
backlog graph --critical-path
```

**Output (ASCII)**:
```
task-001 (Create project structure)
├── task-005 (Database schema)
│   ├── task-012 (User model)
│   │   └── task-013 (Login endpoint)
│   └── task-015 (Auth middleware)
└── task-002 (Initialize tests)
```

## Search and Query

### `backlog search`

Search tasks by keyword.

**Usage**:
```bash
backlog search <query> [options]
```

**Options**:
- `--title` - Search in titles only
- `--content` - Search in content only
- `--labels` - Search in labels
- `--case-sensitive` - Case-sensitive search
- `--format <format>` - Output format

**Examples**:
```bash
# Search all fields
backlog search "authentication"

# Search titles only
backlog search "login" --title

# Search with label filter
backlog search "model" --labels backend

# Case-sensitive
backlog search "User" --case-sensitive
```

---

### `backlog query`

Advanced querying with expressions.

**Usage**:
```bash
backlog query <expression> [options]
```

**Expressions**:
- `status:todo` - Tasks with todo status
- `priority:high` - High priority tasks
- `assignee:jane@example.com` - Assigned to Jane
- `label:US1` - Has US1 label
- `created:<2025-01-01` - Created before date
- `updated:>2025-11-20` - Updated after date
- `AND`, `OR`, `NOT` - Combine conditions

**Examples**:
```bash
# High priority todos
backlog query "status:todo AND priority:high"

# Backend tasks for US1 or US2
backlog query "label:backend AND (label:US1 OR label:US2)"

# Unassigned high priority
backlog query "priority:high AND NOT assignee:*"

# Recent updates
backlog query "updated:>2025-11-20"

# Complex query
backlog query "status:in_progress AND assignee:dev@example.com AND created:<2025-11-01"
```

## Configuration

### `backlog config`

View or modify configuration.

**Usage**:
```bash
backlog config [key] [value] [options]
```

**Options**:
- `--global` - Modify global config
- `--local` - Modify project config (default)
- `--list` - List all configuration

**Examples**:
```bash
# List config
backlog config --list

# Get value
backlog config default_status

# Set value
backlog config default_status "In Progress"

# Set global config
backlog config --global auto_open_browser false

# Edit config file
backlog config --edit
```

**Common Settings**:
```yaml
project_name: "your-project"
default_status: "To Do"
statuses: ["To Do", "In Progress", "Done"]
labels: [bug, feature, documentation]
default_port: 6420
auto_open_browser: true
```

## MCP Integration

### `backlog mcp start`

Start MCP server for AI integration.

**Usage**:
```bash
backlog mcp start [options]
```

**Options**:
- `--port <port>` - MCP server port
- `--log-level <level>` - debug, info, warn, error

**Examples**:
```bash
# Start MCP server
backlog mcp start

# With debug logging
backlog mcp start --log-level debug
```

**Note**: Usually configured in `.mcp.json` and started automatically by Claude Code.

---

### MCP Tools Available

When MCP server is running, AI assistants can use:

| Tool | Description | Example |
|------|-------------|---------|
| `backlog_list_tasks` | List tasks with filters | "Show me all US1 tasks" |
| `backlog_create_task` | Create new task | "Create a task for login" |
| `backlog_update_task` | Update task metadata | "Mark task-12 as done" |
| `backlog_get_task` | Get task details | "Show me task-12" |
| `backlog_search` | Search tasks | "Find all authentication tasks" |
| `backlog_archive_task` | Archive task | "Archive task-42" |

## Git Integration

### `backlog git status`

Show git status of backlog directory.

**Usage**:
```bash
backlog git status
```

**Output**:
```
Modified tasks: 3
  task-012-user-model.md (status: todo → in_progress)
  task-013-login-endpoint.md (assignee: → dev@example.com)
  task-015-auth-middleware.md (new)
```

---

### `backlog git commit`

Commit task changes.

**Usage**:
```bash
backlog git commit [message] [options]
```

**Options**:
- `--auto` - Auto-generate commit message
- `--push` - Push after commit

**Examples**:
```bash
# Manual message
backlog git commit "Update US1 task status"

# Auto-generate message
backlog git commit --auto

# Commit and push
backlog git commit --auto --push
```

## Import/Export

### `backlog export`

Export tasks to various formats.

**Usage**:
```bash
backlog export [options]
```

**Options**:
- `--format <format>` - csv, json, markdown, jira, linear
- `--output <file>` - Output file
- `--filter <label>` - Export only filtered tasks

**Examples**:
```bash
# Export to CSV
backlog export --format csv --output tasks.csv

# Export to JSON
backlog export --format json > backup.json

# Export US1 tasks to Markdown
backlog export --format markdown --filter US1 > us1-tasks.md

# Export to Jira format
backlog export --format jira --output jira-import.csv
```

---

### `backlog import`

Import tasks from external sources.

**Usage**:
```bash
backlog import <file> [options]
```

**Options**:
- `--format <format>` - csv, json, jira, linear, trello
- `--mapping <file>` - Field mapping configuration
- `--dry-run` - Preview import without creating tasks

**Examples**:
```bash
# Import from CSV
backlog import tasks.csv --format csv

# Import from Jira export
backlog import jira-export.csv --format jira

# Preview import
backlog import tasks.json --format json --dry-run

# Custom field mapping
backlog import external.csv --mapping field-mapping.yml
```

## Advanced Usage

### Batch Operations

**Update multiple tasks**:
```bash
# Mark all US1 tasks as high priority
for task in backlog/tasks/*US1*.md; do
  backlog task edit $(basename $task .md) --field priority --value high
done

# Assign all backend tasks to developer
backlog query "label:backend AND status:todo" --format json | \
  jq -r '.[] | .id' | \
  xargs -I {} backlog task edit {} --field assignee --value "dev@example.com"
```

**Archive completed tasks**:
```bash
# Archive all done tasks older than 30 days
backlog task archive --status done --before $(date -d '30 days ago' +%Y-%m-%d)
```

### Scripting

**Check for blocked tasks**:
```bash
#!/bin/bash
# scripts/check-blocked-tasks.sh

BLOCKED=$(backlog list --status blocked --format json)
COUNT=$(echo "$BLOCKED" | jq length)

if [ $COUNT -gt 0 ]; then
  echo "⚠️ $COUNT blocked tasks found:"
  echo "$BLOCKED" | jq -r '.[] | "  - \(.id): \(.title)"'
  exit 1
fi
```

**Auto-complete tasks when tests pass**:
```bash
#!/bin/bash
# .github/workflows/auto-complete-task.sh

TASK_ID=$1
TEST_RESULT=$2

if [ "$TEST_RESULT" = "success" ]; then
  backlog task edit "task-$TASK_ID" --field status --value done
  git add backlog/
  git commit -m "Auto-complete task-$TASK_ID: tests passed"
fi
```

### Integration Patterns

**Slack notifications**:
```bash
# Send blocked tasks to Slack daily
backlog list --status blocked --format json | \
  jq -r '.[] | "Task \(.id) is blocked: \(.title)"' | \
  while read line; do
    curl -X POST -H 'Content-type: application/json' \
      --data "{\"text\":\"$line\"}" \
      $SLACK_WEBHOOK_URL
  done
```

**GitHub issues sync**:
```bash
# Create GitHub issue for each backlog task
backlog list --filter needs-github-issue --format json | \
  jq -r '.[] | @base64' | \
  while read task; do
    TITLE=$(echo $task | base64 -d | jq -r .title)
    BODY=$(echo $task | base64 -d | jq -r .description)
    gh issue create --title "$TITLE" --body "$BODY"
  done
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BACKLOG_ROOT` | Backlog directory path | `./backlog` |
| `BACKLOG_EDITOR` | Editor for task editing | `$EDITOR` |
| `BACKLOG_PORT` | Default web UI port | `6420` |
| `BACKLOG_MCP_PORT` | MCP server port | `6421` |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | Task not found |
| 4 | Configuration error |
| 5 | Git operation failed |

## Tips and Tricks

### Aliases

Add to `.bashrc` or `.zshrc`:

```bash
alias bb='backlog board'
alias bt='backlog task'
alias bl='backlog list'
alias bs='backlog search'

# Quick task creation
function btc() {
  backlog task create "$1" --labels "$2"
}

# View US1 tasks
alias bus1='backlog board --filter US1'
```

### Keyboard Shortcuts (in board)

- `j/k` - Navigate up/down
- `h/l` - Navigate left/right (between columns)
- `Enter` - View task details
- `/` - Search
- `f` - Filter by label
- `s` - Sort tasks
- `r` - Refresh
- `q` - Quit

### Performance

For large backlogs (1000+ tasks):

```bash
# Use filtering instead of viewing all
backlog board --filter US1

# Archive old completed tasks
backlog task archive --status done --before 2025-01-01

# Use list instead of board for bulk operations
backlog list --format json | jq '...'
```

---

## See Also

- [Backlog.md Quick Start](../guides/backlog-quickstart.md)
- [Backlog.md User Guide](../guides/backlog-user-guide.md)
- [Migration Guide](../guides/backlog-migration.md)
- [Backlog.md Official Docs](https://github.com/MrLesk/Backlog.md)

---

**Last Updated**: 2025-11-24
**Version**: 1.0 (based on Backlog.md v1.20.1)
