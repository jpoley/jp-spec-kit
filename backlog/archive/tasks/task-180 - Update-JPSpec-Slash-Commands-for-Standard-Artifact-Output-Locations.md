---
id: task-180
title: Update JPSpec Slash Commands for Standard Artifact Output Locations
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
- [x] AC1: Update /jpspec:assess to output to ./docs/assess/
- [x] AC2: Update /jpspec:specify to output PRD to ./docs/prd/
- [x] AC3: Update /jpspec:research to output to ./docs/research/
- [x] AC4: Update /jpspec:plan to output ADRs to ./docs/adr/
- [x] AC5: Update /jpspec:implement to generate ./tests/ac-coverage.json
- [x] AC6: Update /jpspec:validate to output to ./docs/qa/ and ./docs/security/
- [x] AC7: Add feature name slug derivation to all commands
- [x] AC8: Add artifact verification step to all commands
- [x] AC9: Add transition validation check to all commands
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Summary
Update all /jpspec:* slash commands to output artifacts at standardized locations and verify artifact creation before completing.

## Artifact Output Mapping

| Command | Artifact Type | Output Location |
|---------|---------------|-----------------|
| /jpspec:assess | assessment_report | ./docs/assess/{feature}-assessment.md |
| /jpspec:specify | prd | ./docs/prd/{feature}.md |
| /jpspec:specify | backlog_tasks | ./backlog/tasks/*.md |
| /jpspec:research | research_report | ./docs/research/{feature}-research.md |
| /jpspec:research | business_validation | ./docs/research/{feature}-validation.md |
| /jpspec:plan | adr | ./docs/adr/ADR-{NNN}-{slug}.md |
| /jpspec:plan | platform_design | ./docs/platform/{feature}-platform.md |
| /jpspec:implement | source_code | ./src/ (project-specific) |
| /jpspec:implement | tests | ./tests/ |
| /jpspec:implement | ac_coverage | ./tests/ac-coverage.json |
| /jpspec:validate | qa_report | ./docs/qa/{feature}-qa-report.md |
| /jpspec:validate | security_report | ./docs/security/{feature}-security.md |
| /jpspec:operate | deployment_manifest | ./deploy/ or ./k8s/ |

## Command Template Updates

Each slash command (.claude/commands/jpspec/*.md) must include:

### 1. Output Artifacts Section
```markdown
## Output Artifacts
| Artifact | Location | Required |
|----------|----------|----------|
| PRD | ./docs/prd/{FEATURE_NAME}.md | Yes |
| Backlog Tasks | ./backlog/tasks/*.md | Yes |
```

### 2. Feature Name Derivation
```markdown
## Feature Naming
- Derive FEATURE_NAME from user input
- Convert to slug format: lowercase, hyphens, no spaces
- Example: "User Authentication System" → "user-authentication-system"
```

### 3. Artifact Verification Step
```markdown
## Completion Checklist
Before completing this workflow:
- [ ] Primary artifact exists at expected path
- [ ] Artifact contains all required sections
- [ ] Artifact passes structural validation
- [ ] Transition validation mode satisfied
```

### 4. Transition Validation
```markdown
## Transition Validation
Current validation mode: {VALIDATION_MODE}

If NONE: Proceed immediately
If KEYWORD["X"]: Prompt user for keyword
If PULL_REQUEST: Check for merged PR
```

Completed via PR #144
<!-- SECTION:NOTES:END -->
