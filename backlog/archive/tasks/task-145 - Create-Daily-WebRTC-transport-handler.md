---
id: task-145
title: Create Daily WebRTC transport handler
status: To Do
assignee:
  - '@pm-planner'
created_date: '2025-11-28'
labels:
  - implement
  - voice
  - us1
  - transport
  - phase3
dependencies:
  - task-140
priority: high
---

## Description

Create src/specify_cli/voice/transport.py with DailyTransport class wrapping pipecat-ai Daily WebRTC integration for real-time audio streaming. Reference: docs/research/pipecat-voice-integration-summary.md Transport Options section

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 DailyTransport class creates WebRTC room connection using Daily API
- [ ] #2 API key loaded from DAILY_API_KEY environment variable
- [ ] #3 Supports both creating new rooms and joining existing room URLs
- [ ] #4 Audio quality configured for 16kHz sample rate matching STT/TTS requirements
- [ ] #5 Connection errors raise TransportError with room URL and error details
<!-- AC:END -->
