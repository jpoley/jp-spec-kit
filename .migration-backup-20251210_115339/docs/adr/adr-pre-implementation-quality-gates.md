# ADR: Pre-Implementation Quality Gates

**Status**: Accepted
**Date**: 2025-12-01
**Deciders**: Quality Guardian Agent
**Tags**: quality, workflow, automation, gates

## Context

The `/jpspec:implement` command initiates implementation work by deploying frontend and backend engineer agents. However, there was no automated mechanism to verify that specifications were complete and high-quality before implementation began. This led to:

1. **Wasted Implementation Effort**: Engineers working from incomplete or ambiguous specs
2. **Implementation Rework**: Discovering spec issues mid-implementation requiring backtracking
3. **Quality Debt**: Poor specs leading to poor implementations that "technically work" but miss the mark
4. **Process Violation**: Constitutional requirements (DCO, testing, ACs) being overlooked

The core insight: **Zero implementations should start with incomplete specs.** Quality gates at the specification phase are far cheaper than fixing issues discovered during or after implementation.

## Decision

Implement automated quality gates that run before `/jpspec:implement` can proceed, enforced via a `.claude/hooks/pre-implement.sh` script.

### Gates Implemented

1. **Required Files Validation**
   - Verify `docs/prd/spec.md` exists
   - Verify `docs/adr/plan.md` exists
   - Verify `tasks.md` exists
   - Rationale: Implementation requires complete artifact chain for traceability

2. **Spec Completeness Check**
   - Detect unresolved markers: `NEEDS CLARIFICATION`, `[TBD]`, `[TODO]`, `???`, `PLACEHOLDER`, `<insert>`
   - Report exact line numbers for each marker found
   - Rationale: Ambiguity markers indicate incomplete decision-making

3. **Constitutional Compliance Check**
   - Verify DCO sign-off requirement is mentioned
   - Verify testing requirements are specified
   - Verify acceptance criteria are defined
   - Rationale: Enforce constitutional principles from `memory/constitution.md`

4. **Spec Quality Threshold Check**
   - Run `specify quality` scorer on spec.md
   - Require overall score >= 70/100
   - Report score breakdown and recommendations
   - Rationale: Quantitative quality gate prevents subjective "good enough" decisions

### Override Mechanism

Included `--skip-quality-gates` flag for power users:
- Bypasses ALL gates with warning
- Logs bypass decision for audit trail
- Use case: Emergency fixes or experimental work
- NOT RECOMMENDED for normal workflow

### User Experience

**Pass State** (all gates pass):
```
Running pre-implementation quality gates...

Gate 1: Checking required files...
✓ spec.md exists
✓ plan.md exists
✓ tasks.md exists

Gate 2: Checking spec completeness...
✓ No unresolved markers found

Gate 3: Checking constitutional compliance...
✓ Constitutional compliance verified

Gate 4: Checking spec quality threshold (>= 70)...
✓ Quality score: 82/100 (threshold: 70)

==========================================
✅ All quality gates passed. Proceeding with implementation.
```

**Fail State** (with remediation):
```
Running pre-implementation quality gates...

Gate 1: Checking required files...
✓ spec.md exists
✗ Missing required file: docs/adr/plan.md
  → Create plan using /jpspec:plan
✓ tasks.md exists

Gate 2: Checking spec completeness...
✗ Unresolved markers found in spec.md:
  - Line 45: NEEDS CLARIFICATION: authentication method
  - Line 89: [TBD] database schema
  → Resolve all markers before implementation

Gate 3: Checking constitutional compliance...
✗ Constitutional compliance violations found:
  - Missing DCO sign-off requirement mention
  → Ensure spec follows constitutional requirements in memory/constitution.md

Gate 4: Checking spec quality threshold (>= 70)...
✗ Quality score: 58/100 (threshold: 70)
  Recommendations:
  - Add missing section: ## User Story
  - Add missing section: ## Technical Requirements
  - Reduce vague terms (currently: 12 instances)
  → Improve spec quality using /speckit:clarify

==========================================
❌ Quality gates failed:

Run with --skip-quality-gates to bypass (NOT RECOMMENDED).
```

## Consequences

### Positive

1. **Earlier Quality Detection**: Spec issues caught before implementation work begins
2. **Clear Remediation**: Every failure includes specific fix guidance
3. **Cost Savings**: Prevention cheaper than cure - fixing spec issues is faster than implementation rework
4. **Process Enforcement**: Constitutional principles automatically enforced
5. **Quality Culture**: Quantitative threshold sets minimum acceptable spec quality
6. **Audit Trail**: Gate results provide visibility into spec quality at implementation time

### Negative

1. **Potential Friction**: Gates may block legitimate work if specs don't meet threshold
2. **Learning Curve**: Teams need to understand gate requirements and how to address failures
3. **Maintenance Burden**: Gate logic needs to stay synchronized with constitutional changes
4. **False Positives**: Some legitimate specs may contain markers (e.g., "TODO" in code examples)

### Mitigation Strategies

1. **Override Flag**: `--skip-quality-gates` provides escape hatch for edge cases
2. **Clear Error Messages**: Every failure includes remediation steps
3. **Comprehensive Tests**: 14 test scenarios ensure gate reliability
4. **Graceful Degradation**: Missing quality scorer doesn't block gates, just skips score check
5. **Incremental Gates**: Each gate is independent; partial compliance still provides value

## Implementation Details

### File Structure
```
.claude/hooks/
├── pre-implement.sh           # Main quality gate script
└── test-pre-implement.sh      # Comprehensive test suite (14 tests)
```

### Integration Point

The `/jpspec:implement` command in `.claude/commands/jpspec/implement.md` already includes:
```bash
# Phase 0: Quality Gate (MANDATORY)
specify gate
```

However, the `pre-implement.sh` script provides a more comprehensive implementation with:
- Multiple independent gates (not just quality score)
- Line-specific error reporting
- Constitutional compliance checks
- Aggregate error reporting

### Configuration

Gates use environment variables for flexibility:
```bash
SPEC_DIR="${SPEC_DIR:-docs/prd}"
ADR_DIR="${ADR_DIR:-docs/adr}"
QUALITY_THRESHOLD=70
```

### Testing

Comprehensive test suite (`test-pre-implement.sh`) validates:
- All gates passing scenario
- Each gate failing independently
- Multiple simultaneous failures
- Override flag behavior
- Edge cases (empty files, mixed markers, etc.)

**Test Results**: 14/14 tests passing

## Alternatives Considered

### 1. Manual Gate Review
**Rejected**: Too error-prone and inconsistent. Humans skip steps under time pressure.

### 2. Quality Score Only
**Rejected**: Misses specific issues like constitutional violations and unresolved markers.

### 3. CI/CD Integration
**Considered**: Could run gates in CI, but:
- Gates need to run BEFORE engineers start work, not after PR creation
- Pre-commit hook provides immediate feedback
- CI can still run gates as defense-in-depth

### 4. LLM-Based Quality Assessment
**Future Work**: Current implementation uses rule-based checks. An LLM could provide deeper semantic analysis (e.g., "does the spec actually answer the user story?"). However, deterministic gates provide faster feedback and clearer pass/fail criteria.

## References

- **Constitutional Principles**: `memory/constitution.md` (Task Quality, DCO Sign-off)
- **Quality Scorer**: `src/specify_cli/quality/scorer.py`
- **Quality Assessors**: `src/specify_cli/quality/assessors.py`
- **Implement Command**: `.claude/commands/jpspec/implement.md`

## Versioning

- **Version**: 1.0
- **Ratified**: 2025-12-01
- **Last Amended**: 2025-12-01

## Future Enhancements

1. **Configurable Thresholds**: Allow per-project quality thresholds via `jpspec_workflow.yml`
2. **Gate Metrics**: Track gate pass/fail rates to identify common spec quality issues
3. **LLM Semantic Analysis**: Add semantic quality checks (coherence, completeness, testability)
4. **Integration with /speckit:clarify**: Auto-suggest running clarify workflow when ambiguity detected
5. **Custom Gate Extensions**: Allow projects to add custom gates via hook scripts
