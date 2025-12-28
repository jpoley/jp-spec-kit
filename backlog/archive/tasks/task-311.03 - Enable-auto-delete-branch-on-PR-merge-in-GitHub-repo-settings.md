---
id: task-311.03
title: Enable auto-delete branch on PR merge in GitHub repo settings
status: Done
assignee:
  - '@galway'
created_date: '2025-12-08 01:43'
updated_date: '2025-12-15 13:43'
labels:
  - ci
  - github-actions
  - config
dependencies: []
parent_task_id: task-311
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Ensure the GitHub repository has "Automatically delete head branches" enabled.

**Steps**:
1. Go to repository Settings → General
2. Under "Pull Requests" section
3. Enable "Automatically delete head branches"

This ensures version-bump branches are deleted when their PRs are merged.

**Note**: This is a repo setting, not a code change.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 GitHub repo setting 'Automatically delete head branches' is enabled
- [ ] #2 Merged PR branches are automatically deleted
<!-- AC:END -->
