---
id: task-089
title: Phase 3 - AC Verification Engine with Human Approval
status: Done
assignee: []
created_date: '2025-11-28 15:56'
updated_date: '2025-12-03 01:15'
labels:
  - validate-enhancement
  - phase-3
  - backend
  - verification
dependencies:
  - task-088
  - task-089
  - task-090
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement the acceptance criteria verification engine that presents each AC with supporting evidence (test results, agent reports), requests human confirmation for subjective criteria, and marks verified ACs as complete using the backlog CLI.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 For each AC with validation_approach='automated' and passing tests, auto-marks as verified with evidence
- [ ] #2 For each AC with validation_approach='manual', presents the AC text with context and requests human confirmation via AskUserQuestion
- [ ] #3 For each AC with validation_approach='hybrid', shows automated evidence and requests human final approval
- [ ] #4 Uses `backlog task edit <id> --check-ac <index>` to mark each verified AC as complete
- [ ] #5 Tracks verification status: verified_auto, verified_manual, pending, failed
- [ ] #6 If any AC fails verification, stops the workflow and reports which ACs failed and why
- [ ] #7 Presents a verification summary showing: total ACs, auto-verified count, manually-verified count, pending count
- [ ] #8 All AC checks are idempotent - re-running doesn't double-check already-verified ACs
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementation complete on main: src/specify_cli/workflow/validator.py (25KB)
<!-- SECTION:NOTES:END -->
