# @chamonix Execution Order

Generated: 2025-12-15 06:10
Updated: task-204 family completed, task-508 completed, task-485 DONE, task-486 DONE, task-487 DONE, task-504 DONE

## Summary

| Metric | Count |
|--------|-------|
| Total Tasks | 44 |
| Already Done | 9 |
| On Hold | 1 |
| To Do | 34 |
| Execution Levels | 3 |

## Focus Areas

- **agent-event-system**: 40 tasks
- **infrastructure**: 12 tasks
- **implement**: 10 tasks
- **hooks**: 6 tasks
- **git**: 4 tasks

## Execution Order

Tasks are grouped by execution level. Tasks within the same level have no dependencies on each other and **CAN be executed in parallel**.

### Level 1 (PARALLEL OK)
- **task-505**: Create Git Workflow Configuration Schema
  - Labels: `agent-event-system, git, schema`
- **task-506**: Implement Configuration Loader with Validation
  - Labels: `agent-event-system, config, validation`
- **task-507**: Integrate Claude Code Hooks with Event Emission
  - Labels: `agent-event-system, claude-code, hooks`
- **task-509**: Integrate Git Operations with Event Emission
  - Labels: `agent-event-system, git, integration`
- **task-510**: Integrate MCP Server with Event Emission
  - Labels: `agent-event-system, mcp, integration`
- **task-511**: Implement Action Registry with 55 Actions
  - Labels: `agent-event-system, actions, registry`
- **task-512**: Implement Action Decorator and Helper System
  - Labels: `agent-event-system, actions, helpers`
- **task-513**: Implement Action to Event Mapping
  - Labels: `agent-event-system, actions, events`
- **task-514**: Implement Allowed Followups Validation
  - Labels: `agent-event-system, actions, validation`
- **task-515**: Implement Worktree Creation Automation
  - Labels: `agent-event-system, git, automation`
- **task-516**: Implement Worktree Cleanup Automation
  - Labels: `agent-event-system, git, automation`
- **task-517**: Design Git Hook Framework for Local PR
  - Labels: `agent-event-system, git, design`
- **task-518**: Implement Pre-Commit Quality Gate Lint
  - Labels: `agent-event-system, git, quality`
- **task-519**: Implement Pre-Commit Quality Gate Test
  - Labels: `agent-event-system, git, quality`
- **task-520**: Implement Pre-Commit Quality Gate SAST
  - Labels: `agent-event-system, git, security`
- **task-521**: Implement Local PR Approval Workflow
  - Labels: `agent-event-system, git, workflow`
- **task-522**: Design Agent GPG Key Management System
  - Labels: `agent-event-system, security, design`
- **task-523**: Implement GPG Key Generation for Agents
  - Labels: `agent-event-system, security, implement`
- **task-524**: Implement Automated Commit Signing
  - Labels: `agent-event-system, git, security`
- **task-525**: Design Container Orchestration Strategy
  - Labels: `agent-event-system, containers, design`
- **task-526**: Implement Container Launch Automation
  - Labels: `agent-event-system, containers, implement`
- **task-527**: Implement Runtime Secret Injection
  - Labels: `agent-event-system, security, secrets`
- **task-528**: Implement Container Resource Monitoring
  - Labels: `agent-event-system, containers, monitoring`
- **task-529**: Implement Container Cleanup Automation
  - Labels: `agent-event-system, containers, automation`
- **task-530**: Implement Decision Event Emission Helpers
  - Labels: `agent-event-system, decisions, helpers`
- **task-531**: Implement Decision Query Utilities
  - Labels: `agent-event-system, decisions, query`
- **task-532**: Implement Reversibility Assessment Tool
  - Labels: `agent-event-system, decisions, safety`
- **task-533**: Implement Git Workflow State Machine
  - Labels: `agent-event-system, git, workflow`
- **task-534**: Implement State Recovery Utilities
  - Labels: `agent-event-system, git, recovery`
- **task-535**: Implement Automated Cleanup Orchestrator
  - Labels: `agent-event-system, automation, cleanup`
- **task-536**: Agent Event System Architecture Documentation
  - Labels: `agent-event-system, documentation, architecture`
- **task-537**: Create Event System Integration Tests
  - Labels: `agent-event-system, testing, integration`
- **task-538**: Create Event System Performance Benchmarks
  - Labels: `agent-event-system, testing, performance`
- **task-539**: Implement DORA Metrics Dashboard
  - Labels: `agent-event-system, metrics, observability`
- **task-540**: Create Operational Runbooks for Event System
  - Labels: `agent-event-system, operations, documentation`

## Already Completed (9 tasks)

- **task-504**: Implement Event Query CLI and API ✅
  - Completed: 2025-12-15
  - Deliverables:
    - `src/specify_cli/events/query.py` - EventQuery fluent API with aggregations
    - `src/specify_cli/events/cli.py` - Enhanced CLI with filters and export
    - `tests/test_event_query.py` - 54 passing tests
    - Features: count_by, group_by, time_series; export to JSON/CSV/markdown
    - Performance: 100k events queried in <5 seconds
- **task-487**: Implement Event Router with Namespace Dispatch ✅
  - Completed: 2025-12-15
  - Deliverables:
    - `src/specify_cli/events/router.py` - EventRouter class with pattern matching
    - `src/specify_cli/events/handlers.py` - 7 built-in handlers (JsonlHandler, McpHandler, etc.)
    - `tests/test_event_router.py` - 54 passing tests
    - Pattern matching with wildcards, priority ordering, thread-safe dispatch
- **task-204**: Integrate Event Emission into Backlog Task Operations ✅
  - Completed: 2025-12-15
  - Final design: Python shim + shell wrapper (git hook deprecated)
- **task-204.01**: Create git hook to emit events on backlog task file changes ✅ *(DEPRECATED)*
  - Completed: 2025-12-15
  - Note: Git hooks reserved for other purposes; use wrapper/shim instead
- **task-204.02**: Create backlog CLI wrapper with auto-emit events ✅
  - Location: `scripts/bin/bk`
- **task-485**: Implement Core Event Schema v1.1.0 ✅
  - Completed: 2025-12-15
  - Deliverables:
    - `schemas/events/event-v1.1.0.json` - JSON Schema draft-07
    - `src/specify_cli/hooks/validators.py` - EventValidator class
    - `tests/test_event_schema_v1_1.py` - 36 passing tests
    - 11 namespaces, 60 event types, backward compatible
- **task-486**: Implement JSONL Event Writer Library ✅
  - Completed: 2025-12-15
  - Deliverables:
    - `src/specify_cli/events/writer.py` - EventWriter class with daily rotation
    - `src/specify_cli/events/cli.py` - CLI commands (emit, query, cleanup, tail, stats)
    - `tests/test_event_writer.py` - 32 passing tests
    - Async support, schema validation, thread-safe writes
- **task-508**: Integrate Backlog Operations with Event Emission ✅
  - Completed: 2025-12-15
  - Satisfied by Python shim (`src/specify_cli/backlog/shim.py`)

## On Hold (1 task)

- **task-204.03**: Contribute hooks/events feature to upstream backlog.md ⏸️
  - Reason: Current wrapper + shim implementation fully satisfies requirements
  - Will revisit if upstream interest emerges

## Dependency Map

| Task | Depends On | Blocks | Status |
|------|------------|--------|--------|
| task-204 | - | task-204.03 | ✅ DONE |
| task-204.03 | task-204 | - | ⏸️ ON HOLD |
| task-485 | - | task-486, task-504, task-507-540 | ✅ DONE |
| task-486 | task-485 | task-504, task-507-540 | ✅ DONE |
| task-487 | task-486 | task-507-540 | ✅ DONE |
| task-504 | task-486 | - | ✅ DONE |
| task-505 | - | task-506 | To Do |
| task-506 | task-505 | task-533 | To Do |
| task-507-540 | task-485, task-486, task-487 | - | To Do |
| task-508 | task-204 | - | ✅ DONE |

## Design Decisions (2025-12-15)

### Backlog Event Emission Architecture

**Decision**: Use Python shim + shell wrapper; deprecate git hook approach.

| Approach | Status | Use Case |
|----------|--------|----------|
| Python Shim | ✅ Primary | Agents, workflows, CI/CD |
| Shell Wrapper (`bk`) | ✅ Primary | Human CLI users |
| Git Hook | ⚠️ Deprecated | Not needed - git hooks for other purposes |
| Upstream Contribution | ⏸️ On Hold | Nice-to-have, not blocking |

**Files**:

- `src/specify_cli/backlog/shim.py` - Python API
- `scripts/bin/bk` - Shell wrapper
- `user-docs/user-guides/backlog-wrapper.md` - Documentation
