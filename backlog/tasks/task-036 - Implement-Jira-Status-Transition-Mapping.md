---
id: task-036
title: Implement Jira Status Transition Mapping
status: To Do
assignee: []
created_date: '2025-11-24'
updated_date: '2025-11-28 01:30'
labels:
  - implementation
  - provider
  - jira
  - US-2
  - US-4
  - P0
  - satellite-mode
dependencies:
  - task-034
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Map local task status to Jira workflow transitions.

## Phase

Phase 4: Implementation - Providers

## User Stories

- US-2: Sync assigned tasks
- US-4: Compliance mode
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Configurable status mapping (local → Jira)
- [ ] #2 Workflow-aware transitions (validate allowed)
- [ ] #3 Handle custom workflows
- [ ] #4 Resolution field handling
- [ ] #5 Comment on transition (optional)

## Deliverables

- Status mapping logic in provider
- Configuration schema
- Sample configs for common workflows
- Unit tests

## Parallelizable

[P] with task-035
<!-- AC:END -->
