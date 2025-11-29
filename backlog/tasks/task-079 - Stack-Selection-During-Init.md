---
id: task-079
title: Stack Selection During Init
status: To Do
assignee: []
created_date: '2025-11-27 21:53'
updated_date: '2025-11-29 05:38'
labels:
  - specify-cli
  - feature
  - stacks
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Allow users to select a technology stack (React+Go, React+Python, Full-Stack TypeScript, Mobile+Go, Data/ML Pipeline, etc.) when running 'specify init'. After selection, remove unselected stack files to reduce clutter. Copy selected stack's CI/CD workflow to .github/workflows/. Feasibility: MEDIUM-HIGH complexity, 3-5 days effort.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Add STACK_CONFIG to specify-cli with all 9 stack definitions
- [ ] #2 Create interactive stack selection UI (arrow keys)
- [ ] #3 Add --stack CLI flag for non-interactive use
- [ ] #4 Implement cleanup function to remove unselected stacks
- [ ] #5 Copy selected stack workflow to .github/workflows/
- [ ] #6 Add skip option to keep all stacks
- [ ] #7 Update release packages to include stacks
- [ ] #8 Create integration tests for stack selection
<!-- AC:END -->
