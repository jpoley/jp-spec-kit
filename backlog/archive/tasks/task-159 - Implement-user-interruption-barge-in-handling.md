---
id: task-159
title: Implement user interruption (barge-in) handling
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

Add barge-in detection to src/specify_cli/voice/bot.py that stops TTS playback when user starts speaking, enabling natural conversational interruptions. Reference: docs/research/pipecat-voice-integration-summary.md Phase 3 Interruption Handling

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Voice activity detection (VAD) signals interrupt when user speaks during TTS
- [ ] #2 TTS playback stops within 200ms of interrupt detection
- [ ] #3 Pipeline transitions to listening mode after interrupt
- [ ] #4 Interrupted response context preserved for potential continuation
- [ ] #5 Interrupt sensitivity configurable (low/medium/high) via VoiceConfig
<!-- AC:END -->
