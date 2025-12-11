# Implementation Guide: OpenSSF Scorecard Security Workflow (task-437.05)

**Parent Design**: [GitHub Workflows Platform Architecture](./task-437-github-workflows-platform.md)

**Task ID**: task-437.05
**Status**: To Do
**Priority**: High (Security)
**Dependencies**: None

---

## Overview

This guide provides step-by-step implementation instructions for OpenSSF Scorecard security workflow for flowspec. Scorecard evaluates repositories against security best practices and provides a public badge showing the security posture.

## Files to Create/Update

1. `.github/workflows/scorecard.yml` - Scorecard workflow
2. `README.md` - Add Scorecard badge

---

## Phase 1: Understand OpenSSF Scorecard

### What is OpenSSF Scorecard?

OpenSSF (Open Source Security Foundation) Scorecard is an automated tool that evaluates open source projects against a set of security best practices. It provides a score (0-10) and specific recommendations for improvement.

### Key Checks

| Check | Description | Impact on flowspec |
|-------|-------------|-------------------|
| **Binary-Artifacts** | No binaries in repo | ✅ Clean repo |
| **Branch-Protection** | Main branch protected | ✅ Already enabled |
| **CI-Tests** | Automated tests run | ✅ CI workflow exists |
| **CII-Best-Practices** | OpenSSF badge | 🟡 Future enhancement |
| **Code-Review** | PRs require review | ✅ CODEOWNERS enforces |
| **Dangerous-Workflow** | No script injection | ✅ Safe workflows |
| **Dependency-Update-Tool** | Renovate/Dependabot | 🟡 To be added |
| **Fuzzing** | Fuzz testing enabled | ⚠️ Not applicable (CLI tool) |
| **License** | Valid license file | ✅ LICENSE exists |
| **Maintained** | Recent activity | ✅ Active development |
| **Pinned-Dependencies** | Actions use SHA | ✅ After task-437.03 |
| **SAST** | Static analysis | ✅ Bandit + Semgrep |
| **Security-Policy** | SECURITY.md exists | 🟡 To be created (task-437.06) |
| **Signed-Releases** | Release signatures | 🟡 Future enhancement |
| **Token-Permissions** | Minimal permissions | ✅ Already implemented |
| **Vulnerabilities** | Known CVEs | ✅ Security scan checks |

**Expected Initial Score**: 6.5-7.5 (good baseline)
**Target Score**: 8.0+ (excellent security posture)

### Why Scorecard Matters

1. **Transparency**: Public badge shows security commitment
2. **Continuous Monitoring**: Weekly scans catch regressions
3. **Best Practices**: Automated enforcement of security standards
4. **Compliance**: Aligns with SLSA framework (already a flowspec goal)
5. **Trust**: Users can verify security practices

---

## Phase 2: Lookup Current Action SHAs

Before creating the workflow, verify and record current action SHAs:

```bash
# Get actions/checkout SHA for v4.1.1
gh api repos/actions/checkout/commits/v4.1.1 --jq .sha
# Expected (verify): b4ffde65f46336ab88eb53be808477a3936bae11

# Get ossf/scorecard-action SHA for v2.3.1
gh api repos/ossf/scorecard-action/commits/v2.3.1 --jq .sha
# Expected (verify): 0864cf19026789058feabb7e87baa5f140aac736

# Get actions/upload-artifact SHA for v4.3.0
gh api repos/actions/upload-artifact/commits/v4.3.0 --jq .sha
# Expected (verify): 26f96dfa697d77e81fd5907df203aa23a56210a8

# Get github/codeql-action SHA for upload-sarif (v3.23.0)
gh api repos/github/codeql-action/commits/v3.23.0 --jq .sha
# Expected (verify): 012739e5082ff0c22ca6d6ab32e07c36df03c4a4
```

**CRITICAL**: Do NOT use these SHAs without verification. Always check for the latest stable versions.

**Record SHAs**:
| Action | Version | SHA (verified on <date>) |
|--------|---------|--------------------------|
| actions/checkout | v4.1.1 | `<your-verified-sha>` |
| ossf/scorecard-action | v2.3.1 | `<your-verified-sha>` |
| actions/upload-artifact | v4.3.0 | `<your-verified-sha>` |
| github/codeql-action/upload-sarif | v3.23.0 | `<your-verified-sha>` |

---

## Phase 3: Create Scorecard Workflow

**Location**: `/Users/jasonpoley/ps/flowspec/.github/workflows/scorecard.yml`

**Purpose**: Run OpenSSF Scorecard analysis weekly and on every push to main, upload results to GitHub Security tab.

### Workflow File

```yaml
# .github/workflows/scorecard.yml
# OpenSSF Scorecard - Security best practices analysis
# Runs weekly and on every push to main
# Uploads SARIF to GitHub Security tab

name: OpenSSF Scorecard

on:
  push:
    branches: [main]
  schedule:
    - cron: '30 1 * * 6'  # Saturdays 1:30 AM UTC (avoid :00 times)
  workflow_dispatch:

# Minimal permissions by default, explicit grants below
permissions: read-all

jobs:
  scorecard:
    name: Scorecard analysis
    runs-on: ubuntu-latest
    timeout-minutes: 15

    permissions:
      security-events: write  # Upload SARIF to Security tab
      id-token: write         # OIDC token for Scorecard API
      contents: read          # Read repository
      actions: read           # Read workflow files for analysis

    steps:
      - name: Checkout code
        uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
        with:
          persist-credentials: false  # Security best practice

      - name: Run Scorecard analysis
        uses: ossf/scorecard-action@0864cf19026789058feabb7e87baa5f140aac736  # v2.3.1
        with:
          results_file: results.sarif
          results_format: sarif
          publish_results: true  # Publish to Scorecard API for badge

      - name: Upload SARIF artifact
        uses: actions/upload-artifact@26f96dfa697d77e81fd5907df203aa23a56210a8  # v4.3.0
        with:
          name: SARIF file
          path: results.sarif
          retention-days: 5

      - name: Upload SARIF to GitHub Security
        uses: github/codeql-action/upload-sarif@012739e5082ff0c22ca6d6ab32e07c36df03c4a4  # v3.23.0
        with:
          sarif_file: results.sarif
          category: flowspec-scorecard
```

### Configuration Breakdown

| Setting | Value | Rationale |
|---------|-------|-----------|
| **Triggers** | `push: [main]`, `schedule`, `workflow_dispatch` | Run on every main push + weekly scan + manual |
| **Cron Schedule** | `30 1 * * 6` (Sat 1:30 AM) | Weekly, off-hours, avoids :00 load spike |
| **Default Permissions** | `read-all` | Least privilege by default |
| **Job Permissions** | Explicit security-events, id-token, contents, actions | Minimal required for Scorecard |
| **persist-credentials** | `false` | Prevents credential leakage in logs |
| **publish_results** | `true` | Enables public Scorecard badge |
| **SARIF Category** | `flowspec-scorecard` | Separate from other security scans |
| **Artifact Retention** | 5 days | SARIF uploaded to Security tab (permanent), artifact is backup |

### Security Hardening

- ✅ **Action SHA Pinning**: All actions use full commit SHA
- ✅ **Minimal Permissions**: Only required permissions granted
- ✅ **Credential Isolation**: `persist-credentials: false`
- ✅ **Timeout**: 15 minutes prevents runaway jobs
- ✅ **Read-only Default**: `permissions: read-all` prevents accidental writes

---

## Phase 4: Add Scorecard Badge to README

**Location**: `/Users/jasonpoley/ps/flowspec/README.md`

### Step 1: Read Current README

```bash
# View current README
cat README.md | head -20
```

### Step 2: Add Badge

Add the Scorecard badge to the badges section (typically near the top):

```markdown
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/jpoley/flowspec/badge)](https://scorecard.dev/viewer/?uri=github.com/jpoley/flowspec)
```

**Badge Placement Example**:
```markdown
# flowspec

[![CI](https://github.com/jpoley/flowspec/actions/workflows/ci.yml/badge.svg)](https://github.com/jpoley/flowspec/actions/workflows/ci.yml)
[![Security Scan](https://github.com/jpoley/flowspec/actions/workflows/security-scan.yml/badge.svg)](https://github.com/jpoley/flowspec/actions/workflows/security-scan.yml)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/jpoley/flowspec/badge)](https://scorecard.dev/viewer/?uri=github.com/jpoley/flowspec)

Spec-Driven Development toolkit for AI-augmented workflows.
```

### Badge URL Format

```
https://api.scorecard.dev/projects/github.com/{OWNER}/{REPO}/badge
```

For flowspec:
- Owner: `jpoley`
- Repo: `flowspec`
- Badge URL: `https://api.scorecard.dev/projects/github.com/jpoley/flowspec/badge`
- Viewer URL: `https://scorecard.dev/viewer/?uri=github.com/jpoley/flowspec`

**Note**: Badge will show "No data" until first workflow run completes and publishes results.

---

## Phase 5: Testing

### Test Plan

1. **Commit Workflow File**
   ```bash
   git checkout -b feat/openssf-scorecard
   git add .github/workflows/scorecard.yml
   git commit -m "feat: add OpenSSF Scorecard security workflow"
   git push -u origin feat/openssf-scorecard
   ```

2. **Create PR (Optional)**
   ```bash
   gh pr create --title "feat: Add OpenSSF Scorecard workflow" \
                --body "Implements task-437.05: OpenSSF Scorecard security analysis"
   ```

3. **Merge to Main**
   ```bash
   gh pr merge --merge  # Or merge via GitHub UI
   ```

4. **Verify Workflow Triggers on Push**
   ```bash
   # Check workflow run status
   gh run list --workflow=scorecard.yml --limit 1

   # View logs
   gh run view --log
   ```

5. **Verify SARIF Upload**
   - Navigate to: `https://github.com/jpoley/flowspec/security/code-scanning`
   - Look for "flowspec-scorecard" category
   - Check for Scorecard findings

6. **Verify Artifact Upload**
   ```bash
   # Download artifact
   gh run download <run-id> --name "SARIF file"

   # View SARIF
   cat results.sarif | jq .
   ```

7. **Verify Badge**
   - Wait 5-10 minutes for Scorecard API to update
   - Navigate to: `https://scorecard.dev/viewer/?uri=github.com/jpoley/flowspec`
   - Check score and detailed results
   - Verify badge displays in README

8. **Manual Trigger Test**
   ```bash
   # Trigger workflow manually
   gh workflow run scorecard.yml

   # Check status
   gh run watch
   ```

### Expected Results

- [ ] Workflow completes successfully (green check)
- [ ] SARIF uploaded to Security tab under "flowspec-scorecard"
- [ ] Artifact uploaded with 5-day retention
- [ ] Scorecard badge shows score (may take 10 minutes)
- [ ] Scorecard viewer shows detailed check results
- [ ] No workflow errors in logs

---

## Phase 6: Interpret Scorecard Results

After first run, review results at: `https://scorecard.dev/viewer/?uri=github.com/jpoley/flowspec`

### Score Interpretation

| Score | Rating | Action Required |
|-------|--------|-----------------|
| **9.0-10.0** | Excellent | Maintain current practices |
| **7.5-8.9** | Good | Minor improvements recommended |
| **6.0-7.4** | Fair | Address medium-priority findings |
| **4.0-5.9** | Needs Improvement | Fix high-priority issues |
| **0.0-3.9** | Critical | Immediate action required |

### Common Findings and Remediations

**Dependency-Update-Tool (likely to fail initially)**:
- Finding: No automated dependency updates
- Remediation: Add Renovate config (future task)
- Impact on Score: -1.0

**Security-Policy (likely to fail initially)**:
- Finding: No SECURITY.md file
- Remediation: Create SECURITY.md (task-437.06)
- Impact on Score: -0.5

**Signed-Releases (likely to fail)**:
- Finding: Releases not cryptographically signed
- Remediation: Configure release signing (future enhancement)
- Impact on Score: -0.5

**Pinned-Dependencies (should pass after task-437.03)**:
- Finding: All actions use commit SHA
- Status: ✅ Implemented
- Impact on Score: +1.0

**SAST (should pass)**:
- Finding: Bandit + Semgrep configured
- Status: ✅ Implemented
- Impact on Score: +1.0

### Remediation Priority

1. **High Priority** (fix immediately):
   - Pinned-Dependencies (task-437.03)
   - Token-Permissions (already done)
   - Dangerous-Workflow (already safe)

2. **Medium Priority** (fix in next sprint):
   - Security-Policy (task-437.06)
   - Dependency-Update-Tool (add Renovate)

3. **Low Priority** (nice to have):
   - Signed-Releases
   - CII-Best-Practices badge
   - Fuzzing (not applicable for CLI)

---

## Phase 7: Security Validation

### Security Checklist

- [ ] **All Actions Pinned**: Every `uses:` statement has 40-character SHA
  ```bash
  grep "uses:" .github/workflows/scorecard.yml | grep -v "@[a-f0-9]\{40\}"
  # Should return empty (all pinned)
  ```

- [ ] **Minimal Permissions**: Job permissions are least-privilege
  ```yaml
  permissions:
    security-events: write  # ✅ Required for SARIF upload
    id-token: write         # ✅ Required for Scorecard API
    contents: read          # ✅ Required to read repo
    actions: read           # ✅ Required to analyze workflows
  ```

- [ ] **Credential Isolation**: No credential leakage
  ```yaml
  persist-credentials: false  # ✅ Prevents Git credential exposure
  ```

- [ ] **SARIF Category Unique**: No conflict with other scans
  ```bash
  grep "category:" .github/workflows/*.yml
  # Should show: flowspec-scorecard, flowspec-security (unique)
  ```

- [ ] **Safe Cron Schedule**: Avoids `:00` minute
  ```bash
  grep "cron:" .github/workflows/scorecard.yml
  # Should show: '30 1 * * 6' (not :00)
  ```

### OpenSSF Scorecard Impact

This workflow improves the Scorecard score by:
- **Pinned-Dependencies**: ✅ Uses SHA-pinned actions
- **Token-Permissions**: ✅ Minimal permissions model
- **CI-Tests**: ✅ Demonstrates active security testing

**Expected Score After Implementation**: +0.5 to +1.0 improvement

---

## Phase 8: Copy to Templates

For reuse across projects:

```bash
# Create templates directory
mkdir -p templates/github/workflows

# Copy workflow
cp .github/workflows/scorecard.yml templates/github/workflows/

# Create template with variables
cat > templates/github/workflows/scorecard.yml.template << 'EOF'
# Template: OpenSSF Scorecard workflow
# Replace variables before use:
#   {{ CHECKOUT_SHA }} - actions/checkout commit SHA
#   {{ SCORECARD_SHA }} - ossf/scorecard-action commit SHA
#   {{ UPLOAD_ARTIFACT_SHA }} - actions/upload-artifact commit SHA
#   {{ CODEQL_SHA }} - github/codeql-action/upload-sarif commit SHA
#   {{ PROJECT_NAME }} - Project name for SARIF category (e.g., flowspec)

name: OpenSSF Scorecard

on:
  push:
    branches: [main]
  schedule:
    - cron: '30 1 * * 6'
  workflow_dispatch:

permissions: read-all

jobs:
  scorecard:
    name: Scorecard analysis
    runs-on: ubuntu-latest
    timeout-minutes: 15

    permissions:
      security-events: write
      id-token: write
      contents: read
      actions: read

    steps:
      - name: Checkout code
        uses: actions/checkout@{{ CHECKOUT_SHA }}  # v4.1.1
        with:
          persist-credentials: false

      - name: Run Scorecard analysis
        uses: ossf/scorecard-action@{{ SCORECARD_SHA }}  # v2.3.1
        with:
          results_file: results.sarif
          results_format: sarif
          publish_results: true

      - name: Upload SARIF artifact
        uses: actions/upload-artifact@{{ UPLOAD_ARTIFACT_SHA }}  # v4.3.0
        with:
          name: SARIF file
          path: results.sarif
          retention-days: 5

      - name: Upload SARIF to GitHub Security
        uses: github/codeql-action/upload-sarif@{{ CODEQL_SHA }}  # v3.23.0
        with:
          sarif_file: results.sarif
          category: {{ PROJECT_NAME }}-scorecard
EOF

# Update template README
cat >> templates/github/README.md << 'EOF'

## OpenSSF Scorecard Workflow

File: `workflows/scorecard.yml`
- Weekly security best practices scan
- SARIF uploaded to Security tab
- Public badge for README
- Requires: Public repository or GitHub Apps installation

### Setup:
1. Replace template variables with actual SHAs
2. Update SARIF category with project name
3. Add badge to README:
   ```markdown
   [![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/{owner}/{repo}/badge)](https://scorecard.dev/viewer/?uri=github.com/{owner}/{repo})
   ```
EOF
```

---

## Troubleshooting

### Issue: Workflow Fails with "Permission denied"

**Symptoms**: Scorecard action fails with permission error

**Diagnosis**:
```bash
# Check workflow permissions
grep -A10 "permissions:" .github/workflows/scorecard.yml
```

**Resolution**:
Ensure job-level permissions include:
```yaml
permissions:
  security-events: write  # Required
  id-token: write         # Required
  contents: read          # Required
  actions: read           # Required
```

### Issue: SARIF Not Appearing in Security Tab

**Symptoms**: Workflow completes but no SARIF in Security tab

**Diagnosis**:
1. Check SARIF category uniqueness
2. Verify upload-sarif step succeeded
3. Check artifact for valid SARIF

**Resolution**:
```bash
# Download artifact
gh run download <run-id> --name "SARIF file"

# Validate SARIF structure
jq . results.sarif

# Check category
jq '.runs[0].tool.driver.name' results.sarif

# Verify upload-sarif step
gh run view <run-id> --log | grep "upload-sarif"
```

### Issue: Badge Shows "No Data"

**Symptoms**: Scorecard badge displays "No data" even after workflow runs

**Diagnosis**:
1. Check `publish_results: true` in workflow
2. Verify workflow completed successfully
3. Wait 10-15 minutes for Scorecard API to update

**Resolution**:
```bash
# Verify publish_results setting
grep "publish_results" .github/workflows/scorecard.yml

# Check workflow run status
gh run view --log | grep "Scorecard action completed"

# Wait and refresh badge URL
# Visit: https://scorecard.dev/viewer/?uri=github.com/jpoley/flowspec
```

### Issue: Score Lower Than Expected

**Symptoms**: Scorecard score is below 7.0

**Diagnosis**:
Review detailed results at Scorecard viewer

**Resolution**:
1. **Pinned-Dependencies**: Ensure all workflows use SHA (task-437.03)
2. **Security-Policy**: Create SECURITY.md (task-437.06)
3. **Branch-Protection**: Enable required reviews on main
4. **Dependency-Update-Tool**: Add Renovate config

Priority order: Fix critical (red) checks first, then high (orange), then medium (yellow).

---

## Acceptance Criteria Validation

Before marking task complete, verify all ACs:

- [ ] **AC #1**: scorecard.yml workflow triggers on push to main and weekly
  - Trigger: `on: push: branches: [main]`
  - Trigger: `schedule: - cron: '30 1 * * 6'`
  - Trigger: `workflow_dispatch`

- [ ] **AC #2**: SARIF results uploaded to code-scanning dashboard
  - Navigate to: `https://github.com/jpoley/flowspec/security/code-scanning`
  - Verify: "flowspec-scorecard" category present
  - Check: Scorecard findings visible

- [ ] **AC #3**: Artifact uploaded with 5-day retention
  - Workflow run shows artifact: "SARIF file"
  - Retention: `retention-days: 5`

- [ ] **AC #4**: All action versions pinned with full commit SHA
  - Verify: `grep "uses:" .github/workflows/scorecard.yml | grep "[a-f0-9]\{40\}"`
  - Count: 4 actions, all SHA-pinned

- [ ] **AC #5**: README badge displays current scorecard rating
  - Badge added to README.md
  - URL: `https://api.scorecard.dev/projects/github.com/jpoley/flowspec/badge`
  - Badge shows score (not "No data")

- [ ] **AC #6**: Workflow passes on first run
  - Run status: ✅ Success (green check)
  - No errors in logs
  - SARIF uploaded successfully

---

## Post-Implementation Monitoring

### Weekly Scorecard Review

Set calendar reminder to review Scorecard results weekly:
1. Visit: `https://scorecard.dev/viewer/?uri=github.com/jpoley/flowspec`
2. Check for score changes (+/-)
3. Review new findings
4. Address critical/high severity issues

### Score Trend Tracking

| Date | Score | Change | Key Improvements |
|------|-------|--------|------------------|
| 2025-12-10 | TBD | Initial | Scorecard workflow added |
| 2025-12-11 | TBD | +X.X | Pinned dependencies (task-437.03) |
| 2025-12-12 | TBD | +X.X | Security policy (task-437.06) |
| Future | 8.0+ | +X.X | Renovate added |

### Alerting Strategy

- **Score drops below 7.0**: Investigate immediately
- **New critical finding**: Fix within 24 hours
- **New high finding**: Fix within 1 week
- **New medium finding**: Schedule for next sprint

---

## Files Created/Updated

| File | Purpose | Template Location |
|------|---------|-------------------|
| `.github/workflows/scorecard.yml` | Scorecard workflow | `templates/github/workflows/scorecard.yml.template` |
| `README.md` | Badge added | N/A |

---

## References

- **Platform Design**: [task-437-github-workflows-platform.md](./task-437-github-workflows-platform.md) (Section 2.1, 2.2, 4.1)
- **Parent Task**: task-437
- **OpenSSF Scorecard**: [https://securityscorecards.dev/](https://securityscorecards.dev/)
- **Scorecard Action**: [https://github.com/ossf/scorecard-action](https://github.com/ossf/scorecard-action)
- **SLSA Framework**: [https://slsa.dev/](https://slsa.dev/)

---

**Implementation Checklist**:
- [ ] Phase 1: Understand Scorecard checks and expectations
- [ ] Phase 2: Action SHAs verified and recorded
- [ ] Phase 3: scorecard.yml workflow created with pinned SHAs
- [ ] Phase 4: Badge added to README
- [ ] Phase 5: Testing completed successfully
- [ ] Phase 6: Results interpreted and remediation planned
- [ ] Phase 7: Security validation passed
- [ ] Phase 8: Template created for reuse
- [ ] All acceptance criteria validated
- [ ] Post-implementation monitoring configured
