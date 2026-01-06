---
id: task-579.05
title: 'P0.5: Fix upgrade-repo to update flowspec_workflow.yml to v2.0'
status: In Progress
assignee: []
created_date: '2026-01-06 17:20'
updated_date: '2026-01-06 18:49'
labels:
  - phase-0
  - upgrade-repo
  - workflow
  - release-blocker
dependencies: []
parent_task_id: task-579
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The upgrade_repo command does NOT update flowspec_workflow.yml in target repos. They remain stuck on v1.0 with deprecated features.

v1.0 issues:
- Still has 'operate' transition (removed in v2.0)
- Missing v2.0 features: roles, custom_workflows, agent_loops sections

Changes needed:
1. Add workflow config version detection
2. Offer migration from v1.0 to v2.0
3. Preserve custom configurations during migration
4. Remove deprecated 'operate' transition
5. Add new v2.0 sections (roles, custom_workflows, agent_loops)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 upgrade_repo detects flowspec_workflow.yml version
- [ ] #2 v1.0 configs migrated to v2.0 format
- [ ] #3 Custom configurations preserved during migration
- [ ] #4 'operate' transition removed during migration
- [ ] #5 New v2.0 sections added (roles, custom_workflows, agent_loops)
- [ ] #6 Test: running upgrade-repo updates workflow config correctly
<!-- AC:END -->
