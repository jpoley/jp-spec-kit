---
id: task-146
title: Create JP Spec Kit voice assistant system prompt
status: To Do
assignee:
  - '@pm-planner'
created_date: '2025-11-28'
labels:
  - implement
  - voice
  - us1
  - prompt
  - phase3
dependencies:
  - task-140
priority: high
---

## Description

Create src/specify_cli/voice/prompts.py with SYSTEM_PROMPT constant defining the JP Spec Kit voice assistant persona, capabilities, and interaction style for concise voice responses. Reference: docs/research/pipecat-voice-integration-summary.md System Prompt Engineering section

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 SYSTEM_PROMPT defines assistant as "JP Spec Kit Voice Assistant"
- [ ] #2 Prompt describes 5 core capabilities: generate specs, create plans, manage tasks, answer questions, guide SDD workflow
- [ ] #3 Prompt instructs assistant to keep responses concise for voice (under 3 sentences)
- [ ] #4 Prompt includes instructions for using function calling tools
- [ ] #5 System prompt is loadable and overridable via VoiceConfig.assistant.system_prompt
<!-- AC:END -->
