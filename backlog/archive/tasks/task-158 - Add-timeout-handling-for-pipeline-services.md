---
id: task-158
title: Add timeout handling for pipeline services
status: To Do
assignee:
  - '@pm-planner'
created_date: '2025-11-28'
labels:
  - implement
  - voice
  - hardening
  - phase6
dependencies:
  - task-144
priority: high
---

## Description

Add configurable timeout handling to STT, LLM, and TTS services in src/specify_cli/voice/services/*.py to prevent indefinite hangs. Reference: docs/research/pipecat-voice-integration-summary.md Latency Profile section

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 STT timeout defaults to 10 seconds, configurable via VoiceConfig
- [ ] #2 LLM timeout defaults to 30 seconds for complex queries, configurable
- [ ] #3 TTS timeout defaults to 15 seconds, configurable
- [ ] #4 Timeout triggers ServiceTimeoutError with service name and configured limit
- [ ] #5 User informed via voice "This is taking longer than expected" after 5s
<!-- AC:END -->
