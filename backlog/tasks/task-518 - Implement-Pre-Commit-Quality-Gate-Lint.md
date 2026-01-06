---
id: task-518
title: Implement Pre-Commit Quality Gate - Lint
status: To Do
assignee:
  - '@chamonix'
created_date: '2025-12-14 03:35'
updated_date: '2026-01-06 18:52'
labels:
  - agent-event-system
  - phase-4
  - infrastructure
  - quality
  - cicd
  - git-workflow
dependencies:
  - task-517
priority: high
ordinal: 52000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create lint quality gate running configured linters before commit.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Pre-commit hook calls quality-gates/lint.sh
- [ ] #2 Supports ruff eslint golangci-lint
- [ ] #3 Emits quality_gate.started and quality_gate.passed/failed events
- [ ] #4 Configurable skip with git commit --no-verify
- [ ] #5 Exit code 1 blocks commit on failure
<!-- AC:END -->
