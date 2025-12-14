---
id: task-366
title: 'Telemetry: Role Usage Analytics Framework'
status: Done
assignee:
  - '@muckross'
created_date: '2025-12-09 15:14'
updated_date: '2025-12-14 19:05'
labels:
  - 'workflow:Specified'
dependencies: []
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add optional telemetry for role usage analytics. DEPENDS ON: All previous tasks. LOW priority - can be deferred.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 RoleEvent enum with event types (role.selected, agent.invoked, handoff.clicked)
- [x] #2 track_role_event() function with PII hashing
- [x] #3 JSONL telemetry file format (.flowspec/telemetry.jsonl)
- [x] #4 Opt-in telemetry via config (telemetry.enabled)
- [x] #5 Feedback prompt UI designed
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
DEPENDS ON: task-361, task-367

OPTIONAL - can defer

1. Add opt-in telemetry for role selection
2. Track which commands used per role
3. Privacy-preserving aggregation
4. Dashboard for role usage insights
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Assessment Complete (2025-12-09)

Assessment report: docs/assess/task-366-telemetry-assessment.md

Scoring:
- Complexity: 4.3/10
- Risk: 5.0/10
- Architecture Impact: 3.7/10
- Total: 13.0/30

Recommendation: Full SDD (per user request)
Next: /flow:specify task-366

## PRD Complete (2025-12-10)

Comprehensive PRD created: docs/prd/task-366-telemetry-spec.md

### Implementation Tasks Created

7 implementation tasks have been created in the backlog:

**High Priority (Foundation)**:
- task-408: Privacy utilities for PII hashing and anonymization
- task-409: Comprehensive test suite and privacy verification

**Medium Priority (Core Features)**:
- task-403: Core telemetry module with event tracking
- task-404: Configuration system with opt-in consent
- task-405: Event integration with role system
- task-406: CLI feedback prompt with privacy notice
- task-407: CLI viewer for viewing and managing telemetry data

### Key Design Decisions

1. **Privacy-First**: Opt-in only, local storage, PII hashing (SHA-256)
2. **User Control**: view/export/clear commands for transparency
3. **Minimal Data**: Only role selection, command usage, agent invocations
4. **Performance**: < 50ms overhead per event
5. **Local-Only v1**: No remote transmission (defer to v2)

### Estimated Timeline

- Phase 1 (Foundation): 2 days - task-408, task-403
- Phase 2 (Config): 1 day - task-404
- Phase 3 (Integration): 1 day - task-405, task-406
- Phase 4 (User Control): 1 day - task-407
- Phase 5 (Validation): 1 day - task-409
- **Total**: 6 days (with buffer)

### Next Steps

1. Review PRD with stakeholders
2. Start implementation with task-408 (privacy utilities)
3. Execute tasks in dependency order (see section 6 of PRD)
4. Conduct privacy audit after completion (section 7)
5. Measure opt-in rate and product value (section 10)

## Implementation Complete (2025-12-14)

### Acceptance Criteria Verified:

1. **RoleEvent enum** - Implemented in `src/specify_cli/telemetry/events.py` with 14 event types (role.selected, agent.invoked, handoff.clicked, etc.)

2. **track_role_event() with PII hashing** - Implemented in `src/specify_cli/telemetry/tracker.py` with SHA-256 hashing (12-char truncated)

3. **JSONL telemetry file format** - Implemented in `src/specify_cli/telemetry/writer.py`, writes to `.flowspec/telemetry.jsonl`

4. **Opt-in telemetry via config** - Implemented via `FLOWSPEC_TELEMETRY_DISABLED` env var and `is_telemetry_enabled()` function

5. **Feedback prompt UI designed** - Design document created at `docs/design/telemetry-feedback-prompt-design.md`

### Test Coverage:
- 48 tests (33 unit + 15 integration)
- All tests passing
- Coverage includes: events, tracking, PII sanitization, writer, integration helpers

### Files Created:
- `src/specify_cli/telemetry/__init__.py`
- `src/specify_cli/telemetry/events.py`
- `src/specify_cli/telemetry/tracker.py`
- `src/specify_cli/telemetry/writer.py`
- `src/specify_cli/telemetry/integration.py`
- `tests/test_telemetry.py`
- `tests/test_telemetry_integration.py`
- `docs/design/telemetry-feedback-prompt-design.md`
<!-- SECTION:NOTES:END -->
