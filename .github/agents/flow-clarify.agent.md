---
name: "flow-clarify"
description: "Identify underspecified areas in the current feature spec by asking up to 5 highly targeted clarification questions and encoding answers back into the spec."
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
  - label: "Update Specification"
    agent: "flow-specify"
    prompt: "Based on the clarifications, update the feature specification with the additional details."
    send: false
---

@import ../../templates/commands/flow/clarify.md
