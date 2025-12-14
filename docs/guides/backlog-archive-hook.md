# Backlog Archive Hook Guide

This guide explains the Claude Code hook for backlog archive previews.

## Overview

The `post-workflow-archive.sh` hook runs after workflow completion and shows what tasks would be archived. It's designed as a notification mechanism, not an enforcement tool.

## Hook Details

| Property | Value |
|----------|-------|
| **Location** | `.claude/hooks/post-workflow-archive.sh` |
| **Trigger Event** | `validate.completed` (after `/flow:validate`) |
| **Mode** | Dry-run only (preview, no actual archiving) |
| **Exit Behavior** | Always exits 0 (fail-open, never blocks workflow) |
| **Timeout** | 30 seconds |

## How It Works

1. **Event Received**: Hook receives JSON event on stdin after workflow completion
2. **Event Validation**: Checks for `validate.completed` event type
3. **Archive Preview**: Runs `archive-tasks.sh --dry-run`
4. **Output Logging**: Shows which tasks would be archived
5. **Exit**: Always exits 0 (fail-open principle)

## Event Format

The hook receives event JSON on stdin:

```json
{
  "event_type": "validate.completed",
  "feature": "feature-123",
  "project_root": "/path/to/project"
}
```

## Output Example

```
[post-workflow-archive] Starting archive preview...
[post-workflow-archive] Event: validate.completed
[post-workflow-archive] Feature: feature-123
[post-workflow-archive] Project: /home/user/project
[post-workflow-archive] Running archive preview (dry-run)...
[post-workflow-archive] Command: /home/user/project/scripts/bash/archive-tasks.sh --dry-run
[post-workflow-archive] Archive preview output:
[post-workflow-archive]   === Backlog Archive (Dry Run) ===
[post-workflow-archive]   Mode: Done tasks only
[post-workflow-archive]   [DRY RUN] Would archive: task-042 - Implement login
[post-workflow-archive]   Summary:
[post-workflow-archive]     Tasks to archive: 1
[post-workflow-archive] Archive preview completed - tasks would be archived
[post-workflow-archive] Archive preview complete
```

## Configuration

### Enabling the Hook

The hook is enabled by default when present in `.claude/hooks/`. To use it:

1. Ensure `post-workflow-archive.sh` exists in `.claude/hooks/`
2. Ensure the file is executable: `chmod +x .claude/hooks/post-workflow-archive.sh`
3. The hook auto-triggers after `/flow:validate` completes

### Disabling the Hook

To disable without deleting:

```bash
# Option 1: Remove execute permission
chmod -x .claude/hooks/post-workflow-archive.sh

# Option 2: Rename the file
mv .claude/hooks/post-workflow-archive.sh .claude/hooks/post-workflow-archive.sh.disabled
```

### Changing the Trigger Event

Edit the event type check in the script:

```bash
# Current: Only runs for validate.completed
if [[ "$event_type" != "validate.completed" && -n "$event_type" ]]; then
    log "Skipping: event type '$event_type' is not validate.completed"
    exit 0
fi

# Alternative: Run for any workflow.completed event
if [[ "$event_type" != "workflow.completed" && -n "$event_type" ]]; then
    ...
fi
```

### Adjusting Timeout

Edit the `TIMEOUT` variable:

```bash
# Default: 30 seconds
TIMEOUT=30

# Increase for large backlogs
TIMEOUT=60
```

## Fail-Open Design

The hook follows the **fail-open principle**:

- Always exits 0, regardless of errors
- Never blocks workflow completion
- Logs errors but continues gracefully
- Missing script? Continue.
- Timeout? Continue.
- JSON parse error? Continue.

This ensures the hook never disrupts development workflow.

## Customization Examples

### Add Slack Notification

```bash
# After archive preview completes
if [[ -n "$output" && "$exit_code" -eq 0 ]]; then
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"Archive preview: tasks available for archiving\"}" \
        "$SLACK_WEBHOOK_URL"
fi
```

### Log to File

```bash
# Add to main function
LOG_FILE="${PROJECT_ROOT}/.flowspec/archive-preview.log"
mkdir -p "$(dirname "$LOG_FILE")"
echo "[$(date -Iseconds)] $output" >> "$LOG_FILE"
```

### Change to Enforce Mode

**Warning:** This changes the fail-open behavior. Not recommended for production.

```bash
# Remove fail-open behavior
if [[ $exit_code -ne 0 && $exit_code -ne 2 ]]; then
    log "ERROR: Archive check failed"
    exit 1  # Now blocks workflow
fi
```

## Troubleshooting

### Hook Not Running

1. **Check file exists**: `ls -la .claude/hooks/post-workflow-archive.sh`
2. **Check permissions**: `chmod +x .claude/hooks/post-workflow-archive.sh`
3. **Verify event type**: Hook only runs for `validate.completed` by default

### No Output Shown

1. **Check logs**: Output goes to stdout during workflow
2. **Run manually**: Test the script directly:
   ```bash
   echo '{"event_type":"validate.completed"}' | .claude/hooks/post-workflow-archive.sh
   ```

### Python Not Found

The hook uses Python for JSON parsing:
```bash
python3 --version
# If missing, install Python 3
```

### Timeout Issues

For large backlogs, increase timeout:
```bash
# In post-workflow-archive.sh
TIMEOUT=60  # Increase from 30 to 60 seconds
```

## Dependencies

- **Bash 4.0+**: Shell scripting
- **Python 3**: JSON parsing
- **archive-tasks.sh**: Archive script at `scripts/bash/archive-tasks.sh`
- **backlog.md CLI**: Required by archive script

## Related Documentation

- [Backlog Archive User Guide](backlog-archive.md)
- [Backlog Archive Workflow Guide](backlog-archive-workflow.md)
- [Claude Hooks Documentation](claude-hooks.md)
- [Troubleshooting Runbook](../runbooks/backlog-archive-troubleshooting.md)
