---
id: task-110
title: 'Update /jpspec:plan to use backlog.md CLI'
status: Done
assignee:
  - '@claude-agent'
created_date: '2025-11-28 16:56'
updated_date: '2025-11-29 05:14'
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
- [x] #1 Command discovers existing backlog tasks for the feature being planned
- [x] #2 Both agents receive shared backlog instructions from _backlog-instructions.md
- [x] #3 Software Architect creates architecture tasks in backlog (ADRs, design docs)
- [x] #4 Platform Engineer creates infrastructure tasks in backlog (CI/CD, observability)
- [x] #5 Agents update task status and add implementation plans to existing tasks
- [x] #6 Test: Run /jpspec:plan and verify architecture/infra tasks created in backlog
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Verified /jpspec:plan backlog.md integration is complete.

Implementation Status:
- plan.md includes Step 0: Backlog Task Discovery with search and list commands
- Both Software Architect and Platform Engineer agents include {{INCLUDE:_backlog-instructions.md}}
- Software Architect has instructions for creating ADR, Design, and Pattern tasks
- Platform Engineer has instructions for CI/CD, Observability, Security, and IaC tasks
- Both agents have task edit commands for status updates and implementation plans
- 38 comprehensive tests in test_jpspec_plan_backlog.py cover all acceptance criteria

Test Results: All 38 tests pass
Code Quality: ruff formatting applied
<!-- SECTION:NOTES:END -->
