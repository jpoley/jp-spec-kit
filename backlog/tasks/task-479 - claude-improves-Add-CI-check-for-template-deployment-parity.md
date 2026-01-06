---
id: task-479
title: 'claude-improves: Add CI check for template-deployment parity'
status: To Do
assignee:
  - '@kinsale'
created_date: '2025-12-12 01:15'
updated_date: '2026-01-06 18:52'
labels:
  - claude-improves
  - ci
  - validation
  - automation
  - phase-1
dependencies: []
priority: high
ordinal: 32000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Source repository has organic growth without sync validation between templates/ and deployed files (.claude/).

Need automated CI check to ensure:
- All skills in .claude/skills/ exist in templates/skills/
- All commands have corresponding templates
- Symlinks are valid and point to correct targets
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 CI workflow checks templates/skills/ matches .claude/skills/ (excluding dev-only)
- [ ] #2 CI validates all command symlinks resolve correctly
- [ ] #3 CI checks for orphaned templates without deployment
- [ ] #4 CI checks for deployed files without templates
- [ ] #5 Workflow fails on parity mismatch with clear error message
- [ ] #6 Add make dev-validate target for local validation
<!-- AC:END -->
