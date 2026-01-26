---
id: task-582
title: 'SPEC-006: Extract rules to modular .claude/rules/ architecture'
status: Done
assignee:
  - '@backend-engineer'
created_date: '2026-01-24 15:35'
updated_date: '2026-01-24 17:09'
labels:
  - architecture
  - refactoring
  - phase-1
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Extract rules embedded in CLAUDE.md and commands into modular, standalone files.

**Current State**: Rules embedded in commands and CLAUDE.md imports
**Target State**: Standalone rule files in .claude/rules/

**New Structure**:
```
.claude/rules/
├── security.md          # No hardcoded secrets, injection prevention
├── coding-style.md      # Immutability, file limits, naming
├── testing.md           # TDD, coverage requirements
├── git-workflow.md      # Commit format, PR process
├── agents.md            # When to delegate to subagents
├── performance.md       # Model selection, context management
└── rigor.md             # Workflow quality gates
```

**Source**: docs/specs/flowspec-improvement-specs-v1.md
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Each rule file < 100 lines
- [x] #2 Rules independently loadable
- [x] #3 Override mechanism per-project works
- [x] #4 CLAUDE.md becomes leaner after extraction
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Completed via PR #1157

New files created:
- .claude/rules/security.md (87 lines)
- .claude/rules/coding-style.md (87 lines)
- .claude/rules/testing.md (89 lines)
- .claude/rules/git-workflow.md (100 lines)
- .claude/rules/agents.md (74 lines)
- .claude/rules/performance.md (77 lines)
- .claude/rules/rigor.md (86 lines)

All files under 100 lines. Rules extracted from:
- memory/critical-rules.md
- memory/code-standards.md
- memory/test-quality-standards.md
- .claude/partials/flow/_rigor-rules.md
<!-- SECTION:NOTES:END -->
