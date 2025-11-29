---
id: task-144
title: Implement Pipecat voice bot pipeline
status: Done
assignee:
  - '@pm-planner'
created_date: '2025-11-28'
updated_date: '2025-11-29 03:59'
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
Implemented VoiceBot pipeline orchestrator with:
- Pipeline assembly: STT → Context → LLM → TTS
- start()/stop() lifecycle methods
- SIGINT/SIGTERM signal handlers for graceful shutdown
- 5-second timeout with force cleanup fallback
- INFO-level logging for all pipeline stage transitions
- Transport cleanup with error handling
<!-- SECTION:NOTES:END -->
