---
id: task-480
title: 'claude-improves: Add flowspec init --complete option'
status: In Progress
assignee:
  - '@myself'
created_date: '2025-12-12 01:15'
updated_date: '2025-12-22 21:55'
labels:
  - claude-improves
  - cli
  - specify-init
  - feature
  - phase-2
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add a --complete flag to flowspec init that deploys ALL templates in a single command, rather than requiring multiple init invocations for different components.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 --complete flag enables all optional features
- [ ] #2 Skills deployed to .claude/skills/
- [ ] #3 All hooks enabled in hooks.yaml
- [ ] #4 Full CI/CD template with lint, test, security jobs
- [ ] #5 Complete VSCode settings and extensions
- [ ] #6 MCP configuration created
- [ ] #7 Documentation explains --complete vs default behavior
<!-- AC:END -->
