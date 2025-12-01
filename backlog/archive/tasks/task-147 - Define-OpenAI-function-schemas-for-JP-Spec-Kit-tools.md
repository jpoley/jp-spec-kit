---
id: task-147
title: Define OpenAI function schemas for JP Spec Kit tools
status: To Do
assignee:
  - '@pm-planner'
created_date: '2025-11-28'
labels:
  - implement
  - voice
  - us2
  - tools
  - phase4
dependencies:
  - task-144
priority: high
---

## Description

Create src/specify_cli/voice/tools/schemas.py with OpenAI function calling schemas for all JP Spec Kit operations: run_specify_command, list_backlog_tasks, update_task_status, create_task, run_plan_command. Reference: docs/research/pipecat-voice-integration-summary.md Function Calling Integration section

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 TOOL_SCHEMAS list contains 5 tool definitions with name, description, parameters
- [ ] #2 Each tool has JSON schema parameters with required/optional fields defined
- [ ] #3 run_specify_command schema includes feature_description required parameter
- [ ] #4 list_backlog_tasks schema includes optional status enum filter parameter
- [ ] #5 Schemas validate against OpenAI function calling spec (type, properties, required)
<!-- AC:END -->
