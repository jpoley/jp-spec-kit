---
id: task-424
title: 'Phase 7: Migrate Documentation Files'
status: To Do
assignee: []
created_date: '2025-12-10 02:59'
labels:
  - migration
  - documentation
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Rename specflow-specific documentation files and update all /specflow references across 50+ docs files. Update diagrams, guides, references, ADRs, and table of contents. DEPENDS ON: task-423 source code migration.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Documentation files with specflow in filename renamed (16 files)
- [ ] #2 All /specflow: command references updated in docs
- [ ] #3 Config file references updated: specflow_workflow.yml → specflow_workflow.yml
- [ ] #4 File path references updated: commands/specflow/ → commands/specflow/
- [ ] #5 Cross-reference links updated in all docs
- [ ] #6 Table of contents updated: docs/toc.yml
- [ ] #7 Diagram files renamed and updated: specflow-workflow.* → specflow-workflow.*
- [ ] #8 CLAUDE.md updated with /specflow commands
- [ ] #9 README.md updated with /specflow references
- [ ] #10 No broken links: validation check passes
<!-- AC:END -->
