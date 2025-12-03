---
id: task-227
title: Add event emission instructions to /jpspec slash commands
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-12-03 02:10'
updated_date: '2025-12-03 02:26'
labels:
  - hooks
  - integration
  - slash-commands
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update all /jpspec slash command markdown files to include event emission at command completion. This enables automatic hook triggering when agents complete workflow phases.

**Context**: Currently hooks can only be triggered manually via `specify hooks emit`. We need agents to emit events automatically when they complete /jpspec commands.

**Approach**: Add a "Post-Completion" section to each slash command that instructs the agent to call `specify hooks emit <event-type>` after successful completion.

**Commands to Update**:
- `.claude/commands/jpspec/assess.md` → emit `workflow.assessed`
- `.claude/commands/jpspec/specify.md` → emit `spec.created`
- `.claude/commands/jpspec/research.md` → emit `research.completed`
- `.claude/commands/jpspec/plan.md` → emit `plan.created`
- `.claude/commands/jpspec/implement.md` → emit `implement.completed`
- `.claude/commands/jpspec/validate.md` → emit `validate.completed`
- `.claude/commands/jpspec/operate.md` → emit `deploy.completed`

**Template to add to each command**:
```markdown
## Post-Completion: Emit Workflow Event

After successfully completing this command, emit the workflow event:

\`\`\`bash
specify hooks emit <event-type> \
  --spec-id "$FEATURE_ID" \
  --task-id "$TASK_ID" \
  -f <artifact-files>
\`\`\`

This triggers any configured hooks in `.specify/hooks/hooks.yaml`.
```
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 All 7 /jpspec commands updated with post-completion event emission instructions
- [x] #2 Each command emits the correct event type for its workflow phase
- [x] #3 Instructions include --spec-id and --task-id parameters
- [x] #4 Instructions include -f flag for created artifact files
- [x] #5 Template added to templates/commands/jpspec/ for new project scaffolding
- [x] #6 Documentation updated in docs/guides/hooks-quickstart.md
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add "Post-Completion: Emit Workflow Event" section to each /jpspec command
2. Update .claude/commands/jpspec/*.md files (7 files)
3. Update templates/commands/jpspec/*.md files (7 files)
4. Update docs/guides/hooks-quickstart.md with /jpspec integration section
5. Commit and create PR
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implementation Summary (2025-12-03)

### What Was Implemented

Added "Post-Completion: Emit Workflow Event" section to all /jpspec slash commands to enable automatic hook triggering when workflow phases complete.

### Files Updated

**Command Files** (7 files):
- `.claude/commands/jpspec/assess.md` → emits `workflow.assessed`
- `.claude/commands/jpspec/specify.md` → emits `spec.created`
- `.claude/commands/jpspec/research.md` → emits `research.completed`
- `.claude/commands/jpspec/plan.md` → emits `plan.created`
- `.claude/commands/jpspec/implement.md` → emits `implement.completed`
- `.claude/commands/jpspec/validate.md` → emits `validate.completed`
- `.claude/commands/jpspec/operate.md` → emits `deploy.completed`

**Template Files** (7 files):
- `templates/commands/jpspec/*.md` - Same changes for new project scaffolding

**Documentation** (1 file):
- `docs/guides/hooks-quickstart.md` - Added "/jpspec Command Integration" section

### Standard Template Added

Each command now includes:
```markdown
## Post-Completion: Emit Workflow Event

After successfully completing this command, emit the workflow event:

specify hooks emit <event-type> \
  --spec-id "$FEATURE_NAME" \
  --task-id "$TASK_ID" \
  -f <artifact-files>

This triggers any configured hooks in `.specify/hooks/hooks.yaml`.
```

### Event Type Mapping

| Command | Event Type |
|---------|------------|
| assess | workflow.assessed |
| specify | spec.created |
| research | research.completed |
| plan | plan.created |
| implement | implement.completed |
| validate | validate.completed |
| operate | deploy.completed |
<!-- SECTION:NOTES:END -->
