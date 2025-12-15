---
id: task-487
title: Implement Event Router with Namespace Dispatch
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-12-14 03:06'
updated_date: '2025-12-15 14:34'
labels:
  - agent-event-system
  - phase-1
  - architecture
  - infrastructure
  - foundation
  - 'workflow:Validated'
dependencies:
  - task-485
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create event routing system dispatching events to handlers based on namespace with pluggable consumers.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 EventRouter class with register_handler method
- [x] #2 Pattern matching supports wildcards like git.* matches all git events
- [x] #3 Built-in handlers for JSONL file and MCP server
- [x] #4 Event filtering by task_id agent_id time_range
- [x] #5 Unit tests for routing to multiple handlers
<!-- AC:END -->
