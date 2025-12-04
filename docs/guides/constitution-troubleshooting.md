# Constitution Troubleshooting Guide

This guide provides solutions for common issues when working with constitutions in JP Spec Kit.

## Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Language Detection Issues](#language-detection-issues)
- [Validation Issues](#validation-issues)
- [Workflow Command Issues](#workflow-command-issues)
- [Version Issues](#version-issues)
- [File Issues](#file-issues)
- [Getting Help](#getting-help)

## Quick Diagnostics

Before troubleshooting specific errors, run these diagnostic commands:

```bash
# 1. Check if constitution exists
ls -la memory/constitution.md

# 2. Check validation status
specify constitution validate

# 3. Check constitution version
specify constitution version

# 4. Check for NEEDS_VALIDATION markers
grep -n "NEEDS_VALIDATION" memory/constitution.md

# 5. Verify file permissions
ls -la memory/constitution.md
```

## Language Detection Issues

### Issue: Incorrect Language Detection

**Symptoms**:
- Wrong programming language listed in TECH_STACK section
- Missing framework that's clearly used in project
- Tool listed that isn't actually used
- Languages from test files incorrectly included

**Example**:
```markdown
## Technology Stack
<!-- NEEDS_VALIDATION: Detected languages/frameworks -->
- **JavaScript**: Node.js  # Wrong - project is Python
- **Ruby**: Rails          # Wrong - no Ruby code
```

**Causes**:
1. LLM scanning missed key files or misidentified patterns
2. Non-standard project structure (e.g., source in `lib/` not `src/`)
3. Files in `.gitignore` were not scanned
4. Test files or documentation examples misidentified as production code
5. Vendored dependencies detected as project languages

**Resolution**:

**Step 1: Manual review and correction**
```bash
# 1. Edit constitution directly
vim memory/constitution.md

# 2. Navigate to TECH_STACK section (search for "Technology Stack")

# 3. Remove incorrect entries
# 4. Add correct entries
# 5. Verify section matches actual project

# Example correction:
# Before:
# - **JavaScript**: Node.js
# - **Ruby**: Rails

# After:
# - **Python 3.11+**: FastAPI, SQLAlchemy, Pydantic
# - **TypeScript 5**: React, Next.js 15
```

**Step 2: Remove validation marker**
```bash
# After updating content, remove the NEEDS_VALIDATION marker
# Delete this line:
<!-- NEEDS_VALIDATION: Detected languages/frameworks -->
```

**Step 3: Verify correction**
```bash
specify constitution validate
# Should no longer show language detection warning
```

**Step 4: Consider re-running detection (optional)**
```bash
# If many sections are wrong, consider regenerating
# WARNING: This will overwrite custom changes
/speckit:constitution
```

**Prevention Tips**:
- Always review auto-detected languages before removing NEEDS_VALIDATION marker
- Keep project structure standard (`src/`, `tests/`, etc.)
- Ensure primary language files are not in `.gitignore`
- Document any unusual project structure in constitution notes

---

## Validation Issues

### Issue: Stuck NEEDS_VALIDATION Markers

**Symptoms**:
- `specify constitution validate` always shows unvalidated sections
- Marker won't go away even after review
- Validation seems broken
- Re-running validate shows same marker repeatedly

**Example output**:
```
Constitution Validation Status
========================================

⚠ 2 section(s) need validation:

✗ Technology Stack
  Line 74: Populate with detected languages/frameworks

✗ Version and dates
  Line 95: Version and dates
```

**Causes**:
1. Marker comment not completely removed
2. Marker syntax slightly wrong (typo in comment)
3. Hidden Unicode characters in marker
4. Content added but marker line still present

**Resolution**:

**Step 1: Verify marker syntax**
```bash
# Check exact marker text
grep -n "NEEDS_VALIDATION" memory/constitution.md

# Should show:
# 74:<!-- NEEDS_VALIDATION: Description text -->
```

**Step 2: Delete entire marker line**
```bash
# Open in editor
vim memory/constitution.md

# Navigate to line with marker (e.g., line 74)
# Delete the ENTIRE line including <!-- and -->
# Example:
# DELETE THIS ENTIRE LINE:
<!-- NEEDS_VALIDATION: Populate with detected languages/frameworks -->
```

**Step 3: Check for hidden characters**
```bash
# If marker persists, check for hidden Unicode
cat -A memory/constitution.md | grep -n "NEEDS_VALIDATION"

# Look for unusual characters like ^M (carriage return) or special spaces
```

**Step 4: Re-run validation**
```bash
specify constitution validate

# Should now show fewer unvalidated sections
```

**Step 5: If still present, manual cleanup**
```bash
# Use sed to remove all markers (emergency only)
sed -i.backup '/NEEDS_VALIDATION/d' memory/constitution.md

# Verify backup created
ls -la memory/constitution.md.backup

# Verify markers removed
grep "NEEDS_VALIDATION" memory/constitution.md
# Should return no results
```

**Common Mistake - Not Deleting Marker**:
```markdown
# ❌ WRONG - Added content but didn't remove marker
## Technology Stack
<!-- NEEDS_VALIDATION: Populate with detected languages/frameworks -->
- **Python 3.11+**: FastAPI, SQLAlchemy
# Marker still present! Will fail validation.

# ✅ CORRECT - Added content AND removed marker
## Technology Stack
- **Python 3.11+**: FastAPI, SQLAlchemy
# Marker completely removed. Will pass validation.
```

---

### Issue: Cannot Remove NEEDS_VALIDATION (Genuinely Unknown)

**Symptoms**:
- Section content is genuinely unknown or TBD
- Cannot populate placeholder yet
- Early project phase - technologies not selected

**Example**:
```markdown
## Technology Stack
<!-- NEEDS_VALIDATION: Populate with detected languages/frameworks -->
[LANGUAGES_AND_FRAMEWORKS]
# We genuinely don't know yet - project just starting
```

**Causes**:
1. Very early project phase (no code yet)
2. Technology decisions pending
3. Constitution created before implementation starts

**Resolution**:

**Option 1: Add placeholder content (RECOMMENDED)**
```markdown
## Technology Stack

**Status**: Technology selection in progress

**Candidates under evaluation**:
- Backend: Python (FastAPI) vs. Go (Chi)
- Frontend: React vs. Vue
- Database: PostgreSQL vs. MySQL

**Decision date**: Target 2025-12-15

<!-- Remove NEEDS_VALIDATION marker after adding placeholder -->
```

**Option 2: Document as TBD**
```markdown
## Technology Stack

**TBD**: Technologies will be selected during planning phase (task-123)

**Constraints**:
- Must support Linux
- Must have strong community support
- Must integrate with existing infrastructure

**Update trigger**: Remove this placeholder after completing task-123

<!-- Remove NEEDS_VALIDATION marker -->
```

**Option 3: Use lighter constitution tier**
```bash
# If many sections are TBD, consider using light tier
# Light tier has fewer required sections

# Check current tier
grep "Constitution Tier:" memory/constitution.md

# If heavy, consider downgrade to medium or light
# This requires manual edit or regeneration
```

**Important**: Never leave NEEDS_VALIDATION markers indefinitely. Always replace with placeholder content explaining why the section is incomplete.

---

## Workflow Command Issues

### Issue: /jpspec Command Blocked by Unvalidated Constitution

**Symptoms**:
- Heavy tier constitution blocking `/jpspec` commands
- "Must validate constitution" error
- Can't proceed with workflow
- Warning: "Constitution has unvalidated sections"

**Example error**:
```
⚠ Constitution has unvalidated sections. Run 'specify constitution validate' to review.

ERROR: Heavy tier constitution requires full validation before executing workflow commands.

Run: specify constitution validate
```

**Causes**:
1. Heavy tier constitution enforces validation (by design)
2. One or more sections still have NEEDS_VALIDATION markers
3. Constitution not fully reviewed
4. First time running `/jpspec` command with new constitution

**Resolution**:

**Solution 1: Complete validation (RECOMMENDED)**
```bash
# Step 1: Check what needs validation
specify constitution validate

# Output shows unvalidated sections
# ✗ Technology Stack
#   Line 74: Populate with detected languages/frameworks

# Step 2: Fix each section
vim memory/constitution.md
# Update content for each marked section
# Remove NEEDS_VALIDATION markers

# Step 3: Verify
specify constitution validate
# ✓ Constitution fully validated!

# Step 4: Retry workflow command
/jpspec:implement
# Should now work
```

**Solution 2: Use --skip-validation flag (EMERGENCY ONLY)**
```bash
# WARNING: Only use if you understand the implications
# This bypasses validation checking

/jpspec:implement --skip-validation

# Note: This flag may not exist in all commands
# Check command help: /jpspec:implement --help
```

**Solution 3: Downgrade to medium tier**
```bash
# If heavy tier is too restrictive, downgrade to medium
# Medium tier shows warnings but doesn't block

# Edit constitution manually
vim memory/constitution.md

# Change tier line:
# Before:
# **Constitution Tier**: Heavy

# After:
# **Constitution Tier**: Medium

# Save and retry
/jpspec:implement
# Will show warning but won't block
```

**Solution 4: Temporarily disable enforcement (DEV ONLY)**
```bash
# For local development, temporarily disable enforcement
export SPECIFY_SKIP_CONSTITUTION_VALIDATION=1

# Run workflow command
/jpspec:implement

# Unset after use
unset SPECIFY_SKIP_CONSTITUTION_VALIDATION

# WARNING: Do NOT use this in CI/CD or production
```

**When Heavy Tier is Appropriate**:
- Production-grade projects (e.g., SLSA Level 3 compliance)
- Regulated industries (finance, healthcare)
- Open source projects with strict governance
- Projects with constitutional compliance requirements

**When Medium/Light Tier is Better**:
- Rapid prototyping
- Personal projects
- Early-stage startups
- Exploratory research projects

---

## Version Issues

### Issue: Constitution Version Mismatch After Upgrade

**Symptoms**:
- Constitution version doesn't match latest JP Spec Kit version
- Upgrade didn't update constitution
- New features missing after upgrade
- Constitution shows old version number

**Example**:
```bash
specify constitution version
# Constitution version: 1.0.0
# Latest available: 1.2.0
# Status: Outdated
```

**Causes**:
1. User declined constitution upgrade during `specify upgrade`
2. Manual edits conflicted with automatic upgrade
3. Constitution backup needed restoration
4. Upgrade process failed or was interrupted

**Resolution**:

**Step 1: Check current status**
```bash
# Check constitution version
specify constitution version

# Output example:
# Constitution version: 1.0.0
# Latest available: 1.2.0
# Status: Outdated
#
# Run 'specify upgrade' to update
```

**Step 2: Backup current constitution**
```bash
# Always backup before upgrading
cp memory/constitution.md memory/constitution.md.backup.$(date +%Y%m%d_%H%M%S)

# Verify backup
ls -la memory/constitution.md.backup.*
```

**Step 3: Run upgrade**
```bash
# Run upgrade command
specify upgrade

# When prompted:
# "Update constitution to v1.2.0? [Y/n]"
# Answer: Y

# Review changes if shown
# Accept if appropriate for your project
```

**Step 4: Verify upgrade**
```bash
specify constitution version
# Should now show:
# Constitution version: 1.2.0
# Latest available: 1.2.0
# Status: Up to date
```

**Step 5: Review changes**
```bash
# Compare with backup to see what changed
diff memory/constitution.md.backup.* memory/constitution.md

# Review significant changes
# Ensure custom amendments still present
```

**If Custom Amendments Were Lost**:
```bash
# Step 1: View backup
cat memory/constitution.md.backup.20251204_153000

# Step 2: Identify custom sections
# Look for:
# - Custom quality standards
# - Project-specific tool requirements
# - Team-specific practices

# Step 3: Manually merge custom sections
vim memory/constitution.md
# Add back custom sections that were lost

# Step 4: Re-validate
specify constitution validate
```

**Prevention Tips**:
- Always backup before upgrading
- Document custom amendments in a separate section labeled "Custom Amendments"
- Consider using Git to track constitution changes
- Review release notes before upgrading

---

### Issue: Constitution Upgrade Conflicts

**Symptoms**:
- Upgrade shows merge conflicts
- Custom changes lost after upgrade
- Constitution format broken after upgrade

**Resolution**:

**Step 1: Restore from backup**
```bash
# If upgrade went wrong, restore backup
cp memory/constitution.md.backup.latest memory/constitution.md
```

**Step 2: Manual upgrade with merge**
```bash
# 1. Export current constitution to temp file
cp memory/constitution.md memory/constitution.custom.md

# 2. Get new template
specify upgrade --constitution-only --force

# 3. Manually merge custom sections
# Use three-way merge tool
git merge-file \
  memory/constitution.md \
  memory/constitution.md.backup.* \
  memory/constitution.custom.md

# Or use visual merge tool
code --diff memory/constitution.md memory/constitution.custom.md
```

**Step 3: Verify merged result**
```bash
specify constitution validate
# Fix any validation issues
```

---

## File Issues

### Issue: Constitution File Missing

**Symptoms**:
- "Constitution file not found" error
- Commands fail with "No constitution at memory/constitution.md"
- New project without constitution

**Resolution**:

**Step 1: Check if file exists**
```bash
ls -la memory/constitution.md
# If not found: ls: cannot access 'memory/constitution.md': No such file or directory
```

**Step 2: Create constitution**
```bash
# Option 1: Initialize in existing project
specify init --here

# When prompted, select tier:
# 1. Light - Minimal governance
# 2. Medium - Balanced governance (RECOMMENDED)
# 3. Heavy - Strict governance
# Enter choice: 2

# Constitution will be created at memory/constitution.md
```

**Step 3: Verify creation**
```bash
ls -la memory/constitution.md
# Should now exist

specify constitution validate
# Check validation status
```

**Step 4: Customize if needed**
```bash
# Run constitution generator for customization
/speckit:constitution

# Or manually edit
vim memory/constitution.md
```

---

### Issue: Permission Denied When Validating

**Symptoms**:
- "Permission denied" error when running validate
- Cannot read constitution file
- Validation command fails with EACCES

**Resolution**:

**Step 1: Check file permissions**
```bash
ls -la memory/constitution.md

# Should show read permission for user:
# -rw-r--r-- 1 user group 12345 Dec 04 15:30 memory/constitution.md
#  ^^ user can read and write
```

**Step 2: Fix permissions if wrong**
```bash
# Give read/write permission to user
chmod u+rw memory/constitution.md

# Verify
ls -la memory/constitution.md
```

**Step 3: Check directory permissions**
```bash
ls -la memory/
# Directory should be readable and executable:
# drwxr-xr-x 2 user group 4096 Dec 04 15:30 memory/
#  ^^ user can read, write, execute (enter directory)
```

**Step 4: Retry validation**
```bash
specify constitution validate
# Should now work
```

---

### Issue: Constitution File Corrupted

**Symptoms**:
- Validation fails with parse errors
- File appears garbled or truncated
- YAML frontmatter broken
- Markdown formatting issues

**Resolution**:

**Step 1: Check file integrity**
```bash
# View file
cat memory/constitution.md

# Check for:
# - Truncation (file ends abruptly)
# - Binary characters (^@ or other control chars)
# - Duplicate sections
# - Broken markdown (unclosed code blocks)
```

**Step 2: Restore from Git (if tracked)**
```bash
# Check Git history
git log memory/constitution.md

# Restore from last good commit
git checkout HEAD~1 memory/constitution.md

# Or restore from specific commit
git checkout abc123 memory/constitution.md
```

**Step 3: Restore from backup (if available)**
```bash
# List backups
ls -la memory/constitution.md.backup.*

# Restore latest
cp memory/constitution.md.backup.20251204_153000 memory/constitution.md
```

**Step 4: Regenerate if no backup**
```bash
# Last resort: regenerate constitution
# WARNING: This loses all customizations

# Backup corrupted file (for reference)
mv memory/constitution.md memory/constitution.md.corrupted

# Regenerate
specify init --here
# Select appropriate tier

# Manually re-add customizations from corrupted file
```

---

## General Debugging Tips

### Enable Debug Logging

```bash
# If available, enable verbose output
export SPECIFY_DEBUG=1
export SPECIFY_LOG_LEVEL=debug

# Run command
specify constitution validate

# Check for detailed error messages

# Disable after debugging
unset SPECIFY_DEBUG
unset SPECIFY_LOG_LEVEL
```

### Check Constitution Structure

```bash
# Verify markdown structure
# Check for required sections:
grep -E "^## " memory/constitution.md

# Should include:
# ## Project Identity
# ## Technology Stack
# ## Development Standards
# etc.
```

### Validate YAML Frontmatter (if present)

```bash
# Some constitutions may have YAML frontmatter
# Check first few lines
head -n 20 memory/constitution.md

# If starts with ---, validate YAML
python3 -c "
import yaml
with open('memory/constitution.md') as f:
    content = f.read()
    if content.startswith('---'):
        # Extract frontmatter
        parts = content.split('---', 2)
        if len(parts) >= 3:
            yaml.safe_load(parts[1])
            print('✓ YAML frontmatter valid')
"
```

### Check JP Spec Kit Version

```bash
# Ensure JP Spec Kit is up to date
specify --version

# If outdated, upgrade
uv tool install . --force

# Or update globally
pip install --upgrade specify-cli
```

---

## Recovery and Rollback

### Rolling Back Constitution Changes

**If constitution changes cause issues:**

**Step 1: Check Git history**
```bash
# See recent changes to constitution
git log --oneline memory/constitution.md

# View specific change
git show <commit-hash>:memory/constitution.md
```

**Step 2: Restore previous version**
```bash
# Restore from Git
git checkout HEAD~1 memory/constitution.md

# Or restore from specific commit
git checkout <commit-hash> memory/constitution.md

# Verify
specify constitution validate
```

**Step 3: Create backup before changes**
```bash
# Always backup before editing
cp memory/constitution.md memory/constitution.md.backup.$(date +%Y%m%d_%H%M%S)

# Edit safely
vim memory/constitution.md

# If issues occur, restore
cp memory/constitution.md.backup.* memory/constitution.md
```

---

### Emergency: Reset to Default Template

**If constitution is completely broken:**

```bash
# 1. Backup current (even if broken, for reference)
mv memory/constitution.md memory/constitution.md.broken

# 2. Create new constitution from template
specify init --here
# Select appropriate tier

# 3. Verify default works
specify constitution validate

# 4. Gradually re-add customizations from broken constitution
# Open both files and manually copy custom sections
code memory/constitution.md memory/constitution.md.broken
```

---

## Prevention Best Practices

### 1. Always Validate Before Committing

```bash
# Pre-commit checklist
vim memory/constitution.md
specify constitution validate  # Must pass before commit
git add memory/constitution.md
git commit -s -m "docs(constitution): update tech stack"
```

### 2. Version Control Constitution Changes

```bash
# Commit constitution changes separately
git add memory/constitution.md
git commit -s -m "docs(constitution): add Python linting standards

- Add ruff for linting and formatting
- Specify mypy for type checking
- Document coverage requirements"

# Don't mix constitution changes with code changes
```

### 3. Backup Before Major Changes

```bash
# Before major changes or upgrades
cp memory/constitution.md memory/constitution.md.backup.$(date +%Y%m%d_%H%M%S)

# Make changes
vim memory/constitution.md

# If something goes wrong, restore
cp memory/constitution.md.backup.* memory/constitution.md
```

### 4. Document Custom Amendments

```markdown
## Custom Amendments

**Last Updated**: 2025-12-04

### Custom Quality Standards
- Test coverage: 90% (higher than default 80%)
- Security scans required on every PR

### Custom Tooling
- Using `ruff` instead of `black` + `flake8`
- Required pre-commit hooks: ruff, mypy, pytest

**Rationale**: These standards exceed default template to meet SOC2 requirements.
```

### 5. Review Constitution Regularly

```bash
# Quarterly review schedule
# Add to calendar or project schedule

# Review checklist:
# - [ ] Tech stack still accurate?
# - [ ] Quality standards still appropriate?
# - [ ] New tools adopted since last review?
# - [ ] Any deprecated practices?

# Update and commit
specify constitution validate
git commit -s -m "docs(constitution): quarterly review Q4 2025"
```

---

## Getting Help

### 1. Check Documentation

- [Constitution Validation Guide](./constitution-validation.md)
- [Constitution Distribution PRD](../prd/constitution-distribution-prd.md)
- [Tiered Constitution Templates](../../templates/constitutions/)

### 2. Check Existing Issues

```bash
# Search GitHub issues for similar problems
# https://github.com/jpoley/jp-spec-kit/issues?q=constitution
```

### 3. Enable Debug Output

```bash
# Run with maximum verbosity
export SPECIFY_DEBUG=1
export SPECIFY_LOG_LEVEL=debug
specify constitution validate 2>&1 | tee constitution-debug.log

# Share debug log when reporting issues
```

### 4. Report Issues

If none of these solutions work:

**Collect diagnostic information**:
```bash
# 1. System info
uname -a
python --version
specify --version

# 2. Constitution status
specify constitution validate --json > constitution-status.json
specify constitution version > constitution-version.txt

# 3. File info
ls -la memory/constitution.md

# 4. First 50 lines (check for corruption)
head -n 50 memory/constitution.md > constitution-sample.txt
```

**Report via GitHub Issues**:
1. Go to https://github.com/jpoley/jp-spec-kit/issues/new
2. Use template: "Constitution Issue"
3. Include:
   - Error message (full text)
   - Command that failed
   - Diagnostic output from above
   - JP Spec Kit version
   - Constitution tier (light/medium/heavy)
   - Steps to reproduce
4. Attach `constitution-status.json` (redact sensitive project info)

---

## Summary

**Most Common Issues**:
1. **Incorrect language detection** → Manually edit TECH_STACK, remove NEEDS_VALIDATION marker
2. **Stuck NEEDS_VALIDATION markers** → Delete entire marker line (including `<!--` and `-->`)
3. **Workflow blocked by validation** → Complete validation OR downgrade to medium tier
4. **Version mismatch** → Run `specify upgrade` and accept constitution update
5. **Missing constitution** → Run `specify init --here` to create

**Quick Fixes**:
- Check validation: `specify constitution validate`
- Check version: `specify constitution version`
- Backup before changes: `cp memory/constitution.md memory/constitution.md.backup`
- Restore from Git: `git checkout HEAD~1 memory/constitution.md`
- Reset to default: `mv memory/constitution.md{,.broken} && specify init --here`

**Prevention**:
- Always validate before committing
- Backup before major changes
- Document custom amendments
- Review constitution quarterly
- Version control all modifications

**Emergency Recovery**:
- Restore from backup: `cp memory/constitution.md.backup.* memory/constitution.md`
- Restore from Git: `git checkout HEAD~1 memory/constitution.md`
- Regenerate: `specify init --here` (loses customizations)

---

**Related Documentation**:
- [Constitution Validation Guide](./constitution-validation.md) - Detailed validation workflow
- [Workflow Troubleshooting Guide](./workflow-troubleshooting.md) - Workflow configuration issues
- [Backlog Troubleshooting Guide](./backlog-troubleshooting.md) - Task management issues
