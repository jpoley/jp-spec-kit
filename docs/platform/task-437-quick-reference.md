# Task-437 Quick Reference: GitHub Workflows Platform

**Quick access checklist for implementing GitHub project automation features.**

---

## Action SHA Lookup Commands

Run these before implementation to get current SHAs:

```bash
# actions/checkout (currently v4.1.1)
gh api repos/actions/checkout/commits/v4.1.1 --jq .sha

# actions/labeler (currently v5.0.0)
gh api repos/actions/labeler/commits/v5.0.0 --jq .sha

# actions/stale (currently v9.0.0)
gh api repos/actions/stale/commits/v9.0.0 --jq .sha

# actions/upload-artifact (currently v4.3.0)
gh api repos/actions/upload-artifact/commits/v4.3.0 --jq .sha

# ossf/scorecard-action (currently v2.3.1)
gh api repos/ossf/scorecard-action/commits/v2.3.1 --jq .sha

# github/codeql-action (currently v3.23.0)
gh api repos/github/codeql-action/commits/v3.23.0 --jq .sha
```

**Record SHAs in**: Implementation guides before creating workflows.

---

## Files to Create

### task-437.03: CODEOWNERS + Labeler
- [ ] `.github/CODEOWNERS`
- [ ] `.github/labeler.yml`
- [ ] `.github/workflows/labeler.yml`

### task-437.04: Release Notes + Stale
- [ ] `.github/release.yml`
- [ ] `.github/workflows/stale.yml`

### task-437.05: OpenSSF Scorecard
- [ ] `.github/workflows/scorecard.yml`
- [ ] `README.md` (add badge)

### All Tasks: Templates
- [ ] `templates/github/CODEOWNERS`
- [ ] `templates/github/labeler.yml`
- [ ] `templates/github/workflows/labeler.yml`
- [ ] `templates/github/release.yml`
- [ ] `templates/github/workflows/stale.yml`
- [ ] `templates/github/workflows/scorecard.yml.template`
- [ ] `templates/github/README.md`

---

## Labels to Create

Run once before task-437.04:

```bash
# Release note categories
gh label create "breaking-change" --color "b60205" --description "Breaking API change" || true
gh label create "feature" --color "0e8a16" --description "New feature or enhancement" || true
gh label create "enhancement" --color "0e8a16" --description "Enhancement to existing feature" || true
gh label create "bug" --color "d73a4a" --description "Bug fix" || true
gh label create "fix" --color "d73a4a" --description "Bug fix (alternate)" || true
gh label create "security" --color "ee0701" --description "Security vulnerability or fix" || true
gh label create "vulnerability" --color "ee0701" --description "Security vulnerability" || true

# Stale management
gh label create "stale" --color "eeeeee" --description "Marked stale due to inactivity" || true
gh label create "pinned" --color "0052cc" --description "Never mark as stale" || true
gh label create "PRD" --color "5319e7" --description "Product requirements document" || true
gh label create "work-in-progress" --color "fbca04" --description "PR actively being worked on" || true

# Exclusions
gh label create "skip-changelog" --color "cccccc" --description "Exclude from release notes" || true
gh label create "duplicate" --color "cccccc" --description "Duplicate issue/PR" || true
gh label create "invalid" --color "cccccc" --description "Invalid issue/PR" || true
gh label create "wontfix" --color "cccccc" --description "Won't be fixed" || true
```

---

## Security Validation Commands

### Verify Action SHA Pinning
```bash
# Check all workflows for unpinned actions
grep -r "uses:" .github/workflows/ | grep -v "@[a-f0-9]\{40\}"
# Should return empty (all pinned)

# Verify specific workflow
grep "uses:" .github/workflows/scorecard.yml
# Every line should have 40-character SHA
```

### Verify Permissions
```bash
# Check for overly permissive workflows
grep -r "permissions:" .github/workflows/ -A5 | grep "write-all"
# Should return empty (no write-all grants)
```

### Verify Cron Schedules
```bash
# Check for :00 minute cron times (avoid)
grep -r "cron:" .github/workflows/
# Should show non-zero minutes (:17, :30)
```

---

## Testing Commands

### Test Labeler
```bash
# Create test PR
git checkout -b test-labeler
echo "# Test" >> docs/test.md
echo "# Test" >> src/test.py
git add -A
git commit -m "test: labeler workflow"
git push -u origin test-labeler
gh pr create --draft --title "Test: Labeler" --body "Testing labels"

# Verify labels applied
gh pr view --json labels --jq '.labels[].name'
# Should show: documentation, source

# Clean up
gh pr close --delete-branch
```

### Test Stale Workflow
```bash
# Manual trigger
gh workflow run stale.yml

# Check status
gh run list --workflow=stale.yml --limit 1

# View logs
gh run view --log
```

### Test Scorecard
```bash
# Manual trigger
gh workflow run scorecard.yml

# Wait for completion
gh run watch

# Check SARIF upload
# Visit: https://github.com/jpoley/flowspec/security/code-scanning

# Check badge
# Visit: https://scorecard.dev/viewer/?uri=github.com/jpoley/flowspec
```

### Test Release Notes
```bash
# Create test release
gh release create v0.1.0-test --title "Test" --notes "Test release notes"

# View release
gh release view v0.1.0-test

# Clean up
gh release delete v0.1.0-test --yes
```

---

## Workflow Status Commands

```bash
# List all workflow runs
gh run list --limit 10

# Check specific workflow
gh run list --workflow=scorecard.yml --limit 5

# View workflow details
gh run view <run-id>

# View workflow logs
gh run view <run-id> --log

# Re-run failed workflow
gh run rerun <run-id>

# Watch workflow in real-time
gh run watch
```

---

## SARIF Commands

```bash
# Download SARIF artifact
gh run download <run-id> --name "SARIF file"

# Validate SARIF structure
jq . results.sarif

# Check SARIF category
jq '.runs[0].tool.driver.name' results.sarif

# Count findings
jq '.runs[0].results | length' results.sarif

# List finding severities
jq '.runs[0].results[].level' results.sarif | sort | uniq -c
```

---

## Scorecard Commands

```bash
# View Scorecard results
# Visit: https://scorecard.dev/viewer/?uri=github.com/jpoley/flowspec

# Check badge URL
curl -I https://api.scorecard.dev/projects/github.com/jpoley/flowspec/badge

# Download JSON results (if published)
curl https://api.scorecard.dev/projects/github.com/jpoley/flowspec
```

---

## Troubleshooting Quick Fixes

### Labeler Not Working
```bash
# Validate YAML
yamllint .github/workflows/labeler.yml
yamllint .github/labeler.yml

# Check permissions
grep -A5 "permissions:" .github/workflows/labeler.yml
```

### Stale Workflow Not Running
```bash
# Verify cron syntax
# Visit: https://crontab.guru/#17_3_*_*_*

# Manual trigger
gh workflow run stale.yml
```

### SARIF Not in Security Tab
```bash
# Check upload step succeeded
gh run view <run-id> --log | grep "upload-sarif"

# Verify SARIF category unique
jq '.runs[0].tool.driver.name' results.sarif
```

### Scorecard Badge Shows "No Data"
```bash
# Check publish_results setting
grep "publish_results" .github/workflows/scorecard.yml
# Should be: true

# Wait 10-15 minutes, then refresh
```

---

## Documentation Links

- **Platform Architecture**: [task-437-github-workflows-platform.md](./task-437-github-workflows-platform.md)
- **Implementation Summary**: [task-437-implementation-summary.md](./task-437-implementation-summary.md)
- **Implementation Guides**:
  - [task-437.03: CODEOWNERS + Labeler](./task-437.03-implementation-guide.md)
  - [task-437.04: Release Notes + Stale](./task-437.04-implementation-guide.md)
  - [task-437.05: OpenSSF Scorecard](./task-437.05-implementation-guide.md)

---

## Expected Outcomes

### After task-437.03
- ✅ PRs auto-labeled based on file paths
- ✅ Reviewers auto-assigned via CODEOWNERS
- ✅ Workflow completes in < 30 seconds

### After task-437.04
- ✅ Release notes auto-generated with categories
- ✅ Stale issues/PRs marked automatically
- ✅ No critical items marked stale (exemptions work)

### After task-437.05
- ✅ Scorecard workflow runs weekly
- ✅ SARIF uploaded to Security tab
- ✅ Badge displays score (6.5-7.5 initially)
- ✅ Score improvement plan identified

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Workflow Success Rate | 98%+ | `gh run list --json conclusion` |
| Mean Time to Label | < 30s | PR creation to label applied |
| Stale Issue Ratio | < 10% | Stale issues / total open |
| Scorecard Score | 8.0+ | scorecard.dev viewer |
| Action SHA Pinning | 100% | `grep "uses:" .github/workflows/` |

---

**Quick Reference Complete** ✅

For detailed instructions, see implementation guides.
For architecture details, see platform design document.
