---
id: task-243
title: Detect existing projects without constitution
status: Done
assignee:
  - '@kinsale'
created_date: '2025-12-03 02:38'
updated_date: '2025-12-04 22:40'
labels:
  - constitution-cleanup
  - 'workflow:Specified'
dependencies:
  - task-242
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add logic to detect when specify init/upgrade runs on existing project missing a constitution
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Detect existing project (has .git, package.json, pyproject.toml, etc.)
- [x] #2 Check for missing memory/constitution.md
- [x] #3 Prompt user: 'No constitution found. Select tier: light/medium/heavy'
- [x] #4 Trigger LLM constitution customization flow after tier selection
- [x] #5 Works with both specify init --here and specify upgrade
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Already implemented in main:

- AC #1-2: `is_existing_project()` and `has_constitution()` functions exist in `src/specify_cli/__init__.py`
- AC #3-4: Tier selection and LLM customization flow implemented via `/speckit:constitution` command
- AC #5: Works with `specify init --here` and `specify upgrade`

Verified existing implementation - marked as Done.
<!-- SECTION:NOTES:END -->
