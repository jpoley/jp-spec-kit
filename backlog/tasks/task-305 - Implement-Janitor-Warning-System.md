---
id: task-305
title: Implement Janitor Warning System
status: To Do
assignee:
  - '@pm-planner'
created_date: '2025-12-07 20:38'
updated_date: '2025-12-07 20:55'
labels:
  - implement
  - hooks
  - ux
dependencies:
  - task-304
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a warning system that alerts when github-janitor hasn't been run after validation:
1. Track janitor execution in session state or temp file
2. Warn in session-start hook if pending janitor tasks exist
3. Display warning in backlog task list when janitor is overdue
4. Integrate with existing session-start.sh hook

Warning should be non-blocking but persistent until janitor runs.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Janitor state tracking implemented
- [ ] #2 session-start.sh updated with janitor warning
- [ ] #3 Warning displays pending cleanup count
- [ ] #4 Warning clears after janitor runs
- [ ] #5 Non-blocking behavior confirmed
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Implementation Plan

### Overview
Implement janitor warning system in session-start hook to alert when cleanup is pending.

### Tasks

1. **Modify session-start.sh Hook**
   - Location: .claude/hooks/session-start.sh
   - Add check for pending-cleanup.json (after line 92)
   - Parse pending branches count
   - Parse pending worktrees count
   - Add warning if total > 0
   - Suggest /jpspec:validate or github-janitor

2. **Create Pending Cleanup Reader**
   - Location: src/specify_cli/janitor/reader.py
   - Read pending-cleanup.json
   - Parse counts safely (handle missing/corrupted files)
   - Return structured cleanup status

3. **Add Warning Display Logic**
   - Integrate with existing warning system in session-start.sh
   - Use consistent format (⚠ symbol, yellow color)
   - Show counts of pending items
   - Non-blocking (warning only, not error)

4. **Integration Tests**
   - Location: .claude/hooks/test-session-start.sh
   - Test warning displays when cleanup pending
   - Test no warning when cleanup empty
   - Test handles missing state file gracefully
   - Test handles corrupted JSON gracefully

### Files to Create/Modify
- .claude/hooks/session-start.sh (MODIFY - add janitor warning)
- src/specify_cli/janitor/reader.py (NEW)
- .claude/hooks/test-session-start.sh (MODIFY - add janitor tests)

### Dependencies
- task-304 (requires janitor state files)

### Reference
- Platform design: docs/platform/push-rules-platform-design.md Section 1.3
- PRD Section 4.4 (Warning System)
- Existing hook: .claude/hooks/session-start.sh
<!-- SECTION:PLAN:END -->
