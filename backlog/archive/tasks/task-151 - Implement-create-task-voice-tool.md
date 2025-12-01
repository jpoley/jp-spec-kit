---
id: task-151
title: Implement create_task voice tool
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

Add create_task function to src/specify_cli/voice/tools/backlog_tools.py that creates new backlog tasks from voice commands. Reference: docs/research/pipecat-voice-integration-summary.md Integration Strategy Use Cases

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Function accepts title, description, and optional priority parameters
- [ ] #2 Generates at least one acceptance criterion from description
- [ ] #3 Invokes backlog task create command with --ac flag
- [ ] #4 Returns confirmation "Created task N: title" with task ID on success
- [ ] #5 Returns error message with reason if task creation fails
<!-- AC:END -->
