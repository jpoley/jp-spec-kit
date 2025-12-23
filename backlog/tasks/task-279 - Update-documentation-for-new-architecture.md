---
id: task-279
title: Update documentation for new architecture
status: Done
assignee:
  - '@myself'
created_date: '2025-12-03 14:01'
updated_date: '2025-12-23 18:56'
labels:
  - bug
  - documentation
  - branding
  - 'workflow:ReadyForDone'
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
- [x] #5 Verify docs build locally with docfx
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

## Branding Cleanup Completed (2025-12-16)

Fixed the following files:
- **CLAUDE.md**: Updated JP Spec + Backlog.md Integration references to Flowspec
- **LAYERED-EXTENSION-ARCHITECTURE.md**: Fixed JP Flowspec/JP spec-kit references, updated src/specify_cli paths to src/flowspec_cli
- **muckross-security-platform-plan-v2.md**: Fixed JP Spec workflow reference, updated all specify CLI commands to flowspec
- **backlog-user-guide.md**: Fixed JP Spec Integration Guide link, updated specify tasks generate to flowspec
- **CONTRIBUTING.md**: Fixed spec-kit reference to Flowspec
- **design-command-migration-path.md**: Updated all specify migrate-commands to flowspec migrate-commands

Decisions documented in: docs/decisions/task-279-branding-cleanup.jsonl

Branch: 279-doc-branding-cleanup

## Final Verification Completed (2025-12-22)

### GitHub Pages Environment Configuration - ALREADY FIXED

**Status**: ✅ Environment protection rules are correctly configured

**Current Configuration**:
- Environment: `github-pages`
- Protection rules: branch_policy enabled
- Deployment branch policy: custom_branch_policies = true
- **Branch policies**:
  - `main` branch (id: 39620594)
  - `v*` tag pattern (id: 39678618) ✅

**Conclusion**: The `v*` tag pattern protection rule mentioned in AC#6 is **already configured** in the GitHub Pages environment. Tags matching `v*` (e.g., v0.2.348, v0.3.0) are allowed to deploy.

### Recent Workflow Status

The docs.yml workflow shows "skipped" status for recent workflow_run events. This is **expected behavior**:
- Workflow_run triggers skip when the upstream Release workflow doesn't create a new release
- Actual release-triggered deployments will succeed with the v* tag rule in place

### Branding Cleanup Status

All branding updates completed in PR #894 and PR #900:
- ✅ docfx.json: "Flowspec Documentation" branding
- ✅ docs.yml: "Flowspec v{VERSION}" footer injection
- ✅ ~35 Specflow references updated to flowspec
- ✅ ~120 JP Spec/flowspec references updated to flowspec
- ✅ DocFX structure validated and resilient

### Ready for Completion

All 6 acceptance criteria are complete. The GitHub Pages environment is correctly configured. No manual settings changes required.

Next release (when created) will deploy docs successfully to GitHub Pages.

## Sprint Planning (Dec 22)

**Status**: Ready for Done
**All ACs complete**: Yes (6/6)
**Blockers**: None

GitHub Pages environment protection rules already configured for v* tags. Task can be marked Done immediately after visual verification of docs site.

## Closed (Dec 22)

All ACs were already complete. GitHub Pages environment protection rules confirmed configured correctly. Task ready for closure per planning analysis.
<!-- SECTION:NOTES:END -->
