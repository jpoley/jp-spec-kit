---
id: task-278
title: Add CI validation for command structure
status: Done
assignee:
  - '@galway'
created_date: '2025-12-03 14:01'
updated_date: '2025-12-15 13:43'
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
- [ ] #1 Create .github/workflows/validate-commands.yml
- [ ] #2 Add check that .claude/commands/ contains only symlinks
- [ ] #3 Add check that all symlinks resolve to templates/
- [ ] #4 Add check that dogfood and init produce equivalent structures
- [ ] #5 Add check for template file completeness
- [ ] #6 Test workflow triggers on push and PR
<!-- AC:END -->
