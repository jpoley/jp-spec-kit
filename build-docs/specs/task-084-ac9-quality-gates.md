# Task-084 AC #9: Pre-Implementation Quality Gates

## Overview
Integrate `flowspec quality` command as a pre-implementation gate that validates spec quality before coding begins.

## Requirements

### 1. Gate Integration Points
- **Slash command integration**: `/flow:implement` should run quality check first
- **CLI integration**: New `flowspec gate` command that runs quality + blocks on failure
- **Threshold configuration**: Use existing `.flowspec/quality-config.json` thresholds

### 2. Behavior
- Run `flowspec quality` on spec.md before implementation
- If overall score < threshold (default 70): BLOCK with recommendations
- If score >= threshold: PROCEED with summary
- `--force` flag to bypass gate (with warning)

### 3. Implementation Approach

**Recommended: Option C (Both CLI command + Slash command integration)**

#### Option A: CLI `flowspec gate` Command
- Add new `gate` command to CLI
- Wraps existing quality check logic
- Returns exit code 0 (pass) or 1 (fail)
- Displays pass/fail status with recommendations

#### Option B: Modify `/flow:implement` Slash Command
- Add quality gate check at start of implementation workflow
- Uses existing `flowspec quality` via subprocess
- Blocks implementation if gate fails
- Allows `--force` flag to bypass

#### Option C: Both (Recommended)
- Implement standalone `flowspec gate` command for manual use
- Integrate gate check into `/flow:implement` workflow
- Provides both programmatic (exit codes) and interactive (slash command) interfaces
- Maximizes reusability and flexibility

### 4. Exit Codes

For `flowspec gate` command:
- **0**: Quality gate passed (score >= threshold)
- **1**: Quality gate failed (score < threshold)
- **2**: Error running quality check (file not found, invalid config, etc.)

### 5. Output Format

#### Success Case
```
🔍 Running pre-implementation quality gate...

Quality Assessment: spec.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Score: 85/100 ✅ PASSED (minimum: 70)

Dimension Scores:
• Completeness:   90/100
• Clarity:        85/100
• Traceability:   80/100
• Constitutional: 85/100
• Ambiguity:      90/100

✅ Quality gate passed. Proceeding with implementation...
```

#### Failure Case
```
🔍 Running pre-implementation quality gate...

Quality Assessment: spec.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Score: 45/100 ❌ FAILED (minimum: 70)

Dimension Scores:
• Completeness:   30/100 ⚠️
• Clarity:        50/100 ⚠️
• Traceability:   40/100 ⚠️
• Constitutional: 60/100
• Ambiguity:      45/100 ⚠️

Top Recommendations:
1. Add missing section: ## Technical Requirements
2. Add missing section: ## Acceptance Criteria
3. Improve clarity: Remove vague terms like "etc", "various"
4. Add clear acceptance criteria to specification
5. Resolve ambiguity: TBD items in section 3

❌ Quality gate failed. Implementation blocked.

Fix the issues above or run with --force to bypass (not recommended).
```

#### Force Bypass
```
🔍 Running pre-implementation quality gate...

Quality Assessment: spec.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Score: 45/100 ❌ FAILED (minimum: 70)

⚠️  WARNING: Quality gate bypassed with --force flag
Proceeding with implementation despite low quality score.
This may lead to implementation issues and rework.
```

### 6. Configuration

Uses existing `QualityConfig.find_config()` to locate `.flowspec/quality-config.json`:

```json
{
  "thresholds": {
    "passing": 70,
    "excellent": 90
  },
  "weights": {
    "completeness": 0.30,
    "clarity": 0.25,
    "traceability": 0.20,
    "constitutional": 0.15,
    "ambiguity": 0.10
  }
}
```

If no config file exists, uses default threshold of 70.

### 7. Implementation Details

#### CLI Command Structure
```python
# src/specify_cli/__init__.py

@app.command()
def gate(
    spec_path: Path = typer.Option(None, "--spec", help="Path to spec.md"),
    force: bool = typer.Option(False, "--force", help="Bypass quality gate"),
    threshold: Optional[int] = typer.Option(None, "--threshold", help="Override threshold"),
) -> None:
    """Run pre-implementation quality gate on specification."""

    # Find spec.md if not provided
    # Load quality config
    # Run quality check
    # Display results
    # Exit with appropriate code
```

#### Slash Command Integration
Modify `/flow:implement` to include quality gate check before Phase 1:

```markdown
## Phase 0: Pre-Implementation Quality Gate

Before launching engineer agents, validate specification quality:

```bash
flowspec gate

# If gate fails, stop here and fix issues
# If gate passes, continue to Phase 1
```

If quality gate fails and user wants to proceed anyway:
```bash
flowspec gate --force
```
```

### 8. Error Handling

- **Spec file not found**: Exit code 2, clear error message
- **Invalid config file**: Exit code 2, show config path and error
- **Missing required sections**: Reported in recommendations, exit code 1
- **Config validation fails**: Exit code 2, explain weight sum error

## Acceptance Criteria

- [ ] AC #9.1: `flowspec gate` command implemented with quality check
- [ ] AC #9.2: Exit code 0 on pass (score >= threshold), 1 on fail, 2 on error
- [ ] AC #9.3: Respects threshold from `.flowspec/quality-config.json` or uses default 70
- [ ] AC #9.4: `--force` flag bypasses gate with warning (exit code 0)
- [ ] AC #9.5: Clear pass/fail output with dimension scores
- [ ] AC #9.6: Recommendations displayed on failure (top 5)
- [ ] AC #9.7: `/flow:implement` slash command includes quality gate check
- [ ] AC #9.8: Documentation updated with gate usage examples

## Test Plan

### Unit Tests
- [ ] Test with high-quality spec (score 85) - should pass
- [ ] Test with low-quality spec (score 45) - should fail
- [ ] Test with threshold = 60, score = 65 - should pass
- [ ] Test with threshold = 80, score = 75 - should fail
- [ ] Test `--force` flag - should always pass (exit code 0)
- [ ] Test custom threshold via `--threshold` flag
- [ ] Test spec file not found - exit code 2
- [ ] Test invalid config file - exit code 2

### Integration Tests
- [ ] Test with real spec.md from sample project
- [ ] Test config file discovery (walks up directory tree)
- [ ] Test default config when no config file exists
- [ ] Test `/flow:implement` with quality gate enabled

### Edge Cases
- [ ] Empty spec file
- [ ] Spec file with only one section
- [ ] Config file with invalid JSON
- [ ] Config weights don't sum to 1.0
- [ ] Spec path is a directory, not a file

## Implementation Notes

### Files to Modify
1. **`src/specify_cli/__init__.py`** - Add `gate()` command
2. **`.claude/commands/flow/implement.md`** - Add Phase 0 quality gate
3. **`tests/test_quality_gate.py`** - New test file for gate command
4. **`docs/reference/quality-gates.md`** - New documentation

### Files to Reference (Existing Code)
1. **`src/specify_cli/quality/scorer.py`** - `QualityScorer` class
2. **`src/specify_cli/quality/config.py`** - `QualityConfig.find_config()`
3. **`src/specify_cli/quality/assessors.py`** - Assessment functions

### Dependencies
- No new dependencies required
- Reuses existing quality assessment infrastructure
- Integrates with Rich for formatted output

## Out of Scope

- Web UI for quality gates
- Git hooks integration (separate task)
- CI/CD integration (separate task)
- Historical quality tracking
- Automated spec fixing

## Questions for Approval

1. **Should the gate check plan.md and tasks.md as well, or only spec.md?**
   - Current design: Only spec.md (as it's the source of truth)
   - Alternative: Check all three if they exist

2. **Should we add a `--quiet` flag for CI/CD use cases?**
   - Output only exit code, no pretty formatting
   - Useful for automation scripts

3. **Should the slash command integration be optional or mandatory?**
   - Current design: Mandatory (always runs)
   - Alternative: Add `--skip-gate` flag to `/flow:implement`

## Success Metrics

- Quality gate reduces implementation rework by catching spec issues early
- Gate pass rate increases over time as teams learn quality standards
- Time spent in specification reviews decreases (gate does first-pass check)
- Implementation velocity increases (fewer mid-implementation spec clarifications)
