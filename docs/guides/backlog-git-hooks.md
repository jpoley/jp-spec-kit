# Backlog Git Hooks Guide

## Overview

The **post-commit-backlog-events** hook automatically emits flowspec events when backlog task files are modified through git commits.

## How It Works

```
User: backlog task edit 123 -s Done
    ↓
Backlog CLI modifies: backlog/tasks/task-123.md
    ↓
User: git add . && git commit -m "Complete task 123"
    ↓
Git post-commit hook fires
    ↓
Hook parses git diff to detect changes
    ↓
Hook emits: specify hooks emit task.completed --task-id task-123
    ↓
Matching hooks execute (CI, notifications, etc.)
```

## Events Emitted

| Change Detected | Event Emitted | Detection Method |
|----------------|---------------|------------------|
| New task file created | `task.created` | File added in commit |
| Task status changed | `task.status_changed` | `status:` field changed |
| Task marked as Done | `task.completed` | `status: Done` or `status: ○ Done` |
| AC checkbox changed | `task.ac_checked` | `- [x]` or `- [ ]` state changed |

## Installation

Create a symlink in your git hooks directory:

```bash
ln -sf ../../scripts/hooks/post-commit-backlog-events.sh .git/hooks/post-commit
```

### Verification

Check that the hook is installed:

```bash
ls -la .git/hooks/post-commit
```

You should see a symlink pointing to `../../scripts/hooks/post-commit-backlog-events.sh`.

## Requirements

- **specify CLI**: Must be installed and available in PATH
  ```bash
  uv tool install specify-cli
  ```
- **Git repository**: Hook only works in git-tracked projects
- **Backlog tasks**: Task files must be in `backlog/tasks/` directory

## Usage

The hook runs automatically after every `git commit`. No manual invocation needed.

### Example Workflow

1. Edit a task status:
   ```bash
   backlog task edit task-123 -s "In Progress"
   ```

2. Commit the change:
   ```bash
   git add backlog/tasks/task-123.md
   git commit -m "Start work on task 123"
   ```

3. Hook emits `task.status_changed` event automatically
   ```
   [post-commit-backlog-events] Status change detected for task-123: To Do → In Progress
   Emitting event: task.status_changed (task: task-123)
   ✓ run-tests completed in 1250ms
   ```

4. Configured hooks execute (tests, notifications, CI triggers, etc.)

## Limitations

### Not Real-Time

Events are only emitted **after a git commit**, not immediately when the backlog CLI modifies files.

**Impact**: There's a delay between running `backlog task edit` and event emission.

**Workaround**: Commit task changes immediately after editing:
```bash
backlog task edit task-123 -s Done && git add . && git commit -m "Complete task 123"
```

### Batched Changes

If multiple task files are modified in one commit, multiple events will be emitted sequentially.

**Example**:
```bash
backlog task edit task-100 -s Done
backlog task edit task-101 -s Done
git add . && git commit -m "Complete multiple tasks"
```

This will emit:
- `task.completed --task-id task-100`
- `task.completed --task-id task-101`

### Initial Commit Handling

On the very first commit in a repository, the hook compares against an empty tree. All task files will be treated as new and emit `task.created` events.

### Requires Git Workflow

This approach only works if you commit backlog changes to git. If you modify task files but don't commit, no events are emitted.

### Parse Errors

The hook parses markdown files using regex. If task file format changes significantly, the hook may fail to detect changes correctly.

**Robustness**: The hook is designed to fail silently (exit 0) if parsing errors occur, so it won't break your git workflow.

## Troubleshooting

### Hook Not Running

Check if the hook is installed and executable:

```bash
# Verify symlink
ls -la .git/hooks/post-commit

# Verify executable bit
ls -l scripts/hooks/post-commit-backlog-events.sh

# Make executable if needed
chmod +x scripts/hooks/post-commit-backlog-events.sh
```

### No Events Emitted

1. **Check specify is installed**:
   ```bash
   specify --version
   ```

2. **Run hook manually** (for debugging):
   ```bash
   .git/hooks/post-commit
   ```

3. **Check git diff output**:
   ```bash
   git diff --name-only HEAD~1 HEAD | grep backlog/tasks
   ```

### Hook Errors

The hook outputs colored logs to stderr during commit:

- **Green**: Events successfully emitted
- **Yellow**: Warnings (e.g., specify not found, invalid task ID)
- **Red**: Errors (should be rare)

If the hook fails, it may exit with a non-zero status, but git commit will still succeed (post-commit hooks do not block commits).

## Idempotency

The hook is **idempotent** - it's safe to run multiple times on the same commit:

- Uses `git diff HEAD~1 HEAD` to compare exactly two commit states
- Only emits events for detected changes between those commits
- Re-running won't emit duplicate events unless file content changed

## Testing

See `tests/test_post_commit_hook.py` for integration tests with mock git repositories.

Run tests:
```bash
pytest tests/test_post_commit_hook.py -v
```

## Alternative Approaches

If you need real-time event emission without git commits, consider:

1. **CLI Wrapper** (task-204.02): Wrap backlog CLI with automatic event emission
   ```bash
   ./scripts/backlog-wrapper.sh task edit task-123 -s Done
   ```

2. **Manual Emission**: Emit events manually after backlog commands
   ```bash
   backlog task edit task-123 -s Done && specify hooks emit task.completed --task-id task-123
   ```

3. **Upstream Contribution** (task-204.03): Contribute hook support to backlog.md project
   - Allows native event emission from backlog CLI
   - Long-term solution with better integration

## See Also

- [Workflow Configuration](./workflow-customization.md)
