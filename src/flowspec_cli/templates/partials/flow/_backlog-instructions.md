# Backlog.md Task Management Instructions

This document provides shared instructions for all flowspec agents to interact with the backlog.md CLI for task management.

## Critical Rules

**NEVER edit task files directly.** All task operations MUST use the backlog CLI.

- ✅ DO: `backlog task edit <id> --check-ac 1`
- ✅ DO: `backlog task list --plain`
- [X] DON'T: Edit markdown files directly
- [X] DON'T: Manually change checkboxes in files

Additional requirements:
1. **Use `--plain` flag** when viewing/listing tasks for clean AI-readable output
2. **Mark ACs complete as you finish them** - Don't batch completions
3. **Add implementation notes** before marking tasks Done

## Task Discovery

Before starting work, discover existing tasks related to your scope:

```bash
# Search for tasks by keyword
backlog search "<feature-keyword>" --plain

# List tasks by status
backlog task list -s "To Do" --plain
backlog task list -s "In Progress" --plain

# View specific task details
backlog task <id> --plain
```

## Starting Work on a Task

When you begin work on a task:

```bash
# 1. Assign yourself and set status to In Progress
backlog task edit <id> -s "In Progress" -a @<your-agent-name>

# 2. Add your implementation plan
backlog task edit <id> --plan $'1. Step one\n2. Step two\n3. Step three'
```

## Tracking Progress with Acceptance Criteria

Mark acceptance criteria complete AS you finish each one:

```bash
# Check single AC
backlog task edit <id> --check-ac 1

# Check multiple ACs in one command
backlog task edit <id> --check-ac 1 --check-ac 2 --check-ac 3

# If you need to uncheck (made a mistake)
backlog task edit <id> --uncheck-ac 2

# Add new acceptance criteria if needed
backlog task edit <id> --ac "New criterion"
```

**Important**: AC indices are 1-based (first AC is #1, not #0).

## Adding Implementation Notes

Add notes describing what was implemented (like a PR description):

```bash
# Replace existing notes
backlog task edit <id> --notes $'Implemented feature X using pattern Y.\n\nKey changes:\n- Modified file A\n- Added file B\n- Updated tests'

# Append to existing notes
backlog task edit <id> --append-notes $'Additional note about implementation'
```

## Creating New Tasks

When your work reveals additional tasks needed:

```bash
# Create a new task with acceptance criteria (MANDATORY)
backlog task create "Task title" \
  -d "Description of what needs to be done" \
  --ac "First acceptance criterion" \
  --ac "Second acceptance criterion" \
  -l label1,label2 \
  --priority high \
  -a @your-agent-identity
```

**Every task MUST have at least one acceptance criterion.**

## Pre-PR Validation (MANDATORY - NO EXCEPTIONS)

**⚠️ CRITICAL: Before creating ANY pull request, you MUST run and pass ALL validation checks.**

This is a blocking gate. Do NOT create a PR until ALL checks pass.

```bash
# 1. Format code first
uv run ruff format .

# 2. Verify format passes (CI runs this check)
uv run ruff format --check .

# 3. Run lint check - MUST pass with ZERO errors
uv run ruff check .

# 4. Run test suite - MUST pass with ZERO failures
uv run pytest tests/ -x -q

# Combined command to run all checks:
uv run ruff format . && uv run ruff format --check . && uv run ruff check . && uv run pytest tests/ -x -q
```

### Pre-PR Validation Checklist (ALL REQUIRED)

- [ ] `ruff format --check .` passes (no files need reformatting)
- [ ] `ruff check .` passes with zero errors
- [ ] `pytest tests/ -x -q` passes with zero failures

**⚠️ DO NOT proceed to create a PR if ANY checklist item fails.**

PRs that fail CI:
- Waste reviewer time
- Create noise in the repository
- Demonstrate lack of due diligence
- Will be closed without review

## Completing Tasks

Before marking a task Done, verify the Definition of Done:

### Definition of Done Checklist

1. ✅ **All acceptance criteria checked** - Every `[ ]` must be `[x]`
2. ✅ **Implementation notes added** - Describes what was built
3. ✅ **Tests pass** - All relevant tests are green
4. ✅ **Code reviewed** - Self-review completed
5. ✅ **No regressions** - Existing functionality still works
6. ✅ **Pre-PR validation passed** - Lint and tests pass locally

```bash
# Mark task as done (only after DoD is satisfied)
backlog task edit <id> -s Done
```

## Key Flags Reference

| Flag | Purpose |
|------|---------|
| `--plain` | AI-readable output (use with list/view commands) |
| `-s` | Status: "To Do", "In Progress", "Done" |
| `-a` | Assignee: @agent-identity |
| `--ac` | Add acceptance criterion |
| `--check-ac N` | Mark AC #N as complete |
| `--uncheck-ac N` | Mark AC #N as incomplete |
| `--notes` | Replace implementation notes |
| `--append-notes` | Add to existing notes |
| `--plan` | Set implementation plan |
| `-l` | Labels (comma-separated) |
| `--priority` | Priority: low, medium, high |

## Multi-line Input Syntax

For descriptions, plans, and notes with multiple lines, use ANSI-C quoting:

```bash
# Bash/Zsh - use $'...' syntax
backlog task edit <id> --notes $'Line 1\nLine 2\n\nParagraph 2'

# Or use printf
backlog task edit <id> --notes "$(printf 'Line 1\nLine 2')"
```

**Do NOT use** regular double quotes with `\n` - they won't create newlines:
```bash
# WRONG - produces literal \n characters
backlog task edit <id> --notes "Line 1\nLine 2"
```

## Common Workflows

### Engineer Workflow
```bash
# 1. Find work
backlog task list -s "To Do" --plain

# 2. Claim task
backlog task edit <id> -s "In Progress" -a @<agent>

# 3. Plan
backlog task edit <id> --plan $'1. Analyze\n2. Implement\n3. Test'

# 4. Work and check ACs progressively
backlog task edit <id> --check-ac 1
# ... do work ...
backlog task edit <id> --check-ac 2

# 5. Document
backlog task edit <id> --notes $'Implemented X with Y pattern'

# 6. Complete
backlog task edit <id> -s Done
```

### Research Workflow
```bash
# 1. Search for related tasks
backlog search "topic" --plain

# 2. Create research spike task if none exists
backlog task create "Research: <topic>" \
  --ac "Document findings" \
  --ac "Recommend approach" \
  -l research \
  --priority high

# 3. Assign and work
backlog task edit <id> -s "In Progress" -a @researcher

# 4. Add findings
backlog task edit <id> --notes $'Findings:\n- Option A: pros/cons\n- Option B: pros/cons\n\nRecommendation: Option A'
```

### Validation Workflow
```bash
# 1. Find tasks ready for validation
backlog task list -s "In Progress" --plain
backlog task list -s "Done" --plain

# 2. Review each task's ACs match implementation
backlog task <id> --plain

# 3. If validation passes, ensure DoD is met
# 4. If issues found, add notes and potentially uncheck ACs
backlog task edit <id> --append-notes $'Validation issue: AC #2 not fully met'
backlog task edit <id> --uncheck-ac 2
```

## Error Handling

If a backlog command fails:
1. Check the task ID exists: `backlog task <id> --plain`
2. Verify the backlog directory exists in project root
3. Ensure backlog CLI is installed: `backlog --version`

## Agent Identification

Use descriptive agent names when assigning tasks:
- `@pm-planner` - Product Requirements Manager
- `@software-architect` - Software Architect
- `@platform-engineer` - Platform Engineer
- `@researcher` - Researcher agent
- `@business-validator` - Business Validator
- `@frontend-engineer` - Frontend Engineer
- `@backend-engineer` - Backend Engineer
- `@ai-ml-engineer` - AI/ML Engineer
- `@quality-guardian` - QA/Quality Guardian
- `@security-engineer` - Security Engineer
- `@tech-writer` - Technical Writer
- `@release-manager` - Release Manager
- `@sre-agent` - SRE/Operations Agent
