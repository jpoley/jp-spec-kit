---
id: task-312
title: 'Research: Analyze version management workflow order of operations'
status: Done
assignee:
  - '@galway'
created_date: '2025-12-08 02:05'
updated_date: '2025-12-15 02:17'
labels:
  - research
  - ci
  - version-management
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## Research Task

Analyze the current release workflow to understand the exact order of operations and identify all version desync scenarios.

**Current State**:
- pyproject.toml shows `0.2.328`
- Latest git tag is `v0.2.334`
- 6 version gap exists

**Research Questions**:
1. Why does the workflow create tags before updating version files?
2. What happens when the version bump commit fails?
3. Are there race conditions with multiple releases?
4. What permissions are needed for the fallback PR creation?

**Files to Analyze**:
- `.github/workflows/release.yml`
- `.github/workflows/scripts/get-next-version.sh`
- `.github/workflows/scripts/update-version.sh`

**Output**: Document findings and propose solution architecture for task-312.01
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Document current workflow order with diagram
- [x] #2 Identify all failure modes that cause version desync
- [x] #3 Propose solution architecture (version-first vs tag-first)
- [x] #4 Validate solution works with branch protection
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Research Completed

**Report**: docs/research/version-management-research.md

### Key Findings

1. **Root Cause**: Tags created BEFORE version files updated (lines 32-43 vs 62-68 in release.yml)

2. **Version Desync**: 9-version gap (tags at v0.2.340, files at 0.2.328)

3. **Four Failure Modes Identified**:
   - Version desync (100% occurrence with branch protection)
   - Orphaned branches (4 found with double-dash bug)
   - Race conditions (unlikely but possible)
   - Silent failures (continue-on-error masks problems)

4. **Recommendation**: Version-first architecture with PR auto-merge

### Follow-up Implementation Tasks

- task-311.01: Fix double-dash branch naming → PR #629
- task-310.01: Fix version detection → PR #630
- task-313: Core workflow refactor (version-first)
- task-314: Sync pyproject.toml to latest tag
- task-315: Add release workflow integration tests
<!-- SECTION:NOTES:END -->
