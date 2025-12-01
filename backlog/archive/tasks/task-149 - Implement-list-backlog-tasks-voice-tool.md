---
id: task-149
title: Implement list_backlog_tasks voice tool
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

Create src/specify_cli/voice/tools/backlog_tools.py with list_backlog_tasks function that retrieves tasks from backlog CLI and formats them for voice response. Reference: docs/research/pipecat-voice-integration-summary.md Sample Voice Interaction Flow 2

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Function accepts optional status filter parameter ("To Do", "In Progress", "Done")
- [ ] #2 Invokes backlog CLI with --plain flag for machine-readable output
- [ ] #3 Returns formatted list suitable for voice: "Task N: title, status"
- [ ] #4 Returns "No tasks found" message when list is empty
- [ ] #5 Limits response to first 5 tasks with "and N more" suffix for voice brevity
<!-- AC:END -->
