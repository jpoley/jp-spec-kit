---
id: task-304
title: 'Integrate Janitor into /jpspec:validate Workflow'
status: To Do
assignee:
  - '@pm-planner'
created_date: '2025-12-07 20:38'
updated_date: '2025-12-07 20:55'
labels:
  - implement
  - workflow
  - integration
dependencies:
  - task-303
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add a Phase 7 to /jpspec:validate that invokes the github-janitor agent after successful PR creation:
1. New phase after Phase 6 (PR Generation)
2. Runs github-janitor agent with current branch context
3. Reports cleanup actions taken
4. Sets flag indicating janitor has run

Also update jpspec_workflow.yml to include janitor in workflow configuration.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Phase 7 added to validate.md command template
- [ ] #2 github-janitor agent invoked after PR creation
- [ ] #3 Cleanup results reported to user
- [ ] #4 Janitor completion flag set for warning system
- [ ] #5 jpspec_workflow.yml updated with janitor step
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Implementation Plan

### Overview
Integrate github-janitor agent into /jpspec:validate workflow as Phase 7.

### Tasks

1. **Define github-janitor Agent**
   - Location: .claude/agents/github-janitor.md
   - Define agent capabilities (prune branches, clean worktrees)
   - Extend /jpspec:prune-branch patterns
   - Add PR status sync capability
   - Add branch naming validation
   - Generate cleanup report

2. **Update /jpspec:validate Command**
   - Location: .claude/commands/jpspec/validate.md
   - Add Phase 7: Janitor Cleanup
   - Invoke github-janitor after validation phases
   - Pass push-rules.md config to janitor
   - Capture cleanup report

3. **Create Janitor State Writer**
   - Location: src/specify_cli/janitor/state.py
   - Write pending-cleanup.json after janitor scan
   - Update janitor-last-run timestamp
   - Clear pending items after successful cleanup
   - Log cleanup actions to audit.log

4. **Integration Tests**
   - Location: tests/integration/test_validate_workflow.py
   - Test janitor runs after validation
   - Test state files updated correctly
   - Test cleanup report generated

### Files to Create/Modify
- .claude/agents/github-janitor.md (NEW)
- .claude/commands/jpspec/validate.md (MODIFY - add Phase 7)
- src/specify_cli/janitor/state.py (NEW)
- tests/integration/test_validate_workflow.py (NEW or MODIFY)

### Dependencies
- task-301 (requires push-rules.md config)

### Reference
- Platform design: docs/platform/push-rules-platform-design.md Section 2
- PRD Section 4.3 (github-janitor)
- Existing command: .claude/commands/jpspec/prune-branch.md
<!-- SECTION:PLAN:END -->
