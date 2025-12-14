---
id: task-204
title: Integrate Event Emission into Backlog Task Operations
status: In Progress
assignee:
  - '@muckross'
created_date: '2025-12-03 00:41'
updated_date: '2025-12-14 19:20'
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
- [x] #1 Emit task.created when new task created via backlog CLI
- [x] #2 Emit task.status_changed when status transitions occur
- [x] #3 Emit task.completed when task marked as Done
- [x] #4 Emit task.ac_checked when acceptance criterion checked/unchecked
- [x] #5 Integration tests for each event type
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

## Implementation Progress (2025-12-14)

### Completed Sub-tasks:

**task-204.01: Git hook for backlog events** - DONE
- Created `scripts/hooks/post-commit-backlog-events.sh`
- Detects task changes in git commits
- Emits events: task.created, task.status_changed, task.completed, task.ac_checked
- Integration tests in `tests/integration/test_post_commit_backlog_events.sh`

**task-204.03: Upstream contribution proposal** - IN PROGRESS
- Proposal document: `docs/proposals/backlog-md-hooks-proposal.md`
- Codebase reviewed, design drafted
- Awaiting GitHub issue creation and maintainer engagement

### Acceptance Criteria Status:

1. **task.created** - Implemented via post-commit hook detecting new task files
2. **task.status_changed** - Implemented via post-commit hook parsing status changes
3. **task.completed** - Implemented via post-commit hook (status=Done detection)
4. **task.ac_checked** - Implemented via post-commit hook (checkbox detection)
5. **Integration tests** - Created in tests/integration/test_post_commit_backlog_events.sh

### Note:
Task remains In Progress as task-204.03 requires external action (GitHub issue on upstream repo).
<!-- SECTION:NOTES:END -->
