---
id: task-178
title: Update jpspec_workflow.yml with Transition Artifact Definitions
status: Done
assignee: []
created_date: '2025-11-30 21:33'
updated_date: '2025-12-01 01:53'
labels:
  - workflow-artifacts
  - critical
dependencies: []
priority: high
---

<!-- AC:BEGIN -->
- [x] AC1: Add "Assessed" state to states array
- [x] AC2: Add assess workflow with workflow-assessor agent
- [x] AC3: Add input_artifacts and output_artifacts to all transitions
- [x] AC4: Set validation: NONE for all transitions (default)
- [x] AC5: Add validation field schema (NONE | KEYWORD["..."] | PULL_REQUEST)
- [x] AC6: Update metadata counts
- [x] AC7: Add workflow-assessor to agent_loops (outer loop)
- [x] AC8: Run test_workflow_config_valid.py to verify schema
- [x] AC9: Document transition artifact path variables ({feature}, {NNN}, {slug})
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Summary
Update the jpspec_workflow.yml configuration to include all transition definitions with input/output artifacts and validation modes.

## Schema Updates

### New State: Assessed
```yaml
states:
  - "To Do"        # Initial state
  - "Assessed"     # NEW: After /jpspec:assess
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
    command: "/jpspec:assess"
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
```

### Complete Transition Definitions
```yaml
transitions:
  # Entry transition
  - name: assess
    from: "To Do"
    to: "Assessed"
    via: "assess"
    input_artifacts: []
    output_artifacts:
      - type: assessment_report
        path: ./docs/assess/{feature}-assessment.md
    validation: NONE

  # Specify transition
  - name: specify
    from: "Assessed"
    to: "Specified"
    via: "specify"
    input_artifacts:
      - type: assessment_report
        path: ./docs/assess/{feature}-assessment.md
        required: true
    output_artifacts:
      - type: prd
        path: ./docs/prd/{feature}.md
        required: true
      - type: backlog_tasks
        path: ./backlog/tasks/*.md
        required: true
    validation: NONE

  # Research transition (optional)
  - name: research
    from: "Specified"
    to: "Researched"
    via: "research"
    input_artifacts:
      - type: prd
        path: ./docs/prd/{feature}.md
        required: true
    output_artifacts:
      - type: research_report
        path: ./docs/research/{feature}-research.md
      - type: business_validation
        path: ./docs/research/{feature}-validation.md
    validation: NONE

  # Plan transition
  - name: plan
    from: ["Specified", "Researched"]
    to: "Planned"
    via: "plan"
    input_artifacts:
      - type: prd
        path: ./docs/prd/{feature}.md
        required: true
    output_artifacts:
      - type: adr
        path: ./docs/adr/ADR-{NNN}-{slug}.md
        required: true
        multiple: true
    validation: NONE

  # Implement transition
  - name: implement
    from: "Planned"
    to: "In Implementation"
    via: "implement"
    input_artifacts:
      - type: adr
        path: ./docs/adr/ADR-*.md
        required: true
    output_artifacts:
      - type: source_code
        path: ./src/
      - type: tests
        path: ./tests/
        required: true
      - type: ac_coverage
        path: ./tests/ac-coverage.json
        required: true
    validation: NONE

  # Validate transition
  - name: validate
    from: "In Implementation"
    to: "Validated"
    via: "validate"
    input_artifacts:
      - type: tests
        required: true
      - type: ac_coverage
        required: true
    output_artifacts:
      - type: qa_report
        path: ./docs/qa/{feature}-qa-report.md
      - type: security_report
        path: ./docs/security/{feature}-security.md
    validation: NONE

  # Operate transition
  - name: operate
    from: "Validated"
    to: "Deployed"
    via: "operate"
    input_artifacts:
      - type: qa_report
      - type: security_report
    output_artifacts:
      - type: deployment_manifest
        path: ./deploy/
    validation: NONE

  # Terminal transition
  - name: complete
    from: "Deployed"
    to: "Done"
    via: "manual"
    validation: NONE
```

Completed via PR #125
<!-- SECTION:NOTES:END -->
