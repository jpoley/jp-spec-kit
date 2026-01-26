---
id: task-587
title: 'SPEC-002: Implement /flow:orchestrate command pattern'
status: To Do
assignee: []
created_date: '2026-01-24 15:35'
labels:
  - commands
  - orchestration
  - agents
  - phase-2
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add orchestration command to chain agents sequentially with context handoff.

**Problem**: Flowspec lacks a way to chain agents with structured handoff.

**Solution**: /flow:orchestrate command with workflow types.

**Workflow Types**:
- feature: planner -> tdd-guide -> code-reviewer -> security-reviewer
- bugfix: explorer -> tdd-guide -> code-reviewer
- refactor: architect -> code-reviewer -> tdd-guide
- security: security-reviewer -> code-reviewer -> architect
- custom: <agents> <description>

**Handoff Document Format**:
```markdown
## HANDOFF: [previous-agent] -> [next-agent]
### Context
### Findings
### Files Modified
### Open Questions
### Recommendations
```

**Source**: docs/specs/flowspec-improvement-specs-v1.md
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Handoff documents persist between agents
- [ ] #2 Parallel execution supported for independent agents
- [ ] #3 Final report aggregates all agent outputs
- [ ] #4 Custom workflows via 'custom <agents> <description>'
<!-- AC:END -->
