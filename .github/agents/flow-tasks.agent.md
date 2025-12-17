---
name: "flow-tasks"
description: "Generate an actionable, dependency-ordered task backlog for the feature based on available design artifacts."
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
  - label: "Analyze Tasks"
    agent: "flow-analyze"
    prompt: "Tasks generated. Analyze the tasks for consistency with spec and plan."
    send: false
  - label: "Implement Tasks"
    agent: "flow-implement"
    prompt: "Tasks generated. Begin implementation of the task backlog."
    send: false
---

@import ../../templates/commands/flow/tasks.md
