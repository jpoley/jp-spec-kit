docs: recover dev-setup architecture (all review issues fixed)

## Executive Summary

The `specify dev-setup` command has significant gaps compared to what `specify init` installs into target projects. This document provides a comprehensive analysis of the differences between:

1. **flowspec source repo** (dev-setup installation at `./flowspec`)
2. **nanofuse project** (normal `specify init` installation at `./nanofuse`)

**Critical Finding**: The dev-setup command only sets up `speckit` symlinks but completely ignores `flowspec` commands and many other components that are installed during `specify init`.

---

## Chain of Thought Analysis

### Step 1: Understanding the dev-setup Command Implementation

**Location**: `flowspec/src/specify_cli/__init__.py:2499-2630`

**What it does:**
1. Checks for `.flowspec-source` marker file
2. Creates `.claude/commands/speckit/` directory
3. Creates symlinks from `speckit/*.md` → `templates/commands/*.md`
4. Verifies symlinks work

**What it does NOT do:**
- Does NOT create symlinks for `flowspec` commands
- Does NOT set up `.specify/` directory structure
- Does NOT install memory files
- Does NOT install scripts
- Does NOT handle naming convention differences (subdirs vs flat files)

### Step 2: Comparing Command File Structures

#### Nanofuse Installation (via `specify init`)
```
.claude/commands/
├── flowspec.implement.md      (2933 bytes)
├── flowspec.operate.md        (2796 bytes)
├── flowspec.plan.md           (2266 bytes)
├── flowspec.research.md       (1491 bytes)
├── flowspec.specify.md        (1534 bytes)
├── flowspec.validate.md       (3017 bytes)
├── speckit.analyze.md       (7135 bytes)
├── speckit.checklist.md     (16843 bytes)
├── speckit.clarify.md       (11202 bytes)
├── speckit.constitution.md  (5075 bytes)
├── speckit.implement.md     (7150 bytes)
├── speckit.plan.md          (2886 bytes)
├── speckit.specify.md       (11533 bytes)
├── speckit.tasks.md         (6713 bytes)
└── speckit.taskstoissues.md (1067 bytes)   ← MISSING FROM flowspec
```

- **15 command files total**
- **Flat file structure** with dot notation (e.g., `flowspec.implement.md`)
- All files are actual files, not symlinks

#### flowspec dev-setup Installation
```
.claude/commands/
├── flowspec/                          ← Subdirectory structure
│   ├── _backlog-instructions.md    (6444 bytes)  ← NOT IN TEMPLATES
│   ├── assess.md                   (11671 bytes) ← NOT IN TEMPLATES
│   ├── implement.md                (19960 bytes) ← 7x larger than template!
│   ├── operate.md                  (12048 bytes) ← 4x larger than template!
│   ├── plan.md                     (15087 bytes) ← 4x larger than template!
│   ├── prune-branch.md             (4084 bytes)  ← NOT IN TEMPLATES
│   ├── research.md                 (15025 bytes) ← 5x larger than template!
│   ├── specify.md                  (9637 bytes)  ← 3x larger than template!
│   └── validate.md                 (15945 bytes) ← 5x larger than template!
└── speckit/                         ← Symlinks created by dev-setup
    ├── analyze.md → ../../../templates/commands/analyze.md
    ├── checklist.md → ...
    ├── clarify.md → ...
    ├── constitution.md → ...
    ├── implement.md → ...
    ├── plan.md → ...
    ├── specify.md → ...
    └── tasks.md → ...
```

- **17 command files** (8 speckit symlinks + 9 flowspec real files)
- **Subdirectory structure** (not flat with dot notation)
- speckit files are symlinks; flowspec files are NOT symlinks
- flowspec files are **heavily customized** with backlog integration

### Step 3: The Three Versions Problem

There are **THREE different versions** of flowspec commands:

| Location | Files | Content |
|----------|-------|---------|
| `nanofuse/.claude/commands/flow.*.md` | 6 files | From release package, small/simple |
| `flowspec/templates/commands/flowspec/` | 6 files | Templates for release, small/simple |
| `flowspec/.claude/commands/flow/` | 9 files | Enhanced for development, 3-7x larger |

**MD5 Hash Comparison (implement.md):**
```
nanofuse:        d693b495cd6ac36126506b09b335f4b1  (2933 bytes)
templates:       94f6876d82379e85ce89ab1772f3c92a  (2945 bytes)
.claude actual:  c20b339affedc24243167e0f0f552da4  (19960 bytes)
```

All three are different! The version flowspec uses for development (`.claude/commands/flow/`) is NOT what gets distributed.

### Step 4: Missing Files from dev-setup Setup

#### Missing Command: `speckit.taskstoissues.md`
- Present in nanofuse but not in flowspec templates
- Creates GitHub issues from tasks.md
- **Not part of dev-setup setup**

#### Missing flowspec Commands (in templates only, not dev-setup):
- `assess.md` - exists in .claude but NOT in templates
- `_backlog-instructions.md` - exists in .claude but NOT in templates
- `prune-branch.md` - exists in .claude but NOT in templates

### Step 5: Missing Directory Structure

#### `.specify/` Directory
**Nanofuse has:**
```
.specify/
├── memory/
│   ├── claude-hooks.md
│   ├── code-standards.md
│   ├── constitution.md
│   ├── critical-rules.md
│   ├── flowspec_workflow.schema.json
│   ├── flowspec_workflow.yml
│   ├── mcp-configuration.md
│   ├── README.md
│   └── WORKFLOW_DESIGN_SPEC.md
├── scripts/
│   ├── bash/
│   │   ├── check-mcp-servers.sh
│   │   ├── check-prerequisites.sh
│   │   ├── common.sh
│   │   ├── create-new-feature.sh
│   │   ├── flush-backlog.sh
│   │   ├── install-act.sh
│   │   ├── install-pre-commit-hook.sh
│   │   ├── install-specify-latest.sh
│   │   ├── pre-commit-hook.sh
│   │   ├── run-local-ci.sh
│   │   ├── setup-plan.sh
│   │   ├── test-mcp-health-check.sh
│   │   ├── update-agent-context.sh
│   │   └── verify-backlog-integration.sh
│   ├── CLAUDE.md
│   ├── README.md
│   ├── check-mcp-servers.sh
│   └── validate-workflow-config.py
└── templates/
    ├── *.md (templates)
    ├── constitutions/
    ├── docs/
    ├── github-actions/
    └── partials/
```

**flowspec has:**
- NO `.specify/` directory (expected for source repo)
- `memory/` at root level with only 2 files (vs 9 in nanofuse)
- `scripts/` at root level with different structure
- `templates/` at root level

### Step 6: Memory Directory Differences

**Nanofuse `.specify/memory/` (9 files):**
- claude-hooks.md
- code-standards.md
- constitution.md
- critical-rules.md
- flowspec_workflow.schema.json
- flowspec_workflow.yml
- mcp-configuration.md
- README.md
- WORKFLOW_DESIGN_SPEC.md

**flowspec `memory/` (2 files):**
- constitution.md
- WORKFLOW_DESIGN_SPEC.md

**Missing:** 7 files that provide critical context for AI assistants

### Step 7: Claude Integration Files Differences

**Nanofuse `.claude/`:**
```
.claude/
├── CLAUDE.md        (13070 bytes)
├── commands/        (15 files, flat structure)
└── constitution.md  (1812 bytes)
```

**flowspec `.claude/`:**
```
.claude/
├── agents/
│   └── project-manager-backlog.md
├── agents-config.json
├── AGENTS-INTEGRATION.md
├── commands/       (subdirectory structure)
│   ├── flowspec/    (9 files, NOT symlinks)
│   └── speckit/   (8 symlinks)
├── INTEGRATION-COMPLETE.md
├── load-agent.py
└── settings.json
```

**Key differences:**
- Different CLAUDE.md content
- Different command structure (flat vs subdirs)
- flowspec has extra agent files

---

## Issues Found

### Issue 1: dev-setup Command is Incomplete (CRITICAL)

**Problem**: The `specify dev-setup` command only creates symlinks for `speckit` commands, completely ignoring `flowspec` commands.

**Evidence**:
```python
# From __init__.py:2546-2547
speckit_commands_dir = project_path / ".claude" / "commands" / "speckit"
speckit_commands_dir.mkdir(parents=True, exist_ok=True)
```

**Impact**: The flowspec commands in `.claude/commands/flow/` are manually maintained separately and have diverged significantly from the templates.

### Issue 2: flowspec Content Divergence (CRITICAL)

**Problem**: The flowspec commands used for flowspec development are 3-7x larger than the template versions, with extensive backlog integration that is NOT distributed to end users.

**File Size Comparison:**
| File | Templates | .claude | Ratio |
|------|-----------|---------|-------|
| implement.md | 2945 bytes | 19960 bytes | 6.8x |
| operate.md | 2808 bytes | 12048 bytes | 4.3x |
| plan.md | 3778 bytes | 15087 bytes | 4.0x |
| research.md | 3202 bytes | 15025 bytes | 4.7x |
| validate.md | 3029 bytes | 15945 bytes | 5.3x |

**Impact**: End users get a vastly inferior experience compared to what flowspec developers use.

### Issue 3: Missing flowspec Commands in Templates

**Problem**: Three flowspec commands exist in `.claude/commands/flow/` but NOT in templates:
- `assess.md`
- `_backlog-instructions.md`
- `prune-branch.md`

**Impact**: These features are not available to end users.

### Issue 4: Missing speckit Command in Templates

**Problem**: `speckit.taskstoissues.md` exists in nanofuse installation but NOT in flowspec templates.

**Impact**: The "tasks to GitHub issues" feature is not available to end users.

### Issue 5: Naming Convention Mismatch

**Problem**: dev-setup creates `speckit/implement.md` but `specify init` creates `speckit.implement.md`.

**Evidence**:
- nanofuse: `.claude/commands/speckit.implement.md` (dot notation)
- flowspec: `.claude/commands/speckit/implement.md` (subdirectory)

**Impact**: Different command invocation syntax depending on installation method.

### Issue 6: Missing Memory Files

**Problem**: flowspec `memory/` has only 2 files vs 9 files installed by `specify init`.

**Missing files:**
- claude-hooks.md
- code-standards.md
- critical-rules.md
- flowspec_workflow.schema.json
- flowspec_workflow.yml
- mcp-configuration.md
- README.md

**Impact**: Reduced AI context and guidance for dev-setup users.

---

## Root Cause Analysis

The fundamental problem is that flowspec has **two parallel command systems**:

1. **Templates** (`templates/commands/`) - Simple, minimal versions for distribution
2. **Actual** (`.claude/commands/`) - Enhanced versions with backlog integration

The dev-setup command was designed to only link the `speckit` commands, assuming flowspec was "already available" (per CONTRIBUTING.md). However, the flowspec commands in `.claude/commands/flow/` have evolved independently and are now completely different from the templates.

This creates a **dual-source-of-truth problem** where:
- Developers working on flowspec get the enhanced commands
- End users installing via `specify init` get the minimal template versions

---

## Recommendations

### Fix 1: Sync flowspec Commands

Either:
- **Option A**: Copy enhanced `.claude/commands/flow/` files to `templates/commands/flowspec/`
- **Option B**: Make `.claude/commands/flow/` use symlinks to templates (like speckit)

Recommendation: **Option A** - The enhanced versions are clearly better.

### Fix 2: Update dev-setup Command

Add flowspec symlink creation:
```python
# Create flowspec symlinks as well
flowspec_commands_dir = project_path / ".claude" / "commands" / "flowspec"
flowspec_commands_dir.mkdir(parents=True, exist_ok=True)

flowspec_templates_dir = project_path / "templates" / "commands" / "flowspec"
for template_file in flowspec_templates_dir.glob("*.md"):
    symlink_path = flowspec_commands_dir / template_file.name
    relative_target = Path("..") / ".." / ".." / "templates" / "commands" / "flowspec" / template_file.name
    # ... symlink creation
```

### Fix 3: Add Missing Commands to Templates

- Add `assess.md` to `templates/commands/flowspec/`
- Add `_backlog-instructions.md` to `templates/commands/flowspec/`
- Add `prune-branch.md` to `templates/commands/flowspec/`
- Add `taskstoissues.md` to `templates/commands/`

### Fix 4: Standardize Naming Convention

Decide whether to use:
- Subdirectory structure: `flowspec/implement.md`
- Dot notation: `flowspec.implement.md`

Update both dev-setup and init commands to use the same convention.

### Fix 5: Sync Memory Files

Update flowspec `memory/` directory to include all files that get installed via `specify init`:
- claude-hooks.md
- code-standards.md
- critical-rules.md
- flowspec_workflow.schema.json
- flowspec_workflow.yml
- mcp-configuration.md
- README.md

---

## Verification Steps Performed

1. Listed directory structures of both repos
2. Compared file counts and sizes
3. Verified symlink targets
4. Compared file contents with diff and MD5 hashes
5. Read dev-setup command source code
6. Read CONTRIBUTING.md documentation
7. Read init and upgrade command source code
8. Cross-referenced all findings

**All findings have been double-checked against actual file system state.**

---

## Files Referenced

| File | Purpose |
|------|---------|
| `flowspec/src/specify_cli/__init__.py` | Main CLI code including dev-setup command |
| `flowspec/CONTRIBUTING.md` | Documentation about dev-setuping |
| `flowspec/.flowspec-source` | Marker file for source repo |
| `flowspec/.claude/commands/` | Active command files |
| `flowspec/templates/commands/` | Templates for distribution |
| `flowspec/memory/` | Memory/context files |
| `nanofuse/.claude/commands/` | Installed commands (for comparison) |
| `nanofuse/.specify/` | Installed specify directory structure |

---

## Conclusion

The dev-setup setup is fundamentally incomplete. It was designed as a quick workaround to enable speckit commands via symlinks, but it:

1. Completely ignores flowspec commands
2. Has allowed flowspec commands to diverge significantly between development and distribution
3. Creates a different command structure than what end users get
4. Missing several files and commands that are installed via `specify init`

This needs to be fixed to ensure flowspec developers have the same experience as end users, and that improvements made during development are properly propagated to the release templates.
