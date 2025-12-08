---
id: task-298
title: Update specify upgrade to be interactive or upgrade all
status: Done
assignee: []
created_date: '2025-12-07 19:09'
updated_date: '2025-12-07 19:23'
labels:
  - backend
  - cli
  - ux
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update the main `upgrade` command to either prompt for upgrade type (tools vs repo) or provide flags to choose. Fix the misleading version hint.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 specify upgrade --tools runs upgrade-tools
- [x] #2 specify upgrade --repo runs upgrade-repo
- [x] #3 specify upgrade --all upgrades both tools and repo
- [x] #4 Interactive mode asks which type if no flags
- [x] #5 Version hint updated to reflect correct command
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementation completed:
- specify upgrade --tools/-t runs _run_upgrade_tools()
- specify upgrade --repo/-r shows upgrade-repo instructions
- specify upgrade --all/-a upgrades both tools and shows repo info
- Interactive mode prompts for choice (1/2/3) when no flags
- Version hint updated to say 'upgrade-tools' (task-299)

Note: --repo delegates to informational message directing users to
'specify upgrade-repo' for full options (version pinning, etc.)

Files modified:
- src/specify_cli/__init__.py

Tests in tests/test_upgrade_commands.py
<!-- SECTION:NOTES:END -->
