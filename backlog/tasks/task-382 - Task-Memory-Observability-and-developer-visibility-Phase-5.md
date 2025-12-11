---
id: task-382
title: 'Task Memory: Observability and developer visibility (Phase 5)'
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-12-09 15:57'
updated_date: '2025-12-11 08:20'
labels:
  - infrastructure
  - cli
  - observability
  - phase-5
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Provide comprehensive visibility into Task Memory: stats, size, token count, warnings, compaction
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 backlog memory stats shows size and token estimation
- [x] #2 backlog memory list displays all active memories
- [x] #3 Size warnings for memories > 25KB
- [x] #4 backlog memory compact reduces redundant content
- [x] #5 Token usage displayed in session start
- [x] #6 CI reports memory size in PR checks
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented all task memory observability features:

## AC#1: Stats command for specific tasks
- Enhanced `specify memory stats` to accept optional task_id argument
- Shows size (KB and bytes), token estimate (~chars/4), line count
- Displays modified timestamp and file path
- Warning when memory > 25KB with suggestion to compact

## AC#2: List command with token estimates
- Added Tokens column to memory list table
- Calculates token estimates for all memories
- Shows warnings (⚠) for files over 25KB
- Plain output includes tokens and warning marker

## AC#3: Size warnings
- Stats command warns at 25KB threshold
- List command shows warning icon and count
- Session-start hook displays warning for oversized memories
- Configurable threshold in workflow

## AC#4: Compact command
- `specify memory compact <task-id>` with dry-run default
- Strategies: remove duplicate lines, collapse blanks, trim whitespace
- Shows original/compacted size and reduction percentage
- Creates backup before compaction with --execute
- Returns compacted content via helper function

## AC#5: Session start token display
- Updated .claude/hooks/session-start.sh
- Shows token estimate and size for each active task memory
- Warning indicator (⚠) for memories > 25KB
- Example: "✓ Task memory: ~140 tokens (0.5 KB)"

## AC#6: CI workflow
- Created .github/workflows/memory-size-check.yml
- Runs on PR and push to main when memory files change
- Checks all memories against 25KB warning / 100KB error thresholds
- Shows detailed report with tokens and sizes
- Posts PR comment on failure
- Generates GitHub step summary

## Implementation Details
- Used typer for CLI with rich formatting
- Token estimation: 1 token ≈ 4 characters (OpenAI guideline)
- All commands support --json for scripting
- Helper functions: _show_task_stats, _show_overall_stats, _compact_content
- Cross-platform file size checks in CI workflow

## Testing
- Tested all commands manually
- All existing tests pass (316 passed)
- No ruff linting errors
<!-- SECTION:NOTES:END -->
