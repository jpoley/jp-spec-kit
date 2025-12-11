# Backlog CLI Wrapper (bk)

The `bk` wrapper provides automatic event emission for backlog commands, enabling seamless integration with the flowspec hooks system.

## Overview

Instead of using `backlog` directly, you can use the `bk` wrapper which:
- Passes all arguments transparently to the `backlog` CLI
- Automatically emits flowspec events after successful operations
- Preserves exit codes and output
- Works with both bash and zsh

## Installation

### Option 1: Add to PATH

Add the wrapper to your PATH in your shell configuration:

```bash
# In ~/.bashrc or ~/.zshrc
export PATH="$PATH:/path/to/flowspec/scripts/bin"
```

Then use `bk` directly:
```bash
bk task create "My task"
bk task edit task-123 -s Done
```

### Option 2: Shell Alias

Create an alias in your shell configuration:

```bash
# In ~/.bashrc or ~/.zshrc
alias bk='/path/to/flowspec/scripts/bin/bk'
```

### Option 3: Direct Usage

Use the full path to the wrapper:

```bash
/path/to/flowspec/scripts/bin/bk task create "My task"
```

## Usage

Use `bk` exactly as you would use `backlog`:

```bash
# Create tasks
bk task create "Implement feature X" --ac "First criterion" --ac "Second criterion"

# Edit tasks
bk task edit task-123 -s "In Progress"
bk task edit task-123 --check-ac 1
bk task edit task-123 -s Done

# List and view tasks
bk task list
bk task view task-123

# All other backlog commands work too
bk board
bk search "keyword"
bk doc create "My Document"
```

## Events Emitted

The wrapper automatically emits the following flowspec events:

| Command | Event Emitted | When |
|---------|---------------|------|
| `bk task create "Title"` | `task.created` | After task is successfully created |
| `bk task edit <id> -s "Status"` | `task.status_changed` | When status is changed to any value except "Done" |
| `bk task edit <id> -s Done` | `task.completed` | When status is changed to "Done" |
| `bk task edit <id> --check-ac N` | `task.ac_checked` | When any acceptance criterion is checked |
| `bk task edit <id> --uncheck-ac N` | `task.ac_checked` | When any acceptance criterion is unchecked |

### Event Context

Events include the following context:
- `task_id`: The task identifier (e.g., "task-123")
- All standard flowspec event metadata (timestamp, project_root, etc.)

### Hook Integration

These events can trigger hooks defined in `.specify/hooks/hooks.yaml`. For example:

```yaml
version: "1.0"
hooks:
  - name: notify-on-task-completion
    events:
      - type: task.completed
    script: scripts/notify-slack.sh
    fail_mode: warn
```

## Behavior

### Exit Code Preservation

The wrapper preserves the exact exit code from the `backlog` CLI:

```bash
bk task view nonexistent  # Exits with backlog's exit code (non-zero)
echo $?  # Shows the actual error code
```

### Event Emission on Success Only

Events are only emitted if the underlying `backlog` command succeeds (exit code 0). If the command fails, no events are emitted.

### Silent Event Emission

Event emission happens in the background and won't interrupt your workflow:
- If event emission fails (e.g., hooks system not configured), the wrapper continues normally
- Event emission errors are suppressed (stderr redirected to /dev/null)
- The wrapper's exit code is always the backlog command's exit code, never from event emission

### Output Preservation

All output from the backlog CLI is preserved exactly:

```bash
bk task create "My task"
# Output:
# Created task task-123
# File: /path/to/backlog/tasks/task-123 - My-task.md
# No hooks matched this event                     # From hooks system
```

## Shell Compatibility

The wrapper is implemented in bash but works with:
- **bash** (3.2+)
- **zsh** (any recent version)

It uses portable bash features and should work on:
- Linux (all distributions)
- macOS
- WSL (Windows Subsystem for Linux)
- Git Bash (Windows)

## Troubleshooting

### "specify: command not found"

The wrapper requires the `specify` CLI to emit events. Install it:

```bash
cd /path/to/flowspec
uv tool install . --force
```

### Events not triggering hooks

Check that hooks are configured:

```bash
# Validate hooks configuration
specify hooks validate

# List configured hooks
specify hooks list

# View audit log to see if events are being received
specify hooks audit --tail 10
```

### Wrapper not found

Make sure the wrapper is executable and in your PATH:

```bash
chmod +x /path/to/flowspec/scripts/bin/bk
export PATH="$PATH:/path/to/flowspec/scripts/bin"
```

## Examples

### Basic Task Workflow

```bash
# Create a task
bk task create "Implement user authentication" \
  --ac "Backend API endpoints" \
  --ac "Frontend login form" \
  --ac "Tests passing" \
  -l backend,frontend

# Start working on it
bk task edit task-456 -s "In Progress" -a @myself

# Check acceptance criteria as you complete them
bk task edit task-456 --check-ac 1  # Backend done
bk task edit task-456 --check-ac 2  # Frontend done
bk task edit task-456 --check-ac 3  # Tests done

# Complete the task
bk task edit task-456 -s Done
```

### With Hooks Integration

Configure hooks to automatically run tests when tasks are completed:

```yaml
# .specify/hooks/hooks.yaml
version: "1.0"
hooks:
  - name: run-tests-on-completion
    events:
      - type: task.completed
    command: "pytest tests/"
    fail_mode: fail
    timeout: 300
```

Then:

```bash
bk task edit task-456 -s Done
# Output:
# Updated task task-456
# Emitting event: task.completed (task: task-456)
# Executed 1 hook(s):
# ✓ run-tests-on-completion (exit=0, 1234ms)
```

### Event-Driven Workflows

Use hooks to automate workflows:

```yaml
version: "1.0"
hooks:
  # Automatically create GitHub issue when task is created
  - name: sync-to-github
    events:
      - type: task.created
    script: scripts/create-github-issue.sh

  # Send Slack notification when task is completed
  - name: notify-team
    events:
      - type: task.completed
    script: scripts/notify-slack.sh

  # Update project board when task status changes
  - name: update-board
    events:
      - type: task.status_changed
      - type: task.completed
    script: scripts/update-project-board.sh
```

## Implementation Details

### Architecture

```
User: bk task edit 123 -s Done
    ↓
Wrapper: backlog task edit 123 -s Done
    ↓
Backlog CLI executes normally
    ↓
Wrapper detects: status changed to Done
    ↓
Wrapper emits: specify hooks emit task.completed --task-id task-123
    ↓
Hooks system executes matching hooks
```

### Command Detection

The wrapper parses command-line arguments to detect:

1. **Task create**: Extracts task ID from output regex `Created task task-([0-9]+)`
2. **Status changes**: Looks for `-s` or `--status` flags
3. **AC operations**: Looks for `--check-ac` or `--uncheck-ac` flags

### Event Emission

Events are emitted using the specify hooks CLI:

```bash
specify hooks emit task.created --task-id task-123
specify hooks emit task.completed --task-id task-123
specify hooks emit task.status_changed --task-id task-123
specify hooks emit task.ac_checked --task-id task-123
```

## Limitations

1. **Requires specify CLI**: The wrapper depends on the `specify` CLI being installed
2. **Bash/Zsh only**: Won't work in other shells (fish, PowerShell) without modification
3. **Pattern matching**: Event detection relies on parsing command-line arguments and output
4. **No event suppression**: Can't disable event emission for individual commands (use `backlog` directly if needed)

## Related Documentation

- [Backlog CLI User Guide](backlog-user-guide.md)
- [Flowspec Hooks System](../reference/hooks.md)
- [Event Types Reference](../reference/event-types.md)
- [Hook Configuration](../guides/hook-configuration.md)
