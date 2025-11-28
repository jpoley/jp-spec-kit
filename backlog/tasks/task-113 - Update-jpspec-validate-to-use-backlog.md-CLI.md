---
id: task-113
title: 'Update /jpspec:validate to use backlog.md CLI'
status: Done
assignee: []
created_date: '2025-11-28 16:56'
updated_date: '2025-11-28 20:21'
labels:
  - jpspec
  - backlog-integration
  - validate
  - P1
dependencies:
  - task-107
  - task-108
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Modify the validate.md command to integrate backlog.md task management. QA, Security, Tech Writer, and Release Manager agents must validate against backlog task ACs and update completion status.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Command discovers tasks in In Progress or Done status for validation
- [ ] #2 All 4 validator agents receive shared backlog instructions from _backlog-instructions.md
- [ ] #3 Quality Guardian validates ACs match test results
- [ ] #4 Security Engineer validates security-related ACs
- [ ] #5 Tech Writer creates/updates documentation tasks in backlog
- [ ] #6 Release Manager verifies Definition of Done before marking tasks Done
- [x] #7 Test: Run /jpspec:validate and verify task validation workflow
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Updated /jpspec:validate command to integrate with backlog.md CLI for task validation workflows.

Key Changes:
- Added backlog task discovery section (commands to find In Progress/Done tasks)
- Integrated {{BACKLOG_INSTRUCTIONS}} template markers in all 4 validator agent contexts:
  * Quality Guardian: AC validation requirements added
  * Security Engineer: Security AC validation requirements added
  * Technical Writer: Task creation instructions for documentation work
  * Release Manager: Definition of Done verification workflow
- Added "Backlog Context" sections to each agent prompt
- Created comprehensive test suite (tests/test_jpspec_validate_backlog.py) with 31 tests covering:
  * Command structure validation
  * Each agent backlog integration
  * Workflow ordering
  * Documentation quality

Implementation follows the pattern established in /jpspec:specify and /jpspec:plan commands.

Note: The {{BACKLOG_INSTRUCTIONS}} template marker must be replaced with actual content from _backlog-instructions.md when executing the command.
<!-- SECTION:NOTES:END -->
