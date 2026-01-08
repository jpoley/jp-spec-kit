---
name: FlowPlan
description: "Execute planning workflow using project architect and platform engineer agents to create ADRs and platform design."
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
  - label: "Start Implementation"
    agent: "flow.implement"
    prompt: "The technical design is complete. Start implementing the feature."
    send: false
---

# /flow:plan - Technical Planning

Create comprehensive architectural and platform planning using specialized agents.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Instructions

This command creates technical architecture and platform design following Gregor Hohpe's principles.

**Prerequisites:**
1. Run `/flow:specify` first to create PRD
2. Have specification with clear requirements

**Workflow:**
1. Discover existing backlog tasks and PRD documents
2. Launch parallel planning agents:
   - **System Architecture**: ADRs, component design, integration patterns
   - **Platform & Infrastructure**: CI/CD, DevSecOps, observability
3. Create planning artifacts in `docs/adr/` and `docs/platform/`
4. Update backlog with planning tasks

**Key Principles:**
- Architecture as selling options (defer decisions until maximum information)
- Enterprise Integration Patterns for service communication
- Platform Quality Framework (7 C's)
- DORA Elite Performance targets

**Output:**
- Architecture Decision Records (ADRs) in `docs/adr/`
- Platform design document in `docs/platform/`
- API contracts and data models
- Workflow state updated to `Planned`

After completion, suggest running `/flow:implement` to start coding.
