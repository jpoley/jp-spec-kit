---
id: task-082
title: Problem-Sizing Assessment Command
status: Done
assignee:
  - '@claude-agent'
created_date: '2025-11-27 21:53'
updated_date: '2025-11-29 05:49'
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
Add '/jpspec:assess' command to evaluate if SDD workflow is appropriate for a feature. Addresses Böckeler critique: 'What I found missing is an answer to: Which problems are they meant for?' Prevents over-specification frustration. Output: Full SDD workflow (complex), Spec-light mode (medium), Skip SDD (simple).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Design assessment prompts (LOC estimate, modules affected, integrations, team size)
- [x] #2 Implement decision logic for workflow recommendation
- [x] #3 Create /jpspec:assess command in .claude/commands/jpspec/
- [x] #4 Output clear recommendations with examples
- [x] #5 Integrate with specify init workflow
- [x] #6 Document when to use SDD vs traditional development
- [x] #7 Test with various feature complexity levels
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented comprehensive /jpspec:assess command with:
- 8-question assessment framework covering scope, integration, team, and risk dimensions
- 4-point scoring system (A=1 to D=4) per question, total range 8-32
- Three complexity classifications: Simple (8-12), Medium (13-20), Complex (21-32)
- Clear workflow recommendations: Skip SDD, Spec-Light Mode, Full SDD Workflow
- Detailed examples for each complexity level (bug fix, API endpoint, payment integration)
- Integration guidance for specify init workflow
- Documentation explaining when to use SDD vs traditional development
- 35 comprehensive tests verifying all acceptance criteria
- All tests passing (100% coverage of requirements)
<!-- SECTION:NOTES:END -->
