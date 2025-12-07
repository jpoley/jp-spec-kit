---
id: task-302
title: Implement Rebase-vs-Main Enforcement
status: Done
assignee:
  - '@claude'
created_date: '2025-12-07 20:38'
updated_date: '2025-12-07 21:35'
labels:
  - implement
  - git-workflow
  - enforcement
dependencies:
  - task-302
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create enforcement mechanism that ensures branches are always rebased vs main:
1. Detect merge commits in branch history
2. Block PRs with merge commits
3. Provide guidance on how to rebase
4. Integration with pre-push hook

Should work with git worktrees for parallel development.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Merge commit detection implemented
- [x] #2 Clear error message when merge commits found
- [x] #3 Rebase instructions provided in error output
- [x] #4 Works with git worktrees
- [x] #5 CI integration documented
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Implementation Plan

### Phase 1: Rebase Detection Module
1. Create `src/specify_cli/hooks/rebase_checker.py`
2. Implement `detect_merge_commits(base_branch: str) -> list[str]`
3. Use `git log --merges base_branch..HEAD` for detection
4. Handle worktree-specific git context

### Phase 2: Pre-Push Hook Integration
1. Add rebase check as Gate 2 in pre-push-validate.sh
2. Call Python rebase checker module
3. Format clear error output with affected commits

### Phase 3: Error Messages and Remediation
1. Display merge commit SHAs and messages
2. Provide `git rebase -i main` command
3. Add link to documentation for complex rebases

### Phase 4: Worktree Support
1. Test with git worktrees for parallel development
2. Handle detached HEAD state
3. Ensure correct base branch detection in worktrees

### Phase 5: Testing
1. Create `tests/unit/test_rebase_checker.py`
2. Test with clean history, merge commits, worktrees
3. Create integration test in `.claude/hooks/test-pre-push-validate.sh`

### References
- ADR-012: docs/adr/ADR-012-push-rules-enforcement-architecture.md
- Platform Design: docs/platform/push-rules-platform-design.md
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implementation Summary

### Deliverables

| File | Description |
|------|-------------|
| `src/specify_cli/hooks/rebase_checker.py` | Rebase detection module with merge commit finder |
| `src/specify_cli/hooks/__init__.py` | Updated exports |
| `tests/test_rebase_checker.py` | 41 comprehensive unit tests |
| `docs/guides/push-rules-configuration.md` | Added CI integration section |

### Key Functions

- `find_merge_commits(base_branch, current_branch, cwd)` - Find all merge commits since divergence
- `is_branch_rebased(base_branch, current_branch, cwd)` - Quick check if branch is rebased
- `check_rebase_status(base_branch, current_branch, cwd)` - Full status with remediation
- `format_rebase_error(result)` - Human-readable error formatting

### Worktree Support

All functions accept optional `cwd` parameter for git worktree support.

### Test Results

- 41 tests covering all scenarios
- Edge cases: detached HEAD, remote tracking branches, timeout handling
- 100% pass rate
<!-- SECTION:NOTES:END -->
