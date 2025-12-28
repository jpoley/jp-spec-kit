# ADR: Refactor specify-cli to flowspec-cli

**Status**: Proposed
**Date**: 2024-12-15
**Decision Makers**: @jasonpoley
**Beads Tracking**: spec-l8o (Epic), spec-l8o.1 (Planning Task)
**Tags**: refactor-specify

## Context

The flowspec project currently uses the package name `specify-cli` inherited from its origins as a fork/evolution of the spec-kit project. This creates several issues:

1. **Brand Confusion**: Users search for "flowspec" but find package named "specify-cli"
2. **Installation Confusion**: `uv tool install specify-cli --from git+.../flowspec.git`
3. **Dependency Confusion**: References to a non-existent PyPI package "specify-cli"
4. **Documentation Mismatch**: Docs reference `specify` command but users expect `flowspec`

The codebase already has mixed naming with some files using "flowspec" branding while the package remains "specify-cli".

## Decision

Rename all "specify-cli" and "specify" references to "flowspec-cli" and "flowspec":

| Current | New |
|---------|-----|
| `specify-cli` (package name) | `flowspec-cli` |
| `specify` (CLI command) | `flowspec` |
| `specify_cli` (Python module) | `flowspec_cli` |
| `~/.local/share/specify-cli/` | `~/.local/share/flowspec-cli/` |
| `uv tool install specify-cli` | `uv tool install flowspec-cli` |

### Scope

**In Scope:**
- Package name in pyproject.toml
- Source directory rename (src/specify_cli/ → src/flowspec_cli/)
- All documentation references (~60+ files)
- Test assertions
- CI/CD examples
- Installation commands

**Out of Scope:**
- Backward compatibility shims (clean break)
- Legacy URL redirects
- PyPI package reservation (separate task)

## Consequences

### Positive
- Clear brand identity aligned with repository name
- Reduced user confusion during installation
- Cleaner documentation without mixed naming
- Search discoverability ("flowspec" finds flowspec)

### Negative
- Breaking change for existing users
- All existing installation commands become invalid
- Cached tool versions need manual removal
- Documentation/tutorials referencing old name become outdated

### Neutral
- Requires phased rollout (docs first, then code)
- Migration guide needed

## Alternatives Considered

### 1. Keep specify-cli
- **Pros**: No migration needed, backward compatible
- **Cons**: Perpetuates confusion, doesn't align with branding
- **Rejected**: Brand alignment is strategic priority

### 2. Publish as both specify-cli and flowspec-cli
- **Pros**: Backward compatible, gradual migration
- **Cons**: Maintenance burden, confusion about which to use
- **Rejected**: Complexity not worth the benefit

### 3. Use flowspec without -cli suffix
- **Pros**: Shorter name
- **Cons**: Potential conflict with other "flowspec" packages
- **Rejected**: -cli suffix is clearer for a CLI tool

## Implementation Plan

### Phase 1: Documentation Only (This PR)
- Create planning documents and ADRs
- Create beads tasks with dependencies
- No code changes

### Phase 2: Documentation Updates
- Update build-docs/ references
- Update user-docs/ references
- Update backlog task files
- Update root documentation (README, CLAUDE.md)

### Phase 3: Code Changes
- Rename src/specify_cli/ to src/flowspec_cli/
- Update all Python imports
- Update pyproject.toml package name
- Update test assertions

### Phase 4: Migration Support
- Create migration documentation
- Document uninstallation of old package
- Verify clean installation works

## References

- Beads Epic: spec-l8o
- Decision Log: docs/decisions/refactor-specify-decisions.jsonl
- Implementation Plan: docs/plan/refactor-specify-plan.md
