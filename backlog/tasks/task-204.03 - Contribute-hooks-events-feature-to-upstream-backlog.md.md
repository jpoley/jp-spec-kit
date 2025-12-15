---
id: task-204.03
title: Contribute hooks/events feature to upstream backlog.md
status: To Do
assignee:
  - '@chamonix'
created_date: '2025-12-03 02:19'
updated_date: '2025-12-15 02:17'
labels:
  - hooks
  - backlog
  - upstream
  - open-source
dependencies: []
parent_task_id: task-204
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Open a feature request or PR to the upstream backlog.md project (MrLesk/Backlog.md) to add native hook/event support.

**Context**: The cleanest integration would be for backlog.md itself to emit events. This is a long-term task to contribute back to the open source project.

**Proposal for upstream**:

```typescript
// backlog.config.js or hooks in CLI
module.exports = {
  hooks: {
    'task.created': async (task) => {
      // Custom hook logic
    },
    'task.completed': async (task) => {
      // Or shell command
      await exec('specify hooks emit task.completed --task-id ' + task.id);
    }
  }
}
```

**Or simpler - just shell hook support**:
```yaml
# .backlog/config.yaml
hooks:
  post_task_edit: "./hooks/on-task-edit.sh"
  post_task_create: "./hooks/on-task-create.sh"
```

**Steps**:
1. Review backlog.md codebase for extension points
2. Draft feature proposal / RFC
3. Open GitHub issue to discuss with maintainer
4. If accepted, implement and submit PR
5. Document integration once released

**Alternative**: Fork backlog.md and maintain flowspec specific version with hooks built-in.

**Repository**: https://github.com/MrLesk/Backlog.md
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Review backlog.md codebase for hook extension points
- [ ] #2 Draft feature proposal document
- [ ] #3 Open GitHub issue on MrLesk/Backlog.md repo
- [ ] #4 Engage with maintainer on design
- [ ] #5 If accepted: implement hooks feature in backlog.md
- [ ] #6 If accepted: submit PR to upstream
- [ ] #7 Document outcome (accepted/rejected/forked)
<!-- AC:END -->
