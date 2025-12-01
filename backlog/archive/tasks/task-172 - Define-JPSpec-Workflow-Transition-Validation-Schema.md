---
id: task-172
title: Define JPSpec Workflow Transition Validation Schema
status: Done
assignee: []
created_date: '2025-11-30 21:31'
updated_date: '2025-12-01 01:53'
labels:
  - workflow-artifacts
  - critical
dependencies: []
priority: high
---

<!-- AC:BEGIN -->
- [x] AC1: Define transition schema with input_artifacts, output_artifacts, validation fields
- [x] AC2: Document all 7 workflow transitions with complete artifact specifications
- [x] AC3: Create validation mode enum: NONE | KEYWORD["<string>"] | PULL_REQUEST
- [x] AC4: Set all transitions to validation: NONE as default
- [x] AC5: Add transition schema to jpspec_workflow.yml
- [x] AC6: Create validation for transition definitions (all 3 fields required)
- [x] AC7: Document artifact path patterns ({feature}, {NNN}, {slug} variables)
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Summary
Define the complete input/output artifacts and validation gates for each JPSpec workflow transition. Each transition MUST define its validation mode.

## Validation Mode Types

| Mode | Syntax | Behavior |
|------|--------|----------|
| `NONE` | `validation: NONE` | No gate - transition proceeds automatically |
| `KEYWORD` | `validation: KEYWORD["APPROVED"]` | User must type exact keyword to proceed |
| `PULL_REQUEST` | `validation: PULL_REQUEST` | Transition blocked until PR containing artifact is merged |

## Transition Definitions

Every workflow transition MUST define:
1. **Input artifacts** - What must exist before transition
2. **Output artifacts** - What is produced by the workflow
3. **Validation mode** - NONE, KEYWORD["..."], or PULL_REQUEST

### Complete Transition Matrix

```yaml
transitions:
  assess_to_specified:
    from: "To Do"
    to: "Assessed"
    via: "assess"
    input_artifacts: []
    output_artifacts:
      - type: assessment_report
        path: ./docs/assess/{feature}-assessment.md
    validation: NONE  # Default

  specified_to_researched:
    from: "Assessed"
    to: "Specified"
    via: "specify"
    input_artifacts:
      - type: assessment_report
        path: ./docs/assess/{feature}-assessment.md
    output_artifacts:
      - type: prd
        path: ./docs/prd/{feature}.md
      - type: backlog_tasks
        path: ./backlog/tasks/*.md
    validation: NONE  # Default (configurable)

  researched_to_planned:
    from: "Specified"
    to: "Researched"
    via: "research"
    input_artifacts:
      - type: prd
        path: ./docs/prd/{feature}.md
    output_artifacts:
      - type: research_report
        path: ./docs/research/{feature}-research.md
      - type: business_validation
        path: ./docs/research/{feature}-validation.md
    validation: NONE  # Default

  planned_to_implementing:
    from: "Researched"
    to: "Planned"
    via: "plan"
    input_artifacts:
      - type: prd
        path: ./docs/prd/{feature}.md
      - type: research_report
        path: ./docs/research/{feature}-research.md
    output_artifacts:
      - type: adr
        path: ./docs/adr/ADR-{NNN}-{slug}.md
      - type: platform_design
        path: ./docs/platform/{feature}-platform.md
    validation: NONE  # Default

  implementing_to_validated:
    from: "Planned"
    to: "In Implementation"
    via: "implement"
    input_artifacts:
      - type: adr
        path: ./docs/adr/ADR-{NNN}-{slug}.md
    output_artifacts:
      - type: source_code
        path: ./src/
      - type: tests
        path: ./tests/
      - type: ac_coverage
        path: ./tests/ac-coverage.json
    validation: NONE  # Default

  validated_to_deployed:
    from: "In Implementation"
    to: "Validated"
    via: "validate"
    input_artifacts:
      - type: source_code
      - type: tests
      - type: ac_coverage
    output_artifacts:
      - type: qa_report
        path: ./docs/qa/{feature}-qa-report.md
      - type: security_report
        path: ./docs/security/{feature}-security.md
    validation: NONE  # Default

  deployed_to_done:
    from: "Validated"
    to: "Deployed"
    via: "operate"
    input_artifacts:
      - type: qa_report
      - type: security_report
    output_artifacts:
      - type: deployment_manifest
        path: ./deploy/
    validation: NONE  # Default
```

Completed via PR #113
<!-- SECTION:NOTES:END -->
