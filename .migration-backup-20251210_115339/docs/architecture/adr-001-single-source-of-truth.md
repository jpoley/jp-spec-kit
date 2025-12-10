# ADR-001: Single Source of Truth for Commands

**Status**: Proposed

**Date**: 2025-12-03

**Deciders**: JP Spec Kit Development Team

**Context and Problem Statement**:

We currently have three different versions of jpspec commands:

1. **Enhanced versions** in `.claude/commands/jpspec/` (20KB files with full backlog integration)
2. **Minimal versions** in `templates/commands/jpspec/` (3KB files, basic stubs)
3. **Distributed versions** (same as #2, installed by `specify init`)

This creates several problems:

- **Maintenance burden**: Must manually sync enhancements from version #1 to #2
- **Inconsistent user experience**: Developers get superior commands (#1), end users get minimal versions (#2)
- **Feature drift risk**: Enhancements made in #1 during development never propagate to #2
- **Confusion about canonical version**: Which file should be edited?
- **Sync errors**: Manual copying is error-prone and often forgotten

**Concrete Example**:

```
implement.md file sizes:
- .claude/commands/jpspec/implement.md:     19,960 bytes (6.8x larger)
- templates/commands/jpspec/implement.md:    2,945 bytes
- nanofuse .claude/commands/implement.md:    2,933 bytes (user gets minimal)
```

End users get a vastly inferior experience (3KB stub) compared to what jp-spec-kit developers use during development (20KB enhanced).

---

## Decision Drivers

1. **Maintainability**: Reduce duplicate file management overhead
2. **User Experience**: All users should get the same high-quality commands
3. **Development Velocity**: Changes should propagate automatically to releases
4. **Risk Reduction**: Eliminate sync errors from manual copying
5. **Clarity**: One obvious place to edit commands

---

## Considered Options

### Option 1: Keep Current Dual-Source Model (Status Quo)

**Description**: Continue maintaining enhanced commands in `.claude/commands/jpspec/` and minimal templates in `templates/commands/jpspec/`.

**Pros**:
- No migration needed
- No breaking changes
- Familiar to current developers

**Cons**:
- ❌ Ongoing maintenance burden (manual sync)
- ❌ Users get inferior commands (3KB vs 20KB)
- ❌ High risk of content divergence
- ❌ Slow feature velocity (must update 2 places)
- ❌ Unclear which version is canonical

**Verdict**: ❌ Rejected - Technical debt accumulates, poor UX for users

---

### Option 2: Make `.claude/commands/` the Source (Invert)

**Description**: Use `.claude/commands/jpspec/` as the canonical source, copy from there to `templates/` during build.

**Pros**:
- ✅ Enhanced commands become canonical
- ✅ No change to current development workflow

**Cons**:
- ❌ dev-setup would need to copy instead of symlink (slower, more complex)
- ❌ Breaks existing pattern (templates should be canonical for distribution)
- ❌ Confusing: Why are distribution templates sourced from `.claude/`?
- ❌ Requires build-time preprocessing

**Verdict**: ❌ Rejected - Inverts expected flow, adds complexity

---

### Option 3: Single Source in `templates/` with Symlinks (SELECTED)

**Description**: Move enhanced commands to `templates/commands/jpspec/` (the canonical source). dev-setup creates symlinks from `.claude/commands/` to templates.

**Pros**:
- ✅ One canonical source (templates/)
- ✅ Enhanced commands distributed to users
- ✅ Zero sync overhead (symlinks always current)
- ✅ Consistent with existing speckit pattern
- ✅ Clear: templates/ is obviously the source
- ✅ Fast: symlinks are instant

**Cons**:
- ❌ One-time migration effort (~1-2 days)
- ❌ Breaking change to source repo structure
- ❌ Windows requires Developer Mode for symlinks

**Verdict**: ✅ **SELECTED** - Best long-term solution

---

### Option 4: Build-Time Template Preprocessing

**Description**: Use template variables and includes in templates/, preprocess during build to generate final commands.

**Pros**:
- ✅ Could support variants (minimal vs enhanced)
- ✅ DRY for shared content

**Cons**:
- ❌ Significant build complexity
- ❌ Developers can't test final output directly
- ❌ Debugging is harder (source ≠ output)
- ❌ Slower iteration cycle

**Verdict**: ❌ Rejected - Over-engineered, adds complexity

---

## Decision Outcome

**Chosen Option**: **Option 3 - Single Source in templates/ with Symlinks**

### Implementation Approach:

1. **Move enhanced jpspec commands** from `.claude/commands/jpspec/` to `templates/commands/jpspec/`
2. **Update dev-setup command** to create jpspec symlinks (currently only does speckit)
3. **Delete original `.claude/commands/jpspec/` files** - replace with symlinks created by dev-setup
4. **Keep init command unchanged** - it already copies from templates

### File Flow:

```
templates/commands/jpspec/implement.md   ◄─── CANONICAL SOURCE (20KB enhanced)
                │
                ├─► (dev-setup symlink) .claude/commands/jpspec/implement.md
                │
                └─► (init copy) user-project/.claude/commands/jpspec/implement.md
```

---

## Consequences

### Positive

- ✅ **One canonical source**: Eliminates confusion about which file to edit
- ✅ **All users get enhanced commands**: End users get same 20KB enhanced files developers use
- ✅ **Zero sync overhead**: Symlinks always reflect current template content
- ✅ **Faster feature velocity**: Update once in templates, automatically propagates
- ✅ **Reduced risk**: No manual sync means no sync errors
- ✅ **Consistent with speckit**: Already works this way for speckit commands
- ✅ **Easy to verify**: CI can check all `.claude/commands/` are symlinks

### Negative

- ❌ **Breaking change**: Requires migration for existing source repo setup
- ❌ **One-time effort**: ~1-2 days to migrate and test
- ❌ **Platform dependency**: Windows requires Developer Mode or Administrator for symlinks
- ❌ **Documentation update**: Must update CONTRIBUTING.md to reflect new canonical location

### Neutral

- ℹ️ **Learning curve**: Developers must remember templates/ is canonical
- ℹ️ **CI validation needed**: Add checks to prevent direct edits in `.claude/commands/`

---

## Mitigation Strategies

### For Breaking Change:
- Document in CONTRIBUTING.md with clear examples
- Add pre-commit hook to warn if editing symlinks
- CI check ensures `.claude/commands/` contains only symlinks
- Phased rollout: migrate templates first, then update dev-setup, then replace files

### For Windows Symlink Issue:
- Document Windows Developer Mode requirement
- Provide fallback: copy files instead of symlink on platforms without symlink support
- Test on Windows in CI

### For Documentation:
- Update CONTRIBUTING.md to emphasize templates/ as canonical
- Add troubleshooting section for symlink issues
- Include diagram showing file flow

---

## Validation Criteria

The decision will be validated by:

1. **Technical Metrics**:
   - Zero direct files in `.claude/commands/` (source repo only)
   - 100% symlink resolution rate (no broken links)
   - CI checks pass consistently

2. **User Experience Metrics**:
   - End user command files match developer command files (content hash equality)
   - Zero reported issues with command structure post-migration
   - Positive feedback on enhanced command content from users

3. **Process Metrics**:
   - Time to add new command: <1 hour (vs ~3 hours with manual sync)
   - Zero manual sync operations required
   - Release builds include enhanced commands automatically

---

## Related Documents

- Main Architecture: `docs/architecture/dev-setup-single-source-of-truth.md`
- ADR-002: Directory Structure Convention
- ADR-003: Shared Content Strategy
- Migration Plan: See main architecture doc Section 5

---

## Revision History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2025-12-03 | 1.0 | Senior IT Strategy Architect | Initial ADR |

---

## Notes

This ADR follows the principle of **"Architecture as Selling Options"** from Gregor Hohpe's work. We're not just making a decision - we're creating organizational optionality while deferring commitment to specific implementation details until we have maximum information.

The single source of truth pattern is a fundamental architectural principle that reduces cognitive load, prevents errors, and accelerates development velocity.
