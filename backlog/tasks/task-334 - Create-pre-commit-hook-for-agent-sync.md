---
id: task-334
title: Create pre-commit hook for agent sync
status: To Do
assignee: []
created_date: '2025-12-08 22:28'
labels:
  - implement
  - tooling
  - 'workflow:Planned'
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add pre-commit hook to automatically sync .claude/commands/ changes to .github/agents/ when commands are modified
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Hook configuration added to .specify/hooks/hooks.yaml
- [ ] #2 Hook triggers only when .claude/commands/ files are staged
- [ ] #3 Hook auto-stages generated .github/agents/ files
- [ ] #4 Hook can be bypassed with git commit --no-verify
- [ ] #5 Hook shows clear output indicating which files were synced
<!-- AC:END -->
