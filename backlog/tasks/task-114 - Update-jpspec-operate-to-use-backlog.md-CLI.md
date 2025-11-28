---
id: task-114
title: 'Update /jpspec:operate to use backlog.md CLI'
status: Done
assignee:
  - '@claude-opus'
created_date: '2025-11-28 16:56'
updated_date: '2025-11-28 22:02'
labels:
  - jpspec
  - backlog-integration
  - operate
  - P1
dependencies:
  - task-107
  - task-108
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Modify the operate.md command to integrate backlog.md task management. SRE agent must create and manage operational tasks for CI/CD, Kubernetes, DevSecOps, and observability work.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 SRE agent receives shared backlog instructions from _backlog-instructions.md
- [x] #2 Agent creates operational tasks in backlog (deployment, monitoring, alerts)
- [x] #3 Agent tracks infrastructure changes as tasks with clear ACs
- [x] #4 Agent updates task status as operations complete
- [x] #5 Runbook creation tasks added to backlog when alerts are defined
- [x] #6 Test: Run /jpspec:operate and verify operational tasks created
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Updated /jpspec:operate command with full backlog.md CLI integration.

Changes:
- Added Step 1: Discover Existing Operational Tasks
- SRE agent receives backlog instructions (@sre-agent)
- Agent creates operational tasks:
  - CI/CD Pipeline (infrastructure,cicd)
  - Kubernetes Configuration (infrastructure,kubernetes)
  - Observability Stack (infrastructure,observability)
  - SLOs and Alerting (infrastructure,monitoring)
- Agent tracks infrastructure changes as tasks with clear ACs
- Agent updates task status during operations
- Runbook tasks created when alerts are defined (runbook,operations)
- Added tests in tests/test_jpspec_operate_backlog.py (18 tests, all passing)
<!-- SECTION:NOTES:END -->
