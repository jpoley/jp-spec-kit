---
description: Run quality gate validation on spec documents before implementation.
loop: inner
# Loop Classification: INNER LOOP
# This command validates spec quality as a gate before implementation begins.
---

## User Input

```text
$ARGUMENTS
```

## Execution Instructions

This command validates spec quality before implementation can proceed. It ensures PRDs and specifications meet minimum quality thresholds.

### Quality Gate Validation

**CRITICAL**: Spec quality must pass before implementation begins.

```bash
# Run quality gate on spec.md
flowspec gate

# Alternative: Override threshold if needed
flowspec gate --threshold 60

# Emergency bypass (NOT RECOMMENDED - use only with explicit user approval)
flowspec gate --force
```

**Quality Gate Exit Codes:**
- `0` = PASSED - Proceed to implementation
- `1` = FAILED - Spec quality below threshold
- `2` = ERROR - Missing spec.md or validation error

### If Gate PASSES (exit code 0)

```
[OK] Quality gate passed
Proceeding with implementation...
```

### If Gate FAILS (exit code 1)

```
[X] Quality gate failed: Spec quality is X/100 (minimum: 70)

Recommendations:
  - Add missing section: ## Description
  - Add missing section: ## User Story
  - Reduce vague terms (currently: Y instances)
  - Add measurable acceptance criteria

Action Required:
1. Improve spec quality using recommendations
2. Re-run: flowspec quality docs/prd/<feature>-spec.md
3. When quality >= 70, re-run: /flow:gate

OR (not recommended without user approval):
  flowspec gate --force
```

### --force Bypass

The `--force` flag:
- Only use with explicit user approval
- Warns that bypassing quality checks may lead to unclear requirements
- Logs the bypass decision

### Output

Report the gate status:

| Result | Action |
|--------|--------|
| PASSED | Report success, implementation can proceed |
| FAILED | Report issues and recommendations |
| BYPASSED | Log bypass, warn about risks |

### Composability

This command can be invoked:
- Standalone: `/flow:gate` for manual quality checks
- As part of `/flow:implement` orchestration
- In CI pipelines for automated quality enforcement
