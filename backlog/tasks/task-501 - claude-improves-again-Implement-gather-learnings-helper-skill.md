---
id: task-501
title: 'claude-improves-again: Implement gather-learnings helper skill'
status: Done
assignee:
  - '@muckross'
created_date: '2025-12-14 03:07'
updated_date: '2025-12-17 01:28'
labels:
  - context-engineering
  - skills
  - claude-improves-again
dependencies:
  - task-500
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a skill that reads learning files from memory/learnings and matches entries based on file paths, keywords, or tags. Returns curated list for insertion into PRD/PRP gotchas section.

Source: docs/research/archon-inspired.md Task 14
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Skill created at .claude/skills/gather-learnings/SKILL.md
- [x] #2 Reads learning files from memory/learnings directory
- [x] #3 Matches entries by relevant file paths
- [x] #4 Matches entries by keywords or tags
- [x] #5 Returns curated list suitable for PRD/PRP insertion
- [x] #6 Can be invoked by /flow:specify and /flow:generate-prp
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented gather-learnings helper skill for extracting relevant lessons from memory/learnings directory.

Key Implementation Details:

1. Skill Structure:
   - Created .claude/skills/gather-learnings/SKILL.md
   - Follows established pattern from pm-planner, architect, sdd-methodology
   - YAML frontmatter with name and description
   - Comprehensive documentation with examples

2. Matching Strategies:
   - File path matching (direct and directory-level)
   - Keyword matching (case-insensitive, with synonyms)
   - Tag/category matching (issue types, tech stack)
   - Contextual relevance scoring

3. Output Format:
   - Markdown table ready for PRD/PRP insertion
   - Columns: Gotcha | Impact | Mitigation | Source
   - Top 5-8 most relevant learnings
   - Explicit notice when few/no matches

4. Example Learning File:
   - Created memory/learnings/example-skill-implementation.md
   - Demonstrates expected structure and metadata
   - Shows gotcha extraction example
   - Includes tags for testing matching

5. Integration Points:
   - Invocable by /flow:specify
   - Invocable by /flow:generate-prp
   - Can be used manually for doc updates

Changes:
- Added .claude/skills/gather-learnings/SKILL.md (9KB, comprehensive skill)
- Added memory/learnings/example-skill-implementation.md (4KB, template/example)
- Updated task-501 with all ACs checked

PR: #906
Branch: feat/task-501-gather-learnings-v1
<!-- SECTION:NOTES:END -->
