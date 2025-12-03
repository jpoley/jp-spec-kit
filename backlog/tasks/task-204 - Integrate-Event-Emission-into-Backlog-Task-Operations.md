---
id: task-204
title: Integrate Event Emission into Backlog Task Operations
status: To Do
assignee:
  - '@pm-planner'
created_date: '2025-12-03 00:41'
updated_date: '2025-12-03 01:41'
labels:
  - implement
  - integration
  - hooks
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add event emission to backlog task lifecycle events (created, updated, status changed, completed). Enables automation based on task state changes.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Emit task.created when new task created via backlog CLI
- [ ] #2 Emit task.status_changed when status transitions occur
- [ ] #3 Emit task.completed when task marked as Done
- [ ] #4 Emit task.ac_checked when acceptance criterion checked/unchecked
- [ ] #5 Integration tests for each event type
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## CLI Event Emission Capability

Created hooks CLI that enables manual task event emission:
- `specify hooks emit task.completed --task-id task-123`
- `specify hooks emit task.status_changed --task-id task-123`
- All task events from EventType enum are supported

## Backlog Integration Challenges

Direct integration with backlog.md is not possible because:
1. Backlog is managed by external MCP server (mcp__backlog__*)
2. Cannot modify MCP server code to add emit_event() calls
3. Must rely on external triggers (git hooks, user commands, shell aliases)

## Implementation Alternatives

Users can emit events manually or via git hooks:
```bash
# Manual emission after task completion
backlog task edit 123 -s Done
specify hooks emit task.completed --task-id task-123

# Or create post-commit hook to auto-emit
# .git/hooks/post-commit:
#!/bin/bash
# Parse backlog.md changes and emit events
```

## Files Created
- src/specify_cli/hooks/cli.py - Includes task event emission commands
- tests/test_hooks_cli.py - Task event emission tests included
<!-- SECTION:NOTES:END -->
