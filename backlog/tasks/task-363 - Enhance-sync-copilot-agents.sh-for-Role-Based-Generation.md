---
id: task-363
title: 'Enhance: sync-copilot-agents.sh for Role-Based Generation'
status: To Do
assignee: []
created_date: '2025-12-09 15:14'
updated_date: '2025-12-09 15:48'
labels:
  - infrastructure
  - automation
  - phase-3
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Modify sync-copilot-agents.sh to generate role-filtered agents in .github/agents/. DEPENDS ON: task-364 (schema), task-367 (command files).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Role configuration reading from jpspec_workflow.yml implemented
- [ ] #2 get_role_metadata() function extracts agent role mappings
- [ ] #3 generate_frontmatter() enhanced with role and priority fields
- [ ] #4 Role-specific agent generation (--role flag) supported
- [ ] #5 VS Code settings generation (generate_vscode_settings) implemented

- [ ] #6 Role metadata added to agent frontmatter
- [ ] #7 Role-specific handoff chains generated
- [ ] #8 Agent files named {role}-{command}.agent.md
- [ ] #9 --role flag filters generation
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
DEPENDS ON: task-364, task-367

1. Read role definitions from specflow_workflow.yml
2. Add role metadata to agent frontmatter (role:, priority_for_roles:)
3. Generate role-specific handoff chains
4. Filter agents based on primary role selection
5. Update agent naming: {role}-{command}.agent.md
6. Add --role flag to generate for specific role only
<!-- SECTION:PLAN:END -->
