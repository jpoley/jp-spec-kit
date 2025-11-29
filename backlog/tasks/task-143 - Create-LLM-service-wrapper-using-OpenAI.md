---
id: task-143
title: Create LLM service wrapper using OpenAI
status: Done
assignee:
  - '@pm-planner'
created_date: '2025-11-28'
updated_date: '2025-11-29 03:59'
labels:
  - implement
  - voice
  - us1
  - llm
  - phase3
dependencies:
  - task-140
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement src/specify_cli/voice/services/llm.py with OpenAILLMService class wrapping pipecat-ai OpenAI integration for GPT-4o with streaming responses and function calling support. Reference: docs/research/pipecat-voice-integration-summary.md LLM Provider section
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 OpenAILLMService class extends pipecat OpenAILLMService with function calling enabled
- [x] #2 Supports streaming responses for token-by-token delivery to TTS
- [x] #3 API key loaded from OPENAI_API_KEY environment variable
- [x] #4 Model defaults to "gpt-4o" with temperature and max_tokens configurable
- [x] #5 LLM errors raise LLMServiceError with OpenAI error code and message
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented OpenAILLMService wrapper with:
- InputParams for temperature and max_tokens configuration
- Streaming responses enabled for token-by-token delivery to TTS
- Function calling support via pipecat context/tools mechanism
- API key and parameter validation with error codes
- from_config() factory method
- Custom LLMServiceError with error_code extraction
<!-- SECTION:NOTES:END -->
