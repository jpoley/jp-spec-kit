---
id: task-281.01
title: Implement archive-tasks.sh script with flexible filtering
status: Done
assignee:
  - '@galway'
created_date: '2025-12-04 03:32'
updated_date: '2025-12-05 19:48'
labels:
  - backend
  - infrastructure
  - task-management
dependencies: []
parent_task_id: task-281
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create bash script to archive backlog tasks with --all, --done-by, and --dry-run flags. Integrate with backlog CLI for atomic archiving operations.

**Script Location**: `scripts/bash/archive-tasks.sh`

**Filtering Modes**:
- Default: Archive Done tasks only
- `--all`: Archive all tasks regardless of status
- `--done-by YYYY-MM-DD`: Archive tasks completed by specific date
- `--dry-run`: Preview without making changes

**Implementation Notes**:
- Follow existing flush-backlog.sh pattern for consistency
- Use backlog CLI for atomic task archiving
- Support TRIGGER_SOURCE environment variable for audit trails
- Output human-readable logs to stdout/stderr

**Exit Codes**:
- 0: Success (tasks archived)
- 1: Validation error (CLI missing, invalid args)
- 2: No tasks to archive (informational)
- 3: Partial failure (some tasks failed)

**References**:
- Existing script: `scripts/bash/flush-backlog.sh`
- Platform design: `docs/platform/archive-tasks-integration.md`
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Script supports --all flag to archive all tasks
- [x] #2 Script supports --done-by YYYY-MM-DD flag to archive by date
- [x] #3 Script supports --dry-run flag for preview
- [x] #4 Script has proper exit codes (0=success, 1=error, 2=no tasks, 3=partial)
- [x] #5 Script outputs human-readable logs to stdout/stderr
- [x] #6 Script passes shellcheck linting
- [x] #7 Script has --help flag with usage documentation
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implementation Complete

The `archive-tasks.sh` script was implemented and is already on main.

### Script Location
`scripts/bash/archive-tasks.sh`

### Features Verified
- `--all` flag: Archives ALL tasks regardless of status (135 tasks in current backlog)
- `--done-by YYYY-MM-DD` flag: Archives Done tasks updated on or before specified date
- `--dry-run` flag: Preview mode showing what would be archived without changes
- `--help` flag: Comprehensive usage documentation

### Exit Codes
- 0: Success (tasks archived)
- 1: Validation error (invalid args, missing CLI, invalid date)
- 2: No tasks to archive (informational)
- 3: Partial failure (some tasks failed)

### Quality Checks
- Shellcheck: PASSED (no warnings or errors)
- Date validation: Works for both GNU and BSD date formats
- Mutual exclusivity: `--all` and `--done-by` properly reject when combined

### Test Results
- `--dry-run`: Found 88 Done tasks
- `--all --dry-run`: Found 135 total tasks  
- `--done-by 2025-12-01 --dry-run`: Found 6 tasks matching date filter
- Error handling: All error cases return exit code 1 with clear messages

### Integration Points
- Works with backlog.md CLI for atomic archiving
- Supports TRIGGER_SOURCE env var for audit trails
- Follows same pattern as existing `flush-backlog.sh` script

No PR needed - implementation was completed via GitHub UI edits and merged to main.
<!-- SECTION:NOTES:END -->
