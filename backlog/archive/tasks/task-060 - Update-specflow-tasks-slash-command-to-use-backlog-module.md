---
id: task-060
title: 'Update /specflow:tasks slash command to use backlog module'
status: Done
assignee:
  - backend-engineer
created_date: '2025-11-25 00:24'
completed_date: '2025-11-24 20:45'
labels:
  - US1
  - CLI
  - P0
  - migrated
dependencies: []
---

## Implementation Complete

Updated `/specflow:tasks` slash command to integrate with the backlog module.

### Changes Made

1. **Updated Command Template**: `templates/commands/tasks.md`
   - Modified description to reflect dual-output behavior
   - Added Step 5: Convert to Backlog.md format
   - Enhanced reporting with both output paths

2. **Integration with Backlog Module**:
   - Uses `specify tasks generate --source {FEATURE_DIR}`
   - Converts intermediate tasks.md to Backlog.md format
   - Creates individual task files in `backlog/tasks/`

3. **Documentation Created**:
   - Implementation guide: `docs/specflow-tasks-command-update.md`
   - Testing guide: `docs/task-6-testing-guide.md`
   - Summary document: `docs/task-6-implementation-summary.md`

### Workflow

```
/specflow:tasks
  → AI generates intermediate tasks.md
  → specify tasks generate converts to Backlog.md format
  → Output: tasks.md + backlog/tasks/*.md
```

### Key Features

- All existing functionality preserved
- Backward compatible (tasks.md still generated)
- Enhanced task tracking with individual task files
- YAML frontmatter with structured metadata
- Dependency graph validation
- Execution order and critical path analysis

### Testing Status

- Template changes validated
- Git diff reviewed
- Documentation complete
- Ready for end-to-end testing

### Next Steps

1. Run end-to-end testing (see `docs/task-6-testing-guide.md`)
2. Gather user feedback
3. Create automated tests (task-7)

See `docs/task-6-implementation-summary.md` for complete details.


