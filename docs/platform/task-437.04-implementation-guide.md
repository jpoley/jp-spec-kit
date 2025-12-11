# Implementation Guide: Release Notes and Stale Management (task-437.04)

**Parent Design**: [GitHub Workflows Platform Architecture](./task-437-github-workflows-platform.md)

**Task ID**: task-437.04
**Status**: To Do
**Priority**: Medium
**Dependencies**: task-437.03 (labeler must be configured first)

---

## Overview

This guide provides step-by-step implementation instructions for automated release notes generation and stale issue/PR management for flowspec. This implementation follows the platform architecture defined in task-437.

## Files to Create

1. `.github/release.yml` - Release notes configuration
2. `.github/workflows/stale.yml` - Stale management workflow

---

## Phase 1: Create Release Notes Configuration

**Location**: `/Users/jasonpoley/ps/flowspec/.github/release.yml`

**Purpose**: Automatically generate categorized changelogs from PR labels when creating GitHub releases.

### File Content

```yaml
# .github/release.yml
# GitHub Release Notes Configuration
# Auto-generates categorized changelogs from PR labels

changelog:
  exclude:
    labels:
      - skip-changelog
      - duplicate
      - invalid
      - wontfix
    authors:
      - renovate
      - renovate[bot]
      - github-actions[bot]
      - dependabot[bot]

  categories:
    - title: Breaking Changes
      labels:
        - breaking-change
        - breaking

    - title: New Features
      labels:
        - feature
        - enhancement
        - feat

    - title: Bug Fixes
      labels:
        - bug
        - fix
        - bugfix

    - title: Documentation
      labels:
        - documentation
        - docs

    - title: Dependencies
      labels:
        - dependencies
        - deps

    - title: Infrastructure
      labels:
        - infrastructure
        - ci-cd
        - platform

    - title: Security
      labels:
        - security
        - vulnerability

    - title: Agents & Templates
      labels:
        - agents
        - templates

    - title: Other Changes
      labels:
        - '*'
```

### Label Consistency Check

Verify these labels align with `labeler.yml`:
- ✅ `documentation` (auto-applied by labeler)
- ✅ `infrastructure` (auto-applied by labeler)
- ✅ `dependencies` (auto-applied by labeler)
- ✅ `agents` (auto-applied by labeler)
- ✅ `templates` (auto-applied by labeler)
- ⚠️ `feature`, `bug` (manually applied by developers)
- ⚠️ `breaking-change`, `security` (manually applied for critical changes)

### Bot Exclusion Rationale

- **renovate[bot]**: Dependency updates are noise in release notes
- **github-actions[bot]**: Automated PRs (e.g., backlog flush) aren't user-facing changes
- **dependabot[bot]**: Similar to Renovate, not user-relevant

**Result**: Focus on human-contributed changes while tracking dependency updates in "Dependencies" section.

---

## Phase 2: Create Stale Management Workflow

**Location**: `/Users/jasonpoley/ps/flowspec/.github/workflows/stale.yml`

**Purpose**: Automatically mark and close stale issues/PRs to maintain a clean backlog.

### Step 1: Lookup Current Action SHA

```bash
# Get actions/stale SHA for v9.0.0
gh api repos/actions/stale/commits/v9.0.0 --jq .sha
# Expected (verify): 28ca1036281a5e5922ade5f6a508c69cc48b4657
```

**IMPORTANT**: Verify the SHA before use. Do not blindly copy.

### Step 2: Create Workflow File

```yaml
# .github/workflows/stale.yml
# Mark and close stale issues and PRs
# Issues: 60 days -> stale, 7 days -> close (67 total)
# PRs: 30 days -> stale, 7 days -> close (37 total)

name: Stale

on:
  schedule:
    - cron: '17 3 * * *'  # Daily at 3:17 AM UTC (avoid :00 times)
  workflow_dispatch:

permissions:
  issues: write
  pull-requests: write

jobs:
  stale:
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - name: Mark and close stale issues/PRs
        uses: actions/stale@28ca1036281a5e5922ade5f6a508c69cc48b4657  # v9.0.0
        with:
          # Issue configuration
          days-before-issue-stale: 60
          days-before-issue-close: 7
          stale-issue-label: 'stale'
          stale-issue-message: |
            This issue has been automatically marked as stale because it has not had
            recent activity. It will be closed in 7 days if no further activity occurs.

            If this issue is still relevant, please comment to keep it open.

            Thank you for your contributions to flowspec.
          close-issue-message: |
            This issue was automatically closed because it has been stale for 7 days
            with no activity.

            If you believe this issue should remain open, please reopen it and provide
            an update or explanation.

            Thank you for your understanding.
          exempt-issue-labels: 'pinned,security,PRD'

          # PR configuration
          days-before-pr-stale: 30
          days-before-pr-close: 7
          stale-pr-label: 'stale'
          stale-pr-message: |
            This pull request has been automatically marked as stale because it has not
            had recent activity. It will be closed in 7 days if no further activity occurs.

            If you're still working on this, please:
            - Push updates to the branch
            - Comment on the PR
            - Add the 'work-in-progress' label

            Thank you for your contribution to flowspec.
          close-pr-message: |
            This pull request was automatically closed because it has been stale for 7 days
            with no activity.

            If you'd like to continue this work, please reopen the PR or create a new one
            with updated changes.

            Thank you for your contribution.
          exempt-pr-labels: 'pinned,security,work-in-progress'

          # Exemptions
          exempt-all-milestones: true
          exempt-all-assignees: true

          # Operations
          operations-per-run: 100
          remove-stale-when-updated: true
          ascending: false  # Process newest first
```

### Configuration Breakdown

| Setting | Value | Rationale |
|---------|-------|-----------|
| **Cron Schedule** | `17 3 * * *` | Avoid `:00` times (GitHub Actions load spike) |
| **Issue Stale** | 60 days | Long enough for low-priority work |
| **Issue Close** | 7 days after stale | Grace period for response |
| **PR Stale** | 30 days | Shorter timeline for active work |
| **PR Close** | 7 days after stale | Grace period for updates |
| **Exempt Labels (Issues)** | `pinned`, `security`, `PRD` | Critical items never close |
| **Exempt Labels (PRs)** | `pinned`, `security`, `work-in-progress` | Active work protected |
| **Exempt Milestones** | `true` | Milestone work is planned |
| **Exempt Assignees** | `true` | Someone owns it |
| **Operations per run** | 100 | Prevent API rate limits |

### Exemption Strategy

**Protected Items** (never marked stale):
- Issues/PRs with `pinned` label (long-term tracking)
- Issues/PRs with `security` label (never auto-close vulnerabilities)
- Issues with `PRD` label (product requirements in progress)
- PRs with `work-in-progress` label (actively being developed)
- Any issue/PR in a milestone (planned work)
- Any issue/PR with an assignee (owned work)

**Example Timeline**:
```
Day 0: Issue created
Day 60: Issue marked stale (no activity)
Day 61-67: Grace period (7 days)
Day 67: Issue auto-closed

Exception: If issue has security label → never marked stale
Exception: If someone comments on Day 65 → stale label removed, timer resets
```

---

## Phase 3: Testing

### Test Plan for Release Notes

1. **Create Test Labels**
   ```bash
   # Ensure labels exist in repository
   gh label create "feature" --color "0e8a16" --description "New feature or enhancement" || true
   gh label create "bug" --color "d73a4a" --description "Bug fix" || true
   gh label create "breaking-change" --color "b60205" --description "Breaking API change" || true
   gh label create "skip-changelog" --color "cccccc" --description "Exclude from release notes" || true
   ```

2. **Create Test PRs**
   ```bash
   # Create feature PR
   git checkout -b test-feature
   echo "# Feature" >> test-feature.txt
   git add test-feature.txt
   git commit -m "feat: add test feature"
   git push -u origin test-feature
   gh pr create --title "feat: Test Feature" --body "Test feature PR" --label "feature"
   gh pr merge --merge

   # Create bug fix PR
   git checkout -b test-bugfix
   echo "# Fix" >> test-bugfix.txt
   git add test-bugfix.txt
   git commit -m "fix: test bugfix"
   git push -u origin test-bugfix
   gh pr create --title "fix: Test Bugfix" --body "Test bugfix PR" --label "bug"
   gh pr merge --merge
   ```

3. **Create Test Release**
   ```bash
   gh release create v0.1.0-test --title "Test Release" --notes "Auto-generated release notes test"
   ```

4. **Verify Release Notes**
   - Navigate to Releases page
   - Check "What's Changed" section
   - Verify categories: "New Features", "Bug Fixes"
   - Verify PRs are correctly categorized

5. **Clean Up**
   ```bash
   gh release delete v0.1.0-test --yes
   git push --delete origin test-feature test-bugfix
   ```

### Test Plan for Stale Workflow

**Note**: Testing stale management requires waiting or manual triggers. Use dry-run approach:

1. **Manual Trigger (Dry Run)**
   ```bash
   # Trigger workflow manually
   gh workflow run stale.yml

   # Check run status
   gh run list --workflow=stale.yml --limit 1

   # View logs
   gh run view --log
   ```

2. **Create Test Stale Issue**
   ```bash
   # Create old issue (simulate with manual label)
   gh issue create --title "Test Stale Issue" --body "This will be marked stale for testing"

   # Manually add stale label to test messages
   gh issue edit <issue-number> --add-label "stale"

   # Verify stale message format in issue comments
   ```

3. **Test Exemptions**
   ```bash
   # Create pinned issue
   gh issue create --title "Pinned Issue" --body "Should never be stale" --label "pinned"

   # Run stale workflow
   gh workflow run stale.yml

   # Verify pinned issue NOT marked stale
   gh issue view <issue-number> --json labels --jq '.labels[].name' | grep -v stale
   ```

4. **Expected Stale Workflow Behavior**
   - [ ] Workflow runs successfully (green check)
   - [ ] Stale label applied to old issues/PRs
   - [ ] Exempt labels prevent stale marking
   - [ ] Messages are posted correctly
   - [ ] No errors in workflow logs

---

## Phase 4: Security Validation

### Security Checklist

- [ ] **Action Pinned**: actions/stale uses full commit SHA (not tag)
  ```bash
  grep "actions/stale@" .github/workflows/stale.yml | grep "[a-f0-9]\{40\}"
  # Should return SHA-pinned version
  ```

- [ ] **Minimal Permissions**: Workflow has only required permissions
  ```yaml
  permissions:
    issues: write          # ✅ Required for stale labels/close
    pull-requests: write   # ✅ Required for PR stale labels/close
  ```

- [ ] **No External Scripts**: Workflow is declarative only
  ```bash
  grep "run:" .github/workflows/stale.yml
  # Should return empty (no script execution)
  ```

- [ ] **Safe Cron Schedule**: Avoids `:00` minute times
  ```bash
  grep "cron:" .github/workflows/stale.yml
  # Should show non-zero minute (e.g., :17)
  ```

### OpenSSF Scorecard Impact

After implementation:
- **Pinned-Dependencies**: ✅ Maintained (action uses SHA)
- **Token-Permissions**: ✅ Maintained (minimal permissions)
- **Dangerous-Workflow**: ✅ Passed (no script injection risk)

Expected Scorecard score: No change (security maintained)

---

## Phase 5: Label Creation

Ensure all referenced labels exist in the repository:

```bash
# Create release note category labels
gh label create "breaking-change" --color "b60205" --description "Breaking API change" || true
gh label create "feature" --color "0e8a16" --description "New feature or enhancement" || true
gh label create "enhancement" --color "0e8a16" --description "Enhancement to existing feature" || true
gh label create "bug" --color "d73a4a" --description "Bug fix" || true
gh label create "fix" --color "d73a4a" --description "Bug fix (alternate)" || true
gh label create "security" --color "ee0701" --description "Security vulnerability or fix" || true
gh label create "vulnerability" --color "ee0701" --description "Security vulnerability" || true

# Create stale management labels
gh label create "stale" --color "eeeeee" --description "Marked stale due to inactivity" || true
gh label create "pinned" --color "0052cc" --description "Never mark as stale" || true
gh label create "PRD" --color "5319e7" --description "Product requirements document" || true
gh label create "work-in-progress" --color "fbca04" --description "PR actively being worked on" || true

# Create exclusion labels
gh label create "skip-changelog" --color "cccccc" --description "Exclude from release notes" || true
gh label create "duplicate" --color "cccccc" --description "Duplicate issue/PR" || true
gh label create "invalid" --color "cccccc" --description "Invalid issue/PR" || true
gh label create "wontfix" --color "cccccc" --description "Won't be fixed" || true
```

**Note**: Labels auto-created by labeler.yml (documentation, source, tests, etc.) do NOT need manual creation.

---

## Phase 6: Copy to Templates

For reuse across projects:

```bash
# Create templates directory structure
mkdir -p templates/github/workflows

# Copy files
cp .github/release.yml templates/github/
cp .github/workflows/stale.yml templates/github/workflows/

# Update template README
cat >> templates/github/README.md << 'EOF'

## Release Notes Configuration

File: `release.yml`
- Categorizes PRs by labels
- Excludes bot authors
- Generates auto-changelog on release

## Stale Management Workflow

File: `workflows/stale.yml`
- Issues: 60 days → stale, 67 days → close
- PRs: 30 days → stale, 37 days → close
- Exempts: pinned, security, PRD, milestones, assignees
EOF
```

---

## Troubleshooting

### Issue: Release Notes Not Categorized

**Symptoms**: Release notes show "Uncategorized" or missing categories

**Diagnosis**:
1. Check PR labels (release notes are generated from merged PRs)
2. Verify label names match `release.yml` exactly
3. Confirm release was created after PRs merged

**Resolution**:
```bash
# List PRs in release
gh pr list --state merged --search "merged:>2025-12-01"

# Check PR labels
gh pr view <pr-number> --json labels --jq '.labels[].name'

# Verify label exists in release.yml categories
grep "<label-name>" .github/release.yml

# Re-create release if needed
gh release delete v1.0.0 --yes
gh release create v1.0.0 --generate-notes
```

### Issue: Stale Workflow Not Running

**Symptoms**: No stale issues/PRs marked, workflow shows no recent runs

**Diagnosis**:
1. Check workflow syntax (YAML errors prevent scheduling)
2. Verify cron schedule format
3. Check GitHub Actions status
4. Review workflow runs history

**Resolution**:
```bash
# Validate YAML syntax
yamllint .github/workflows/stale.yml

# Verify cron schedule
# Visit: https://crontab.guru/#17_3_*_*_*
# Should show: "At 03:17 every day"

# Manually trigger workflow
gh workflow run stale.yml

# Check workflow status
gh run list --workflow=stale.yml --limit 5

# View logs for errors
gh run view <run-id> --log
```

### Issue: Critical Issues Marked Stale

**Symptoms**: Security or pinned issues incorrectly marked stale

**Diagnosis**:
1. Verify exempt labels are correct
2. Check if label was added BEFORE stale check
3. Review exempt-all-milestones/assignees settings

**Resolution**:
```bash
# Add exempt label
gh issue edit <issue-number> --add-label "security"

# Remove stale label
gh issue edit <issue-number> --remove-label "stale"

# Verify exemption in workflow config
grep "exempt-issue-labels" .github/workflows/stale.yml
# Should include: 'pinned,security,PRD'
```

### Issue: Stale Messages Too Aggressive

**Symptoms**: Users complain about stale bot tone

**Resolution**:
Edit `stale-issue-message` and `close-issue-message` in `stale.yml` to be more friendly:

```yaml
stale-issue-message: |
  👋 Hi there! This issue hasn't had activity in 60 days.

  If it's still relevant, please comment to let us know. Otherwise, we'll
  close it in 7 days to keep our backlog manageable.

  Thanks for your contribution to flowspec!
```

---

## Acceptance Criteria Validation

Before marking task complete, verify all ACs:

- [ ] **AC #1**: release.yml categorizes PRs by label for changelog generation
  - File: `.github/release.yml`
  - Categories: Breaking Changes, Features, Bug Fixes, Documentation, Dependencies, Infrastructure, Security, Other

- [ ] **AC #2**: Bot authors excluded from release notes
  - Excluded: renovate, renovate[bot], github-actions[bot], dependabot[bot]
  - Verify in `release.yml` exclude section

- [ ] **AC #3**: stale.yml workflow runs on daily schedule
  - File: `.github/workflows/stale.yml`
  - Trigger: `schedule: - cron: '17 3 * * *'`
  - Also: `workflow_dispatch` for manual runs

- [ ] **AC #4**: Issues marked stale after 60 days, closed after 67 days
  - Config: `days-before-issue-stale: 60`, `days-before-issue-close: 7`
  - Total: 67 days

- [ ] **AC #5**: PRs marked stale after 30 days, closed after 37 days
  - Config: `days-before-pr-stale: 30`, `days-before-pr-close: 7`
  - Total: 37 days

- [ ] **AC #6**: Security and pinned labels exempt from stale automation
  - Issues: `exempt-issue-labels: 'pinned,security,PRD'`
  - PRs: `exempt-pr-labels: 'pinned,security,work-in-progress'`

- [ ] **AC #7**: Action versions pinned with full commit SHA
  - Verify: `actions/stale@<40-char-sha>`
  - Command: `grep "actions/stale@" .github/workflows/stale.yml`

---

## Files Created

| File | Purpose | Template Location |
|------|---------|-------------------|
| `.github/release.yml` | Release notes config | `templates/github/release.yml` |
| `.github/workflows/stale.yml` | Stale management workflow | `templates/github/workflows/stale.yml` |

---

## References

- **Platform Design**: [task-437-github-workflows-platform.md](./task-437-github-workflows-platform.md) (Section 3.1, 3.3, 4.2)
- **Parent Task**: task-437
- **Dependency**: task-437.03 (labeler configuration)
- **GitHub Docs**: [Release Notes](https://docs.github.com/en/repositories/releasing-projects-on-github/automatically-generated-release-notes)
- **Stale Action**: [actions/stale](https://github.com/actions/stale)

---

**Implementation Checklist**:
- [ ] Phase 1: release.yml created with categories
- [ ] Phase 2: stale.yml workflow created with pinned SHA
- [ ] Phase 3: Testing completed (release notes + stale dry-run)
- [ ] Phase 4: Security validation passed
- [ ] Phase 5: All labels created in repository
- [ ] Phase 6: Templates copied for reuse
- [ ] All acceptance criteria validated
