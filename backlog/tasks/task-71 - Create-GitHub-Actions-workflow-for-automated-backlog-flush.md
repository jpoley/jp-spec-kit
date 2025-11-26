---
id: task-71
title: Create GitHub Actions workflow for automated backlog flush
status: To Do
assignee: []
created_date: '2025-11-26 16:44'
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
- [ ] #1 Workflow file created at .github/workflows/backlog-flush.yml with correct YAML syntax
- [ ] #2 Triggers only on push to main branch (not feature branches or PRs)
- [ ] #3 Conditional execution using if: contains() checks commit message for 'flush-backlog' (case-insensitive)
- [ ] #4 Installs backlog.md CLI via npm as prerequisite step
- [ ] #5 Runs flush-backlog.sh with TRIGGER_SOURCE env var set to 'automated (commit hash)'
- [ ] #6 Commits flush summary with standardized message and pushes to main
- [ ] #7 Workflow completes successfully even when no Done tasks exist (handles exit code 2)
<!-- AC:END -->
