---
id: task-153
title: Implement context aggregator for multi-turn conversations
status: To Do
assignee:
  - '@pm-planner'
created_date: '2025-11-28'
labels:
  - implement
  - voice
  - us3
  - processor
  - phase5
dependencies:
  - task-152
priority: high
---

## Description

Create src/specify_cli/voice/processors/context_aggregator.py with ContextAggregator processor that maintains conversation history across multiple turns for coherent multi-step interactions. Reference: docs/research/pipecat-voice-integration-summary.md Phase 2 Context Aggregation

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Aggregator maintains list of (role, content) tuples for conversation history
- [ ] #2 Context window limited to last 20 messages to stay within token limits
- [ ] #3 System prompt always included as first message regardless of window
- [ ] #4 Function call results properly formatted and included in context
- [ ] #5 Context can be reset programmatically for new conversation sessions
<!-- AC:END -->
