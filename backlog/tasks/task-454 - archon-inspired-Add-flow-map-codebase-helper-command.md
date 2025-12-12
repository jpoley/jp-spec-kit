---
id: task-454
title: 'archon-inspired: Add /flow:map-codebase helper command'
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-12-12 01:00'
updated_date: '2025-12-12 01:54'
labels:
  - archon-inspired
  - architecture
  - commands
  - context-engineering
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a helper command that generates bounded directory tree listings and feature maps for relevant parts of the codebase.

**Location**: `.claude/commands/flow/map-codebase.md`

**Purpose**: Ensure every feature has a short, readable map of the code area it touches. Supports PRP generation and feature context.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Command file created at .claude/commands/flow/map-codebase.md
- [x] #2 Accepts one or more paths of interest (directories under src/)
- [x] #3 Runs bounded directory tree listing (limited depth)
- [x] #4 Filters to relevant files only (excludes node_modules, __pycache__, etc.)
- [x] #5 Can write output to: PRP file under CODEBASE SNAPSHOT section OR separate file at docs/feature-maps/<task-id>.md
- [x] #6 Supports --depth flag for tree depth control
- [x] #7 Supports --output flag for destination control
- [x] #8 Command documented in CLAUDE.md slash commands section
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented /flow:map-codebase helper command for generating bounded directory tree listings.

**Files Created:**
- `templates/commands/flow/map-codebase.md` - Command implementation
- `.claude/commands/flow/map-codebase.md` - Symlink to template

**Files Modified:**
- `CLAUDE.md` - Added /flow:map-codebase to slash commands section

**Command Features:**
1. Accepts one or more paths of interest (src/, tests/, etc.)
2. Runs bounded directory tree listing with configurable depth
3. Excludes common non-essential directories (node_modules, __pycache__, .git, .venv, etc.)
4. Identifies key entry points (main.py, index.ts, app.py, etc.)
5. Identifies integration points (routes, models, config files)
6. Generates file type summary
7. Supports --depth flag for tree depth control (default: 3)
8. Supports --output flag to write to specific file
9. Supports --prp flag to update CODEBASE SNAPSHOT section in PRP files
10. Uses tree command when available, falls back to find

**Usage:**
```bash
/flow:map-codebase src/                    # Single path
/flow:map-codebase src/ tests/ --depth 4   # Multiple paths with depth
/flow:map-codebase src/ --prp task-123     # Update PRP file
/flow:map-codebase src/ --output docs/feature-maps/auth.md
```

**Output:** Directory tree, key entry points table, integration points table, file type summary
<!-- SECTION:NOTES:END -->
