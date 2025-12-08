---
id: task-332
title: Build sync-copilot-agents.sh automation script
status: To Do
assignee: []
created_date: '2025-12-08 22:28'
labels:
  - implement
  - tooling
  - 'workflow:Planned'
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create Bash script to automate conversion of .claude/commands/ to .github/agents/ with frontmatter transformation and include resolution
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Script located at scripts/bash/sync-copilot-agents.sh with execute permissions
- [ ] #2 Script converts all 23 commands (jpspec + speckit) without manual edits
- [ ] #3 Script supports --dry-run, --validate, and --force flags
- [ ] #4 Script resolves {{INCLUDE:...}} directives correctly (max depth 3)
- [ ] #5 Script completes in under 2 seconds for 23 commands
- [ ] #6 Script runs successfully on macOS, Linux, and Windows WSL2
<!-- AC:END -->
