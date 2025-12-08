---
id: task-206
title: Create specify init Hook Scaffolding
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-12-03 00:41'
updated_date: '2025-12-03 01:47'
labels:
  - implement
  - cli
  - hooks
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Extend 'specify init' command to create .specify/hooks/ directory structure with example hooks and documentation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create .specify/hooks/ directory during project initialization
- [x] #2 Generate hooks.yaml template with commented examples
- [x] #3 Create example hook scripts (run-tests.sh, update-docs.sh)
- [x] #4 Add hooks section to project CLAUDE.md template
- [x] #5 Integration test verifying directory structure created
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created src/specify_cli/hooks/scaffold.py with:
- EXAMPLE_HOOKS_YAML with 4 example hooks (run-tests, update-changelog, lint-code, quality-gate)
- 4 example shell scripts with real-world patterns
- README.md for the hooks directory
- scaffold_hooks() function to create all files

Integrated into specify init command at line 2154-2168:
- Automatically creates .specify/hooks/ directory structure
- Creates 6 files total (hooks.yaml, 4 scripts, README.md)
- Non-fatal error handling (warns but continues if hook setup fails)
- Progress tracking in init output
<!-- SECTION:NOTES:END -->
