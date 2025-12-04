---
id: task-168
title: Add macOS CI Matrix Testing
status: To Do
assignee:
  - '@kinsale'
created_date: '2025-11-30 16:49'
updated_date: '2025-12-04 17:07'
labels:
  - ci-cd
  - enhancement
  - 'workflow:Specified'
dependencies: []
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add macos-latest to GitHub Actions CI matrix to verify cross-platform compatibility of run-local-ci.sh and other bash scripts. This follows up on task-085 AC #9 which verified Linux compatibility and documented portable design.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Add macos-latest to strategy.matrix.os in .github/workflows/ci.yml
- [ ] #2 Verify run-local-ci.sh passes on macOS runner
- [ ] #3 Fix any platform-specific issues discovered (if any)
- [ ] #4 Document macOS-specific requirements or limitations in scripts/CLAUDE.md
<!-- AC:END -->
