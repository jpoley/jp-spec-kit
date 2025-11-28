---
id: task-028
title: Implement Rate Limiter & Retry Logic
status: To Do
assignee: []
created_date: '2025-11-24'
updated_date: '2025-11-28 01:30'
labels:
  - implementation
  - core
  - P0
  - satellite-mode
dependencies:
  - task-026
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement token bucket rate limiter and exponential backoff retry.

## Phase

Phase 3: Implementation - Core
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 `RateLimiter` class with token bucket algorithm
- [ ] #2 Exponential backoff using `tenacity` library
- [ ] #3 Configurable limits per provider
- [ ] #4 Rate limit warnings logged
- [ ] #5 Auto-resume after rate limit reset

## Deliverables

- `src/backlog_md/infrastructure/rate_limiter.py` - Implementation
- Unit tests with time mocking
- Integration tests with real APIs (controlled)

## Parallelizable

[P] with task-027
<!-- AC:END -->
