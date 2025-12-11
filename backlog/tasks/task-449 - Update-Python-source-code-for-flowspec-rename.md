---
id: task-449
title: Update Python source code for flowspec rename
status: To Do
assignee: []
created_date: '2025-12-11 01:36'
labels:
  - backend
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Replace all flowspec references in Python source code with flowspec. Covers 20 Python files in src/specify_cli/. **Depends on: task-448 (schema rename)**
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All 'flowspec' → 'flowspec' in src/**/*.py files
- [ ] #2 All 'FLOWSPEC' → 'FLOWSPEC' in constants and env vars
- [ ] #3 All '/flow:' → '/flow:' in command strings
- [ ] #4 Docstrings and comments updated
- [ ] #5 Error messages updated to reference new names
- [ ] #6 No broken imports
- [ ] #7 Linting passes (ruff check)
- [ ] #8 All affected tests pass
<!-- AC:END -->
