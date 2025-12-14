# Feature Proposal: Extended Hook System for Backlog.md

**Target Repository**: [MrLesk/Backlog.md](https://github.com/MrLesk/Backlog.md)
**Author**: @jpoley (Flowspec Project)
**Date**: 2025-12-14
**Status**: Draft

## Summary

This proposal suggests extending the existing `onStatusChange` hook in Backlog.md to support a comprehensive event-driven hook system that enables integration with external tools, CI/CD pipelines, and workflow automation.

## Motivation

Backlog.md is increasingly used with AI coding assistants (Claude, Copilot, Cursor) for task management. These tools benefit from real-time task state notifications to:

1. **Sync state** between backlog and external systems (Jira, Linear, GitHub Issues)
2. **Trigger workflows** when tasks are created, modified, or completed
3. **Enable telemetry** for understanding task completion patterns
4. **Support automation** like auto-archiving completed tasks

The current `onStatusChange` hook is a great foundation but limited to status changes. Expanding to a full lifecycle event system would unlock powerful integrations.

## Current State

Backlog.md currently supports:

```yaml
# backlog/config.yml
onStatusChange: "./scripts/on-status-change.sh"
```

This calls the script with task information when status changes.

## Proposed Enhancement

### Option A: Extended Shell Hook System (Minimal Change)

Add additional hook points to the existing config:

```yaml
# backlog/config.yml
hooks:
  # Existing hook (backwards compatible)
  onStatusChange: "./scripts/on-status-change.sh"

  # New lifecycle hooks
  onTaskCreate: "./scripts/on-task-create.sh"
  onTaskEdit: "./scripts/on-task-edit.sh"
  onTaskDelete: "./scripts/on-task-delete.sh"
  onTaskArchive: "./scripts/on-task-archive.sh"

  # Acceptance criteria hooks
  onAcceptanceCriteriaCheck: "./scripts/on-ac-check.sh"
  onAcceptanceCriteriaUncheck: "./scripts/on-ac-uncheck.sh"

  # Bulk operation hooks
  onBulkStatusChange: "./scripts/on-bulk-status.sh"
```

**Hook Interface (stdin)**:

Hooks receive JSON on stdin with event details:

```json
{
  "event_type": "task.created",
  "timestamp": "2025-12-14T19:00:00Z",
  "task": {
    "id": "task-123",
    "title": "Implement feature X",
    "status": "To Do",
    "priority": "high",
    "labels": ["backend", "api"],
    "acceptance_criteria": [
      {"index": 1, "text": "API endpoint created", "checked": false}
    ]
  },
  "context": {
    "previous_status": null,
    "changed_fields": ["title", "description"],
    "user": "jpoley"
  }
}
```

### Option B: Event Emitter Pattern (TypeScript)

For programmatic integrations, add an event emitter:

```typescript
// backlog.config.ts
import { BacklogConfig } from 'backlog-md';

export default {
  hooks: {
    'task.created': async (event) => {
      console.log(`Task created: ${event.task.id}`);
      // Send to external system
      await fetch('https://api.example.com/webhook', {
        method: 'POST',
        body: JSON.stringify(event)
      });
    },
    'task.status_changed': async (event) => {
      if (event.task.status === 'Done') {
        // Trigger CI/CD
        await exec('gh workflow run deploy.yml');
      }
    }
  }
} as BacklogConfig;
```

### Option C: Hybrid Approach (Recommended)

Support both shell commands (simple) and TypeScript functions (advanced):

```yaml
# backlog/config.yml
hooks:
  # Simple shell hook
  onTaskCreate: "./scripts/on-task-create.sh"

  # Reference to TypeScript config for complex logic
  advanced: "./backlog.hooks.ts"
```

```typescript
// backlog.hooks.ts
export const hooks = {
  'task.completed': async (event) => {
    // Complex logic with type safety
  }
};
```

## Event Types

| Event | Trigger | Payload |
|-------|---------|---------|
| `task.created` | `backlog task create` | New task data |
| `task.edited` | `backlog task edit` | Task data + changed fields |
| `task.status_changed` | Status field modified | Previous + new status |
| `task.deleted` | `backlog task delete` | Deleted task data |
| `task.archived` | Task moved to archive | Archived task data |
| `ac.checked` | AC marked complete | AC index + task data |
| `ac.unchecked` | AC marked incomplete | AC index + task data |

## Implementation Considerations

### Backwards Compatibility

The existing `onStatusChange` should continue to work. New hooks are additive.

### Performance

- Hooks should be async and not block the CLI
- Consider `--no-hooks` flag for batch operations
- Optional timeout configuration

### Error Handling

- Hook failures should log warnings but not block operations
- Exit codes: 0 = success, non-zero = warning logged
- Optional `--fail-on-hook-error` for strict mode

## Use Cases

### 1. Sync with GitHub Issues

```bash
#!/bin/bash
# on-task-create.sh
event=$(cat)
title=$(echo "$event" | jq -r '.task.title')
gh issue create --title "$title" --body "Created from Backlog.md"
```

### 2. Slack Notifications

```bash
#!/bin/bash
# on-task-completed.sh
event=$(cat)
task_title=$(echo "$event" | jq -r '.task.title')
curl -X POST "$SLACK_WEBHOOK" \
  -d "{\"text\": \"Task completed: $task_title\"}"
```

### 3. Telemetry Collection

```bash
#!/bin/bash
# on-status-change.sh
event=$(cat)
echo "$event" >> .backlog/telemetry.jsonl
```

### 4. Auto-Archive Workflow

```bash
#!/bin/bash
# on-task-completed.sh
event=$(cat)
task_id=$(echo "$event" | jq -r '.task.id')

# Check if all ACs are complete
all_checked=$(echo "$event" | jq '.task.acceptance_criteria | all(.checked)')
if [ "$all_checked" = "true" ]; then
  backlog task archive "$task_id"
fi
```

## Flowspec Integration

Flowspec (https://github.com/jpoley/flowspec) uses Backlog.md for task management in AI-assisted development workflows. This proposal would enable:

1. **Native event emission** without wrapper scripts
2. **Workflow state transitions** triggered by task completion
3. **Telemetry integration** for role/agent analytics
4. **CI/CD triggers** for automated validation

Current workaround: Git hooks + file watching (fragile, race conditions)

## Alternatives Considered

### Fork Backlog.md

**Pros**: Full control, immediate implementation
**Cons**: Maintenance burden, divergence from upstream

### File System Watching

**Pros**: No upstream changes needed
**Cons**: Race conditions, OS-specific, misses CLI operations

### MCP Server Middleware

**Pros**: Works with current architecture
**Cons**: Intercepts all operations, complexity

## Next Steps

1. **Discussion**: Open issue on MrLesk/Backlog.md to discuss approach
2. **Design Review**: Gather feedback from maintainer(s)
3. **Implementation**: If accepted, implement Option C (hybrid)
4. **Testing**: Add test coverage for hook system
5. **Documentation**: Update README and add hook examples

## Questions for Maintainer

1. Is the current `onStatusChange` implementation a good foundation to extend?
2. Preference for shell-only (Option A) vs TypeScript support (Option B/C)?
3. Any concerns about hook performance in large backlogs?
4. Interest in accepting this as a community contribution?

---

## Appendix: Related Work

- **Git Hooks**: Similar event-driven model, proven pattern
- **npm lifecycle scripts**: pre/post hooks for operations
- **Husky**: Git hooks made easy (already used in Backlog.md)
- **Claude Code Hooks**: Event-driven AI assistant customization

## References

- [Backlog.md Repository](https://github.com/MrLesk/Backlog.md)
- [Flowspec Project](https://github.com/jpoley/flowspec)
- [Claude Code Hooks Documentation](https://docs.anthropic.com/en/docs/claude-code/hooks)
