---
id: task-092
title: Phase 4 - Task Completion Handler
status: Done
assignee: []
created_date: '2025-11-28 15:56'
updated_date: '2025-12-03 01:15'
labels:
  - validate-enhancement
  - phase-4
  - backend
  - completion
dependencies:
  - task-091
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement the task completion handler that verifies all acceptance criteria are checked, adds implementation notes (suitable for PR description), and marks the task as Done using the backlog CLI.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Verifies 100% of ACs are checked before proceeding (queries task state via backlog CLI)
- [ ] #2 If any AC unchecked, halts and reports which ACs still need verification
- [ ] #3 Generates implementation notes summarizing: what was implemented, how it was tested, key decisions made
- [ ] #4 Adds implementation notes via `backlog task edit <id> --notes "..."` with proper multi-line formatting
- [ ] #5 Updates task status to Done via `backlog task edit <id> -s Done`
- [ ] #6 Generates a TaskCompletionReport with: task_id, completion_timestamp, ac_summary, validation_summary
- [ ] #7 Handles edge case: task already Done (idempotent, reports already complete)
- [ ] #8 Logs all backlog CLI commands executed for audit trail
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementation complete on main: src/specify_cli/workflow/completion.py (10KB)
<!-- SECTION:NOTES:END -->
