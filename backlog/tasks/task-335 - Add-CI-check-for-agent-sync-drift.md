---
id: task-335
title: Add CI check for agent sync drift
status: Done
assignee:
  - '@muckross'
created_date: '2025-12-08 22:28'
updated_date: '2025-12-14 20:15'
labels:
  - implement
  - ci
  - 'workflow:Planned'
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create GitHub Actions workflow to validate .claude/commands/ and .github/agents/ are in sync on every PR
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 CI workflow runs sync-copilot-agents.sh --validate on every PR
- [x] #2 CI fails if .claude/commands/ changed but .github/agents/ not updated
- [x] #3 CI runs on macOS, Linux, and Windows (GitHub Actions matrix)
- [x] #4 CI performance: validation completes in under 30 seconds
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implementation Complete (2025-12-14)

Created `.github/workflows/validate-agent-sync.yml` with:

1. **Trigger**: On PRs to main when command/agent files change
2. **Matrix**: Runs on ubuntu-latest, macos-latest, windows-latest
3. **Validation**: Runs `sync-copilot-agents.sh --validate` (exit 2 if drift)
4. **Performance**: Warns if validation > 30 seconds
5. **Job summary**: Shows platform, status, and fix instructions
<!-- SECTION:NOTES:END -->
