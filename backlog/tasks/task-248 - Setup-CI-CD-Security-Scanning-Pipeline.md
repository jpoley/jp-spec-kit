---
id: task-248
title: Setup CI/CD Security Scanning Pipeline
status: To Do
assignee:
  - '@muckross'
created_date: '2025-12-03 02:26'
updated_date: '2025-12-04 16:32'
labels:
  - 'workflow:Planned'
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Configure GitHub Actions for security scanning integration with /jpspec:security commands. Create reusable workflow that supports incremental scanning, SARIF upload, caching, and parallel execution for large codebases.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create reusable workflow .github/workflows/security-scan.yml
- [ ] #2 Implement SARIF upload to GitHub Security tab with proper permissions
- [ ] #3 Add caching for Semgrep binaries (<50MB) to reduce CI time
- [ ] #4 Configure matrix strategy for parallel scanning (frontend/backend/infra)
- [ ] #5 Add PR comment bot for scan summaries with fix suggestions
- [ ] #6 Test workflow on 3 different project sizes (10K, 50K, 100K LOC)
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Implementation Plan: CI/CD Security Scanning Pipeline

### Overview
Create a reusable GitHub Actions workflow that integrates /jpspec:security commands into CI/CD pipelines with caching, parallel execution, and SARIF upload capabilities.

### Step-by-Step Implementation

#### Step 1: Create Reusable Workflow File
**File**: `.github/workflows/security-scan.yml`
**Duration**: 2 hours

1. Create workflow with `workflow_call` trigger
2. Define inputs:
   - `scan-type`: incremental|full|fast (default: incremental)
   - `fail-on`: critical,high,medium,low (default: critical,high)
   - `upload-sarif`: boolean (default: true)
3. Define outputs:
   - `findings-count`: total findings
   - `critical-count`: critical findings
4. Set timeout to 10 minutes by default

#### Step 2: Implement Job Steps
**Duration**: 3 hours

1. **Checkout** with `fetch-depth: 0` for incremental scanning
2. **Setup Python 3.11** with pip cache
3. **Cache Semgrep binary**:
   - Path: `~/.local/bin/semgrep`
   - Key: `semgrep-${{ runner.os }}-1.50.0`
4. **Install Tools**:
   ```bash
   pip install uv
   uv tool install specify-cli
   pip install semgrep==1.50.0
   ```
5. **Run Security Scan**:
   - Determine baseline commit for incremental mode
   - Execute `specify security scan` with appropriate flags
   - Parse SARIF output with jq for metrics
   - Set outputs for findings count
6. **Upload SARIF**:
   - Use `github/codeql-action/upload-sarif@v3`
   - Set category to `jpspec-security`
   - Add permissions check (security-events: write)
7. **Upload Artifacts**:
   - SARIF file
   - docs/security/*.md and *.json
   - Retention: 90 days
8. **PR Comment**:
   - Use `actions/github-script@v7`
   - Display summary with total/critical counts
   - Add fix instructions in collapsible section

#### Step 3: Add Matrix Strategy Support
**Duration**: 2 hours

1. Create example for parallel scanning by component
2. Document in workflow comments:
   ```yaml
   strategy:
     matrix:
       component: [backend-python, frontend-typescript, infra-terraform]
   ```
3. Show how to scan specific paths per component
4. Document SARIF upload with different categories

#### Step 4: Create Usage Documentation
**Duration**: 1 hour

1. Add workflow header comments with:
   - Input descriptions
   - Output descriptions
   - Usage examples
2. Create `docs/platform/security-cicd-usage.md`:
   - Quick start example
   - Configuration options table
   - Troubleshooting section

#### Step 5: Test on Multiple Project Sizes
**Duration**: 3 hours

1. **Test 1: Small (10K LOC)**
   - Use jp-spec-kit itself
   - Verify scan completes in <1 minute
   - Check cache hit on second run
2. **Test 2: Medium (50K LOC)**
   - Create or use test project
   - Verify scan completes in <3 minutes
   - Test incremental vs. full scan
3. **Test 3: Large (100K LOC)**
   - Use monorepo test case
   - Verify scan completes in <5 minutes
   - Test parallel execution with matrix
4. Document performance results in platform doc

#### Step 6: Add Permissions and Error Handling
**Duration**: 1 hour

1. Document required permissions:
   - `contents: read`
   - `security-events: write`
   - `pull-requests: write`
2. Add error handling:
   - Tool installation failures
   - SARIF upload failures
   - Network timeouts
3. Add fallback behaviors

### Dependencies
- PRD complete (docs/prd/jpspec-security-commands.md) ✓
- Platform design complete (docs/platform/jpspec-security-platform.md) ✓
- `specify security scan` command implementation (task-210)

### Testing Checklist
- [ ] Workflow validates with `actionlint`
- [ ] Cache hit rate >90% on repeated runs
- [ ] SARIF upload succeeds with proper permissions
- [ ] PR comments render correctly
- [ ] Matrix execution completes in parallel
- [ ] Performance budgets met for all project sizes

### Estimated Effort
**Total**: 12 hours (1.5 days)
<!-- SECTION:PLAN:END -->
