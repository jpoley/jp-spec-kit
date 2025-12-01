---
id: task-156
title: Add conversation state tracking
status: To Do
assignee:
  - '@pm-planner'
created_date: '2025-11-28'
labels:
  - implement
  - voice
  - us3
  - state
  - phase5
dependencies:
  - task-153
priority: high
---

## Description

Create src/specify_cli/voice/state.py with ConversationState class that tracks current conversation mode (casual, requirements_gathering, task_management), gathered requirements, and session metadata. Reference: docs/research/pipecat-voice-integration-summary.md Session Management

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 ConversationState tracks current_mode enum (CASUAL, REQUIREMENTS, TASK_MGMT)
- [ ] #2 Stores partial requirements as they are gathered across turns
- [ ] #3 Tracks session start time and turn count for analytics
- [ ] #4 State serializable to JSON for optional persistence
- [ ] #5 State resets cleanly when user says "start over" or "new conversation"
<!-- AC:END -->
