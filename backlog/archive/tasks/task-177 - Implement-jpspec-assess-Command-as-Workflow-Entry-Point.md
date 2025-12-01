---
id: task-177
title: 'Implement /jpspec:assess Command as Workflow Entry Point'
status: Done
assignee: []
created_date: '2025-11-30 21:32'
updated_date: '2025-12-01 01:53'
labels:
  - workflow-artifacts
  - critical
dependencies: []
priority: high
---

<!-- AC:BEGIN -->
- [x] AC1: Create .claude/commands/jpspec/assess.md slash command template
- [x] AC2: Implement complexity scoring (effort, components, integrations)
- [x] AC3: Implement risk scoring (security, compliance, data sensitivity)
- [x] AC4: Implement architecture impact scoring
- [x] AC5: Generate assessment report at ./docs/assess/{feature}-assessment.md
- [x] AC6: Output recommendation (Full SDD | Spec-Light | Skip SDD) with confidence
- [x] AC7: Provide specific next-step commands based on recommendation
- [x] AC8: Add "Assessed" state to workflow state machine
- [x] AC9: Support --mode {full|light|skip} flag to override recommendation
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Summary
Implement /jpspec:assess as the mandatory entry point to the jpspec workflow. This command evaluates complexity, risk, and architecture impact to recommend Full SDD, Spec-Light, or Skip SDD.

## Command Usage
```bash
/jpspec:assess Build a user authentication system with OAuth2 and MFA
```

## Assessment Output

### Recommendation Types
| Mode | Criteria | Workflow |
|------|----------|----------|
| **Full SDD** | Complex, high-risk, multi-team | assess → specify → research → plan → implement → validate → operate |
| **Spec-Light** | Medium complexity, moderate risk | assess → specify (light) → plan (minimal) → implement → validate |
| **Skip SDD** | Simple, low-risk, quick fix | assess → implement → validate (tests only) |

### Assessment Report Artifact
Path: `./docs/assess/{feature-slug}-assessment.md`

```markdown
# Assessment: {Feature Name}

## Recommendation: {Full SDD | Spec-Light | Skip SDD}
**Confidence:** {High | Medium | Low}

## Complexity Analysis
| Factor | Score | Notes |
|--------|-------|-------|
| Estimated effort | {X days/weeks} | |
| Component count | {N} | |
| Integration points | {N} | |
| **Complexity Score** | {1-10} | |

## Risk Assessment
| Factor | Level | Notes |
|--------|-------|-------|
| Security implications | {High|Medium|Low} | |
| Compliance requirements | {Yes|No} | |
| Data sensitivity | {High|Medium|Low} | |
| **Risk Score** | {1-10} | |

## Architecture Impact
| Factor | Impact | Notes |
|--------|--------|-------|
| New patterns required | {Yes|No} | |
| Breaking changes | {Yes|No} | |
| Dependencies affected | {list} | |
| **Impact Score** | {1-10} | |

## Recommendation Rationale
{Detailed explanation of why this mode was recommended}

## Next Steps
Based on **{recommendation}** mode:
1. Run: `/jpspec:specify {feature}`
2. Then: {subsequent commands based on mode}

## Override
To override this recommendation:
```bash
/jpspec:specify --mode full {feature}
/jpspec:specify --mode light {feature}
```
```

### Transition Definition
```yaml
assess_to_specified:
  from: "To Do"
  to: "Assessed"
  via: "assess"
  input_artifacts: []  # Entry point - no inputs required
  output_artifacts:
    - type: assessment_report
      path: ./docs/assess/{feature}-assessment.md
      required: true
  validation: NONE  # Always NONE for entry workflow
```

Completed via PR #117
<!-- SECTION:NOTES:END -->
