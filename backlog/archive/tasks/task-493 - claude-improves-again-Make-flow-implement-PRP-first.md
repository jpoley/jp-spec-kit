---
id: task-493
title: 'claude-improves-again: Make /flow:implement PRP-first'
status: Done
assignee:
  - '@muckross'
created_date: '2025-12-14 03:06'
updated_date: '2025-12-17 01:27'
labels:
  - context-engineering
  - commands
  - claude-improves-again
dependencies:
  - task-491
  - task-492
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update /flow:implement to check for and load PRP files as primary context. If PRP exists for the active task, load it first. If not, recommend running /flow:generate-prp before implementation.

Source: docs/research/archon-inspired.md Task 6
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 /flow:implement checks for docs/prp/<task-id>.md
- [x] #2 If PRP exists, loads it as primary context for the agent
- [x] #3 If PRP missing, recommends: Generate PRP via /flow:generate-prp first
- [x] #4 Documentation updated to explain PRP-first workflow
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementation complete for PRP-first workflow in /flow:implement.

Key changes:
- Added Phase 0.5 to templates/commands/flow/implement.md
- Phase checks for docs/prp/<task-id>.md before implementation
- If PRP exists: loads it as primary context for all engineer agents
- If PRP missing: warns and recommends running /flow:generate-prp first
- Updated all engineer agent contexts (frontend, backend, AI/ML) to reference PRP
- Enhanced templates/docs/prp/README.md with PRP-first workflow documentation
- Added benefits table and complete workflow example

All acceptance criteria verified:
✓ AC #1: /flow:implement checks for docs/prp/<task-id>.md
✓ AC #2: Loads PRP as primary context when found
✓ AC #3: Recommends /flow:generate-prp when missing
✓ AC #4: Documentation updated with PRP-first workflow

Pull Request: https://github.com/jpoley/flowspec/pull/903
<!-- SECTION:NOTES:END -->
