---
name: "flow-checklist"
description: "Generate a custom checklist for the current feature based on user requirements."
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
  - label: "Execute Tasks"
    agent: "flow-implement"
    prompt: "The checklist is ready. Execute the implementation based on the checklist items."
    send: false
---

@import ../../templates/commands/flow/checklist.md
