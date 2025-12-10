---
id: task-175
title: Implement Configurable Artifact Validation Mode Toggle
status: To Do
assignee: []
created_date: '2025-11-30 20:06'
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
Implement a configurable validation mode system that allows each workflow transition artifact (PRD, ADR, Tests) to be validated via different mechanisms based on team preferences.

## Validation Mode Configuration

### Config Location
`specflow_workflow.yml` workflow-level and project-level settings:

```yaml
version: "1.0"

# Project-level defaults
defaults:
  validation_mode: human_review  # Default for all artifacts

workflows:
  specify:
    output_artifacts:
      - type: prd
        path: ./docs/prd/{feature}.md
        validation_mode: human_review  # Override project default
        required: true
    
  plan:
    input_artifacts:
      - type: prd
        validation: required
    output_artifacts:
      - type: adr
        path: ./docs/adr/ADR-{NNN}-{slug}.md
        validation_mode: pr_review  # Different mode per artifact
        required: true
```

### Validation Modes

| Mode | Behavior | Use Case |
|------|----------|----------|
| `human_review` | Pause workflow, prompt user for approval | Default, highest rigor |
| `pr_review` | Artifact validated when PR containing it is merged | Team review workflow |
| `auto` | Structural validation only (schema check) | Spec-light mode, rapid iteration |
| `skip` | No validation (use sparingly) | Emergency/hotfix workflows |

### Validation Flow
```
Workflow attempts transition
  ↓
Check artifact exists at expected path
  ↓
Based on validation_mode:
  - human_review → Prompt user, wait for approval
  - pr_review → Check if artifact is in merged PR
  - auto → Run schema validator
  - skip → Allow immediately
  ↓
Proceed or block transition
```

## Acceptance Criteria
- [ ] AC1: Add validation_mode field to workflow artifact schema
- [ ] AC2: Implement human_review validation (prompt + await input)
- [ ] AC3: Implement pr_review validation (check GitHub PR status)
- [ ] AC4: Implement auto validation (JSON/YAML schema check)
- [ ] AC5: Add project-level defaults.validation_mode config
- [ ] AC6: Allow per-artifact validation_mode override
- [ ] AC7: Update CLI to show validation status during workflow execution
- [ ] AC8: Add --validation-mode flag to specflow commands for one-time override

## Dependencies
- task-172 (Workflow Artifacts Specification)
- task-173 (PRD Requirement Gate)
- task-174 (ADR Requirement Gate)
<!-- SECTION:NOTES:END -->
