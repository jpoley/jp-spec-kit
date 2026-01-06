---
id: task-548
title: 'Integrate rigor rules into /flow:operate'
status: Done
assignee: []
created_date: '2025-12-17 16:41'
updated_date: '2026-01-06 18:57'
labels:
  - rigor
  - operate
  - command
  - 'workflow:Planned'
dependencies:
  - task-541
priority: medium
ordinal: 76000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add rigor rules include to the operate command for deployment hygiene. Final workflow step must verify all gates passed.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Add {{INCLUDE:_rigor-rules.md}} reference to operate.md template
- [ ] #2 Verify all validation gates passed before deployment
- [ ] #3 Enforce task status updates with deployment (task must be marked Done)
- [ ] #4 Clean up bead statuses as part of deployment completion
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add {{INCLUDE:_rigor-rules.md}} to operate.md template
2. Add validation gates verification
3. Enforce task status update to Done
4. Add bead cleanup step
5. Test operate workflow
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
**Closed as OBSOLETE**: /flow:operate has been removed from flowspec. Deployment and operations are outer loop responsibilities handled externally by CI/CD pipelines (see flowspec_workflow.yml). This task is no longer applicable.
<!-- SECTION:NOTES:END -->
