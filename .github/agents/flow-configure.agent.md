---
name: "flow-configure"
description: "Configure or reconfigure workflow settings including role selection and validation modes."
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
  - label: "Initialize Project"
    agent: "flow-init"
    prompt: "Configuration complete. Initialize the project with the new settings."
    send: false
---

@import ../../templates/commands/flow/configure.md
