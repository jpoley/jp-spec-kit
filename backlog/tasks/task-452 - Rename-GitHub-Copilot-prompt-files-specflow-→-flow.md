---
id: task-452
title: Rename GitHub Copilot prompt files (flowspec → flow)
status: To Do
assignee: []
created_date: '2025-12-11 01:36'
labels:
  - infrastructure
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Rename all 31 GitHub Copilot prompt files from flowspec.*.prompt.md to flow.*.prompt.md and update prompt content. **Depends on: task-450 (command directories)**
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All 31 prompt files renamed (flowspec.* → flow.*)
- [ ] #2 Prompt content updated to reference /flow: commands
- [ ] #3 Command examples in prompts updated
- [ ] #4 No broken references to old command names
- [ ] #5 Prompts still load correctly in GitHub Copilot
<!-- AC:END -->
