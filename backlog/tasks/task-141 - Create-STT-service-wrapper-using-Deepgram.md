---
id: task-141
title: Create STT service wrapper using Deepgram
status: In Progress
assignee:
  - '@backend-engineer'
created_date: '2025-11-28'
updated_date: '2025-11-29 00:34'
labels:
  - implement
  - voice
  - us1
  - stt
  - phase3
dependencies:
  - task-140
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement src/specify_cli/voice/services/stt.py with DeepgramSTTService class wrapping pipecat-ai Deepgram integration. Use Nova 3 model for optimal accuracy and streaming transcription. Reference: docs/research/pipecat-voice-integration-summary.md STT Provider section
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 DeepgramSTTService class extends pipecat DeepgramSTTService with custom configuration
- [x] #2 Supports streaming transcription returning TranscriptionFrame with word-level timing
- [x] #3 API key loaded from DEEPGRAM_API_KEY environment variable
- [x] #4 Model defaults to "nova-3" with language "en" configurable via config
- [x] #5 Connection errors raise STTServiceError with descriptive message and retry hint
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented DeepgramSTTService wrapper with the following features:

Implementation Details:
- Extended pipecat-ai DeepgramSTTService for JP Spec Kit integration
- Uses Nova 3 model by default for optimal accuracy
- Three initialization methods: __init__, from_config(), from_env()
- Comprehensive error handling with STTServiceError exception
- Clear retry hints for common error scenarios

Key Features:
- Streaming transcription with word-level timing via TranscriptionFrame
- Configurable model and language (defaults: nova-3, en)
- Environment-based API key loading (DEEPGRAM_API_KEY)
- Type hints on all public methods
- Extra kwargs support for advanced configuration

Testing:
- 13 comprehensive unit tests with 100% pass rate
- Tests cover all initialization methods and error scenarios
- Mock-based testing to avoid actual API calls
- All code passes ruff linting and formatting

Files Created:
- src/specify_cli/voice/services/stt.py (153 lines)
- tests/voice/test_stt.py (189 lines)
- Updated src/specify_cli/voice/services/__init__.py
<!-- SECTION:NOTES:END -->
