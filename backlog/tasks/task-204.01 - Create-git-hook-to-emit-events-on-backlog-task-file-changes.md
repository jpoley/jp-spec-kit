---
id: task-204.01
title: Create git hook to emit events on backlog task file changes
status: To Do
assignee:
  - '@muckross'
created_date: '2025-12-03 02:19'
updated_date: '2025-12-14 17:48'
labels:
  - hooks
  - git
  - backlog
  - integration
dependencies: []
parent_task_id: task-204
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a git post-commit hook that detects changes to backlog task files and emits corresponding flowspec events.

**Context**: Backlog.md stores tasks as markdown files in `backlog/tasks/`. When these files change (via `backlog task edit`, `backlog task create`, etc.), git sees the file modifications. A post-commit hook can parse these changes and emit events.

**Architecture**:
```
User: backlog task edit 123 -s Done
    ↓
Backlog CLI modifies: backlog/tasks/task-123.md
    ↓
User: git add . && git commit
    ↓
Git post-commit hook fires
    ↓
Hook parses: git diff --name-only HEAD~1
    ↓
Hook detects: task-123.md changed, status now "Done"
    ↓
Hook emits: specify hooks emit task.completed --task-id task-123
```

**Implementation**:
1. Create `scripts/hooks/post-commit-backlog-events.sh`
2. Parse `git diff` to find changed task files
3. For each changed task:
   - Detect if new file → `task.created`
   - Detect status change → `task.status_changed` or `task.completed`
   - Detect AC changes → `task.ac_checked`
4. Call `specify hooks emit` with appropriate event
5. Install script via `specify init` or manual setup

**Limitations**:
- Only fires on commit (not real-time)
- Requires git workflow (commit after each change)
- May batch multiple changes into one commit

**Files to create**:
- `scripts/hooks/post-commit-backlog-events.sh`
- `docs/guides/backlog-git-hooks.md`
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Git hook script created at scripts/hooks/post-commit-backlog-events.sh
- [ ] #2 Hook detects new task files and emits task.created
- [ ] #3 Hook detects status changes and emits task.status_changed
- [ ] #4 Hook detects Done status and emits task.completed
- [ ] #5 Hook detects AC checkbox changes and emits task.ac_checked
- [ ] #6 Hook is idempotent (safe to run multiple times)
- [ ] #7 Documentation explains setup and limitations
- [ ] #8 Integration test with mock git repo
<!-- AC:END -->
