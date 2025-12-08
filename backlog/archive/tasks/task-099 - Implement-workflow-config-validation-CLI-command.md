---
id: task-099
title: Implement workflow config validation CLI command
status: Done
assignee: []
created_date: '2025-11-28 15:58'
updated_date: '2025-12-03 01:44'
labels:
  - implementation
  - cli
  - validation
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement CLI command to validate workflow configuration files for both syntax and semantic correctness
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 New command 'specify workflow validate' implemented
- [x] #2 Command validates jpspec_workflow.yml against JSON schema
- [x] #3 Command runs semantic validation checks (circular deps, reachability, etc)
- [x] #4 Command provides clear success message when validation passes
- [x] #5 Command provides detailed error messages for validation failures
- [x] #6 Command exits with code 0 on success, non-zero on failure
- [x] #7 Command can validate custom workflow files with --file option
- [x] #8 Command provides --verbose flag for detailed output
<!-- AC:END -->
