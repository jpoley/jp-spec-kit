# ADR-013: Command Architecture Restructuring

**Status:** Proposed
**Date:** 2025-12-04
**Author:** Enterprise Software Architect (Hohpe Principles Expert)
**Context:** Migrate /speckit commands to subdirectory (4 tasks: 272, 276, 278, 279)
**Supersedes:** None
**Amended by:** None

---

## Strategic Context (Penthouse View)

### Business Problem

JP Spec Kit command structure currently exhibits **flat namespace pollution**:
- `.claude/commands/` contains both `/jpspec` and `/speckit` commands in same directory
- Command discovery is difficult (50+ commands in one flat namespace)
- No clear separation between **workflow commands** (`/jpspec:*`) and **utility commands** (`/speckit:*`)
- Users struggle to find relevant commands for their task

**The Core Tension:** Command proliferation enhances functionality but **degrades discoverability**. A flat namespace that worked for 10 commands becomes **cognitive overload** at 50+ commands.

**Business Impact:**
- **Discovery Tax:** Users can't find commands they need (support burden)
- **Naming Conflicts:** Flat namespace limits command names (e.g., `/plan` ambiguous)
- **Mental Model Confusion:** No distinction between workflow phases and utilities
- **Onboarding Friction:** New users overwhelmed by command count

### Business Value (Strategic Investment)

**Primary Value Streams:**

1. **Improved Discoverability** - Hierarchical structure groups related commands
2. **Clear Mental Model** - Workflow vs. utility commands visually separated
3. **Namespace Expansion** - Subdirectories enable intuitive naming (e.g., `/speckit/tasks/create`)
4. **Future Extensibility** - Supports plugins and third-party command namespaces

**Success Metrics:**

| Metric | Target | Timeline |
|--------|--------|----------|
| Command discovery time | <30 seconds | 1 month |
| Support tickets for "can't find command" | -50% | 2 months |
| New user onboarding time | -20% | 3 months |

### Investment Justification

**Option Value:**
- **Plugin Foundation:** Subdirectories enable third-party command namespaces
- **Scalability:** Architecture supports 100+ commands without degradation
- **Clarity Premium:** Clear organization reduces cognitive load

**Cost:**
- **Development:** 1-2 weeks (migration script + CI validation + docs)
- **Migration Risk:** Low (backward compatibility preserved with symlinks)

**Decision:** Restructure commands into hierarchical namespace

---

## Decision

### Chosen Architecture: Hierarchical Command Namespace

Migrate from **flat namespace** to **two-tier hierarchy**:

```
BEFORE (Flat Namespace):
.claude/commands/
├── assess.md               # /jpspec:assess
├── specify.md              # /jpspec:specify
├── research.md             # /jpspec:research
├── plan.md                 # /jpspec:plan
├── implement.md            # /jpspec:implement
├── validate.md             # /jpspec:validate
├── operate.md              # /jpspec:operate
├── speckit-clarify.md      # /speckit:clarify
├── speckit-analyze.md      # /speckit:analyze
├── speckit-constitution.md # /speckit:constitution
├── speckit-tasks.md        # /speckit:tasks
└── ... (50+ commands)

AFTER (Hierarchical Namespace):
.claude/
├── commands/
│   └── jpspec/                      # Workflow phase commands
│       ├── assess.md                # /jpspec:assess
│       ├── specify.md               # /jpspec:specify
│       ├── research.md              # /jpspec:research
│       ├── plan.md                  # /jpspec:plan
│       ├── implement.md             # /jpspec:implement
│       ├── validate.md              # /jpspec:validate
│       └── operate.md               # /jpspec:operate
│
└── skills/
    └── speckit/                     # Utility commands (skills-based)
        ├── clarify.md               # /speckit:clarify
        ├── analyze.md               # /speckit:analyze
        ├── constitution.md          # /speckit:constitution
        ├── tasks.md                 # /speckit:tasks
        ├── plan.md                  # /speckit:plan
        ├── specify.md               # /speckit:specify
        └── implement.md             # /speckit:implement
```

### Key Architectural Patterns

1. **Namespace Pattern** - Commands organized by functional domain
2. **Migration Pattern** - Gradual transition with backward compatibility
3. **Convention Over Configuration** - Directory structure implies command namespace

---

## Engine Room View: Component Architecture

### New Directory Structure

**Rationale for Split:**

| Directory | Purpose | Command Prefix | Invocation Model |
|-----------|---------|----------------|------------------|
| `.claude/commands/jpspec/` | Workflow phase commands | `/jpspec:*` | User-invoked, sequential workflow |
| `.claude/skills/` | Utility skills (model-invoked) | N/A (skill invocation) | Model-invoked during workflow execution |

**Key Insight:** `/speckit` commands are actually **skills** that Claude Code can invoke during workflow execution, not top-level slash commands. This aligns with Claude Code's [skill system](https://claude.ai/docs/skills).

### Migration Strategy: Phased Approach with Backward Compatibility

**Phase 1: Create New Structure (Week 1)**
```bash
# Create new directories
mkdir -p .claude/commands/jpspec
mkdir -p .claude/skills/

# Move /jpspec commands
mv .claude/commands/assess.md .claude/commands/jpspec/
mv .claude/commands/specify.md .claude/commands/jpspec/
# ... (all workflow commands)

# Move /speckit commands to skills
mv .claude/commands/speckit-clarify.md .claude/skills/clarify.md
mv .claude/commands/speckit-analyze.md .claude/skills/analyze.md
# ... (all utility commands)
```

**Phase 2: Create Symlinks for Backward Compatibility (Week 1)**
```bash
# Symlink old paths to new paths
ln -s commands/jpspec/assess.md .claude/commands/jpspec-assess.md
ln -s skills/clarify.md .claude/commands/speckit-clarify.md
# ... (all commands)
```

**Phase 3: Update Command Invocation (Week 2)**
```bash
# Update all command files to use new paths
# Example: In implement.md, change references from:
#   /jpspec:plan
# To:
#   /jpspec:plan  # (no change needed, handled by Claude Code)
```

**Phase 4: Deprecation Notice (Week 2)**
```markdown
<!-- In legacy symlink files -->
# ⚠️ DEPRECATED: This command has moved

This command is now located at `.claude/commands/jpspec/assess.md`.

**Old path (deprecated):** `.claude/commands/assess.md`
**New path:** `.claude/commands/jpspec/assess.md`

The command will continue to work via symlink until v1.0.0 (2026-03-01).
Please update your bookmarks and documentation.
```

**Phase 5: Remove Symlinks (v1.0.0 - 3 months after migration)**
```bash
# Remove backward compatibility symlinks
rm .claude/commands/jpspec-*.md
rm .claude/commands/speckit-*.md
```

### Migration Script

**File:** `scripts/bash/migrate-commands.sh`

**Purpose:** Automated migration with dry-run support

```bash
#!/usr/bin/env bash
# migrate-commands.sh - Migrate commands to new hierarchy

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
COMMANDS_DIR="${PROJECT_ROOT}/.claude/commands"
SKILLS_DIR="${PROJECT_ROOT}/.claude/skills"

# Flags
DRY_RUN=false

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

show_help() {
    cat <<EOF
migrate-commands.sh - Migrate JP Spec Kit commands to new hierarchy

USAGE:
    ./scripts/bash/migrate-commands.sh [OPTIONS]

OPTIONS:
    --dry-run       Preview migration without making changes
    --help, -h      Show this help message

WHAT THIS DOES:
    1. Creates new directory structure (.claude/commands/jpspec, .claude/skills/)
    2. Moves /jpspec commands to .claude/commands/jpspec/
    3. Moves /speckit commands to .claude/skills/
    4. Creates symlinks for backward compatibility
    5. Updates documentation references

EXAMPLES:
    # Preview migration
    ./scripts/bash/migrate-commands.sh --dry-run

    # Execute migration
    ./scripts/bash/migrate-commands.sh
EOF
}

print_color() {
    local color="$1"
    local message="$2"
    echo -e "${color}${message}${NC}"
}

main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                print_color "${RED}" "ERROR: Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    if [[ "$DRY_RUN" == true ]]; then
        print_color "${YELLOW}" "==> DRY RUN MODE - No changes will be made"
    fi

    print_color "${BLUE}" "==> Migrating commands to new hierarchy..."

    # Step 1: Create new directories
    if [[ "$DRY_RUN" == false ]]; then
        mkdir -p "${COMMANDS_DIR}/jpspec"
        mkdir -p "${SKILLS_DIR}"
    fi
    print_color "${GREEN}" "✓ Created directory structure"

    # Step 2: Move /jpspec commands
    local jpspec_commands=("assess" "specify" "research" "plan" "implement" "validate" "operate")
    for cmd in "${jpspec_commands[@]}"; do
        local old_path="${COMMANDS_DIR}/${cmd}.md"
        local new_path="${COMMANDS_DIR}/jpspec/${cmd}.md"

        if [[ -f "$old_path" ]]; then
            if [[ "$DRY_RUN" == false ]]; then
                mv "$old_path" "$new_path"
                # Create symlink for backward compatibility
                ln -s "jpspec/${cmd}.md" "$old_path"
            fi
            print_color "${GREEN}" "  ✓ Moved /jpspec:${cmd} -> .claude/commands/jpspec/${cmd}.md"
        fi
    done

    # Step 3: Move /speckit commands to skills
    local speckit_commands=$(ls "${COMMANDS_DIR}" | grep '^speckit-' | sed 's/^speckit-//' | sed 's/\.md$//')
    for cmd in $speckit_commands; do
        local old_path="${COMMANDS_DIR}/speckit-${cmd}.md"
        local new_path="${SKILLS_DIR}/${cmd}.md"

        if [[ -f "$old_path" ]]; then
            if [[ "$DRY_RUN" == false ]]; then
                mv "$old_path" "$new_path"
                # Create symlink for backward compatibility
                ln -s "../skills/${cmd}.md" "${COMMANDS_DIR}/speckit-${cmd}.md"
            fi
            print_color "${GREEN}" "  ✓ Moved /speckit:${cmd} -> .claude/skills/${cmd}.md"
        fi
    done

    # Step 4: Update CLAUDE.md
    if [[ "$DRY_RUN" == false ]]; then
        # Add migration notice to CLAUDE.md
        cat >> "${PROJECT_ROOT}/CLAUDE.md" <<EOF

## Command Structure Migration (2025-12-04)

Commands have been reorganized into a hierarchical structure:
- \`.claude/commands/jpspec/\` - Workflow phase commands (\`/jpspec:*\`)
- \`.claude/skills/\` - Utility skills (model-invoked during workflows)

Backward compatibility symlinks will be removed in v1.0.0 (2026-03-01).
EOF
    fi
    print_color "${GREEN}" "✓ Updated CLAUDE.md"

    # Summary
    echo ""
    if [[ "$DRY_RUN" == true ]]; then
        print_color "${YELLOW}" "==> DRY RUN completed - No changes made"
    else
        print_color "${GREEN}" "==> Migration completed successfully"
    fi

    print_color "${BLUE}" "Next steps:"
    print_color "${BLUE}" "  1. Update documentation references (run: ./scripts/bash/update-docs.sh)"
    print_color "${BLUE}" "  2. Test all commands work with new paths"
    print_color "${BLUE}" "  3. Commit changes: git add .claude/ && git commit -s -m 'refactor(commands): migrate to hierarchical structure'"
}

main "$@"
```

### CI Validation

**File:** `.github/workflows/validate-command-structure.yml`

**Purpose:** Ensure command structure integrity

```yaml
name: Validate Command Structure

on:
  pull_request:
    paths:
      - '.claude/commands/**'
      - '.claude/skills/**'
  push:
    branches:
      - main

jobs:
  validate-structure:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check /jpspec commands in correct directory
        run: |
          # All /jpspec commands should be in .claude/commands/jpspec/
          jpspec_commands=$(find .claude/commands/jpspec -name "*.md" 2>/dev/null | wc -l)
          if [ "$jpspec_commands" -lt 7 ]; then
            echo "ERROR: Expected at least 7 /jpspec commands in .claude/commands/jpspec/"
            exit 1
          fi
          echo "✓ Found $jpspec_commands /jpspec commands"

      - name: Check /speckit commands migrated to skills
        run: |
          # /speckit commands should be in .claude/skills/
          speckit_commands=$(find .claude/skills -name "*.md" 2>/dev/null | wc -l)
          if [ "$speckit_commands" -lt 5 ]; then
            echo "ERROR: Expected at least 5 skills in .claude/skills/"
            exit 1
          fi
          echo "✓ Found $speckit_commands skills"

      - name: Check for flat namespace violations
        run: |
          # No top-level command files (except symlinks)
          violations=$(find .claude/commands -maxdepth 1 -name "*.md" ! -type l | wc -l)
          if [ "$violations" -gt 0 ]; then
            echo "ERROR: Found $violations command files in flat namespace"
            find .claude/commands -maxdepth 1 -name "*.md" ! -type l
            exit 1
          fi
          echo "✓ No flat namespace violations"

      - name: Check symlink validity
        run: |
          # All symlinks should point to valid files
          find .claude/commands -maxdepth 1 -type l | while read symlink; do
            if [ ! -e "$symlink" ]; then
              echo "ERROR: Broken symlink: $symlink"
              exit 1
            fi
          done
          echo "✓ All symlinks valid"
```

---

## Platform Quality Assessment (7 C's)

### 1. Clarity - 10/10

**Strengths:**
- Clear separation: workflow commands vs. skills
- Intuitive directory names (`jpspec/`, `skills/`)
- Migration path is obvious

### 2. Consistency - 10/10

**Strengths:**
- Consistent naming convention (directory matches command prefix)
- All workflow commands in one place
- Follows Claude Code skill conventions

### 3. Composability - 9/10

**Strengths:**
- Subdirectories enable namespacing
- Skills can be shared across projects
- Third-party plugins can add namespaces

**Minor Gap:**
- No formal plugin API (yet)

### 4. Consumption (Developer Experience) - 9/10

**Strengths:**
- Migration script automates transition
- Backward compatibility preserves existing workflows
- Clear deprecation timeline (3 months)

**Minor Gap:**
- Users must run migration script manually

### 5. Correctness (Validation) - 10/10

**Strengths:**
- CI validation ensures structure integrity
- Migration script has dry-run mode
- Symlink validation prevents broken links

### 6. Completeness - 8/10

**Covers:**
- Migration automation
- Backward compatibility
- CI validation
- Documentation updates

**Missing (Future):**
- Auto-migration on `specify init`
- Plugin namespace registration

### 7. Changeability - 10/10

**Strengths:**
- Phased migration allows incremental changes
- Symlinks provide escape hatch
- Clear deprecation timeline

---

## Alternatives Considered and Rejected

### Option A: Keep Flat Namespace

**Approach:** Maintain current flat structure, improve naming conventions.

**Rejected Because:**
- **Scalability:** Flat namespace doesn't scale beyond 50 commands
- **Discovery:** No grouping makes finding commands difficult
- **Mental Model:** No separation between workflow and utilities

### Option B: Multi-Level Hierarchy (3+ levels)

**Approach:** Deep hierarchy like `.claude/commands/jpspec/implementation/backend/`.

**Rejected Because:**
- **Over-Engineering:** 2 levels sufficient for current command count
- **Complexity:** Deep nesting increases cognitive load
- **YAGNI:** Can add levels later if needed

### Option C: Single Namespace with Prefixes

**Approach:** Keep flat but use longer prefixes (e.g., `jpspec-implement-backend.md`).

**Rejected Because:**
- **Verbosity:** Long filenames are cumbersome
- **No Grouping:** Still can't navigate by category
- **Tooling:** File explorers don't group by prefix

---

## Implementation Guidance

### Task Dependency Graph

```
Create Migration Script (task-272)
    ↓
Create User Migration Guide (task-276)
    ↓
Add CI Validation (task-278)
    ↓
Update All Documentation (task-279)
```

### Week-by-Week Implementation Plan

**Week 1: Migration Script**
- [ ] Implement migrate-commands.sh with dry-run
- [ ] Test migration on clean clone
- [ ] Create rollback script (restore from backup)
- [ ] Document migration process

**Week 2: CI and Documentation**
- [ ] Create validate-command-structure.yml workflow
- [ ] Update CLAUDE.md with new structure
- [ ] Update all docs/ references to commands
- [ ] Test CI validation in PR

---

## Risks and Mitigations

### Risk 1: Broken Command References

**Likelihood:** High (many docs reference old paths)
**Impact:** Medium (users can't follow docs)

**Mitigation:**
- Automated search-and-replace script
- CI check for broken command links
- Symlinks preserve functionality during transition

### Risk 2: Third-Party Tool Breakage

**Likelihood:** Low (few external tools depend on command paths)
**Impact:** Low (symlinks provide compatibility)

**Mitigation:**
- 3-month deprecation period
- Clear migration guide
- Support for users reporting issues

### Risk 3: Claude Code Breaking Changes

**Likelihood:** Low (skill system is stable)
**Impact:** High (entire command system breaks)

**Mitigation:**
- Test migration on latest Claude Code version
- Monitor Claude Code release notes
- Keep symlinks until Claude Code 1.0

---

## Success Criteria

**Objective Measures:**

1. **Command Discovery Time** - <30 seconds to find command (user testing)
2. **Migration Success Rate** - 100% of commands work post-migration
3. **CI Validation** - 0 structure violations in PRs

**Subjective Measures:**

1. **Developer Satisfaction** - "Commands are easier to find" (NPS >40)
2. **Onboarding Feedback** - "Command structure is intuitive" (>80% agree)

---

## Decision

**APPROVED for implementation as Hierarchical Command Namespace**

**Timing:** Phased rollout over 2 weeks, 3-month deprecation period

**Next Steps:**

1. Implement migration script (task-272)
2. Create user migration guide (task-276)
3. Add CI validation (task-278)
4. Update documentation (task-279)

**Review Date:** 2026-Q1 (after symlink removal)

---

## References

### Related Documents

- [Claude Code Skills Documentation](https://claude.ai/docs/skills)
- [JP Spec Kit Command Documentation](docs/reference/slash-commands.md)

### Related ADRs

- **ADR-001:** Backlog.md Integration (command-driven workflow)

---

*This ADR follows Gregor Hohpe's architectural philosophy: strategic framing (why), engine room details (how), quality assessment (verification), and alternatives considered (decision rationale).*
