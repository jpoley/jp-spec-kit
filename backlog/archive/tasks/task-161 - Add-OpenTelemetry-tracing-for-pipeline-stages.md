---
id: task-161
title: Add OpenTelemetry tracing for pipeline stages
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
  - task-160
priority: high
---

## Description

Create src/specify_cli/voice/observability.py with OpenTelemetry tracing spans for each pipeline stage (STT, LLM, TTS, function calls) to enable distributed tracing and latency analysis. Reference: docs/research/pipecat-voice-integration-summary.md Latency Profile and Observability

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Parent span created for each user request with session_id attribute
- [ ] #2 Child spans created for STT, LLM, TTS, and function call stages
- [ ] #3 Spans include duration, status (OK/ERROR), and service name attributes
- [ ] #4 Traces exportable to OTLP endpoint via OTEL_EXPORTER_OTLP_ENDPOINT
- [ ] #5 Tracing disabled by default, enabled via VOICE_ENABLE_TRACING=true
<!-- AC:END -->
