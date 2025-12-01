---
id: task-181
title: Document Complete Workflow Artifact Flow with Transition Validation
status: Done
assignee: []
created_date: '2025-11-30 21:34'
updated_date: '2025-12-01 01:53'
labels:
  - workflow-artifacts
  - critical
dependencies: []
priority: high
---

<!-- AC:BEGIN -->
- [x] AC1: Create docs/reference/workflow-artifact-flow.md
- [x] AC2: Include ASCII workflow diagram
- [x] AC3: Document all 8 transitions with complete details
- [x] AC4: Create artifact location reference table
- [x] AC5: Document validation modes with examples
- [x] AC6: Include rework/rollback transition handling
- [x] AC7: Add troubleshooting section for validation failures
- [x] AC8: Cross-reference jpspec_workflow.yml for programmatic lookup
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Summary
Create comprehensive documentation of the complete jpspec workflow showing all artifacts, transitions, and validation modes.

## Documentation Deliverable

Create `docs/reference/workflow-artifact-flow.md`:

### Workflow Pipeline Diagram
```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    JPSpec Workflow Pipeline with Artifacts                    │
└──────────────────────────────────────────────────────────────────────────────┘

 ┌─────────┐      ┌─────────┐      ┌─────────┐      ┌─────────┐
 │ ASSESS  │─────▶│ SPECIFY │─────▶│RESEARCH │─────▶│  PLAN   │
 └────┬────┘      └────┬────┘      └────┬────┘      └────┬────┘
      │                │                │                │
      ▼                ▼                ▼                ▼
 ┌─────────┐      ┌─────────┐      ┌─────────┐      ┌─────────┐
 │Assessment│      │  PRD    │      │Research │      │  ADRs   │
 │ Report  │      │         │      │ Report  │      │         │
 └─────────┘      └─────────┘      └─────────┘      └─────────┘
      │                │                │                │
      └────────────────┴────────────────┴────────────────┘
                              │
                              ▼
                     ┌──────────────┐
                     │  IMPLEMENT   │
                     └──────┬───────┘
                            │
                            ▼
            ┌────────────────────────────┐
            │ Code + Tests + AC Coverage │
            └────────────┬───────────────┘
                         │
                         ▼
                  ┌──────────────┐
                  │   VALIDATE   │
                  └──────┬───────┘
                         │
                         ▼
            ┌────────────────────────────┐
            │  QA Report + Security      │
            └────────────┬───────────────┘
                         │
                         ▼
                  ┌──────────────┐
                  │   OPERATE    │
                  └──────┬───────┘
                         │
                         ▼
            ┌────────────────────────────┐
            │   Deployed System (Done)   │
            └────────────────────────────┘
```

### Complete Transition Reference Table

| # | From State | To State | Command | Input Artifacts | Output Artifacts | Validation |
|---|------------|----------|---------|-----------------|------------------|------------|
| 1 | To Do | Assessed | /jpspec:assess | (none) | Assessment Report | NONE |
| 2 | Assessed | Specified | /jpspec:specify | Assessment Report | PRD, Backlog Tasks | NONE |
| 3 | Specified | Researched | /jpspec:research | PRD | Research Report, Business Validation | NONE |
| 4 | Researched | Planned | /jpspec:plan | PRD, Research Report | ADRs | NONE |
| 5 | Planned | In Implementation | /jpspec:implement | ADRs | Code, Tests, AC Coverage | NONE |
| 6 | In Implementation | Validated | /jpspec:validate | Tests, AC Coverage | QA Report, Security Report | NONE |
| 7 | Validated | Deployed | /jpspec:operate | QA Report, Security Report | Deployment Manifest | NONE |
| 8 | Deployed | Done | manual | (all prior) | (completed) | NONE |

### Artifact Location Reference

| Artifact Type | Directory | Filename Pattern | Example |
|---------------|-----------|------------------|---------|
| Assessment Report | ./docs/assess/ | {feature}-assessment.md | user-auth-assessment.md |
| PRD | ./docs/prd/ | {feature}.md | user-auth.md |
| Research Report | ./docs/research/ | {feature}-research.md | user-auth-research.md |
| Business Validation | ./docs/research/ | {feature}-validation.md | user-auth-validation.md |
| ADR | ./docs/adr/ | ADR-{NNN}-{slug}.md | ADR-001-oauth-strategy.md |
| QA Report | ./docs/qa/ | {feature}-qa-report.md | user-auth-qa-report.md |
| Security Report | ./docs/security/ | {feature}-security.md | user-auth-security.md |
| AC Coverage | ./tests/ | ac-coverage.json | ac-coverage.json |

### Validation Modes Reference

| Mode | Syntax | Behavior | Use Case |
|------|--------|----------|----------|
| NONE | `validation: NONE` | Pass immediately | Default, rapid iteration |
| KEYWORD | `validation: KEYWORD["APPROVED"]` | User types keyword | Human approval |
| PULL_REQUEST | `validation: PULL_REQUEST` | PR must be merged | Team review |

Completed via PR #138
<!-- SECTION:NOTES:END -->
