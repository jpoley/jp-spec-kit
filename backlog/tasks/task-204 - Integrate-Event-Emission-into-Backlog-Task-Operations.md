---
id: task-204
title: Integrate Event Emission into Backlog Task Operations
status: To Do
assignee:
  - '@chamonix'
created_date: '2025-12-03 00:41'
updated_date: '2025-12-15 02:17'
labels:
  - implement
  - integration
  - hooks
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**PARENT TASK** - Integrate event emission with backlog task operations.

This task has been broken into sub-tasks because backlog.md is a third-party MCP server (MrLesk/Backlog.md) that we cannot modify directly.

**Sub-tasks**:
- task-214: Git hook to emit events on task file changes
- task-215: Backlog CLI wrapper with auto-emit
- task-216: Contribute hooks feature to upstream backlog.md

See sub-tasks for implementation details.
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
## Analysis

Backlog.md is a third-party package: https://github.com/MrLesk/Backlog.md

We cannot modify it directly, so we need alternative integration approaches.

## Sub-tasks Created

- task-214: Git hook approach (automatic, parses file changes)
- task-215: CLI wrapper approach (explicit, user calls wrapper)
- task-216: Upstream contribution (long-term, proper integration)

## Current Capability

Users can already emit events manually:
```bash
backlog task edit 123 -s Done && specify hooks emit task.completed --task-id task-123
```
<!-- SECTION:NOTES:END -->
