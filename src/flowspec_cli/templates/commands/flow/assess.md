---
description: Evaluate if SDD workflow is appropriate for a feature. Output: Full SDD workflow (complex), Spec-light mode (medium), Skip SDD (simple).
loop: outer
# Loop Classification: OUTER LOOP
# This command is part of the outer loop (planning/design phase). It evaluates feature
# complexity and determines workflow approach before implementation begins.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Execution Instructions

This command is the **mandatory entry point** to the flowspec workflow. It evaluates whether a feature requires the full Spec-Driven Development (SDD) workflow, a lighter specification approach, or can skip SDD entirely.

**For /flow:assess**: This is the workflow entry point. Required input state is `workflow:To Do` or no workflow label. Output state will be `workflow:Assessed`.

If the task already has a workflow state label (e.g., `workflow:Specified`), inform the user:
- Assessment is meant for new features at the start of the workflow
- For re-assessment: use `--skip-state-check` or remove the workflow label first
- Consider whether you need `/flow:specify` or another workflow command instead

### Overview

The assess command:
1. Analyzes feature complexity, risk, and architectural impact
2. Generates a detailed assessment report
3. Recommends workflow path (Full SDD, Spec-Light, or Skip SDD)
4. Transitions workflow state from "To Do" -> "Assessed"
5. Provides specific next-step commands

### Step 1: Feature Analysis

Analyze the feature request along three dimensions (1-10 scale):

#### Complexity Scoring
- **Effort Days** (1-10): Estimated development time
  - 1-2: Single day or less
  - 3-5: Few days, straightforward implementation
  - 6-8: Week or more, moderate complexity
  - 9-10: Multiple weeks, high complexity
- **Component Count** (1-10): Number of modules/services affected
  - 1-2: Single component
  - 3-5: 2-3 components
  - 6-8: 4-6 components
  - 9-10: 7+ components or cross-cutting
- **Integration Points** (1-10): External dependencies
  - 1-2: No external integrations
  - 3-5: 1-2 integrations
  - 6-8: 3-5 integrations
  - 9-10: 6+ integrations or complex orchestration

**Complexity Score = (Effort + Components + Integrations) / 3**

#### Risk Scoring
- **Security Implications** (1-10): Security risk level
  - 1-2: No security concerns
  - 3-5: Minor security considerations
  - 6-8: Moderate security requirements
  - 9-10: Critical security controls required
- **Compliance Requirements** (1-10): Regulatory compliance
  - 1-2: No compliance requirements
  - 3-5: Basic compliance (logging, audit)
  - 6-8: Industry standards (PCI, HIPAA)
  - 9-10: Strict regulatory compliance
- **Data Sensitivity** (1-10): Data handling requirements
  - 1-2: Public/non-sensitive data
  - 3-5: Internal business data
  - 6-8: Customer personal data
  - 9-10: Financial/health/highly sensitive data

**Risk Score = (Security + Compliance + Data) / 3**

#### Architecture Impact Scoring
- **New Patterns** (1-10): Introduction of new patterns
  - 1-2: Uses existing patterns
  - 3-5: Minor pattern variations
  - 6-8: New patterns for team
  - 9-10: Novel architectural patterns
- **Breaking Changes** (1-10): API/contract changes
  - 1-2: No breaking changes
  - 3-5: Internal breaking changes only
  - 6-8: Public API breaking changes
  - 9-10: Major breaking changes across system
- **Dependencies Affected** (1-10): Impact on other systems
  - 1-2: Self-contained
  - 3-5: 1-2 downstream dependencies
  - 6-8: 3-5 downstream dependencies
  - 9-10: Wide-ranging dependency impact

**Architecture Impact Score = (Patterns + Breaking + Dependencies) / 3**

### Step 2: Recommendation Logic

Calculate recommendation based on scores:

# Each score (Complexity, Risk, Architecture Impact) is the average of three sub-scores (range 1-10).
# Total Score = Complexity + Risk + Architecture Impact
# Total Score range: 3 (all scores = 1) to 30 (all scores = 10)
```
Total Score = Complexity + Risk + Architecture Impact

IF any individual score >= 7 OR Total Score >= 18:
    Recommendation: Full SDD
    Confidence: High
    Rationale: High complexity/risk/impact requires full workflow

ELSE IF any individual score >= 4 OR Total Score >= 10:
    Recommendation: Spec-Light
    Confidence: Medium
    Rationale: Moderate complexity benefits from lightweight specification

ELSE:
    Recommendation: Skip SDD
    Confidence: High
    Rationale: Low complexity allows direct implementation
```

### Step 3: Generate Assessment Report

Create the assessment report at `./docs/assess/{feature}-assessment.md`:

```markdown
# Feature Assessment: {Feature Name}

**Date**: {YYYY-MM-DD}
**Assessed By**: Claude AI Agent
**Status**: Assessed

## Feature Overview

{Brief description of the feature from user input}

## Scoring Analysis

### Complexity Score: {X.X}/10

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Effort Days | {N}/10 | {Explanation} |
| Component Count | {N}/10 | {Explanation} |
| Integration Points | {N}/10 | {Explanation} |
| **Average** | **{X.X}/10** | |

### Risk Score: {X.X}/10

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Security Implications | {N}/10 | {Explanation} |
| Compliance Requirements | {N}/10 | {Explanation} |
| Data Sensitivity | {N}/10 | {Explanation} |
| **Average** | **{X.X}/10** | |

### Architecture Impact Score: {X.X}/10

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| New Patterns | {N}/10 | {Explanation} |
| Breaking Changes | {N}/10 | {Explanation} |
| Dependencies Affected | {N}/10 | {Explanation} |
| **Average** | **{X.X}/10** | |

## Overall Assessment

**Total Score**: {XX.X}/30
**Recommendation**: {Full SDD | Spec-Light | Skip SDD}
**Confidence**: {High | Medium | Low}

### Rationale

{Detailed explanation of recommendation based on scores}

### Key Factors

- **Complexity**: {Summary}
- **Risk**: {Summary}
- **Impact**: {Summary}

## Next Steps

{Based on recommendation, provide specific commands}

### Full SDD Path
```bash
/flow:specify {feature}
```

### Spec-Light Path
```bash
# Create lightweight spec in ./docs/prd/{feature}-spec.md
# Include: problem statement, key requirements, acceptance criteria
# Then proceed to implementation
```

### Skip SDD Path
```bash
# Proceed directly to implementation
# Document decisions in ADRs as needed
```

## Override

If this assessment doesn't match your needs, you can override:

```bash
# Force full SDD workflow
/flow:assess {feature} --mode full

# Force spec-light mode
/flow:assess {feature} --mode light

# Force skip SDD
/flow:assess {feature} --mode skip
```

---

*Assessment generated by /flow:assess workflow*
```

### Step 4: Support Override Mode

If user provides `--mode {full|light|skip}` flag:
1. Skip scoring analysis
2. Generate assessment report with override noted
3. Proceed with specified workflow path

### Step 5: Output Recommendation

After generating the report, output:

```
## Assessment Complete

**Feature**: {feature name}
**Recommendation**: {Full SDD | Spec-Light | Skip SDD}
**Confidence**: {High | Medium | Low}
**Report**: ./docs/assess/{feature}-assessment.md

### Scoring Summary
- Complexity: {X.X}/10
- Risk: {X.X}/10
- Architecture Impact: {X.X}/10
- **Total**: {XX.X}/30

### Next Command

{Based on recommendation:}

For Full SDD:
    /flow:specify {feature}

For Spec-Light:
    Create lightweight spec at ./docs/prd/{feature}-spec.md then implement

For Skip SDD:
    Proceed to implementation, document in ADRs as needed
```

### Implementation Notes

1. **State Transition**: This command transitions from "To Do" -> "Assessed"
2. **Artifact**: Produces `./docs/assess/{feature}-assessment.md`
3. **Validation Mode**: NONE (automatic transition)
4. **Override Support**: `--mode {full|light|skip}` flag bypasses scoring

### Error Handling

- If `./docs/assess/` directory doesn't exist, create it
- If feature name is ambiguous, ask for clarification
- If assessment already exists, ask whether to overwrite
- If override mode is invalid, show valid options

### Quality Checks

Before completing:
- [ ] Assessment report exists at correct path
- [ ] All scoring dimensions are documented
- [ ] Recommendation is clear and justified
- [ ] Next steps are specific and actionable
- [ ] Override instructions are provided

## Post-Completion: Emit Workflow Event

After successfully completing this command (assessment report generated), emit the workflow event:

```bash
flowspec hooks emit workflow.assessed \
  --spec-id "$FEATURE_ID" \
  --task-id "$TASK_ID" \
  -f docs/assess/$FEATURE_ID-assessment.md
```

Replace `$FEATURE_ID` with the feature being assessed and `$TASK_ID` with the backlog task ID if available.

This triggers any configured hooks in `.flowspec/hooks/hooks.yaml` (e.g., notifications, workflow tracking).
