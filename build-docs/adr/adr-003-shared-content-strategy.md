# ADR-003: Shared Content Strategy for Commands

**Status**: Proposed

**Date**: 2025-12-03

**Deciders**: JP Flowspec Development Team

**Context and Problem Statement**:

The `_backlog-instructions.md` file contains 6KB of common task management instructions that are relevant to multiple flowspec commands (implement, research, validate, plan, specify, operate). Currently, this content exists only in `.claude/partials/flow/_backlog-instructions.md` and is NOT in templates.

**The Duplication Problem**:

If we inline this content in each command:
- 6KB × 9 commands = **54KB of duplication**
- Changes require updating 9 files
- High risk of content divergence
- Maintenance burden scales with number of commands

**The Include Problem**:

Claude Code doesn't natively support file includes or template preprocessing.

**Shared Content Example**:

```markdown
# _backlog-instructions.md (6KB)

## Critical Rules
NEVER edit task files directly. All task operations MUST use the backlog CLI.
- ✅ DO: `backlog task edit <id> --check-ac 1`
- ❌ DON'T: Edit markdown files directly

## Task Discovery
backlog search "<feature-keyword>" --plain
backlog task list -s "To Do" --plain

## Starting Work on a Task
backlog task edit <id> -s "In Progress" -a @<your-agent-name>
...
(continues for 229 lines)
```

This content is valuable for ALL flowspec agent commands, not just one.

---

## Decision Drivers

1. **DRY Principle**: Don't duplicate 6KB across 9 files (54KB waste)
2. **Maintainability**: Changes should update once, apply everywhere
3. **Consistency**: All commands should reference same instructions
4. **Tooling Constraints**: Claude Code doesn't support includes
5. **Build Simplicity**: Avoid complex preprocessing pipelines
6. **User Experience**: Commands should be self-contained or clearly reference shared content

---

## Considered Options

### Option 1: Inline in Each Command

**Description**: Copy `_backlog-instructions.md` content into every flowspec command file.

**Implementation**:
```markdown
<!-- In implement.md, research.md, validate.md, etc. -->

## Backlog Task Management (REQUIRED)

# Critical Rules
NEVER edit task files directly...
(6KB of instructions repeated)
```

**Pros**:
- ✅ Self-contained: Each command is complete standalone
- ✅ No tooling complexity: Simple copy-paste
- ✅ Works with current Claude Code (no includes needed)

**Cons**:
- ❌ **54KB duplication** (6KB × 9 files)
- ❌ Hard to maintain: Must update 9 files for any change
- ❌ High risk of divergence: Easy to update one file and forget others
- ❌ Wastes disk/network: 54KB vs 6KB
- ❌ Cognitive load: Developers must remember to update all copies

**Verdict**: ❌ Rejected - Violates DRY, unsustainable

---

### Option 2: Build-Time Template Preprocessing

**Description**: Use template variables/includes in source, preprocess during build to generate final commands.

**Implementation**:
```markdown
<!-- In implement.md.template -->
## Backlog Task Management
{{include: _backlog-instructions.md}}

<!-- Build script generates implement.md with inlined content -->
```

**Tools**: Jinja2, Liquid, custom preprocessor

**Pros**:
- ✅ DRY: Single source for shared content
- ✅ Maintainable: Update once, builds propagate
- ✅ Self-contained output: Final files have all content

**Cons**:
- ❌ **Build complexity**: Requires preprocessing pipeline
- ❌ **Source ≠ Output**: Developers can't test source directly
- ❌ **Debugging harder**: Must build to see final result
- ❌ **Tooling burden**: Must maintain preprocessor
- ❌ **Slower iteration**: Edit → build → test cycle vs direct editing
- ❌ **Infrastructure**: Need build step in CI/CD

**Verdict**: ❌ Rejected - Over-engineered for current needs

---

### Option 3: Claude Code Native Includes

**Description**: Use a hypothetical include syntax that Claude Code might support.

**Implementation**:
```markdown
<!-- In implement.md -->
## Backlog Task Management
{{#include _backlog-instructions.md}}
```

**Pros**:
- ✅ DRY: Single source
- ✅ Simple syntax
- ✅ No build step

**Cons**:
- ❌ **Not supported**: Claude Code doesn't have this feature
- ❌ **Blocked on external team**: Can't implement ourselves
- ❌ **Timeline unknown**: May never be available
- ❌ **Alternative needed**: Still need solution today

**Verdict**: ❌ Rejected - Not available, can't rely on it

---

### Option 4: Separate File with Textual References (SELECTED)

**Description**: Keep `_backlog-instructions.md` as separate file, reference it from commands with clear callout.

**Implementation**:

```markdown
<!-- templates/partials/flowspec/_backlog-instructions.md -->
# Backlog.md Task Management Instructions
(full 6KB of content)

<!-- templates/commands/flowspec/implement.md -->
## Backlog Task Management (REQUIRED)

**⚠️ IMPORTANT**: Full task management workflow documented in `_backlog-instructions.md`

Quick reference:
- Start work: `backlog task edit <id> -s "In Progress" -a @frontend-engineer`
- Check AC: `backlog task edit <id> --check-ac 1`
- Complete: `backlog task edit <id> -s Done`

See `_backlog-instructions.md` for complete workflow, examples, and best practices.
```

**File Naming Convention**:
- Underscore prefix signals "partial" or "shared" content
- Not directly invokable as command
- Clear semantic: "This is included/referenced elsewhere"

**Distribution**:
- dev-setup: Creates symlink `.claude/partials/flow/_backlog-instructions.md → templates/partials/flowspec/_backlog-instructions.md`
- Init: Copies `_backlog-instructions.md` to user project

**Pros**:
- ✅ **DRY**: Single 6KB file, not 54KB duplication
- ✅ **Maintainable**: Update once, applies everywhere
- ✅ **No preprocessing**: Works with current tooling
- ✅ **Simple**: Just reference another file
- ✅ **Discoverable**: Underscore prefix is clear convention
- ✅ **Flexible**: Can inline later if needed
- ✅ **Testable**: Can read/test files directly

**Cons**:
- ❌ **Not fully self-contained**: Commands reference external file
- ❌ **User must read both**: Two files to understand complete workflow
- ❌ **Potential confusion**: Users might miss the reference

**Mitigations**:
- Use **clear callouts** with warning emoji (⚠️)
- Include **quick reference** with most common commands
- **Repeat the reference** in multiple places (intro, task sections)
- **Bold** the reference to draw attention

**Verdict**: ✅ **SELECTED** - Pragmatic, works today, maintainable

---

## Decision Outcome

**Chosen Option**: **Option 4 - Separate File with Textual References**

### Rationale:

1. **Pragmatic**: Works with current tooling (no preprocessing)
2. **Maintainable**: Single source of truth (6KB, not 54KB)
3. **Simple**: Just a reference, no complex machinery
4. **Clear**: Underscore prefix signals "partial/shared"
5. **Flexible**: Can evolve approach later if needed

### Implementation Details:

**File Structure**:
```
templates/commands/flowspec/
├── implement.md          (references _backlog-instructions.md)
├── research.md           (references _backlog-instructions.md)
├── validate.md           (references _backlog-instructions.md)
├── plan.md               (references _backlog-instructions.md)
├── specify.md            (references _backlog-instructions.md)
├── operate.md            (references _backlog-instructions.md)
└── _backlog-instructions.md  (6KB shared content)
```

**Reference Format** (standardized across all commands):

```markdown
## Backlog Task Management (REQUIRED)

**⚠️ IMPORTANT**: Complete task management workflow in `_backlog-instructions.md`

This command requires active backlog tasks. See `_backlog-instructions.md` for:
- Task discovery and assignment
- Acceptance criteria tracking
- Implementation notes
- Definition of Done checklist

Quick commands:
- Discover: `backlog search "keyword" --plain`
- Start: `backlog task edit <id> -s "In Progress" -a @agent`
- Check AC: `backlog task edit <id> --check-ac 1`
- Complete: `backlog task edit <id> -s Done`
```

**dev-setup Behavior**:
```python
# Create symlink for partial
symlink_path = ".claude/partials/flow/_backlog-instructions.md"
target = "templates/partials/flowspec/_backlog-instructions.md"
symlink_path.symlink_to(relative_path_to(target))
```

**Init Behavior**:
```python
# Copy partial along with commands
shutil.copy2(
    "templates/partials/flowspec/_backlog-instructions.md",
    ".claude/partials/flow/_backlog-instructions.md"
)
```

---

## Consequences

### Positive

- ✅ **No duplication**: 6KB total vs 54KB
- ✅ **Single source**: One file to update for backlog workflow changes
- ✅ **No preprocessing**: Works with current tooling
- ✅ **Clear organization**: Underscore prefix signals shared content
- ✅ **Flexible**: Can inline or preprocess later if needed
- ✅ **Testable**: Can test files directly without build step
- ✅ **Fast iteration**: Edit → test cycle (no build step)

### Negative

- ❌ **Not self-contained**: Commands reference external file
- ❌ **Two files to read**: Users must open both files
- ❌ **Potential confusion**: Users might miss reference
- ❌ **Convention dependency**: Must remember underscore = partial

### Neutral

- ℹ️ **Documentation needed**: Explain underscore convention
- ℹ️ **Consistency required**: All commands must use same reference format

---

## Mitigation Strategies

### For "Not Self-Contained" Issue:

1. **Clear Callouts**: Use warning emoji (⚠️) and bold text
2. **Quick Reference**: Include most common commands inline
3. **Repeat Reference**: Mention `_backlog-instructions.md` multiple times
4. **First-Line Reference**: Start task sections with reference
5. **Relative Path**: Use simple filename (not full path)

### For "Potential Confusion" Issue:

1. **Documentation**: Explain in CONTRIBUTING.md
2. **Examples**: Show in README and guides
3. **Naming Convention**: Underscore prefix clearly signals "not a command"
4. **CI Validation**: Check all commands reference shared content
5. **Linting**: Could add linter to ensure references exist

### For "Convention Dependency" Issue:

1. **Document Convention**: `_<name>.md` = partial/shared content
2. **Consistent Across Project**: Use for all shared content
3. **CI Check**: Verify underscore files not registered as commands
4. **gitignore Pattern**: Could add rules for build outputs (if we ever preprocess)

---

## Future Enhancements

### Near Term (Next 3-6 months):
- Add more shared content files as needed (e.g., `_code-standards.md`)
- Monitor user feedback on reference pattern
- Consider adding command to view shared files: `/flow:help/backlog`

### Medium Term (6-12 months):
- If many partials emerge, evaluate build-time preprocessing
- If Claude Code adds include support, migrate to native includes
- Consider auto-generating table of contents for shared files

### Long Term (1+ years):
- Full template preprocessing pipeline if complexity justifies it
- Dynamic content assembly based on agent context
- Version-specific partials (e.g., `_backlog-v2-instructions.md`)

---

## Validation Criteria

The decision will be validated by:

1. **Technical Metrics**:
   - Total disk usage: 6KB (shared) + 17 commands < 54KB (inline)
   - Update time: 1 file edit vs 9 file edits
   - Zero content divergence between references

2. **User Experience Metrics**:
   - User feedback: "Instructions clear" vs "Couldn't find instructions"
   - Support requests: Track questions about backlog workflow
   - Time to onboard: Can users discover shared content?

3. **Maintenance Metrics**:
   - Time to update shared content: <5 minutes (single file edit)
   - Consistency: All commands reference same version (CI validated)
   - Cognitive load: Developers know where to update (single file)

---

## Related Documents

- Main Architecture: `docs/architecture/dev-setup-single-source-of-truth.md`
- ADR-001: Single Source of Truth for Commands
- ADR-002: Directory Structure Convention
- Shared Content: `templates/partials/flowspec/_backlog-instructions.md`

---

## Revision History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2025-12-03 | 1.0 | Senior IT Strategy Architect | Initial ADR |

---

## Notes

This decision exemplifies **"Deferred Decision Making"** - we chose the simplest solution that works today (textual references) while preserving the option to upgrade to preprocessing or native includes later if needed.

The underscore prefix convention for partials is inspired by:
- Ruby/Rails: `_partial.html.erb`
- Sass/SCSS: `_variables.scss`
- Hugo/Jekyll: `_index.md`

This is a well-established pattern in software development for signaling "included content" vs "standalone files."
