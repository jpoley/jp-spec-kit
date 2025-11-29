---
id: task-142
title: Create TTS service wrapper using Cartesia
status: Done
assignee:
  - '@pm-planner'
created_date: '2025-11-28'
updated_date: '2025-11-29 03:59'
labels:
  - implement
  - voice
  - us1
  - tts
  - phase3
dependencies:
  - task-140
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement src/specify_cli/voice/services/tts.py with CartesiaTTSService class wrapping pipecat-ai Cartesia integration for low-latency speech synthesis. Reference: docs/research/pipecat-voice-integration-summary.md TTS Provider section
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 CartesiaTTSService class extends pipecat CartesiaTTSService with custom configuration
- [x] #2 Supports WebSocket streaming for real-time audio output
- [x] #3 API key loaded from CARTESIA_API_KEY environment variable
- [x] #4 Voice ID and output format (pcm_16000) configurable via VoiceConfig
- [x] #5 Synthesis errors raise TTSServiceError with provider error details
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented CartesiaTTSService wrapper with:
- WebSocket streaming for real-time audio output (via pipecat)
- Proper model (sonic-3), sample_rate, and encoding parameters
- API key validation with provider context errors
- from_config() factory method with sample rate parsing
- Custom TTSServiceError with original_error tracking
<!-- SECTION:NOTES:END -->
