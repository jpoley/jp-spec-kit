---
id: task-089
title: Create default jpspec_workflow.yml configuration
status: To Do
assignee: []
created_date: '2025-11-28 15:57'
labels:
  - architecture
  - configuration
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create the default workflow configuration file that maps /jpspec commands to task states and agents
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 jpspec_workflow.yml created in project root with all 6 phases (specify, research, plan, implement, validate, operate)
- [ ] #2 All default states defined: To Do, Specified, Researched, Planned, In Implementation, Validated, Deployed, Done
- [ ] #3 All /jpspec commands mapped with correct agents and input/output states
- [ ] #4 Agent assignments match current /jpspec command implementations
- [ ] #5 State transitions form a valid DAG with no cycles or unreachable states
- [ ] #6 Agent loop classification matches documented inner/outer loop agents
- [ ] #7 Configuration follows JSON schema and validates without errors
- [ ] #8 Configuration is documented with comments explaining each section
<!-- AC:END -->
