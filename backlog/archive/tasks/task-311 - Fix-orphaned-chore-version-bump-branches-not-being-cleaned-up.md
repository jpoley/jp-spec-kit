---
id: task-311
title: Fix orphaned chore/version-bump branches not being cleaned up
status: Done
assignee:
  - '@galway'
created_date: '2025-12-08 01:43'
updated_date: '2025-12-15 13:43'
labels:
  - bug
  - ci
  - github-actions
  - cleanup
dependencies:
  - task-313
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## Bug Description

Branches like `chore/version-bump--0.2.332` are created by the release workflow but never cleaned up, leaving orphaned branches in the repository.

**Observed**: Multiple `chore/version-bump-*` branches accumulating in the repo.

## Root Cause Analysis

The issue is in `.github/workflows/release.yml` at lines 96-114.

**The workflow logic**:
1. After creating a release, tries to update version in source files
2. Tries direct push to main (line 89) - **fails due to branch protection**
3. Falls back to creating a branch `chore/version-bump-{version}` (lines 97-99)
4. Pushes the branch (line 99)
5. Tries to create a PR (lines 102-106)

**Problems identified**:

1. **PR creation likely fails** - GitHub Actions token may not have permission to create PRs, or the PR creation fails silently and the branch is left orphaned

2. **No cleanup on PR merge** - Even if PR is created and merged, the branch is never deleted

3. **No cleanup on PR creation failure** - If PR creation fails (lines 108-114), the branch remains with a manual action note but no automation to clean it up

4. **Double-dash in branch name** - The regex `${NEW_VERSION//[^0-9.]/-}` creates `chore/version-bump--0.2.332` (double dash) because it replaces `v` with `-` from `v0.2.332`

## Code Location

`.github/workflows/release.yml:96-114`

```yaml
# Create a branch and PR for the version bump
BRANCH_NAME="chore/version-bump-${NEW_VERSION//[^0-9.]/-}"  # Bug: double dash
git checkout -b "$BRANCH_NAME"
git push origin "$BRANCH_NAME"

# Try to create PR - may fail if Actions can't create PRs
if gh pr create ...; then
  echo "✅ Created PR for version bump"
else
  # Branch left orphaned here!
  echo "⚠️ Could not create PR automatically."
  ...
fi
```

## Impact

- Repository accumulates stale branches over time
- Confusing for developers who see these orphaned branches
- Potential for conflicts if version bump branches pile up
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Branch is deleted after PR is merged (enable delete branch on merge)
- [ ] #2 Branch is deleted if PR creation fails
- [ ] #3 Fix double-dash in branch name (v0.2.332 → 0.2.332 not --0.2.332)
- [ ] #4 Add workflow to periodically clean up stale version-bump branches
<!-- AC:END -->
