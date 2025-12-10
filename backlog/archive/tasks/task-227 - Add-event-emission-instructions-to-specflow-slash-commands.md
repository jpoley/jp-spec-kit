---
id: task-227
title: Add event emission instructions to /specflow slash commands
status: Done
assignee: []
created_date: '2025-12-03 02:10'
updated_date: '2025-12-03 22:27'
labels:
  - hooks
  - integration
  - slash-commands
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update all /specflow slash command markdown files to include event emission at command completion. This enables automatic hook triggering when agents complete workflow phases.

**Context**: Currently hooks can only be triggered manually via `specify hooks emit`. We need agents to emit events automatically when they complete /specflow commands.

**Approach**: Add a "Post-Completion" section to each slash command that instructs the agent to call `specify hooks emit <event-type>` after successful completion.

**Commands to Update**:
- `.claude/commands/specflow/assess.md` → emit `workflow.assessed`
- `.claude/commands/specflow/specify.md` → emit `spec.created`
- `.claude/commands/specflow/research.md` → emit `research.completed`
- `.claude/commands/specflow/plan.md` → emit `plan.created`
- `.claude/commands/specflow/implement.md` → emit `implement.completed`
- `.claude/commands/specflow/validate.md` → emit `validate.completed`
- `.claude/commands/specflow/operate.md` → emit `deploy.completed`

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
- [ ] #1 All 7 /specflow commands updated with post-completion event emission instructions
- [ ] #2 Each command emits the correct event type for its workflow phase
- [ ] #3 Instructions include --spec-id and --task-id parameters
- [ ] #4 Instructions include -f flag for created artifact files
- [ ] #5 Template added to templates/commands/specflow/ for new project scaffolding
- [ ] #6 Documentation updated in docs/guides/hooks-quickstart.md
<!-- AC:END -->
