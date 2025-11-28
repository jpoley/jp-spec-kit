---
id: task-033
title: Implement GitHub Issue Field Mapping
status: To Do
assignee: []
created_date: '2025-11-24'
updated_date: '2025-11-28 01:30'
labels:
  - implementation
  - provider
  - github
  - US-1
  - US-2
  - P1
  - satellite-mode
dependencies:
  - task-031
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Map GitHub issue fields to task schema.

## Phase

Phase 4: Implementation - Providers

## User Stories

- US-1: Pull remote task by ID
- US-2: Sync assigned tasks
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Title, body, state, assignee, labels
- [ ] #2 Milestone mapping
- [ ] #3 Project (beta) support
- [ ] #4 Custom field handling (if available)
- [ ] #5 Bidirectional mapping (task → issue)

## Deliverables

- Field mapping logic in provider
- Configuration schema in config.yml
- Unit tests for all field types

## Parallelizable

[P] with task-032
<!-- AC:END -->
