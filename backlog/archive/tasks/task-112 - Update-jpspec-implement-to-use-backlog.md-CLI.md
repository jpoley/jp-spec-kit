---
id: task-112
title: 'Update /jpspec:implement to use backlog.md CLI'
status: Done
assignee:
  - '@claude-opus'
created_date: '2025-11-28 16:56'
updated_date: '2025-11-28 20:36'
labels:
  - jpspec
  - backlog-integration
  - implement
  - P0
  - critical
dependencies:
  - task-107
  - task-108
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
CRITICAL: Modify the implement.md command to integrate backlog.md task management. Engineers must work exclusively from backlog tasks, checking ACs as they complete work. No feature work without backlog tasks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Command REQUIRES existing backlog tasks to work on (fails gracefully if none found)
- [x] #2 All 5 engineer agents receive shared backlog instructions from _backlog-instructions.md
- [x] #3 Engineers pick up tasks from backlog (backlog task list -s To Do)
- [x] #4 Engineers assign themselves and set status to In Progress before coding
- [x] #5 Engineers check ACs (--check-ac) as each criterion is implemented
- [x] #6 Engineers add implementation notes describing what was built
- [x] #7 Code reviewers verify AC completion matches actual code changes
- [x] #8 Test: Run /jpspec:implement with test task and verify AC progression
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
CRITICAL P0: Updated /jpspec:implement command with full backlog.md CLI integration.

Engineers now work EXCLUSIVELY from backlog tasks.

Changes:
- Added Step 0: REQUIRED task discovery (fails gracefully if no tasks)
- All 5 agents receive backlog instructions:
  - Frontend Engineer (@frontend-engineer)
  - Backend Engineer (@backend-engineer)
  - AI/ML Engineer (@ai-ml-engineer)
  - Frontend Code Reviewer (@frontend-code-reviewer)
  - Backend Code Reviewer (@backend-code-reviewer)
- Engineers pick tasks, assign themselves, set In Progress
- Engineers check ACs progressively during implementation
- Engineers add implementation notes
- Code reviewers verify AC completion matches code changes
- Added tests in tests/test_jpspec_implement_backlog.py (21 tests, all passing)
<!-- SECTION:NOTES:END -->
