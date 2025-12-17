# Decision Tracker

A lightweight system for logging architectural, technical, and process decisions throughout a project's lifecycle using the unified [JSONL Event System](jsonl-event-system.md).

## Purpose

Track decisions to:
- **Preserve context** - Why was this choice made? What alternatives existed?
- **Identify lock-in** - Which decisions are one-way doors vs easily reversible?
- **Trace implications** - What downstream effects and dependencies result?
- **Enable onboarding** - New team members can understand the decision history
- **Support auditing** - Compliance and security reviews have documented rationale
- **Correlate with work** - Link decisions to tasks, branches, and agents

## Integration with JSONL Event System

**Decisions are events.** This document describes the decision-specific schema that lives within the unified [JSONL Event System](jsonl-event-system.md).

### Event Types for Decisions

| Event Type | Description | When Emitted |
|------------|-------------|--------------|
| `decision.made` | A decision was recorded | After reasoning |
| `decision.rationale` | Extended reasoning | Complex decisions |
| `decision.rejected` | Option rejected | Alternative considered |

### Decision Event Structure

A decision is a standard event with `event_type: "decision.*"` and a `decision` object:

```json
{
  "version": "1.1.0",
  "event_type": "decision.made",
  "timestamp": "2024-12-13T16:00:00Z",
  "agent_id": "@architect",
  "message": "Adopt event sourcing for order management",
  "context": {
    "task_id": "task-45",
    "branch_name": "task-45-order-service",
    "decision_id": "ARCH003"
  },
  "decision": {
    "decision_id": "ARCH003",
    "category": "architecture",
    "reversibility": {
      "type": "one-way-door",
      "lock_in_factors": ["schema design", "data migration", "team training"],
      "reversal_cost": "prohibitive",
      "reversal_window": "before first production order",
      "notes": "Once orders exist as events, migrating to CRUD would lose audit history"
    },
    "alternatives_considered": [
      {"option": "Traditional CRUD with audit table", "rejected_reason": "Audit table becomes bottleneck, doesn't capture intent"},
      {"option": "Database triggers for auditing", "rejected_reason": "Hidden complexity, hard to test, vendor-specific"}
    ],
    "supporting_material": {
      "links": [
        {"url": "https://martinfowler.com/eaaDev/EventSourcing.html", "title": "Martin Fowler on Event Sourcing", "type": "documentation"},
        {"url": "https://www.eventstore.com/blog/what-is-event-sourcing", "title": "EventStore Introduction", "type": "blog"}
      ],
      "internal_refs": ["specs/order-management.md", "adrs/ADR-007-event-sourcing.md"],
      "related_decisions": ["ARCH001", "SEC002"]
    }
  },
  "metadata": {
    "stakeholders": ["backend-team", "compliance", "finance"],
    "status": "accepted",
    "tags": ["event-sourcing", "compliance", "orders", "critical-path"]
  }
}
```

## File Format

Decisions live in the unified event stream (`events-{date}.jsonl`). For convenience, you can extract a decision-only view:

```bash
# Extract decision log from unified event stream
jq -c 'select(.event_type | startswith("decision."))' events.jsonl > decision-log.jsonl
```

This format is:
- Append-only friendly (no file parsing needed to add entries)
- Git diff friendly (changes show as single line additions)
- Easy to query with `jq`, `grep`, or scripts
- Importable into databases or analytics tools
- **Correlated** - Links to tasks, branches, and agents via `context`

## Quick Start

### Logging a Decision

Emit a decision event to the unified stream:

```json
{"version":"1.1.0","event_type":"decision.made","timestamp":"2024-12-13T15:00:00Z","agent_id":"@architect","message":"Use TypeScript for API server","context":{"task_id":"task-12","decision_id":"001"},"decision":{"decision_id":"001","category":"technology","reversibility":{"type":"two-way-door","reversal_cost":"medium"}},"metadata":{"rationale":"Type safety reduces runtime errors, team prefers static typing","outcome":"All backend code will be TypeScript with strict mode enabled"}}
```

### Required Fields

| Field | Location | Description |
|-------|----------|-------------|
| `version` | root | Schema version (e.g., `"1.1.0"`) |
| `event_type` | root | `"decision.made"`, `"decision.rationale"`, or `"decision.rejected"` |
| `timestamp` | root | ISO 8601 datetime |
| `agent_id` | root | Who made the decision (e.g., `"@architect"`, `"@human"`) |
| `decision.decision_id` | decision | Unique ID (e.g., `001`, `ARCH042`, `SEC003`) |
| `decision.category` | decision | Classification (see categories below) |

### Recommended Fields

| Field | Location | Description |
|-------|----------|-------------|
| `message` | root | What was decided (concise, <200 chars) |
| `context.task_id` | context | Link to related task |
| `context.branch_name` | context | Link to git branch |
| `metadata.rationale` | metadata | Why this choice was made |
| `metadata.outcome` | metadata | Expected or actual result |

### Categories

- `analysis` - Investigation findings and assessments
- `design` - UI/UX and system design choices
- `architecture` - Structural and component decisions
- `technology` - Tool, language, framework selections
- `integration` - How systems connect and communicate
- `migration` - Data or system migration strategies
- `security` - Security controls and policies
- `performance` - Optimization and scaling decisions
- `process` - Development workflow and methodology
- `organizational` - Team structure and responsibility
- `recommendations` - Suggested future actions
- `completion` - Milestone or phase completion markers
- `rollback` - Decisions to reverse previous choices

## One-Way Doors vs Two-Way Doors

**Critical concept**: Not all decisions are equal. Some are easily reversible (two-way doors), while others create significant lock-in (one-way doors).

### Identifying One-Way Doors

Ask these questions:
1. **Data commitment** - Does this create persistent data in a specific format?
2. **External contracts** - Does this expose an API or contract to external consumers?
3. **Vendor lock-in** - Does this tie us to a specific vendor's ecosystem?
4. **Team investment** - Does this require significant training or hiring?
5. **Infrastructure** - Does this require provisioning that's hard to undo?
6. **Regulatory** - Does this trigger compliance requirements?

### Lock-in Factors

Common lock-in factors to document:
- `vendor contract` - Legal/financial commitment
- `data migration` - Existing data in proprietary format
- `API exposure` - External consumers depend on interface
- `team training` - Significant skill investment
- `infrastructure provisioning` - Hardware or cloud resources
- `regulatory compliance` - Compliance certifications obtained
- `schema design` - Data structures baked into systems
- `integration coupling` - Deep integration with other systems

### Reversibility Assessment

```json
"decision": {
  "reversibility": {
    "type": "one-way-door",
    "lock_in_factors": ["data migration", "API exposure"],
    "reversal_cost": "high",
    "reversal_window": "before v1.0 launch",
    "notes": "After public API release, breaking changes require deprecation cycle"
  }
}
```

**Reversal cost levels:**
- `trivial` - Minutes of work, no user impact
- `low` - Hours of work, minimal coordination
- `medium` - Days of work, some user communication
- `high` - Weeks of work, significant coordination
- `prohibitive` - Months of work, may not be feasible

## Tracking Implications

Document the ripple effects of decisions in metadata:

```json
"metadata": {
  "implications": {
    "affected_components": ["api-server", "mobile-app", "admin-dashboard"],
    "dependencies_created": ["redis", "kafka"],
    "constraints_imposed": ["must maintain backward compatibility", "requires 99.9% uptime"],
    "follow_up_decisions": ["caching strategy", "failover approach"]
  }
}
```

## Supporting Material

Link to evidence, documentation, and related resources:

```json
"decision": {
  "supporting_material": {
    "links": [
      {"url": "https://example.com/benchmark", "title": "Performance benchmark results", "type": "benchmark"},
      {"url": "https://github.com/org/repo/issues/123", "title": "Original discussion", "type": "discussion"}
    ],
    "internal_refs": ["specs/api-design.md", "adrs/ADR-005.md"],
    "related_decisions": ["003", "007", "012"],
    "attachments": ["diagrams/architecture-v2.png"]
  }
}
```

**Link types:** `documentation`, `blog`, `paper`, `benchmark`, `discussion`, `issue`, `pr`, `adr`, `other`

## Alternatives Considered

Document rejected options to prevent revisiting settled debates:

```json
"decision": {
  "alternatives_considered": [
    {"option": "GraphQL API", "rejected_reason": "Team lacks expertise, overkill for current needs"},
    {"option": "gRPC", "rejected_reason": "Browser support requires proxy layer"}
  ]
}
```

Or emit separate `decision.rejected` events:

```json
{"version":"1.1.0","event_type":"decision.rejected","timestamp":"2024-12-13T15:00:00Z","agent_id":"@architect","message":"Rejected GraphQL API","context":{"decision_id":"001"},"metadata":{"option":"GraphQL API","rejected_reason":"Team lacks expertise, overkill for current needs"}}
```

## Decision Lifecycle

Decisions have a status tracked in metadata:
- `proposed` - Under consideration, not yet finalized
- `accepted` - Agreed upon, ready for implementation
- `implemented` - Actually in production/use
- `deprecated` - No longer recommended, but still in use
- `superseded` - Replaced by another decision

When superseding a decision:
```json
{"event_type": "decision.made", "context": {"decision_id": "089"}, "metadata": {"status": "accepted", "supersedes": "042"}}
```

And update the old decision:
```json
{"event_type": "decision.made", "context": {"decision_id": "042"}, "metadata": {"status": "superseded", "superseded_by": "089"}}
```

## Querying Decisions

### Using jq

```bash
# All architecture decisions
jq -c 'select(.event_type | startswith("decision.")) | select(.decision.category == "architecture")' events.jsonl

# One-way doors only
jq -c 'select(.decision.reversibility.type == "one-way-door")' events.jsonl

# Decisions with high reversal cost
jq -c 'select(.decision.reversibility.reversal_cost == "high" or .decision.reversibility.reversal_cost == "prohibitive")' events.jsonl

# Decisions for a specific task
jq -c 'select(.event_type | startswith("decision.")) | select(.context.task_id == "task-45")' events.jsonl

# Find by tag
jq -c 'select(.metadata.tags | index("security"))' events.jsonl

# Decisions affecting a component
jq -c 'select(.metadata.implications.affected_components | index("api-server"))' events.jsonl

# Decisions by agent
jq -c 'select(.event_type | startswith("decision.")) | select(.agent_id == "@architect")' events.jsonl
```

### Using grep

```bash
# Quick search
grep '"decision.made"' events.jsonl | grep "database"

# Count by category
grep '"decision.made"' events.jsonl | grep -o '"category":"[^"]*"' | sort | uniq -c
```

## Integration with Flowspec

In spec-driven development workflows, decisions are emitted at each stage:

| Flowspec Command | Decision Events |
|-----------------|-----------------|
| `/flow:assess` | `decision.made` - Assessment conclusions, SDD applicability |
| `/flow:specify` | `decision.made` - Functional design choices, scope decisions |
| `/flow:plan` | `decision.made` - Architecture and technology choices |
| `/flow:implement` | `decision.made` - Implementation approach, library selection |
| `/flow:validate` | `decision.made` - Review outcomes, quality gate decisions |
| `/flow:operate` | `decision.made` - Deployment strategy, scaling decisions |

### Automatic Logging

Agents should emit decision events when:
- Choosing between multiple valid approaches
- Selecting technologies, libraries, or tools
- Defining interfaces or contracts
- Making trade-offs (performance vs simplicity, etc.)
- Establishing conventions or patterns

Example from `@backend-engineer` during implementation:

```json
{"version":"1.1.0","event_type":"decision.made","timestamp":"2024-12-13T16:30:00Z","agent_id":"@backend-engineer","message":"Using SQLAlchemy 2.0 async engine","context":{"task_id":"task-45","branch_name":"task-45-database","decision_id":"IMPL-003"},"decision":{"decision_id":"IMPL-003","category":"technology","reversibility":{"type":"two-way-door","reversal_cost":"low"},"alternatives_considered":[{"option":"SQLAlchemy sync","rejected_reason":"Blocks event loop"},{"option":"Raw asyncpg","rejected_reason":"Too low-level, loses ORM benefits"}]}}
```

## Best Practices

1. **Log early, log often** - Better to over-document than under-document
2. **Be specific in rationale** - Future you will thank past you
3. **Always assess reversibility** - Flag one-way doors explicitly
4. **Link supporting evidence** - Don't just state opinions, cite sources
5. **Document alternatives** - Explain why other options were rejected
6. **Update status** - Emit new events when decisions are implemented or superseded
7. **Use consistent IDs** - Consider prefixes by domain (ARCH, SEC, PERF)
8. **Include context** - Always set `context.task_id` and `context.branch_name` when applicable
9. **Review periodically** - Revisit old decisions as context changes

## Schema Reference

The full decision schema is defined in [JSONL Event System - Decision Object](jsonl-event-system.md#decision-object).

Key schema elements:
- `decision.decision_id` - Unique identifier
- `decision.category` - Classification
- `decision.reversibility` - One-way/two-way door assessment
- `decision.alternatives_considered` - Rejected options
- `decision.supporting_material` - Links, refs, related decisions

## Migration from Standalone Format

If you have existing `decision-log.jsonl` files in the old format, migrate them to the unified format:

### Old Format (v1.0)
```json
{"timestamp": "2024-12-13T15:00:00Z", "decision_id": "001", "category": "technology", "decision": "Use TypeScript", "rationale": "Type safety", "outcome": "All backend TypeScript"}
```

### New Format (v1.1)
```json
{"version":"1.1.0","event_type":"decision.made","timestamp":"2024-12-13T15:00:00Z","agent_id":"@human","message":"Use TypeScript","context":{"decision_id":"001"},"decision":{"decision_id":"001","category":"technology"},"metadata":{"rationale":"Type safety","outcome":"All backend TypeScript"}}
```

Migration script:
```bash
# Convert old format to new format
jq -c '{
  version: "1.1.0",
  event_type: "decision.made",
  timestamp: .timestamp,
  agent_id: (.agent_id // "@human"),
  message: .decision,
  context: {decision_id: .decision_id},
  decision: {
    decision_id: .decision_id,
    category: .category,
    reversibility: .reversibility
  },
  metadata: {
    rationale: .rationale,
    outcome: .outcome,
    status: (.status // "accepted"),
    tags: .tags
  }
}' old-decision-log.jsonl > migrated-decisions.jsonl
```

## Example: Full Decision Entry

```json
{
  "version": "1.1.0",
  "event_type": "decision.made",
  "timestamp": "2024-12-13T16:00:00Z",
  "agent_id": "@architect",
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Adopt event sourcing for order management",
  "context": {
    "task_id": "task-45",
    "branch_name": "task-45-order-service",
    "decision_id": "ARCH003"
  },
  "decision": {
    "decision_id": "ARCH003",
    "category": "architecture",
    "reversibility": {
      "type": "one-way-door",
      "lock_in_factors": ["schema design", "data migration", "team training"],
      "reversal_cost": "prohibitive",
      "reversal_window": "before first production order",
      "notes": "Once orders exist as events, migrating to CRUD would lose audit history"
    },
    "alternatives_considered": [
      {"option": "Traditional CRUD with audit table", "rejected_reason": "Audit table becomes bottleneck, doesn't capture intent"},
      {"option": "Database triggers for auditing", "rejected_reason": "Hidden complexity, hard to test, vendor-specific"}
    ],
    "supporting_material": {
      "links": [
        {"url": "https://martinfowler.com/eaaDev/EventSourcing.html", "title": "Martin Fowler on Event Sourcing", "type": "documentation"},
        {"url": "https://www.eventstore.com/blog/what-is-event-sourcing", "title": "EventStore Introduction", "type": "blog"}
      ],
      "internal_refs": ["specs/order-management.md", "adrs/ADR-007-event-sourcing.md"],
      "related_decisions": ["ARCH001", "SEC002"]
    }
  },
  "metadata": {
    "stakeholders": ["backend-team", "compliance", "finance"],
    "status": "accepted",
    "tags": ["event-sourcing", "compliance", "orders", "critical-path"],
    "implications": {
      "affected_components": ["order-service", "billing", "reporting", "admin-tools"],
      "dependencies_created": ["event-store", "projection-service"],
      "constraints_imposed": ["events are immutable", "must version event schemas"],
      "follow_up_decisions": ["event schema versioning strategy", "projection rebuild process"]
    }
  },
  "correlation": {
    "trace_id": "trace-abc123",
    "span_id": "span-005"
  }
}
```

## Related Documents

- [JSONL Event System](jsonl-event-system.md) - Unified event schema
- [Git Workflow Objectives](git-workflow-objectives.md) - Git workflow with event integration
