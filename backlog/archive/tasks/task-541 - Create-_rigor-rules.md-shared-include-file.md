---
id: task-541
title: Create _rigor-rules.md shared include file
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-12-17 16:40'
updated_date: '2025-12-17 17:31'
labels:
  - rigor
  - foundation
  - implement
  - 'workflow:Validated'
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create the shared include file containing all task rigor rules organized by workflow phase. This file will be included by all /flow:* commands to enforce consistent rigor across the development lifecycle.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create templates/partials/flow/_rigor-rules.md with all rules from task-rigor.md
- [x] #2 Organize rules by phase: Setup, Execution, Freeze, Validation, PR
- [x] #3 Include enforcement mode configuration (strict/warn/off)
- [x] #4 Add symlink in .claude/partials/flow/_rigor-rules.md
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create _rigor-rules.md with all 23 rules organized by phase
2. Add enforcement mode configuration (strict/warn/off)
3. Include helper script references
4. Add integration point documentation
5. Create symlink in .claude/commands/flow/
6. Update memory/README.md with rigor rules reference
<!-- SECTION:PLAN:END -->
