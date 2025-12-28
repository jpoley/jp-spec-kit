---
id: task-282
title: >-
  Create backlog-archive.yml workflow with manual, scheduled, and keyword
  triggers
status: Done
assignee:
  - '@galway'
created_date: '2025-12-04 03:32'
updated_date: '2025-12-15 13:43'
labels:
  - infrastructure
  - ci-cd
  - github-actions
dependencies:
  - task-281
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement GitHub Actions workflow to automate backlog archiving with multiple trigger modes (workflow_dispatch, schedule, push keyword).

**Workflow Location**: `.github/workflows/backlog-archive.yml`

**Trigger Modes**:
1. **Manual Dispatch** (workflow_dispatch):
   - Input: mode (done/all/date)
   - Input: done_by_date (YYYY-MM-DD)
   - Input: dry_run (true/false)

2. **Scheduled** (cron):
   - Weekly on Sundays at midnight UTC
   - Archives Done tasks only

3. **Commit Keyword** (push):
   - Triggers when commit message contains 'archive-backlog'

**Workflow Steps**:
1. Checkout repository
2. Setup Node.js and install backlog CLI
3. Determine archive mode based on trigger
4. Run archive-tasks.sh script
5. Commit and push changes (if not dry-run)
6. Generate job summary

**Security**:
- Requires `contents: write` permission
- Uses GITHUB_TOKEN for commits
- Commits as github-actions[bot]

**References**:
- Existing workflow: `.github/workflows/backlog-flush.yml`
- Platform design: `docs/platform/archive-tasks-integration.md`
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Workflow supports manual dispatch with mode selection (done/all/date)
- [ ] #2 Workflow supports scheduled execution (weekly on Sundays)
- [ ] #3 Workflow supports commit keyword trigger (archive-backlog)
- [ ] #4 Workflow commits and pushes archive changes
- [ ] #5 Workflow generates job summary with archive results
- [ ] #6 Workflow handles exit codes correctly (0, 2 = success, 1/3 = failure)
- [ ] #7 Workflow has proper permissions (contents: write)
<!-- AC:END -->
