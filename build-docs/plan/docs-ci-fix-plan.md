# Documentation CI Fix Plan

**Date**: 2025-12-16
**Status**: Ready for Implementation
**Priority**: CRITICAL
**Decision Log**: `docs/decisions/docs-ci-fix-2025-12-16.jsonl`

## Executive Summary

The documentation deployment CI has been failing since December 14, 2025. This plan outlines the root cause, fixes, and resilience improvements to ensure this never happens again.

## Root Cause Analysis

### What Happened

1. **Breaking Commit**: `b2ea519` on 2025-12-14 ("refactor(docs): flatten build-docs/building/ and update test paths")
2. **False Claim**: Commit message stated "No files deleted - all content preserved and reorganized"
3. **Actual Result**: Deleted `docs/docfx.json` and reorganized docs into three separate directories

### Error Message
```
jq: error: Could not open file docs/docfx.json: No such file or directory
##[error]Process completed with exit code 2
```

### Impact Timeline
| Date | Runs | Failures | Skipped |
|------|------|----------|---------|
| Dec 14-16 | 50+ | 7 | ~43 |

### Current Directory Structure (Broken)
```
flowspec/
├── user-docs/           # User content (index.md, guides/)
├── build-docs/          # Dev docs + DocFX config (docfx.json, toc.yml)
└── docs/                # Leftover files (adr/, decisions/)
```

### Expected Structure (by docs.yml)
```
flowspec/
└── docs/
    ├── docfx.json       # <-- MISSING
    ├── toc.yml          # <-- MISSING
    ├── index.md
    └── guides/
```

## Fix Implementation

### Phase 1: Immediate Fix (Unblock CI)

**Option Selected**: Consolidate DocFX structure to `user-docs/`

#### Step 1.1: Move DocFX Config
```bash
mv build-docs/docfx.json user-docs/
mv build-docs/toc.yml user-docs/
```

#### Step 1.2: Update toc.yml Paths
The toc.yml references files like `guides/backlog-quickstart.md` but the actual path is `user-guides/backlog-quickstart.md`. Update paths to match actual structure.

#### Step 1.3: Update docs.yml Workflow
Change all `docs/` references to `user-docs/`:

```yaml
# Line 101-110: Inject version step
- name: Inject version into docfx.json
  env:
    VERSION: ${{ steps.version.outputs.version }}
  run: |
    jq --arg ver "$VERSION" '.build.globalMetadata._appVersion = $ver' user-docs/docfx.json > user-docs/docfx.json.tmp
    mv user-docs/docfx.json.tmp user-docs/docfx.json
    jq --arg footer "Flowspec v$VERSION - Specification-driven development for AI-augmented teams" \
      '.build.globalMetadata._appFooter = $footer' user-docs/docfx.json > user-docs/docfx.json.tmp
    mv user-docs/docfx.json.tmp user-docs/docfx.json
    echo "Updated docfx.json with version $VERSION:"
    jq '.build.globalMetadata' user-docs/docfx.json

# Line 121-123: Build step
- name: Build with DocFX
  run: |
    cd user-docs
    docfx docfx.json

# Line 134: Upload artifact
- name: Upload artifact
  uses: actions/upload-pages-artifact@v3
  with:
    path: 'user-docs/_site'
```

### Phase 2: Resilience Improvements

#### Step 2.1: Add Prerequisite Validation
Add new step before version injection:

```yaml
- name: Validate documentation structure
  run: |
    echo "Validating documentation prerequisites..."
    ERRORS=0

    # Check required files
    for file in user-docs/docfx.json user-docs/toc.yml user-docs/index.md; do
      if [ ! -f "$file" ]; then
        echo "::error::Required file missing: $file"
        ERRORS=$((ERRORS + 1))
      else
        echo "Found: $file"
      fi
    done

    # Check jq is available
    if ! command -v jq &> /dev/null; then
      echo "::error::jq is not installed"
      ERRORS=$((ERRORS + 1))
    fi

    # Validate JSON syntax
    if [ -f "user-docs/docfx.json" ]; then
      if ! jq empty user-docs/docfx.json 2>/dev/null; then
        echo "::error::docfx.json contains invalid JSON"
        ERRORS=$((ERRORS + 1))
      fi
    fi

    if [ $ERRORS -gt 0 ]; then
      echo "::error::$ERRORS prerequisite errors found. See above for details."
      exit 1
    fi

    echo "All prerequisites validated successfully"
```

#### Step 2.2: Add Self-Healing Fallback
```yaml
- name: Ensure docfx.json exists
  run: |
    if [ ! -f "user-docs/docfx.json" ]; then
      echo "::warning::docfx.json not found, checking fallback locations..."
      if [ -f "build-docs/docfx.json" ]; then
        echo "Found docfx.json in build-docs/, copying..."
        cp build-docs/docfx.json user-docs/
      elif [ -f "templates/docfx.json" ]; then
        echo "Found docfx.json in templates/, copying..."
        cp templates/docfx.json user-docs/
      else
        echo "::error::No docfx.json found in any location"
        exit 1
      fi
    fi
```

### Phase 3: Alerting & Monitoring

#### Step 3.1: Add Failure Notification Job
```yaml
notify-failure:
  runs-on: ubuntu-latest
  needs: [build, deploy]
  if: failure()
  permissions:
    issues: write
    contents: read
  steps:
    - name: Create failure issue
      env:
        GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        RUN_URL: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
        RUN_ID: ${{ github.run_id }}
      run: |
        ISSUE_TITLE="[CI] Documentation deployment failed - Run #$RUN_ID"
        ISSUE_BODY="## Documentation Deployment Failed

        **Run**: [#$RUN_ID]($RUN_URL)
        **Trigger**: ${{ github.event_name }}
        **Branch**: ${{ github.ref_name }}
        **Time**: $(date -u +%Y-%m-%dT%H:%M:%SZ)

        ### Action Required
        1. Check the [workflow run]($RUN_URL) for error details
        2. Verify \`user-docs/docfx.json\` exists
        3. Ensure all toc.yml references are valid

        /cc @jpoley"

        # Check if issue already exists
        EXISTING=$(gh issue list --repo ${{ github.repository }} --label ci-failure --state open --search "Documentation deployment failed" --json number --jq '.[0].number')

        if [ -n "$EXISTING" ]; then
          echo "Updating existing issue #$EXISTING"
          gh issue comment "$EXISTING" --body "$ISSUE_BODY"
        else
          echo "Creating new issue"
          gh issue create --title "$ISSUE_TITLE" --body "$ISSUE_BODY" --label "ci-failure,documentation,priority:critical"
        fi
```

### Phase 4: Prevention

#### Step 4.1: Update CODEOWNERS
```
# .github/CODEOWNERS
# Documentation deployment protection
.github/workflows/docs.yml @jpoley
user-docs/docfx.json @jpoley
user-docs/toc.yml @jpoley
```

#### Step 4.2: Add PR Validation Workflow
Create `.github/workflows/docs-validate.yml`:
```yaml
name: Validate Documentation Structure

on:
  pull_request:
    paths:
      - 'user-docs/**'
      - 'build-docs/**'
      - '.github/workflows/docs*.yml'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate DocFX structure
        run: |
          echo "Checking documentation structure..."

          # Required files
          REQUIRED_FILES=(
            "user-docs/docfx.json"
            "user-docs/toc.yml"
            "user-docs/index.md"
          )

          for file in "${REQUIRED_FILES[@]}"; do
            if [ ! -f "$file" ]; then
              echo "::error::Required file missing: $file"
              exit 1
            fi
          done

          # Validate JSON
          jq empty user-docs/docfx.json || {
            echo "::error::docfx.json is invalid JSON"
            exit 1
          }

          # Validate YAML
          python3 -c "import yaml; yaml.safe_load(open('user-docs/toc.yml'))" || {
            echo "::error::toc.yml is invalid YAML"
            exit 1
          }

          echo "Documentation structure validated successfully"
```

## Implementation Checklist

- [ ] **Phase 1**: Immediate Fix
  - [ ] Move `build-docs/docfx.json` to `user-docs/`
  - [ ] Move `build-docs/toc.yml` to `user-docs/`
  - [ ] Update path references in `toc.yml`
  - [ ] Update `.github/workflows/docs.yml` paths
  - [ ] Test locally with `docfx serve`

- [ ] **Phase 2**: Resilience
  - [ ] Add prerequisite validation step
  - [ ] Add self-healing fallback step
  - [ ] Add JSON/YAML validation

- [ ] **Phase 3**: Alerting
  - [ ] Add `notify-failure` job
  - [ ] Create `ci-failure` label in GitHub
  - [ ] Test failure notification

- [ ] **Phase 4**: Prevention
  - [ ] Update `.github/CODEOWNERS`
  - [ ] Create `docs-validate.yml` workflow
  - [ ] Document in CLAUDE.md

## Success Criteria

1. Documentation deploys successfully on next release
2. Failures create GitHub issues automatically
3. PR validation catches missing files before merge
4. CODEOWNERS prevents accidental deletion

## Rollback Plan

If issues persist after fix:
1. Revert to last known good state: `git show 122ede4:docs/docfx.json > user-docs/docfx.json`
2. Temporarily disable workflow with `if: false` condition
3. Manual deployment via `workflow_dispatch` with explicit version

---

*Generated by Claude Code - 2025-12-16*
