# Backlog Git Hooks

This guide explains how to use git hooks to automatically emit flowspec events when backlog task files change.

## Overview

The `post-commit-backlog-events.sh` hook automatically detects changes to backlog task files and emits corresponding flowspec events. This enables:

- **Automated Workflows**: Trigger hooks when tasks are created, updated, or completed
- **Multi-Machine Observability**: Track task progress across distributed development environments
- **Integration with External Tools**: Connect backlog changes to CI/CD, notifications, or dashboards

## Events Emitted

| Event Type | Triggered When |
|------------|----------------|
| `task.created` | New task file added to `backlog/tasks/` |
| `task.status_changed` | Task status field changes (e.g., "To Do" to "In Progress") |
| `task.completed` | Task status changes to "Done" |
| `task.ac_checked` | Acceptance criteria checkboxes change |

## Installation

### Option 1: Using install-hooks.sh (Recommended)

```bash
./scripts/hooks/install-hooks.sh
```

This installs all git hooks including the post-commit backlog events hook.

### Option 2: Manual Installation

```bash
# Symlink the script to .git/hooks/post-commit
ln -s ../../scripts/hooks/post-commit-backlog-events.sh .git/hooks/post-commit

# Or copy it
cp scripts/hooks/post-commit-backlog-events.sh .git/hooks/post-commit
chmod +x .git/hooks/post-commit
```

## Usage

Once installed, the hook runs automatically after each commit. No manual action required.

### Example Workflow

```bash
# 1. Create a task
backlog task create "Implement login" --ac "AC 1" --ac "AC 2"

# 2. Commit the task file
git add backlog/tasks/
git commit -m "Create login task"
# → Hook emits: task.created for task-XXX

# 3. Start working on the task
backlog task edit XXX -s "In Progress"
git add backlog/tasks/
git commit -m "Start login task"
# → Hook emits: task.status_changed

# 4. Check off acceptance criteria
backlog task edit XXX --check-ac 1
git add backlog/tasks/
git commit -m "Complete AC 1"
# → Hook emits: task.ac_checked

# 5. Complete the task
backlog task edit XXX -s Done
git add backlog/tasks/
git commit -m "Complete login task"
# → Hook emits: task.completed
```

## Command Line Options

```bash
# Dry run - show what would be emitted without executing
./scripts/hooks/post-commit-backlog-events.sh --dry-run

# Verbose output
./scripts/hooks/post-commit-backlog-events.sh --verbose

# Both
./scripts/hooks/post-commit-backlog-events.sh --dry-run --verbose
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SPECIFY_CMD` | Path to specify CLI | `specify` |
| `DRY_RUN` | Set to `true` for dry-run mode | `false` |
| `VERBOSE` | Set to `true` for verbose output | `false` |

## Limitations

1. **Commit-based**: Events only fire on commit, not in real-time when files change
2. **Batched Changes**: Multiple task changes in one commit may batch into fewer events
3. **Git Workflow Required**: Requires committing after each backlog change for immediate events
4. **Requires flowspec CLI**: Event emission depends on `flowspec hooks emit` command

## Troubleshooting

### Events Not Firing

1. **Check hook is installed**:
   ```bash
   ls -la .git/hooks/post-commit
   ```

2. **Check hook is executable**:
   ```bash
   chmod +x .git/hooks/post-commit
   ```

3. **Test hook manually**:
   ```bash
   ./scripts/hooks/post-commit-backlog-events.sh --dry-run --verbose
   ```

4. **Check flowspec CLI is available**:
   ```bash
   which flowspec
   flowspec hooks emit --help
   ```

### Hook Fails Silently

The hook is designed to be resilient and not block commits. If events fail to emit, the commit still succeeds. Check:

```bash
# Run with verbose to see errors
VERBOSE=true ./scripts/hooks/post-commit-backlog-events.sh
```

### No Events for Some Changes

The hook only processes:
- Files in `backlog/tasks/` directory
- Files matching `task-*.md` pattern
- Status changes (not all metadata changes)
- AC checkbox changes

## Integration with Flowspec Hooks

Events emitted by this git hook trigger matching flowspec hooks configured in `.flowspec/hooks/hooks.yaml`:

```yaml
hooks:
  - name: notify-task-complete
    events:
      - type: task.completed
    script: notify-slack.sh
    description: Send Slack notification when task completes
    enabled: true
```

See [Hooks Guide](./hooks.md) for more details on configuring flowspec hooks.

## See Also

- [Backlog Quick Start](./backlog-quickstart.md)
- [Backlog User Guide](./backlog-user-guide.md)
- [Hooks Guide](./hooks.md)
- [Event System Reference](../reference/event-types.md)
