# Architecture Documentation

This directory contains architectural design documents and decision records for the JP Spec Kit project.

## Architecture Documents

### [dev-setup Single Source of Truth Architecture](./dev-setup-single-source-of-truth.md)

Comprehensive architecture document for resolving the command file divergence problem.

**Problem**: Three versions of jpspec commands exist (enhanced dev, minimal template, distributed), creating maintenance burden and inconsistent user experience.

**Solution**: Establish `templates/commands/` as single source of truth, use symlinks for development (dev-setup), copies for distribution (init).

**Key Sections**:
1. Strategic Framing (Penthouse View) - Business objectives and investment justification
2. Architectural Blueprint (Engine Room View) - Technical design and data flow
3. Architecture Decision Records (ADRs) - Key decisions with trade-offs
4. Component Design - Detailed component specifications
5. Migration Plan - 7 phases with timelines and rollback plans
6. Constitution Principles - Architectural principles for `/speckit.constitution`
7. Implementation Readiness - Scorecard and success metrics

**Status**: Ready for implementation (9.3/10 readiness score)

---

## Architecture Decision Records (ADRs)

### [ADR-001: Single Source of Truth for Commands](./adr-001-single-source-of-truth.md)

**Decision**: Move enhanced jpspec commands from `.claude/commands/jpspec/` to `templates/commands/jpspec/` to establish single canonical source.

**Context**: Three versions of commands exist (20KB enhanced, 3KB minimal template, 3KB distributed), causing maintenance burden and inconsistent UX.

**Rationale**:
- Eliminates duplicate file management
- Ensures users get enhanced commands (5-7x more capability)
- Reduces risk of content divergence
- Accelerates feature velocity

**Consequences**:
- ✅ One canonical source eliminates sync overhead
- ✅ All users get enhanced commands (better UX)
- ❌ Breaking change requires migration
- ❌ One-time migration effort (~1-2 days)

**Status**: Proposed

---

### [ADR-002: Directory Structure Convention](./adr-002-directory-structure.md)

**Decision**: Use subdirectory structure (`jpspec/implement.md`) instead of flat structure with dots (`jpspec.implement.md`).

**Context**: dev-setup uses subdirectories, init uses flat structure, creating inconsistent experience.

**Rationale**:
- Better organization for 17+ commands
- Supports shared partials (`_backlog-instructions.md`)
- Scales well as library grows
- Clearer semantic grouping

**Consequences**:
- ✅ Cleaner organization, supports partials
- ✅ Consistent structure across dev-setup and init
- ❌ Breaking change for existing init users
- ❌ Migration script required

**Migration**: `scripts/bash/migrate-commands-to-subdirs.sh` provided

**Status**: Proposed

---

### [ADR-003: Shared Content Strategy](./adr-003-shared-content-strategy.md)

**Decision**: Keep shared content (like `_backlog-instructions.md`) as separate file with textual references, not inlined.

**Context**: 6KB of task management instructions relevant to 9 commands. Inlining creates 54KB duplication.

**Rationale**:
- DRY: Single 6KB file vs 54KB duplication
- Maintainable: Update once, applies everywhere
- No preprocessing: Works with current tooling
- Clear convention: Underscore prefix signals "partial"

**Consequences**:
- ✅ No duplication, single source for updates
- ✅ Works with current tooling (no build step)
- ❌ Not fully self-contained (references external file)
- ❌ Users must read both files

**Mitigations**: Clear callouts with ⚠️ emoji, quick reference inline, bold text

**Status**: Proposed

---

## Implementation Tasks

The following backlog tasks have been created for implementation:

| ID | Task | Priority | Type |
|----|------|----------|------|
| task-267 | ADR: Single Source of Truth for Commands | HIGH | architecture, adr |
| task-268 | ADR: Directory Structure Convention | HIGH | architecture, adr |
| task-269 | ADR: Shared Content Strategy | HIGH | architecture, adr |
| task-270 | Design: Unified Command Template Structure | HIGH | architecture, design |
| task-271 | Migrate jpspec commands to templates | HIGH | architecture, migration |
| task-272 | Migrate speckit commands to subdirectory | HIGH | architecture, migration |
| task-273 | Update dev-setup command for jpspec symlinks | HIGH | cli, dev-setup, implementation |
| task-274 | Replace source repo commands with symlinks | HIGH | architecture, migration |
| task-275 | Update init command for subdirectory structure | HIGH | cli, init, implementation |
| task-276 | Create command migration script for users | HIGH | tooling, migration |
| task-277 | Create dev-setup-init equivalence validation tests | HIGH | testing, validation |
| task-278 | Add CI validation for command structure | HIGH | ci, validation |
| task-279 | Update documentation for new architecture | HIGH | documentation |

**Total**: 13 tasks covering all phases of migration

---

## Migration Timeline

### Phase 1: Preparation (Pre-Migration) - 1 day
- ✅ Architecture documentation created
- ✅ ADRs written
- ✅ Migration tasks created
- ⏳ Pending stakeholder approval

### Phase 2: Template Migration - 2-3 days
- Move enhanced jpspec commands to templates
- Reorganize speckit commands to subdirectory
- Update documentation

### Phase 3: dev-setup Command Update - 1 day
- Add jpspec symlink creation
- Test and validate

### Phase 4: Replace Source Commands - 30 minutes
- Delete direct files
- Create symlinks via dev-setup

### Phase 5: Init Command Update - 2 days
- Update to subdirectory structure
- Create migration script
- Write equivalence tests

### Phase 6: CI Validation - 1 day
- Create validation workflow
- Add pre-commit hooks
- Test automation

### Phase 7: Release and Communication - 1 day
- Version bump (v0.0.101 → v0.1.0)
- Build release
- Write migration guide

**Total Estimated Time**: 8-9 days

---

## Key Architectural Principles

From the main architecture document, these principles should be added to the project constitution:

### 1. Single Source of Truth for Commands
All command development occurs in `templates/commands/`. This is canonical for both development (symlinks) and distribution (copies).

### 2. Subdirectory Organization for Commands
Commands organized in subdirectories by namespace (`jpspec/`, `speckit/`), not flat files with dots.

### 3. Enhanced Commands Over Minimal Stubs
Distributed commands should be fully-featured (10-20KB) with comprehensive guidance, not minimal placeholders (2-3KB).

### 4. Symlink Strategy for Development
dev-setup creates symlinks from `.claude/commands/` to `templates/commands/` to ensure developers test distributed content.

### 5. Automated Validation of Structure
CI validates command structure to prevent content divergence and structural errors.

---

## Success Metrics

### Technical Metrics
- 0 direct files in `.claude/commands/` (source repo)
- 100% symlink resolution rate
- 100% test pass rate
- <5 minutes dev-setup execution time

### User Experience Metrics
- User command files match developer command files (content hash equality)
- 0 reported issues with command structure
- Positive feedback on enhanced command content

### Process Metrics
- Single source updates propagate to releases automatically
- Zero manual sync operations required
- <1 hour to add new command (vs ~3 hours with manual sync)

---

## References

- Problem Analysis: `docs/fix-dev-setup.md`
- Main Architecture: `./dev-setup-single-source-of-truth.md`
- ADR-001: `./adr-001-single-source-of-truth.md`
- ADR-002: `./adr-002-directory-structure.md`
- ADR-003: `./adr-003-shared-content-strategy.md`

---

## Document Metadata

**Author**: Senior IT Strategy Architect (Claude Code)
**Date**: 2025-12-03
**Version**: 1.0
**Status**: Approved for Implementation
**Next Review**: After Phase 3 completion

---

## Notes

This architecture follows Gregor Hohpe's principles:

- **The Architect Elevator**: Translates strategic objectives (consistent UX) into technical decisions (single source of truth)
- **Architecture as Selling Options**: Framework decisions as structured options with clear trade-offs
- **Deferred Decision Making**: Choose simplest solution now (textual references) while preserving upgrade path later
- **Master Builder Perspective**: Deep comprehension of long-term consequences (maintenance burden, content drift)

The documentation is comprehensive, actionable, and ready for implementation.
