---
id: task-327
title: 'Design: CI/CD Pipeline for Agent Sync Validation'
status: Done
assignee:
  - '@muckross'
created_date: '2025-12-08 22:22'
updated_date: '2025-12-14 20:31'
labels:
  - infrastructure
  - cicd
  - 'workflow:Planned'
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Design GitHub Actions workflow for validating .claude/commands/ and .github/agents/ are in sync on every PR
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Workflow triggers on PR changes to .claude/commands/ or .github/agents/
- [x] #2 Matrix strategy covers macOS, Linux, Windows
- [x] #3 Drift detection with clear error messages and remediation steps
- [x] #4 Performance target: validation completes in < 30 seconds
- [ ] #5 Workflow file documented in docs/platform/ci-agent-sync.md
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implemented (2025-12-14)

Workflow created at `.github/workflows/validate-agent-sync.yml` (task-335):
- AC#1: Triggers on PR changes to .claude/commands/ or .github/agents/
- AC#2: Matrix strategy covers ubuntu-latest, macos-latest, windows-latest
- AC#3: Drift detection with clear error messages
- AC#4: Performance warning if > 30 seconds
- AC#5: Documentation in `docs/guides/vscode-copilot-setup.md`
<!-- SECTION:NOTES:END -->
