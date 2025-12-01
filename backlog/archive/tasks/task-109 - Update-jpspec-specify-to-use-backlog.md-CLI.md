---
id: task-109
title: 'Update /jpspec:specify to use backlog.md CLI'
status: Done
assignee:
  - '@claude-opus'
created_date: '2025-11-28 16:56'
updated_date: '2025-11-28 20:33'
labels:
  - jpspec
  - backlog-integration
  - specify
  - P1
dependencies:
  - task-107
  - task-108
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Modify the specify.md command to integrate backlog.md task management. The PM planner agent must create tasks in backlog or work with existing tasks, not just output PRD sections.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Command checks for existing backlog tasks related to feature (backlog search)
- [x] #2 PM planner agent receives shared backlog instructions from _backlog-instructions.md
- [x] #3 Agent creates new tasks via backlog task create when defining work items
- [x] #4 Agent assigns itself to tasks it creates
- [x] #5 Generated PRD includes backlog task IDs (not just prose task lists)
- [x] #6 Test: Run /jpspec:specify and verify tasks appear in backlog with correct format
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Updated /jpspec:specify command with full backlog.md CLI integration.

Changes:
- Added Step 1: Discover Existing Tasks section with backlog search
- Added Backlog.md CLI Integration section to agent prompt with key commands
- Updated Section 6 to create actual backlog tasks via CLI
- Agent assigns itself (@pm-planner) to created tasks
- PRD output includes backlog task IDs for traceability
- Added tests in tests/test_jpspec_specify_backlog.py (18 tests, all passing)
<!-- SECTION:NOTES:END -->
