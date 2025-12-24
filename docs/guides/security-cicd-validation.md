# Security CI/CD Validation Guide

This guide provides validation procedures for security scanning workflows.

## Quick Validation

### 1. Files in Place

Verify all required files are present:

```bash
# Check workflow files
ls -la .github/workflows/security*.yml

# Check configuration
ls -la .github/security-config.yml

# Expected files:
# - .github/workflows/security-scan.yml (reusable workflow)
# - .github/workflows/security.yml (entry point)
# - .github/security-config.yml (configuration)
```

### 2. Template Variables Replaced

Ensure all `{{PROJECT_NAME}}` placeholders are replaced:

```bash
# Check for unreplaced variables
grep -r "{{PROJECT_NAME}}" .github/workflows/

# Should return no results
```

### 3. Permissions Set

Verify workflows have required permissions:

```bash
# Check security-scan.yml permissions
grep -A5 "permissions:" .github/workflows/security-scan.yml

# Required permissions:
# - contents: read
# - security-events: write
# - pull-requests: write
```

### 4. Workflow Syntax Valid

Validate YAML syntax:

```bash
# Install actionlint if needed
brew install actionlint  # macOS
# or
sudo apt install actionlint  # Linux

# Validate workflows
actionlint .github/workflows/security-scan.yml
actionlint .github/workflows/security.yml
```

## Functional Testing

### Test 1: Manual Trigger

```bash
# Trigger security scan manually
gh workflow run security.yml

# View run status
gh run list --workflow=security.yml

# View logs
gh run view --log
```

**Expected:** Workflow completes successfully, SARIF uploaded

### Test 2: Pull Request Trigger

```bash
# Create test branch
git checkout -b test-security-scan
echo "# Test change" >> README.md
git add README.md
git commit -m "test: trigger security scan"
git push origin test-security-scan

# Create PR
gh pr create --title "Test Security Scan" --body "Testing workflow"

# Check PR status
gh pr checks
```

**Expected:**
- Security workflow runs automatically
- PR comment posted with scan summary
- Workflow status shows in PR checks

### Test 3: Scheduled Run

```bash
# Check scheduled runs (if schedule is configured)
gh run list --workflow=security.yml --event=schedule
```

**Expected:** Scheduled runs occur at configured intervals

### Test 4: SARIF Upload

```bash
# Check Security tab via API
gh api repos/:owner/:repo/code-scanning/analyses

# Or visit Security tab in GitHub UI
# Repository -> Security -> Code scanning alerts
```

**Expected:** Scan results visible in Security tab

### Test 5: Artifacts

```bash
# Download artifacts from latest run
run_id="$(gh run list --workflow=security.yml --limit=1 --json databaseId -q '.[0].databaseId')"
if [ -z "$run_id" ] || [ "$run_id" = "null" ]; then
  echo "No completed security.yml runs found to download artifacts from."
  exit 1
fi
gh run download "$run_id"

# Check SARIF file exists
ls -la security-scan-results-*/security-results.sarif
```

**Expected:** SARIF file downloaded and valid JSON

## Performance Validation

### Scan Time Benchmarks

| Project Size | Expected Time |
|--------------|---------------|
| < 10K LOC | 1-2 minutes |
| 10K-100K LOC | 3-5 minutes |
| 100K-500K LOC | 5-10 minutes |
| > 500K LOC | Use parallel scanning |

### Cache Effectiveness

```bash
# First run (no cache)
gh workflow run security.yml
# Note the duration

# Second run (with cache)
gh workflow run security.yml
# Should be ~20% faster due to Semgrep binary caching
```

## Configuration Validation

### Severity Threshold

Test different severity levels:

```bash
# Test with critical (default)
gh workflow run security.yml -f fail-on=critical

# Test with high
gh workflow run security.yml -f fail-on=high

# Test with medium
gh workflow run security.yml -f fail-on=medium
```

### Custom Scan Path

```bash
# Scan specific directory
gh workflow run security.yml -f scan-path=src/

# Verify in logs
gh run view --log | grep "Running security scan on:"
```

## Integration Validation

### With Branch Protection

1. Enable branch protection for main:
   - Settings → Branches → Add rule
   - Branch name pattern: `main`
   - Require status checks: `Security Scan`

2. Create PR that should fail:
   ```bash
   # Add intentional finding, create PR
   # PR should be blocked until scan passes
   ```

### With CODEOWNERS

```bash
# Create .github/CODEOWNERS if not exists
echo "/.github/workflows/security*.yml @security-team" > .github/CODEOWNERS

# Verify changes to security workflows require security team review
```

## Troubleshooting Checklist

- [ ] Workflow files have no syntax errors (actionlint passes)
- [ ] Template variables replaced (no `{{...}}` remaining)
- [ ] Permissions set correctly (security-events, pull-requests)
- [ ] flowspec-cli installs successfully in workflow
- [ ] Semgrep installs successfully in workflow
- [ ] SARIF file generated (check artifacts)
- [ ] SARIF uploads to Security tab (check API/UI)
- [ ] PR comments posted (check PR thread)
- [ ] Caching works (subsequent runs faster)
- [ ] Manual dispatch accepts inputs
- [ ] Scheduled runs occur (if configured)

## Success Criteria

The security CI/CD pipeline is validated when:

1. ✅ Workflows run on every PR to main
2. ✅ SARIF results visible in Security tab
3. ✅ PR comments posted with scan summaries
4. ✅ Scan completes within expected time
5. ✅ Artifacts uploaded and downloadable
6. ✅ Severity thresholds respected
7. ✅ Caching improves performance
8. ✅ Manual triggers work with custom inputs

## Next Steps

After validation:

1. **Production rollout**: Enable on main branch
2. **Team training**: Train on `/flow:security` commands
3. **Monitoring**: Track scan metrics (time, findings, fixes)
4. **Runbooks**: Document triage and remediation processes
5. **Continuous improvement**: Tune rules, add custom checks

## References

- [Security CI/CD Setup Guide](security-cicd-setup.md)
- [GitHub Actions Documentation](https://docs.github.com/actions)
- [SARIF Specification](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)
