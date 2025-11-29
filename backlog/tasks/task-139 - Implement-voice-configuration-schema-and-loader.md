---
id: task-139
title: Implement voice configuration schema and loader
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-11-28'
updated_date: '2025-11-29 00:26'
labels:
  - implement
  - voice
  - foundational
  - phase2
dependencies:
  - task-138
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create src/specify_cli/voice/config.py with dataclasses for AssistantConfig (name, system_prompt, first_message, last_message, voice_settings) and PipelineConfig (stt, llm, tts providers). Load from JSON config file and environment variables for API keys. Reference: docs/research/pipecat-voice-integration-summary.md Configuration Architecture section
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 VoiceConfig dataclass validates required fields: assistant.name, pipeline.stt.provider, pipeline.llm.provider, pipeline.tts.provider
- [x] #2 Environment variables DEEPGRAM_API_KEY, OPENAI_API_KEY, CARTESIA_API_KEY, DAILY_API_KEY loaded when present
- [x] #3 Missing required API key raises ValueError with message listing all missing keys
- [x] #4 JSON config template created at templates/voice-config.json with all fields documented in comments
- [x] #5 Unit test tests/voice/test_config.py achieves 90%+ line coverage on config.py
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented voice configuration schema and loader with complete validation.

Changes:
- Created src/specify_cli/voice/config.py with dataclasses:
  - VoiceConfig (main config with validation)
  - AssistantConfig (assistant behavior)
  - PipelineConfig, STTConfig, LLMConfig, TTSConfig (pipeline providers)
  - TransportConfig (transport layer)
- Environment variable loading for all API keys (DEEPGRAM, OPENAI, CARTESIA, DAILY)
- Required field validation with detailed error messages
- Created templates/voice-config.json with comprehensive documentation
- Comprehensive test suite (27 tests, 100% coverage)
- All code passes ruff linting and formatting
<!-- SECTION:NOTES:END -->
