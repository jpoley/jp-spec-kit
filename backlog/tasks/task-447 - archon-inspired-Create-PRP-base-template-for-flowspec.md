---
id: task-447
title: 'archon-inspired: Create PRP base template for flowspec'
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-12-12 01:00'
updated_date: '2025-12-12 01:31'
labels:
  - archon-inspired
  - architecture
  - templates
  - context-engineering
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a Product Requirements Prompt (PRP) template that acts as a self-contained context packet for each feature. If you give this PRP to an LLM as the only context, it should have everything needed to work on the feature.

**Location**: `templates/docs/prp/prp-base-flowspec.md`

**Pattern Source**: Based on context-engineering-intro PRP structure
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Template file created at templates/docs/prp/prp-base-flowspec.md
- [x] #2 Contains ALL NEEDED CONTEXT section with subsections: Code Files, Docs/Specs, Examples, Known Gotchas, Related Backlog Tasks
- [x] #3 Contains CODEBASE SNAPSHOT section (bounded directory tree placeholder)
- [x] #4 Contains VALIDATION LOOP section: Commands, Expected Success, Known Failure Modes
- [x] #5 All sections are machine-parseable with consistent heading structure
- [x] #6 Template includes explanatory comments for each section
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create templates/docs/prp/ directory
2. Create prp-base-flowspec.md template
3. Add ALL NEEDED CONTEXT section with all subsections
4. Add CODEBASE SNAPSHOT section with tree placeholder
5. Add VALIDATION LOOP section with commands/success/failures
6. Ensure consistent heading structure for machine parsing
7. Add explanatory comments throughout
8. Create README for directory
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented PRP (Product Requirements Prompt) template based on archon-inspired context engineering patterns.

**Files Created:**
- `templates/docs/prp/prp-base-flowspec.md` - Main PRP template
- `templates/docs/prp/README.md` - Directory documentation

**Template Sections:**
1. **FEATURE SUMMARY** - Brief overview with task metadata
2. **ALL NEEDED CONTEXT** - Machine-parseable tables:
   - Code Files (path, purpose, read priority)
   - Docs/Specs (PRDs, ADRs, tech specs)
   - Examples (location, what it demonstrates)
   - Known Gotchas (impact, mitigation, source)
   - Related Backlog Tasks (relationship, status)
3. **CODEBASE SNAPSHOT** - Directory tree structure with:
   - Key Entry Points table
   - Integration Points table
4. **VALIDATION LOOP** - Feature-specific validation:
   - Commands (bash blocks with specific commands)
   - Expected Success (criteria table)
   - Known Failure Modes (failure, meaning, fix)
5. **ACCEPTANCE CRITERIA** - Checkbox list from task
6. **LOOP CLASSIFICATION** - Inner/outer loop responsibilities
7. **IMPLEMENTATION NOTES** - Space for decisions, blockers, follow-ups

**Key Features:**
- All sections use consistent table format for machine parsing
- HTML comments explain each section's purpose
- Placeholder variables use {{VARIABLE}} syntax
- Self-contained: provides everything needed to implement feature
<!-- SECTION:NOTES:END -->
