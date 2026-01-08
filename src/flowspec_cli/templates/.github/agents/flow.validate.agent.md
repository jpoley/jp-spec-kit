---
name: FlowValidate
description: "Execute validation and quality assurance using QA, security, documentation, and release management agents."
target: "chat"
tools:
  - "Read"
  - "Write"
  - "Edit"
  - "Grep"
  - "Glob"
  - "Bash"
  - "mcp__backlog__*"
  - "mcp__serena__*"
  - "Skill"

handoffs:
  - label: "Submit PR"
    agent: "flow.submit-n-watch-pr"
    prompt: "Validation is complete. Submit PR and monitor CI/reviews."
    send: false
---

# /flow:validate - Quality Assurance

Execute comprehensive validation with automated testing, security scanning, and AC verification.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Instructions

This command performs thorough validation before PR submission.

**Prerequisites:**
1. Run `/flow:implement` first to complete coding
2. All acceptance criteria should be checked in backlog
3. Code should pass local tests

**Validation Phases:**

### Phase 1: Code Quality
- Lint check: `ruff check .` (Python), `go vet` (Go), `npm run lint` (TS)
- Format check: `ruff format --check .`
- Type check: `pyright`/`tsc --noEmit`

### Phase 2: Test Suite
- Unit tests: `pytest tests/unit/`
- Integration tests: `pytest tests/integration/`
- Coverage verification

### Phase 3: Security Scan
- SAST: `bandit -r src/` (Python)
- Dependency audit: `npm audit`, `safety check`
- Secret detection

### Phase 4: AC Verification
- Verify all acceptance criteria are met
- Review implementation notes
- Confirm test coverage for each AC

### Phase 5: Documentation
- API documentation updated
- README current
- CHANGELOG entry added

**Output:**
- QA report in `docs/qa/`
- Security scan results
- Workflow state updated to `Validated`

After validation passes, run `/flow:submit-n-watch-pr` to create and monitor PR.
