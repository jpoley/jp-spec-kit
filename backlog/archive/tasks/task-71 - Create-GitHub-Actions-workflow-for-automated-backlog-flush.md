---
id: task-71
title: Create GitHub Actions workflow for automated backlog flush
status: Done
assignee:
  - '@claude'
created_date: '2025-11-26 16:44'
updated_date: '2025-11-26 17:02'
labels:
  - ci-cd
  - github-actions
dependencies:
  - task-69
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create GitHub Actions workflow that triggers on push to main branch when commit message contains 'flush-backlog' keyword. Workflow installs backlog.md CLI, runs flush script, and commits/pushes the summary.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Workflow file created at .github/workflows/backlog-flush.yml with correct YAML syntax
- [x] #2 Triggers only on push to main branch (not feature branches or PRs)
- [x] #3 Conditional execution using if: contains() checks commit message for 'flush-backlog' (case-insensitive)
- [x] #4 Installs backlog.md CLI via npm as prerequisite step
- [x] #5 Runs flush-backlog.sh with TRIGGER_SOURCE env var set to 'automated (commit hash)'
- [x] #6 Commits flush summary with standardized message and pushes to main
- [x] #7 Workflow completes successfully even when no Done tasks exist (handles exit code 2)
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Check if .github/workflows directory exists
2. Create backlog-flush.yml with all required steps
3. Validate YAML syntax
4. Check all acceptance criteria are met
5. Commit the workflow file
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created GitHub Actions workflow for automated backlog flush with the following implementation:

- Workflow triggers on push to main branch only
- Uses conditional execution with `if: contains()` to check for "flush-backlog" keyword (case-insensitive)
- Installs Node.js 20 and backlog.md CLI via npm
- Runs flush-backlog.sh script with TRIGGER_SOURCE env var set to "automated (commit <hash>)"
- Handles exit code 2 (no Done tasks) gracefully by setting has_changes=false
- Only commits and pushes changes when tasks were actually archived
- Uses github-actions[bot] for commit authorship
- YAML syntax validated successfully

All acceptance criteria met and verified.
<!-- SECTION:NOTES:END -->
