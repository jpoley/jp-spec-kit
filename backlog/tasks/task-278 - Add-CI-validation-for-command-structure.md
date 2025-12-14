---
id: task-278
title: Add CI validation for command structure
status: Done
assignee:
  - '@muckross'
created_date: '2025-12-03 14:01'
updated_date: '2025-12-14 20:09'
labels:
  - ci
  - validation
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create GitHub Actions workflow to validate command structure and prevent drift
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create .github/workflows/validate-commands.yml
- [x] #2 Add check that .claude/commands/ contains only symlinks
- [x] #3 Add check that all symlinks resolve to templates/
- [x] #4 Add check that dogfood and init produce equivalent structures
- [x] #5 Add check for template file completeness
- [x] #6 Test workflow triggers on push and PR
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implementation Complete (2025-12-14)

Created `.github/workflows/validate-commands.yml` with three jobs:

1. **validate-symlinks** - Ensures .claude/commands/ contains only symlinks pointing to templates/commands/
2. **validate-templates** - Validates required directories and command files exist
3. **validate-equivalence** - Tests that `specify init` and `specify dev-setup` produce correct structures

Triggers on push and PR to main when .claude/commands/** or templates/commands/** change.
<!-- SECTION:NOTES:END -->
