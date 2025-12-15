---
id: task-311.04
title: Add scheduled workflow to cleanup stale version-bump branches
status: To Do
assignee:
  - '@galway'
created_date: '2025-12-08 01:43'
updated_date: '2025-12-15 02:17'
labels:
  - ci
  - github-actions
  - cleanup
dependencies: []
parent_task_id: task-311
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a scheduled GitHub Action to periodically clean up any orphaned `chore/version-bump-*` branches older than 7 days.

**New workflow**: `.github/workflows/cleanup-branches.yml`

```yaml
name: Cleanup Stale Branches

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:

jobs:
  cleanup:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - name: Delete stale version-bump branches
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          # Find and delete version-bump branches older than 7 days
          for branch in $(gh api repos/${{ github.repository }}/branches --paginate -q '.[].name | select(startswith("chore/version-bump"))'); do
            echo "Deleting stale branch: $branch"
            git push origin --delete "$branch" || true
          done
```
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Workflow runs weekly on schedule
- [ ] #2 Deletes chore/version-bump-* branches
- [ ] #3 Can be triggered manually via workflow_dispatch
<!-- AC:END -->
