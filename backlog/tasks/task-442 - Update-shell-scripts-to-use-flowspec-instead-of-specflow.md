---
id: task-442
title: Update shell scripts to use flowspec instead of flowspec
status: To Do
assignee: []
created_date: '2025-12-11 01:32'
labels:
  - platform
  - scripts
  - rename
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update all shell scripts with flowspec references:

Scripts to update:
- scripts/bash/sync-copilot-agents.sh
- scripts/bash/migrate-commands-to-subdirs.sh
- scripts/bash/pre-commit-dev-setup.sh
- scripts/bash/verify-backlog-integration.sh
- scripts/generate-deprecated-aliases.sh
- .github/workflows/scripts/create-release-packages.sh

Updates per script:
1. sync-copilot-agents.sh: Update directory paths, validation checks
2. migrate-commands-to-subdirs.sh: Update flowspec.*.md patterns to flowspec.*.md
3. pre-commit-dev-setup.sh: Update R7 validation for flowspec/ directory
4. verify-backlog-integration.sh: Update command path references
5. generate-deprecated-aliases.sh: Add /flow: → /flow: deprecation mappings
6. create-release-packages.sh: Update package content paths

Specific changes:
- Directory paths: commands/flowspec → commands/flowspec
- File patterns: flowspec.*.md → flowspec.*.md
- Command examples: /flow: → /flow:
- Variable names: FLOWSPEC_* → FLOWSPEC_*
- Comments and documentation
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All shell scripts updated to use flowspec paths
- [ ] #2 sync-copilot-agents.sh validates flowspec/ directory
- [ ] #3 migrate-commands script handles flowspec pattern
- [ ] #4 pre-commit hook checks flowspec structure
- [ ] #5 deprecated-aliases script includes /flow: → /flow: mappings
- [ ] #6 All scripts execute successfully after rename
- [ ] #7 Shellcheck passes on updated scripts
<!-- AC:END -->
