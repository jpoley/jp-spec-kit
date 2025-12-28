# Backlog Task Management

## CRITICAL: Never Edit Task Files Directly

**ALL task operations MUST use the backlog CLI.**

- ✅ `backlog task edit 42 --check-ac 1` - Mark AC complete
- ✅ `backlog task edit 42 --notes "..."` - Add notes
- ❌ Editing `backlog/tasks/task-42.md` directly
- ❌ Manually changing `- [ ]` to `- [x]`

Direct file editing breaks metadata sync, Git tracking, and relationships.

## Task Workflow

```bash
# 1. Find work
backlog task list -s "To Do" --plain

# 2. Start task (assign + status)
backlog task edit 42 -s "In Progress" -a @myself

# 3. Add implementation plan
backlog task edit 42 --plan $'1. Research\n2. Implement\n3. Test'

# 4. Mark ACs complete as you finish each one
backlog task edit 42 --check-ac 1
backlog task edit 42 --check-ac 2

# 5. Add implementation notes (like PR description)
backlog task edit 42 --notes $'Implemented X using Y pattern.\n\nChanges:\n- Modified A\n- Added B'

# 6. Complete task
backlog task edit 42 -s Done
```

## Command Reference

| Action | Command |
|--------|---------|
| View task | `backlog task 42 --plain` |
| List tasks | `backlog task list --plain` |
| Search | `backlog search "keyword" --plain` |
| Create task | `backlog task create "Title" --ac "Criterion" --ac "Another"` |
| Change status | `backlog task edit 42 -s "In Progress"` |
| Assign | `backlog task edit 42 -a @engineer` |
| Check AC | `backlog task edit 42 --check-ac 1` |
| Check multiple ACs | `backlog task edit 42 --check-ac 1 --check-ac 2` |
| Uncheck AC | `backlog task edit 42 --uncheck-ac 1` |
| Add AC | `backlog task edit 42 --ac "New criterion"` |
| Remove AC | `backlog task edit 42 --remove-ac 3` |
| Set plan | `backlog task edit 42 --plan "..."` |
| Set notes | `backlog task edit 42 --notes "..."` |
| Append notes | `backlog task edit 42 --append-notes "..."` |
| Archive | `backlog task archive 42` |

## Multi-line Input

Use ANSI-C quoting for newlines:
```bash
# Correct - creates actual newlines
backlog task edit 42 --notes $'Line 1\nLine 2\n\nParagraph 2'

# Wrong - produces literal \n characters
backlog task edit 42 --notes "Line 1\nLine 2"
```

## Task Creation Requirements

**Every task MUST have at least one acceptance criterion:**
```bash
backlog task create "Feature title" \
  -d "Description of what and why" \
  --ac "First testable criterion" \
  --ac "Second testable criterion" \
  -l backend,feature \
  --priority high
```

## Definition of Done

Before marking a task Done:
1. ✅ All acceptance criteria checked
2. ✅ Implementation notes added
3. ✅ Tests pass
4. ✅ Code self-reviewed
5. ✅ No regressions

## Design Tasks

Tasks with labels `design`, `research`, `spike`, `architecture`:
- MUST create implementation tasks before marking Done
- Include "Follow-up Tasks:" section in implementation notes

## Full Documentation

- Quick Start: `docs/guides/backlog-quickstart.md`
- User Guide: `docs/guides/backlog-user-guide.md`
- Commands: `docs/reference/backlog-commands.md`
- Flush/Archive: `docs/guides/backlog-flush.md`

## Active Task Context

@import ../memory/task-368.md
