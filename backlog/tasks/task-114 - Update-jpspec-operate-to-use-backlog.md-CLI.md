---
id: task-114
title: 'Update /jpspec:operate to use backlog.md CLI'
status: To Do
assignee: []
created_date: '2025-11-28 16:56'
updated_date: '2025-11-28 16:57'
labels:
  - jpspec
  - backlog-integration
  - operate
  - P1
dependencies:
  - task-107
  - task-108
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Modify the operate.md command to integrate backlog.md task management. SRE agent must create and manage operational tasks for CI/CD, Kubernetes, DevSecOps, and observability work.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 SRE agent receives shared backlog instructions from _backlog-instructions.md
- [ ] #2 Agent creates operational tasks in backlog (deployment, monitoring, alerts)
- [ ] #3 Agent tracks infrastructure changes as tasks with clear ACs
- [ ] #4 Agent updates task status as operations complete
- [ ] #5 Runbook creation tasks added to backlog when alerts are defined
- [ ] #6 Test: Run /jpspec:operate and verify operational tasks created
<!-- AC:END -->
