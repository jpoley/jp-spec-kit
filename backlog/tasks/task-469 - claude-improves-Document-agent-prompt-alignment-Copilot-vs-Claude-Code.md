---
id: task-469
title: 'claude-improves: Document agent-prompt alignment (Copilot vs Claude Code)'
status: To Do
assignee:
  - '@kinsale'
created_date: '2025-12-12 01:15'
updated_date: '2026-01-06 18:52'
labels:
  - claude-improves
  - source-repo
  - agents
  - prompts
  - alignment
  - phase-2
dependencies: []
priority: high
ordinal: 28000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
17 agents in .github/agents/ have no corresponding prompts. Need to either:
1. Create corresponding prompts in .github/prompts/
2. Document that these agents are Copilot-only

Missing prompts for agents:
- arch-decide, arch-design, arch-model
- dev-build, dev-cleanup, dev-debug, dev-refactor
- flow-init, flow-reset
- ops-deploy, ops-monitor, ops-respond, ops-scale
- pm-assess, pm-define, pm-discover
- qa-review, qa-test, qa-verify
- sec-audit, sec-fix, sec-report, sec-scan, sec-triage
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Audit all agents in .github/agents/
- [ ] #2 Document which agents are Copilot-only vs Claude Code
- [ ] #3 Create missing prompts for Claude Code agents OR document exclusion
- [ ] #4 Update CLAUDE.md with agent usage guide
- [ ] #5 Add CI check for agent-prompt alignment
<!-- AC:END -->
