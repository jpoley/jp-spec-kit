# ADR-002: Directory Structure Convention for Commands

**Status**: Proposed

**Date**: 2025-12-03

**Deciders**: JP Flowspec Development Team

**Context and Problem Statement**:

We have two different naming conventions in use:

1. **Subdirectory structure**: `.claude/commands/flow/implement.md` (current dev-setup output)
2. **Flat structure with dots**: `.claude/commands/flow.implement.md` (current init output)

Both work with Claude Code, but they create inconsistent experiences:

```
# Subdirectory structure (dev-setup)
.claude/commands/
├── flowspec/
│   ├── implement.md
│   ├── research.md
│   └── _backlog-instructions.md   ← Can have partials
└── speckit/
    ├── implement.md
    └── analyze.md

# Flat structure (init)
.claude/commands/
├── flowspec.implement.md
├── flowspec.research.md              ← No way to include partials
├── speckit.implement.md
└── speckit.analyze.md
```

**Problems with Current State**:
- Users get different structures depending on how they installed
- Flat structure doesn't support shared partials (e.g., `_backlog-instructions.md`)
- As command library grows, flat structure becomes cluttered
- Different invocation patterns may confuse users

---

## Decision Drivers

1. **Consistency**: Same structure whether installed via dev-setup or init
2. **Scalability**: Structure should handle growing command library
3. **Maintainability**: Support shared content (partials) without duplication
4. **User Experience**: Clear organization makes commands discoverable
5. **Breaking Changes**: Minimize disruption to existing users

---

## Considered Options

### Option 1: Subdirectory Structure

**Structure**:
```
.claude/commands/
├── flowspec/
│   ├── implement.md
│   ├── research.md
│   ├── validate.md
│   ├── plan.md
│   ├── specify.md
│   ├── operate.md
│   ├── assess.md
│   ├── prune-branch.md
│   └── _backlog-instructions.md    ← Shared partial
└── speckit/
    ├── implement.md
    ├── analyze.md
    ├── checklist.md
    ├── clarify.md
    ├── constitution.md
    ├── plan.md
    ├── specify.md
    └── tasks.md
```

**Invocation**:
```
/flow:implement
/flow:research
/speckit:implement
```

**Pros**:
- ✅ Cleaner organization with many commands (17 total)
- ✅ Natural grouping by namespace
- ✅ Supports shared partials with underscore prefix
- ✅ Scales well as library grows
- ✅ Easier to navigate and understand
- ✅ Matches typical file organization patterns
- ✅ Already used by dev-setup (less change for source repo)

**Cons**:
- ❌ Breaking change for existing init users
- ❌ Requires migration for projects using flat structure
- ❌ One more directory level

**Verdict**: ✅ **SELECTED** - Best long-term structure

---

### Option 2: Flat Structure with Dots

**Structure**:
```
.claude/commands/
├── flowspec.implement.md
├── flowspec.research.md
├── flowspec.validate.md
├── flowspec.plan.md
├── flowspec.specify.md
├── flowspec.operate.md
├── flowspec.assess.md
├── flowspec.prune-branch.md
├── speckit.implement.md
├── speckit.analyze.md
├── speckit.checklist.md
├── speckit.clarify.md
├── speckit.constitution.md
├── speckit.plan.md
├── speckit.specify.md
└── speckit.tasks.md
```

**Invocation**:
```
/flowspec.implement
/flowspec.research
/speckit.implement
```

**Pros**:
- ✅ Matches current init behavior (no breaking change)
- ✅ Simpler file listing (one level)
- ✅ Familiar to existing users

**Cons**:
- ❌ Cannot use underscore-prefixed partials (`_backlog-instructions.md` would be visible as command)
- ❌ Cluttered with 17+ files in one directory
- ❌ Harder to organize related commands
- ❌ Poor scalability as library grows
- ❌ Requires duplication of shared content (6KB × 9 files = 54KB)

**Verdict**: ❌ Rejected - Doesn't scale, no partials

---

### Option 3: Support Both (Dual Mode)

**Description**: dev-setup uses subdirectories, init uses flat structure, both work.

**Pros**:
- ✅ No breaking changes
- ✅ Backward compatible

**Cons**:
- ❌ Complexity: Two code paths to maintain
- ❌ Confusing: Different structures in different contexts
- ❌ Hard to document ("it depends how you installed")
- ❌ Testing burden: Must test both modes
- ❌ Doesn't solve partial problem for init users

**Verdict**: ❌ Rejected - Unnecessary complexity

---

### Option 4: Flat with Namespaces as Subdirs (Hybrid)

**Description**: Keep commands flat within each namespace subdirectory.

**Structure**:
```
.claude/commands/
├── flowspec/
│   └── (flat files, no further nesting)
└── speckit/
    └── (flat files, no further nesting)
```

**Pros**:
- ✅ Some organization benefit
- ✅ Supports partials per namespace

**Cons**:
- ❌ Same as Option 1 (subdirectory) but with no additional benefit
- ❌ Still a breaking change
- ❌ Doesn't simplify anything

**Verdict**: ❌ Rejected - Same as Option 1 without advantages

---

## Decision Outcome

**Chosen Option**: **Option 1 - Subdirectory Structure**

### Rationale:

1. **Scalability**: With 17 commands today and growing, subdirectories provide better organization
2. **Shared Content**: Partials like `_backlog-instructions.md` eliminate 54KB of duplication
3. **Clarity**: Related commands grouped together (`flowspec/`, `speckit/`)
4. **Maintainability**: Easier to navigate for developers and users
5. **Future-Proof**: Structure scales to 50+ commands without cluttering

### Implementation:

```
templates/commands/
├── flowspec/
│   ├── implement.md
│   ├── research.md
│   ├── validate.md
│   ├── plan.md
│   ├── specify.md
│   ├── operate.md
│   ├── assess.md
│   ├── prune-branch.md
│   └── _backlog-instructions.md
└── speckit/
    ├── implement.md
    ├── analyze.md
    ├── checklist.md
    ├── clarify.md
    ├── constitution.md
    ├── plan.md
    ├── specify.md
    └── tasks.md
```

**Command Invocation**: Unchanged (`/flow:implement`, `/speckit:implement`)

---

## Consequences

### Positive

- ✅ **Cleaner organization**: Related commands grouped naturally
- ✅ **Supports partials**: Shared content in `_backlog-instructions.md` (6KB single file vs 54KB duplicated)
- ✅ **Scales well**: Can grow to 50+ commands without cluttering
- ✅ **Discoverable**: Users can browse by namespace
- ✅ **Consistent**: Same structure for dev-setup and init
- ✅ **Professional**: Matches industry-standard project organization

### Negative

- ❌ **Breaking change**: Existing init users must migrate
- ❌ **Migration required**: Projects using flat structure need conversion
- ❌ **Documentation update**: Must update all examples and guides
- ❌ **One-time effort**: ~1 day to implement and test

### Neutral

- ℹ️ **Command invocation unchanged**: `/flow:implement` works for both structures
- ℹ️ **Minor learning curve**: Users must remember subdirectory structure

---

## Migration Strategy

### For End Users (Existing Projects):

**Migration Script**: `scripts/bash/migrate-commands-to-subdirs.sh`

```bash
#!/bin/bash
# Migrate flat command structure to subdirectory structure

COMMANDS_DIR=".claude/commands"

echo "Migrating command structure to subdirectories..."

# Migrate flowspec commands
for file in "$COMMANDS_DIR"/flowspec.*.md; do
    [ -e "$file" ] || continue
    name="${file##*/flowspec.}"
    mkdir -p "$COMMANDS_DIR/flowspec"
    mv "$file" "$COMMANDS_DIR/flowspec/$name"
    echo "  Moved: flowspec.$name → flowspec/$name"
done

# Migrate speckit commands
for file in "$COMMANDS_DIR"/speckit.*.md; do
    [ -e "$file" ] || continue
    name="${file##*/speckit.}"
    mkdir -p "$COMMANDS_DIR/speckit"
    mv "$file" "$COMMANDS_DIR/speckit/$name"
    echo "  Moved: speckit.$name → speckit/$name"
done

echo "Migration complete! Commands now in subdirectories."
echo "Command invocation unchanged: /flow:implement still works."
```

**Usage**:
```bash
cd your-project
bash scripts/bash/migrate-commands-to-subdirs.sh
```

### For flowspec Source Repo:

1. Move flat template files to subdirectories
2. Update dev-setup to create subdirectory symlinks
3. Update init to copy subdirectory structure
4. Run dev-setup to recreate symlinks

### Communication:

- **CHANGELOG**: Document as breaking change (v0.0.x → v0.1.0)
- **Upgrade Guide**: Step-by-step migration instructions
- **README**: Update command examples
- **Release Notes**: Highlight migration script availability

---

## Validation Criteria

1. **Technical**:
   - dev-setup creates subdirectory structure
   - Init creates subdirectory structure
   - Both produce identical layouts
   - Partials (`_backlog-instructions.md`) copied/symlinked correctly

2. **User Experience**:
   - Command invocation works: `/flow:implement`
   - Commands discoverable via file browser
   - Partial file accessible and readable

3. **Process**:
   - Migration script successfully converts existing projects
   - CI validates structure correctness
   - No reported issues after 2 weeks

---

## Related Documents

- Main Architecture: `docs/architecture/dev-setup-single-source-of-truth.md`
- ADR-001: Single Source of Truth for Commands
- ADR-003: Shared Content Strategy
- Migration Script: `scripts/bash/migrate-commands-to-subdirs.sh`

---

## Revision History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2025-12-03 | 1.0 | Senior IT Strategy Architect | Initial ADR |

---

## Notes

This decision aligns with the principle of **"Deferred Decision Making"** from Hohpe's option theory. We delayed choosing a structure until we had clear evidence (17 commands, need for partials) that subdirectories provide superior organization.

The breaking change is justified by long-term maintainability gains and current user base size (limited impact window).
