---
name: "flow-constitution"
description: "Analyze repository and create customized constitution.md based on detected tech stack."
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
  - label: "Assess Project"
    agent: "flow-assess"
    prompt: "Constitution created. Now assess the project to determine SDD workflow suitability."
    send: false
---

@import ../../templates/commands/flow/constitution.md
