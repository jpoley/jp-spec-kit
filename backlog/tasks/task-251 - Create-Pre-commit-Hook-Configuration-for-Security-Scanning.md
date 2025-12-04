---
id: task-251
title: Create Pre-commit Hook Configuration for Security Scanning
status: To Do
assignee:
  - '@muckross'
created_date: '2025-12-03 02:26'
updated_date: '2025-12-04 16:32'
labels:
  - 'workflow:Planned'
dependencies: []
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Provide pre-commit hook template and setup script for local security scanning. Enable fast feedback (<10 seconds) before commit using /jpspec:security scan --fast.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create .pre-commit-config.yaml template with jpspec-security hook
- [ ] #2 Implement setup script scripts/setup-security-hooks.sh with installation
- [ ] #3 Add documentation for pre-commit hook usage in docs/guides/
- [ ] #4 Test hook performance (<10 seconds for typical 5-10 file commit)
- [ ] #5 Support bypass mechanism (git commit --no-verify) with audit logging
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Implementation Plan: Pre-commit Hook Configuration

### Overview
Create pre-commit hook template and setup script for fast local security scanning before commits (<10 seconds).

### Step-by-Step Implementation

#### Step 1: Create Pre-commit Hook Template
**File**: `templates/.pre-commit-config.yaml`
**Duration**: 1 hour

1. Create template with jpspec-security hook:
   ```yaml
   # JP Spec Kit Security Pre-commit Hook
   # Install: pip install pre-commit && pre-commit install
   
   repos:
     - repo: local
       hooks:
         - id: jpspec-security-fast-scan
           name: JP Spec Kit Security Scan (Fast)
           description: Run fast security scan on changed files
           entry: specify security scan --fast --changed-only --fail-on critical
           language: system
           stages: [commit]
           pass_filenames: false
           verbose: true
           # Only run if security scanning is enabled
           files: '^src/|^tests/|^lib/'
   ```

2. Add configuration options:
   - `--fast`: Skip AI triage, only basic scan
   - `--changed-only`: Only scan files in git staging area
   - `--fail-on critical`: Block only on critical issues (not high/medium)

3. Document optional hooks:
   - Pre-push hook for more thorough scan
   - Manual trigger with `--no-verify` bypass

#### Step 2: Create Setup Script
**File**: `scripts/bash/setup-security-hooks.sh`
**Duration**: 2 hours

1. Implement setup script:
   ```bash
   #!/bin/bash
   # Setup script for /jpspec:security pre-commit hooks
   
   set -e
   
   echo "Setting up JP Spec Kit security pre-commit hooks..."
   
   # Check if pre-commit is installed
   if ! command -v pre-commit &> /dev/null; then
       echo "Installing pre-commit..."
       pip install pre-commit
   fi
   
   # Copy template if .pre-commit-config.yaml doesn't exist
   if [ ! -f .pre-commit-config.yaml ]; then
       echo "Creating .pre-commit-config.yaml from template..."
       cp templates/.pre-commit-config.yaml .pre-commit-config.yaml
   else
       echo "⚠️  .pre-commit-config.yaml already exists"
       read -p "Append security hook? (y/n) " -n 1 -r
       echo
       if [[ $REPLY =~ ^[Yy]$ ]]; then
           # Append security hook to existing config
           cat >> .pre-commit-config.yaml << 'EOF'
   
     - repo: local
       hooks:
         - id: jpspec-security-fast-scan
           name: JP Spec Kit Security Scan (Fast)
           entry: specify security scan --fast --changed-only --fail-on critical
           language: system
           stages: [commit]
           pass_filenames: false
   EOF
       fi
   fi
   
   # Install hooks
   pre-commit install
   
   echo "✅ Security pre-commit hooks installed successfully!"
   echo ""
   echo "To test hooks on all files:"
   echo "  pre-commit run --all-files"
   echo ""
   echo "To skip hook temporarily:"
   echo "  git commit --no-verify"
   ```

2. Add error handling:
   - Check for specify-cli installation
   - Verify Python version (3.11+)
   - Handle permission issues

3. Add uninstall script:
   ```bash
   scripts/bash/uninstall-security-hooks.sh
   ```

#### Step 3: Optimize Fast Scan Performance
**File**: `src/specify_cli/security/fast_scan.py`
**Duration**: 2 hours

1. Implement fast scan mode:
   - Only scan files in git staging area
   - Skip AI triage (defer to CI)
   - Use minimal ruleset (critical issues only)
   - Skip report generation
   - Output to console only

2. Performance optimizations:
   - Cache Semgrep results by file hash
   - Skip unchanged files
   - Parallel file scanning
   - Progress indicator with ETA

3. Target performance: <10 seconds for 5-10 files

#### Step 4: Add Documentation
**File**: `docs/guides/pre-commit-hooks.md`
**Duration**: 1 hour

1. Create user guide:
   - Installation instructions
   - Configuration options
   - Performance tips
   - Troubleshooting common issues

2. Add examples:
   - Minimal configuration
   - Custom severity thresholds
   - Skip specific file patterns

3. Document bypass mechanisms:
   - `git commit --no-verify` for emergencies
   - Audit logging of bypasses
   - When bypass is appropriate

#### Step 5: Implement Bypass Audit Logging
**File**: `src/specify_cli/security/bypass_log.py`
**Duration**: 1 hour

1. Detect when hook is bypassed:
   - Check for `--no-verify` flag (not directly detectable)
   - Log when expected hook doesn't run
   - Track bypass events in `docs/security/bypass-log.md`

2. Bypass log format:
   ```markdown
   ## Security Hook Bypasses
   
   | Date | User | Commit | Reason | Approved By |
   |------|------|--------|--------|-------------|
   | 2025-12-04 | alice | abc123 | Emergency hotfix | security-team |
   ```

3. Add bypass review command:
   ```bash
   specify security bypass-review --since 2025-12-01
   ```

#### Step 6: Testing
**Duration**: 2 hours

1. **Performance Test**:
   - Commit 5 files: measure time
   - Commit 10 files: measure time
   - Verify <10 second target met

2. **Functionality Test**:
   - Test with vulnerable code: should block
   - Test with clean code: should pass
   - Test with medium severity: should warn but pass

3. **Edge Cases**:
   - No files changed: should pass immediately
   - Binary files: should skip
   - Large files (>1MB): should warn about performance

4. **Integration Test**:
   - Install on real project
   - Run through typical development workflow
   - Verify no false positives blocking commits

### Dependencies
- `specify security scan --fast` command implementation (task-210)
- Git integration for changed file detection

### Testing Checklist
- [ ] Setup script runs without errors
- [ ] Pre-commit hook triggers on commit
- [ ] Fast scan completes in <10 seconds
- [ ] Hook blocks critical vulnerabilities
- [ ] Hook allows safe commits
- [ ] Bypass with --no-verify works
- [ ] Bypass audit logging works

### Estimated Effort
**Total**: 9 hours (1.1 days)
<!-- SECTION:PLAN:END -->
