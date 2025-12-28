---
id: task-381
title: 'Task Memory: Git synchronization and conflict resolution (Phase 4)'
status: Done
assignee:
  - '@adare'
created_date: '2025-12-09 15:56'
updated_date: '2025-12-15 01:49'
labels:
  - infrastructure
  - git
  - security
  - phase-4
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Enable cross-machine Task Memory sync via Git with union merge strategy and secret detection
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 .gitattributes configured for union merge on memory files
- [x] #2 Pre-commit hook scans Task Memory for secrets
- [x] #3 backlog memory diff command shows changes between commits
- [x] #4 Conflict resolution documented for concurrent edits
- [x] #5 E2E tests for multi-machine sync scenarios
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented Task Memory Git synchronization and conflict resolution:

**AC#1 - .gitattributes union merge**:
- Added union merge configuration for backlog/memory/*.md files
- Auto-resolves concurrent append conflicts without manual intervention

**AC#2 - Pre-commit secret detection**:
- Created .backlog/hooks/pre-commit-secrets.sh script
- Scans staged Task Memory files for potential secrets (API keys, passwords, tokens)
- Blocks commits containing suspicious patterns
- Installed Git pre-commit hook to invoke the script

**AC#3 - backlog memory diff command**:
- Added diff command to memory CLI (src/specify_cli/memory/cli.py)
- Shows unstaged changes: backlog memory diff <task-id>
- Shows staged changes: backlog memory diff <task-id> --cached
- Compare with commits: backlog memory diff <task-id> --commit HEAD~1
- Show changes since date: backlog memory diff <task-id> --since "1 week ago"

**AC#4 - Conflict resolution documentation**:
- Created comprehensive guide: docs/guides/task-memory-conflicts.md
- Documents union merge behavior and why conflicts are rare (<5%)
- Provides manual resolution strategies for edge cases
- Includes troubleshooting section and best practices

**AC#5 - E2E multi-machine sync tests**:
- Enhanced tests/e2e/test_memory_sync_e2e.py with:
  - TestUnionMergeDriver: 2 tests for concurrent append scenarios
  - TestSecretDetection: 2 tests for pre-commit hook behavior
  - TestMemoryDiff: 3 tests for diff command variations
- All tests pass successfully
- Fixed git_pull helper to use --no-rebase for divergent branches

**Architecture alignment**: Follows ADR-004 design:
- Git-based sync with standard push/pull
- Markdown format for line-based diffs
- Append-mostly structure minimizes conflicts
- Union merge driver for automatic resolution

**Testing**: All new E2E tests pass (7 tests added)
**Linting**: Ruff checks pass, no unused imports/variables
<!-- SECTION:NOTES:END -->
