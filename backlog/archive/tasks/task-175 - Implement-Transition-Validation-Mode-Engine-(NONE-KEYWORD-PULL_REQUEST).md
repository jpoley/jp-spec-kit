---
id: task-175
title: Implement Transition Validation Mode Engine (NONE/KEYWORD/PULL_REQUEST)
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
- [x] AC1: Implement NONE validation mode (immediate pass-through)
- [x] AC2: Implement KEYWORD validation with exact string matching
- [x] AC3: Implement PULL_REQUEST validation with GitHub API check
- [x] AC4: Add validation mode parser for KEYWORD["<string>"] syntax
- [x] AC5: Integrate validation engine into workflow transition logic
- [x] AC6: Add CLI prompts for KEYWORD mode
- [x] AC7: Add helpful error messages for failed validations
- [x] AC8: Support --skip-validation flag for emergency override (with warning)
- [x] AC9: Log all validation decisions for audit trail
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Summary
Implement the core validation engine that enforces transition gates based on the configured validation mode: NONE, KEYWORD["<string>"], or PULL_REQUEST.

## Validation Mode Definitions

### NONE
```yaml
validation: NONE
```
- No gate enforcement
- Transition proceeds immediately after artifacts are created
- Use case: Rapid iteration, solo development, spec-light mode

### KEYWORD["<user-defined>"]
```yaml
validation: KEYWORD["APPROVED"]
validation: KEYWORD["LGTM"]
validation: KEYWORD["PRD_READY"]
```
- User must type the exact keyword (case-sensitive) to proceed
- Prompt displayed: "Type '{keyword}' to approve transition from {from_state} to {to_state}:"
- Invalid input: "Invalid keyword. Expected '{keyword}'. Try again or type 'cancel' to abort."
- Use case: Human approval without PR overhead

### PULL_REQUEST
```yaml
validation: PULL_REQUEST
```
- Transition blocked until a PR containing the output artifact(s) is merged
- Detection: Check if artifact file path exists in merged PR files
- GitHub API integration required: `gh pr list --state merged --json files`
- Use case: Team review, compliance requirements

## Implementation Details

### Validation Engine Interface
```python
class TransitionValidator:
    def validate(self, transition: Transition, context: WorkflowContext) -> ValidationResult:
        """Validate if transition can proceed based on configured mode."""
        
    def check_artifacts_exist(self, artifacts: list[Artifact]) -> bool:
        """Verify all required input artifacts exist."""
        
    def prompt_keyword(self, keyword: str) -> bool:
        """Prompt user for keyword and validate input."""
        
    def check_pr_merged(self, artifacts: list[Artifact]) -> bool:
        """Check if artifacts exist in a merged PR."""
```

### Configuration in jpspec_workflow.yml
```yaml
transitions:
  - name: specify_to_research
    from: "Specified"
    to: "Researched"
    via: "research"
    validation: NONE  # NONE | KEYWORD["..."] | PULL_REQUEST
    
  - name: plan_to_implement
    from: "Planned"
    to: "In Implementation"
    via: "implement"
    validation: KEYWORD["DESIGN_APPROVED"]
```

### CLI Integration
```bash
# Transition attempt
$ specify workflow transition --to "In Implementation"

# NONE mode
✓ Artifacts validated
✓ Transitioning to "In Implementation"

# KEYWORD mode
✓ Artifacts validated
? Type 'DESIGN_APPROVED' to approve transition: DESIGN_APPROVED
✓ Transitioning to "In Implementation"

# PULL_REQUEST mode
✓ Artifacts validated
✗ Waiting for PR containing ./docs/adr/ADR-001-*.md to be merged
  Hint: Create PR with: gh pr create --title "ADR: Feature X"
```

Completed via PR #156
<!-- SECTION:NOTES:END -->
