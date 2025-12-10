docs: recover dev-setup architecture (all review issues fixed)

## Executive Summary

The `specify dev-setup` command has significant gaps compared to what `specify init` installs into target projects. This document provides a comprehensive analysis of the differences between:

1. **jp-spec-kit source repo** (dev-setup installation at `./jp-spec-kit`)
2. **nanofuse project** (normal `specify init` installation at `./nanofuse`)

**Critical Finding**: The dev-setup command only sets up `speckit` symlinks but completely ignores `specflow` commands and many other components that are installed during `specify init`.

---

## Chain of Thought Analysis

### Step 1: Understanding the dev-setup Command Implementation

**Location**: `jp-spec-kit/src/specify_cli/__init__.py:2499-2630`

**What it does:**
1. Checks for `.jp-spec-kit-source` marker file
2. Creates `.claude/commands/speckit/` directory
3. Creates symlinks from `speckit/*.md` → `templates/commands/*.md`
4. Verifies symlinks work

**What it does NOT do:**
- Does NOT create symlinks for `specflow` commands
- Does NOT set up `.specify/` directory structure
- Does NOT install memory files
- Does NOT install scripts
- Does NOT handle naming convention differences (subdirs vs flat files)

### Step 2: Comparing Command File Structures

#### Nanofuse Installation (via `specify init`)
```
.claude/commands/
├── specflow.implement.md      (2933 bytes)
├── specflow.operate.md        (2796 bytes)
├── specflow.plan.md           (2266 bytes)
├── specflow.research.md       (1491 bytes)
├── specflow.specify.md        (1534 bytes)
├── specflow.validate.md       (3017 bytes)
├── speckit.analyze.md       (7135 bytes)
├── speckit.checklist.md     (16843 bytes)
├── speckit.clarify.md       (11202 bytes)
├── speckit.constitution.md  (5075 bytes)
├── speckit.implement.md     (7150 bytes)
├── speckit.plan.md          (2886 bytes)
├── speckit.specify.md       (11533 bytes)
├── speckit.tasks.md         (6713 bytes)
└── speckit.taskstoissues.md (1067 bytes)   ← MISSING FROM JP-SPEC-KIT
```

- **15 command files total**
- **Flat file structure** with dot notation (e.g., `specflow.implement.md`)
- All files are actual files, not symlinks

#### JP-Spec-Kit dev-setup Installation
```
.claude/commands/
├── specflow/                          ← Subdirectory structure
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

- **17 command files** (8 speckit symlinks + 9 specflow real files)
- **Subdirectory structure** (not flat with dot notation)
- speckit files are symlinks; specflow files are NOT symlinks
- specflow files are **heavily customized** with backlog integration

### Step 3: The Three Versions Problem

There are **THREE different versions** of specflow commands:

| Location | Files | Content |
|----------|-------|---------|
| `nanofuse/.claude/commands/specflow.*.md` | 6 files | From release package, small/simple |
| `jp-spec-kit/templates/commands/specflow/` | 6 files | Templates for release, small/simple |
| `jp-spec-kit/.claude/commands/specflow/` | 9 files | Enhanced for development, 3-7x larger |

**MD5 Hash Comparison (implement.md):**
```
nanofuse:        d693b495cd6ac36126506b09b335f4b1  (2933 bytes)
templates:       94f6876d82379e85ce89ab1772f3c92a  (2945 bytes)
.claude actual:  c20b339affedc24243167e0f0f552da4  (19960 bytes)
```

All three are different! The version jp-spec-kit uses for development (`.claude/commands/specflow/`) is NOT what gets distributed.

### Step 4: Missing Files from dev-setup Setup

#### Missing Command: `speckit.taskstoissues.md`
- Present in nanofuse but not in jp-spec-kit templates
- Creates GitHub issues from tasks.md
- **Not part of dev-setup setup**

#### Missing specflow Commands (in templates only, not dev-setup):
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
│   ├── specflow_workflow.schema.json
│   ├── specflow_workflow.yml
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

**JP-spec-kit has:**
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
- specflow_workflow.schema.json
- specflow_workflow.yml
- mcp-configuration.md
- README.md
- WORKFLOW_DESIGN_SPEC.md

**JP-spec-kit `memory/` (2 files):**
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

**JP-spec-kit `.claude/`:**
```
.claude/
├── agents/
│   └── project-manager-backlog.md
├── agents-config.json
├── AGENTS-INTEGRATION.md
├── commands/       (subdirectory structure)
│   ├── specflow/    (9 files, NOT symlinks)
│   └── speckit/   (8 symlinks)
├── INTEGRATION-COMPLETE.md
├── load-agent.py
└── settings.json
```

**Key differences:**
- Different CLAUDE.md content
- Different command structure (flat vs subdirs)
- jp-spec-kit has extra agent files

---

## Issues Found

### Issue 1: dev-setup Command is Incomplete (CRITICAL)

**Problem**: The `specify dev-setup` command only creates symlinks for `speckit` commands, completely ignoring `specflow` commands.

**Evidence**:
```python
# From __init__.py:2546-2547
speckit_commands_dir = project_path / ".claude" / "commands" / "speckit"
speckit_commands_dir.mkdir(parents=True, exist_ok=True)
```

**Impact**: The specflow commands in `.claude/commands/specflow/` are manually maintained separately and have diverged significantly from the templates.

### Issue 2: specflow Content Divergence (CRITICAL)

**Problem**: The specflow commands used for jp-spec-kit development are 3-7x larger than the template versions, with extensive backlog integration that is NOT distributed to end users.

**File Size Comparison:**
| File | Templates | .claude | Ratio |
|------|-----------|---------|-------|
| implement.md | 2945 bytes | 19960 bytes | 6.8x |
| operate.md | 2808 bytes | 12048 bytes | 4.3x |
| plan.md | 3778 bytes | 15087 bytes | 4.0x |
| research.md | 3202 bytes | 15025 bytes | 4.7x |
| validate.md | 3029 bytes | 15945 bytes | 5.3x |

**Impact**: End users get a vastly inferior experience compared to what jp-spec-kit developers use.

### Issue 3: Missing specflow Commands in Templates

**Problem**: Three specflow commands exist in `.claude/commands/specflow/` but NOT in templates:
- `assess.md`
- `_backlog-instructions.md`
- `prune-branch.md`

**Impact**: These features are not available to end users.

### Issue 4: Missing speckit Command in Templates

**Problem**: `speckit.taskstoissues.md` exists in nanofuse installation but NOT in jp-spec-kit templates.

**Impact**: The "tasks to GitHub issues" feature is not available to end users.

### Issue 5: Naming Convention Mismatch

**Problem**: dev-setup creates `speckit/implement.md` but `specify init` creates `speckit.implement.md`.

**Evidence**:
- nanofuse: `.claude/commands/speckit.implement.md` (dot notation)
- jp-spec-kit: `.claude/commands/speckit/implement.md` (subdirectory)

**Impact**: Different command invocation syntax depending on installation method.

### Issue 6: Missing Memory Files

**Problem**: jp-spec-kit `memory/` has only 2 files vs 9 files installed by `specify init`.

**Missing files:**
- claude-hooks.md
- code-standards.md
- critical-rules.md
- specflow_workflow.schema.json
- specflow_workflow.yml
- mcp-configuration.md
- README.md

**Impact**: Reduced AI context and guidance for dev-setup users.

---

## Root Cause Analysis

The fundamental problem is that jp-spec-kit has **two parallel command systems**:

1. **Templates** (`templates/commands/`) - Simple, minimal versions for distribution
2. **Actual** (`.claude/commands/`) - Enhanced versions with backlog integration

The dev-setup command was designed to only link the `speckit` commands, assuming specflow was "already available" (per CONTRIBUTING.md). However, the specflow commands in `.claude/commands/specflow/` have evolved independently and are now completely different from the templates.

This creates a **dual-source-of-truth problem** where:
- Developers working on jp-spec-kit get the enhanced commands
- End users installing via `specify init` get the minimal template versions

---

## Recommendations

### Fix 1: Sync specflow Commands

Either:
- **Option A**: Copy enhanced `.claude/commands/specflow/` files to `templates/commands/specflow/`
- **Option B**: Make `.claude/commands/specflow/` use symlinks to templates (like speckit)

Recommendation: **Option A** - The enhanced versions are clearly better.

### Fix 2: Update dev-setup Command

Add specflow symlink creation:
```python
# Create specflow symlinks as well
specflow_commands_dir = project_path / ".claude" / "commands" / "specflow"
specflow_commands_dir.mkdir(parents=True, exist_ok=True)

specflow_templates_dir = project_path / "templates" / "commands" / "specflow"
for template_file in specflow_templates_dir.glob("*.md"):
    symlink_path = specflow_commands_dir / template_file.name
    relative_target = Path("..") / ".." / ".." / "templates" / "commands" / "specflow" / template_file.name
    # ... symlink creation
```

### Fix 3: Add Missing Commands to Templates

- Add `assess.md` to `templates/commands/specflow/`
- Add `_backlog-instructions.md` to `templates/commands/specflow/`
- Add `prune-branch.md` to `templates/commands/specflow/`
- Add `taskstoissues.md` to `templates/commands/`

### Fix 4: Standardize Naming Convention

Decide whether to use:
- Subdirectory structure: `specflow/implement.md`
- Dot notation: `specflow.implement.md`

Update both dev-setup and init commands to use the same convention.

### Fix 5: Sync Memory Files

Update jp-spec-kit `memory/` directory to include all files that get installed via `specify init`:
- claude-hooks.md
- code-standards.md
- critical-rules.md
- specflow_workflow.schema.json
- specflow_workflow.yml
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
| `jp-spec-kit/src/specify_cli/__init__.py` | Main CLI code including dev-setup command |
| `jp-spec-kit/CONTRIBUTING.md` | Documentation about dev-setuping |
| `jp-spec-kit/.jp-spec-kit-source` | Marker file for source repo |
| `jp-spec-kit/.claude/commands/` | Active command files |
| `jp-spec-kit/templates/commands/` | Templates for distribution |
| `jp-spec-kit/memory/` | Memory/context files |
| `nanofuse/.claude/commands/` | Installed commands (for comparison) |
| `nanofuse/.specify/` | Installed specify directory structure |

---

## Conclusion

The dev-setup setup is fundamentally incomplete. It was designed as a quick workaround to enable speckit commands via symlinks, but it:

1. Completely ignores specflow commands
2. Has allowed specflow commands to diverge significantly between development and distribution
3. Creates a different command structure than what end users get
4. Missing several files and commands that are installed via `specify init`

This needs to be fixed to ensure jp-spec-kit developers have the same experience as end users, and that improvements made during development are properly propagated to the release templates.
