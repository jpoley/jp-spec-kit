---
description: Create It - Implementation and validation (implement + validate)
mode: agent
loop: inner
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

{{INCLUDE:.claude/commands/flow/_constitution-check.md}}

{{INCLUDE:.claude/commands/flow/_rigor-rules.md}}

{{INCLUDE:.claude/commands/flow/_workflow-state.md}}

## Meta-Workflow: Build (Create It)

This meta-workflow executes the complete build phase with **atomic** semantics - both implementation and validation must succeed together:

1. **Implement** - Write code, tests, and documentation
2. **Validate** - QA checks, security scans, documentation review

**Required input state**: `Planned`
**Output state**: `Validated`
**Orchestration**: Atomic (both must succeed or neither completes)

## Step 1: Verify Task State

```bash
# Get current task from branch or arguments
TASK_ID="${TASK_ID:-$(git branch --show-current 2>/dev/null | grep -Eo 'task-[0-9]+' || echo '')}"

if [ -z "$TASK_ID" ]; then
  echo "❌ No task ID found. Run from a feature branch or specify task ID."
  echo "Usage: /flow:meta-build [task-id]"
  exit 1
fi

# Check task state using backlog.md
CURRENT_STATE=$(backlog task "$TASK_ID" --plain 2>/dev/null | grep "^Status:" | awk '{print $2}')

if [ "$CURRENT_STATE" != "Planned" ]; then
  echo "❌ Task $TASK_ID is in state '$CURRENT_STATE' but requires 'Planned'"
  echo "This meta-workflow can only run from 'Planned' state."
  echo ""
  echo "Did you run /flow:meta-research first?"
  exit 1
fi

echo "✓ Task $TASK_ID verified in 'Planned' state"
echo "✓ Starting meta-workflow: build (Create It)"
echo "✓ Atomic mode: Implementation and validation will execute together"
echo ""
```

## Step 2: Execute Sub-Workflows (Atomic)

Execute implementation and validation sub-workflows atomically. If either fails, both fail.

### 2.1 Run /flow:implement

Execute implementation with frontend/backend engineers and code reviewers:

**Execute**: `/flow:implement`

Wait for implement to complete. This will:
- Execute backlog tasks for this feature
- Write source code in `src/`
- Create tests in `tests/`
- Generate AC coverage report
- Run code review agents
- Transition task to `In Implementation` state

### 2.2 Run /flow:validate

Execute validation with QA, security, and documentation checks:

**Execute**: `/flow:validate`

Wait for validate to complete. This will:
- Run QA validation and test execution
- Execute security scans (bandit, semgrep, etc.)
- Review documentation completeness
- Run release manager checks
- Create validation report in `docs/qa/`
- Create security report in `docs/security/`

## Step 3: Quality Gate Enforcement

After validation completes, enforce quality gates before transitioning to `Validated`:

```bash
echo ""
echo "Enforcing quality gates..."
echo ""

# Quality Gate 1: Test Coverage ≥ 80%
COVERAGE=$(pytest --cov=src --cov-report=term-missing 2>/dev/null | grep "^TOTAL" | awk '{print $NF}' | tr -d '%')
COVERAGE=${COVERAGE:-0}

if [ "$COVERAGE" -lt 80 ]; then
  echo "❌ Quality Gate FAILED: Test Coverage"
  echo "   Required: ≥80%"
  echo "   Actual: ${COVERAGE}%"
  echo "   Fix: Add more tests to increase coverage"
  exit 1
fi
echo "✅ Quality Gate PASSED: Test Coverage (${COVERAGE}% ≥ 80%)"

# Quality Gate 2: Security Scan - 0 HIGH+ findings
HIGH_FINDINGS=$(grep -c "Severity: HIGH\|Severity: CRITICAL" docs/security/*-security.md 2>/dev/null || echo "0")

if [ "$HIGH_FINDINGS" -gt 0 ]; then
  echo "❌ Quality Gate FAILED: Security Scan"
  echo "   Required: 0 HIGH+ findings"
  echo "   Actual: ${HIGH_FINDINGS} HIGH+ findings"
  echo "   Fix: Address security findings in docs/security/"
  exit 1
fi
echo "✅ Quality Gate PASSED: Security Scan (0 HIGH+ findings)"

# Quality Gate 3: Acceptance Criteria 100% coverage
AC_TOTAL=$(grep -c "^\- \[ \]\|^\- \[x\]" backlog/tasks/*${TASK_ID}*.md 2>/dev/null || echo "1")
AC_DONE=$(grep -c "^\- \[x\]" backlog/tasks/*${TASK_ID}*.md 2>/dev/null || echo "0")
AC_PERCENT=$((AC_DONE * 100 / AC_TOTAL))

if [ "$AC_PERCENT" -lt 100 ]; then
  echo "❌ Quality Gate FAILED: Acceptance Criteria"
  echo "   Required: 100% coverage"
  echo "   Actual: ${AC_PERCENT}% (${AC_DONE}/${AC_TOTAL} criteria met)"
  echo "   Fix: Complete all acceptance criteria in backlog task"
  exit 1
fi
echo "✅ Quality Gate PASSED: Acceptance Criteria (${AC_PERCENT}% = ${AC_DONE}/${AC_TOTAL})"

echo ""
echo "All quality gates passed! Transitioning to Validated state..."
```

## Step 4: Atomic Transition

Update task state to `Validated` only if both sub-workflows and all quality gates succeeded:

```bash
# Update task state using backlog.md
backlog task edit "$TASK_ID" -s "Validated" 2>/dev/null

# Verify final state
FINAL_STATE=$(backlog task "$TASK_ID" --plain 2>/dev/null | grep "^Status:" | awk '{print $2}')

if [ "$FINAL_STATE" = "Validated" ]; then
  echo ""
  echo "✅ Meta-workflow 'build' completed successfully!"
  echo "   Task $TASK_ID transitioned: Planned → Validated"
  echo ""
  echo "Artifacts created:"
  echo "  - src/ (source code)"
  echo "  - tests/ (test suite)"
  echo "  - tests/ac-coverage.json (AC coverage report)"
  echo "  - docs/qa/$TASK_ID-qa-report.md"
  echo "  - docs/security/$TASK_ID-security.md"
  echo ""
  echo "Quality gates enforced:"
  echo "  ✅ Test coverage: ${COVERAGE}% (≥80%)"
  echo "  ✅ Security scan: 0 HIGH+ findings"
  echo "  ✅ Acceptance criteria: ${AC_PERCENT}% (100% required)"
  echo ""
  echo "Next step: Run /flow:meta-run to deploy the feature"
else
  echo "⚠️ Warning: Expected state 'Validated' but task is in '$FINAL_STATE'"
  echo "Atomic operation failed - implementation and validation did not complete together."
  exit 1
fi
```

## Atomic Execution Guarantee

This meta-workflow enforces **atomic semantics**:

- If implementation succeeds but validation fails → Task remains in `Planned` state
- If validation succeeds but quality gates fail → Task remains in `Planned` state
- Only if all succeed → Task transitions to `Validated`

This prevents "half-done" features and ensures quality is always enforced.

## Execution Summary

This meta-workflow consolidates 2 workflow commands into 1 with atomic guarantees:

**Instead of running separately:**
```bash
/flow:implement
/flow:validate  # Hope nothing breaks!
```

**You run once:**
```bash
/flow:meta-build  # Atomic: both succeed or both fail
```

All sub-workflows integrate with backlog.md for state management and task tracking.

## See Also

- `/flow:meta-research` - Plan It (assess + specify + research + plan)
- `/flow:meta-run` - Deploy It (operate)
- `flowspec_workflow.yml` - Configuration reference
- `docs/adr/003-meta-workflow-simplification.md` - Design rationale
