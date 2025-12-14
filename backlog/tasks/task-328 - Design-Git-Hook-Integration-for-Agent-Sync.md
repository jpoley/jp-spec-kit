---
id: task-328
title: 'Design: Git Hook Integration for Agent Sync'
status: Done
assignee:
  - '@muckross'
created_date: '2025-12-08 22:22'
updated_date: '2025-12-14 18:07'
labels:
  - infrastructure
  - tooling
  - 'workflow:Planned'
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Design pre-commit hook configuration in .specify/hooks/hooks.yaml for automatic agent sync when command files change
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Hook triggers only when .claude/commands/**/*.md files are staged
- [x] #2 Hook runs sync-copilot-agents.sh automatically
- [x] #3 Hook auto-stages generated .github/agents/ files
- [x] #4 Hook can be bypassed with git commit --no-verify
- [x] #5 Hook shows clear output indicating files synced
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Design document created at build-docs/design/git-hook-agent-sync-design.md

Key design decisions:
1. Use pre-commit framework (preferred) with fallback to native git hook
2. File pattern: ^\\.claude/commands/.*\\.md$|^templates/commands/.*\\.md$
3. Script location: scripts/bash/pre-commit-agent-sync.sh
4. Auto-stage generated files with git add .github/agents/
5. Clear logging output with [agent-sync] prefix

Implementation task: task-334

Commit: 6b5d3d3
<!-- SECTION:NOTES:END -->
