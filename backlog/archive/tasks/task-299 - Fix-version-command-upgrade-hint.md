---
id: task-299
title: Fix version command upgrade hint
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-12-07 19:09'
updated_date: '2025-12-07 19:23'
labels:
  - backend
  - cli
  - bugfix
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The version command shows upgrade hint 'Run specify upgrade to update components' but that command upgrades repo templates, not the CLI tools shown in the version table. Fix to point to correct command.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Version hint says 'specify upgrade-tools' for tool upgrades
- [x] #2 Clear distinction between tool upgrades and repo upgrades in output
- [x] #3 Help text updated for clarity
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Find the version hint text in show_version_info function
2. Update hint to say 'specify upgrade-tools' for CLI tool upgrades
3. Add clarifying text distinguishing tool vs repo upgrades
4. Update help text for version command
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementation completed:
- Updated version hint from 'specify upgrade' to 'specify upgrade-tools' in show_version_info()
- Clear distinction now exists between tool upgrades and repo upgrades
- Help text updated in all upgrade commands

Files modified:
- src/specify_cli/__init__.py (line ~928)

Tests added in tests/test_upgrade_commands.py
<!-- SECTION:NOTES:END -->
