---
id: task-443
title: Update documentation files for flowspec to flowspec rename
status: To Do
assignee: []
created_date: '2025-12-11 01:32'
labels:
  - documentation
  - rename
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update all documentation to reflect flowspec → flowspec rename:

Documentation files (10+ files):
- docs/guides/workflow-step-implementation-guide.md
- docs/guides/workflow-step-visual-reference.md
- docs/guides/workflow-architecture.md
- docs/guides/workflow-customization.md
- docs/guides/security-workflow-integration.md
- docs/guides/team-mode-workflow.md
- docs/guides/release-workflow-fix.md
- docs/guides/workflow-troubleshooting.md
- docs/guides/flowspec-backlog-workflow.md → docs/guides/flowspec-backlog-workflow.md
- docs/guides/flowspec-workflow-guide.md → docs/guides/flowspec-workflow-guide.md
- CLAUDE.md files (project root and subdirectories)
- README.md

Updates needed:
1. Rename files with 'flowspec' in name to 'flowspec'
2. Update all command examples: /flow: → /flow:
3. Update file references: flowspec_workflow.yml → flowspec_workflow.yml
4. Update directory paths: commands/flowspec → commands/flowspec
5. Update section headings and titles
6. Update configuration examples
7. Add migration notes where appropriate

Special attention:
- CLAUDE.md: Update slash command reference table
- README.md: Update quick start and examples
- Workflow guides: Update state diagrams and examples
- Integration guides: Update command sequences
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All docs files renamed from flowspec-* to flowspec-*
- [ ] #2 All command examples use /flow: prefix
- [ ] #3 CLAUDE.md slash command table updated
- [ ] #4 README quick start uses /flow: commands
- [ ] #5 Configuration examples reference flowspec_workflow.yml
- [ ] #6 Migration notes added to changelog
- [ ] #7 All internal links verified and working
- [ ] #8 No broken references to old flowspec names
<!-- AC:END -->
