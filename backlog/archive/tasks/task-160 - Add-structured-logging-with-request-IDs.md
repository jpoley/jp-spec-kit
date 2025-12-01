---
id: task-160
title: Add structured logging with request IDs
status: To Do
assignee:
  - '@pm-planner'
created_date: '2025-11-28'
labels:
  - implement
  - voice
  - hardening
  - observability
  - phase6
dependencies:
  - task-144
priority: high
---

## Description

Create src/specify_cli/voice/logging.py with structured JSON logging and unique request IDs for tracing voice interactions through the pipeline. Reference: docs/research/pipecat-voice-integration-summary.md Observability section

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Each voice session assigned unique session_id (UUID)
- [ ] #2 Each user utterance assigned unique request_id within session
- [ ] #3 All log messages include session_id, request_id, pipeline_stage
- [ ] #4 Logs output as JSON when VOICE_LOG_FORMAT=json environment variable set
- [ ] #5 Log level configurable via VOICE_LOG_LEVEL (DEBUG, INFO, WARNING, ERROR)
<!-- AC:END -->
