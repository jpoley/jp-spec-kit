---
id: task-272
title: Migrate speckit commands to subdirectory
status: Done
assignee:
  - '@template-migrator'
created_date: '2025-12-03 14:01'
updated_date: '2025-12-03 14:14'
labels:
  - architecture
  - migration
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Move speckit template commands into templates/commands/speckit/ subdirectory for consistency
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create templates/commands/speckit/ directory
- [ ] #2 Move all 8 speckit command files into subdirectory (implement, analyze, checklist, clarify, constitution, plan, specify, tasks)
- [ ] #3 Verify no flat files remain in templates/commands/
- [ ] #4 Update dogfood command to handle speckit subdirectory
- [ ] #5 Test dogfood creates correct speckit symlinks
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Moved speckit commands into subdirectory
<!-- SECTION:NOTES:END -->
