# ADR-011: Unified Release Workflow

## Status

Proposed

## Context

The Specflow release system is **fundamentally broken** due to a GitHub Actions security limitation that was not understood when designing the current two-workflow release process.

### Current (Broken) Architecture

```
┌─────────────────────────┐    GITHUB_TOKEN    ┌─────────────────────────┐
│  release-on-merge.yml   │ ──── pushes ────▶  │      release.yml        │
│  (creates tag on merge) │       tag          │  (builds on tag push)   │
└─────────────────────────┘                    └─────────────────────────┘
         ✓ RUNS                                        ✗ NEVER RUNS
```

**The Fatal Flaw**: When a GitHub Actions workflow pushes a tag using `GITHUB_TOKEN`, GitHub **intentionally does NOT trigger** other workflows from that event. This is a documented security feature to prevent infinite workflow loops.

### Evidence of Failure

| Version | Tag Created | release.yml Ran | GitHub Release | Artifacts |
|---------|-------------|-----------------|----------------|-----------|
| v0.2.344 | Yes | Yes | Yes | Yes |
| v0.2.345 | Yes | **NO** | **NO** | **NO** |

The v0.2.345 release PR merged, the tag was created by `release-on-merge.yml`, but `release.yml` never triggered. Users see only source code, no installable packages.

### Root Cause Analysis

1. **PR #721** introduced the PR-based release workflow to fix a race condition
2. The design split release into two workflows: tag creation and release building
3. The split introduced a dependency on workflow-to-workflow triggering
4. GitHub Actions blocks this by design when using `GITHUB_TOKEN`
5. **Result**: Tag created, release never built

### Secondary Issues

1. **Branding inconsistency**: Release titles show "Spec Kit Templates" instead of "Specflow"
2. **Unnecessary complexity**: Two workflows when one would suffice
3. **Fragile handoff**: Any failure in the handoff leaves orphaned tags

## Decision

**Merge both workflows into a single unified `release.yml`** that handles the entire release process in one execution.

### New Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    release.yml (unified)                      │
│                                                              │
│  Trigger: pull_request closed + merged + release/v* branch   │
│                                                              │
│  Steps (single job, single execution):                       │
│  1. Validate branch format (release/vX.Y.Z)                  │
│  2. Extract version, verify source files                     │
│  3. Read .release-commit for pinned SHA                      │
│  4. CREATE TAG (on pinned commit)                            │
│  5. PUSH TAG                                                 │
│  6. Set up Python + uv                                       │
│  7. Build packages                                           │
│  8. Create release packages (all AI assistants)              │
│  9. Generate release notes                                   │
│  10. CREATE GITHUB RELEASE with all artifacts                │
│  11. Delete release branch                                   │
└──────────────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **Single Workflow**: No handoff between workflows = no GITHUB_TOKEN limitation
2. **Atomic Execution**: Tag + Release + Artifacts created together or not at all
3. **Pinned Commits**: Honor `.release-commit` file for race condition protection
4. **Consistent Branding**: All user-facing text uses "Specflow"
5. **Backward Compatibility**: Keep `workflow_dispatch` trigger for manual releases

### Files to Change

| File | Action | Purpose |
|------|--------|---------|
| `.github/workflows/release.yml` | Rewrite | Unified workflow |
| `.github/workflows/release-on-merge.yml` | Delete | No longer needed |
| `.github/workflows/scripts/create-github-release.sh` | Update | Fix branding to "Specflow" |
| `scripts/release.py` | Update | PR body references new workflow |

### Trigger Configuration

```yaml
on:
  pull_request:
    types: [closed]
    branches: [main]
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to release (e.g., v1.0.0)'
        required: false
        type: string
```

The workflow checks `github.event.pull_request.merged == true` and `startsWith(github.event.pull_request.head.ref, 'release/v')` before proceeding.

## Consequences

### Positive

- **Reliability**: No more orphaned tags without releases
- **Simplicity**: One workflow to understand and maintain
- **Atomicity**: Release either fully succeeds or fully fails
- **Debuggability**: Single workflow run to inspect on failure

### Negative

- **Longer workflow**: Single job runs for ~2-3 minutes instead of split execution
- **No parallel building**: Can't parallelize tag creation and package building (acceptable tradeoff)

### Neutral

- **Same release.py script**: No changes to developer workflow
- **Same PR process**: Create release branch, PR to main, merge

## Verification Plan

1. Merge implementation PR
2. Create test release v0.2.346 using `./scripts/release.py`
3. Verify after PR merge:
   - Tag v0.2.346 exists
   - GitHub Release v0.2.346 exists with title "Specflow - 0.2.346"
   - All 26 artifact zip files attached
   - Source archives attached

## References

- [GitHub Docs: Events that trigger workflows](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#triggering-a-workflow-from-a-workflow)
- [GitHub Community: GITHUB_TOKEN doesn't trigger workflows](https://github.community/t/github-actions-workflow-not-triggering-with-tag-push/17053)
- task-431: CRITICAL: Release system fundamentally broken
- PR #721: Original PR-based release workflow (introduced the bug)
