---
id: task-365
title: 'CI/CD: Role-Based Validation Workflows'
status: To Do
assignee: []
created_date: '2025-12-09 15:14'
updated_date: '2025-12-09 15:48'
labels:
  - infrastructure
  - cicd
  - phase-4
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add CI validation for role-based command structure. DEPENDS ON: task-367 (command files), task-363 (sync script).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Role-based CI workflow detects changed role artifacts
- [ ] #2 PM validation job checks PRD structure
- [ ] #3 Dev validation job runs tests and ADR checks
- [ ] #4 Sec validation job runs security scanning
- [ ] #5 QA validation job checks test coverage and docs
- [ ] #6 Team role validation prevents .vscode/settings.json commits in team mode
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
DEPENDS ON: task-367, task-363

1. Add workflow to validate specflow_workflow.yml schema
2. Validate all role commands exist in correct directories
3. Check agent-to-role mappings are valid
4. Verify backwards-compatible aliases work
5. Run sync-copilot-agents.sh --validate in CI
6. Check for drift between commands and schema
<!-- SECTION:PLAN:END -->
