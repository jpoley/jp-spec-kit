---
id: task-090
title: Implement WorkflowConfig Python class for config loading
status: Done
assignee: []
created_date: '2025-11-28 15:57'
updated_date: '2025-12-03 01:15'
labels:
  - implementation
  - python
  - core
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement Python class to load, parse, and provide query API for workflow configuration
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 WorkflowConfig class created in src/specify_cli/workflow/config.py
- [x] #2 Class loads jpspec_workflow.yml using YAML parser (PyYAML)
- [x] #3 Class provides query methods: get_agents(workflow), get_next_state(current_state, workflow), get_transitions()
- [x] #4 Class validates loaded config against JSON schema using jsonschema library
- [x] #5 Class raises clear exceptions for validation errors with helpful messages
- [x] #6 Class caches config in memory for performance
- [x] #7 Class supports reloading config for development workflow
- [x] #8 Comprehensive docstrings for all public methods
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementation verified complete 2025-12-01. All ACs met in src/specify_cli/workflow/config.py (707 lines). Tests: 47 tests passing.

Implementation complete on main: src/specify_cli/workflow/config.py (24KB, 700+ lines)
<!-- SECTION:NOTES:END -->
