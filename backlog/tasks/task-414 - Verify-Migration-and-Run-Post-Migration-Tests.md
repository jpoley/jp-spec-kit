---
id: task-414
title: Verify Migration and Run Post-Migration Tests
status: To Do
assignee: []
created_date: '2025-12-10 02:58'
labels:
  - infrastructure
  - migration
  - verification
  - testing
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Run comprehensive verification suite to validate migration completeness and correctness.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 verify-specflow-migration.sh passes all checks
- [ ] #2 All pytest tests pass with new naming
- [ ] #3 No broken symlinks in .claude/commands/
- [ ] #4 YAML workflow files are valid (Python yaml.safe_load succeeds)
- [ ] #5 Command files contain no /specflow: references
- [ ] #6 Local CI simulation passes (./scripts/bash/run-local-ci.sh)
<!-- AC:END -->
