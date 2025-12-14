# Technical Specification: Agent Event System Architecture

**Version**: 1.0.0
**Status**: Draft
**Author**: @galway (Software Architect)
**Created**: 2025-12-13
**PRD Source**: N/A (Architecture Initiative)

---

## Executive Summary

The Agent Event System is a **unified observability and coordination platform** that consolidates four interconnected subsystems—JSONL events, actions, decisions, and git workflows—into a single event-driven architecture. This system provides complete visibility into agent behavior, enables distributed tracing, supports compliance auditing, and powers event-driven workflows across multi-agent systems.

### Business Value

| Objective | Value Delivered | Success Metric |
|-----------|----------------|----------------|
| **Unified Observability** | Single source of truth for all agent/git/task activity | 100% of operations emit events |
| **Compliance & Audit** | Complete audit trail for security, decisions, git operations | Zero gaps in event coverage |
| **Developer Experience** | Simple emit/query interface for events | <5 lines to emit event |
| **Distributed Coordination** | Enable multi-agent workflows via event correlation | Support 10+ concurrent agents |
| **Git Workflow Automation** | Event-driven worktree, PR, container lifecycle | Zero manual cleanup |

### Investment Justification (Selling Options)

Using Gregor Hohpe's "Selling Options" framework:

**Option 1: Manual Coordination (Status Quo)**
- **Cost**: High developer overhead, manual tracking, error-prone
- **Risk**: No audit trail, coordination failures, compliance gaps
- **Lock-in**: Tribal knowledge, fragile scripts

**Option 2: Build Unified Event System (Proposed)**
- **Cost**: 3-4 weeks development + 1 week testing
- **Risk**: Low - JSONL is proven, event sourcing is well-understood
- **Lock-in**: None - event schema can evolve via versioning
- **Payoff**: Enables advanced workflows, compliance, multi-agent orchestration

**Option 3: Commercial Observability Platform**
- **Cost**: $5k-20k/year license + integration effort
- **Risk**: Vendor lock-in, data privacy concerns
- **Lock-in**: High - vendor-specific APIs and data formats

**Recommendation**: **Option 2** - Build unified system. The investment creates a flexible foundation for future agent capabilities while maintaining full control and avoiding vendor lock-in.

---

## 1. Strategic Framing (Penthouse View)

### 1.1 Business Objectives

| ID | Objective | Stakeholder | Priority |
|----|-----------|-------------|----------|
| BO1 | Enable multi-agent workflows with coordination | Engineering | HIGH |
| BO2 | Provide complete audit trail for compliance | Security/Legal | HIGH |
| BO3 | Support git workflow automation (worktrees, PRs, containers) | DevOps | HIGH |
| BO4 | Track architectural decisions with reversibility assessment | Architecture | MEDIUM |
| BO5 | Enable real-time monitoring and debugging of agent behavior | Engineering | MEDIUM |

### 1.2 Organizational Impact

**Before**: Fragmented observability, manual coordination, tribal knowledge
- Agent activities tracked in separate systems (MCP logs, git logs, task comments)
- No correlation between task → branch → container → decision
- Manual cleanup of worktrees and containers
- No audit trail for decisions or agent actions

**After**: Unified event stream, automated workflows, institutional knowledge
- Single JSONL stream captures all events with correlation IDs
- Query events by task, agent, branch, container, or decision
- Event-driven state machines automate git workflow lifecycle
- Complete decision history with reversibility assessment

**Change Management**:
- **Phase 1**: Introduce event emission in new code (low disruption)
- **Phase 2**: Retrofit existing workflows (moderate disruption)
- **Phase 3**: Event-driven automation (workflow changes)

### 1.3 Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Event schema drift over time | MEDIUM | HIGH | Strict versioning, JSON Schema validation |
| Event log size grows unbounded | HIGH | MEDIUM | Rotation policy, archival strategy |
| Integration complexity with existing tools | MEDIUM | MEDIUM | Wrapper scripts, backward compatibility |
| Performance overhead of event emission | LOW | LOW | Async writes, buffering |
| Developer resistance to event-first design | MEDIUM | MEDIUM | Clear documentation, helper utilities |

---

## 2. Architecture Blueprint (Engine Room View)

### 2.1 Core Components

```
┌────────────────────────────────────────────────────────────────────┐
│                    AGENT EVENT SYSTEM ARCHITECTURE                  │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐          │
│  │   Event     │     │   Event     │     │   Event     │          │
│  │  Producers  │────▶│   Router    │────▶│  Consumers  │          │
│  └─────────────┘     └─────────────┘     └─────────────┘          │
│        │                    │                    │                 │
│        │                    ▼                    │                 │
│        │            ┌───────────────┐            │                 │
│        │            │  Event Store  │            │                 │
│        │            │  (JSONL)      │            │                 │
│        │            └───────────────┘            │                 │
│        │                    │                    │                 │
│        ▼                    ▼                    ▼                 │
│  ┌──────────────────────────────────────────────────────┐          │
│  │              Integration Layer                       │          │
│  ├──────────────────────────────────────────────────────┤          │
│  │ • Claude Hooks    • Git Hooks    • Backlog.md       │          │
│  │ • MCP Servers     • CLI Wrappers • Bash Scripts     │          │
│  └──────────────────────────────────────────────────────┘          │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

#### 2.1.1 Event Producers

**Responsibility**: Emit events to the unified stream

| Producer | Event Types | Integration Method |
|----------|-------------|-------------------|
| Claude Code Hooks | `hook.*`, `lifecycle.*`, `activity.*` | `.claude/hooks/*.sh` scripts |
| Git Operations | `git.*` | Git hooks (pre-commit, post-commit, etc.) |
| Backlog.md | `task.*` | Git hook + file watcher |
| Actions | `action.*` | Direct function calls in code |
| Decisions | `decision.*` | Agent reasoning loops |
| Containers | `container.*` | Docker event listeners |
| System | `system.*` | Periodic heartbeat, config changes |

**Emit Function Signature**:
```python
def emit_event(
    event_type: str,
    agent_id: str,
    message: str = None,
    context: dict = None,
    correlation: dict = None,
    **kwargs
) -> dict:
    """Emit event to unified JSONL stream."""
    pass
```

#### 2.1.2 Event Router

**Responsibility**: Route events to appropriate consumers based on event type

Routing Rules:
- All events → `events-{date}.jsonl` (main log)
- `decision.*` → `decision-log.jsonl` (filtered view)
- Events with `context.task_id` → `task-{id}/events.jsonl` (per-task view)
- Events with `correlation.trace_id` → `traces/{trace-id}.jsonl` (trace view)

**Implementation**: Simple namespace-based routing in Python/Bash

#### 2.1.3 Event Store

**Responsibility**: Persist events to JSONL files

Storage Strategy:
```
.flowspec/events/
├── main/
│   ├── events-2025-12-13.jsonl       # Daily main log
│   ├── events-2025-12-14.jsonl
│   └── ...
├── decisions/
│   └── decision-log.jsonl            # Filtered: decision.* only
├── tasks/
│   ├── task-123/
│   │   └── events.jsonl              # Filtered: context.task_id == task-123
│   └── task-124/
│       └── events.jsonl
└── traces/
    ├── trace-abc123/
    │   └── trace.jsonl               # Filtered: correlation.trace_id == trace-abc123
    └── trace-xyz789/
        └── trace.jsonl
```

**Rotation Policy**:
- Daily rotation for main log (configurable)
- Archive logs older than 90 days (configurable)
- Compress archived logs with gzip

#### 2.1.4 Event Consumers

**Responsibility**: Query, analyze, and act on events

| Consumer | Purpose | Implementation |
|----------|---------|----------------|
| CLI Query Tool | Ad-hoc event queries | `specify events query` command |
| Dashboard | Real-time visualization | Web UI (future) |
| State Machine | Workflow automation | Event-driven transitions |
| Analytics | Metrics and reporting | jq scripts, analytics tool |
| Alerting | Anomaly detection | Pattern matching rules |

### 2.2 Integration Patterns (Enterprise Integration Patterns)

#### 2.2.1 Message Channels

| Channel Type | Implementation | Purpose |
|--------------|----------------|---------|
| **Point-to-Point** | JSONL file append | Main event stream |
| **Publish-Subscribe** | File watchers + routing | Real-time consumers |
| **Dead Letter** | `events-failed.jsonl` | Failed event emission |

#### 2.2.2 Message Routing

| Pattern | Usage | Example |
|---------|-------|---------|
| **Content-Based Router** | Route by `event_type` namespace | `git.*` → git consumer |
| **Message Filter** | Filter by context fields | `context.task_id == "task-123"` |
| **Splitter** | Split compound events | Multi-step action → multiple events |

#### 2.2.3 Message Transformation

| Transformation | Input | Output |
|----------------|-------|--------|
| **Hook → Event** | Claude Code hook payload | Unified event schema |
| **Git → Event** | Git hook environment vars | `git.*` event |
| **Backlog → Event** | Task file diff | `task.*` event |

### 2.3 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        EVENT LIFECYCLE                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. EVENT GENERATION                                                 │
│     ┌──────────┐                                                     │
│     │ Producer │──► emit_event(type, agent_id, **kwargs)            │
│     └──────────┘                                                     │
│          │                                                           │
│          ▼                                                           │
│  2. SCHEMA VALIDATION                                                │
│     ┌────────────────┐                                               │
│     │ JSON Schema    │──► Validate against event-v1.1.0.json        │
│     │ Validator      │                                               │
│     └────────────────┘                                               │
│          │                                                           │
│          ▼                                                           │
│  3. ENRICHMENT                                                       │
│     ┌────────────────┐                                               │
│     │ Add: event_id, │──► UUID, timestamp, correlation if missing   │
│     │ timestamp, etc │                                               │
│     └────────────────┘                                               │
│          │                                                           │
│          ▼                                                           │
│  4. ROUTING                                                          │
│     ┌────────────────┐                                               │
│     │ Event Router   │──► Route to main + filtered views            │
│     └────────────────┘                                               │
│          │                                                           │
│          ▼                                                           │
│  5. PERSISTENCE                                                      │
│     ┌────────────────┐                                               │
│     │ Append to      │──► Write to events-{date}.jsonl (atomic)     │
│     │ JSONL          │                                               │
│     └────────────────┘                                               │
│          │                                                           │
│          ▼                                                           │
│  6. NOTIFICATION (optional)                                          │
│     ┌────────────────┐                                               │
│     │ Notify watchers│──► File watcher, webhook, MCP server         │
│     └────────────────┘                                               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.4 Correlation Strategy

**Purpose**: Trace events across distributed workflows (multi-agent, multi-container)

**Implementation**: OpenTelemetry-inspired correlation object

```json
{
  "correlation": {
    "trace_id": "trace-abc123",        // Entire workflow
    "span_id": "span-001",              // This specific operation
    "parent_span_id": "span-000",       // Parent operation
    "root_agent_id": "@orchestrator"    // Root agent
  }
}
```

**Trace Propagation**:
1. Root agent generates `trace_id` on workflow start
2. Each agent/action creates new `span_id`
3. Child operations inherit `trace_id` and set `parent_span_id`
4. Query traces: `jq 'select(.correlation.trace_id == "trace-abc123")' events.jsonl`

### 2.5 State Machine Implementation

**Git Workflow State Machine** (from git-workflow-objectives.md):

```python
class GitWorkflowStateMachine:
    """Event-driven state machine for git workflow."""

    STATES = [
        "IDLE", "TASK_READY", "BRANCH_READY", "WORKTREE_READY",
        "CONTAINER_READY", "AGENT_WORKING", "AWAITING_APPROVAL",
        "APPROVED", "PUSHED", "PR_OPEN", "MERGED", "DONE", "CLEANED_UP"
    ]

    TRANSITIONS = {
        "task.created": ("IDLE", "TASK_READY"),
        "git.branch_created": ("TASK_READY", "BRANCH_READY"),
        "git.worktree_created": ("BRANCH_READY", "WORKTREE_READY"),
        "container.started": ("WORKTREE_READY", "CONTAINER_READY"),
        "lifecycle.started": ("CONTAINER_READY", "AGENT_WORKING"),
        "git.local_pr_submitted": ("AGENT_WORKING", "AWAITING_APPROVAL"),
        "git.local_pr_rejected": ("AWAITING_APPROVAL", "AGENT_WORKING"),
        "git.local_pr_approved": ("AWAITING_APPROVAL", "APPROVED"),
        "git.pushed": ("APPROVED", "PUSHED"),
        "git.pr_created": ("PUSHED", "PR_OPEN"),
        "git.merged": ("PR_OPEN", "MERGED"),
        "task.completed": ("MERGED", "DONE"),
        # Cleanup transition accepts compound event
        "cleanup": ("DONE", "CLEANED_UP"),
    }

    def transition(self, event: dict) -> str:
        """Process event and return new state."""
        event_type = event["event_type"]
        current_state = self.get_current_state(event["context"]["task_id"])

        if event_type in self.TRANSITIONS:
            expected_from, to_state = self.TRANSITIONS[event_type]
            if current_state == expected_from:
                self.set_state(event["context"]["task_id"], to_state)
                return to_state
            else:
                raise InvalidTransitionError(
                    f"Cannot transition from {current_state} via {event_type}"
                )

        return current_state
```

---

## 3. Architecture Decision Records (ADRs) Needed

These ADRs should be created as separate tasks:

### ADR-001: Event Storage Strategy

**Decision Question**: Should events be stored in local JSONL files, a centralized database, or both?

**Context**:
- JSONL is simple, git-friendly, human-readable
- Database enables complex queries, real-time dashboards
- Hybrid approach increases complexity

**Proposed Decision**: **Local JSONL with optional database sync**
- Primary storage: JSONL files (`.flowspec/events/`)
- Optional: Sync to SQLite/PostgreSQL for advanced queries
- Migration path to database preserves existing JSONL files

**Lock-in Assessment**:
- **Type**: Two-way door
- **Reversal Cost**: Low - JSONL is portable, can switch databases
- **Lock-in Factors**: None - schema-driven, not database-specific

### ADR-002: Event Validation Approach

**Decision Question**: When should event validation occur - at emit time or async processing?

**Context**:
- Emit-time validation catches errors early but impacts performance
- Async validation allows faster writes but errors discovered late
- Invalid events corrupt the stream if not caught

**Proposed Decision**: **Emit-time validation with optional bypass**
- Default: Validate against JSON Schema before writing
- Flag `--skip-validation` for trusted producers (e.g., system)
- Async validator runs periodically to catch schema drift

**Lock-in Assessment**:
- **Type**: Two-way door
- **Reversal Cost**: Trivial - validation can be toggled
- **Lock-in Factors**: JSON Schema dependency (standard)

### ADR-003: Correlation and Tracing Strategy

**Decision Question**: How to implement distributed tracing - OpenTelemetry, custom, or hybrid?

**Context**:
- OpenTelemetry is industry standard, rich ecosystem
- Custom solution avoids heavy dependencies
- Hybrid uses OTEL concepts but simpler implementation

**Proposed Decision**: **OTEL-inspired custom implementation**
- Use OTEL concepts: `trace_id`, `span_id`, `parent_span_id`
- Lightweight implementation without OTEL SDK
- Compatible with OTEL exporters (future)

**Lock-in Assessment**:
- **Type**: Two-way door
- **Reversal Cost**: Low - can migrate to full OTEL later
- **Lock-in Factors**: None - compatible with OTEL

### ADR-004: Action-Event Mapping Implementation

**Decision Question**: Should action invocations automatically emit events, or require explicit emission?

**Context**:
- Automatic emission ensures consistency but couples code
- Explicit emission provides control but risks missed events
- Decorator pattern could provide middle ground

**Proposed Decision**: **Decorator-based automatic emission**
- Action functions decorated with `@emits_events`
- Decorator handles `action.invoked`, `action.succeeded/failed`
- Side-effect events emitted explicitly in action body

**Lock-in Assessment**:
- **Type**: Two-way door
- **Reversal Cost**: Medium - requires refactoring action functions
- **Lock-in Factors**: Decorator pattern (Python idiom)

### ADR-005: State Machine Implementation Approach

**Decision Question**: How to implement state machines - in-process, event-driven, or external engine?

**Context**:
- In-process: Simple but no persistence
- Event-driven: Reconstructable from event stream
- External engine: Complex but powerful

**Proposed Decision**: **Event-driven with state reconstruction**
- State derived by replaying events from stream
- No separate state storage
- Idempotent transitions allow replay

**Lock-in Assessment**:
- **Type**: One-way door (somewhat)
- **Reversal Cost**: Medium - changing requires state migration
- **Lock-in Factors**: Event sourcing pattern

---

## 4. Platform Quality Assessment (7 C's)

### 4.1 Clarity

**Assessment**: ✅ STRONG

- Event taxonomy is well-structured (11 namespaces, 60 event types)
- Clear naming convention: `namespace.action`
- JSON Schema provides unambiguous contract
- Comprehensive documentation

**Gaps**:
- Need glossary of terms (trace, span, context, correlation)
- Examples needed for each event type

### 4.2 Consistency

**Assessment**: ✅ STRONG

- Consistent field naming (`agent_id`, `event_type`, `timestamp`)
- Uniform namespacing across all event types
- Standard context object for cross-referencing
- Correlation object follows OpenTelemetry conventions

**Gaps**:
- Some legacy `status` field creates inconsistency (backward compat)
- Need linter to enforce naming conventions

### 4.3 Compliance

**Assessment**: ✅ STRONG

- Complete audit trail for all operations
- Decision tracking with reversibility assessment
- GPG signing for agent attribution
- SLSA attestation support in security events

**Gaps**:
- Need retention policy documentation
- Compliance reporting queries not yet documented

### 4.4 Composability

**Assessment**: ⚠️ MODERATE

- JSONL format is universally parsable
- Event types can be consumed independently
- Routing allows filtered views
- Correlation enables composable workflows

**Gaps**:
- No standard event aggregation patterns
- Cross-repo event correlation undefined

### 4.5 Coverage

**Assessment**: ✅ STRONG

- 60 event types across 11 namespaces
- 55+ actions mapped to events
- Git workflow fully covered (worktree, PR, containers)
- Decision lifecycle fully covered

**Gaps**:
- CI/CD events not yet defined
- Deployment events need expansion
- Monitoring/alerting events missing

### 4.6 Consumption

**Assessment**: ⚠️ MODERATE

- Emit function is simple (5 lines)
- jq queries are powerful but require learning curve
- No high-level query API yet

**Gaps**:
- Need CLI tool: `specify events query`
- Need helper functions for common queries
- Dashboard/UI for visualization

### 4.7 Credibility

**Assessment**: ✅ STRONG

- Event sourcing is proven pattern
- JSONL is battle-tested format
- JSON Schema validation ensures reliability
- Atomic append-only writes prevent corruption

**Gaps**:
- Need performance benchmarks
- Need reliability metrics (uptime, event loss rate)

**Overall Assessment**: **STRONG** (5/7 strong, 2/7 moderate)

---

## 5. Task Breakdown Structure

### Phase 1: Foundation (Weeks 1-2)

#### Task 1.1: Implement Core Event Schema
**Description**: Implement JSON Schema validation and event emission utilities

**Dependencies**: None

**Acceptance Criteria**:
1. JSON Schema file `event-v1.1.0.json` created and matches spec
2. Python function `validate_event(event: dict) -> bool` implemented
3. Python function `emit_event(event_type, agent_id, **kwargs) -> dict` implemented
4. Unit tests for validation (valid events, invalid events, edge cases)
5. Documentation in `docs/guides/event-schema.md`

**Labels**: architecture, foundation, schema
**Priority**: HIGH
**Complexity**: M

---

#### Task 1.2: Create JSONL Event Writer Utility
**Description**: Implement atomic append-only JSONL writer with rotation

**Dependencies**: Task 1.1

**Acceptance Criteria**:
1. Function `append_event(event: dict, filepath: str) -> bool` with atomic writes
2. Daily log rotation implemented (configurable)
3. Archive old logs (compress with gzip)
4. Handle concurrent writes safely (file locking)
5. Unit tests for writer (concurrent writes, rotation, archival)

**Labels**: architecture, foundation, storage
**Priority**: HIGH
**Complexity**: M

---

#### Task 1.3: Implement Event Router
**Description**: Route events to filtered views (decisions, tasks, traces)

**Dependencies**: Task 1.2

**Acceptance Criteria**:
1. Route `decision.*` events to `decision-log.jsonl`
2. Route events with `context.task_id` to `tasks/{id}/events.jsonl`
3. Route events with `correlation.trace_id` to `traces/{id}/trace.jsonl`
4. Configurable routing rules in `event-routing.yml`
5. Unit tests for routing logic

**Labels**: architecture, foundation, routing
**Priority**: MEDIUM
**Complexity**: M

---

#### Task 1.4: Create Event Query CLI
**Description**: Implement `specify events query` command for ad-hoc queries

**Dependencies**: Task 1.2

**Acceptance Criteria**:
1. `specify events query --task task-123` returns all events for task
2. `specify events query --agent @backend-engineer` returns agent events
3. `specify events query --type git.commit` returns all commits
4. `specify events query --trace trace-abc123` returns trace
5. Support output formats: json, table, timeline

**Labels**: implementation, cli, tooling
**Priority**: MEDIUM
**Complexity**: L

---

### Phase 2: Event Emission Integration (Week 3)

#### Task 2.1: Implement Claude Hook Event Emission
**Description**: Emit events from Claude Code hooks (10 hook types)

**Dependencies**: Task 1.2

**Acceptance Criteria**:
1. All 10 hook types emit corresponding `hook.*` events
2. Hook payloads preserved in `hook.raw_payload`
3. Session ID tracked across hook invocations
4. Correlation IDs assigned to sessions
5. Integration tests for each hook type

**Labels**: implementation, hooks, integration
**Priority**: HIGH
**Complexity**: L

---

#### Task 2.2: Implement Backlog Task Event Emission (Git Hook)
**Description**: Git hook to emit `task.*` events on task file changes

**Dependencies**: Task 1.2, Task-204.01 (existing)

**Acceptance Criteria**:
1. Pre-commit hook detects changes to `backlog/tasks/*.md`
2. Parse task file diff to extract state changes
3. Emit `task.created`, `task.state_changed`, `task.completed` events
4. Emit `task.ac_checked` when AC checkbox changes
5. Integration tests with mock git repo

**Labels**: implementation, hooks, integration
**Priority**: HIGH
**Complexity**: M

---

#### Task 2.3: Implement Git Operation Event Emission
**Description**: Git hooks to emit `git.*` events for commits, branches, etc.

**Dependencies**: Task 1.2

**Acceptance Criteria**:
1. Post-commit hook emits `git.commit` with GPG info
2. Post-branch hook emits `git.branch_created`
3. Pre-push hook can emit `git.local_pr_submitted` (optional)
4. Post-merge hook emits `git.merged`
5. Integration tests with test git repo

**Labels**: implementation, hooks, git
**Priority**: HIGH
**Complexity**: M

---

### Phase 3: Action System (Week 4)

#### Task 3.1: Implement Action Vocabulary
**Description**: Create action registry with 55+ actions from action-system.md

**Dependencies**: Task 1.1

**Acceptance Criteria**:
1. Action registry data structure (verb, domain, category, etc.)
2. All 55 actions defined in `actions-registry.json`
3. Validation: action exists in registry before invocation
4. Query function: `get_actions_by_category(category)`
5. Unit tests for registry queries

**Labels**: architecture, action-system
**Priority**: MEDIUM
**Complexity**: M

---

#### Task 3.2: Implement Action Decorator for Event Emission
**Description**: `@emits_events` decorator to auto-emit action lifecycle events

**Dependencies**: Task 3.1, Task 1.2

**Acceptance Criteria**:
1. Decorator emits `action.invoked` on function entry
2. Decorator emits `action.succeeded` on normal return
3. Decorator emits `action.failed` on exception
4. Decorator emits `action.aborted` on SIGINT/SIGTERM
5. Function can emit side-effect events explicitly

**Labels**: implementation, action-system
**Priority**: MEDIUM
**Complexity**: L

---

#### Task 3.3: Implement Allowed Followups Validation
**Description**: Validate action sequences against allowed followups graph

**Dependencies**: Task 3.1

**Acceptance Criteria**:
1. Allowed followups graph loaded from `action-system.md`
2. Function `validate_followup(prev_action, next_action) -> bool`
3. Warning emitted if invalid followup attempted
4. Configurable: strict mode (reject) vs warning mode
5. Unit tests for validation logic

**Labels**: implementation, action-system, validation
**Priority**: LOW
**Complexity**: M

---

### Phase 4: Git Workflow (Week 5)

#### Task 4.1: Implement Git Worktree Management
**Description**: Create/remove worktrees with event emission

**Dependencies**: Task 2.3

**Acceptance Criteria**:
1. Function `create_worktree(task_id, branch_name) -> worktree_path`
2. Emit `git.branch_created` and `git.worktree_created` events
3. Function `remove_worktree(worktree_path, delete_branch=False)`
4. Emit `git.worktree_removed` event
5. Integration tests with git repo

**Labels**: implementation, git-workflow
**Priority**: HIGH
**Complexity**: M

---

#### Task 4.2: Implement Local PR Quality Gates
**Description**: Pre-push hook with lint, test, SAST checks

**Dependencies**: Task 2.3

**Acceptance Criteria**:
1. Pre-push hook runs lint, test, SAST (configurable)
2. Emit `git.local_pr_submitted` event
3. Emit `git.local_pr_approved` if all checks pass
4. Emit `git.local_pr_rejected` if any check fails
5. Support approval modes: auto, human_required, agent_review

**Labels**: implementation, git-workflow, quality
**Priority**: HIGH
**Complexity**: L

---

#### Task 4.3: Implement Agent GPG Signing
**Description**: GPG sign commits with agent-specific keys

**Dependencies**: Task 2.3

**Acceptance Criteria**:
1. Generate GPG key for agent (if not exists)
2. Configure git to use agent's GPG key for signing
3. Commit event includes `git.gpg_key_id` and `git.signer_agent_id`
4. Support co-authored commits (multiple agents)
5. Documentation for key management

**Labels**: implementation, git-workflow, security
**Priority**: MEDIUM
**Complexity**: M

---

### Phase 5: Container Integration (Week 6)

#### Task 5.1: Implement Container Lifecycle Events
**Description**: Emit events for container start/stop/resource limits

**Dependencies**: Task 1.2

**Acceptance Criteria**:
1. Emit `container.started` with image, resource limits, network mode
2. Emit `container.secrets_injected` (secret names only, never values!)
3. Emit `container.resource_limit_hit` if resource exhaustion
4. Emit `container.stopped` with exit code
5. Integration tests with Docker

**Labels**: implementation, container, security
**Priority**: MEDIUM
**Complexity**: M

---

#### Task 5.2: Implement Devcontainer Isolation
**Description**: Run agents in devcontainers with secret injection

**Dependencies**: Task 5.1

**Acceptance Criteria**:
1. Spawn devcontainer from `.devcontainer/devcontainer.json`
2. Inject secrets at runtime (never baked into image)
3. Mount worktree as volume
4. Emit `container.agent_attached` when agent starts in container
5. Documentation for devcontainer setup

**Labels**: implementation, container, security
**Priority**: MEDIUM
**Complexity**: L

---

### Phase 6: Decision Tracking (Week 7)

#### Task 6.1: Implement Decision Event Emission
**Description**: Helper functions for emitting decision events

**Dependencies**: Task 1.2

**Acceptance Criteria**:
1. Function `emit_decision(decision_id, category, reversibility, **kwargs)`
2. Support all decision categories (architecture, technology, etc.)
3. Reversibility assessment helper (prompts for lock-in factors)
4. Emit `decision.made` with supporting material links
5. Unit tests for decision emission

**Labels**: implementation, decision-tracker
**Priority**: MEDIUM
**Complexity**: S

---

#### Task 6.2: Implement Decision Query Utilities
**Description**: CLI queries for decisions (one-way doors, by category, etc.)

**Dependencies**: Task 6.1, Task 1.4

**Acceptance Criteria**:
1. `specify decisions list --category architecture`
2. `specify decisions list --one-way-doors`
3. `specify decisions list --task task-123`
4. `specify decisions show ARCH-001` (detailed view)
5. Support output formats: json, table, markdown

**Labels**: implementation, decision-tracker, cli
**Priority**: LOW
**Complexity**: S

---

### Phase 7: State Machine & Automation (Week 8)

#### Task 7.1: Implement Git Workflow State Machine
**Description**: Event-driven state machine for git workflow lifecycle

**Dependencies**: Task 1.4, Task 4.1, Task 4.2

**Acceptance Criteria**:
1. State machine tracks workflow states (IDLE → CLEANED_UP)
2. Process events to transition states
3. Validate transitions (reject invalid state changes)
4. Reconstruct state by replaying events
5. Unit tests for state machine logic

**Labels**: architecture, state-machine, git-workflow
**Priority**: MEDIUM
**Complexity**: L

---

#### Task 7.2: Implement Automated Cleanup Workflow
**Description**: Auto-cleanup worktrees/containers on task completion

**Dependencies**: Task 7.1, Task 4.1, Task 5.1

**Acceptance Criteria**:
1. Listen for `task.completed` or `task.archived` events
2. Trigger `remove_worktree` and `destroy_container` actions
3. Emit cleanup events (`git.worktree_removed`, `container.stopped`)
4. Handle errors gracefully (already cleaned, missing worktree)
5. Integration tests with event stream

**Labels**: implementation, automation, git-workflow
**Priority**: MEDIUM
**Complexity**: M

---

### Phase 8: Documentation & Testing (Week 9)

#### Task 8.1: Write Comprehensive Documentation
**Description**: User guides, architecture docs, troubleshooting

**Dependencies**: All implementation tasks

**Acceptance Criteria**:
1. Architecture overview (`docs/architecture/event-system-overview.md`)
2. User guide (`docs/guides/event-system-user-guide.md`)
3. Developer guide (`docs/guides/event-system-developer-guide.md`)
4. Troubleshooting guide (`docs/guides/event-system-troubleshooting.md`)
5. API reference (`docs/reference/event-api.md`)

**Labels**: documentation
**Priority**: HIGH
**Complexity**: M

---

#### Task 8.2: Create Integration Test Suite
**Description**: End-to-end tests for complete workflows

**Dependencies**: All implementation tasks

**Acceptance Criteria**:
1. Test: Task creation → worktree → commit → local PR → merge → cleanup
2. Test: Multi-agent collaboration with correlation IDs
3. Test: Decision tracking with reversibility assessment
4. Test: Container lifecycle with secret injection
5. All tests pass in CI/CD

**Labels**: testing, integration
**Priority**: HIGH
**Complexity**: L

---

#### Task 8.3: Performance Benchmarking
**Description**: Measure event emission overhead and throughput

**Dependencies**: Task 8.2

**Acceptance Criteria**:
1. Benchmark: Event emission latency (p50, p95, p99)
2. Benchmark: Throughput (events/second)
3. Benchmark: Storage growth rate (events/day)
4. Benchmark: Query performance (jq, SQLite)
5. Document results in `docs/performance/benchmarks.md`

**Labels**: testing, performance
**Priority**: LOW
**Complexity**: S

---

## 6. Execution Order & Dependencies

```
Phase 1: Foundation
  1.1 (Schema) ──┬──► 1.2 (Writer) ──┬──► 1.3 (Router)
                 │                    │
                 └────────────────────┴──► 1.4 (Query CLI)

Phase 2: Event Emission
  1.2 ──► 2.1 (Hooks) ──┐
       └► 2.2 (Backlog)─┼──► [All Phase 2 tasks independent]
       └► 2.3 (Git)    ─┘

Phase 3: Action System
  1.1 ──► 3.1 (Registry) ──┬──► 3.2 (Decorator)
       └─────────────────┴──► 3.3 (Validation)

Phase 4: Git Workflow
  2.3 ──► 4.1 (Worktree) ──┬──► [Independent]
       └► 4.2 (Local PR)  ─┼──► [Independent]
       └► 4.3 (GPG Sign)  ─┘

Phase 5: Container Integration
  1.2 ──► 5.1 (Lifecycle) ──► 5.2 (Devcontainer)

Phase 6: Decision Tracking
  1.2 ──┬──► 6.1 (Emission) ──► 6.2 (Query)
  1.4 ──┘

Phase 7: State Machine & Automation
  [1.4, 4.1, 4.2] ──► 7.1 (State Machine) ──┐
  [7.1, 4.1, 5.1] ──────────────────────────┴──► 7.2 (Cleanup)

Phase 8: Documentation & Testing
  [All tasks] ──► 8.1 (Docs) ──┬──► 8.2 (Integration Tests) ──► 8.3 (Benchmarks)
```

---

## 7. Risk Mitigation Strategies

### 7.1 Event Schema Drift

**Risk**: Schema changes break existing consumers

**Mitigation**:
1. Strict semver versioning for schema (`version: "1.1.0"`)
2. Schema validation enforced at emit time
3. Backward compatibility: old events remain valid
4. Migration scripts for major version changes

### 7.2 Event Log Growth

**Risk**: Unbounded log growth consumes disk space

**Mitigation**:
1. Daily log rotation (configurable interval)
2. Archive logs older than 90 days (configurable)
3. Compress archived logs (gzip, 80% reduction)
4. Monitoring alerts for disk usage

### 7.3 Integration Complexity

**Risk**: Wrapping existing tools (backlog.md, git) is fragile

**Mitigation**:
1. Wrapper scripts with clear error handling
2. Fallback to manual event emission if automation fails
3. Integration tests to catch breakage early
4. Documentation for manual workarounds

### 7.4 Performance Overhead

**Risk**: Event emission adds latency to operations

**Mitigation**:
1. Async event writes (non-blocking)
2. Batch writes for high-volume producers
3. Benchmark and document overhead (<10ms target)
4. Optional bypass flag for performance-critical paths

### 7.5 Adoption Resistance

**Risk**: Developers resist event-first design

**Mitigation**:
1. Clear documentation with examples
2. Helper utilities for common patterns
3. Gradual rollout (opt-in initially)
4. Success stories from early adopters

---

## 8. Open Questions

### Q1: Event Storage Location
**Question**: Should events be per-worktree, per-repo, or centralized?

**Options**:
- **Per-worktree**: Isolated but fragmented
- **Per-repo**: Single source of truth, but large files
- **Centralized**: Across all repos, requires infrastructure

**Recommendation**: **Per-repo** with optional centralized sync (Phase 9+)

---

### Q2: Event Retention Policy
**Question**: How long to keep events? Archive strategy?

**Options**:
- **Short (30 days)**: Minimal disk usage, lose history
- **Medium (90 days)**: Balance history vs disk
- **Long (1 year+)**: Complete history, high disk usage

**Recommendation**: **90 days active + compress/archive older** (configurable)

---

### Q3: Real-Time Streaming
**Question**: Support real-time event streaming (WebSocket/SSE)?

**Options**:
- **Not needed**: jq queries are sufficient
- **Nice to have**: Dashboard/monitoring use case
- **Critical**: Multi-agent coordination requires it

**Recommendation**: **Nice to have** - defer to Phase 9+ (post-MVP)

---

### Q4: Cross-Repo Correlation
**Question**: How to correlate events across multiple repositories?

**Options**:
- **Not supported**: Each repo independent
- **Shared trace IDs**: Manual coordination
- **Centralized event store**: All repos write to central location

**Recommendation**: **Shared trace IDs** - simple, sufficient for now

---

## 9. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Event Coverage | 100% of operations emit events | Code coverage analysis |
| Event Loss Rate | <0.1% | Compare expected vs actual events |
| Emit Latency (p95) | <10ms | Benchmark suite |
| Query Performance | <1s for 10k events | jq benchmarks |
| Developer Adoption | 80% of new code uses events | Code review metrics |
| Bug Detection | 20% faster via event analysis | Time-to-resolution |

---

## 10. Future Enhancements (Phase 9+)

1. **Real-time Dashboard**: Web UI for live event visualization
2. **Centralized Event Store**: SQLite/PostgreSQL for advanced queries
3. **Alerting & Anomalies**: Pattern-based alerts (e.g., stuck workflows)
4. **Cross-Repo Correlation**: Centralized trace aggregation
5. **Event Replay**: Replay events to reproduce bugs
6. **Metrics & Analytics**: Aggregate metrics (agent productivity, workflow duration)
7. **Integration with agent-updates-collector**: Dual ingestion (MCP + file watcher)

---

## Appendix A: Complete Task List

### Foundation (Phase 1)
- [ ] Task 1.1: Implement Core Event Schema (HIGH, M)
- [ ] Task 1.2: Create JSONL Event Writer Utility (HIGH, M)
- [ ] Task 1.3: Implement Event Router (MEDIUM, M)
- [ ] Task 1.4: Create Event Query CLI (MEDIUM, L)

### Event Emission (Phase 2)
- [ ] Task 2.1: Implement Claude Hook Event Emission (HIGH, L)
- [ ] Task 2.2: Implement Backlog Task Event Emission (HIGH, M)
- [ ] Task 2.3: Implement Git Operation Event Emission (HIGH, M)

### Action System (Phase 3)
- [ ] Task 3.1: Implement Action Vocabulary (MEDIUM, M)
- [ ] Task 3.2: Implement Action Decorator for Event Emission (MEDIUM, L)
- [ ] Task 3.3: Implement Allowed Followups Validation (LOW, M)

### Git Workflow (Phase 4)
- [ ] Task 4.1: Implement Git Worktree Management (HIGH, M)
- [ ] Task 4.2: Implement Local PR Quality Gates (HIGH, L)
- [ ] Task 4.3: Implement Agent GPG Signing (MEDIUM, M)

### Container Integration (Phase 5)
- [ ] Task 5.1: Implement Container Lifecycle Events (MEDIUM, M)
- [ ] Task 5.2: Implement Devcontainer Isolation (MEDIUM, L)

### Decision Tracking (Phase 6)
- [ ] Task 6.1: Implement Decision Event Emission (MEDIUM, S)
- [ ] Task 6.2: Implement Decision Query Utilities (LOW, S)

### State Machine & Automation (Phase 7)
- [ ] Task 7.1: Implement Git Workflow State Machine (MEDIUM, L)
- [ ] Task 7.2: Implement Automated Cleanup Workflow (MEDIUM, M)

### Documentation & Testing (Phase 8)
- [ ] Task 8.1: Write Comprehensive Documentation (HIGH, M)
- [ ] Task 8.2: Create Integration Test Suite (HIGH, L)
- [ ] Task 8.3: Performance Benchmarking (LOW, S)

**Total Tasks**: 22
**Total Estimated Effort**: ~8 weeks (1 developer)

---

## Appendix B: Related Documents

- [JSONL Event System Specification](jsonl-event-system.md)
- [Action & Event System](action-system.md)
- [Decision Tracker](decision-tracker.md)
- [Git Workflow Objectives](git-workflow-objectives.md)

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-12-13 | @galway | Initial architecture specification |
