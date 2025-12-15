---
id: task-311.01
title: Fix double-dash in version-bump branch name
status: Done
assignee:
  - '@galway'
created_date: '2025-12-08 01:43'
updated_date: '2025-12-15 13:43'
labels:
  - bug
  - ci
  - github-actions
dependencies: []
parent_task_id: task-311
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Fix the branch naming regex in `.github/workflows/release.yml` line 97.

**Current code**:
```bash
BRANCH_NAME="chore/version-bump-${NEW_VERSION//[^0-9.]/-}"
```

**Problem**: When `NEW_VERSION=v0.2.332`, the regex replaces `v` with `-`, creating `chore/version-bump--0.2.332` (double dash).

**Fix**: Strip the `v` prefix first:
```bash
VERSION_NUM="${NEW_VERSION#v}"
BRANCH_NAME="chore/version-bump-${VERSION_NUM}"
```

**Location**: `.github/workflows/release.yml:97`
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Branch name is chore/version-bump-0.2.332 (single dash)
- [ ] #2 No regex replacement needed - just strip v prefix
<!-- AC:END -->
