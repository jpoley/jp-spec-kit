---
id: task-272
title: Migrate speckit commands to subdirectory
status: Done
assignee:
  - '@galway'
created_date: '2025-12-03 14:01'
updated_date: '2025-12-05 01:42'
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
REOPENED: Task was marked Done but speckit commands are NOT in subdirectory.

Current state:
- templates/commands/ has flat speckit files (analyze.md, checklist.md, etc.)
- .claude/commands/speckit/ symlinks point to flat templates/commands/
- Task AC#2 requires: "Move all 8 speckit command files into subdirectory"
- AC#3 requires: "Verify no flat files remain in templates/commands/"

The implementation did NOT move speckit to templates/commands/speckit/.
Need to complete migration to match jpspec subdirectory pattern.

Verified complete - speckit/ subdirectory exists with all symlinks pointing correctly
<!-- SECTION:NOTES:END -->
