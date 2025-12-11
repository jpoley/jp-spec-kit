---
id: task-450
title: Rename command directories and recreate symlinks (flowspec → flow)
status: To Do
assignee: []
created_date: '2025-12-11 01:36'
labels:
  - backend
  - infrastructure
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Rename command directories from flowspec to flow and recreate all symlinks. Includes backward-compatible symlink for deprecation phase. **Depends on: task-448 (schema rename)**
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 templates/commands/flowspec → templates/commands/flow
- [ ] #2 .claude/commands/flowspec symlinks recreated pointing to flow/
- [ ] #3 Backward-compatible symlink created (.claude/commands/flowspec → flow)
- [ ] #4 All 17 command files accessible via /flow: namespace
- [ ] #5 Command discovery works correctly
- [ ] #6 Old /flow: commands show deprecation warning
<!-- AC:END -->
