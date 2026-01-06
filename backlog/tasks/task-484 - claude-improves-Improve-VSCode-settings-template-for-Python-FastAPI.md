---
id: task-484
title: 'claude-improves: Improve VSCode settings template for Python/FastAPI'
status: To Do
assignee:
  - '@kinsale'
created_date: '2025-12-12 01:15'
updated_date: '2026-01-06 18:52'
labels:
  - claude-improves
  - templates
  - vscode
  - python
  - phase-2
dependencies: []
priority: high
ordinal: 34000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
VSCode settings.json template is incomplete. Missing Python/FastAPI specific configuration:
- Python interpreter path
- Ruff as formatter/linter
- Test discovery settings
- Debug configurations
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 settings.json includes python.defaultInterpreterPath
- [ ] #2 Ruff configured as default formatter
- [ ] #3 Python testing configured for pytest
- [ ] #4 Editor settings for Python files (tab size, rulers)
- [ ] #5 Debug launch configurations for common scenarios
- [ ] #6 Template is conditional based on detected project type
<!-- AC:END -->
