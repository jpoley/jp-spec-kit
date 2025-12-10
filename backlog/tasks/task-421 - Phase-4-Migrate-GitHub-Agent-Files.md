---
id: task-421
title: 'Phase 4: Migrate GitHub Agent Files'
status: To Do
assignee: []
created_date: '2025-12-10 02:59'
labels:
  - migration
  - agents
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Rename 15 GitHub agent files from specflow-*.agent.md to specflow-*.agent.md and update all include paths and command references. DEPENDS ON: task-420 symlink recreation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All 15 agent files renamed: specflow-*.agent.md → specflow-*.agent.md
- [ ] #2 Include paths updated in all agent files
- [ ] #3 Command references updated: /specflow: → /specflow:
- [ ] #4 Agent identity references validated (if any @specflow- references exist)
- [ ] #5 Validation checkpoint passes: all includes resolve
<!-- AC:END -->
