---
id: task-543
title: 'Integrate rigor rules into /flow:implement'
status: Done
assignee: []
created_date: '2025-12-17 16:40'
updated_date: '2025-12-22 21:54'
labels:
  - rigor
  - implement
  - command
  - 'workflow:Planned'
dependencies:
  - task-541
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add rigor rules include to the implement command and enforce pre-PR validation rules. This is the primary inner-loop command where most rigor rules apply.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Add {{INCLUDE:_rigor-rules.md}} reference to implement.md template
- [ ] #2 Enforce branch naming convention (hostname/task-#/slug-description)
- [ ] #3 Enforce git worktree name matches branch name
- [ ] #4 Add pre-PR validation gate with lint, tests, rebase checks
- [ ] #5 Add decision logging hooks at key decision points
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add {{INCLUDE:_rigor-rules.md}} to implement.md template
2. Add branch naming validation script call
3. Add worktree alignment check
4. Add pre-PR validation gate section
5. Add decision logging hooks
6. Test end-to-end implementation workflow
<!-- SECTION:PLAN:END -->
