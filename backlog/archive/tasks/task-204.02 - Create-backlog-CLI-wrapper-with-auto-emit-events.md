---
id: task-204.02
title: Create backlog CLI wrapper with auto-emit events
status: Done
assignee:
  - '@chamonix'
created_date: '2025-12-03 02:19'
updated_date: '2025-12-15 02:17'
labels:
  - hooks
  - cli
  - backlog
  - wrapper
dependencies: []
parent_task_id: task-204
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a wrapper script/function around the `backlog` CLI that automatically emits flowspec events after each command.

**Context**: Since we can't modify backlog.md directly, we can wrap its CLI to add event emission. Users would use `bk` (or similar alias) instead of `backlog` directly.

**Architecture**:
```
User: bk task edit 123 -s Done
    ↓
Wrapper: backlog task edit 123 -s Done
    ↓
Backlog CLI executes normally
    ↓
Wrapper detects: status changed to Done
    ↓
Wrapper emits: specify hooks emit task.completed --task-id task-123
```

**Implementation Options**:

**Option A: Shell wrapper script**
```bash
#!/bin/bash
# bk - backlog wrapper with event emission
backlog "$@"
exit_code=$?

# Parse command and emit events
if [[ "$1" == "task" && "$2" == "edit" ]]; then
  task_id="$3"
  if [[ "$*" == *"-s Done"* || "$*" == *"-s \"Done\""* ]]; then
    specify hooks emit task.completed --task-id "$task_id"
  elif [[ "$*" == *"-s"* ]]; then
    specify hooks emit task.status_changed --task-id "$task_id"
  fi
fi

exit $exit_code
```

**Option B: Shell function (in .zshrc/.bashrc)**
```bash
bk() {
  backlog "$@"
  # ... emit logic
}
```

**Option C: Python wrapper CLI**
- More robust parsing
- Can read task file to get full context
- Installable via pip

**Recommended**: Option A (shell script) for simplicity, with Option C as enhancement.

**Files to create**:
- `scripts/bin/bk` (shell wrapper)
- `src/specify_cli/backlog_wrapper.py` (optional Python wrapper)
- `docs/guides/backlog-wrapper.md`
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Shell wrapper script created at scripts/bin/bk
- [x] #2 Wrapper passes all arguments to backlog CLI transparently
- [x] #3 Wrapper detects task create and emits task.created
- [x] #4 Wrapper detects status changes and emits appropriate events
- [x] #5 Wrapper detects AC check/uncheck and emits task.ac_checked
- [x] #6 Wrapper preserves original exit code from backlog CLI
- [x] #7 Installation instructions documented (PATH, alias)
- [x] #8 Works with both bash and zsh
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Examine existing backlog CLI and hooks system
2. Create bk wrapper script at scripts/bin/bk
3. Implement command detection and argument parsing
4. Add event emission for each command type
5. Create shell tests for bash and zsh
6. Create documentation
7. Test and validate all ACs
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented backlog CLI wrapper with automatic event emission.

Implementation:
- Created scripts/bin/bk wrapper script (78 lines, bash)
- Wrapper transparently proxies all backlog commands
- Auto-emits events: task.created, task.completed, task.status_changed, task.ac_checked
- Preserves exit codes and output from backlog CLI
- Works with both bash and zsh
- Silent event emission (errors suppressed)

Testing:
- Manual testing confirmed all event types working correctly
- Verified exit code preservation (success and failure)
- Verified zsh compatibility
- Created comprehensive test suite (tests/test_backlog_wrapper.sh)
- Created simple smoke test (tests/test_backlog_wrapper_simple.sh)

Documentation:
- Created docs/guides/backlog-wrapper.md
- Includes installation instructions (3 options)
- Usage examples and troubleshooting
- Event emission reference table
- Integration examples with hooks

Technical Details:
- Regex parsing for task ID extraction: "Created task task-(d+)"
- Argument parsing for status changes and AC operations
- Event emission via specify hooks CLI
- Exit code preserved with exit $exit_code at end
- 2>/dev/null for silent event emission failures

All 8 acceptance criteria met and verified.
<!-- SECTION:NOTES:END -->
