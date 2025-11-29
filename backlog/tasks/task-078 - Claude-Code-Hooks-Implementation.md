---
id: task-078
title: Claude Code Hooks Implementation
status: To Do
assignee: []
created_date: '2025-11-27 21:53'
updated_date: '2025-11-29 05:38'
labels:
  - specify-cli
  - hooks
  - claude-code
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement high-priority Claude Code hooks for jp-spec-kit. Phase 1: Sensitive file protection (PreToolUse), Git command safety validator (PreToolUse), Auto-format Python (PostToolUse), Auto-lint Python (PostToolUse). Phase 2: Version consistency checker, Git commit message validator, Destructive command confirmation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Implement sensitive file protection hook (PreToolUse)
- [ ] #2 Implement Git command safety validator hook (PreToolUse)
- [ ] #3 Implement auto-format Python files hook (PostToolUse)
- [ ] #4 Implement auto-lint Python files hook (PostToolUse)
- [ ] #5 Document hooks in CLAUDE.md
- [ ] #6 Test hooks with various scenarios
<!-- AC:END -->
