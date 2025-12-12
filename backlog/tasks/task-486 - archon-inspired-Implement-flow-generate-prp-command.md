---
id: task-486
title: 'archon-inspired: Implement /flow:generate-prp command'
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-12-12 01:48'
updated_date: '2025-12-12 01:48'
labels:
  - archon-inspired
  - commands
  - context-engineering
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a command that generates PRP (Product Requirements Prompt) documents by collecting context from PRD, specs, examples, and learnings into a self-contained context bundle.

**Location**: `.claude/commands/flow/generate-prp.md`

**Pattern Source**: Based on context-engineering-intro PRP generation
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Command file created at .claude/commands/flow/generate-prp.md
- [x] #2 Accepts task-id argument to identify which task to generate PRP for
- [x] #3 Reads PRD from docs/prd/ directory
- [x] #4 Reads task memory file from backlog/memory/<task-id>.md
- [x] #5 Extracts examples from examples/ directory
- [x] #6 Collects gotchas from memory/learnings/
- [x] #7 Generates PRP at docs/prp/<task-id>.md using PRP template
- [x] #8 Command documented in CLAUDE.md
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented /flow:generate-prp command for generating PRP (Product Requirements Prompt) context bundles.

**Files Created:**
- `templates/commands/flow/generate-prp.md` - Command implementation
- `.claude/commands/flow/generate-prp.md` - Symlink to template

**Files Modified:**
- `CLAUDE.md` - Added /flow:generate-prp to slash commands section

**Command Features:**
1. Accepts task-id argument to identify target task
2. Gathers context from multiple sources:
   - Task information (title, description, ACs)
   - Task memory file (backlog/memory/<task-id>.md)
   - Related PRDs (docs/prd/)
   - Examples (examples/ directory)
   - Learnings/gotchas (memory/learnings/)
   - Codebase structure (relevant directories)
3. Generates PRP using template structure:
   - ALL NEEDED CONTEXT (Code Files, Docs, Examples, Gotchas, Related Tasks)
   - CODEBASE SNAPSHOT (Directory tree, Entry points, Integration points)
   - VALIDATION LOOP (Commands, Expected Success, Known Failure Modes)
   - ACCEPTANCE CRITERIA (from task)
   - LOOP CLASSIFICATION (Inner/Outer loop tasks)
   - IMPLEMENTATION NOTES (space for decisions, blockers, follow-ups)
4. Handles missing context gracefully with placeholders
5. Outputs summary with sources used and next steps

**Usage:**
```bash
/flow:generate-prp task-123
```

**Output:** docs/prp/<task-id>.md
<!-- SECTION:NOTES:END -->
