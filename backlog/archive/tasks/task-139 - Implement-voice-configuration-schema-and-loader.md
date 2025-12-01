---
id: task-139
title: Implement voice configuration schema and loader
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-11-28'
updated_date: '2025-11-29 01:03'
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
Implemented comprehensive voice configuration schema with dataclasses and loader.

Components:
- VoiceConfig dataclass with nested AssistantConfig, PipelineConfig, TransportConfig, APIKeys
- Validation of all required fields and API keys based on selected providers
- load_config() function to parse JSON configuration files
- load_api_keys() function to load from environment variables
- Comprehensive error messages for missing keys

Files created:
- src/specify_cli/voice/config.py (101 lines, 98% test coverage)
- templates/voice-config.json (documented template with comments)
- tests/voice/test_config.py (28 tests, all passing)

Validation:
- All required fields validated (assistant.name, pipeline providers)
- API keys checked based on selected providers (deepgram, openai, cartesia, daily, etc.)
- Missing keys raise ValueError with complete list
- 98% test coverage exceeds 90% requirement
<!-- SECTION:NOTES:END -->
