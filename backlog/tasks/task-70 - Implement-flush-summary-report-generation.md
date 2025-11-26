---
id: task-70
title: Implement flush summary report generation
status: To Do
assignee: []
created_date: '2025-11-26 16:41'
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
- [ ] #1 Generates timestamped summary file at backlog/archive/flush-YYYY-MM-DD-HHMMSS.md
- [ ] #2 Extracts task metadata (title, assignee, labels, priority, dates) from archived markdown files using YAML frontmatter parsing
- [ ] #3 Includes relative links to archived task files with URL-encoded paths
- [ ] #4 Handles missing metadata gracefully (displays 'None' or omits field rather than error)
- [ ] #5 Calculates and displays statistics: total archived, tasks by priority, most common labels
<!-- AC:END -->
