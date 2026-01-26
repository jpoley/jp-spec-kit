---
id: task-589
title: 'SPEC-007: Add model selection guidance rules'
status: To Do
assignee: []
created_date: '2026-01-24 15:36'
labels:
  - rules
  - performance
  - phase-3
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add explicit model selection rules to guide when to use Haiku/Sonnet/Opus.

**Problem**: No clear guidance on model selection for different tasks.

**Solution**: New .claude/rules/performance.md with model selection strategy.

**Model Selection Strategy**:
- Haiku: Worker agents, quick tasks, pair programming (3x cost savings)
- Sonnet: Main dev work, orchestrating workflows, default
- Opus: Architecture, deep reasoning, research, multi-step planning

**Also Include**:
- Context window management (20-30 MCPs configured, <10 enabled)
- Agent tool specification guidance
- disabledMcpServers configuration

**Source**: docs/specs/flowspec-improvement-specs-v1.md
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Clear decision tree for model selection
- [ ] #2 Agent definitions include model field
- [ ] #3 MCP management guidance documented
- [ ] #4 Cost optimization patterns explicit
<!-- AC:END -->
