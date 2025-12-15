---
id: task-335
title: Add CI check for agent sync drift
status: Done
assignee:
  - '@galway'
created_date: '2025-12-08 22:28'
updated_date: '2025-12-15 13:43'
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
- [ ] #1 CI workflow runs sync-copilot-agents.sh --validate on every PR
- [ ] #2 CI fails if .claude/commands/ changed but .github/agents/ not updated
- [ ] #3 CI runs on macOS, Linux, and Windows (GitHub Actions matrix)
- [ ] #4 CI performance: validation completes in under 30 seconds
<!-- AC:END -->
