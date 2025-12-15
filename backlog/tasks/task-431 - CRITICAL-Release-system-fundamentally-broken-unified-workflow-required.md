---
id: task-431
title: 'CRITICAL: Release system fundamentally broken - unified workflow required'
status: Done
assignee:
  - '@adare'
created_date: '2025-12-10 21:39'
updated_date: '2025-12-15 02:18'
labels:
  - release
  - critical
  - ci-cd
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## Problem Statement

The release system is **fundamentally broken** due to a GitHub Actions security limitation that was not understood when designing the two-workflow release process.

### Root Cause

The current release system uses TWO workflows:
1. `release-on-merge.yml` - Creates git tag when release PR merges
2. `release.yml` - Triggers on tag push, builds packages, creates GitHub Release

**THE FATAL FLAW**: When `release-on-merge.yml` pushes a tag using `GITHUB_TOKEN`, GitHub **intentionally does NOT trigger** other workflows. This is a security feature to prevent infinite workflow loops.

Result: Tag v0.2.345 was created, but `release.yml` NEVER ran. No GitHub Release. No artifacts. Only source code.

### Evidence

```
Tag v0.2.345: EXISTS (created by release-on-merge.yml)
release.yml runs for v0.2.345: ZERO
GitHub Release v0.2.345: DOES NOT EXIST
Artifacts for v0.2.345: NONE
Latest release shown: v0.2.344 (the last working release)
```

### Secondary Issues

1. **Branding inconsistency**: Release titles say "Spec Kit Templates" - should be "Specflow"
2. **Unnecessary complexity**: Two workflows when one would work
3. **The race condition fix is moot**: PR #725 fixed commit pinning, but it doesn't matter if release.yml never runs

### Impact

- Users cannot install working releases
- v0.2.345 tag exists but has no usable artifacts
- Trust in the release process is destroyed
- Every release since the two-workflow design has been at risk

## Solution

**ONE unified workflow** that does everything in a single execution:
1. Triggers on release PR merge
2. Creates the tag
3. Builds packages
4. Creates GitHub Release with all artifacts

No handoff between workflows. No GITHUB_TOKEN limitation issue.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Single unified release.yml workflow handles entire release process
- [x] #2 release-on-merge.yml is deleted
- [x] #3 Branding updated to Specflow everywhere (not Spec Kit Templates)
- [x] #4 Test release v0.2.346+ creates tag AND GitHub Release with artifacts
- [x] #5 Documentation updated to reflect new release process
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementation PR: https://github.com/jpoley/flowspec/pull/728

Changes made:
1. Rewrote release.yml as unified workflow that handles the entire release process
2. Deleted release-on-merge.yml (no longer needed)
3. Updated branding from "Spec Kit Templates" to "Specflow"
4. Updated ADR-011 status to Accepted

The unified workflow:
- Triggers on release PR merge (pull_request closed + merged + release/v* branch)
- Also supports workflow_dispatch for manual releases
- Creates annotated tag on pinned commit from .release-commit file
- Builds Python packages with uv
- Creates template zips for all 13 AI assistants
- Creates GitHub Release with all artifacts
- Deletes release branch on success

Key design: No handoff between workflows = no GITHUB_TOKEN limitation.

Next: Test with v0.2.346 release after PR merge.

## Completion Summary

The unified release workflow was implemented and verified working:
- v0.2.347, v0.2.348, v0.2.349 all released successfully with Specflow branding
- release-on-merge.yml deleted, release.yml handles everything
- All acceptance criteria verified complete on 2025-12-10
<!-- SECTION:NOTES:END -->
