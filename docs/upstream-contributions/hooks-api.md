# Backlog.md Hooks API

**Status**: Documentation for Upstream Contribution
**Target Repository**: https://github.com/MrLesk/Backlog.md

## Overview

Backlog.md hooks allow you to run custom scripts when task lifecycle events occur. Hooks are executable scripts placed in `.backlog/hooks/` that receive context via environment variables.

## Quick Start

### 1. Create Hooks Directory

```bash
mkdir -p .backlog/hooks
```

### 2. Create a Hook Script

```bash
cat > .backlog/hooks/post-task-create.sh << 'EOF'
#!/bin/bash
echo "New task created: $BACKLOG_TASK_ID - $BACKLOG_TASK_TITLE"
EOF
chmod +x .backlog/hooks/post-task-create.sh
```

### 3. Test It

```bash
backlog task create "Test hooks integration"
# Output: New task created: task-XXX - Test hooks integration
```

## Available Hooks

### post-task-create

Triggered after a task file is successfully created and committed.

**Environment Variables**:
```bash
BACKLOG_HOOK_EVENT=post-task-create
BACKLOG_TASK_ID=task-42
BACKLOG_TASK_TITLE="Implement feature X"
BACKLOG_TASK_STATUS="To Do"
BACKLOG_TASK_ASSIGNEE="@user1,@user2"  # comma-separated list
```

**Example Use Cases**:
- Initialize task memory context
- Send notifications to team chat
- Create related resources (branches, boards, etc.)
- Log task creation metrics

**Example Script**:
```bash
#!/bin/bash
# .backlog/hooks/post-task-create.sh

# Send Slack notification
curl -X POST https://hooks.slack.com/... \
  -d "New task: [$BACKLOG_TASK_ID] $BACKLOG_TASK_TITLE"

# Initialize task memory
if command -v speckit &> /dev/null; then
    speckit memory capture "$BACKLOG_TASK_ID"
fi
```

### post-task-update

Triggered after task metadata is successfully updated and committed.

**Environment Variables**:
```bash
BACKLOG_HOOK_EVENT=post-task-update
BACKLOG_TASK_ID=task-42
BACKLOG_TASK_TITLE="Implement feature X"
BACKLOG_TASK_STATUS="In Progress"
BACKLOG_OLD_STATUS="To Do"              # only if status changed
BACKLOG_NEW_STATUS="In Progress"        # only if status changed
BACKLOG_TASK_ASSIGNEE="@backend-engineer"
```

**Status Change Detection**:
When a task status changes, both `BACKLOG_OLD_STATUS` and `BACKLOG_NEW_STATUS` are set. For other updates (title, assignee, etc.), these variables are not set.

**Example Use Cases**:
- Capture task context when work begins (status → "In Progress")
- Archive task memory when work completes (status → "Done")
- Update external project management tools
- Trigger CI/CD pipelines on status changes
- Send status change notifications

**Example Script**:
```bash
#!/bin/bash
# .backlog/hooks/post-task-update.sh

# Capture context when task starts
if [[ "$BACKLOG_NEW_STATUS" == "In Progress" && "$BACKLOG_OLD_STATUS" != "In Progress" ]]; then
    echo "[$(date)] Task started: $BACKLOG_TASK_ID"
    speckit memory capture "$BACKLOG_TASK_ID"
fi

# Notify team when task completes
if [[ "$BACKLOG_NEW_STATUS" == "Done" ]]; then
    curl -X POST https://hooks.slack.com/... \
      -d "✅ Task completed: [$BACKLOG_TASK_ID] $BACKLOG_TASK_TITLE"
fi

# Update external tracker
if [[ -n "$BACKLOG_OLD_STATUS" && -n "$BACKLOG_NEW_STATUS" ]]; then
    python scripts/sync_to_jira.py "$BACKLOG_TASK_ID" "$BACKLOG_NEW_STATUS"
fi
```

### post-task-archive

Triggered after a task is successfully archived (moved to archive directory).

**Environment Variables**:
```bash
BACKLOG_HOOK_EVENT=post-task-archive
BACKLOG_TASK_ID=task-42
BACKLOG_TASK_TITLE="Implement feature X"
```

**Example Use Cases**:
- Archive task memory files
- Clean up related resources
- Update completion metrics
- Trigger post-completion workflows

**Example Script**:
```bash
#!/bin/bash
# .backlog/hooks/post-task-archive.sh

# Archive task memory
if command -v speckit &> /dev/null; then
    speckit memory archive "$BACKLOG_TASK_ID"
fi

# Log completion metrics
echo "$(date -u +%s),$BACKLOG_TASK_ID,archived" >> .backlog/metrics.csv

# Clean up branch if it exists
BRANCH_NAME="task/$BACKLOG_TASK_ID"
if git show-ref --verify --quiet "refs/heads/$BRANCH_NAME"; then
    git branch -d "$BRANCH_NAME" 2>/dev/null
fi
```

## Configuration

Configure hooks in `.backlog/config.yml`:

```yaml
hooks:
  enabled: true                    # Global enable/disable (default: true)
  directory: .backlog/hooks        # Custom hook directory (default: .backlog/hooks)
  timeout: 5000                    # Timeout in milliseconds (default: 5000)
  logLevel: info                   # Logging level: none, error, info, debug (default: info)
```

### Configuration Options

#### enabled
Type: `boolean`
Default: `true`

Globally enable or disable all hooks. When disabled, no hook scripts will be executed.

```yaml
hooks:
  enabled: false  # Disable all hooks
```

#### directory
Type: `string`
Default: `.backlog/hooks`

Custom directory for hook scripts. Useful for sharing hooks across projects or organizing hooks differently.

```yaml
hooks:
  directory: scripts/backlog-hooks  # Custom location
```

#### timeout
Type: `number` (milliseconds)
Default: `5000`

Maximum execution time for hook scripts. Scripts exceeding this timeout are terminated.

```yaml
hooks:
  timeout: 10000  # 10 second timeout
```

#### logLevel
Type: `string`
Default: `info`
Values: `none`, `error`, `info`, `debug`

Control hook logging verbosity:
- `none`: No logging
- `error`: Only log errors
- `info`: Log hook execution
- `debug`: Verbose logging with script paths and environment

```yaml
hooks:
  logLevel: debug  # Verbose logging
```

## Hook Execution Model

### Execution Flow

```
┌─────────────────────────────┐
│  User runs backlog command  │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  Core operation executes    │
│  (create/update/archive)    │
└────────────┬────────────────┘
             │
             ▼ [Success]
┌─────────────────────────────┐
│  Hook system checks for     │
│  matching hook script       │
└────────────┬────────────────┘
             │
             ▼ [Script exists + executable]
┌─────────────────────────────┐
│  Execute hook with timeout  │
│  (async, non-blocking)      │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  User gets CLI result       │
│  (hook runs in background)  │
└─────────────────────────────┘
```

### Execution Guarantees

1. **Fail-Safe**: Hook failures never block task operations
2. **Async**: Hooks run in background (non-blocking)
3. **Timeout**: Hooks are killed after timeout expires
4. **Post-Success**: Hooks only fire after successful operations

### Error Handling

Hook scripts that fail (non-zero exit code) are logged but do not affect the CLI operation:

```bash
# This hook fails but task creation still succeeds
#!/bin/bash
exit 1  # Hook fails, task still created
```

## Best Practices

### 1. Keep Hooks Fast

Hooks run after CLI commands. Keep them fast to maintain responsive CLI:

```bash
# Good: Quick notification
curl -X POST https://api.slack.com/...

# Bad: Long-running operation (use background jobs instead)
#!/bin/bash
# DON'T do this - blocks for 30 seconds
sleep 30
complex_operation_that_takes_forever
```

For long operations, spawn background jobs:

```bash
#!/bin/bash
# Spawn background job and exit immediately
nohup python long_running_script.py "$BACKLOG_TASK_ID" &> /dev/null &
```

### 2. Handle Missing Commands

Not all environments have the same tools installed:

```bash
#!/bin/bash
if command -v speckit &> /dev/null; then
    speckit memory capture "$BACKLOG_TASK_ID"
else
    echo "Warning: speckit not installed" >&2
fi
```

### 3. Use Absolute Paths

Hook scripts may be executed from different working directories:

```bash
#!/bin/bash
# Bad: relative path
./scripts/sync.py "$BACKLOG_TASK_ID"

# Good: absolute path or find project root
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
"$PROJECT_ROOT/scripts/sync.py" "$BACKLOG_TASK_ID"
```

### 4. Log Hook Activity

Create audit trails for debugging:

```bash
#!/bin/bash
LOG_FILE=".backlog/hooks.log"
echo "[$(date -Iseconds)] $BACKLOG_HOOK_EVENT: $BACKLOG_TASK_ID" >> "$LOG_FILE"
```

### 5. Test Hooks Thoroughly

Test hooks before relying on them:

```bash
# Test by creating a test task
backlog task create "Test hook" --status "To Do"

# Check hook execution
tail -f .backlog/hooks.log

# Verify hook outputs
ls -la expected_output_file
```

### 6. Version Control Hooks

Commit hooks to share workflows with team:

```bash
git add .backlog/hooks/
git commit -m "Add task lifecycle hooks"
```

Add execute permissions in Git:
```bash
git update-index --chmod=+x .backlog/hooks/post-task-create.sh
```

### 7. Document Hook Dependencies

Document required tools in README:

```markdown
## Development Setup

This project uses backlog.md hooks that require:
- `curl` (for notifications)
- `jq` (for JSON processing)
- `speckit` (for task memory)
```

## Advanced Use Cases

### Task Memory Integration

Automatically capture and archive task context:

```bash
#!/bin/bash
# .backlog/hooks/post-task-update.sh

case "$BACKLOG_NEW_STATUS" in
    "In Progress")
        # Capture context when work starts
        speckit memory capture "$BACKLOG_TASK_ID"
        ;;
    "Done"|"Blocked")
        # Save snapshot on completion or blocker
        speckit memory snapshot "$BACKLOG_TASK_ID"
        ;;
esac
```

### Multi-Tool Notifications

Send notifications to multiple channels:

```bash
#!/bin/bash
# .backlog/hooks/post-task-update.sh

if [[ -n "$BACKLOG_OLD_STATUS" && -n "$BACKLOG_NEW_STATUS" ]]; then
    MESSAGE="Task $BACKLOG_TASK_ID: $BACKLOG_OLD_STATUS → $BACKLOG_NEW_STATUS"

    # Slack
    curl -X POST "$SLACK_WEBHOOK_URL" -d "text=$MESSAGE"

    # Email
    echo "$MESSAGE" | mail -s "Backlog Update" team@example.com

    # Desktop notification
    notify-send "Backlog" "$MESSAGE"
fi
```

### Analytics and Metrics

Track task lifecycle metrics:

```bash
#!/bin/bash
# .backlog/hooks/post-task-create.sh

METRICS_FILE=".backlog/metrics.csv"
TIMESTAMP=$(date -u +%s)

# CSV format: timestamp,task_id,event,status,assignee
echo "$TIMESTAMP,$BACKLOG_TASK_ID,created,$BACKLOG_TASK_STATUS,$BACKLOG_TASK_ASSIGNEE" \
    >> "$METRICS_FILE"
```

Generate reports:
```bash
# Daily task creation count
awk -F',' '$3=="created"' .backlog/metrics.csv | wc -l

# Average time in progress (requires both create and archive events)
```

### External System Integration

Sync with Jira, GitHub Issues, Linear, etc.:

```bash
#!/bin/bash
# .backlog/hooks/post-task-update.sh

if [[ -n "$BACKLOG_NEW_STATUS" ]]; then
    # Map backlog status to Jira status
    case "$BACKLOG_NEW_STATUS" in
        "In Progress") JIRA_STATUS="In Progress" ;;
        "Done") JIRA_STATUS="Done" ;;
        *) JIRA_STATUS="To Do" ;;
    esac

    # Update Jira via API
    python scripts/update_jira.py \
        --task-id "$BACKLOG_TASK_ID" \
        --status "$JIRA_STATUS"
fi
```

### CI/CD Triggers

Trigger builds or deployments on status changes:

```bash
#!/bin/bash
# .backlog/hooks/post-task-update.sh

if [[ "$BACKLOG_NEW_STATUS" == "Ready for Review" ]]; then
    # Trigger CI pipeline
    gh workflow run ci.yml \
        --ref "task/$BACKLOG_TASK_ID" \
        -f task_id="$BACKLOG_TASK_ID"
fi
```

## Troubleshooting

### Hook Not Executing

**Symptoms**: Hook script exists but doesn't run.

**Checks**:
1. Is the script executable?
   ```bash
   ls -l .backlog/hooks/post-task-create.sh
   # Should show: -rwxr-xr-x
   ```

2. Make it executable:
   ```bash
   chmod +x .backlog/hooks/post-task-create.sh
   ```

3. Check hooks are enabled:
   ```bash
   cat .backlog/config.yml | grep -A 3 hooks
   # Should show: enabled: true
   ```

4. Test hook manually:
   ```bash
   BACKLOG_TASK_ID=task-test \
   BACKLOG_TASK_TITLE="Test" \
   .backlog/hooks/post-task-create.sh
   ```

### Hook Timing Out

**Symptoms**: Hook logs show timeout errors.

**Solutions**:
1. Increase timeout:
   ```yaml
   # .backlog/config.yml
   hooks:
     timeout: 10000  # 10 seconds
   ```

2. Move slow operations to background:
   ```bash
   #!/bin/bash
   # Run slow operation in background
   (
     sleep 30
     complex_operation
   ) &
   ```

3. Optimize hook script performance

### Environment Variables Not Set

**Symptoms**: Variables like `$BACKLOG_TASK_TITLE` are empty.

**Causes**:
- Not all variables are set for all events
- Variable only set when data is available

**Check availability**:
```bash
#!/bin/bash
# Debug script to see all available variables
env | grep BACKLOG | sort
```

**Guard against missing variables**:
```bash
#!/bin/bash
if [[ -n "$BACKLOG_TASK_TITLE" ]]; then
    echo "Title: $BACKLOG_TASK_TITLE"
else
    echo "No title available"
fi
```

### Hook Output Not Visible

**Symptoms**: Hook seems to run but you don't see output.

**Cause**: Hooks run in background with suppressed output.

**Solution**: Enable debug logging:
```yaml
# .backlog/config.yml
hooks:
  logLevel: debug
```

Or log to a file explicitly:
```bash
#!/bin/bash
{
    echo "Task: $BACKLOG_TASK_ID"
    echo "Status: $BACKLOG_TASK_STATUS"
} >> .backlog/hooks.log 2>&1
```

## Security Considerations

### User Permissions

Hooks run with your user permissions. They cannot:
- Escalate privileges
- Access files you can't access
- Execute as root (unless you're root)

### Untrusted Hooks

**Never run hooks from untrusted sources**. Hook scripts can execute arbitrary code.

Review hooks before making them executable:
```bash
# Review before enabling
cat .backlog/hooks/post-task-create.sh

# Only then make executable
chmod +x .backlog/hooks/post-task-create.sh
```

### Sensitive Data

Avoid logging sensitive data in hook scripts:

```bash
# Bad: Logs API keys
echo "API_KEY: $SECRET_API_KEY" >> hooks.log

# Good: Logs safely
echo "Notification sent to Slack" >> hooks.log
```

Use environment variables or secret management:
```bash
#!/bin/bash
# Load secrets from secure location
source ~/.backlog_secrets

curl -H "Authorization: Bearer $SLACK_TOKEN" ...
```

## Migration from Other Systems

### From Git Hooks

Git hooks are similar but different:

| Aspect | Git Hooks | Backlog Hooks |
|--------|-----------|---------------|
| Location | `.git/hooks/` | `.backlog/hooks/` |
| Triggers | Git operations | Task operations |
| Blocking | Can block operations | Never blocks |
| Version Control | Not tracked | Tracked in repo |

### From Cron Jobs

Replace polling cron jobs with event-driven hooks:

**Before (polling)**:
```cron
*/5 * * * * check_task_status.py  # Check every 5 minutes
```

**After (event-driven)**:
```bash
#!/bin/bash
# .backlog/hooks/post-task-update.sh
# Runs immediately when status changes
handle_status_change.py "$BACKLOG_TASK_ID" "$BACKLOG_NEW_STATUS"
```

## Examples

Complete example hook scripts are available in:
- `docs/examples/hooks/task-memory-integration.sh`
- `docs/examples/hooks/slack-notifications.sh`
- `docs/examples/hooks/metrics-tracking.sh`
- `docs/examples/hooks/jira-sync.sh`

## Related Documentation

- [Backlog.md User Guide](https://backlog.md/docs)
- [Task Memory System](../guides/task-memory.md)
- [Status Callbacks](./status-callbacks.md)
- [Configuration Reference](./config-reference.md)
