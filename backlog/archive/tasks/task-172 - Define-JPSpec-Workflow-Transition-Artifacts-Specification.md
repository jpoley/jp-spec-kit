---
id: task-172
title: Define JPSpec Workflow Transition Artifacts Specification
status: To Do
assignee: []
created_date: '2025-11-30 20:05'
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
Define the complete input/output artifacts for each JPSpec workflow transition to ensure clear deliverables at each phase boundary.

## Workflow Artifact Matrix

| Transition | Input Artifacts | Output Artifacts | Validation |
|------------|-----------------|------------------|------------|
| assess → specify | User feature request | Assessment report (Full/Light/Skip) | Human review |
| specify → research | Assessment report | PRD (./docs/prd/{feature}.md) | Configurable |
| research → plan | PRD | Research report, Business validation | Configurable |
| plan → implement | PRD + Research | ADR (./docs/adr/{feature}-*.md) | Configurable |
| implement → validate | ADR + Architecture | Code + Runnable tests | CI gate |
| validate → operate | Tested code | QA report, Security report, Docs | Human/PR |
| operate → done | Validated release | Deployment confirmation | SRE review |

## Acceptance Criteria
- [ ] AC1: Create specflow_workflow_artifacts.yml schema defining all input/output artifacts
- [ ] AC2: Document artifact locations (./docs/prd, ./docs/adr, ./tests)
- [ ] AC3: Define artifact format specifications (markdown structure)
- [ ] AC4: Add artifact validation rules to workflow transitions
- [ ] AC5: Update specflow_workflow.yml to include artifact requirements

## Technical Notes
- Extends existing specflow_workflow.yml schema
- Artifacts should be machine-verifiable where possible
- Human review should be the default validation mode
<!-- SECTION:NOTES:END -->
