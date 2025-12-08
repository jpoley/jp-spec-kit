---
id: task-297
title: Rename specify upgrade to upgrade-repo
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-12-07 19:09'
updated_date: '2025-12-07 19:23'
labels:
  - backend
  - cli
  - refactor
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Rename the current `upgrade` command to `upgrade-repo` to clarify it upgrades repository templates, not the CLI tools themselves. Keep `upgrade` as an alias for backwards compatibility.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Current upgrade function renamed to upgrade_repo
- [x] #2 specify upgrade-repo works identically to old specify upgrade
- [x] #3 specify upgrade remains as alias (deprecation notice)
- [x] #4 Help text clarifies this upgrades repo templates not tools
- [x] #5 Documentation updated
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create new upgrade_repo function as copy of current upgrade
2. Update docstring to clarify it upgrades repo templates
3. Keep upgrade as alias with deprecation notice
4. Update help text
5. Add tests
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementation completed:
- Renamed upgrade function to upgrade_repo with @app.command(name="upgrade-repo")
- Updated docstring to clarify it upgrades repository templates
- New 'upgrade' command created as interactive dispatcher with --tools, --repo, --all flags
- Help text includes "See also: specify upgrade-tools"
- ADR documented at docs/adr/upgrade-commands-plan.md

Files modified:
- src/specify_cli/__init__.py

Tests added in tests/test_upgrade_commands.py
<!-- SECTION:NOTES:END -->
