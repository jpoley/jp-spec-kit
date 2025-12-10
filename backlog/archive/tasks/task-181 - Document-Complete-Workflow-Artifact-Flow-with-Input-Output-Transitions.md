---
id: task-181
title: Document Complete Workflow Artifact Flow with Input/Output Transitions
status: To Do
assignee: []
created_date: '2025-11-30 20:08'
updated_date: '2025-11-30 20:08'
labels:
  - workflow-artifacts
  - critical
dependencies: []
priority: high
---

<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Summary
Create comprehensive documentation of the complete specflow workflow showing all artifacts, their inputs, outputs, and validation requirements at each transition.

## Documentation Deliverable

Create `docs/reference/workflow-artifact-flow.md`:

```markdown
# JPSpec Workflow Artifact Flow

## Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          JPSpec Workflow Pipeline                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────┐        ┌──────────┐        ┌──────────┐        ┌──────────┐
│  ASSESS  │───────▶│ SPECIFY  │───────▶│ RESEARCH │───────▶│   PLAN   │
└──────────┘        └──────────┘        └──────────┘        └──────────┘
     │                   │                   │                   │
     ▼                   ▼                   ▼                   ▼
┌──────────┐        ┌──────────┐        ┌──────────┐        ┌──────────┐
│Assessment│        │   PRD    │        │ Research │        │   ADRs   │
│  Report  │        │          │        │  Report  │        │          │
└──────────┘        └──────────┘        └──────────┘        └──────────┘
     │                   │                   │                   │
     └───────────────────┴───────────────────┴───────────────────┘
                                    │
                                    ▼
                            ┌──────────────┐
                            │  IMPLEMENT   │
                            └──────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────┐
                    │  Code + Tests + AC Map    │
                    └───────────────────────────┘
                                    │
                                    ▼
                            ┌──────────────┐
                            │   VALIDATE   │
                            └──────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────┐
                    │ QA + Security + Docs      │
                    └───────────────────────────┘
                                    │
                                    ▼
                            ┌──────────────┐
                            │   OPERATE    │
                            └──────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────┐
                    │     Deployed System       │
                    └───────────────────────────┘
```

## Transition Details

### Transition 1: Entry → Assessed
**Command:** `/specflow:assess`
**Input:** User feature description (free text)
**Output:** Assessment Report
**Location:** `./docs/assess/{feature}-assessment.md`
**Validation:** Auto (structural check)
**Gate:** None (entry point)

### Transition 2: Assessed → Specified  
**Command:** `/specflow:specify`
**Input:** Assessment Report
**Output:** PRD + Backlog Tasks
**Location:** `./docs/prd/{feature}.md`, `./backlog/tasks/*.md`
**Validation:** human_review (default) | pr_review | auto
**Gate:** Assessment report must exist

[... continue for all transitions ...]
```

## Acceptance Criteria
- [ ] AC1: Create docs/reference/workflow-artifact-flow.md with complete diagram
- [ ] AC2: Document each transition with input/output/validation details
- [ ] AC3: Include artifact location table with file paths
- [ ] AC4: Add validation mode options for each artifact type
- [ ] AC5: Document rework/rollback transitions and their artifact impacts
- [ ] AC6: Include examples of artifact content at each stage
- [ ] AC7: Cross-reference with specflow_workflow.yml for programmatic lookup
- [ ] AC8: Add troubleshooting section for common artifact validation failures

## Dependencies
- task-172 (Workflow Artifacts Specification)
- task-178 (State Machine Update)
<!-- SECTION:NOTES:END -->
