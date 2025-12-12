---
id: task-450
title: 'archon-inspired: Add ''Known Gotchas / Prior Failures'' section to templates'
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-12-12 01:00'
updated_date: '2025-12-12 01:39'
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
Ensure both PRD and PRP templates include a structured section for known gotchas and prior failures. Forces each feature doc to explicitly enumerate prior lessons.

**Targets**: 
- PRD template
- PRP template

**Purpose**: Automatically surface historical lessons in every feature's context bundle
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Known Gotchas section added to PRD template
- [x] #2 Known Gotchas section added to PRP template
- [x] #3 Section includes: Links to learning documents
- [x] #4 Section includes: Brief descriptions of what went wrong previously
- [x] #5 Section includes: Task IDs of prior related failures
- [x] #6 Section is positioned prominently (not buried at end)
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
This task was already satisfied by prior tasks in this archon-inspired batch.

**Existing Sections Found:**

1. **PRD Template** (`templates/prd-template.md`, lines 134-149):
   - Section: "Gotchas / Prior Failures" within "All Needed Context"
   - Table format: Gotcha | Impact | Mitigation | Source
   - Source column includes task IDs and doc links
   - Comment block lists sources: memory/learnings/*.md, task notes, ADRs, post-mortems

2. **PRP Template** (`templates/docs/prp/prp-base-flowspec.md`, lines 62-77):
   - Section: "Known Gotchas" within "ALL NEEDED CONTEXT"
   - Same table format for consistency
   - Same source documentation

**AC Verification:**
- AC1-2: Sections exist in both templates
- AC3: Source column links to learning docs
- AC4: Impact column captures what went wrong
- AC5: Source column explicitly includes task-XXX format
- AC6: Both positioned in "All Needed Context" section (middle of doc, not buried)

No code changes needed - sections were added in task-447 (PRP template) and task-448 (PRD All Needed Context).
<!-- SECTION:NOTES:END -->
