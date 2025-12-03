# Dev Setup Consistency Guide

## Overview

The JP Spec Kit project uses a "dev-setuping" approach where the same commands used by consumers are used during development. This ensures what we ship is what we use, preventing content drift and quality issues.

## The Single Source of Truth Principle

### Architecture

```
templates/commands/           # SINGLE SOURCE OF TRUTH
├── speckit commands          # What gets distributed via `specify init`
│   ├── analyze.md
│   ├── checklist.md
│   ├── clarify.md
│   └── ...
└── jpspec/                   # Enhanced commands (to be added)
    ├── research.md
    ├── implement.md
    └── ...

.claude/commands/             # SYMLINKS ONLY (development use)
├── speckit/                  # Symlinks to templates/commands/*.md
│   ├── analyze.md -> ../../../templates/commands/analyze.md
│   └── ...
└── jpspec/                   # Symlinks to templates/commands/jpspec/*.md
    ├── research.md -> ../../../templates/commands/jpspec/research.md
    └── ...
```

### Key Principles

1. **No Direct Editing**: Never edit files in `.claude/commands/` directly
2. **Templates First**: All changes go to `templates/commands/`
3. **Symlinks Only**: `.claude/commands/` contains ONLY symlinks in the source repo
4. **Automated Validation**: CI/CD prevents non-symlink files from being committed

## Common Workflows

### Editing an Existing Command

```bash
# ✅ CORRECT: Edit the template
vim templates/commands/speckit/analyze.md

# Symlink automatically reflects changes (no action needed)
# Commit the template change
git add templates/commands/speckit/analyze.md
git commit -s -m "feat: enhance analyze command"
```

```bash
# ❌ WRONG: Don't edit .claude/commands directly
vim .claude/commands/speckit/analyze.md  # DON'T DO THIS
```

### Adding a New Command

```bash
# 1. Create the template
vim templates/commands/speckit/new-command.md

# 2. Run dev-setup to create symlink
specify dev-setup --force
# Or: make dev-setup-fix

# 3. Verify it works
ls -la .claude/commands/speckit/new-command.md

# 4. Commit both template and symlink
git add templates/commands/speckit/new-command.md
git add .claude/commands/speckit/new-command.md
git commit -s -m "feat: add new-command"
```

### Recovering from Mistakes

If you accidentally edited `.claude/commands/` directly:

```bash
# 1. Move changes to templates
cp .claude/commands/jpspec/implement.md templates/commands/jpspec/

# 2. Recreate symlinks
make dev-setup-fix

# 3. Verify
make dev-setup-validate
```

Or use the automated fix:

```bash
# Quick fix - recreates all symlinks
make dev-setup-fix
```

## Validation Tools

### Pre-commit Hook

Automatically runs before each commit:

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Manually run
pre-commit run --all-files
```

### Manual Validation

```bash
# Check dev-setup consistency
make dev-setup-validate

# Show current status
make dev-setup-status

# Run full test suite
make test-dev-setup
```

### CI/CD Pipeline

Every PR runs:
1. Non-symlink file detection
2. Broken symlink detection
3. Content equivalence tests
4. Structure validation

## Troubleshooting

### Error: "Found non-symlink .md files in .claude/commands/"

**Cause**: Files were edited directly instead of through templates

**Fix**:
```bash
# Option 1: Quick fix (loses local changes)
make dev-setup-fix

# Option 2: Preserve changes
# 1. Copy changed files to templates
cp .claude/commands/jpspec/implement.md templates/commands/jpspec/

# 2. Recreate symlinks
make dev-setup-fix
```

### Error: "Found broken symlinks"

**Cause**: Template files were deleted or moved

**Fix**:
```bash
# Check what's broken
make dev-setup-status

# If templates are missing, restore them or remove symlinks
rm .claude/commands/speckit/missing-file.md

# Recreate valid symlinks
make dev-setup-fix
```

### Pre-commit Hook Failing

**Cause**: Validation detected inconsistencies

**Fix**:
```bash
# See what's wrong
./scripts/bash/pre-commit-dev-setup.sh

# Fix automatically
make dev-setup-fix

# Retry commit
git commit -s -m "your message"
```

## Developer Workflows

### Daily Development

```bash
# 1. Start work
git checkout -b feature-new-command

# 2. Edit templates
vim templates/commands/speckit/my-command.md

# 3. Test locally (symlink works automatically)
specify analyze

# 4. Validate before commit
make dev-setup-validate

# 5. Commit
git add templates/commands/speckit/my-command.md
git commit -s -m "feat: add my-command"
```

### Code Review Checklist

When reviewing PRs:

- [ ] Changes are in `templates/commands/`, not `.claude/commands/`
- [ ] New commands have corresponding symlinks
- [ ] CI dev-setup-validation passes
- [ ] No broken symlinks
- [ ] Content is consistent between template and usage

## Architecture Benefits

### For Developers

- **Single edit point**: Change template, see results immediately
- **No duplication**: One file, multiple uses via symlinks
- **Automatic validation**: Can't commit mistakes
- **Fast feedback**: Pre-commit hooks catch issues early

### For Users

- **Quality assurance**: What ships is what's tested
- **No drift**: Templates match what developers use
- **Complete features**: Enhanced content reaches users
- **Consistent experience**: Same commands, same content

### For Operations

- **Automated enforcement**: CI/CD prevents drift
- **Self-healing**: Make targets fix common issues
- **Observable**: Status commands show health
- **Low maintenance**: Symlinks reduce file management

## DORA Metrics Impact

This architecture supports Elite DORA performance:

- **Deployment Frequency**: Fast, safe changes to commands
- **Lead Time**: Quick validation, immediate feedback
- **Change Failure Rate**: Pre-commit hooks prevent bad commits
- **MTTR**: `make dev-setup-fix` restores consistency in seconds

## Future Enhancements

### Planned Improvements

1. **Automatic template generation**: Scaffold new commands with boilerplate
2. **Content linting**: Validate command structure and metadata
3. **Changelog integration**: Auto-update docs when commands change
4. **Diff visualization**: Show template vs. usage differences

### Migration Tasks

Current focus:

1. Migrate jpspec commands to `templates/commands/jpspec/`
2. Update `specify dev-setup` to create jpspec symlinks
3. Add jpspec commands to `specify init` distribution
4. Validate full equivalence between dev-setup and init

## References

- [Backlog Quick Start](/docs/guides/backlog-quickstart.md)
- [CI/CD Workflow](/.github/workflows/dev-setup-validation.yml)
- [Pre-commit Hook](/scripts/bash/pre-commit-dev-setup.sh)
- [Test Suite](/tests/test_dev-setup_validation.py)

## Support

If you encounter issues not covered here:

1. Check `make dev-setup-status` for current state
2. Try `make dev-setup-fix` for automatic repair
3. Review CI logs for detailed error messages
4. Open an issue with validation output
