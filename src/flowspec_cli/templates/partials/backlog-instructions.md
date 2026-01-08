# Backlog.md CLI Integration Instructions

**IMPORTANT**: You have access to the backlog.md CLI tool for task lifecycle management. Use these commands to track your progress and maintain project visibility.

---

## Task Lifecycle Overview

All tasks follow this lifecycle:

```
To Do → In Progress → Done
         ↕ (optional)
       Blocked
```

**Your Responsibilities**:
1. **Entry**: Task should already be "In Progress" and assigned to you (done by command)
2. **During**: Check acceptance criteria as you complete them
3. **During**: Add progress notes for significant milestones
4. **Exit**: Ensure all ACs are checked and add final implementation notes before marking Done

---

## Common CLI Commands

### Viewing Task Details

```bash
# View your current task (AI-friendly plain text output)
backlog task <task-id> --plain

# List all tasks by status
backlog task list -s "In Progress" --plain

# Search for related tasks
backlog search "feature-name" --plain
```

**When to use**: Before starting work, review task details to understand acceptance criteria and context.

---

### Checking Acceptance Criteria

```bash
# Mark AC #1 as complete
backlog task edit <task-id> --check-ac 1

# Mark multiple ACs as complete (supports multiple --check-ac flags)
backlog task edit <task-id> --check-ac 1 --check-ac 2 --check-ac 3

# Uncheck AC #2 if you need to revisit it
backlog task edit <task-id> --uncheck-ac 2
```

**When to use**:
- Check ACs as soon as you complete them (don't wait until the end)
- For multi-phase work, check ACs at phase boundaries
- Uncheck if you discover an AC wasn't fully satisfied

**Best Practice**: Check ACs incrementally during work, not all at once at the end.

---

### Adding Progress Notes

```bash
# Replace all implementation notes (use for final summary)
backlog task edit <task-id> --notes "Summary of work completed. Key changes: ..."

# Append to existing notes (use for progress updates)
backlog task edit <task-id> --append-notes "Completed phase 1: X, Y, Z"

# Multi-line notes (use shell-appropriate syntax)
# Bash/Zsh (ANSI-C quoting):
backlog task edit <task-id> --append-notes $'Progress update:\n- Completed X\n- Started Y'

# PowerShell (backtick-n):
backlog task edit <task-id> --append-notes "Progress:`n- Item 1`n- Item 2"
```

**When to use**:
- **During work**: Use `--append-notes` for progress updates
- **At completion**: Use `--notes` for final PR description-ready summary

**Note Format Guidelines**:
- Keep notes human-friendly and PR-ready
- Use short paragraphs or bullet lists
- Lead with outcome, then add supporting details
- Prefer Markdown bullets (`-` or `1.`) for easy copy-paste to GitHub

---

### Creating Subtasks (Optional - Task-Creating Agents Only)

```bash
# Create subtask linked to parent
backlog task create "Subtask title" -p <parent-task-id> --ac "Acceptance criterion"

# Create with full metadata
backlog task create "Epic: User Signup" \
  -p <parent-id> \
  -d "Description" \
  --ac "Users can register with email" \
  --ac "Email verification required" \
  --priority high \
  -l epic,auth
```

**When to use**:
- PM Planner: Create epics/user stories from PRD task breakdown (section 6)
- SRE Agent: Create subtasks for each operational area if beneficial
- Other agents: Optional, only if breaking down complex work provides value

**Naming Convention**: `flowspec-{command}-{feature-slug}-{yyyymmdd}-{descriptor}`

Example: `flowspec-specify-auth-20251128-epic-signup`

---

### Handling Blocked State

```bash
# Mark task as blocked
backlog task edit <task-id> -s Blocked --append-notes "Blocker: Waiting for API spec approval"

# Unblock and resume work
backlog task edit <task-id> -s "In Progress" --append-notes "Resolved: API spec approved"
```

**When to use**:
- Dependency on another task or person
- Waiting for external input (approval, credentials, etc.)
- Technical blocker preventing progress

**Best Practice**: Always document the blocker reason in notes.

---

## Task Completion Checklist

Before marking a task as Done, verify:

- [ ] **All acceptance criteria checked**: `backlog task <id> --plain` shows all ACs with `[x]`
- [ ] **Implementation notes added**: Final summary suitable for PR description
- [ ] **No blockers remain**: All dependencies resolved
- [ ] **Code/deliverables complete**: Work is production-ready
- [ ] **Tests passing**: All validations successful

**DO NOT mark a task Done until ALL items above are satisfied.**

---

## Definition of Done

A task is considered **Done** when:

### Via CLI:
1. ✅ All acceptance criteria checked (`--check-ac` for each)
2. ✅ Implementation notes added (`--notes` with PR-ready summary)
3. ✅ Status set to Done (`-s Done`)

### Via Work Quality:
4. ✅ Tests pass (unit, integration, etc.)
5. ✅ Documentation updated (if applicable)
6. ✅ Code reviewed (if applicable)
7. ✅ No regressions (performance, security)

**Command-level exit hooks typically handle final task completion, but you should prepare tasks by checking ACs and adding notes during your work.**

---

## Design Tasks vs Implementation Tasks (Design→Implement Workflow)

### What is a Design Task?

A **design task** produces artifacts (documents, diagrams, architecture decisions, research findings) that require follow-up implementation. Design tasks are identified by:

**Labels** (any of these indicate a design task):
- `design` - Architecture, system design, UI/UX design
- `audit` - Analysis that produces recommendations
- `architecture` - System architecture decisions
- `research` - Research that produces actionable findings
- `spike` - Technical exploration/proof of concept
- `planning` - Planning that produces actionable plans

**Title patterns** (any of these indicate a design task):
- "Design ..." - e.g., "Design authentication flow"
- "... Architecture" - e.g., "Plugin Architecture"
- "Audit ..." - e.g., "Audit API endpoints"
- "Research ..." - e.g., "Research caching strategies"
- "Spike: ..." - e.g., "Spike: GraphQL performance"

### ⚠️ CRITICAL: Design Tasks MUST Create Implementation Tasks

**Design tasks CANNOT be marked Done without corresponding implementation task(s).**

When completing a design task:

1. **Before marking Done**, create implementation tasks that:
   - Reference the design task as a dependency
   - Have specific, actionable acceptance criteria
   - Cover all actionable items from the design deliverables

2. **Implementation Notes MUST include**:
   - "Follow-up Implementation Tasks:" section listing created task IDs
   - Summary of key design decisions
   - Files/artifacts created

### Design Task Completion Workflow

```bash
# 1. Complete design work (produce artifacts, documents, etc.)

# 2. Create implementation tasks BEFORE marking design task Done
backlog task create "Implement [specific feature from design]" \
  -d "Implementation based on task-106 design" \
  --ac "Implement X per ADR-001" \
  --ac "Add tests for X" \
  --dep task-106 \
  -l implement,backend

# 3. Add implementation notes with follow-up task references
backlog task edit 106 --notes $'Designed comprehensive architecture.\n\nDeliverables:\n- ADR-001: Architecture decision record\n- templates/auth-flow.md: Flow diagram\n\nFollow-up Implementation Tasks:\n- task-107: Implement auth service\n- task-108: Implement auth middleware\n- task-109: Add auth tests'

# 4. Only NOW mark design task as Done
backlog task edit 106 -s Done
```

### Design Task Definition of Done

A design task is **Done** only when **ALL** of the following are complete:

1. ✅ All acceptance criteria checked
2. ✅ Design artifacts created (ADRs, diagrams, specs)
3. ✅ **Implementation tasks created** (MANDATORY for design tasks)
4. ✅ Implementation notes include "Follow-up Implementation Tasks:" section
5. ✅ Status set to Done

### Naming Convention for Follow-up Tasks

Implementation tasks should clearly reference their design origin:

| Design Task | Implementation Task(s) |
|------------|------------------------|
| Design authentication flow | Implement auth service, Implement auth middleware |
| Audit API endpoints | Update deprecated endpoints, Add missing validation |
| Research caching strategy | Implement Redis caching layer, Add cache invalidation |
| Spike: GraphQL performance | Implement DataLoader pattern, Add query complexity limits |

### Why This Matters

- **Traceability**: Every design decision has corresponding implementation
- **No orphaned designs**: Prevents valuable design work from being forgotten
- **Clear dependencies**: Implementation tasks can reference design artifacts
- **Audit trail**: Easy to trace from requirement → design → implementation

---

## Multi-line Input Best Practices

The CLI preserves input literally. Use shell-appropriate syntax for newlines:

**Bash/Zsh** (ANSI-C quoting with `$'...'`):
```bash
backlog task edit 42 --notes $'Summary line 1\nLine 2\n\nFinal section'
backlog task edit 42 --plan $'1. First step\n2. Second step\n3. Third step'
```

**PowerShell** (backtick-n):
```powershell
backlog task edit 42 --notes "Line 1`nLine 2`n`nFinal"
```

**POSIX Portable** (printf):
```bash
backlog task edit 42 --notes "$(printf 'Line 1\nLine 2')"
```

**DO NOT** use plain `"...\n..."` - that passes literal backslash + n, not a newline.

---

## Error Handling

If backlog CLI commands fail:

1. **Check CLI installation**: `which backlog` (should return path)
2. **Verify task exists**: `backlog task <id> --plain`
3. **Check command syntax**: Review examples above
4. **Report to user**: If CLI errors persist, inform the user and continue without backlog integration

**Graceful Degradation**: If backlog CLI is unavailable, continue with your work and report completion to the user manually. Task tracking is beneficial but not blocking.

---

## Command Reference Quick Lookup

| Action | Command |
|--------|---------|
| View task | `backlog task <id> --plain` |
| List tasks | `backlog task list -s "In Progress" --plain` |
| Check AC #1 | `backlog task edit <id> --check-ac 1` |
| Check multiple ACs | `backlog task edit <id> --check-ac 1 --check-ac 2` |
| Uncheck AC #2 | `backlog task edit <id> --uncheck-ac 2` |
| Append notes | `backlog task edit <id> --append-notes "Update"` |
| Replace notes | `backlog task edit <id> --notes "Final summary"` |
| Create subtask | `backlog task create "Title" -p <parent-id> --ac "Criterion"` |
| Mark blocked | `backlog task edit <id> -s Blocked --append-notes "Blocker: ..."` |
| Resume from blocked | `backlog task edit <id> -s "In Progress" --append-notes "Resolved: ..."` |
| Search tasks | `backlog search "keyword" --plain` |

---

## Agent-Specific Guidelines

### Product Requirements Manager (PM Planner)
- **Create subtasks** from PRD task breakdown (section 6)
- Use naming: `flowspec-specify-{feature}-{date}-epic-{name}`
- Set priorities and dependencies for subtasks
- Check ACs as PRD sections complete

### SRE Agent
- **Track 9 operational areas** via acceptance criteria
- Check ACs as each area completes (SLOs, CI/CD, K8s, etc.)
- Append notes for each deliverable with key details
- Optional: Create subtasks for complex operational work

### Quality Guardian
- **Check test-related ACs** as test suites complete
- Append notes with test results (passed/failed counts)
- Document risks and issues discovered
- Final notes should include quality metrics

### Release Manager
- **Document human approval** in task notes
- Use format: `APPROVED by [name] on [date]. Reason: [rationale]`
- **DO NOT mark task Done** until approval received
- Append approval details before completion

### All Other Agents
- Check ACs incrementally during work
- Append notes at significant milestones
- Prepare final notes as PR description
- Trust command-level hooks for task activation/completion

---

## Best Practices Summary

1. **Review task first**: Use `backlog task <id> --plain` before starting work
2. **Check ACs incrementally**: Don't wait until the end
3. **Use `--append-notes` during work**: Track progress as you go
4. **Use `--notes` at completion**: Final PR-ready summary
5. **Create subtasks sparingly**: Only when it provides clear value
6. **Document blockers**: Use Blocked status with clear reasons
7. **Verify completion**: Check all ACs before calling task Done
8. **Handle CLI errors gracefully**: Continue work if CLI unavailable

---

**Remember**: Backlog.md integration is designed to enhance visibility and reduce manual work. Use it to track your progress and communicate status, but focus primarily on delivering high-quality work that satisfies acceptance criteria.
