---
id: task-186
title: Add Thinking Triggers to Complex Slash Commands
status: Done
assignee: []
created_date: '2025-12-01 05:04'
updated_date: '2025-12-04 01:25'
labels:
  - claude-code
  - slash-commands
  - quick-win
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add extended thinking trigger guidance to complex slash commands to improve output quality for architecture, security, and research tasks.

Cross-reference: See docs/prd/claude-capabilities-review.md Section 2.11 for thinking mode assessment.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 /jpspec:plan includes 'think hard' guidance for architecture decisions

- [x] #2 /jpspec:validate includes 'think hard' guidance for security analysis
- [x] #3 /jpspec:research includes 'megathink' guidance for comprehensive analysis
- [x] #4 CLAUDE.md documents thinking budget levels (think, megathink, ultrathink)
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Thinking triggers added to all relevant jpspec commands:

- /jpspec:plan: "🧠 Think Hard" section for architecture decisions
- /jpspec:validate: "🧠 Think Hard" section for security analysis
- /jpspec:research: "🧠 Megathink" section for comprehensive analysis

Documented in memory/claude-thinking.md with thinking budget levels:
- think (4K tokens)
- think hard (10K tokens)
- megathink (10K tokens)
- ultrathink (31,999 tokens)

Included via @import in CLAUDE.md
<!-- SECTION:NOTES:END -->
