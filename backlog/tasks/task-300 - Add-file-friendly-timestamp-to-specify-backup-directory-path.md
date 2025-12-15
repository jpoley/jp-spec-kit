---
id: task-300
title: Add file-friendly timestamp to specify-backup directory path
status: Done
assignee:
  - '@adare'
created_date: '2025-12-07 22:28'
updated_date: '2025-12-15 02:17'
labels:
  - backend
  - implement
  - size-s
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The `.specify-backup/` directory created during `specify upgrade-tools` command overwrites previous backups without preserving history. Add a file-friendly timestamp to the backup directory name to preserve multiple backup versions.

Current behavior:
- Backup created at `.specify-backup/`
- Each upgrade overwrites previous backup

Desired behavior:
- Backup created at `.specify-backup-YYYYMMDD-HHMMSS/`
- Multiple backups preserved for rollback options

Files to modify:
- `src/specify_cli/__init__.py` (line ~3675)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Backup directory includes ISO 8601-like timestamp (YYYYMMDD-HHMMSS format)
- [x] #2 Timestamp is file-system safe (no colons or special characters)
- [x] #3 Multiple consecutive upgrades create separate backup directories
- [x] #4 Backup directory name displayed correctly in console output
- [x] #5 Existing tests pass and new tests cover timestamp format
- [x] #6 Documentation updated to reflect new backup naming
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
PR created: https://github.com/jpoley/flowspec/pull/600

## Completed

PR #600 merged. Backup directories now include timestamp in YYYYMMDD-HHMMSS format.
<!-- SECTION:NOTES:END -->
