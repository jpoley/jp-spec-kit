---
id: task-082
title: Problem-Sizing Assessment Command
status: In Progress
assignee:
  - '@claude-agent-10'
created_date: '2025-11-27 21:53'
updated_date: '2025-11-28 18:39'
labels:
  - jpspec
  - feature
  - ux
  - P0
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add '/jpspec:assess' command to evaluate if SDD workflow is appropriate for a feature. Addresses Böckeler critique: 'What I found missing is an answer to: Which problems are they meant for?' Prevents over-specification frustration. Output: Full SDD workflow (complex), Spec-light mode (medium), Skip SDD (simple). See TODO/task-20-suggestions.md and TODO/task-015-summary.md for implementation details.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Design assessment prompts (LOC estimate, modules affected, integrations, team size)
- [ ] #2 Implement decision logic for workflow recommendation
- [ ] #3 Create /jpspec:assess command in .claude/commands/jpspec/
- [ ] #4 Output clear recommendations with examples
- [ ] #5 Integrate with specify init workflow
- [ ] #6 Document when to use SDD vs traditional development
- [ ] #7 Test with various feature complexity levels
<!-- AC:END -->
