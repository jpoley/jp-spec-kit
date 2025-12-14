---
id: task-204.03
title: Contribute hooks/events feature to upstream backlog.md
status: In Progress
assignee:
  - '@muckross'
created_date: '2025-12-03 02:19'
updated_date: '2025-12-14 19:20'
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
- [x] #1 Review backlog.md codebase for hook extension points
- [x] #2 Draft feature proposal document
- [ ] #3 Open GitHub issue on MrLesk/Backlog.md repo
- [ ] #4 Engage with maintainer on design
- [ ] #5 If accepted: implement hooks feature in backlog.md
- [ ] #6 If accepted: submit PR to upstream
- [ ] #7 Document outcome (accepted/rejected/forked)
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Proposal Complete (2025-12-14)

### Codebase Review Summary:
- Backlog.md is written in TypeScript
- Already has `onStatusChange` hook in config.yml
- Uses Husky for git hooks
- MIT licensed, open to contributions
- Has MCP server integration for AI tools

### Proposal Document:
Created: `docs/proposals/backlog-md-hooks-proposal.md`

**Proposed Approach**: Hybrid shell + TypeScript hook system

**Key Features**:
- Extended lifecycle hooks (create, edit, delete, archive)
- Acceptance criteria hooks (check/uncheck)
- JSON event payload on stdin
- Backwards compatible with existing onStatusChange

### Next Steps:
1. Open GitHub issue on MrLesk/Backlog.md
2. Link to proposal document
3. Engage with maintainer on design decisions

### Remaining ACs:
- AC3: Open GitHub issue (requires manual action)
- AC4-7: Depend on maintainer response
<!-- SECTION:NOTES:END -->
