---
id: task-113
title: 'Update /jpspec:validate to use backlog.md CLI'
status: Done
assignee:
  - '@claude-agent'
created_date: '2025-11-28 16:56'
updated_date: '2025-11-29 05:17'
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
- [x] #1 Command discovers tasks in In Progress or Done status for validation
- [x] #2 All 4 validator agents receive shared backlog instructions from _backlog-instructions.md
- [x] #3 Quality Guardian validates ACs match test results
- [x] #4 Security Engineer validates security-related ACs
- [x] #5 Tech Writer creates/updates documentation tasks in backlog
- [x] #6 Release Manager verifies Definition of Done before marking tasks Done
- [x] #7 Test: Run /jpspec:validate and verify task validation workflow
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Verified /jpspec:validate backlog.md CLI integration.

Analysis:
- validate.md already had complete backlog integration from previous work
- All 4 validator agents (QA, Security, Tech Writer, Release Manager) have {{BACKLOG_INSTRUCTIONS}} markers
- Task discovery section finds In Progress/Done tasks
- Each agent has appropriate AC validation instructions

Changes:
- Enhanced test file with explicit AC mapping (task-113 acceptance criteria)
- Reorganized tests into 7 test classes: TestTaskDiscoveryAC1, TestSharedBacklogInstructionsAC2, TestQualityGuardianAC3, TestSecurityEngineerAC4, TestTechWriterAC5, TestReleaseManagerAC6, TestValidationWorkflowAC7
- All 45 tests pass verifying complete integration

Tests verify:
- AC#1: Task discovery for In Progress/Done status
- AC#2: All 4 agents receive _backlog-instructions.md content
- AC#3: QA validates ACs match test results
- AC#4: Security validates security-related ACs
- AC#5: Tech Writer creates documentation tasks
- AC#6: Release Manager verifies DoD before marking Done
- AC#7: Complete workflow structure and integration
<!-- SECTION:NOTES:END -->
