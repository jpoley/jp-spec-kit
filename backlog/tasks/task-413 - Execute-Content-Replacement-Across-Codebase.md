---
id: task-413
title: Execute Content Replacement Across Codebase
status: To Do
assignee: []
created_date: '2025-12-10 02:58'
labels:
  - infrastructure
  - migration
  - content-replacement
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Replace all specflow references in file contents with specflow equivalents using sed-based bulk replacement.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 /specflow: replaced with /specflow: in all command files
- [ ] #2 specflow_workflow replaced with specflow_workflow in all YAML/Python files
- [ ] #3 commands/specflow/ replaced with commands/specflow/ in all references
- [ ] #4 specflow- replaced with specflow- in agent and test references
- [ ] #5 test_specflow_ replaced with test_specflow_ in test files
- [ ] #6 Verification shows <10 remaining specflow references (excluding allowed locations)
<!-- AC:END -->
