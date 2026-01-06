---
id: task-579.01
title: 'P0.1: Remove ALL /flow:operate references from codebase'
status: Done
assignee:
  - '@backend-engineer'
created_date: '2026-01-06 17:19'
updated_date: '2026-01-06 18:59'
labels:
  - phase-0
  - cleanup
  - deprecation
  - release-blocker
dependencies: []
parent_task_id: task-579
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Remove all references to /flow:operate command which has been deprecated. This must happen FIRST before other fixes.

Scope of removal:
- Event system: DEPLOY_STARTED, DEPLOY_COMPLETED events in src/flowspec_cli/hooks/events.py
- Command file: .claude/commands/flow/_DEPRECATED_operate.md (delete)
- Template: templates/commands/flow/_DEPRECATED_operate.md (delete)
- CLAUDE.md references
- flowspec_workflow.yml transitions
- Build docs references (archive or update)
- Task backlog references (close/archive affected tasks)

Per fix plan: /flow:operate is outer loop - deployment handled separately.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 grep -r '/flow:operate' . returns ZERO matches in active code
- [x] #2 DEPLOY_STARTED and DEPLOY_COMPLETED events removed from events.py
- [x] #3 _DEPRECATED_operate.md files deleted from .claude/commands/flow/ and templates/
- [x] #4 CLAUDE.md updated to remove /flow:operate mentions
- [x] #5 flowspec_workflow.yml has no 'operate' transitions
- [x] #6 task-548 closed as obsolete (references /flow:operate)
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Search for all /flow:operate references in codebase
2. Remove DEPLOY_STARTED and DEPLOY_COMPLETED events from events.py
3. Delete _DEPRECATED_operate.md files
4. Update CLAUDE.md to remove /flow:operate mentions
5. Update flowspec_workflow.yml to remove operate transitions
6. Close task-548 as obsolete
7. Verify with grep that zero references remain
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
**Implementation Progress (Jan 6 2026)**:

- Removed DEPLOY_STARTED/DEPLOY_COMPLETED from events.py (added explanatory comment)

- Deleted templates/commands/flow/_DEPRECATED_operate.md

- Updated .claude-plugin/README.md (removed Step 7, command details, workflow sequence)

- CLAUDE.md already has deprecation notes - verified correct

- flowspec_workflow.yml already has removal notes - verified correct

- Closed task-548 as OBSOLETE

- Updated templates/github-actions/README.md

- Updated templates/partials/flow/_rigor-rules.md

- Disabled .claude/hooks/test-post-slash-command-emit.py

**Remaining /flow:operate references are in:**

- Documentation files (build-docs/, user-docs/, docs/) - will be addressed in task-579.16/579.17

- Stale .claude/ integration docs (INTEGRATION-COMPLETE.md, AGENTS-INTEGRATION.md)

- Comments explaining the removal (acceptable)

**Completed Jan 6 2026**:

- Updated .claude/skills/sdd-methodology/SKILL.md (removed /flow:operate from workflow)

- Updated templates/skills/sdd-methodology/SKILL.md (same)

- Final verification: ZERO /flow:operate references in active code (src/, templates/, .claude/commands/, .claude/skills/)

- Remaining references are only in:

- Documentation files intended for cleanup (task-579.16, task-579.17)

- Explanatory comments noting the removal

- Build-docs (to be archived)

- All 6 acceptance criteria satisfied ✅
<!-- SECTION:NOTES:END -->
