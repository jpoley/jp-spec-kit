---
id: task-109
title: 'Update /jpspec:specify to use backlog.md CLI'
status: To Do
assignee: []
created_date: '2025-11-28 16:56'
updated_date: '2025-11-28 20:23'
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
- [ ] #1 Command checks for existing backlog tasks related to feature (backlog search)
- [ ] #2 PM planner agent receives shared backlog instructions from _backlog-instructions.md
- [ ] #3 Agent creates new tasks via backlog task create when defining work items
- [ ] #4 Agent assigns itself to tasks it creates
- [ ] #5 Generated PRD includes backlog task IDs (not just prose task lists)
- [ ] #6 Test: Run /jpspec:specify and verify tasks appear in backlog with correct format
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Note: File modifications ready to apply:
1. .claude/commands/jpspec/specify.md - Add backlog search step, include _backlog-instructions.md, update task breakdown section
2. tests/test_jpspec_specify_backlog.py - Create comprehensive test suite (21 tests)

Due to branch-switching issues during implementation, file changes need to be reapplied manually based on implementation plan and notes.
<!-- SECTION:NOTES:END -->
