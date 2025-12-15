---
id: task-279
title: Update documentation for new architecture
status: In Progress
assignee:
  - '@galway'
created_date: '2025-12-03 14:01'
updated_date: '2025-12-15 02:17'
labels:
  - bug
  - documentation
  - branding
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
BUG FIX: Documentation contains outdated branding references and deployment is broken.

Issues:
1. ~35 references to "Specflow/specflow" need updating to "flowspec"
2. ~120 references to "JP Spec/flowspec" need updating to "flowspec"  
3. docfx.json uses old "Specflow" branding
4. docs.yml workflow uses "Specflow" in footer
5. GitHub Pages deployment failing due to environment protection rules

Original scope (architecture docs) merged into this fix.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Update docfx.json branding from Specflow to flowspec
- [x] #2 Update docs.yml workflow footer branding
- [x] #3 Rename all Specflow references in docs/ to flowspec
- [x] #4 Update JP Spec/flowspec references to flowspec where appropriate
- [ ] #5 Verify docs build locally with docfx
- [x] #6 Document GitHub Pages environment protection rule fix needed
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## GitHub Pages Deployment Fix Required

**Issue**: The docs workflow (v0.2.348) failed due to environment protection rules:
> Tag "v0.2.348" is not allowed to deploy to github-pages due to environment protection rules.

**Root Cause**: The `github-pages` environment has protection rules that don't allow deployment from release tags.

**Fix Required** (manual in GitHub settings):
1. Go to: https://github.com/jpoley/flowspec/settings/environments
2. Click on `github-pages` environment
3. Under "Deployment branches and tags", add rule:
   - Select "Selected branches and tags"
   - Add pattern: `v*` (allows all version tags)
4. Save

Alternatively, use "No restriction" if you want all branches/tags to deploy.

**After fixing**: Re-run the failed docs workflow or create a new release to trigger deployment.
<!-- SECTION:NOTES:END -->
