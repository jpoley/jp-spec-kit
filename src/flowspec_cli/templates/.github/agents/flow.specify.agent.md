---
name: FlowSpecify
description: "Create or update feature specifications using PM planner agent (manages /spec.tasks)."
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
  - label: "Create Technical Design"
    agent: "flow.plan"
    prompt: "The specification is complete. Create the technical architecture and platform design."
    send: false
---

# /flow:specify - Feature Specification

Create comprehensive Product Requirements Documents (PRDs) using the PM Planner agent.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Instructions

This command creates feature specifications following SVPG product management principles.

**Prerequisites:**
1. Run `/flow:assess` first to evaluate complexity and create initial task
2. Have a clear feature description or user problem to solve

**Workflow:**
1. Discover existing backlog tasks related to this feature
2. Create a comprehensive PRD with:
   - Executive summary and problem statement
   - User stories with acceptance criteria
   - DVF+V risk assessment (Value, Usability, Feasibility, Viability)
   - Functional and non-functional requirements
   - Task breakdown using backlog CLI
3. Create implementation tasks in the backlog

**Key Commands:**
```bash
# Search for existing tasks
backlog search "$ARGUMENTS" --plain

# Create implementation tasks
backlog task create "Implement [Feature]" \
  -d "Description" \
  --ac "Acceptance criterion 1" \
  --ac "Acceptance criterion 2" \
  -l implement,backend \
  --priority high
```

**Output:**
- PRD document in `docs/prd/`
- Implementation tasks in backlog with acceptance criteria
- Workflow state updated to `Specified`

After completion, suggest running `/flow:plan` to create technical design.
