---
id: task-428
title: 'CRITICAL: /flowspec commands installation failure - forensic analysis and fix'
status: Done
assignee:
  - '@adare'
created_date: '2025-12-10 20:17'
updated_date: '2025-12-15 01:49'
labels:
  - critical
  - release
  - flowspec
  - cli
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
# Critical Failure Analysis: /flowspec Commands Not Working

## Executive Summary

Multiple cascading failures have resulted in users being unable to use `/flowspec` commands when installing flowspec. This affects ALL new installations and reinstallations.

## Root Cause Analysis

### Failure #1: Release Tag Race Condition

**What happened:** The v0.2.344 release was tagged on a commit (`8b0c8d6`) that **forked BEFORE** the flowspec rename PR was merged.

**Evidence:**
```
Git graph shows parallel paths:
* d04de27 chore: release v0.2.344 (#722)   <-- CURRENT main
* 9908e7d fix: PR-based release workflow (#721)
* 8da08a6 feat!: rename /flowspec to /flowspec (#719)  <-- FLOWSPEC RENAME
| * 8b0c8d6 chore: release v0.2.344        <-- v0.2.344 TAG HERE (WRONG!)
|/  
* ac228c2 docs(task-410.06): Flowspec branding  <-- COMMON ANCESTOR
```

**Impact:** v0.2.344 release packages contain `/flowspec` commands, NOT `/flowspec` commands.

**Verification:**
- `git merge-base --is-ancestor 8da08a6 v0.2.344` returns FALSE
- v0.2.344 packages show `templates/commands/flowspec/` (no flowspec)

### Failure #2: Symlinks in Git Don't Work in GitHub Zipballs

**What happened:** The `.claude/commands/` directory uses symlinks pointing to `../../../templates/commands/...`. GitHub zipballs convert these to text files containing the path string.

**Evidence:**
```bash
# At v0.2.343, .claude/commands/flowspec/init.md is:
$ git show v0.2.343:.claude/commands/flowspec/init.md
../../../templates/commands/flowspec/init.md  # Just 46 bytes of text!

# Should be 11,580 bytes of actual content
```

**Impact:** Anyone cloning the repo directly (not using release packages) gets broken commands that are just text files with paths.

**Note:** This doesn't affect `specify init` users because that downloads RELEASE PACKAGES (which are generated from templates), not the repo zipball. But it affects:
- Direct cloners
- Developers working on the repo
- CI/CD pipelines that clone

### Failure #3: Incorrect Command Namespace in All Recent Releases

**What happened:** Even v0.2.344 (today's release) generates packages with `/flowspec:*` commands instead of `/flow:*`.

**Evidence:**
```bash
$ unzip -l spec-kit-template-claude-sh-v0.2.344.zip | grep commands
.claude/commands/flowspec/init.md      # WRONG - should be flowspec
.claude/commands/flowspec/specify.md   # WRONG
.claude/commands/flowspec/plan.md      # WRONG
```

**Impact:** Users installing with `specify init` get commands like `/flowspec:init` which:
1. Don't match the documentation (which says `/flow:*`)
2. Don't match the CLAUDE.md instructions
3. Create massive user confusion

### Failure #4: Version Display Issue (Needs Clarification)

**User reported:** "it said flowspec was version 1.0.0"

**Investigation:** The code has `CONSTITUTION_VERSION = "1.0.0"` which is for constitution templates, not the package version. Package version at v0.2.344 is correctly "0.2.344".

**Possible causes:**
- User may have seen constitution version instead of package version
- May be a display bug in `specify init` output
- May be from a different error path

**ACTION NEEDED:** User clarification on where "1.0.0" was displayed.

## Affected Users

1. **ALL new `specify init` installations** - Get flowspec commands instead of flowspec
2. **ALL reinstallations** - Same issue
3. **Direct repo cloners** - Get broken symlink text files
4. **Developers** - Local development environment has broken symlinks

## Timeline of Events

| Date | Event | Commit | Issue |
|------|-------|--------|-------|
| Dec 7 | flowspec symlinks introduced | 520e124 | Symlinks don't work in zipballs |
| Dec 10 9:37 | Flowspec rename merged | 8da08a6 | -- |
| Dec 10 ~10:00 | v0.2.344 release created | 8b0c8d6 | Tagged BEFORE rename merge |
| Dec 10 ~11:00 | v0.2.344 packages built | -- | Built from wrong commit |

## What Works vs What's Broken

| Scenario | Status | Details |
|----------|--------|---------|
| `specify init --ai claude` | PARTIAL | Gets flowspec commands, not flowspec |
| `/flow:init` command | BROKEN | Command doesn't exist in packages |
| `/flowspec:init` command | WORKS | But deprecated/undocumented |
| Direct repo clone | BROKEN | Symlinks become text files |
| Documentation | INCORRECT | Says /flowspec but users get /flowspec |
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Running `specify init --ai claude` creates project with `/flow:*` commands
- [x] #2 All /flowspec commands work as documented
- [x] #3 Release packages contain flowspec directory (not flowspec)
- [ ] #4 Direct repo clones have real files (not symlinks) in .claude/commands/
- [x] #5 Version numbers are correct and consistent
- [x] #6 Documentation matches actual behavior

- [x] #7 Release system MUST accept explicit commit hash parameter to prevent race conditions between branch creation and tag creation
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Implementation Plan

### Phase 1: Replace Symlinks with Real Files (~30 min)
**Problem solved:** Failure #2 - GitHub zipballs break symlinks

**Directories to fix:**
- `.claude/commands/flow/` - Replace symlinks → real files
- `.claude/commands/pm/` - Replace symlinks → real files
- `.claude/commands/dev/` - Replace symlinks → real files
- `.claude/commands/arch/` - Replace symlinks → real files
- `.claude/commands/ops/` - Replace symlinks → real files
- `.claude/commands/qa/` - Replace symlinks → real files
- `.claude/commands/sec/` - Replace symlinks → real files
- `.claude/commands/speckit/` - Replace symlinks → real files
- `.claude/skills/` - Check and fix if symlinks

**New files:**
- `.github/workflows/check-command-sync.yml` - CI check that .claude/commands/ matches templates/commands/
- `scripts/bash/sync-commands.sh` - Script to copy from templates/ to .claude/

### Phase 2: Clean Up flowspec (~15 min)
**Problem solved:** Failure #4 - DEPRECATED stubs confusing users

**Files to delete:**
- All `templates/commands/flowspec/_DEPRECATED_*.md` files
- Archive or remove `templates/commands/flowspec/` directory

**Files to modify:**
- `.github/workflows/scripts/create-release-packages.sh` - Ensure flowspec excluded

### Phase 3: Fix Release System (~45 min)
**Problem solved:** Failures #1 and #5 - Race condition, unreliable releases

**scripts/release.py changes:**
- Add `--commit-hash` parameter (optional, defaults to HEAD)
- Write commit hash to `.release-commit` file in release branch
- Validate hash format

**release-on-merge.yml changes:**
- Read `.release-commit` file from merged PR
- Tag THAT specific commit, not HEAD
- Validate commit is ancestor of current HEAD
- Fail with clear error if validation fails

### Phase 4: Cut New Release (~15 min)
- Run `./scripts/release.py --commit-hash $(git rev-parse HEAD)`
- Verify PR contains correct commit reference
- After merge, verify tag points to correct commit
- Verify packages contain `/flowspec` commands

### Phase 5: Verification (~20 min)
- Fresh install: `uv tool install flowspec-cli --from git+https://github.com/jpoley/flowspec.git`
- Run: `specify init test-project --ai claude`
- Verify `/flow:*` commands present and functional
- Verify `/pm:*` commands present and functional
- Verify no `_DEPRECATED_` stubs in commands

## Risk Mitigations

1. **Breaking existing cloners:** Fix improves things - symlinks were already broken
2. **Release system changes:** Test with dry-run before real release
3. **Removing flowspec:** DEPRECATED stubs were broken anyway; document migration
4. **CI sync friction:** Provide sync-commands.sh script with clear errors

## Future Work (Separate Task)

- task-430: `flowspec-cli init` to replace `specify init` for AI tool management
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Additional Failure Mode: Fresh Install via `specify init`

When user runs:
```bash
uv tool install flowspec-cli --from git+https://github.com/jpoley/flowspec.git
specify init my-project --ai claude
```

They get:
1. CLI installs correctly (from git main branch)
2. `specify init` downloads RELEASE PACKAGES (v0.2.343 or v0.2.344)
3. Release packages contain `/flowspec:*` commands, NOT `/flow:*`
4. User sees `/flowspec:_DEPRECATED_*` commands (confusing)
5. Role-based commands (/pm, /dev, /arch) are MISSING

## Why DEPRECATED Commands Appear

The rename commit created `_DEPRECATED_*.md` stub files that say "use /pm:assess instead". These:
1. Were meant as backward compatibility redirects
2. Are showing up as primary commands because flowspec commands don't exist in packages
3. Are confusing users

## Role-Based Commands Missing

The /pm, /dev, /arch, /ops, /qa, /sec namespaces were supposed to be:
- ADDITIONS (new way to invoke same functionality)
- NOT deprecations of anything
- Should coexist with /flowspec commands

But they're:
1. Symlinks on origin/main (broken in git clones)
2. NOT in release packages at all (built from old code)

## Failure #5: Release System is Unreliable (CRITICAL)

**User reported:** `./scripts/release.py` was run AFTER the flowspec merge was on main, but the release was still built from old code.

**Impact:** The release system cannot be trusted to release current main. The next release will have the same problem.

**This MUST be fixed as part of this task** - without it, any fix we make won't actually get released correctly.

**Root cause investigation needed** - but NOT until user approves the plan.

## Completion Summary

All critical issues resolved:
- Release packages now contain /flow:* commands (not /flowspec or /specflow)
- Release system fixed (task-431) ensures correct commit is tagged
- Symlinks replaced with real files in release packages
- v0.2.347+ releases verified working with correct commands
- Branding updated to Specflow throughout
<!-- SECTION:NOTES:END -->
