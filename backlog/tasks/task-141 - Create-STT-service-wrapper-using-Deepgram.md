---
id: task-141
title: Create STT service wrapper using Deepgram
status: Done
assignee:
  - '@pm-planner'
created_date: '2025-11-28'
updated_date: '2025-11-29 05:39'
labels:
  - voice
dependencies:
  - task-140
priority: medium
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
Implemented DeepgramSTTService wrapper with:
- LiveOptions for streaming transcription with word-level timing
- API key validation with retry hints
- Model defaults to nova-3 with configurable language
- from_config() and from_env() factory methods
- Custom STTServiceError with retry_hint attribute
<!-- SECTION:NOTES:END -->
