---
id: task-163
title: Create unit tests for voice tools
status: To Do
assignee:
  - '@pm-planner'
created_date: '2025-11-28'
labels:
  - implement
  - voice
  - testing
  - phase7
dependencies:
  - task-148
  - task-149
  - task-150
  - task-151
priority: high
---

## Description

Create tests/voice/test_tools.py with unit tests for all voice tool implementations (specify_tools.py, backlog_tools.py) using mocked CLI commands. Reference: docs/research/pipecat-voice-integration-summary.md Phase 3 Testing section

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Test file tests/voice/test_tools.py exists with pytest fixtures for mocked CLI
- [ ] #2 run_specify_command tests cover: success path, missing params, CLI errors
- [ ] #3 list_backlog_tasks tests cover: all statuses, empty list, truncation
- [ ] #4 update_task_status tests cover: valid update, invalid task ID, invalid status
- [ ] #5 create_task tests cover: success, missing title, AC generation
<!-- AC:END -->
