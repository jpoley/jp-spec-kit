---
id: task-261
title: Add dev-setup validation pre-commit hook
status: Done
assignee:
  - '@adare'
created_date: '2025-12-03 13:54'
updated_date: '2025-12-15 01:48'
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
- [x] #1 Script created: scripts/bash/pre-commit-dev-setup.sh
- [x] #2 Script is executable (chmod +x)
- [x] #3 Added to .pre-commit-config.yaml
- [x] #4 Hook detects non-symlink .md files
- [x] #5 Hook detects broken symlinks
- [x] #6 Hook provides clear error messages and fix instructions
- [x] #7 Hook can be run manually: ./scripts/bash/pre-commit-dev-setup.sh
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementation complete with script named `pre-commit-dev-setup.sh` (better describes purpose than original `pre-commit-dogfood.sh`). Script validates .claude/commands/ symlink structure to ensure single-source-of-truth. All 7 ACs met.
<!-- SECTION:NOTES:END -->
