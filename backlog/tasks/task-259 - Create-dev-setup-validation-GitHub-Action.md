---
id: task-259
title: Create dev-setup validation GitHub Action
status: In Progress
assignee: []
created_date: '2025-12-03 13:54'
updated_date: '2025-12-04 01:40'
labels:
  - infrastructure
  - cicd
  - dogfood
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GitHub Actions workflow to validate dogfood consistency on every PR. Ensures .claude/commands/ only contains symlinks and prevents content drift.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Workflow file created at .github/workflows/dogfood-validation.yml
- [ ] #2 Validates no non-symlink .md files exist in .claude/commands/
- [ ] #3 Validates all symlinks resolve to existing templates
- [ ] #4 Runs dogfood command and verifies output structure
- [ ] #5 Executes test suite (test_dogfood_*.py)
- [ ] #6 Provides clear error messages on failure
<!-- AC:END -->
