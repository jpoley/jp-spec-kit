---
id: task-296
title: Implement specify upgrade-tools command
status: Done
assignee: []
created_date: '2025-12-07 19:09'
updated_date: '2025-12-07 19:23'
labels:
  - backend
  - cli
  - feature
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add new command to upgrade globally installed CLI tools (jp-spec-kit, spec-kit, backlog.md) at their default per-user installation locations. Currently the version command shows upgrades available but `specify upgrade` only upgrades repo templates, not the actual tools.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 specify upgrade-tools upgrades jp-spec-kit via uv tool upgrade specify-cli
- [x] #2 specify upgrade-tools upgrades backlog.md via pnpm/npm add -g backlog-md@latest
- [x] #3 --component flag allows upgrading single component
- [x] #4 --dry-run shows what would be upgraded without making changes
- [x] #5 Version verification after upgrade confirms success
- [x] #6 Handles case where tool not installed (skip with warning)
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementation completed:
- New upgrade-tools command upgrades jp-spec-kit via uv tool upgrade
- Upgrades backlog-md via pnpm/npm add -g backlog-md@latest
- --component/-c flag allows single component upgrade
- --dry-run shows what would be upgraded
- Version verification after upgrade (shows before/after in table)
- Handles not installed case with appropriate message

Key functions added:
- _upgrade_jp_spec_kit(): Upgrades via uv tool
- _upgrade_backlog_md(): Upgrades via npm/pnpm
- _run_upgrade_tools(): Helper for command and dispatcher
- upgrade_tools(): CLI command

Files modified:
- src/specify_cli/__init__.py

Tests: 24 new tests in tests/test_upgrade_commands.py
<!-- SECTION:NOTES:END -->
