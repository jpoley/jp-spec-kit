---
name: FlowImplement
description: "Execute implementation using specialized frontend and backend engineer agents with code review."
target: "chat"
tools:
  - "Read"
  - "Write"
  - "Edit"
  - "Grep"
  - "Glob"
  - "Bash"
  - "mcp__backlog__*"
  - "mcp__serena__*"
  - "Skill"

handoffs:
  - label: "Run Validation"
    agent: "flow.validate"
    prompt: "Implementation is complete. Run validation and quality assurance."
    send: false
---

# /flow:implement - Implementation

Execute implementation using specialized engineering agents with integrated code review.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Instructions

This command implements features from backlog tasks with quality gates and code review.

**Prerequisites:**
1. Run `/flow:plan` first to create technical design
2. Have backlog tasks with acceptance criteria
3. Be on a properly named branch: `{hostname}/task-{id}/{slug}`

**Workflow:**
1. Discover backlog tasks and related specs/ADRs
2. Run quality gate on spec (`flowspec gate`)
3. Load PRP context if available (`docs/prp/{task-id}.md`)
4. Launch implementation agents:
   - **Frontend Engineer**: React, TypeScript, accessibility
   - **Backend Engineer**: APIs, databases, business logic
5. Run code reviews (frontend and backend reviewers)
6. Pre-PR validation (lint, tests, format)

**Key Commands:**
```bash
# Assign yourself to task
backlog task edit <task-id> -s "In Progress" -a @backend-engineer

# Check acceptance criteria as you complete them
backlog task edit <task-id> --check-ac 1

# Run pre-PR validation
uv run ruff check .
uv run pytest tests/ -x -q
```

**Deliverables (ALL REQUIRED):**
- Production code with all ACs satisfied
- Updated documentation
- Complete test coverage

After completion, run `/flow:validate` for comprehensive QA.
