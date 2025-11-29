---
id: task-142
title: Create TTS service wrapper using Cartesia
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-11-28'
updated_date: '2025-11-29 00:34'
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
Implementation complete with comprehensive test coverage:

**Files Created:**
- src/specify_cli/voice/services/tts.py - CartesiaTTSService wrapper with error handling
- tests/voice/test_tts.py - 16 comprehensive unit and integration tests

**Key Features:**
1. CartesiaTTSService extends pipecat-ai CartesiaTTSService with custom configuration
2. WebSocket streaming inherited from pipecat for real-time audio output
3. API key loaded from CARTESIA_API_KEY environment variable
4. Voice ID and output format (pcm_16000) fully configurable via VoiceConfig
5. TTSServiceError exception class wraps provider errors with detailed context

**Implementation Details:**
- Used non-deprecated pipecat import: pipecat.services.cartesia.tts
- Maps output_format to model_id parameter for pipecat compatibility
- from_config() factory method validates provider and creates service from VoiceConfig
- Properties expose voice_id and output_format for introspection
- Comprehensive error handling with original exception preservation

**Test Coverage:**
- All 16 tests passing (100% success rate)
- Tests cover: initialization, configuration, error handling, properties, integration
- Uses mocking to isolate from pipecat dependencies
- Environment variable management via @patch.dict decorators
<!-- SECTION:NOTES:END -->
