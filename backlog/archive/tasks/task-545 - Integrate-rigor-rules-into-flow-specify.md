---
id: task-545
title: 'Integrate rigor rules into /flow:specify'
status: Done
assignee: []
created_date: '2025-12-17 16:40'
updated_date: '2025-12-17 22:48'
labels:
  - rigor
  - specify
  - command
  - 'workflow:Planned'
dependencies:
  - task-541
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add rigor rules include to the specify command for task setup hygiene. This command creates tasks and must enforce clear acceptance criteria and dependency documentation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Add {{INCLUDE:_rigor-rules.md}} reference to specify.md template
- [x] #2 Require documented plan of action (ask if missing)
- [ ] #3 Enforce testable acceptance criteria for all created tasks
- [ ] #4 Require inter-task dependencies to be documented before task ordering
- [ ] #5 Ensure tasks link to beads/agentic task lists where applicable
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add {{INCLUDE:_rigor-rules.md}} to specify.md template
2. Add plan documentation requirement (ask if missing)
3. Enforce testable ACs for all created tasks
4. Add inter-task dependency documentation requirement
5. Add bead linkage guidance
6. Test specify workflow
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
PR #971 merged - integrated rigor rules with SETUP-001 plan verification into /flow:specify
<!-- SECTION:NOTES:END -->
