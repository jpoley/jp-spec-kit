---
id: task-475
title: 'claude-improves: Create symlinks for GitHub prompts to commands'
status: To Do
assignee:
  - '@kinsale'
created_date: '2025-12-12 01:15'
updated_date: '2026-01-06 18:52'
labels:
  - claude-improves
  - source-repo
  - prompts
  - commands
  - symlinks
  - phase-2
dependencies: []
priority: high
ordinal: 30000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
9 speckit prompts in .github/prompts/speckit.*.prompt.md are 3-4 line stubs while full content (100+ lines) exists in .claude/commands/.

This causes content divergence. Should use symlinks from prompts to commands for single-source-of-truth.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Identify all prompts that duplicate command content
- [ ] #2 Replace stub prompts with symlinks to corresponding commands
- [ ] #3 Verify symlinks work correctly in both GitHub Copilot and Claude Code
- [ ] #4 Document symlink strategy in CLAUDE.md
- [ ] #5 Add CI check to validate prompt-command symlinks
<!-- AC:END -->
