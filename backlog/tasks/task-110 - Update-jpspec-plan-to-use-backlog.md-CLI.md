---
id: task-110
title: 'Update /jpspec:plan to use backlog.md CLI'
status: To Do
assignee: []
created_date: '2025-11-28 16:56'
updated_date: '2025-11-28 16:57'
labels:
  - jpspec
  - backlog-integration
  - plan
  - P1
dependencies:
  - task-107
  - task-108
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Modify the plan.md command to integrate backlog.md task management. Software Architect and Platform Engineer agents must work with backlog tasks, creating architecture/infrastructure tasks as they plan.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Command discovers existing backlog tasks for the feature being planned
- [ ] #2 Both agents receive shared backlog instructions from _backlog-instructions.md
- [ ] #3 Software Architect creates architecture tasks in backlog (ADRs, design docs)
- [ ] #4 Platform Engineer creates infrastructure tasks in backlog (CI/CD, observability)
- [ ] #5 Agents update task status and add implementation plans to existing tasks
- [ ] #6 Test: Run /jpspec:plan and verify architecture/infra tasks created in backlog
<!-- AC:END -->
