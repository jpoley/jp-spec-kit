---
id: task-136
title: Add Primary Support for claude-trace Observability Tool
status: To Do
assignee:
  - '@kinsale'
created_date: '2025-11-28 22:03'
updated_date: '2025-12-04 17:07'
labels:
  - observability
  - documentation
  - outer-loop
  - tooling
  - 'workflow:Specified'
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Integrate claude-trace as a recommended observability and debugging tool for Flowspec users, particularly for troubleshooting complex /flowspec workflow executions. This will provide visibility into AI agent decision-making, token usage, and internal Claude Code operations without requiring code changes to Flowspec.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Documentation added to docs/guides/claude-trace-integration.md explaining what claude-trace is and why it's valuable for SDD workflows
- [ ] #2 Installation instructions added including npm install command and prerequisites (Node.js 16+)
- [ ] #3 Usage guide created showing how to capture /flow:* command traces with concrete examples
- [ ] #4 Troubleshooting section added documenting known issues (#46 indexing hangs, #48 native binary compatibility) with workarounds
- [ ] #5 Privacy and security guidance added explaining PII risks and data retention recommendations
- [ ] #6 Integration with existing troubleshooting workflows documented (how claude-trace complements headless mode)
- [ ] #7 Example trace analysis walkthrough created showing how to debug a failed /flow:implement workflow
- [ ] #8 Reference added to CLAUDE.md in the troubleshooting section linking to claude-trace guide
- [ ] #9 Reference added to outer-loop.md observability section as recommended tool
- [ ] #10 Backlog.md integration documented - how to use claude-trace when working on tasks
<!-- AC:END -->
