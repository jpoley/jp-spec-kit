---
id: task-437.04
title: Create release notes and stale management workflows
status: Done
assignee:
  - '@adare'
created_date: '2025-12-11 03:28'
updated_date: '2025-12-15 02:18'
labels:
  - infrastructure
  - github
  - subtask
dependencies: []
parent_task_id: task-437
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Set up automated release notes generation and stale issue/PR management.

## Files to Create

### `.github/release.yml`
Release notes configuration:
- **Categories**:
  - Breaking Changes: breaking-change, breaking
  - New Features: feature, enhancement, feat
  - Bug Fixes: bug, fix, bugfix
  - Documentation: documentation, docs
  - Dependencies: dependencies, deps
  - Other Changes: *
- **Exclude**:
  - Labels: skip-changelog, duplicate, invalid, wontfix
  - Authors: renovate, renovate[bot], github-actions[bot]

### `.github/workflows/stale.yml`
Stale management:
- **Issues**: 60 days -> stale, 7 days -> close
- **PRs**: 30 days -> stale, 7 days -> close
- **Exempt labels**: pinned, security, PRD
- **Exempt**: milestones, assignees
- **Schedule**: daily cron
- **Messages**: Customized stale/close messages

## Reference
- task-437 (parent)
- https://github.com/vfarcic/dot-ai/.github/release.yml
- https://github.com/vfarcic/dot-ai/.github/workflows/stale.yml
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 release.yml categorizes PRs by label for changelog generation
- [x] #2 Bot authors excluded from release notes
- [x] #3 stale.yml workflow runs on daily schedule
- [x] #4 Issues marked stale after 60 days, closed after 67 days
- [x] #5 PRs marked stale after 30 days, closed after 37 days
- [x] #6 Security and pinned labels exempt from stale automation
- [x] #7 Action versions pinned with full commit SHA
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created release notes and stale management:

1. .github/release.yml
   - 8 categories: Breaking Changes, New Features, Bug Fixes, Security, Documentation, Dependencies, Infrastructure, Other
   - Excludes: skip-changelog, duplicate, invalid, wontfix labels
   - Excludes bot authors: renovate, github-actions, dependabot

2. .github/workflows/stale.yml
   - Issues: 60 days stale, 67 days close
   - PRs: 30 days stale, 37 days close
   - Exempt labels: pinned, security, PRD, critical, blocked, work-in-progress
   - Exempt: milestones, assignees
   - Action pinned: stale@28ca1036281a5e5922ead5184a1bbf96e5fc984e (v9.0.0)
   - Cron: 3:17 AM UTC (avoids :00)
   - Manual trigger enabled

Labels verified/created: breaking-change, feature, stale, pinned, PRD, work-in-progress, skip-changelog, blocked, critical, needs-triage
<!-- SECTION:NOTES:END -->
