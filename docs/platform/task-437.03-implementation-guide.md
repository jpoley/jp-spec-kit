# Implementation Guide: CODEOWNERS and Labeler (task-437.03)

**Parent Design**: [GitHub Workflows Platform Architecture](./task-437-github-workflows-platform.md)

**Task ID**: task-437.03
**Status**: To Do
**Priority**: Medium
**Dependencies**: None

---

## Overview

This guide provides step-by-step implementation instructions for creating CODEOWNERS and automated PR labeling for flowspec. This implementation follows the platform architecture defined in task-437.

## Files to Create

1. `.github/CODEOWNERS` - Automatic reviewer assignment
2. `.github/labeler.yml` - Label to file path mappings
3. `.github/workflows/labeler.yml` - Labeler workflow

---

## Phase 1: Create CODEOWNERS File

**Location**: `/Users/jasonpoley/ps/flowspec/.github/CODEOWNERS`

**Purpose**: Automatically assign reviewers based on changed files in PRs.

### File Content

```plaintext
# CODEOWNERS - Automatic reviewer assignment
# See: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners

# Default owner for everything (fallback)
* @jpoley

# Documentation
/docs/ @jpoley
*.md @jpoley
README* @jpoley

# CI/CD and workflows
/.github/ @jpoley
/.github/workflows/ @jpoley
/.github/actions/ @jpoley

# Source code
/src/ @jpoley

# Tests
/tests/ @jpoley

# Templates
/templates/ @jpoley

# Security-sensitive files (require extra scrutiny)
/docs/security/ @jpoley
SECURITY.md @jpoley
.github/workflows/security*.yml @jpoley

# Platform and infrastructure
/k8s/ @jpoley
/manifests/ @jpoley
Dockerfile* @jpoley
```

### Validation

```bash
# Test CODEOWNERS syntax
# GitHub will automatically validate on commit, but you can preview:
# Create a draft PR and check "Reviewers" section
```

---

## Phase 2: Create Labeler Configuration

**Location**: `/Users/jasonpoley/ps/flowspec/.github/labeler.yml`

**Purpose**: Map file path patterns to PR labels for automatic categorization.

### File Content

```yaml
# .github/labeler.yml
# Maps file paths to PR labels
# See: https://github.com/actions/labeler

# Documentation changes
documentation:
  - changed-files:
    - any-glob-to-any-file:
      - 'docs/**/*'
      - '**/*.md'
      - 'README*'

# Source code changes
source:
  - changed-files:
    - any-glob-to-any-file: 'src/**/*'

# Test changes
tests:
  - changed-files:
    - any-glob-to-any-file:
      - 'tests/**/*'
      - '**/*.test.py'
      - '**/*.spec.py'
      - '**/*_test.py'

# CI/CD changes
ci-cd:
  - changed-files:
    - any-glob-to-any-file:
      - '.github/workflows/**'
      - '.github/actions/**'
      - 'Dockerfile*'
      - 'docker-compose*.yml'

# Infrastructure changes
infrastructure:
  - changed-files:
    - any-glob-to-any-file:
      - 'k8s/**'
      - 'kubernetes/**'
      - 'manifests/**'
      - 'terraform/**'

# Dependency changes
dependencies:
  - changed-files:
    - any-glob-to-any-file:
      - 'pyproject.toml'
      - 'requirements*.txt'
      - 'uv.lock'
      - 'package.json'
      - 'package-lock.json'

# Configuration changes
config:
  - changed-files:
    - any-glob-to-any-file:
      - '**/*.config.*'
      - '**/*.yaml'
      - '**/*.yml'
      - '**/*.toml'
      - '**/*.json'

# Template changes (flowspec specific)
templates:
  - changed-files:
    - any-glob-to-any-file: 'templates/**/*'

# Security changes
security:
  - changed-files:
    - any-glob-to-any-file:
      - 'docs/security/**'
      - 'SECURITY.md'
      - '.github/workflows/security*.yml'

# Agent changes (flowspec specific)
agents:
  - changed-files:
    - any-glob-to-any-file:
      - '.claude/agents/**'
      - '.claude/commands/**'
      - '.claude/skills/**'

# Backlog task management
backlog:
  - changed-files:
    - any-glob-to-any-file:
      - 'backlog/**'
      - 'scripts/bash/backlog*'
```

### Label Alignment with release.yml

Ensure these labels match the categories in `.github/release.yml`:
- `feature`, `enhancement` → "New Features"
- `bug`, `fix` → "Bug Fixes"
- `documentation` → "Documentation"
- `dependencies` → "Dependencies"
- `infrastructure`, `ci-cd` → "Infrastructure"

**Note**: You'll manually add feature/bug labels. Labeler adds file-based labels.

---

## Phase 3: Create Labeler Workflow

**Location**: `/Users/jasonpoley/ps/flowspec/.github/workflows/labeler.yml`

**Purpose**: GitHub Actions workflow to apply labels automatically on PRs.

### Step 1: Lookup Current Action SHAs

Before creating the workflow, get the latest pinned SHAs:

```bash
# Get actions/checkout SHA for v4.1.1
gh api repos/actions/checkout/commits/v4.1.1 --jq .sha
# Expected (verify): b4ffde65f46336ab88eb53be808477a3936bae11

# Get actions/labeler SHA for v5.0.0
gh api repos/actions/labeler/commits/v5.0.0 --jq .sha
# Expected (verify): 8558fd74291d67161a8a78ce36a881fa63b766a9
```

**IMPORTANT**: Do NOT use the SHAs above without verification. Always check current versions.

### Step 2: Create Workflow File

```yaml
# .github/workflows/labeler.yml
# Auto-label PRs based on changed files
# Requires: .github/labeler.yml configuration file

name: Labeler

on:
  pull_request:
    types: [opened, synchronize]

permissions:
  contents: read
  pull-requests: write

jobs:
  label:
    runs-on: ubuntu-latest
    timeout-minutes: 5

    steps:
      - name: Checkout code
        uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1

      - name: Apply labels
        uses: actions/labeler@8558fd74291d67161a8a78ce36a881fa63b766a9  # v5.0.0
        with:
          configuration-path: .github/labeler.yml
          sync-labels: true  # Remove labels when files change
```

**Key Configuration Options**:
- `sync-labels: true` - Automatically remove labels when files no longer match pattern
- `repo-token` - Not needed (uses auto-provided GITHUB_TOKEN)

---

## Phase 4: Testing

### Test Plan

1. **Create Draft PR with Mixed Changes**
   ```bash
   git checkout -b test-labeler
   # Edit files in multiple categories
   echo "# Test" >> docs/test.md
   echo "# Test" >> src/test.py
   echo "# Test" >> tests/test_feature.py
   git add -A
   git commit -m "test: verify labeler workflow"
   git push -u origin test-labeler
   gh pr create --draft --title "Test: Labeler Workflow" --body "Testing automatic labels"
   ```

2. **Verify Labels Applied**
   - Check PR page for `documentation`, `source`, `tests` labels
   - Should appear within 30 seconds

3. **Test Label Sync**
   ```bash
   # Remove a file category
   git rm docs/test.md
   git commit -m "test: remove docs file"
   git push
   # Verify `documentation` label removed automatically
   ```

4. **Test CODEOWNERS Assignment**
   - Check PR "Reviewers" section
   - Should show `@jpoley` as requested reviewer

5. **Clean Up**
   ```bash
   gh pr close --delete-branch
   ```

### Expected Results

- [ ] Labels applied within 30 seconds of PR creation
- [ ] Labels sync when files change
- [ ] CODEOWNERS assigns reviewers correctly
- [ ] Workflow completes successfully (green check)

---

## Phase 5: Security Validation

### Security Checklist

- [ ] **Actions Pinned**: All action versions use full commit SHA (not tags)
  ```bash
  # Verify no tag references
  grep "uses:" .github/workflows/labeler.yml | grep -v "@[a-f0-9]\{40\}"
  # Should return empty (all pinned)
  ```

- [ ] **Minimal Permissions**: Workflow has least privilege
  ```yaml
  permissions:
    contents: read          # ✅ Read only
    pull-requests: write    # ✅ Required for labels
  ```

- [ ] **No External Scripts**: Workflow is declarative only (no `run:` commands)
  ```bash
  grep "run:" .github/workflows/labeler.yml
  # Should return empty
  ```

- [ ] **Configuration Validated**: labeler.yml syntax is correct
  ```bash
  # GitHub will validate on first run
  # Check workflow run logs for errors
  ```

### OpenSSF Scorecard Impact

After implementation:
- **Pinned-Dependencies**: ✅ Improved (all actions use SHA)
- **Token-Permissions**: ✅ Maintained (minimal permissions)
- **Code-Review**: ✅ Improved (CODEOWNERS enforces reviews)

Expected Scorecard score increase: +0.5 to +1.0 points

---

## Phase 6: Copy to Templates

For reuse across projects, copy files to templates:

```bash
# Create templates directory structure
mkdir -p templates/github/workflows

# Copy files (preserving structure)
cp .github/CODEOWNERS templates/github/
cp .github/labeler.yml templates/github/
cp .github/workflows/labeler.yml templates/github/workflows/

# Create template README
cat > templates/github/README.md << 'EOF'
# GitHub Project Automation Templates

Templates for CODEOWNERS, labeler, stale management, and OpenSSF Scorecard.

## Usage

1. Copy files to your project's `.github/` directory
2. Replace template variables (e.g., `@jpoley` → `@youruser`)
3. Customize file paths in `labeler.yml`
4. Verify action SHAs are current

See: docs/platform/task-437-github-workflows-platform.md
EOF
```

---

## Troubleshooting

### Issue: Labels Not Applied

**Symptoms**: PR created but no labels appear

**Diagnosis**:
1. Check workflow run status: `gh run list --workflow=labeler.yml`
2. View logs: `gh run view <run-id> --log`
3. Common causes:
   - Workflow file syntax error
   - Permissions insufficient
   - labeler.yml misconfigured

**Resolution**:
```bash
# Validate YAML syntax
yamllint .github/workflows/labeler.yml
yamllint .github/labeler.yml

# Check workflow permissions
grep -A5 "permissions:" .github/workflows/labeler.yml

# Re-trigger workflow
gh pr comment <pr-number> --body "/rerun labeler"
# Or close/reopen PR
```

### Issue: Labels Not Syncing

**Symptoms**: Old labels remain after file changes

**Diagnosis**:
- Check `sync-labels` setting in labeler.yml workflow

**Resolution**:
```yaml
# Ensure sync-labels is true
- name: Apply labels
  uses: actions/labeler@<SHA>
  with:
    configuration-path: .github/labeler.yml
    sync-labels: true  # ← Must be true
```

### Issue: CODEOWNERS Not Assigning Reviewers

**Symptoms**: PR created but no reviewers assigned

**Diagnosis**:
1. Check CODEOWNERS syntax (must be exact paths)
2. Verify user/team exists and has access
3. Check branch protection settings

**Resolution**:
```bash
# Validate CODEOWNERS format
# (GitHub provides no validation tool - test with PR)

# Check user access
gh api repos/jpoley/flowspec/collaborators/jpoley

# Verify branch protection doesn't block auto-assignment
gh api repos/jpoley/flowspec/branches/main/protection
```

---

## Acceptance Criteria Validation

Before marking task complete, verify all ACs:

- [ ] **AC #1**: CODEOWNERS file with default and path-specific owners
  - File: `.github/CODEOWNERS`
  - Content: Default `* @jpoley` + path-specific rules

- [ ] **AC #2**: labeler.yml maps all relevant file paths to labels
  - File: `.github/labeler.yml`
  - Labels: documentation, source, tests, ci-cd, infrastructure, dependencies, config, templates, security, agents

- [ ] **AC #3**: Labeler workflow triggers on pull_request events
  - File: `.github/workflows/labeler.yml`
  - Trigger: `on: pull_request: types: [opened, synchronize]`

- [ ] **AC #4**: Labels automatically applied when PR created/updated
  - Test: Create PR, verify labels appear
  - Test: Update PR, verify labels sync

- [ ] **AC #5**: Action version pinned with full commit SHA
  - Verify: All `uses:` statements have 40-character SHA
  - Command: `grep "uses:" .github/workflows/labeler.yml`

---

## Files Created

| File | Purpose | Template Location |
|------|---------|-------------------|
| `.github/CODEOWNERS` | Auto-assign reviewers | `templates/github/CODEOWNERS` |
| `.github/labeler.yml` | Label mappings | `templates/github/labeler.yml` |
| `.github/workflows/labeler.yml` | Labeler workflow | `templates/github/workflows/labeler.yml` |

---

## References

- **Platform Design**: [task-437-github-workflows-platform.md](./task-437-github-workflows-platform.md) (Section 3.2, 4.1, 4.3)
- **Parent Task**: task-437
- **GitHub Docs**: [CODEOWNERS](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- **Labeler Action**: [actions/labeler](https://github.com/actions/labeler)

---

**Implementation Checklist**:
- [ ] Phase 1: CODEOWNERS created
- [ ] Phase 2: labeler.yml config created
- [ ] Phase 3: labeler.yml workflow created with pinned SHAs
- [ ] Phase 4: Testing completed successfully
- [ ] Phase 5: Security validation passed
- [ ] Phase 6: Templates copied for reuse
- [ ] All acceptance criteria validated
