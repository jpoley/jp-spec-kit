---
id: task-483
title: 'claude-improves: Add CODEOWNERS template'
status: Done
assignee:
  - '@kinsale'
created_date: '2025-12-12 01:15'
updated_date: '2025-12-28 22:15'
labels:
  - claude-improves
  - templates
  - github
  - governance
  - phase-2
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
No .github/CODEOWNERS file is created. This is important for code review automation and ownership clarity.

Should provide template that assigns ownership based on directory structure.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 CODEOWNERS template created in templates/
- [ ] #2 Default ownership assigned to repository owner
- [ ] #3 Specific paths have appropriate owners (docs/, src/, tests/)
- [ ] #4 Comments explain CODEOWNERS syntax
- [ ] #5 Template includes common patterns for monorepos
- [ ] #6 specify init copies to .github/CODEOWNERS
<!-- AC:END -->
