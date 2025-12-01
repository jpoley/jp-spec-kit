---
id: task-162
title: Create unit tests for voice services
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
  - task-141
  - task-142
  - task-143
priority: high
---

## Description

Create tests/voice/test_services.py with comprehensive unit tests for STT, TTS, and LLM service wrappers using mocked API responses. Reference: docs/research/pipecat-voice-integration-summary.md Phase 3 Testing section

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Test file tests/voice/test_services.py exists with pytest fixtures for mocked services
- [ ] #2 DeepgramSTTService tests cover: initialization, transcription, error handling
- [ ] #3 CartesiaTTSService tests cover: initialization, synthesis, voice selection
- [ ] #4 OpenAILLMService tests cover: initialization, streaming, function calling
- [ ] #5 Combined test coverage for services/*.py achieves 80%+ line coverage
<!-- AC:END -->
