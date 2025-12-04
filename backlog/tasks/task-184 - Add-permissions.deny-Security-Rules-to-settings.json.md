---
id: task-184
title: Add permissions.deny Security Rules to settings.json
status: To Do
assignee:
  - '@kinsale'
created_date: '2025-12-01 05:04'
updated_date: '2025-12-04 17:07'
labels:
  - claude-code
  - security
  - quick-win
  - 'workflow:Specified'
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Configure permissions.deny in .claude/settings.json to prevent accidental exposure of sensitive files (.env, secrets) and protect critical files (CLAUDE.md, constitution.md, lock files).

Cross-reference: See docs/prd/claude-capabilities-review.md Section 2.5 for settings gap analysis.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 permissions.deny rules added for .env and .env.* files

- [ ] #2 permissions.deny rules added for secrets/ directory
- [ ] #3 permissions.deny rules protect CLAUDE.md and memory/constitution.md from writes
- [ ] #4 permissions.deny rules protect lock files (uv.lock, package-lock.json)
- [ ] #5 permissions.deny rules block dangerous Bash commands (sudo, rm -rf)
- [ ] #6 Documentation updated in CLAUDE.md explaining permission rules
<!-- AC:END -->
