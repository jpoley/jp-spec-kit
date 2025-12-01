---
priority: high
id: task-107
title: Create shared backlog.md instructions template for agents
status: Done
assignee:
  - '@claude'
created_date: '2025-11-28 16:55'
updated_date: '2025-11-29'
labels:
  - jpspec
  - backlog-integration
  - P0
  - template
dependencies:
  - task-106
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a reusable _backlog-instructions.md template that can be injected into all jpspec agent prompts, ensuring consistent backlog.md CLI usage patterns.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Template file created at .claude/commands/jpspec/_backlog-instructions.md
- [x] #2 Template includes task discovery instructions (backlog search, backlog task list)
- [x] #3 Template includes task assignment workflow (backlog task edit -a)
- [x] #4 Template includes AC tracking instructions (--check-ac pattern)
- [x] #5 Template includes implementation notes pattern
- [x] #6 Template includes Definition of Done checklist
<!-- AC:END -->

## Implementation Notes
<!-- NOTES:BEGIN -->
Implemented shared backlog.md instructions template for all jpspec agents.

Deliverables:
- Created .claude/commands/jpspec/_backlog-instructions.md with comprehensive instructions
- Template includes task discovery (search, list commands)
- Template includes task assignment workflow with -a flag
- Template includes AC tracking with --check-ac pattern
- Template includes implementation notes patterns
- Template includes full Definition of Done checklist
- Also created templates/partials/backlog-instructions.md (alternate location)

The template is now used by all jpspec agent prompts for consistent backlog.md CLI usage.
<!-- NOTES:END -->
