# Product Requirements Document: Role Usage Analytics Telemetry

**Date**: 2025-12-10
**Document Owner**: @pm-planner (Product Requirements Manager)
**Status**: Specified
**Version**: 1.0
**Feature ID**: task-366
**Parent Task**: task-366

---

## 1. Executive Summary

### Problem Statement

JP Flowspec has introduced a sophisticated role-based command architecture (task-361, task-367) with 7 personas (PM, Architect, Developer, Security, QA, Ops, All) and role-specific command namespaces. However, **we have zero visibility into how users interact with this role system**, creating critical gaps in product development:

1. **No usage analytics**: We don't know which roles developers select or which commands they use
2. **No adoption metrics**: We can't measure if role-based commands improve workflow efficiency
3. **No informed iteration**: We lack data to prioritize new role-specific features or deprecate unused commands
4. **No handoff insights**: We don't understand agent-to-agent handoff patterns in multi-machine workflows

These gaps force product decisions based on intuition rather than data, increasing the risk of investing in features users don't need.

### Solution Overview

Introduce an **opt-in, privacy-preserving telemetry system** for role usage analytics. The system consists of:

1. **RoleEvent Tracking**: Canonical event types (role.selected, agent.invoked, handoff.clicked)
2. **Local Storage**: JSONL telemetry file at `.flowspec/telemetry.jsonl`
3. **Privacy-by-Design**: PII hashing, opt-in consent, local-only storage (v1)
4. **User Control**: CLI commands to view, export, and delete telemetry data
5. **Transparent Opt-In**: Clear privacy notice during init/configure with benefits and guarantees

**Key Design Principles**:
- **Privacy-First**: No data collection without explicit consent
- **Local-First**: Telemetry stored locally, no remote transmission in v1
- **Minimal Data**: Collect only what's needed for defined product metrics
- **Transparency**: Users can view and delete their data anytime

### Business Value

**Primary Metrics**:
- **Measure role adoption by 100%** (from 0% visibility to complete coverage)
- **Identify top 5 most-used commands per role** within 3 months of v1 release
- **Inform feature prioritization** based on actual usage patterns vs assumptions
- **Reduce wasted engineering effort by 30%** (data-driven feature decisions)

**Strategic Benefits**:
- **Product-Market Fit**: Understand which roles resonate with users
- **User Empathy**: See how developers actually use the tool in practice
- **Competitive Intelligence**: Benchmark role usage against industry patterns
- **Foundation for V2**: Enable opt-in telemetry export for aggregated insights

### Success Criteria

**Must Have (v1)**:
- Event tracking for role.selected, agent.invoked, handoff.clicked events
- Opt-in consent with clear privacy notice during init/configure
- Local JSONL storage with PII hashing (no remote transmission)
- CLI commands: `specify telemetry {view,export,clear,stats}`
- Privacy verification: Assert no raw PII in telemetry.jsonl

**Nice to Have (v2)**:
- Opt-in telemetry export to aggregated analytics platform
- Dashboard visualizations of role usage patterns
- Anonymized public dataset for research

**Out of Scope (v1)**:
- Remote telemetry transmission (defer to v2 with explicit opt-in)
- Real-time analytics or dashboards
- Cross-project aggregation

---

## 2. User Stories and Use Cases

### Primary Personas

#### Persona 1: Product Manager (Elena)
**Background**: Elena maintains JP Flowspec and needs data to prioritize new role-specific features. She wants to know which roles developers use most and which commands are underutilized.

**Pain Points**:
- No visibility into role selection patterns
- Can't justify investment in new role-specific commands
- Don't know if role system is used or ignored

**Goals**:
- See which roles are selected during init (PM, Dev, All?)
- Identify top 5 most-used commands per role
- Measure adoption of new features (e.g., handoff clicks)

#### Persona 2: Developer (Marcus)
**Background**: Marcus is a privacy-conscious developer who uses JP Flowspec daily. He's willing to share usage data if it improves the product, but only with strong privacy guarantees.

**Pain Points**:
- Distrust of telemetry systems that collect PII
- Concern about tracking project names or file paths
- No visibility into what data is collected

**Goals**:
- Transparent opt-in with clear privacy notice
- Ability to view exactly what data is collected
- Easy opt-out and data deletion

#### Persona 3: Open Source Contributor (Sarah)
**Background**: Sarah contributes to JP Flowspec and wants to understand usage patterns to improve documentation and tutorials for specific roles.

**Pain Points**:
- No data on which roles need better documentation
- Can't prioritize tutorial content (PM vs Dev vs QA?)
- Don't know which commands confuse users

**Goals**:
- Aggregated analytics showing role usage distribution
- Command usage frequency to identify confusing UX
- Handoff patterns to improve multi-agent workflows

### User Stories

#### US1: Opt-In to Telemetry with Privacy Notice

**As a** developer using JP Flowspec,
**I want** to see a clear privacy notice during init/configure,
**So that** I understand what telemetry is collected and can make an informed consent decision.

**Acceptance Criteria**:
- [ ] AC1: During `/flow:init`, user sees telemetry opt-in prompt with privacy notice
- [ ] AC2: Privacy notice explains: local-only storage, PII hashing, opt-out anytime, view/delete data
- [ ] AC3: User can opt-in (Y), opt-out (N), or defer decision (skip)
- [ ] AC4: Consent is stored in `flowspec_workflow.yml` with timestamp
- [ ] AC5: Non-interactive mode via `--telemetry-enabled` flag

**Priority**: Must Have

#### US2: Track Role Selection Events

**As a** product manager,
**I want** to track which roles users select during init/configure,
**So that** I can measure role adoption and prioritize role-specific features.

**Acceptance Criteria**:
- [ ] AC1: When user selects role in init/configure, `role.selected` event is tracked
- [ ] AC2: Event payload includes: timestamp, role (pm/arch/dev/sec/qa/ops/all), hashed project ID
- [ ] AC3: Tracking only occurs if telemetry is enabled (consent check)
- [ ] AC4: Event is appended to `.flowspec/telemetry.jsonl`
- [ ] AC5: No raw PII in event (project name, username, file paths are hashed)

**Priority**: Must Have

#### US3: Track Agent Invocation Events

**As a** product manager,
**I want** to track which agents users invoke via commands,
**So that** I can identify most-used agents and prioritize agent improvements.

**Acceptance Criteria**:
- [ ] AC1: When user runs role-based command (e.g., `/pm:assess`), `agent.invoked` event is tracked
- [ ] AC2: Event payload includes: timestamp, role, command, agent (e.g., `@workflow-assessor`), hashed project ID
- [ ] AC3: Tracking only occurs if telemetry is enabled
- [ ] AC4: Event is appended to `.flowspec/telemetry.jsonl`
- [ ] AC5: Performance overhead < 50ms per event

**Priority**: Must Have

#### US4: Track Handoff Click Events

**As a** product manager,
**I want** to track when users click agent handoff links in VS Code,
**So that** I can measure adoption of multi-agent workflows and improve handoff UX.

**Acceptance Criteria**:
- [ ] AC1: When user clicks handoff link in VS Code Copilot, `handoff.clicked` event is tracked
- [ ] AC2: Event payload includes: timestamp, source_agent, target_agent, hashed project ID
- [ ] AC3: Tracking only occurs if telemetry is enabled
- [ ] AC4: Event is appended to `.flowspec/telemetry.jsonl`
- [ ] AC5: Works with VS Code Copilot extension integration

**Priority**: Nice to Have (depends on VS Code integration)

#### US5: View Telemetry Data

**As a** privacy-conscious developer,
**I want** to view exactly what telemetry data has been collected,
**So that** I can verify no PII is leaked and understand what's tracked.

**Acceptance Criteria**:
- [ ] AC1: `specify telemetry view` command displays recent events in table format
- [ ] AC2: Table shows: timestamp, event_type, role, command, agent (hashed values shown)
- [ ] AC3: Command shows max 50 events by default, with `--limit` flag for more
- [ ] AC4: Command respects privacy - shows hashed values, not raw PII
- [ ] AC5: If telemetry disabled, command shows "Telemetry not enabled"

**Priority**: Must Have

#### US6: Export Telemetry Data

**As a** developer who wants to analyze my own workflow,
**I want** to export telemetry data to JSON/CSV,
**So that** I can analyze my role usage patterns in external tools.

**Acceptance Criteria**:
- [ ] AC1: `specify telemetry export --format json` exports to JSON file
- [ ] AC2: `specify telemetry export --format csv` exports to CSV file
- [ ] AC3: Export includes all events in `.flowspec/telemetry.jsonl`
- [ ] AC4: Export file is written to user-specified path or default `telemetry-export.{json,csv}`
- [ ] AC5: Export maintains privacy - hashed values, not raw PII

**Priority**: Nice to Have

#### US7: Delete Telemetry Data

**As a** privacy-conscious developer,
**I want** to delete all collected telemetry data,
**So that** I can revoke consent and ensure my usage data is removed.

**Acceptance Criteria**:
- [ ] AC1: `specify telemetry clear` command deletes `.flowspec/telemetry.jsonl`
- [ ] AC2: Command prompts for confirmation before deletion (safety check)
- [ ] AC3: Command with `--force` flag skips confirmation
- [ ] AC4: Command also clears `.flowspec/telemetry.salt` (hash salt file)
- [ ] AC5: After deletion, telemetry opt-in prompt shows again on next init/configure

**Priority**: Must Have

#### US8: View Telemetry Statistics

**As a** developer curious about my workflow,
**I want** to see aggregated statistics about my role usage,
**So that** I can understand my own development patterns.

**Acceptance Criteria**:
- [ ] AC1: `specify telemetry stats` command shows aggregated metrics
- [ ] AC2: Metrics include: total events, events by type, events by role, top 5 commands
- [ ] AC3: Stats calculated from local `.flowspec/telemetry.jsonl` (no remote call)
- [ ] AC4: Stats respect date range filters: `--since`, `--until`
- [ ] AC5: Stats output is human-readable with color formatting

**Priority**: Nice to Have

---

## 3. DVF+V Risk Assessment (SVPG Framework)

### Value Risk (Desirability)

**Question**: Will users opt-in to telemetry?

**Risk Level**: HIGH

**Concerns**:
- Developers are privacy-conscious and distrust telemetry
- Fear of PII collection (project names, file paths, usernames)
- Telemetry fatigue - too many tools ask for consent

**Mitigation**:
1. **Transparent Privacy Notice**: Show exactly what data is collected with examples
2. **Local-First Storage**: Emphasize no remote transmission in v1
3. **User Control**: Provide view/export/delete commands to inspect data
4. **Optional Feature**: Make telemetry truly optional, not dark-pattern nudging
5. **Product Benefits**: Explain how telemetry improves features users care about

**Validation Method**:
- **Prototype Test**: Show privacy notice to 10 beta users and measure opt-in rate
- **Target**: >40% opt-in rate (considered success for privacy-first telemetry)

### Usability Risk (Experience)

**Question**: Is the opt-in flow intuitive and non-disruptive?

**Risk Level**: MEDIUM

**Concerns**:
- Complex consent flow may frustrate users during onboarding
- Users may blindly accept without reading privacy notice
- Opt-in prompt delays init workflow completion

**Mitigation**:
1. **Single-Prompt Opt-In**: One question during init, not multi-step wizard
2. **Defer Option**: Allow users to skip decision and re-prompt later
3. **Clear Copy**: Use plain language, not legal jargon
4. **Visual Hierarchy**: Use colors/icons to highlight privacy guarantees
5. **Non-Interactive Mode**: Support `--telemetry-enabled` flag for scripts

**Validation Method**:
- **Usability Test**: Observe 5 users going through init with telemetry prompt
- **Target**: 100% comprehension of what data is collected (via post-test interview)

### Feasibility Risk (Technical)

**Question**: Can we ensure PII is never collected, even accidentally?

**Risk Level**: HIGH

**Concerns**:
- Accidental data leakage through file paths or project names
- Hash collisions revealing PII
- Salt file leakage allowing hash reversal
- Insufficient testing of privacy guarantees

**Mitigation**:
1. **PII Hashing**: SHA-256 hash all potentially identifying data
2. **Project-Specific Salt**: Generate unique salt per project in `.flowspec/telemetry.salt` (gitignored)
3. **Path Sanitization**: Remove usernames and absolute paths before hashing
4. **Privacy Verification Tests**: Assert no raw PII in telemetry.jsonl (property-based testing)
5. **Code Review**: Mandatory security review of telemetry module

**Validation Method**:
- **Privacy Audit**: Manual inspection of 100 telemetry events from beta users
- **Target**: 0 raw PII leaks detected

### Viability Risk (Business)

**Question**: Is telemetry valuable for product decisions?

**Risk Level**: MEDIUM

**Concerns**:
- Low opt-in rate (<20%) yields insufficient data
- Telemetry doesn't answer key product questions
- Effort to build/maintain telemetry system may not yield ROI

**Mitigation**:
1. **Pre-Define Metrics**: Define 5 key metrics telemetry must answer before building
2. **Iterative Launch**: Start with minimal viable telemetry (role.selected only) and expand based on value
3. **Self-Service Analytics**: Build CLI stats command so users can derive value from their own data
4. **Public Roadmap**: Show users how telemetry influenced shipped features

**Validation Method**:
- **Metric Definition Workshop**: Define metrics before implementation
- **Target**: Telemetry answers at least 3/5 pre-defined product questions within 3 months

---

## 4. Functional Requirements

### FR1: Event Model and Tracking

**Description**: Define canonical event types for role usage and provide tracking API to record events.

**Requirements**:
- **FR1.1**: `RoleEvent` enum with event types:
  - `role.selected`: User selects role during init/configure
  - `agent.invoked`: User runs command that invokes agent
  - `handoff.clicked`: User clicks agent handoff link
- **FR1.2**: `track_role_event(event_type, payload)` function to record events
- **FR1.3**: Event payload schema:
  ```json
  {
    "event_id": "evt_01HQZX123...",
    "timestamp": "2025-12-10T12:34:56Z",
    "event_type": "role.selected",
    "schema_version": "1.0",
    "role": "dev",
    "command": "/pm:assess",
    "agent": "@workflow-assessor",
    "project_id": "sha256:abc123...",
    "metadata": {
      "os": "linux",
      "py_version": "3.11"
    }
  }
  ```
- **FR1.4**: All PII (project name, username, paths) hashed with SHA-256
- **FR1.5**: Performance overhead < 50ms per event

**Acceptance Criteria**:
- [ ] RoleEvent enum defined with 3 event types
- [ ] track_role_event() function implemented
- [ ] Event payload matches schema
- [ ] PII hashing applied to project_id, paths, usernames
- [ ] Performance benchmark passes (< 50ms)

### FR2: Configuration and Consent Management

**Description**: Implement opt-in consent configuration in `flowspec_workflow.yml` with consent management API.

**Requirements**:
- **FR2.1**: Telemetry section in `flowspec_workflow.yml`:
  ```yaml
  telemetry:
    enabled: false  # Default to disabled
    consent_date: "2025-12-10T12:34:56Z"
    version: "1.0"
  ```
- **FR2.2**: Consent management API:
  - `get_telemetry_consent() -> bool`
  - `set_telemetry_consent(enabled: bool)`
  - `get_telemetry_config() -> dict`
- **FR2.3**: Environment variable override: `FLOWSPEC_TELEMETRY_ENABLED=true`
- **FR2.4**: Config validation in `specify workflow validate` command
- **FR2.5**: Opt-in only - telemetry disabled by default

**Acceptance Criteria**:
- [ ] Telemetry section added to flowspec_workflow.yml schema
- [ ] Consent management API implemented
- [ ] Env var override works (FLOWSPEC_TELEMETRY_ENABLED)
- [ ] Config validation passes in workflow validate
- [ ] Default is disabled (opt-in only)

### FR3: JSONL Storage

**Description**: Append-only JSONL file storage for telemetry events at `.flowspec/telemetry.jsonl`.

**Requirements**:
- **FR3.1**: JSONL writer appends events to `.flowspec/telemetry.jsonl`
- **FR3.2**: Each event is one line of JSON (newline-delimited)
- **FR3.3**: File created on first event, append-only thereafter
- **FR3.4**: File location: `.flowspec/telemetry.jsonl` (project-local)
- **FR3.5**: Gitignore `.flowspec/telemetry.jsonl` and `.flowspec/telemetry.salt`
- **FR3.6**: File rotation after 10,000 events (archive to `.flowspec/telemetry-{date}.jsonl.gz`)

**Acceptance Criteria**:
- [ ] JSONL writer appends events correctly
- [ ] Events are newline-delimited JSON
- [ ] File created on first event
- [ ] .gitignore updated
- [ ] File rotation works after 10k events

### FR4: Privacy Utilities

**Description**: Provide privacy utilities for hashing PII and anonymizing data.

**Requirements**:
- **FR4.1**: `hash_pii(data: str) -> str` function using SHA-256
- **FR4.2**: Project-specific salt generated in `.flowspec/telemetry.salt`
- **FR4.3**: Salt is 32 bytes of random data (cryptographically secure)
- **FR4.4**: Deterministic hashing - same input produces same hash within project
- **FR4.5**: `anonymize_path(path: str) -> str` removes username and absolute paths
- **FR4.6**: `anonymize_project_name(name: str) -> str` hashes project identifiers

**Acceptance Criteria**:
- [ ] hash_pii() implemented with SHA-256
- [ ] Salt generation works and stores in .flowspec/telemetry.salt
- [ ] Deterministic hashing verified
- [ ] anonymize_path() removes usernames
- [ ] anonymize_project_name() hashes identifiers

### FR5: CLI Feedback Prompt

**Description**: Interactive opt-in prompt during init/configure with clear privacy notice.

**Requirements**:
- **FR5.1**: Prompt displayed during `/flow:init` if telemetry not configured
- **FR5.2**: Privacy notice text:
  ```
  Role Usage Analytics (Optional)

  Help improve JP Flowspec by sharing anonymous role usage data.

  What we collect:
  - Which roles you select (PM, Dev, QA, etc.)
  - Which commands you use
  - Agent handoff patterns

  Privacy guarantees:
  - Local-only storage (no remote transmission)
  - All PII hashed (project names, usernames, paths)
  - View your data anytime: specify telemetry view
  - Delete anytime: specify telemetry clear

  Enable telemetry? [y/N/defer]:
  ```
- **FR5.3**: User options: Y (opt-in), N (opt-out), defer (skip decision)
- **FR5.4**: Non-interactive mode via `--telemetry-enabled` flag
- **FR5.5**: Prompt skipped if telemetry already configured

**Acceptance Criteria**:
- [ ] Prompt shown during init if telemetry not configured
- [ ] Privacy notice matches spec
- [ ] Y/N/defer options work
- [ ] --telemetry-enabled flag works
- [ ] Prompt skipped if already configured

### FR6: Event Integration

**Description**: Integrate telemetry tracking into role selection, agent invocation, and handoff events.

**Requirements**:
- **FR6.1**: Role selection events:
  - Hook `/flow:init` and `/flow:reset` commands
  - Track when user selects role (pm/arch/dev/sec/qa/ops/all)
- **FR6.2**: Agent invocation events:
  - Hook all `/flow:*` commands
  - Track which agent is invoked (e.g., `@workflow-assessor`, `@backend-engineer`)
- **FR6.3**: Handoff click events:
  - Hook VS Code Copilot agent handoff links
  - Track source_agent -> target_agent transitions
- **FR6.4**: Consent check before tracking (fail-safe if disabled)
- **FR6.5**: Event tracking integrated with existing hooks system

**Acceptance Criteria**:
- [ ] Role selection events tracked
- [ ] Agent invocation events tracked
- [ ] Handoff click events tracked
- [ ] Consent check enforced
- [ ] Integration with hooks system works

### FR7: Telemetry Viewer CLI

**Description**: CLI commands for users to view, export, and delete telemetry data.

**Requirements**:
- **FR7.1**: `specify telemetry view` command:
  - Display recent events in table format
  - Show: timestamp, event_type, role, command, agent
  - Default limit: 50 events (configurable with `--limit`)
- **FR7.2**: `specify telemetry export` command:
  - Export to JSON: `--format json`
  - Export to CSV: `--format csv`
  - Output path: `--output telemetry-export.{json,csv}`
- **FR7.3**: `specify telemetry clear` command:
  - Delete `.flowspec/telemetry.jsonl`
  - Prompt for confirmation (skip with `--force`)
  - Also delete `.flowspec/telemetry.salt`
- **FR7.4**: `specify telemetry stats` command:
  - Show aggregated metrics: total events, events by type, top 5 commands
  - Date range filters: `--since`, `--until`
- **FR7.5**: All commands respect privacy (show hashed values, not raw PII)

**Acceptance Criteria**:
- [ ] view command works with table output
- [ ] export command works (JSON and CSV)
- [ ] clear command deletes files with confirmation
- [ ] stats command shows aggregated metrics
- [ ] All commands respect privacy

---

## 5. Non-Functional Requirements

### Performance

**NFR-P1**: Event tracking overhead must be < 50ms per event
- **Rationale**: Telemetry should not slow down workflow commands
- **Measurement**: Benchmark tracking function with 1000 events
- **Target**: 99th percentile < 50ms

**NFR-P2**: JSONL file append must be < 10ms
- **Rationale**: File I/O should not block workflow execution
- **Measurement**: Benchmark JSONL writer with 1000 appends
- **Target**: 99th percentile < 10ms

**NFR-P3**: Telemetry viewer commands must load < 500ms
- **Rationale**: CLI commands should feel instant
- **Measurement**: Benchmark view/export/stats commands with 10k events
- **Target**: 99th percentile < 500ms

### Security

**NFR-S1**: No raw PII in telemetry.jsonl file
- **Rationale**: Privacy-by-design guarantee
- **Validation**: Property-based test asserting no raw usernames, project names, or absolute paths
- **Enforcement**: Mandatory code review + privacy verification tests

**NFR-S2**: Hash salt must be cryptographically secure
- **Rationale**: Prevent hash reversal attacks
- **Implementation**: Use `secrets.token_bytes(32)` for salt generation
- **Storage**: `.flowspec/telemetry.salt` with 0600 permissions (read/write owner only)

**NFR-S3**: Consent must be enforced before tracking
- **Rationale**: Legal compliance (GDPR, CCPA)
- **Implementation**: Check `get_telemetry_consent()` before every `track_role_event()` call
- **Validation**: Integration test asserting no events tracked when consent=false

**NFR-S4**: Telemetry files must be gitignored
- **Rationale**: Prevent accidental PII commit to public repos
- **Implementation**: Add `.flowspec/telemetry.jsonl` and `.flowspec/telemetry.salt` to .gitignore
- **Validation**: Integration test asserting files are gitignored

### Privacy

**NFR-PR1**: Opt-in only consent model
- **Rationale**: User autonomy and trust
- **Default**: `telemetry.enabled = false`
- **Enforcement**: Default config value + privacy notice

**NFR-PR2**: Local-only storage (v1)
- **Rationale**: No remote data collection without explicit opt-in
- **Implementation**: No network calls in v1, defer to v2
- **Documentation**: Privacy notice emphasizes "local-only storage"

**NFR-PR3**: User control over data
- **Rationale**: GDPR right to access, export, delete
- **Implementation**: `specify telemetry {view,export,clear}` commands
- **Validation**: E2E test exercising view -> export -> clear flow

**NFR-PR4**: Transparent data collection
- **Rationale**: Users must understand what's collected
- **Implementation**: Privacy notice with examples, view command shows actual data
- **Documentation**: FAQ explaining exactly what data is collected and why

### Reliability

**NFR-R1**: Telemetry failures must not break workflows
- **Rationale**: Telemetry is optional, core workflows must always succeed
- **Implementation**: Try/except wrapper around `track_role_event()` calls
- **Logging**: Log telemetry errors to debug log, don't raise exceptions

**NFR-R2**: File corruption recovery
- **Rationale**: JSONL file may be corrupted by unclean shutdown
- **Implementation**: Validate each JSON line, skip malformed lines with warning
- **Validation**: Corruption test - insert invalid JSON and verify graceful recovery

**NFR-R3**: Backwards compatibility
- **Rationale**: Telemetry schema may evolve over time
- **Implementation**: Schema version field in events, forward-compatible parser
- **Validation**: Test parser with events from v1.0, v1.1, v2.0 schemas

### Compliance

**NFR-C1**: GDPR compliance
- **Requirements**:
  - Right to access: `specify telemetry view`
  - Right to export: `specify telemetry export`
  - Right to deletion: `specify telemetry clear`
  - Consent management: Opt-in only, revocable anytime
- **Documentation**: Privacy policy in docs/privacy.md

**NFR-C2**: CCPA compliance
- **Requirements**: Same as GDPR + "Do Not Sell" (not applicable - no data sharing in v1)

---

## 6. Task Breakdown

Implementation tasks have been created in the backlog. The following tasks will execute this PRD:

### Core Implementation Tasks

| Task ID | Title | Priority | Labels |
|---------|-------|----------|--------|
| **task-408** | Telemetry: Privacy utilities for PII hashing and anonymization | HIGH | implement, backend, telemetry, security |
| **task-409** | Telemetry: Comprehensive test suite and privacy verification | HIGH | implement, backend, telemetry, testing |
| **task-403** | Telemetry: Core telemetry module with event tracking | MEDIUM | implement, backend, telemetry |
| **task-404** | Telemetry: Configuration system with opt-in consent | MEDIUM | implement, backend, telemetry |
| **task-405** | Telemetry: Event integration with role system | MEDIUM | implement, backend, telemetry |
| **task-406** | Telemetry: CLI feedback prompt with privacy notice | MEDIUM | implement, backend, telemetry, cli |
| **task-407** | Telemetry: CLI viewer for viewing and managing telemetry data | MEDIUM | implement, backend, telemetry, cli |

### Task Dependency Graph

```
task-408 (Privacy Utilities) [HIGH - FOUNDATIONAL]
    ├─> task-403 (Core Telemetry Module)
    │       ├─> task-404 (Configuration System)
    │       │       ├─> task-405 (Event Integration)
    │       │       └─> task-406 (CLI Feedback Prompt)
    │       └─> task-407 (Telemetry Viewer CLI)
    └─> task-409 (Test Suite) [HIGH - FINAL VALIDATION]
```

### Implementation Sequence

**Phase 1: Foundation (Est. 2 days)**
1. task-408: Privacy utilities (PII hashing, path anonymization)
2. task-403: Core telemetry module (RoleEvent, track_role_event, JSONL writer)

**Phase 2: Configuration (Est. 1 day)**
3. task-404: Configuration system (opt-in consent, flowspec_workflow.yml)

**Phase 3: Integration (Est. 1 day)**
4. task-405: Event integration (hook role selection, agent invocation, handoffs)
5. task-406: CLI feedback prompt (privacy notice, opt-in flow)

**Phase 4: User Control (Est. 1 day)**
6. task-407: Telemetry viewer CLI (view, export, clear, stats commands)

**Phase 5: Validation (Est. 1 day)**
7. task-409: Comprehensive test suite (unit, integration, privacy verification)

**Total Estimate**: 6 days (with buffer)

### Task Links

View individual task details:
- task-403: `backlog/tasks/task-403 - Telemetry-Core-telemetry-module-with-event-tracking.md`
- task-404: `backlog/tasks/task-404 - Telemetry-Configuration-system-with-opt-in-consent.md`
- task-405: `backlog/tasks/task-405 - Telemetry-Event-integration-with-role-system.md`
- task-406: `backlog/tasks/task-406 - Telemetry-CLI-feedback-prompt-with-privacy-notice.md`
- task-407: `backlog/tasks/task-407 - Telemetry-CLI-viewer-for-viewing-and-managing-telemetry-data.md`
- task-408: `backlog/tasks/task-408 - Telemetry-Privacy-utilities-for-PII-hashing-and-anonymization.md`
- task-409: `backlog/tasks/task-409 - Telemetry-Comprehensive-test-suite-and-privacy-verification.md`

---

## 7. Discovery and Validation Plan

### Learning Goals

**LG1**: Validate that opt-in rate is acceptable (target: >40%)
**LG2**: Confirm privacy notice is comprehensible (target: 100% comprehension)
**LG3**: Verify no PII leaks in telemetry data (target: 0 leaks)
**LG4**: Measure telemetry value for product decisions (target: answers 3/5 key questions)

### Discovery Experiments

#### Experiment 1: Privacy Notice Usability Test

**Hypothesis**: Privacy notice is clear and users understand what data is collected.

**Method**:
1. Recruit 5 beta users (diverse roles: PM, Dev, QA)
2. Show privacy notice during init workflow
3. After opt-in decision, interview: "What data does JP Flowspec collect?"
4. Measure comprehension accuracy

**Success Criteria**:
- 5/5 users correctly identify: role selection, command usage, agent invocations
- 5/5 users correctly identify privacy guarantees: local-only, PII hashing, opt-out anytime

**Timeline**: Week 1 after implementation

#### Experiment 2: PII Leak Audit

**Hypothesis**: No raw PII is leaked in telemetry.jsonl file.

**Method**:
1. Collect 100 telemetry events from 10 beta users
2. Manual inspection of each event payload
3. Automated regex scan for common PII patterns (usernames, email, absolute paths)
4. Property-based testing with hypothesis library

**Success Criteria**:
- 0/100 events contain raw PII
- 0 PII patterns detected by regex scan
- 100% pass rate on property-based tests

**Timeline**: Week 2 after implementation

#### Experiment 3: Opt-In Rate Measurement

**Hypothesis**: >40% of users will opt-in to telemetry.

**Method**:
1. Track opt-in decisions for 100 new projects over 30 days
2. Measure: opt-in %, opt-out %, defer %
3. Segment by user type (first-time vs returning)

**Success Criteria**:
- Overall opt-in rate >40%
- Returning user opt-in rate >50% (trust builds over time)

**Timeline**: 30 days after launch

#### Experiment 4: Product Decision Value Test

**Hypothesis**: Telemetry answers at least 3/5 key product questions.

**Pre-Defined Questions**:
1. Which role is selected most often during init? (PM, Dev, All?)
2. What are the top 5 most-used commands across all roles?
3. Is the Dev role using security commands (@secure-by-design-engineer)?
4. Are agent handoffs being clicked or ignored?
5. Which commands have high invocation -> task completion rate?

**Method**:
1. Collect 3 months of telemetry data (assuming 40% opt-in from 100 users = 40 data sources)
2. Analyze data to answer each question
3. Use insights to inform roadmap decisions

**Success Criteria**:
- Answers at least 3/5 questions with statistical confidence
- At least 1 roadmap decision influenced by telemetry insights

**Timeline**: 3 months after launch

### Validation Checkpoints

| Checkpoint | Date | Criteria | Go/No-Go Decision |
|------------|------|----------|-------------------|
| Privacy Notice Test | Week 1 | 100% comprehension | Go: Ship v1 / No-Go: Revise notice |
| PII Leak Audit | Week 2 | 0 PII leaks | Go: Ship v1 / No-Go: Fix privacy bugs |
| 30-Day Opt-In Rate | Month 1 | >40% opt-in | Go: Continue / No-Go: Revise UX |
| 90-Day Value Test | Month 3 | Answers 3/5 questions | Go: Invest in v2 / No-Go: Deprecate |

---

## 8. Acceptance Criteria and Testing

### Definition of Done (DoD)

A task is considered "Done" when:
1. All acceptance criteria are met (checkboxes in task file)
2. Unit tests pass with >90% coverage for telemetry modules
3. Integration tests pass for end-to-end telemetry flow
4. Privacy verification tests pass (no raw PII detected)
5. Performance benchmarks pass (< 50ms event tracking)
6. Code review approved by security reviewer
7. Documentation updated (privacy notice, CLI help, FAQ)

### Test Scenarios

#### TS1: End-to-End Telemetry Flow

**Scenario**: User opts in to telemetry and selects Dev role during init

**Steps**:
1. Run `specify workflow init` (or equivalent init command)
2. When prompted "Enable telemetry? [y/N/defer]:", enter "y"
3. Select role: "dev"
4. Run command: `/dev:build`
5. Verify events tracked in `.flowspec/telemetry.jsonl`

**Expected Results**:
- Consent stored in `flowspec_workflow.yml`: `telemetry.enabled = true`
- 2 events in telemetry.jsonl:
  - Event 1: `role.selected` with role="dev"
  - Event 2: `agent.invoked` with command="/dev:build", agent="@backend-engineer"
- Both events have hashed project_id (no raw project name)

**Pass Criteria**: All expected results verified

#### TS2: Consent Enforcement

**Scenario**: User opts out of telemetry, no events should be tracked

**Steps**:
1. Run `specify workflow init`
2. When prompted "Enable telemetry?", enter "N"
3. Select role: "pm"
4. Run command: `/pm:assess`
5. Verify NO events tracked

**Expected Results**:
- Consent stored: `telemetry.enabled = false`
- `.flowspec/telemetry.jsonl` does NOT exist
- No telemetry events tracked despite running commands

**Pass Criteria**: No telemetry file created, no events tracked

#### TS3: PII Privacy Verification

**Scenario**: Verify no raw PII is leaked in telemetry events

**Steps**:
1. Create project with PII-heavy names:
   - Project name: "john-smith-secret-app"
   - Project path: "/home/jsmith/projects/acme-corp-internal/"
2. Opt-in to telemetry
3. Select role and run commands
4. Inspect `.flowspec/telemetry.jsonl` with privacy scanner

**Expected Results**:
- NO raw project name "john-smith-secret-app" in file
- NO raw username "jsmith" in file
- NO absolute path "/home/jsmith/..." in file
- All identifiers are hashed (e.g., `project_id: "sha256:abc123..."`)

**Pass Criteria**: Privacy scanner detects 0 PII leaks

#### TS4: Telemetry Viewer Commands

**Scenario**: User views, exports, and deletes telemetry data

**Steps**:
1. Generate 10 telemetry events
2. Run `specify telemetry view`
3. Run `specify telemetry export --format json --output /tmp/export.json`
4. Run `specify telemetry clear --force`

**Expected Results**:
- `view` command displays 10 events in table format
- `export` command creates `/tmp/export.json` with 10 events
- `clear` command deletes `.flowspec/telemetry.jsonl` and `.flowspec/telemetry.salt`

**Pass Criteria**: All commands execute successfully, data is deleted

#### TS5: Performance Benchmark

**Scenario**: Verify telemetry overhead is < 50ms per event

**Steps**:
1. Benchmark `track_role_event()` with 1000 events
2. Measure 99th percentile latency

**Expected Results**:
- 99th percentile < 50ms

**Pass Criteria**: Performance target met

### Quality Gates

| Gate | Criteria | Automation |
|------|----------|------------|
| Unit Tests | >90% coverage for telemetry modules | pytest --cov |
| Integration Tests | 100% pass rate | pytest tests/integration/ |
| Privacy Tests | 0 PII leaks detected | pytest tests/privacy/ |
| Performance Tests | 99th percentile < 50ms | pytest tests/perf/ |
| Code Review | Security reviewer approval | GitHub PR review |
| Documentation | Privacy notice, FAQ updated | Manual review |

---

## 9. Dependencies and Constraints

### Technical Dependencies

**Internal Dependencies**:
- task-361: Role selection in init/reset commands (DONE)
- task-367: Role-based command namespaces (DONE)
- Hooks system: `src/specify_cli/hooks/` (exists, needs extension)
- Config system: `flowspec_workflow.yml` (exists, needs telemetry section)

**External Dependencies**:
- Python standard library: `json`, `hashlib`, `secrets`, `pathlib`
- No new third-party dependencies (privacy-first design)

### Constraints

**Privacy Constraints**:
- MUST NOT collect raw PII (GDPR/CCPA compliance)
- MUST be opt-in only (legal requirement)
- MUST provide user control (view/export/delete)

**Technical Constraints**:
- Performance overhead < 50ms (UX requirement)
- Local-only storage in v1 (privacy-first)
- JSONL format for append-only writes (performance)

**Resource Constraints**:
- 6 days implementation time (1 developer)
- No budget for third-party analytics platform (v1)

### Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Low opt-in rate (<20%) | HIGH | MEDIUM | Revise privacy notice, emphasize product benefits |
| PII leak despite hashing | HIGH | LOW | Mandatory security review, privacy verification tests |
| Telemetry doesn't answer product questions | MEDIUM | MEDIUM | Pre-define metrics before implementation |
| Performance regression in workflows | MEDIUM | LOW | Benchmarking, fail-safe error handling |
| Schema evolution breaks parsing | LOW | MEDIUM | Forward-compatible parser, schema versioning |

---

## 10. Success Metrics

### North Star Metric

**Role Usage Visibility Index**: Percentage of role/command interactions we can measure

**Definition**: (Tracked events) / (Total role/command interactions) × (Opt-in rate)

**Target**: >30% visibility (40% opt-in rate × 75% event coverage)

**Rationale**: Measures our ability to make data-driven product decisions

### Leading Indicators

**Metric 1: Opt-In Rate**
- **Definition**: % of new projects that enable telemetry
- **Target**: >40% within 30 days of launch
- **Measurement**: Track consent decisions in init workflow
- **Frequency**: Weekly

**Metric 2: Event Tracking Success Rate**
- **Definition**: % of events successfully tracked (no errors)
- **Target**: >99% (fail-safe design)
- **Measurement**: Count successful `track_role_event()` calls vs errors
- **Frequency**: Daily

**Metric 3: Privacy Verification Pass Rate**
- **Definition**: % of telemetry events with 0 PII leaks
- **Target**: 100% (zero tolerance)
- **Measurement**: Automated privacy scanner in CI/CD
- **Frequency**: Every commit

### Lagging Indicators

**Metric 4: Product Question Answer Rate**
- **Definition**: % of pre-defined product questions answered by telemetry
- **Target**: >60% (3/5 questions) within 90 days
- **Measurement**: Manual analysis of telemetry data
- **Frequency**: Monthly

**Metric 5: Feature Prioritization Accuracy**
- **Definition**: % of roadmap decisions influenced by telemetry insights
- **Target**: >30% of decisions within 6 months
- **Measurement**: Track decisions with "telemetry-informed" label
- **Frequency**: Quarterly

**Metric 6: User Trust Score**
- **Definition**: NPS score change after telemetry launch
- **Target**: No decrease (neutral or positive)
- **Measurement**: NPS survey before/after launch
- **Frequency**: Quarterly

### Measurement Dashboard

| Metric | Target | Current | Trend | Status |
|--------|--------|---------|-------|--------|
| Opt-In Rate | >40% | TBD | TBD | Pre-Launch |
| Event Tracking Success | >99% | TBD | TBD | Pre-Launch |
| Privacy Verification | 100% | TBD | TBD | Pre-Launch |
| Product Question Answer Rate | >60% | TBD | TBD | Pre-Launch |
| Feature Prioritization Accuracy | >30% | TBD | TBD | Pre-Launch |
| User Trust Score (NPS) | Neutral | TBD | TBD | Pre-Launch |

---

## Out of Scope (v1)

The following features are explicitly excluded from v1 to maintain focus and ship quickly:

**Remote Telemetry Transmission**:
- ❌ No data upload to remote servers
- ❌ No aggregated analytics platform
- ❌ No cross-project telemetry
- **Defer to**: v2 with explicit opt-in

**Real-Time Dashboards**:
- ❌ No web-based analytics dashboard
- ❌ No real-time visualizations
- **Defer to**: v2 after proving value with CLI stats

**Advanced Analytics**:
- ❌ No machine learning insights
- ❌ No predictive analytics
- ❌ No user segmentation
- **Defer to**: v3 if v2 shows value

**Third-Party Integrations**:
- ❌ No Mixpanel/Amplitude integration
- ❌ No webhook exports (defer to hooks system)
- **Defer to**: v2 via hooks + export command

**Team-Level Telemetry**:
- ❌ No team dashboards
- ❌ No org-wide analytics
- **Defer to**: v2 with enterprise tier

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-10 | @pm-planner | Initial PRD created from task-366 assessment |

---

## Appendix

### A. Privacy Notice Full Text

```
═══════════════════════════════════════════════════════════════
                  Role Usage Analytics (Optional)
═══════════════════════════════════════════════════════════════

Help improve JP Flowspec by sharing anonymous role usage data.

What we collect:
  ✓ Which roles you select (PM, Architect, Dev, Security, QA, Ops)
  ✓ Which commands you use (/pm:assess, /dev:build, etc.)
  ✓ Agent invocation patterns (@backend-engineer, @qa-guardian)
  ✓ Agent handoff interactions (multi-agent workflows)

What we DON'T collect:
  ✗ Project names, file paths, or source code
  ✗ Usernames, email addresses, or personal info
  ✗ Command arguments or task content

Privacy guarantees:
  🔒 Local-only storage (data stays on your machine)
  🔒 All PII hashed with SHA-256 (irreversible anonymization)
  🔒 View your data anytime: specify telemetry view
  🔒 Export your data: specify telemetry export
  🔒 Delete anytime: specify telemetry clear
  🔒 Opt-out anytime: specify workflow configure

Storage location: .flowspec/telemetry.jsonl (gitignored)

Why we collect this:
  📊 Understand which roles developers use most
  📊 Prioritize features for underserved roles
  📊 Improve command UX based on real usage patterns
  📊 Measure adoption of new features

Learn more: docs/privacy.md

═══════════════════════════════════════════════════════════════
Enable telemetry? [y/N/defer]:
```

### B. Event Schema Examples

**role.selected event**:
```json
{
  "event_id": "evt_01JEBQZ8X9...",
  "timestamp": "2025-12-10T12:34:56Z",
  "event_type": "role.selected",
  "schema_version": "1.0",
  "role": "dev",
  "project_id": "sha256:a1b2c3d4...",
  "metadata": {
    "os": "linux",
    "py_version": "3.11",
    "jp_spec_kit_version": "0.1.0"
  }
}
```

**agent.invoked event**:
```json
{
  "event_id": "evt_01JEBQZABC...",
  "timestamp": "2025-12-10T12:35:10Z",
  "event_type": "agent.invoked",
  "schema_version": "1.0",
  "role": "dev",
  "command": "/dev:build",
  "agent": "@backend-engineer",
  "project_id": "sha256:a1b2c3d4...",
  "metadata": {
    "os": "linux",
    "py_version": "3.11",
    "jp_spec_kit_version": "0.1.0"
  }
}
```

**handoff.clicked event**:
```json
{
  "event_id": "evt_01JEBQZCDE...",
  "timestamp": "2025-12-10T12:36:20Z",
  "event_type": "handoff.clicked",
  "schema_version": "1.0",
  "source_agent": "@backend-engineer",
  "target_agent": "@qa-guardian",
  "project_id": "sha256:a1b2c3d4...",
  "metadata": {
    "os": "linux",
    "py_version": "3.11",
    "jp_spec_kit_version": "0.1.0"
  }
}
```

### C. FAQ

**Q: Can I use JP Flowspec without enabling telemetry?**
A: Yes! Telemetry is entirely optional. All features work with telemetry disabled.

**Q: What happens if I opt-out after opting in?**
A: Run `specify telemetry clear` to delete all collected data and disable future tracking.

**Q: Can I see exactly what data is collected?**
A: Yes! Run `specify telemetry view` to see all events in a table format.

**Q: Is my data sent to a remote server?**
A: No. In v1, all telemetry is stored locally in `.flowspec/telemetry.jsonl`. No remote transmission.

**Q: How do you hash PII? Can it be reversed?**
A: We use SHA-256 with a project-specific salt. Hashing is one-way (irreversible). Even we can't recover the original data.

**Q: What if I accidentally commit telemetry.jsonl to Git?**
A: The file is gitignored by default. Even if committed, it only contains hashed data (no raw PII).

**Q: Will you add remote telemetry in the future?**
A: Possibly in v2, but only with explicit opt-in (separate from v1 consent). We'll ask permission first.

**Q: How does this relate to Claude Code hooks?**
A: Claude Code hooks track tool-level events (file edits, git operations). JP Flowspec telemetry tracks workflow-level events (role selection, agent invocations). They're complementary.

---

*Document Version: 1.0*
*Last Updated: 2025-12-10*
*Author: @pm-planner (Claude AI Agent)*
