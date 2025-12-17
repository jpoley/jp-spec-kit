# PRD: {Feature Name}

## Executive Summary

{Brief 2-3 sentence overview of the feature and its business value.}

## Problem Statement

{Describe the problem being solved.}

### Current State

- {Current limitation or pain point 1}
- {Current limitation or pain point 2}

### Desired State

- {What success looks like 1}
- {What success looks like 2}

## User Stories

### US1: {Story Title}

As a {user role}, I want {goal} so that {benefit}.

**Acceptance Criteria:**
- [ ] AC1: {Testable criterion}
- [ ] AC2: {Testable criterion}
- [ ] AC3: {Testable criterion}

### US2: {Story Title}

As a {user role}, I want {goal} so that {benefit}.

**Acceptance Criteria:**
- [ ] AC1: {Testable criterion}
- [ ] AC2: {Testable criterion}

## Functional Requirements

### FR1: {Requirement Title}

{Description of the functional requirement}

- {Sub-requirement 1}
- {Sub-requirement 2}

### FR2: {Requirement Title}

{Description of the functional requirement}

## Non-Functional Requirements

### Performance

- {Performance requirement 1}
- {Performance requirement 2}

### Security

- {Security requirement 1}
- {Security requirement 2}

### Reliability

- {Reliability requirement 1}

### Scalability

- {Scalability requirement 1}

## Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| {Metric 1} | {Target value} | {How to measure} |
| {Metric 2} | {Target value} | {How to measure} |

## Dependencies

### Internal Dependencies

- {Internal system or service 1}
- {Internal system or service 2}

### External Dependencies

- {External API or service 1}
- {External vendor or tool 1}

## All Needed Context

> This section provides all context needed for implementation. Machine-parseable for use by `/flow:generate-prp`, `/flow:implement`, and `/flow:validate`.

### Code Files

<!-- List source code files relevant to this feature -->
<!-- Format: | Path | Purpose | Read Priority | -->

| File Path | Purpose | Read Priority |
|-----------|---------|---------------|
| `{path/to/file1}` | {What this file does and why it's relevant} | High/Medium/Low |
| `{path/to/file2}` | {What this file does and why it's relevant} | High/Medium/Low |

<!-- Read Priority Guide:
- High: Must read before starting implementation
- Medium: Read when working on related functionality
- Low: Reference if needed
-->

### Docs / Specs

<!-- Link to related documentation, specs, and design documents -->
<!-- Format: | Document | Link | Key Sections | -->

| Document | Link | Key Sections |
|----------|------|--------------|
| Architecture Doc | `{docs/path}` | {Relevant sections} |
| ADR | `{docs/adr/path}` | {Decision summary} |
| API Spec | `{docs/path}` | {Relevant endpoints} |
| External RFC | `{URL}` | {Relevant sections} |

### Examples

<!-- REQUIRED: PRDs without at least one example reference are considered incomplete -->
<!-- Examples help implementers understand patterns, expected behavior, and best practices -->
<!-- List example files that demonstrate patterns or expected behavior -->

**Requirement**: Every PRD MUST reference at least one relevant example from the `examples/` directory. Examples provide concrete implementations that guide development and ensure consistency.

**Good Example Reference Criteria**:
- **Relevance**: Example directly relates to the feature's technical domain or pattern
- **Specificity**: Clear explanation of which parts of the example apply to this feature
- **Actionable**: Implementer can extract specific patterns or approaches from the example

> **Important**: Replace the placeholder rows below with actual examples. Rows containing curly braces `{...}` are automatically excluded from validation and will not count toward the requirement.

| Example | Location | Relevance to This Feature |
|---------|----------|---------------------------|
| {Example name} | `examples/{path}` | {How this example relates - be specific about which patterns/functions/approaches apply} |
| {Example name} | `examples/{path}` | {How this example relates - be specific about which patterns/functions/approaches apply} |

<!-- Example of a Good Reference (wrapped in HTML comment to prevent validator from counting it):
| Example | Location | Relevance to This Feature |
|---------|----------|---------------------------|
| MCP Security Agent | `examples/mcp/claude_security_agent.py` | Demonstrates MCP server setup and tool registration pattern that applies to our feature's API integration |
-->

<!-- Example of a Poor Reference - too vague (wrapped in HTML comment):
| Example | Location | Relevance to This Feature |
|---------|----------|---------------------------|
| Security Example | `examples/mcp/README.md` | Shows security stuff |
-->

### Gotchas / Prior Failures

<!-- Document known pitfalls, historical issues, and lessons learned -->
<!-- Format: | Gotcha | Impact | Mitigation | Source | -->

| Gotcha | Impact | Mitigation | Source |
|--------|--------|------------|--------|
| {Known issue or pitfall} | {What goes wrong} | {How to avoid it} | {task-XXX or doc link} |
| {Previous failure mode} | {What went wrong} | {Lesson learned} | {task-XXX or doc link} |

<!-- Sources for gotchas:
- memory/learnings/*.md files
- Previous task implementation notes
- ADR consequences sections
- Post-mortem documents
-->

### External Systems / APIs

<!-- Document external systems and APIs this feature interacts with -->
<!-- Format: | System | Type | Documentation | Notes | -->

| System / API | Type | Documentation | Notes |
|--------------|------|---------------|-------|
| {External service name} | REST/GraphQL/gRPC | {Link to docs} | {Auth method, rate limits, etc.} |
| {Database/Cache} | {Type} | {Link to docs} | {Connection details, constraints} |
| {Third-party SDK} | Library | {Link to docs} | {Version requirements, limitations} |

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| {Risk 1} | High/Medium/Low | High/Medium/Low | {Mitigation strategy} |
| {Risk 2} | High/Medium/Low | High/Medium/Low | {Mitigation strategy} |

## Feature Validation Plan

> Specific validation steps for this feature. Not generic "run tests" but feature-specific validation recipes.

### Commands

<!-- Exact shell commands to validate this feature -->
<!-- Include test commands, lint checks, and feature-specific validations -->

```bash
# Run feature-specific unit tests
{pytest tests/path/to/feature/ -v}

# Run feature-specific integration tests
{pytest tests/integration/feature/ -v}

# Run linting for affected files
{ruff check src/path/to/feature/}

# Feature-specific validation (if applicable)
{custom validation command}
```

### Expected Success

<!-- What does successful validation look like? Be specific. -->

| Validation | Success Criteria |
|------------|------------------|
| Unit Tests | {e.g., "All tests in tests/feature/ pass (currently X tests)"} |
| Integration Tests | {e.g., "API returns 200 for happy path, proper errors for edge cases"} |
| Lint | {e.g., "Zero errors from ruff check on affected files"} |
| Manual Check | {e.g., "Feature visible in UI at /path, behaves as specified"} |
| Performance | {e.g., "Response time < 200ms for typical requests"} |

### Known Failure Modes

<!-- Common ways validation can fail and what they indicate -->

| Failure Pattern | What It Means | How to Fix |
|-----------------|---------------|------------|
| {e.g., "Import error in tests"} | {e.g., "Missing dependency or circular import"} | {e.g., "Check imports, run uv sync"} |
| {e.g., "Timeout in integration test"} | {e.g., "External service unavailable or slow"} | {e.g., "Check service health, increase timeout"} |
| {e.g., "Assertion error on response shape"} | {e.g., "API contract changed"} | {e.g., "Update test expectations or fix API"} |

## Loop Classification

> Explicit inner vs outer loop classification for this feature. Helps agents understand which tasks require fast implementation cycles vs careful planning review.

### Inner Loop Responsibilities

<!-- Fast, implementation-focused tasks handled by coding agents -->
<!-- These run frequently during development with quick feedback -->

- [ ] {e.g., "Write unit tests for new function"}
- [ ] {e.g., "Implement API endpoint"}
- [ ] {e.g., "Fix linting errors"}
- [ ] {e.g., "Add input validation"}
- [ ] {e.g., "Create database migration"}

### Outer Loop Responsibilities

<!-- Planning-focused tasks requiring human review or approval -->
<!-- These involve architectural decisions, security review, or stakeholder sign-off -->

- [ ] {e.g., "Review architecture decision"}
- [ ] {e.g., "Approve API contract changes"}
- [ ] {e.g., "Validate security requirements met"}
- [ ] {e.g., "Sign off on data model changes"}
- [ ] {e.g., "Approve production deployment"}

<!-- Reference:
- Inner Loop: docs/reference/inner-loop.md
- Outer Loop: docs/reference/outer-loop.md
- Agent Classification: docs/reference/agent-loop-classification.md
-->

## Out of Scope

- {Explicitly excluded item 1}
- {Explicitly excluded item 2}
- {Items to consider for future iterations}

## Timeline

| Phase | Description | Target Date |
|-------|-------------|-------------|
| Design | Architecture and detailed design | {Date} |
| Implementation | Core development | {Date} |
| Testing | QA and validation | {Date} |
| Launch | Production deployment | {Date} |

---

*Document Version: 1.0*
*Last Updated: {Date}*
*Author: {Author Name}*
