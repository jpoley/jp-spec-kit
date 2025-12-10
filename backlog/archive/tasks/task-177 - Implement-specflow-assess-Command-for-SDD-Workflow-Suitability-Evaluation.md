---
id: task-177
title: 'Implement /specflow:assess Command for SDD Workflow Suitability Evaluation'
status: To Do
assignee: []
created_date: '2025-11-30 20:07'
updated_date: '2025-11-30 20:08'
labels:
  - workflow-artifacts
  - critical
dependencies: []
priority: high
---

<!-- AC:END -->

<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Summary
Implement the /specflow:assess command as the entry point to the specflow workflow. This command evaluates whether the full SDD workflow is appropriate for a given feature and outputs a recommendation (Full/Light/Skip).

## Command Purpose

Before starting any specflow workflow, users run:
```bash
/specflow:assess Build a user authentication system
```

## Assessment Criteria

| Factor | Full SDD | Spec-Light | Skip SDD |
|--------|----------|------------|----------|
| Complexity | Multi-component, >1 week | Medium, 2-5 days | Simple, <1 day |
| Risk | Security/compliance critical | Moderate | Low |
| Team size | >2 engineers | 1-2 engineers | Solo |
| Dependencies | External services, APIs | Internal only | None |
| Architecture impact | New patterns/systems | Extends existing | None |

## Output Artifact

### Assessment Report
Path: `./docs/assess/{feature-slug}-assessment.md`

```markdown
# Assessment: {Feature Name}

## Recommendation: {Full SDD | Spec-Light | Skip SDD}

## Complexity Analysis
- Estimated effort: {X days/weeks}
- Component count: {N}
- Integration points: {N}

## Risk Assessment
- Security implications: {High | Medium | Low}
- Compliance requirements: {Yes | No}
- Data sensitivity: {High | Medium | Low}

## Architecture Impact
- New patterns required: {Yes | No}
- Breaking changes: {Yes | No}
- Dependencies affected: {list}

## Recommendation Rationale
{Explanation of why Full/Light/Skip was recommended}

## Next Steps
{Specific commands to run based on recommendation}
```

## Workflow Modes

### Full SDD
All phases required:
```
assess → specify → research → plan → implement → validate → operate
```

### Spec-Light
Reduced artifacts:
```
assess → specify (light PRD) → plan (minimal ADR) → implement → validate
```

### Skip SDD
Direct to implementation:
```
assess → implement → validate (tests only)
```

## Acceptance Criteria
- [ ] AC1: Create .claude/commands/specflow/assess.md command template
- [ ] AC2: Implement complexity scoring algorithm (effort, components, integrations)
- [ ] AC3: Implement risk scoring (security, compliance, data sensitivity)
- [ ] AC4: Implement architecture impact analysis
- [ ] AC5: Generate assessment report at ./docs/assess/{feature}-assessment.md
- [ ] AC6: Output recommendation with confidence score
- [ ] AC7: Provide specific next-step commands based on recommendation
- [ ] AC8: Add assessment to specflow_workflow.yml as entry workflow
- [ ] AC9: Allow user to override recommendation with --mode {full|light|skip} flag

## Integration Points
- Output assessment report is input to /specflow:specify
- Assessment mode determines required artifacts for downstream phases
- Recommendation stored in workflow state for gate validation
<!-- SECTION:NOTES:END -->
