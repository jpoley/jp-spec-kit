---
id: task-133
title: Write comprehensive /jpspec workflow documentation
status: In Progress
assignee:
  - '@claude-agent'
created_date: '2025-11-28 17:15'
updated_date: '2025-11-29 05:55'
labels:
  - documentation
dependencies:
  - task-131
  - task-132
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a polished, production-quality markdown document that explains the /jpspec command orchestration system. This document should serve as the authoritative reference for understanding how the slash commands work, when to use each one, and how the specialized agents collaborate. Embed both the Mermaid and Excalidraw diagrams.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Document includes executive summary explaining the purpose and value of the /jpspec workflow system
- [x] #2 Each of the 6 /jpspec commands has a dedicated section with: purpose, when to use, agents invoked, execution pattern, inputs/outputs
- [x] #3 Agent roster section lists all specialized agents with their roles, expertise areas, and which commands invoke them
- [x] #4 Workflow patterns section explains parallel vs sequential execution with rationale for each design choice
- [x] #5 Use case examples section provides 3+ real-world scenarios showing which commands to use in sequence
- [x] #6 Both Mermaid diagram (inline) and Excalidraw PNG (embedded) are included in the document
- [x] #7 Document follows project documentation style (consistent headings, formatting, tone)
- [x] #8 All technical terms are explained or linked to definitions
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created comprehensive /jpspec workflow documentation at docs/guides/jpspec-workflow-guide.md

The guide includes:
- Executive summary explaining purpose and value proposition
- Detailed documentation of all 6 /jpspec commands with purpose, when to use, agents invoked, execution patterns, inputs/outputs
- Complete agent roster (15 agents) with roles, expertise, frameworks, and responsibilities
- Workflow patterns section explaining parallel vs sequential execution with rationale
- 5 real-world use case examples (simple bug fix, API endpoint, payment integration, microservices refactoring, ML feature)
- Both Mermaid diagram (inline) and reference to Excalidraw PNG diagram
- Consistent formatting following project documentation style (matches backlog-user-guide.md, workflow-architecture.md, inner-loop.md)
- All technical terms explained with framework references (SVPG, DORA, Gregor Hohpe, NIST, SLSA)
- Integration with backlog.md task management
- Best practices, troubleshooting, and advanced topics sections

All 8 acceptance criteria met:
AC #1: Executive summary with purpose and value ✓
AC #2: Each command documented with all required details ✓
AC #3: Agent roster with 15 agents fully documented ✓
AC #4: Workflow patterns (parallel vs sequential) explained ✓
AC #5: 5+ use case examples provided ✓
AC #6: Both diagrams included (Mermaid inline, PNG referenced) ✓
AC #7: Follows project documentation style ✓
AC #8: All technical terms explained/linked ✓
<!-- SECTION:NOTES:END -->
