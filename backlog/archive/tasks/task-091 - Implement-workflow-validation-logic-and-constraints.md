---
id: task-091
title: Implement workflow validation logic and constraints
status: Done
assignee: []
created_date: '2025-11-28 15:57'
updated_date: '2025-12-01 05:06'
labels:
  - implementation
  - python
  - validation
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement semantic validation logic that checks workflow configuration for logical errors beyond schema syntax
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 WorkflowValidator class created in src/specify_cli/workflow/validator.py
- [x] #2 Validator checks for circular state transitions (no cycles in DAG)
- [x] #3 Validator checks all states are reachable from 'To Do'
- [x] #4 Validator checks all referenced states exist in states list
- [x] #5 Validator checks all workflow references exist in workflows list
- [x] #6 Validator checks all agent names are valid/defined
- [x] #7 Validator provides detailed error messages for each validation failure
- [x] #8 Validator can be called at config load time and provides both warnings and errors
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementation verified complete 2025-12-01. All ACs met in src/specify_cli/workflow/validator.py (658 lines). Tests: 63 tests passing.
<!-- SECTION:NOTES:END -->
