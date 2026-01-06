---
id: task-520
title: Implement Pre-Commit Quality Gate - SAST
status: To Do
assignee:
  - '@chamonix'
created_date: '2025-12-14 03:35'
updated_date: '2026-01-06 18:52'
labels:
  - git-workflow
  - quality-gate
  - on-hold
dependencies:
  - task-517
priority: high
ordinal: 54000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create security scanning gate with bandit and semgrep.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Pre-commit hook calls quality-gates/sast.sh
- [ ] #2 Runs bandit and semgrep
- [ ] #3 Emits security.vulnerability_found events
- [ ] #4 Fail on high/critical findings
- [ ] #5 SARIF output stored in .flowspec/security/sarif
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
**ON HOLD (Dec 2025)**: Security scanning features may move to dedicated security repo.
<!-- SECTION:NOTES:END -->
