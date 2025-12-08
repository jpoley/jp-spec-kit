---
id: task-199
title: Design Hook Definition Format (YAML Schema)
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-12-03 00:40'
updated_date: '2025-12-03 01:13'
labels:
  - design
  - schema
  - hooks
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Design the YAML configuration format for hook definitions in .specify/hooks/hooks.yaml. Must support event matching, script execution, and security constraints.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Define YAML schema with event matchers (type, wildcards, filters)
- [x] #2 Support multiple execution modes (script, command, webhook placeholder)
- [x] #3 Include security constraints (allowlist, timeout, env vars)
- [x] #4 Create JSON Schema for hooks.yaml validation
- [x] #5 Document hook definition with 5+ realistic examples
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created src/specify_cli/hooks/schema.py

Implemented:
- EventMatcher dataclass with wildcard support (fnmatch)
- HookDefinition dataclass with execution methods (script, command, webhook)
- HooksConfig dataclass for complete configuration
- Event matching logic with filters (labels_any, labels_all, array match)
- JSON Schema for hooks.yaml validation (HOOKS_CONFIG_JSON_SCHEMA)
- Security constraints (timeout 1-600s, path validation)

All AC completed with comprehensive examples in docstrings
<!-- SECTION:NOTES:END -->
