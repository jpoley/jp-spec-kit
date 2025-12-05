---
id: task-261
title: Add dev-setup validation pre-commit hook
status: In Progress
assignee:
  - '@backend-engineer'
created_date: '2025-12-03 13:54'
updated_date: '2025-12-05 16:27'
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
- [x] #1 Script created: scripts/bash/pre-commit-dogfood.sh
- [x] #2 Script is executable (chmod +x)
- [x] #3 Added to .pre-commit-config.yaml
- [x] #4 Hook detects non-symlink .md files
- [x] #5 Hook detects broken symlinks
- [x] #6 Hook provides clear error messages and fix instructions
- [x] #7 Hook can be run manually: ./scripts/bash/pre-commit-dogfood.sh
<!-- AC:END -->
