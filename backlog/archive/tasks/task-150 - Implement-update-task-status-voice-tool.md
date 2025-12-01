---
id: task-150
title: Implement update_task_status voice tool
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
  - task-147
priority: high
---

## Description

Add update_task_status function to src/specify_cli/voice/tools/backlog_tools.py that changes task status via backlog CLI from voice commands like "mark task 15 as done". Reference: docs/research/pipecat-voice-integration-summary.md Sample Voice Interaction Flow 2

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Function accepts task_id and status parameters from LLM function call
- [ ] #2 Validates status is one of: "To Do", "In Progress", "Done"
- [ ] #3 Invokes backlog task edit command with -s flag
- [ ] #4 Returns confirmation message "Task N marked as status" on success
- [ ] #5 Returns error message if task_id not found or update fails
<!-- AC:END -->
