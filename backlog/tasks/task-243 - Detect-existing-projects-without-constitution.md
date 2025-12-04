---
id: task-243
title: Detect existing projects without constitution
status: To Do
assignee:
  - '@kinsale'
created_date: '2025-12-03 02:38'
updated_date: '2025-12-04 17:07'
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
- [ ] #1 Detect existing project (has .git, package.json, pyproject.toml, etc.)
- [ ] #2 Check for missing memory/constitution.md
- [ ] #3 Prompt user: 'No constitution found. Select tier: light/medium/heavy'
- [ ] #4 Trigger LLM constitution customization flow after tier selection
- [ ] #5 Works with both specify init --here and specify upgrade
<!-- AC:END -->
