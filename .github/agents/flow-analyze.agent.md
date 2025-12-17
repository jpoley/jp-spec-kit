---
name: "flow-analyze"
description: "Perform a non-destructive cross-artifact consistency and quality analysis across spec.md, plan.md, and tasks.md after task generation."
target: "chat"
tools:
  - "Read"
  - "Grep"
  - "Glob"
  - "Bash"
  - "mcp__backlog__*"
  - "mcp__serena__*"
  - "Skill"

handoffs:
  - label: "Fix Issues"
    agent: "flow-specify"
    prompt: "Based on the analysis, update the specification to address identified issues."
    send: false
---

@import ../../templates/commands/flow/analyze.md
