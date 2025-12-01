---
id: task-164
title: Create integration test for voice pipeline
status: To Do
assignee:
  - '@pm-planner'
created_date: '2025-11-28'
labels:
  - implement
  - voice
  - testing
  - integration
  - phase7
dependencies:
  - task-162
  - task-163
priority: high
---

## Description

Create tests/voice/test_integration.py with end-to-end integration test that verifies the complete voice pipeline from audio input to audio output using mock audio frames. Reference: docs/research/pipecat-voice-integration-summary.md Success Metrics section

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Integration test creates VoiceBot with mocked transport (no real WebRTC)
- [ ] #2 Test sends mock AudioFrame and receives TranscriptionFrame
- [ ] #3 Test verifies LLM receives transcription and returns response
- [ ] #4 Test verifies TTS receives LLM response and returns audio
- [ ] #5 End-to-end pipeline test completes in under 5 seconds with mocked services
<!-- AC:END -->
