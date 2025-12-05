---
id: task-281.01
title: Implement archive-tasks.sh script with flexible filtering
status: Done
assignee:
  - '@galway'
created_date: '2025-12-04 03:32'
updated_date: '2025-12-05 21:17'
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
## Completed via PR #553

https://github.com/jpoley/jp-spec-kit/pull/553

All 7 ACs verified. CI passed. Merged to main.
<!-- SECTION:NOTES:END -->
