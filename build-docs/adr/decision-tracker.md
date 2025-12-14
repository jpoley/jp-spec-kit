# Decision Tracker

A lightweight system for logging architectural, technical, and process decisions throughout a project's lifecycle using a JSONL (JSON Lines) format.

## Purpose

Track decisions to:
- **Preserve context** - Why was this choice made? What alternatives existed?
- **Identify lock-in** - Which decisions are one-way doors vs easily reversible?
- **Trace implications** - What downstream effects and dependencies result?
- **Enable onboarding** - New team members can understand the decision history
- **Support auditing** - Compliance and security reviews have documented rationale

## File Format

Decisions are stored in `decision-log.jsonl` - one JSON object per line. This format is:
- Append-only friendly (no file parsing needed to add entries)
- Git diff friendly (changes show as single line additions)
- Easy to query with `jq`, `grep`, or scripts
- Importable into databases or analytics tools

## Quick Start

### Logging a Decision

Append a new line to `decision-log.jsonl`:

```json
{"timestamp": "2024-12-13T15:00:00Z", "decision_id": "001", "category": "technology", "decision": "Use TypeScript for API server", "rationale": "Type safety reduces runtime errors, team prefers static typing", "outcome": "All backend code will be TypeScript with strict mode enabled"}
```

### Minimal Required Fields

| Field | Description |
|-------|-------------|
| `timestamp` | ISO 8601 datetime |
| `decision_id` | Unique ID (e.g., `001`, `ARCH042`, `SEC003`) |
| `category` | Classification (see categories below) |
| `decision` | What was decided (concise, <200 chars) |
| `rationale` | Why this choice was made |
| `outcome` | Expected or actual result |

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
"reversibility": {
  "type": "one-way-door",
  "lock_in_factors": ["data migration", "API exposure"],
  "reversal_cost": "high",
  "reversal_window": "before v1.0 launch",
  "notes": "After public API release, breaking changes require deprecation cycle"
}
```

**Reversal cost levels:**
- `trivial` - Minutes of work, no user impact
- `low` - Hours of work, minimal coordination
- `medium` - Days of work, some user communication
- `high` - Weeks of work, significant coordination
- `prohibitive` - Months of work, may not be feasible

## Tracking Implications

Document the ripple effects of decisions:

```json
"implications": {
  "affected_components": ["api-server", "mobile-app", "admin-dashboard"],
  "dependencies_created": ["redis", "kafka"],
  "constraints_imposed": ["must maintain backward compatibility", "requires 99.9% uptime"],
  "follow_up_decisions": ["caching strategy", "failover approach"]
}
```

## Supporting Material

Link to evidence, documentation, and related resources:

```json
"supporting_material": {
  "links": [
    {"url": "https://example.com/benchmark", "title": "Performance benchmark results", "type": "benchmark"},
    {"url": "https://github.com/org/repo/issues/123", "title": "Original discussion", "type": "discussion"}
  ],
  "internal_refs": ["specs/api-design.md", "adrs/ADR-005.md"],
  "related_decisions": ["003", "007", "012"],
  "attachments": ["diagrams/architecture-v2.png"]
}
```

**Link types:** `documentation`, `blog`, `paper`, `benchmark`, `discussion`, `issue`, `pr`, `adr`, `other`

## Alternatives Considered

Document rejected options to prevent revisiting settled debates:

```json
"alternatives_considered": [
  {"option": "GraphQL API", "rejected_reason": "Team lacks expertise, overkill for current needs"},
  {"option": "gRPC", "rejected_reason": "Browser support requires proxy layer"}
]
```

## Decision Lifecycle

Decisions have a status:
- `proposed` - Under consideration, not yet finalized
- `accepted` - Agreed upon, ready for implementation
- `implemented` - Actually in production/use
- `deprecated` - No longer recommended, but still in use
- `superseded` - Replaced by another decision

When superseding a decision:
```json
{"decision_id": "042", "status": "superseded", "superseded_by": "089", ...}
```

## Querying the Log

### Using jq

```bash
# All architecture decisions
jq -c 'select(.category == "architecture")' decision-log.jsonl

# One-way doors only
jq -c 'select(.reversibility.type == "one-way-door")' decision-log.jsonl

# Decisions with high reversal cost
jq -c 'select(.reversibility.reversal_cost == "high" or .reversibility.reversal_cost == "prohibitive")' decision-log.jsonl

# Find by tag
jq -c 'select(.tags | index("security"))' decision-log.jsonl

# Decisions affecting a component
jq -c 'select(.implications.affected_components | index("api-server"))' decision-log.jsonl
```

### Using grep

```bash
# Quick search
grep "database" decision-log.jsonl

# Count by category
grep -o '"category": "[^"]*"' decision-log.jsonl | sort | uniq -c
```

## Integration with Flowspec

In spec-driven development workflows:

1. **During `/flow:specify`** - Log design decisions from functional specs
2. **During `/flow:plan`** - Log architecture and technology choices from technical specs
3. **During `/flow:implement`** - Log implementation decisions as they arise
4. **During `/flow:validate`** - Log any decisions from review feedback
5. **During `/flow:operate`** - Log operational and scaling decisions

### Automatic Logging

Agents should log decisions when:
- Choosing between multiple valid approaches
- Selecting technologies, libraries, or tools
- Defining interfaces or contracts
- Making trade-offs (performance vs simplicity, etc.)
- Establishing conventions or patterns

## Best Practices

1. **Log early, log often** - Better to over-document than under-document
2. **Be specific in rationale** - Future you will thank past you
3. **Always assess reversibility** - Flag one-way doors explicitly
4. **Link supporting evidence** - Don't just state opinions, cite sources
5. **Document alternatives** - Explain why other options were rejected
6. **Update status** - Mark decisions as implemented or superseded
7. **Use consistent IDs** - Consider prefixes by domain (ARCH, SEC, PERF)
8. **Review periodically** - Revisit old decisions as context changes

## Schema Validation

Validate entries against `decision-log.schema.json`:

```bash
# Using ajv-cli
ajv validate -s decision-log.schema.json -d decision-log.jsonl --all-errors

# Using check-jsonschema
check-jsonschema --schemafile decision-log.schema.json decision-log.jsonl
```

## Example: Full Decision Entry

```json
{
  "timestamp": "2024-12-13T16:00:00Z",
  "decision_id": "ARCH003",
  "category": "architecture",
  "decision": "Adopt event sourcing for order management",
  "rationale": "Need complete audit trail for financial compliance. Event replay enables debugging production issues. Supports future CQRS optimization.",
  "outcome": "Order state derived from event stream. Events stored in append-only log with 7-year retention.",
  "reversibility": {
    "type": "one-way-door",
    "lock_in_factors": ["schema design", "data migration", "team training"],
    "reversal_cost": "prohibitive",
    "reversal_window": "before first production order",
    "notes": "Once orders exist as events, migrating to CRUD would lose audit history"
  },
  "implications": {
    "affected_components": ["order-service", "billing", "reporting", "admin-tools"],
    "dependencies_created": ["event-store", "projection-service"],
    "constraints_imposed": ["events are immutable", "must version event schemas"],
    "follow_up_decisions": ["event schema versioning strategy", "projection rebuild process"]
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
  },
  "stakeholders": ["backend-team", "compliance", "finance"],
  "status": "accepted",
  "tags": ["event-sourcing", "compliance", "orders", "critical-path"]
}
```
