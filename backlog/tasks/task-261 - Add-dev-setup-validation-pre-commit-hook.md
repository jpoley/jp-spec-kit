---
id: task-261
title: Add dev-setup validation pre-commit hook
status: In Progress
assignee: []
created_date: '2025-12-03 13:54'
updated_date: '2025-12-04 01:40'
labels:
  - infrastructure
  - hooks
  - dogfood
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Pre-commit hook to catch dogfood issues before commit. Provides fast local feedback to developers.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Script created: scripts/bash/pre-commit-dogfood.sh
- [ ] #2 Script is executable (chmod +x)
- [ ] #3 Added to .pre-commit-config.yaml
- [ ] #4 Hook detects non-symlink .md files
- [ ] #5 Hook detects broken symlinks
- [ ] #6 Hook provides clear error messages and fix instructions
- [ ] #7 Hook can be run manually: ./scripts/bash/pre-commit-dogfood.sh
<!-- AC:END -->
