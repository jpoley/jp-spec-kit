---
id: task-431
title: 'CRITICAL: Release system fundamentally broken - unified workflow required'
status: To Do
assignee: []
created_date: '2025-12-10 21:39'
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
- [ ] #1 Single unified release.yml workflow handles entire release process
- [ ] #2 release-on-merge.yml is deleted
- [ ] #3 Branding updated to Specflow everywhere (not Spec Kit Templates)
- [ ] #4 Test release v0.2.346+ creates tag AND GitHub Release with artifacts
- [ ] #5 Documentation updated to reflect new release process
<!-- AC:END -->
