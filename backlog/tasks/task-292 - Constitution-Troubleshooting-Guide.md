---
id: task-292
title: Constitution Troubleshooting Guide
status: Done
assignee:
  - '@galway'
created_date: '2025-12-04 16:18'
updated_date: '2025-12-04 17:47'
labels:
  - constitution-cleanup
dependencies:
  - task-244
  - task-245
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Help users resolve common constitution issues and validation problems
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Issue: LLM generated incorrect language detection
- [x] #2 Issue: Constitution validation stuck on unresolvable NEEDS_VALIDATION
- [x] #3 Issue: /jpspec command blocked by unvalidated constitution
- [x] #4 Issue: Constitution version mismatch after upgrade
- [x] #5 Each issue includes symptoms, cause, resolution
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created comprehensive constitution troubleshooting guide at docs/guides/constitution-troubleshooting.md

## Coverage

**Language Detection Issues**:
- Symptoms: Wrong/missing languages in TECH_STACK
- Cause: LLM scanning issues, non-standard structure
- Resolution: Manual edit + remove NEEDS_VALIDATION marker

**Validation Issues**:
- Stuck NEEDS_VALIDATION markers
- Genuinely unknown content (TBD scenarios)
- Step-by-step removal process

**Workflow Command Issues**:
- Heavy tier blocking /jpspec commands
- Solutions: Complete validation, downgrade tier, skip-validation flag
- When each tier is appropriate

**Version Issues**:
- Version mismatch after upgrade
- Constitution upgrade conflicts
- Backup and restore procedures

**File Issues**:
- Missing constitution file
- Permission denied errors
- Corrupted file recovery

## Structure

- Quick diagnostics section
- 5 main issue categories (per ACs)
- Each issue includes: symptoms, causes, resolution
- Prevention best practices
- Emergency recovery procedures
- Related documentation links

## Format Consistency

- Follows existing troubleshooting guide patterns
- Clear problem/solution format
- Actionable bash commands with examples
- Cross-references to related docs
<!-- SECTION:NOTES:END -->
