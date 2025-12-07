---
id: task-300
title: Implement Git Push Rules Enforcement System
status: In Progress
assignee:
  - '@pm-planner'
created_date: '2025-12-07 20:38'
updated_date: '2025-12-07 20:58'
labels:
  - feature
  - git-workflow
  - infrastructure
  - 'workflow:Planned'
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a comprehensive git workflow enforcement system including:
1. push-rules.md configuration file defining mandatory checks
2. Pre-push validation hooks
3. github-janitor agent for post-validation cleanup
4. Integration with existing /jpspec:validate workflow
5. Warning system for uncompleted janitor tasks

This is the parent feature task that will be decomposed into atomic implementation tasks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 push-rules.md file is created and validated on every PR
- [ ] #2 Rebase enforcement is active (no merge commits allowed)
- [ ] #3 Linting and testing must pass before push (no exceptions)
- [ ] #4 github-janitor agent is defined and invocable
- [ ] #5 Warning system alerts when janitor hasn't run post-validation
- [ ] #6 Integration with existing /jpspec:validate workflow
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Specification Complete (2025-12-07)

PRD created at: docs/prd/git-push-rules-enforcement-prd.md

Implementation tasks created:
- task-301: push-rules.md template and validation
- task-302: Pre-push hook implementation
- task-303: github-janitor agent definition
- task-304: /jpspec:validate integration
- task-305: Janitor warning system
- task-306: Rebase enforcement
- task-307: specify init updates

Workflow state: Specified → Ready for /jpspec:plan

## Planning Complete (2025-12-07)

### Architecture Deliverables
- ADR-012: docs/adr/ADR-012-push-rules-enforcement-architecture.md (29KB)
- Platform Design: docs/platform/push-rules-platform-design.md (30KB)

### Key Architectural Decisions
1. **Configuration**: Structured markdown with YAML frontmatter (push-rules.md)
2. **Enforcement**: Sequential validation pipeline (fail-fast gates)
3. **Cleanup**: Agent-based janitor (not daemon)
4. **State**: File-based (.specify/state/)
5. **Warnings**: Session-start integration (non-blocking)

### Implementation Tasks with Plans
- task-301: Template + validation schema (has plan)
- task-302: Rebase enforcement (has plan)
- task-303: specify init updates (has plan)
- task-304: Janitor integration
- task-305: Warning system
- task-306: Architecture ADR (DONE)
- task-307: Platform design (DONE)

Workflow state: Planned → Ready for /jpspec:implement
<!-- SECTION:NOTES:END -->
