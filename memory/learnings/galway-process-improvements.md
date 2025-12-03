# Process Improvements from Galway Learnings

**Date**: 2025-12-03
**Host**: galway
**PRs Analyzed**: #342, #349, #351

## Summary

Analysis of closed/unmerged PRs revealed **23 code quality issues** across 3 PRs. This document proposes process improvements to prevent these issues from recurring.

---

## Issue Frequency Analysis

| Issue Type | Count | PRs Affected |
|------------|-------|--------------|
| Imports inside methods | 4 | #342 (3), #351 (1) |
| Misleading error messages | 3 | #351 |
| Pattern matching too broad | 4 | #342 |
| Early return logic flaws | 2 | #342 |
| Unused configuration fields | 1 | #349 |
| Output format placeholders | 1 | #349 |
| Variable shadowing modules | 1 | #349 |
| Import formatting (PEP 8) | 1 | #351 |
| Path handling errors | 1 | #342 |
| Error handling gaps | 1 | #342 |
| Test comment accuracy | 1 | #342 |
| Branch conflicts | 1 | #354 (during merge) |

---

## Root Cause Analysis

### 1. No Pre-Commit Enforcement

**Problem**: Issues like import placement and formatting slip through.

**Solution**: Add pre-commit hooks:
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

### 2. No Pattern Testing with Adversarial Examples

**Problem**: Pattern matching code passes tests but fails on edge cases.

**Solution**: Add adversarial test cases:
```python
def test_sql_injection_false_positive_question_mark():
    """Ensure ? in ternary operator doesn't match."""
    code = "x = a ? b : c"  # Not SQL!
    result = classifier.classify(make_finding(code_snippet=code))
    assert result.classification != Classification.FALSE_POSITIVE
```

### 3. No Validation Message Review

**Problem**: Error messages don't match validation logic.

**Solution**: Add assertion in validation tests:
```python
def test_error_message_matches_condition():
    """Verify error message accurately describes constraint."""
    # If condition is `x < 0`, message should say "non-negative"
    # If condition is `x <= 0`, message should say "positive"
```

### 4. No Feature Flag Verification

**Problem**: Configuration fields added but never used.

**Solution**: Add dead code detection:
```bash
# Check for unused dataclass fields
vulture src/specify_cli --min-confidence 80
```

### 5. No Rebase-Before-Merge Policy

**Problem**: PRs get stale and develop conflicts.

**Solution**: Require rebase before merge:
```yaml
# Branch protection rule
require_branches_to_be_up_to_date: true
```

---

## Recommended Process Changes

### 1. Pre-Commit Hooks (Automated)

Add to all projects:
- `ruff check --fix` - Catches import issues
- `ruff format` - Fixes PEP 8 formatting
- `vulture` - Detects dead code

### 2. PR Checklist (Manual)

Add to PR template:
```markdown
## Code Quality Checklist
- [ ] All imports at module level
- [ ] Error messages match validation conditions
- [ ] Pattern matching tested with adversarial cases
- [ ] All config fields are used somewhere
- [ ] No variable names shadow modules
```

### 3. Review Focus Areas

Copilot catches these well - ensure reviews are addressed:
- Import placement
- Error message accuracy
- Configuration usage

### 4. Stale Branch Prevention

- Rebase branches weekly
- Close PRs that stale >7 days
- Use merge queue to prevent conflicts

---

## Metrics to Track

| Metric | Current | Target |
|--------|---------|--------|
| PRs with Copilot issues | 100% (3/3) | <20% |
| Issues per PR | 7.7 avg | <2 |
| Time to fix | 1 day | 0 (prevented) |
| Conflict rate | 33% | 0% |

---

## Implementation Priority

### Immediate (This Week)
1. Add pre-commit hooks to jp-spec-kit
2. Update PR template with checklist

### Short Term (This Month)
3. Add vulture to CI pipeline
4. Enable branch protection rules

### Long Term (This Quarter)
5. Create adversarial test suite
6. Add automated error message validation

---

## Files Changed in This Session

| Branch | PR | Issues Fixed |
|--------|----|----|
| galway-learnings-triage-fixes | #361 | 16 + conflict |
| galway-learnings-audit-report | #357 | 2 |
| galway-learnings-security-config | #359 | 5 |

**Total**: 23 issues fixed, 3 learnings documents created

---

## References

- `memory/learnings/pr-342-triage-engine.md` - Triage engine learnings
- `memory/learnings/pr-349-audit-report.md` - Audit report learnings
- `memory/learnings/pr-351-security-config.md` - Security config learnings
- `memory/critical-rules.md` - Updated with new rules
