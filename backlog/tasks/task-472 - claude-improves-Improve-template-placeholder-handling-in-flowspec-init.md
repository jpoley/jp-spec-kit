---
id: task-472
title: 'claude-improves: Improve template placeholder handling in flowspec init'
status: To Do
assignee:
  - '@kinsale'
created_date: '2025-12-12 01:15'
updated_date: '2026-01-06 18:52'
labels:
  - claude-improves
  - cli
  - specify-init
  - templates
  - phase-1
dependencies: []
priority: high
ordinal: 29000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Enhance flowspec init to properly substitute placeholders like [PROJECT_NAME], [TECH_STACK] with detected or user-provided values during template deployment.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 PROJECT_NAME auto-detected from pyproject.toml, package.json, or directory name
- [ ] #2 LANGUAGES_AND_FRAMEWORKS detected from project file presence
- [ ] #3 LINTING_TOOLS detected from config files (ruff.toml, .eslintrc, etc.)
- [ ] #4 DATE automatically populated with current date
- [ ] #5 Any remaining placeholders clearly marked with TODO comments
- [ ] #6 Add --interactive flag to prompt for all values
<!-- AC:END -->
