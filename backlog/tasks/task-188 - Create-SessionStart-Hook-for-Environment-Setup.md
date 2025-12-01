---
id: task-188
title: Create SessionStart Hook for Environment Setup
status: To Do
assignee: []
created_date: '2025-12-01 05:04'
updated_date: '2025-12-01 05:30'
labels:
  - claude-code
  - hooks
  - automation
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement SessionStart hook to automate environment verification and display active context when starting or resuming a Claude Code session.

Cross-reference: See docs/prd/claude-capabilities-review.md Section 2.1 for hooks gap analysis.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 SessionStart hook script created at .claude/hooks/session-start.sh

- [ ] #2 Hook verifies key dependencies (uv, backlog CLI)
- [ ] #3 Hook displays active In Progress backlog tasks
- [ ] #4 Hook configuration added to .claude/settings.json
- [ ] #5 Hook completes within timeout (default 60s)
<!-- AC:END -->
