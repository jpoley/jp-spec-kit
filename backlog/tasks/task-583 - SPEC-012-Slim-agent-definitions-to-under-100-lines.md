---
id: task-583
title: 'SPEC-012: Slim agent definitions to under 100 lines'
status: To Do
assignee: []
created_date: '2026-01-24 15:35'
labels:
  - architecture
  - agents
  - phase-1
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Reduce agent definitions from ~400 lines to under 100 lines by referencing skills instead of embedding instructions.

**Current State**: ~400-line agents with embedded instructions
**Target State**: ~50-100 line agents referencing skills

**Example Target Structure**:
```markdown
---
name: backend-engineer
description: Backend implementation - APIs, databases, Python
tools: Read, Write, Edit, Glob, Grep, Bash
model: sonnet
skills:
  - coding-standards
  - backend-patterns
  - tdd-workflow
---

# Backend Engineer
You are a Senior Backend Engineer. Follow the skills listed above.
```

**Source**: docs/specs/flowspec-improvement-specs-v1.md
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Agent files under 100 lines
- [ ] #2 Skills referenced not duplicated
- [ ] #3 Consistent structure across all agents
- [ ] #4 Model specified per agent
<!-- AC:END -->
