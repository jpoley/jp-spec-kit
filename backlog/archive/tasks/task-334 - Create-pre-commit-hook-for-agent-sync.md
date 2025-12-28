---
id: task-334
title: Create pre-commit hook for agent sync
status: Done
assignee:
  - '@muckross'
created_date: '2025-12-08 22:28'
updated_date: '2025-12-14 18:12'
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
- [x] #1 Hook configuration added to .specify/hooks/hooks.yaml
- [x] #2 Hook triggers only when .claude/commands/ files are staged
- [x] #3 Hook auto-stages generated .github/agents/ files
- [x] #4 Hook can be bypassed with git commit --no-verify
- [x] #5 Hook shows clear output indicating which files were synced
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementation complete per design from task-328:

1. Created scripts/bash/pre-commit-agent-sync.sh:
   - Detects staged .claude/commands/**/*.md files
   - Runs sync-copilot-agents.sh --force
   - Auto-stages generated .github/agents/ files
   - Shows clear [agent-sync] prefixed output

2. Added hook to .pre-commit-config.yaml:
   - id: sync-copilot-agents
   - triggers on ^\\.claude/commands/.*\\.md$|^templates/commands/.*\\.md$
   - language: script

3. Updated scripts/CLAUDE.md with documentation

Tested manually: hook correctly detects staged command files, runs sync,
and auto-stages generated agent files.

Commit: dcd3fab
<!-- SECTION:NOTES:END -->
