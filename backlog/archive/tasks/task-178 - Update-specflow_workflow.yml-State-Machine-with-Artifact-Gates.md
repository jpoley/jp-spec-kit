---
id: task-178
title: Update specflow_workflow.yml State Machine with Artifact Gates
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Summary
Update the specflow_workflow.yml configuration to include the new assess workflow and artifact requirement gates for each transition.

## Schema Updates

### New State: Assessed
Add "Assessed" state between entry and "Specified":

```yaml
states:
  - "To Do"        # Initial state
  - "Assessed"     # NEW: After /specflow:assess
  - "Specified"
  - "Researched"
  - "Planned"
  - "In Implementation"
  - "Validated"
  - "Deployed"
  - "Done"
```

### New Workflow: assess
```yaml
workflows:
  assess:
    command: "/specflow:assess"
    description: "Evaluate SDD workflow suitability (Full/Light/Skip)"
    agents:
      - name: "workflow-assessor"
        identity: "@workflow-assessor"
        description: "Evaluates complexity, risk, and architecture impact"
        responsibilities:
          - "Complexity analysis"
          - "Risk assessment"
          - "Architecture impact evaluation"
          - "Workflow mode recommendation"
    input_states:
      - "To Do"
    output_state: "Assessed"
    optional: false
    output_artifacts:
      - type: assessment_report
        path: ./docs/assess/{feature}-assessment.md
        required: true
```

### Artifact Requirements per Workflow
Add to each workflow definition:

```yaml
workflows:
  specify:
    # ... existing fields ...
    input_artifacts:
      - type: assessment_report
        validation: required
    output_artifacts:
      - type: prd
        path: ./docs/prd/{feature}.md
        validation_mode: human_review
        required: true

  plan:
    input_artifacts:
      - type: prd
        validation: required
    output_artifacts:
      - type: adr
        path: ./docs/adr/ADR-{NNN}-{slug}.md
        validation_mode: human_review
        required: true

  implement:
    input_artifacts:
      - type: adr
        validation: required
    output_artifacts:
      - type: source_code
        validation: ci_pass
      - type: tests
        path: ./tests/
        validation_mode: auto
        required: true
      - type: ac_coverage
        path: ./tests/ac-coverage.json
        validation_mode: auto
        required: true
```

## Acceptance Criteria
- [ ] AC1: Add "Assessed" state to states array
- [ ] AC2: Add assess workflow definition with workflow-assessor agent
- [ ] AC3: Add input_artifacts and output_artifacts to all existing workflows
- [ ] AC4: Add transitions from "To Do" → "Assessed" → "Specified"
- [ ] AC5: Update metadata counts (state_count, workflow_count, agent_count)
- [ ] AC6: Update agent_loops to classify workflow-assessor (outer loop)
- [ ] AC7: Add artifact schema definition to JSON Schema section
- [ ] AC8: Run test_workflow_config_valid.py to verify state machine integrity

## Dependencies
- task-172 (Workflow Artifacts Specification)
<!-- SECTION:NOTES:END -->
