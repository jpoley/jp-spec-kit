---
id: task-410
title: 'Documentation Overhaul: Rebrand and Accuracy Review for Specflow'
status: To Do
assignee: []
created_date: '2025-12-10 02:26'
labels:
  - documentation
  - specflow
  - branding
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The documentation site (https://jpoley.github.io/jp-spec-kit/) contains inherited content from the upstream "Spec Kit" project that needs to be thoroughly reviewed and updated to accurately represent Specflow.

## Current State
- 325+ references to "Spec Kit" in docs/
- Links pointing to github/spec-kit instead of jpoley/jp-spec-kit
- Content describes upstream Spec Kit features, not Specflow-specific functionality
- Terminology inconsistency: "Spec Kit", "jp-spec-kit", "Specflow" used interchangeably

## Scope
This is NOT a simple find-and-replace. The docs need:
1. **Branding update**: "Spec Kit" → "Specflow" where referring to this project
2. **Accuracy review**: Verify each doc page reflects actual Specflow features
3. **Link audit**: Fix all broken/incorrect GitHub links
4. **Feature alignment**: Remove/update docs for features that don't exist or work differently in Specflow
5. **New content**: Document Specflow-specific features not in upstream (specflow commands, workflow system, etc.)

## Key Directories to Review
- `docs/guides/` - User guides (33 files)
- `docs/reference/` - Reference docs
- `docs/examples/` - Example workflows
- `docs/adr/` - Architecture Decision Records
- `docs/platform/` - Platform-specific docs
- `docs/index.md` - Landing page
- `docs/installation.md` - Installation guide
- `docs/quickstart.md` - Quick start guide

## Deliverables
- [ ] Audit all 100+ doc files for accuracy
- [ ] Update branding to Specflow consistently
- [ ] Fix all GitHub links to point to jpoley/jp-spec-kit
- [ ] Remove or flag docs for non-existent features
- [ ] Ensure installation/quickstart guides work for Specflow
- [ ] Update toc.yml to reflect actual available docs
- [ ] Verify docfx build succeeds with all changes
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All references to 'Spec Kit' reviewed and updated appropriately to 'Specflow'
- [ ] #2 All GitHub links point to jpoley/jp-spec-kit (not github/spec-kit)
- [ ] #3 Installation and quickstart guides tested and working
- [ ] #4 No broken internal links in documentation site
- [ ] #5 toc.yml matches actual available documentation files
- [ ] #6 DocFX build completes without errors
- [ ] #7 Documentation accurately reflects Specflow features and capabilities
<!-- AC:END -->
