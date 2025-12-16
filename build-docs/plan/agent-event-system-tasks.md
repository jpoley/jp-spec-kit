# Agent Event System - Task Execution Plan

**Status**: Planned
**Branch**: `agent-event-execution`
**Created**: 2025-12-13
**Source Documents**:
- `docs/action-system.md` - 55+ actions across 18 categories
- `docs/decision-tracker.md` - Decision event logging
- `docs/git-workflow-objectives.md` - 5 git workflow objectives
- `docs/jsonl-event-system.md` - 60 event types across 11 namespaces

---

## Executive Summary

This plan defines **40 tasks** across **8 phases** to implement a unified Agent Event System. The system provides:

1. **Unified Observability**: JSONL event stream for all agent, task, git, and container operations
2. **Action Vocabulary**: 55+ standardized actions with guaranteed event emission
3. **Git Workflow Automation**: Worktrees, local PR gates, GPG signing, containers
4. **Decision Tracking**: Reversibility assessment and audit trails
5. **DORA Metrics**: Automated performance measurement

---

## Task Dependency Graph

```
Phase 1: Foundation
┌─────────────────────────────────────────────────────────────────────────┐
│  task-485 ─────┬────► task-486 (Writer) ────► task-492 (Hook Integration)
│  (Schema)      │                                        │
│                ├────► task-487 (Router)                 │
│                │                                        │
│                └────► task-488 (Query CLI)              │
│                                                         │
│  task-489 ─────────► task-490 (Config Loader)          │
│  (Config Schema)                                        │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
Phase 2: Event Emission
┌─────────────────────────────────────────────────────────────────────────┐
│  task-492 ─────────► task-493 (Backlog Events) ────► task-494 (Git Events)
│  (Hooks)             [extends task-204]               [extends task-204.01]
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
Phase 3: Action System
┌─────────────────────────────────────────────────────────────────────────┐
│  task-495 ─────────► task-496 ─────────► task-497 ─────────► task-498
│  (Registry)          (Decorators)        (Mapping)           (Followups)
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
Phase 4: Git Workflow
┌─────────────────────────────────────────────────────────────────────────┐
│  task-499 ─────────► task-500          task-501 ─────► task-502/503/504
│  (Worktree Create)   (Worktree Clean)  (Hook Framework)   (Quality Gates)
│                                                                │
│                                        task-505 ◄──────────────┘
│                                        (Local PR Approval)
│
│  task-506 ─────────► task-507 ─────────► task-508
│  (GPG Design)        (GPG Generate)      (Commit Sign)
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
Phase 5: Container Integration
┌─────────────────────────────────────────────────────────────────────────┐
│  task-509 ─────────► task-510 ─────────► task-511
│  (Strategy)          (Launch)            (Secrets)
│                          │
│                          └────► task-512 (Monitor) ────► task-513 (Cleanup)
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
Phase 6: Decision Tracking
┌─────────────────────────────────────────────────────────────────────────┐
│  task-514 ─────────► task-515 ─────────► task-516
│  (Emission)          (Query)             (Assessment)
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
Phase 7: State Machine
┌─────────────────────────────────────────────────────────────────────────┐
│  task-517 ─────────► task-518 ─────────► task-519
│  (State Machine)     (Recovery)          (Cleanup Orchestrator)
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
Phase 8: Documentation & Testing
┌─────────────────────────────────────────────────────────────────────────┐
│  task-520 (Docs) ────► task-521 (Integration Tests)
│                        task-522 (Benchmarks)
│                        task-523 (DORA Dashboard)
│                        task-524 (Runbooks)
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Foundation (6 tasks)

### task-485: Implement Core Event Schema v1.1.0 ✅ CREATED
- **Priority**: HIGH
- **Labels**: architecture, infrastructure, foundation
- **Description**: Create JSON Schema draft-07 definition for unified event structure with all 60 event types across 11 namespaces.
- **ACs**:
  1. JSON Schema file at `.flowspec/events/schema/event-v1.1.0.json`
  2. Schema supports all 11 namespaces
  3. Schema enforces required fields and validates optional structures
  4. Unit tests validate 60+ sample events
  5. Schema version follows semver

### task-486: Implement JSONL Event Writer Library ✅ CREATED
- **Priority**: HIGH
- **Labels**: architecture, infrastructure, foundation
- **Dependencies**: task-485
- **Description**: Create Python module `flowspec.events` with `emit_event()` function and JSONL file writer with daily rotation.
- **ACs**:
  1. Python module `flowspec.events.writer` with `emit_event()` function
  2. JSONL files auto-rotate daily with configurable retention
  3. Events validated against schema before write
  4. Async `emit_event_async()` for non-blocking writes
  5. CLI command `specify events emit` for manual emission

### task-487: Implement Event Router with Namespace Dispatch
- **Priority**: HIGH
- **Labels**: architecture, infrastructure, foundation
- **Dependencies**: task-485
- **Description**: Create event routing system dispatching events to handlers based on namespace with pluggable consumers.
- **ACs**:
  1. `EventRouter` class with `register_handler(pattern, handler)` method
  2. Pattern matching supports wildcards (`git.*` matches all git events)
  3. Built-in handlers for JSONL file and MCP server
  4. Event filtering by `task_id`, `agent_id`, `time_range`
  5. Unit tests for routing to multiple handlers

### task-488: Implement Event Query CLI and API
- **Priority**: MEDIUM
- **Labels**: architecture, infrastructure, foundation
- **Dependencies**: task-485
- **Description**: Build jq-based query utilities and Python API for event analysis with CLI interface.
- **ACs**:
  1. CLI command `specify events query` with filters
  2. Python module `flowspec.events.query` with fluent API
  3. Export capabilities: JSON, CSV, markdown
  4. Aggregation functions: `count_by()`, `group_by()`, `time_series()`
  5. Query 100k events in under 5 seconds

### task-489: Create Git Workflow Configuration Schema
- **Priority**: HIGH
- **Labels**: infrastructure, configuration
- **Description**: Define YAML schema for `.flowspec/git-workflow.yml` with worktree, local_pr, signing, isolation sections.
- **ACs**:
  1. Configuration schema with all required sections documented
  2. Default configuration template with comments
  3. Validation command `flowspec workflow config validate`
  4. Environment variable override support
  5. Documentation in `docs/reference/git-workflow-config.md`

### task-490: Implement Configuration Loader with Validation
- **Priority**: HIGH
- **Labels**: infrastructure, configuration
- **Dependencies**: task-489
- **Description**: Build configuration loader that validates and merges defaults with user overrides.
- **ACs**:
  1. Configuration class `GitWorkflowConfig` in Python
  2. Load from `.flowspec/git-workflow.yml` with fallback to defaults
  3. Emit `system.config_change` event on reload
  4. CLI command `flowspec config show`
  5. Unit tests for all config sections

---

## Phase 2: Event Emission Integration (4 tasks)

### task-492: Integrate Claude Code Hooks with Event Emission
- **Priority**: HIGH
- **Labels**: architecture, hooks, event-emission
- **Dependencies**: task-486
- **Description**: Wire Claude Code hooks to emit events using unified schema.
- **ACs**:
  1. All 10 Claude Code hook types emit events
  2. Events include proper context with `task_id`, `branch_name`
  3. Correlation IDs propagated across hook chains
  4. Performance impact under 50ms per hook
  5. Backward compatible with existing hook configurations

### task-493: Integrate Backlog Operations with Event Emission
- **Priority**: HIGH
- **Labels**: architecture, backlog-integration, event-emission
- **Dependencies**: task-204 (existing)
- **Description**: Emit task events on backlog operations. Extends task-204.
- **ACs**:
  1. `task.created` event on `backlog task create`
  2. `task.state_changed` event on status updates
  3. `task.ac_checked` event on acceptance criteria completion
  4. `task.assigned` event on assignee changes
  5. Events include full task metadata in `task` object

### task-494: Integrate Git Operations with Event Emission
- **Priority**: HIGH
- **Labels**: architecture, scm, event-emission
- **Dependencies**: task-204.01 (existing)
- **Description**: Emit git events on branch, commit, push, merge operations. Extends task-204.01.
- **ACs**:
  1. `git.commit` event on every commit with sha, message
  2. `git.branch_created` and `git.branch_deleted` events
  3. `git.pushed` event on push to remote
  4. `git.merged` event on merge completion
  5. Events include GPG signing info when available

### task-495: Integrate MCP Server with Event Emission
- **Priority**: MEDIUM
- **Labels**: architecture, mcp, event-emission
- **Dependencies**: task-487
- **Description**: Enable event emission to MCP server for real-time observability.
- **ACs**:
  1. MCP tool `emit_event()` available to agents
  2. Events routed to MCP in addition to JSONL
  3. Configurable MCP endpoint in git-workflow.yml
  4. Graceful degradation if MCP unavailable
  5. Integration tests with agent-updates-collector

---

## Phase 3: Action System (4 tasks)

### task-496: Implement Action Registry with 55 Actions
- **Priority**: HIGH
- **Labels**: architecture, action-system
- **Description**: Create registry for 55 actions across 18 categories as defined in `action-system.md`.
- **ACs**:
  1. `ActionRegistry` class with `register()` and `lookup()` methods
  2. All 55 actions from documentation registered
  3. Actions categorized by domain and category
  4. Input and output contracts defined per action
  5. Idempotency and side-effects documented per action

### task-497: Implement Action Decorator and Helper System
- **Priority**: HIGH
- **Labels**: architecture, action-system
- **Dependencies**: task-496
- **Description**: Create Python decorator for defining actions with automatic event emission.
- **ACs**:
  1. `@action` decorator with `verb`, `domain`, `category` parameters
  2. Automatic `action.invoked` event on execution start
  3. Automatic `action.succeeded` or `action.failed` on completion
  4. Input validation against action contract
  5. Duration tracking in action events

### task-498: Implement Action to Event Mapping
- **Priority**: HIGH
- **Labels**: architecture, action-system
- **Dependencies**: task-497
- **Description**: Implement automatic mapping from action execution to event emission.
- **ACs**:
  1. Every accepted action emits `action.invoked`
  2. Guaranteed terminal event (succeeded, failed, or aborted)
  3. Side-effect events emitted as documented
  4. Mapping table matches `action-system.md` documentation
  5. Unit tests validate all 55 action mappings

### task-499: Implement Allowed Followups Validation
- **Priority**: MEDIUM
- **Labels**: architecture, action-system
- **Dependencies**: task-498
- **Description**: Validate action sequences against allowed followups graph.
- **ACs**:
  1. Followup graph defined matching documentation
  2. `ValidationError` on invalid action sequence
  3. Warnings logged for unusual but allowed sequences
  4. Query API for valid next actions given current state
  5. Visualization of followup graph available

---

## Phase 4: Git Workflow (10 tasks)

### task-500: Implement Worktree Creation Automation
- **Priority**: HIGH
- **Labels**: infrastructure, scm, git-workflow
- **Dependencies**: task-490
- **Description**: Create script to generate git worktrees for tasks with proper branch naming.
- **ACs**:
  1. Script `worktree-create.sh task-id feature-description`
  2. Creates worktree at `worktrees/task-id-feature-description/`
  3. Creates branch from configured base branch
  4. Emits `git.branch_created` and `git.worktree_created` events
  5. Validates task exists in backlog before creating

### task-501: Implement Worktree Cleanup Automation
- **Priority**: MEDIUM
- **Labels**: infrastructure, scm, git-workflow
- **Dependencies**: task-500
- **Description**: Create cleanup automation for completed or abandoned task worktrees.
- **ACs**:
  1. Script `worktree-cleanup.sh task-id`
  2. Removes worktree safely (checks for uncommitted changes)
  3. Optionally deletes branch if merged
  4. Emits `git.worktree_removed` and `git.branch_deleted` events
  5. Post-merge hook triggers automatic cleanup

### task-502: Design Git Hook Framework for Local PR
- **Priority**: HIGH
- **Labels**: infrastructure, devops, cicd, git-workflow
- **Dependencies**: task-490
- **Description**: Create extensible git hook framework with centralized dispatcher.
- **ACs**:
  1. Dispatcher script `hook-dispatcher.sh`
  2. Installation script `install-hooks.sh`
  3. Hook registration via symlinks in `.git/hooks`
  4. Event emission for all hook triggers
  5. Documentation for adding custom hooks

### task-503: Implement Pre-Commit Quality Gate - Lint
- **Priority**: HIGH
- **Labels**: infrastructure, quality, cicd, git-workflow
- **Dependencies**: task-502
- **Description**: Create lint quality gate running configured linters before commit.
- **ACs**:
  1. Pre-commit hook calls `quality-gates/lint.sh`
  2. Supports ruff, eslint, golangci-lint
  3. Emits `quality_gate.started` and `quality_gate.passed/failed` events
  4. Configurable skip with `git commit --no-verify`
  5. Exit code 1 blocks commit on failure

### task-504: Implement Pre-Commit Quality Gate - Test
- **Priority**: HIGH
- **Labels**: infrastructure, quality, cicd, git-workflow
- **Dependencies**: task-502
- **Description**: Create test quality gate running relevant test suite before commit.
- **ACs**:
  1. Pre-commit hook calls `quality-gates/test.sh`
  2. Runs pytest, vitest, or go test based on project
  3. Smart test selection for affected tests only
  4. Emits `quality_gate` events
  5. Configurable timeout (default 600s)

### task-505: Implement Pre-Commit Quality Gate - SAST
- **Priority**: HIGH
- **Labels**: infrastructure, security, devsecops, cicd, git-workflow
- **Dependencies**: task-502
- **Description**: Create security scanning gate with bandit and semgrep.
- **ACs**:
  1. Pre-commit hook calls `quality-gates/sast.sh`
  2. Runs bandit and semgrep
  3. Emits `security.vulnerability_found` events
  4. Fail on high/critical findings
  5. SARIF output stored in `.flowspec/security/sarif`

### task-506: Implement Local PR Approval Workflow
- **Priority**: HIGH
- **Labels**: infrastructure, cicd, devops, git-workflow
- **Dependencies**: task-503, task-504, task-505
- **Description**: Create orchestrator running all quality gates and making approval decision.
- **ACs**:
  1. Script `local-pr-submit.sh`
  2. Runs all configured checks in parallel where possible
  3. Implements approval modes: auto, human_required, agent_review
  4. Emits `git.local_pr_submitted` and `approved/rejected` events
  5. Human approval workflow prompts for sign-off if required

### task-507: Design Agent GPG Key Management System
- **Priority**: HIGH
- **Labels**: infrastructure, security, devsecops, git-workflow
- **Dependencies**: task-490
- **Description**: Design secure key storage and registration system for agent identities.
- **ACs**:
  1. Key storage at `.flowspec/agent-keys/` with .gitignore
  2. Key registry file `keyring.txt`
  3. Public keys in repo, private keys in secure storage
  4. Key rotation strategy documented
  5. Emit `system.config_change` on key registration

### task-508: Implement GPG Key Generation for Agents
- **Priority**: HIGH
- **Labels**: infrastructure, security, devsecops, git-workflow
- **Dependencies**: task-507
- **Description**: Create automation to generate unique GPG keys for each agent.
- **ACs**:
  1. Script `gpg-setup-agent.sh agent-id`
  2. Generates 4096-bit RSA key non-interactively
  3. Registers key in keyring with agent ID mapping
  4. Exports public key to agent-keys directory
  5. Emits `security.gpg_key_generated` event

### task-509: Implement Automated Commit Signing
- **Priority**: MEDIUM
- **Labels**: infrastructure, security, scm, git-workflow
- **Dependencies**: task-508
- **Description**: Configure git to automatically sign commits with agent GPG keys.
- **ACs**:
  1. Post-commit hook emits `git.commit` with GPG info
  2. Git config automatically set for agent identity
  3. Verify signatures before push
  4. Reject unsigned commits in CI if required
  5. Support co-authored-by for multi-agent collaboration

---

## Phase 5: Container Integration (5 tasks)

### task-510: Design Container Orchestration Strategy
- **Priority**: HIGH
- **Labels**: infrastructure, devops, container
- **Dependencies**: task-490
- **Description**: Design architecture for spinning up isolated containers per task with worktree mounts.
- **ACs**:
  1. Architecture document in `docs/guides/container-strategy.md`
  2. Container naming convention documented
  3. Volume mount strategy: worktree (RW), repo (RO)
  4. Network isolation modes documented
  5. Resource limits defined

### task-511: Implement Container Launch Automation
- **Priority**: HIGH
- **Labels**: infrastructure, devops, container
- **Dependencies**: task-510
- **Description**: Create script to launch devcontainers with proper configuration.
- **ACs**:
  1. Script `container-launch.sh task-id agent-id`
  2. Uses flowspec-agents base image
  3. Mounts worktree at `/workspace`
  4. Applies configured resource limits
  5. Emits `container.started` event with container ID

### task-512: Implement Runtime Secret Injection
- **Priority**: HIGH
- **Labels**: infrastructure, security, devsecops, container
- **Dependencies**: task-511
- **Description**: Securely inject secrets into running containers without baking into images.
- **ACs**:
  1. Script `inject-secrets.sh container-id`
  2. Reads secrets from host keychain or secret service
  3. Injects via environment variables
  4. Secrets never written to disk or logs
  5. Emits `container.secrets_injected` event (names only)

### task-513: Implement Container Resource Monitoring
- **Priority**: MEDIUM
- **Labels**: infrastructure, observability, container
- **Dependencies**: task-511
- **Description**: Monitor container resource usage and emit events on limit hits.
- **ACs**:
  1. Monitoring script `monitor-containers.sh`
  2. Runs in background, checks every 30s
  3. Emits `container.resource_limit_hit` when >90%
  4. Logs resource usage to metrics file
  5. Graceful shutdown on persistent limit hits

### task-514: Implement Container Cleanup Automation
- **Priority**: MEDIUM
- **Labels**: infrastructure, devops, container
- **Dependencies**: task-511
- **Description**: Automatically stop and remove containers when tasks complete.
- **ACs**:
  1. Cleanup triggered by `task.completed` or `task.archived` events
  2. Script `container-cleanup.sh task-id`
  3. Saves container logs before removal
  4. Emits `container.stopped` event with exit code
  5. Force-kill containers running >24 hours

---

## Phase 6: Decision Tracking (3 tasks)

### task-515: Implement Decision Event Emission Helpers
- **Priority**: HIGH
- **Labels**: architecture, decision-tracker
- **Dependencies**: task-486
- **Description**: Create helper functions for emitting well-formed decision events.
- **ACs**:
  1. Function `emit_decision()` with `decision_id`, `category`, `message`
  2. Reversibility assessment helper with `type`, `lock_in_factors`, `cost`
  3. Alternatives tracking with `option`, `rejected_reason` pairs
  4. Supporting material links with `url`, `title`, `type`
  5. Integration with flowspec commands for automatic emission

### task-516: Implement Decision Query Utilities
- **Priority**: MEDIUM
- **Labels**: architecture, decision-tracker
- **Dependencies**: task-515
- **Description**: Create utilities to query and analyze decision events from JSONL stream.
- **ACs**:
  1. CLI command `specify decisions list` with filters
  2. Query by category, reversibility_type, time_range
  3. Export decision timeline as markdown
  4. Identify one-way-door decisions for review
  5. Link decisions to tasks and branches

### task-517: Implement Reversibility Assessment Tool
- **Priority**: LOW
- **Labels**: architecture, decision-tracker
- **Dependencies**: task-516
- **Description**: Create interactive tool for assessing decision reversibility.
- **ACs**:
  1. CLI command `specify decision assess`
  2. Prompts for lock-in factors from predefined list
  3. Calculates reversal cost based on factors
  4. Suggests reversal window based on project phase
  5. Outputs formatted decision event ready for emission

---

## Phase 7: State Machine & Automation (3 tasks)

### task-518: Implement Git Workflow State Machine
- **Priority**: HIGH
- **Labels**: architecture, git-workflow, automation
- **Dependencies**: task-487, task-494
- **Description**: Create event-driven state machine for git workflow transitions.
- **ACs**:
  1. `StateMachine` class with states from `git-workflow-objectives.md`
  2. Transitions triggered by `event_type` matching
  3. Invalid transitions raise `StateError`
  4. Current state reconstructed from event replay
  5. Visualization of state machine as mermaid diagram

### task-519: Implement State Recovery Utilities
- **Priority**: MEDIUM
- **Labels**: architecture, git-workflow, automation
- **Dependencies**: task-518
- **Description**: Create utilities for reconstructing workflow state from event replay.
- **ACs**:
  1. Script `state-machine.py` with replay functionality
  2. Reconstruct task state, worktree associations, container mappings
  3. Handle corrupted or missing events gracefully
  4. Validate recovered state against current system state
  5. Tested with 1000+ event corpus

### task-520: Implement Automated Cleanup Orchestrator
- **Priority**: MEDIUM
- **Labels**: architecture, automation
- **Dependencies**: task-501, task-514
- **Description**: Create orchestrator that monitors events and triggers cleanup actions.
- **ACs**:
  1. `CleanupOrchestrator` class listening for completion events
  2. Triggers worktree cleanup on `task.completed`
  3. Triggers container cleanup on `task.archived`
  4. Configurable cleanup delays and conditions
  5. Emits `lifecycle.cleanup_completed` events

---

## Phase 8: Documentation & Testing (5 tasks)

### task-521: Create Agent Event System Architecture Documentation
- **Priority**: HIGH
- **Labels**: documentation
- **Description**: Create comprehensive architecture documentation with diagrams.
- **ACs**:
  1. Architecture overview in `docs/guides/event-system-architecture.md`
  2. ASCII and mermaid diagrams for event flow
  3. Component interaction documentation
  4. API reference for all public functions
  5. Migration guide from legacy systems

### task-522: Create Event System Integration Tests
- **Priority**: HIGH
- **Labels**: testing, quality
- **Dependencies**: All Phase 1-7 tasks
- **Description**: Create comprehensive integration test suite for event system.
- **ACs**:
  1. End-to-end test: task lifecycle emits correct events
  2. Test git workflow state machine transitions
  3. Test container lifecycle with event emission
  4. Test decision tracking workflow
  5. Coverage target 80% for event modules

### task-523: Create Event System Performance Benchmarks
- **Priority**: MEDIUM
- **Labels**: testing, performance
- **Dependencies**: task-486
- **Description**: Create benchmarks for event emission, query, and storage performance.
- **ACs**:
  1. Benchmark `emit_event` latency (target <10ms)
  2. Benchmark query performance for 100k events
  3. Benchmark file rotation and archival
  4. Memory usage profiling for long-running agents
  5. CI integration to track performance regressions

### task-524: Implement DORA Metrics Dashboard
- **Priority**: LOW
- **Labels**: observability, devops
- **Dependencies**: task-488
- **Description**: Create dashboard displaying deployment frequency, lead time, CFR, and MTTR.
- **ACs**:
  1. CLI command `specify metrics dora --dashboard`
  2. Shows all four metrics with color-coded status
  3. Trend arrows showing improvement/degradation
  4. Exportable as JSON, markdown, or HTML
  5. GitHub Actions posts dashboard to PR comments

### task-525: Create Operational Runbooks for Event System
- **Priority**: MEDIUM
- **Labels**: documentation, devops
- **Description**: Create runbooks for incident response, state recovery, and troubleshooting.
- **ACs**:
  1. Incident response runbook in `docs/runbooks`
  2. State recovery runbook with event replay procedures
  3. Performance troubleshooting runbook
  4. Secrets rotation runbook
  5. All runbooks tested with simulated scenarios

---

## Decision Log

All decisions made during this planning session are logged in JSONL format:

**PLAN-001**: Initiated comprehensive Agent Event System planning
- **Category**: architecture
- **Reversibility**: two-way-door (low cost)
- **Rationale**: Four interconnected documentation files define unified event-driven architecture

**PLAN-002**: Consolidated Architecture and Platform plans into unified task breakdown
- **Category**: planning
- **Reversibility**: two-way-door (low cost)
- **Rationale**: Two agents delivered comprehensive but overlapping task lists. Merged to avoid duplication.

**PLAN-003**: Phased implementation approach with 8 phases
- **Category**: process
- **Reversibility**: two-way-door (trivial cost)
- **Alternatives Rejected**:
  - Big bang implementation (too risky, no incremental value)
  - Feature-based slicing (dependencies make pure vertical slicing impractical)

---

## Execution Order Summary

**Phase 1 (Weeks 1-2)**: Foundation
- task-485 → task-486, task-487, task-488 (parallel)
- task-489 → task-490

**Phase 2 (Week 3)**: Event Emission
- task-492 → task-493 → task-494
- task-495 (parallel)

**Phase 3 (Week 4)**: Action System
- task-496 → task-497 → task-498 → task-499

**Phase 4 (Weeks 5-6)**: Git Workflow
- Worktrees: task-500 → task-501
- Local PR: task-502 → task-503, task-504, task-505 (parallel) → task-506
- GPG: task-507 → task-508 → task-509

**Phase 5 (Week 7)**: Container Integration
- task-510 → task-511 → task-512
- task-513, task-514 (parallel with above)

**Phase 6 (Week 7)**: Decision Tracking
- task-515 → task-516 → task-517

**Phase 7 (Week 8)**: State Machine
- task-518 → task-519 → task-520

**Phase 8 (Week 9)**: Documentation & Testing
- task-521, task-522, task-523 (parallel)
- task-524, task-525 (parallel)

---

## Success Metrics

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Event Coverage | 0% | 95%+ | Events emitted / workflow actions |
| Deployment Frequency | 1/week | 3+/day | `git.merged` events |
| Lead Time | 3 days | <4 hours | Commit to merge delta |
| Change Failure Rate | 20% | <5% | Rejected local PRs / total |
| MTTR | 2 hours | <15 min | Incident to recovery delta |

---

## Related Tasks (Existing)

These existing tasks are prerequisites or extensions:
- **task-204**: Integrate Event Emission into Backlog Task Operations
- **task-204.01**: Create git hook to emit events on backlog task file changes
- **task-204.02**: Create backlog CLI wrapper with auto-emit events (Done)
- **task-204.03**: Contribute hooks/events feature to upstream backlog.md
- **task-328**: Design: Git Hook Integration for Agent Sync

---

## Files Modified/Created

This planning session creates:
1. `docs/plan/agent-event-system-tasks.md` (this file)
2. `.flowspec/events/events-2025-12-13.jsonl` (decision events)
3. `scripts/create-event-system-tasks.sh` (task creation script)

Backlog tasks created:
- task-485: Implement Core Event Schema v1.1.0
- task-486: Implement JSONL Event Writer Library
