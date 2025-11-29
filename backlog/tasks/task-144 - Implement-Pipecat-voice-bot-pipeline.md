---
id: task-144
title: Implement Pipecat voice bot pipeline
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-11-28'
updated_date: '2025-11-29 00:43'
labels:
  - implement
  - voice
  - us1
  - core
  - phase3
dependencies:
  - task-141
  - task-142
  - task-143
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create src/specify_cli/voice/bot.py with VoiceBot class that assembles the Pipecat pipeline: Transport → STT → Context Aggregator → LLM → TTS → Transport. Implement pipeline lifecycle management (start, stop, cleanup). Reference: docs/research/pipecat-voice-integration-summary.md Pipeline Architecture section
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 VoiceBot class creates Pipecat pipeline with STT, LLM, TTS processors connected
- [x] #2 Pipeline starts with await bot.start() and stops cleanly with await bot.stop()
- [x] #3 SIGINT and SIGTERM signals trigger graceful shutdown within 5 seconds
- [x] #4 All resources (WebRTC connections, API sessions) properly cleaned up on stop
- [x] #5 Bot logs pipeline stage transitions at INFO level for debugging
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementation complete for VoiceBot pipeline:

IMPLEMENTED:
- src/specify_cli/voice/bot.py: VoiceBot class with complete pipeline assembly
- tests/voice/test_bot.py: 18 comprehensive unit tests (100% passing)

KEY FEATURES:
- Pipeline assembly: Transport → STT → LLM → TTS → Transport
- Lifecycle management: start(), stop() with async support
- Signal handling: SIGINT/SIGTERM with graceful shutdown (<5s timeout)
- Resource cleanup: All API connections properly closed
- Logging: INFO-level logs for all pipeline stage transitions

ARCHITECTURE:
- Uses Pipecat Pipeline, PipelineTask, PipelineRunner
- OpenAILLMContext for conversation state management
- Signal handlers registered during __init__
- Graceful shutdown with 5-second timeout, force cleanup fallback

TESTING:
- 18 unit tests covering initialization, lifecycle, signals, logging
- All tests pass with mocked services
- Code formatted with ruff (0 linting errors)
- All 91 voice module tests passing

ACCEPTANCE CRITERIA MET:
✓ AC1: VoiceBot creates pipeline with STT, LLM, TTS processors
✓ AC2: Pipeline starts/stops with await bot.start() / bot.stop()
✓ AC3: SIGINT/SIGTERM trigger graceful shutdown within 5 seconds
✓ AC4: All resources (WebRTC, API sessions) properly cleaned up
✓ AC5: Bot logs pipeline stage transitions at INFO level
<!-- SECTION:NOTES:END -->
