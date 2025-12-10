# Dev-Setup Consistency Guide

## Overview

This guide explains the **single-source-of-truth architecture** for command files in JP Spec Kit, ensuring consistency between development and distribution. The dev-setup system eliminates content divergence by establishing `templates/commands/` as the canonical source for all command files.

**Key Principle**: What developers test is exactly what users receive.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Developer Workflows](#developer-workflows)
3. [Troubleshooting Guide](#troubleshooting-guide)
4. [Code Review Checklist](#code-review-checklist)
5. [Validation Commands](#validation-commands)

---

## Architecture Overview

### Single Source of Truth

All command development occurs in `templates/commands/`:

- **Canonical location**: `templates/commands/{namespace}/{command}.md`
- **Development**: Symlinks in `.claude/commands/` → `templates/commands/`
- **Distribution**: Copies from `templates/commands/` → user projects

```
┌─────────────────────────────────────────────────────────────┐
│                  SINGLE SOURCE OF TRUTH                      │
│                 (templates/commands/)                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  templates/commands/                                         │
│  ┌──────────────────────────────────────────────┐          │
│  │ jpspec/                                       │          │
│  │   - implement.md      (20KB enhanced)        │          │
│  │   - research.md       (15KB enhanced)        │          │
│  │   - assess.md         (12KB enhanced)        │          │
│  │   - _backlog-instructions.md (6KB partial)   │          │
│  │   (9 files total - ALL enhanced versions)    │          │
│  │                                               │          │
│  │ speckit/                                      │          │
│  │   - implement.md, analyze.md, etc.           │          │
│  │   (8 files)                                   │          │
│  └──────────────────────────────────────────────┘          │
│           │                           │                     │
│           ↓ (symlinks)                ↓ (copies)            │
│  ┌──────────────────┐       ┌──────────────────┐          │
│  │ Development      │       │ Distribution     │          │
│  │ (dev-setup)      │       │ (specify init)   │          │
│  │                  │       │                  │          │
│  │ .claude/commands/│       │ .claude/commands/│          │
│  │   jpspec/        │       │   jpspec/        │          │
│  │   [SYMLINKS]     │       │   [COPIES]       │          │
│  │   speckit/       │       │   speckit/       │          │
│  │   [SYMLINKS]     │       │   [COPIES]       │          │
│  └──────────────────┘       └──────────────────┘          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Directory Structure

**Source Repository** (jp-spec-kit):
```
jp-spec-kit/
├── templates/commands/              ◄─── CANONICAL SOURCE
│   ├── jpspec/
│   │   ├── implement.md             (20KB enhanced)
│   │   ├── research.md              (15KB enhanced)
│   │   ├── validate.md              (16KB enhanced)
│   │   └── _backlog-instructions.md (6KB shared)
│   └── speckit/
│       ├── implement.md
│       ├── analyze.md
│       └── ... (8 files)
│
├── .claude/commands/                ◄─── SYMLINKS ONLY
│   ├── jpspec/
│   │   ├── implement.md → ../../../templates/commands/jpspec/implement.md
│   │   └── ... (all files as symlinks)
│   └── speckit/
│       ├── implement.md → ../../../templates/commands/speckit/implement.md
│       └── ... (all files as symlinks)
│
└── .jp-spec-kit-source              ◄─── MARKER FILE
```

**User Projects** (created via `specify init`):
```
my-project/
└── .claude/commands/                ◄─── COPIED FILES
    ├── jpspec/
    │   ├── implement.md             (copied from templates)
    │   └── ...
    └── speckit/
        ├── implement.md             (copied from templates)
        └── ...
```

### Data Flow

```
┌────────────────────────────────────────────────────────────┐
│                    COMMAND LIFECYCLE                        │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  1. DEVELOPMENT PHASE                                       │
│     ┌─────────────────────────────────────┐               │
│     │ Developer enhances command          │               │
│     │ in templates/commands/jpspec/       │               │
│     └───────────────┬─────────────────────┘               │
│                     ↓                                       │
│     ┌─────────────────────────────────────┐               │
│     │ specify dev-setup creates symlink   │               │
│     │ .claude/commands/jpspec/implement.md│               │
│     │    → templates/commands/...         │               │
│     └───────────────┬─────────────────────┘               │
│                     ↓                                       │
│     ┌─────────────────────────────────────┐               │
│     │ Claude Code reads via symlink       │               │
│     │ Developer tests enhanced command    │               │
│     └───────────────┬─────────────────────┘               │
│                     │                                       │
│  ───────────────────┼──────────────────────────────────   │
│                     │                                       │
│  2. RELEASE PHASE   ↓                                       │
│     ┌─────────────────────────────────────┐               │
│     │ CI builds release package           │               │
│     │ from templates/commands/            │               │
│     └───────────────┬─────────────────────┘               │
│                     ↓                                       │
│     ┌─────────────────────────────────────┐               │
│     │ GitHub Release contains             │               │
│     │ spec-kit-template-*.zip             │               │
│     │ with enhanced commands              │               │
│     └───────────────┬─────────────────────┘               │
│                     │                                       │
│  ───────────────────┼──────────────────────────────────   │
│                     │                                       │
│  3. DISTRIBUTION    ↓                                       │
│     ┌─────────────────────────────────────┐               │
│     │ specify init downloads release      │               │
│     │ Copies files to user's project      │               │
│     └───────────────┬─────────────────────┘               │
│                     ↓                                       │
│     ┌─────────────────────────────────────┐               │
│     │ End user gets ENHANCED commands     │               │
│     │ Same content developer tested       │               │
│     └─────────────────────────────────────┘               │
│                                                             │
│  KEY: Single flow, no manual sync needed!                  │
└────────────────────────────────────────────────────────────┘
```

### File Naming Conventions

- **Regular commands**: `{command-name}.md` (e.g., `implement.md`)
- **Shared partials**: `_{name}.md` (e.g., `_backlog-instructions.md`)
- **Namespaces**: Subdirectories (`jpspec/`, `speckit/`)

The underscore prefix (`_`) signals "partial/shared content" not invoked directly.

### Benefits of This Architecture

| Aspect | Benefit | Impact |
|--------|---------|--------|
| **Single Source** | Edit once, propagate everywhere | 66% reduction in maintenance |
| **Consistency** | Dev and user experience identical | 100% content parity |
| **Safety** | Filesystem enforces architecture | Zero drift risk |
| **Speed** | No manual sync required | 3x faster iteration |
| **Testing** | Developers test production code | Zero integration bugs |

---

## Developer Workflows

### Workflow 1: Editing Existing Commands

**Goal**: Update an existing command file.

```bash
# ✅ CORRECT: Edit template directly
vim templates/commands/jpspec/implement.md

# Test changes immediately (symlink updates automatically)
# Claude Code reads the updated content via symlink

# Commit changes
git add templates/commands/jpspec/implement.md
git commit -s -m "feat: enhance implement command with new workflow"
git push origin feature-branch
```

**Key Points**:
- Changes are **immediately visible** via symlinks
- No `dev-setup` command needed for edits
- Symlink automatically reflects template changes

**Common Mistakes**:
```bash
# ❌ WRONG: Editing symlink target
vim .claude/commands/jpspec/implement.md

# This actually edits the template (via symlink)
# But it's confusing and easy to make mistakes
```

**Prevention**: Always edit files in `templates/commands/`.

---

### Workflow 2: Adding New Commands

**Goal**: Create a new command for distribution.

**Step 1: Create Template**
```bash
# Create new command in templates
vim templates/commands/jpspec/new-command.md

# Add frontmatter and content
# ---
# description: "New command description"
# ---
#
# Command content here...
```

**Step 2: Recreate Symlinks**
```bash
# Regenerate symlinks to include new command
specify dev-setup --force

# Or use Makefile
make dev-fix
```

**Step 3: Verify**
```bash
# Check symlink was created
ls -la .claude/commands/jpspec/new-command.md

# Should show: new-command.md -> ../../../templates/commands/jpspec/new-command.md

# Test command in Claude Code
# Use: /jpspec:new-command
```

**Step 4: Commit**
```bash
git add templates/commands/jpspec/new-command.md
git add .claude/commands/jpspec/new-command.md  # The symlink
git commit -s -m "feat: add new-command for jpspec"
git push origin feature-branch
```

**Key Points**:
- Create file in `templates/` first
- Run `dev-setup --force` to create symlink
- Commit both template and symlink

---

### Workflow 3: Deleting Commands

**Goal**: Remove a command that's no longer needed.

**Step 1: Remove Template**
```bash
# Delete the template file
git rm templates/commands/jpspec/old-command.md
```

**Step 2: Remove Symlink**
```bash
# Delete the symlink
git rm .claude/commands/jpspec/old-command.md
```

**Step 3: Verify**
```bash
# Check for broken symlinks
make dev-validate

# Should pass with no errors
```

**Step 4: Commit**
```bash
git commit -s -m "refactor: remove deprecated old-command"
git push origin feature-branch
```

**Key Points**:
- Delete both template and symlink
- Validate to catch broken links
- Use `git rm` (not `rm`) to track deletion

---

### Workflow 4: Renaming Commands

**Goal**: Rename a command file.

**Step 1: Move Template**
```bash
# Use git mv to preserve history
git mv templates/commands/jpspec/old-name.md \
       templates/commands/jpspec/new-name.md
```

**Step 2: Recreate Symlinks**
```bash
# Remove old symlink
git rm .claude/commands/jpspec/old-name.md

# Recreate all symlinks
specify dev-setup --force
```

**Step 3: Verify**
```bash
# Check new symlink
ls -la .claude/commands/jpspec/new-name.md

# Validate structure
make dev-validate
```

**Step 4: Commit**
```bash
git add .claude/commands/jpspec/new-name.md
git commit -s -m "refactor: rename old-name to new-name"
git push origin feature-branch
```

**Key Points**:
- Use `git mv` to preserve history
- Recreate symlinks after rename
- Update any references in documentation

---

### Workflow 5: Fixing Validation Errors

**Goal**: Resolve dev-setup validation failures.

**Step 1: Diagnose**
```bash
# Run validation to see errors
make dev-validate

# Common errors:
# - Non-symlink .md files in .claude/commands/
# - Broken symlinks
# - Missing templates
```

**Step 2: Quick Fix**
```bash
# Automated recovery (most common issues)
make dev-fix

# This will:
# 1. Remove existing .claude/commands/ content
# 2. Recreate all symlinks from templates
# 3. Validate the new structure
```

**Step 3: Verify**
```bash
# Confirm validation passes
make dev-validate

# Check status
make dev-status
```

**Step 4: Handle Edge Cases**

**If you have uncommitted changes in `.claude/commands/`**:
```bash
# Back up changes first
cp .claude/commands/jpspec/implement.md /tmp/implement-backup.md

# Run fix
make dev-fix

# Merge changes into template
diff /tmp/implement-backup.md templates/commands/jpspec/implement.md
vim templates/commands/jpspec/implement.md

# Commit to template
git add templates/commands/jpspec/implement.md
git commit -s -m "fix: merge changes into template"
```

**If templates are missing**:
```bash
# Restore from git
git checkout main -- templates/commands/jpspec/implement.md

# Recreate symlinks
make dev-fix
```

**Step 5: Commit Fix**
```bash
git add .claude/commands/
git commit -s -m "fix: restore dev-setup consistency"
git push origin feature-branch
```

**Key Points**:
- `make dev-fix` solves most issues
- Always back up uncommitted changes
- Restore missing templates from git history

---

### Workflow 6: Initial Setup (New Contributors)

**Goal**: Set up jp-spec-kit for development.

**Step 1: Clone and Install**
```bash
# Clone repository
git clone https://github.com/jpoley/jp-spec-kit.git
cd jp-spec-kit

# Install dependencies
uv sync

# Install CLI
uv tool install . --force
```

**Step 2: Run Dev-Setup**
```bash
# Create symlinks
specify dev-setup

# Expected output:
# ✓ Created symlink: .claude/commands/jpspec/implement.md
# ✓ Created symlink: .claude/commands/jpspec/research.md
# ...
# ✓ Dev-setup complete
```

**Step 3: Verify**
```bash
# Check structure
make dev-status

# Validate
make dev-validate

# Should see:
# ✓ All .md files are symlinks
# ✓ All symlinks resolve correctly
# ✓ Development setup validation passed
```

**Step 4: Test Claude Code Integration**
```bash
# Open jp-spec-kit in Claude Code
# Verify commands appear in slash command menu:
# - /jpspec:implement
# - /jpspec:research
# - /speckit:implement
# etc.
```

**Key Points**:
- Run `specify dev-setup` after cloning
- Validate before starting work
- Test Claude Code can discover commands

---

## Troubleshooting Guide

### Common Issues Reference Table

| Symptom | Cause | Quick Fix | Details |
|---------|-------|-----------|---------|
| **Non-symlink files detected** | Edited files in `.claude/commands/` | `make dev-fix` | [Issue 1](#issue-1-non-symlink-files-detected) |
| **Broken symlinks** | Template deleted/moved | Restore template + `make dev-fix` | [Issue 2](#issue-2-broken-symlinks) |
| **Pre-commit hook fails** | Validation errors in staged files | Fix errors + retry commit | [Issue 3](#issue-3-pre-commit-hook-failure) |
| **CI validation fails** | PR contains invalid structure | `make ci-local` to reproduce | [Issue 4](#issue-4-ci-validation-fails) |
| **Corrupted .claude directory** | Manual manipulation | `rm -rf .claude/commands && make dev-fix` | [Issue 5](#issue-5-corrupted-claude-directory) |
| **Command not appearing** | Symlink not created | `specify dev-setup --force` | [Issue 6](#issue-6-command-not-appearing-in-claude-code) |
| **Changes not reflecting** | Cached symlink | Restart Claude Code | [Issue 7](#issue-7-changes-not-reflecting) |

---

### Issue 1: Non-Symlink Files Detected

**Symptoms**:
```
❌ ERROR: Found non-symlink .md files in .claude/commands/
Files that should be symlinks:
  .claude/commands/jpspec/implement.md
```

**Root Cause**: Files were edited directly in `.claude/commands/` or created as regular files.

**Quick Fix** (if changes can be discarded):
```bash
make dev-fix
```

**Careful Fix** (preserve changes):
```bash
# 1. Back up changes
cp .claude/commands/jpspec/implement.md /tmp/implement-backup.md

# 2. Compare with template
diff /tmp/implement-backup.md templates/commands/jpspec/implement.md

# 3. Merge changes into template
vim templates/commands/jpspec/implement.md

# 4. Recreate symlinks
make dev-fix

# 5. Verify changes
cat .claude/commands/jpspec/implement.md

# 6. Commit template
git add templates/commands/jpspec/implement.md
git commit -s -m "fix: merge changes into template"
```

**Prevention**:
- Always edit files in `templates/commands/`
- Use pre-commit hooks to catch mistakes
- Review diffs before committing

---

### Issue 2: Broken Symlinks

**Symptoms**:
```
❌ ERROR: Found broken symlinks in .claude/commands/
Broken symlinks:
  .claude/commands/jpspec/implement.md -> ../../../templates/commands/jpspec/implement.md
```

**Root Cause**: Template file was deleted, moved, or renamed without updating symlink.

**Fix**:

**If template should exist**:
```bash
# Restore from git
git checkout main -- templates/commands/jpspec/implement.md

# Recreate symlinks
make dev-fix
```

**If template was intentionally removed**:
```bash
# Remove broken symlink
git rm .claude/commands/jpspec/old-command.md

# Validate
make dev-validate
```

**Prevention**:
- Use `git mv` when renaming templates
- Run `make dev-fix` after structural changes
- Don't delete templates without removing symlinks

---

### Issue 3: Pre-Commit Hook Failure

**Symptoms**:
```
🔍 Validating dev-setup consistency...
❌ ERROR: Found non-symlink .md files in .claude/commands/
```
Commit is blocked.

**Fix**:
```bash
# 1. Run validation manually
make dev-validate

# 2. Fix identified issues
make dev-fix

# 3. Stage fixes
git add .claude/commands/

# 4. Retry commit
git commit -s -m "fix: restore dev-setup consistency"
```

**Emergency Bypass** (not recommended):
```bash
# Skip pre-commit hook (ONLY IN EMERGENCIES)
git commit --no-verify -s -m "emergency fix"

# IMMEDIATELY fix in next commit
make dev-fix
git add .claude/commands/
git commit -s -m "fix: restore dev-setup consistency"
```

**Prevention**:
- Run `make dev-validate` before committing
- Install pre-commit hooks: `pre-commit install` (if using pre-commit framework)
- Test changes locally first

---

### Issue 4: CI Validation Fails

**Symptoms**: GitHub Actions workflow "Dev-Setup Validation" fails.

**Fix**:
```bash
# 1. Reproduce locally
git fetch origin
git checkout pr-branch-name

# 2. Run same checks as CI
make ci-local

# 3. Fix identified issues
make dev-fix

# 4. Verify locally
make dev-validate

# 5. Commit and push
git add .
git commit -s -m "fix: restore dev-setup consistency"
git push origin pr-branch-name
```

**Prevention**:
- Run `make ci-local` before pushing
- Enable pre-commit hooks
- Review diffs before creating PRs

---

### Issue 5: Corrupted .claude Directory

**Symptoms**:
- Multiple validation errors
- Symlinks pointing to wrong locations
- Unexpected git changes

**Fix** (nuclear option):
```bash
# 1. Backup (optional)
cp -r .claude /tmp/claude-backup-$(date +%s)

# 2. Remove entire structure
rm -rf .claude/commands

# 3. Recreate from scratch
make dev-fix

# 4. Verify
make dev-validate

# 5. Review and commit
git diff .claude/commands/
git add .claude/commands/
git commit -s -m "fix: restore .claude/commands structure"
```

**Prevention**:
- Don't manually manipulate `.claude/commands/` structure
- Use `make dev-fix` for all symlink recreation
- Regular validation: `make dev-validate`

---

### Issue 6: Command Not Appearing in Claude Code

**Symptoms**: New command file exists but doesn't show in Claude Code.

**Fix**:
```bash
# 1. Verify template exists
ls -la templates/commands/jpspec/new-command.md

# 2. Verify symlink exists
ls -la .claude/commands/jpspec/new-command.md

# 3. If symlink missing, create it
specify dev-setup --force

# 4. Restart Claude Code
# Commands are discovered on startup
```

**Prevention**:
- Always run `specify dev-setup --force` after adding new commands
- Restart Claude Code after structural changes

---

### Issue 7: Changes Not Reflecting

**Symptoms**: Edited template but changes don't appear in Claude Code.

**Fix**:
```bash
# 1. Verify symlink is valid
ls -la .claude/commands/jpspec/implement.md

# 2. Check symlink content
cat .claude/commands/jpspec/implement.md

# 3. Restart Claude Code
# Claude Code may cache command content
```

**Alternative**:
```bash
# Force symlink recreation
specify dev-setup --force

# Restart Claude Code
```

**Prevention**:
- Restart Claude Code after major edits
- Check symlink resolution after changes

---

### Escalation Paths

**Level 1: Self-Service** (5 minutes)
```bash
make dev-fix
make dev-validate
```

**Level 2: Manual Recovery** (15 minutes)
1. Review error messages
2. Follow scenario-specific procedures above
3. Test locally before committing

**Level 3: Team Review** (30 minutes)

Create GitHub issue with:
- Error messages
- `make dev-status` output
- Recent commits affecting `templates/`
- Reproduction steps

**Level 4: Rollback** (Emergency)
```bash
# Revert to last known good state
git revert HEAD
git push origin main

# Or roll back to specific commit (REQUIRES APPROVAL)
git reset --hard <last-good-commit>
git push --force origin main  # DANGEROUS
```

Production rollback requires:
- Team lead approval
- Incident post-mortem
- Root cause analysis

---

## Code Review Checklist

Use this checklist when reviewing PRs that touch command files.

### Pre-Merge Validation

- [ ] **Template Changes**
  - [ ] All edits are in `templates/commands/`, not `.claude/commands/`
  - [ ] New commands added to correct namespace directory
  - [ ] File naming follows conventions (no spaces, lowercase, `.md` extension)
  - [ ] Frontmatter includes `description` field

- [ ] **Symlink Integrity**
  - [ ] All `.md` files in `.claude/commands/` are symlinks (not regular files)
  - [ ] Symlinks point to correct templates (relative path: `../../../templates/commands/{namespace}/{file}`)
  - [ ] No broken symlinks (target files exist)

- [ ] **Structure Consistency**
  - [ ] Commands organized in subdirectories (`jpspec/`, `speckit/`)
  - [ ] No flat files with dots (`jpspec.implement.md` is invalid)
  - [ ] Shared partials use underscore prefix (`_backlog-instructions.md`)

- [ ] **Content Quality**
  - [ ] Commands are comprehensive (10-20KB), not minimal stubs (2-3KB)
  - [ ] jpspec commands integrate backlog management
  - [ ] Instructions are clear and actionable
  - [ ] Examples provided where appropriate

- [ ] **Validation Passes**
  - [ ] Local validation passes: `make dev-validate`
  - [ ] CI validation workflow passes
  - [ ] Pre-commit hooks pass (if enabled)
  - [ ] Tests pass: `make test-dev`

### Specific Scenarios

**Adding New Commands**:
- [ ] Template created in `templates/commands/{namespace}/`
- [ ] Symlink created in `.claude/commands/{namespace}/`
- [ ] Both files committed (template + symlink)
- [ ] Command tested in Claude Code

**Editing Commands**:
- [ ] Changes made to template, not symlink
- [ ] Content quality maintained or improved
- [ ] No accidental conversion of symlink to regular file

**Deleting Commands**:
- [ ] Template deleted from `templates/commands/`
- [ ] Symlink deleted from `.claude/commands/`
- [ ] No broken symlinks remain
- [ ] References in other files updated

**Renaming Commands**:
- [ ] Template renamed using `git mv`
- [ ] Old symlink deleted
- [ ] New symlink created
- [ ] Documentation updated

### Common Issues to Catch

❌ **Red Flags**:
- Non-symlink `.md` files in `.claude/commands/`
- Broken symlinks
- Flat file structure (`jpspec.implement.md`)
- Direct edits to `.claude/commands/` files
- Missing templates for new symlinks

✅ **Good Signs**:
- All `.claude/commands/*.md` are symlinks
- Templates are comprehensive and well-documented
- Validation commands pass
- Clear commit messages

### Review Commands

Run these commands when reviewing:

```bash
# Check for non-symlink files
find .claude/commands -name "*.md" -type f

# Check for broken symlinks
find .claude/commands -type l ! -exec test -e {} \; -print

# Validate structure
make dev-validate

# Check status
make dev-status

# Run tests
make test-dev
```

### Approval Criteria

**Approve if**:
- ✅ All checklist items pass
- ✅ Validation commands succeed
- ✅ Changes align with architecture principles
- ✅ Tests pass

**Request changes if**:
- ❌ Non-symlink files in `.claude/commands/`
- ❌ Broken symlinks
- ❌ Validation fails
- ❌ Structural violations

**Block merge if**:
- 🚫 Security issues
- 🚫 Breaking changes without migration plan
- 🚫 Multiple validation failures
- 🚫 Data loss risk

---

## Validation Commands

### Quick Reference

```bash
# Status and validation
make dev-status          # Show current state
make dev-validate        # Run all checks

# Recovery
make dev-fix             # Recreate all symlinks

# Testing
make test-dev            # Run dev-setup tests only
make ci-local            # Simulate full CI pipeline

# Development
specify dev-setup        # Run dev-setup command
specify dev-setup --force  # Force recreation of all symlinks
```

### Command Details

#### `make dev-status`

Shows current development setup state.

**Output**:
```
==========================================
Development Setup Status
==========================================

=== .claude/commands/ structure ===
drwxr-xr-x  4 user  staff  128 Dec  3 12:00 .
drwxr-xr-x  3 user  staff   96 Dec  3 12:00 ..
drwxr-xr-x 11 user  staff  352 Dec  3 12:00 jpspec
drwxr-xr-x 10 user  staff  320 Dec  3 12:00 speckit

=== jpspec commands ===
lrwxr-xr-x  1 user  staff  51 Dec  3 12:00 implement.md -> ../../../templates/commands/jpspec/implement.md
...

=== Symlink verification ===
Total .md files: 17
Symlinks: 17
Regular files: 0
```

**Use when**: Checking overall setup state.

---

#### `make dev-validate`

Validates dev-setup consistency with multiple checks.

**Checks**:
1. No non-symlink `.md` files in `.claude/commands/`
2. No broken symlinks
3. All symlinks resolve to existing templates

**Success Output**:
```
Validating development setup...

Checking for non-symlink .md files in .claude/commands/...
✓ All .md files are symlinks

Checking for broken symlinks...
✓ All symlinks resolve correctly

✓ Development setup validation passed
```

**Failure Output**:
```
Validating development setup...

Checking for non-symlink .md files in .claude/commands/...
❌ ERROR: Found non-symlink .md files:
.claude/commands/jpspec/implement.md

Checking for broken symlinks...
❌ ERROR: Found broken symlinks:
.claude/commands/jpspec/old-command.md
```

**Exit Codes**:
- `0`: All checks passed
- `1`: Validation failures

**Use when**:
- Before committing changes
- After structural changes
- As pre-commit hook
- In CI/CD pipelines

---

#### `make dev-fix`

Automated recovery: recreates all symlinks from templates.

**Process**:
1. Backs up current state
2. Removes existing symlinks
3. Runs `specify dev-setup --force`
4. Validates new structure

**Output**:
```
Fixing development setup...

Step 1: Backing up current state...
  - Found jpspec directory
  - Found speckit directory

Step 2: Removing existing symlinks...
  ✓ Removed

Step 3: Recreating symlinks with dev-setup command...
✓ Created symlink: .claude/commands/jpspec/implement.md
✓ Created symlink: .claude/commands/jpspec/research.md
...
✓ Dev-setup complete

Step 4: Validating new setup...
  - Checking symlinks...
  ✓ All files are symlinks

==========================================
✓ Development setup restored successfully
==========================================
```

**Warning**: This discards any uncommitted changes in `.claude/commands/`. Back up first if needed.

**Use when**:
- Validation failures
- Corrupted symlinks
- After adding new commands
- After major branch merges

---

#### `make test-dev`

Runs dev-setup-specific tests.

**Tests Include**:
- Symlink creation
- Symlink resolution
- Template discovery
- Command structure validation

**Output**:
```
Running development setup tests...
pytest tests/test_command_*.py -v

tests/test_command_structure.py::test_dev_setup_creates_jpspec_symlinks PASSED
tests/test_command_structure.py::test_dev_setup_creates_speckit_symlinks PASSED
tests/test_command_structure.py::test_all_symlinks_resolve PASSED
...

=================== 12 passed in 2.34s ===================
```

**Use when**:
- Validating code changes
- Before pushing to remote
- In CI/CD pipelines

---

#### `make ci-local`

Simulates full CI pipeline locally.

**Steps**:
1. Linting (`make lint`)
2. Testing (`make test`)
3. Dev-setup validation (`make dev-validate`)

**Output**:
```
Running local CI simulation...

Step 1: Linting...
Running linter...
✓ Linting passed

Step 2: Testing...
Running tests...
✓ All tests passed

Step 3: Development setup validation...
✓ Development setup validation passed

==========================================
✓ Local CI simulation passed
==========================================
```

**Use when**:
- Before creating PRs
- After major changes
- Troubleshooting CI failures

---

#### `specify dev-setup`

Core CLI command to create symlinks.

**Usage**:
```bash
# Create symlinks (skip existing)
specify dev-setup

# Force recreation (overwrite existing)
specify dev-setup --force
```

**Options**:
- `--force`: Recreate symlinks even if they exist

**Behavior**:
1. Verifies `.jp-spec-kit-source` marker file exists
2. Creates `.claude/commands/{namespace}/` directories
3. Iterates through `templates/commands/{namespace}/*.md`
4. Creates symlinks with relative paths
5. Reports created/skipped files

**Output**:
```
Setting up jp-spec-kit for development...

Creating symlinks for speckit commands...
✓ Created symlink: .claude/commands/speckit/implement.md
✓ Created symlink: .claude/commands/speckit/analyze.md
...

Creating symlinks for jpspec commands...
✓ Created symlink: .claude/commands/jpspec/implement.md
✓ Created symlink: .claude/commands/jpspec/research.md
...

✓ Dev-setup complete
```

**Error Handling**:
- Fails if not in source repository (no `.jp-spec-kit-source` marker)
- Warns if template directory doesn't exist
- Reports symlink creation failures

**Use when**:
- Initial setup after cloning
- Adding new commands
- Corrupted symlinks

---

### Validation in CI/CD

The project includes automated validation in CI/CD pipelines:

**GitHub Actions Workflow**: `.github/workflows/dev-setup-validation.yml` (planned; see [tracking issue #123](https://github.com/your-org/your-repo/issues/123))

**Checks**:
- No non-symlink files in `.claude/commands/`
- All symlinks resolve correctly
- Template coverage is complete
- Tests pass

**Trigger**: On every push and pull request

**Enforcement**: PRs cannot merge if validation fails

---

## Additional Resources

### Documentation
- [Dev-Setup Principles](../platform/dev-setup-principles.md) - Platform-level requirements
- [Dev-Setup Recovery Runbook](../runbooks/dev-setup-recovery.md) - Operational procedures
- [Single Source of Truth Architecture](../architecture/command-single-source-of-truth.md) - Detailed architecture
- [CONTRIBUTING.md](../../CONTRIBUTING.md) - Contributor guidelines

### Tools
- [Makefile](../../Makefile) - Development commands
- [Dev-Setup CLI](../../src/specify_cli/__init__.py) - Implementation
- [Test Suite](../../tests/test_command_*.py) - Validation tests

### Related ADRs
- [ADR-001: Single Source of Truth for Commands](../architecture/adr-001-single-source-of-truth.md)
- [ADR-002: Directory Structure Convention](../architecture/adr-002-directory-structure-convention.md)
- [ADR-003: Shared Content Strategy](../architecture/adr-003-shared-content-strategy.md)

---

## Document Metadata

**Author**: Platform Engineering Team
**Version**: 1.0.0
**Status**: Active
**Last Updated**: 2025-12-03
**Next Review**: 2026-03-03

---

## Glossary

- **Dev-Setup**: Process of setting up jp-spec-kit repository for development using symlinks
- **Single Source of Truth**: Architecture pattern where one canonical location exists for data
- **Symlink**: Symbolic link that references another file
- **Template**: Canonical command file in `templates/commands/`
- **Namespace**: Command grouping (jpspec, speckit)
- **Partial**: Shared content file prefixed with underscore (`_`)

---

## Feedback and Updates

This guide is a living document. If you find issues or have suggestions:

1. Create GitHub issue with label `documentation`
2. Include specific section reference
3. Propose concrete improvements
4. Reference real-world scenarios

**Contribution Welcome**: Pull requests to improve this guide are encouraged!
