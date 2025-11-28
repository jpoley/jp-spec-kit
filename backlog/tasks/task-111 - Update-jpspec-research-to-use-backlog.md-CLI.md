---
id: task-111
title: 'Update /jpspec:research to use backlog.md CLI'
status: To Do
assignee: []
created_date: '2025-11-28 16:56'
updated_date: '2025-11-28 16:57'
labels:
  - jpspec
  - backlog-integration
  - research
  - P1
dependencies:
  - task-107
  - task-108
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Modify the research.md command to integrate backlog.md task management. Researcher and Business Validator agents must create research tasks and document findings in backlog.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Command discovers existing research-related backlog tasks
- [ ] #2 Both agents receive shared backlog instructions from _backlog-instructions.md
- [ ] #3 Researcher creates research spike tasks in backlog
- [ ] #4 Business Validator creates validation tasks in backlog
- [ ] #5 Agents add research findings as implementation notes to tasks
- [ ] #6 Test: Run /jpspec:research and verify research tasks created with findings
<!-- AC:END -->
