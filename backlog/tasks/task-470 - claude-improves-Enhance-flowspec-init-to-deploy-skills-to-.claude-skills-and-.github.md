---
id: task-470
title: >-
  claude-improves: Enhance flowspec init to deploy skills to .claude/skills/ and
  .github/
status: In Progress
assignee:
  - '@myself'
created_date: '2025-12-12 01:15'
updated_date: '2025-12-22 21:55'
labels:
  - claude-improves
  - cli
  - specify-init
  - skills
  - phase-1
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Extend flowspec init to copy skill templates from templates/skills/ to the project's .claude/skills/ directory AND deploy GitHub Copilot prompts/skills to .github/ for dual-agent support.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 specify init copies all skills from templates/skills/ to .claude/skills/
- [ ] #2 Skills maintain proper SKILL.md directory structure
- [ ] #3 Existing skills in .claude/skills/ are not overwritten without --force flag
- [ ] #4 Add --skip-skills flag to opt out of skill deployment
- [ ] #5 Document skill deployment in init output

- [ ] #6 Deploy GitHub Copilot prompts to .github/prompts/ directory
- [ ] #7 Sync skills between .claude/skills/ and .github/ for dual-agent support
<!-- AC:END -->
