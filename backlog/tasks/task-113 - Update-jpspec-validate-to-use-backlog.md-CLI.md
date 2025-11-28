---
id: task-113
title: 'Update /jpspec:validate to use backlog.md CLI'
status: To Do
assignee: []
created_date: '2025-11-28 16:56'
updated_date: '2025-11-28 16:57'
labels:
  - jpspec
  - backlog-integration
  - validate
  - P1
dependencies:
  - task-107
  - task-108
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Modify the validate.md command to integrate backlog.md task management. QA, Security, Tech Writer, and Release Manager agents must validate against backlog task ACs and update completion status.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Command discovers tasks in In Progress or Done status for validation
- [ ] #2 All 4 validator agents receive shared backlog instructions from _backlog-instructions.md
- [ ] #3 Quality Guardian validates ACs match test results
- [ ] #4 Security Engineer validates security-related ACs
- [ ] #5 Tech Writer creates/updates documentation tasks in backlog
- [ ] #6 Release Manager verifies Definition of Done before marking tasks Done
- [ ] #7 Test: Run /jpspec:validate and verify task validation workflow
<!-- AC:END -->
