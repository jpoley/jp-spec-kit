---
id: task-70
title: Implement flush summary report generation
status: Done
assignee: []
created_date: '2025-11-26 16:41'
updated_date: '2025-11-26 17:11'
labels:
  - backend
  - script
  - documentation
dependencies:
  - task-69
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create the summary markdown generation module that extracts metadata from archived tasks and formats them into a human-readable report. Summary includes task titles, assignees, labels, completion statistics, and links to archived files.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Generates timestamped summary file at backlog/archive/flush-YYYY-MM-DD-HHMMSS.md
- [x] #2 Extracts task metadata (title, assignee, labels, priority, dates) from archived markdown files using YAML frontmatter parsing
- [ ] #3 Includes relative links to archived task files with URL-encoded paths
- [x] #4 Handles missing metadata gracefully (displays 'None' or omits field rather than error)
- [x] #5 Calculates and displays statistics: total archived, tasks by priority, most common labels
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Summary generation integrated into flush-backlog.sh script. Generates timestamped summaries, extracts metadata from YAML frontmatter, and handles missing metadata gracefully.
<!-- SECTION:NOTES:END -->
