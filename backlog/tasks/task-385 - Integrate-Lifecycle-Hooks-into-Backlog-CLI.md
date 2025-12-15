---
id: task-385
title: Integrate Lifecycle Hooks into Backlog CLI
status: Done
assignee:
  - '@adare'
created_date: '2025-12-09 15:57'
updated_date: '2025-12-15 02:17'
labels:
  - backend
  - task-memory
  - backlog
  - cli
dependencies:
  - task-377
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add lifecycle hook calls to `backlog task edit` command to trigger memory operations on state changes
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Modify task_edit command in src/specify_cli/commands/task.py
- [x] #2 Call lifecycle_manager.on_state_change() after task status update
- [x] #3 Pass old_state and new_state to lifecycle manager
- [x] #4 Add CLI output messages for memory operations
- [ ] #5 Test with live CLI commands (backlog task edit)
- [ ] #6 Verify memory files created/archived/deleted correctly
- [ ] #7 Add integration tests for CLI + lifecycle
<!-- AC:END -->
