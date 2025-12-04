# Galway GitHub Actions Workflow Specifications

**Status**: Platform Design
**Owner**: Platform Engineer
**Last Updated**: 2025-12-04

## Executive Summary

This document defines reusable GitHub Actions workflows for galway host tasks, implementing CI/CD best practices with matrix testing, security scanning, and automated archival.

## Workflow Architecture

### Workflow Categories

```
┌────────────────────────────────────────────────────────────┐
│                  GitHub Actions Workflows                   │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   PR CI     │  │  Scheduled  │  │   Manual    │        │
│  │  (Validate) │  │ (Maintenance)│  │  (On-demand)│        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │
│         ▼                ▼                ▼                │
│  ┌─────────────────────────────────────────────┐           │
│  │         Reusable Workflows                  │           │
│  │  • matrix-test.yml                          │           │
│  │  • security-scan.yml (exists)               │           │
│  │  • build-publish.yml                        │           │
│  └─────────────────────────────────────────────┘           │
└────────────────────────────────────────────────────────────┘
```

## Matrix Testing Workflow (task-168)

### Reusable Workflow

**File**: `.github/workflows/matrix-test.yml`

```yaml
name: Matrix Test (Reusable)

on:
  workflow_call:
    inputs:
      python-versions:
        description: 'JSON array of Python versions to test'
        type: string
        default: '["3.11", "3.12"]'
      os-matrix:
        description: 'JSON array of operating systems'
        type: string
        default: '["ubuntu-latest", "macos-14"]'
      test-command:
        description: 'Test command to run'
        type: string
        default: 'uv run pytest tests/ -v --cov'
      fail-fast:
        description: 'Fail fast on first error'
        type: boolean
        default: false
    outputs:
      test-results:
        description: 'Summary of test results'
        value: ${{ jobs.test.outputs.summary }}

jobs:
  test:
    name: Test on ${{ matrix.os }} with Python ${{ matrix.python-version }}
    runs-on: ${{ matrix.os }}

    strategy:
      fail-fast: ${{ inputs.fail-fast }}
      matrix:
        os: ${{ fromJSON(inputs.os-matrix) }}
        python-version: ${{ fromJSON(inputs.python-versions) }}

    outputs:
      summary: ${{ steps.results.outputs.summary }}

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Cache uv dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/uv
          key: uv-${{ matrix.os }}-py${{ matrix.python-version }}-${{ hashFiles('pyproject.toml', 'uv.lock') }}
          restore-keys: |
            uv-${{ matrix.os }}-py${{ matrix.python-version }}-
            uv-${{ matrix.os }}-

      - name: Install dependencies
        run: uv sync

      - name: Run tests
        id: test
        run: |
          ${{ inputs.test-command }}
        continue-on-error: true

      - name: Collect test results
        id: results
        if: always()
        run: |
          if [ ${{ steps.test.outcome }} == 'success' ]; then
            echo "summary=✅ Tests passed on ${{ matrix.os }} Python ${{ matrix.python-version }}" >> $GITHUB_OUTPUT
          else
            echo "summary=❌ Tests failed on ${{ matrix.os }} Python ${{ matrix.python-version }}" >> $GITHUB_OUTPUT
          fi

      - name: Upload coverage
        if: always()
        uses: codecov/codecov-action@v4
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          flags: ${{ matrix.os }}-py${{ matrix.python-version }}
          name: ${{ matrix.os }}-py${{ matrix.python-version }}

      - name: Upload test artifacts
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: test-results-${{ matrix.os }}-py${{ matrix.python-version }}
          path: |
            .coverage
            htmlcov/
            test-results.xml
```

### Usage Example

**In main CI workflow** (`.github/workflows/ci.yml`):
```yaml
name: CI

on:
  pull_request:
  push:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - uses: astral-sh/setup-uv@v4
      - run: uv sync
      - run: uv run ruff format --check .
      - run: uv run ruff check .

  matrix-test:
    uses: ./.github/workflows/matrix-test.yml
    with:
      python-versions: '["3.11", "3.12"]'
      os-matrix: '["ubuntu-latest", "macos-14"]'
      test-command: 'uv run pytest tests/ -v --cov --cov-report=xml'
    secrets: inherit

  security:
    uses: ./.github/workflows/security-scan.yml
    with:
      scan-type: incremental
      fail-on: critical,high
    permissions:
      contents: read
      security-events: write
      pull-requests: write
```

### macOS-Specific Considerations

**macOS 14 (M1/M2)**:
- Uses Apple Silicon (ARM64)
- Faster than macOS 13 (Intel)
- May have different behavior for native extensions

**Test Coverage**:
- Keyring integration (macOS Keychain)
- File path handling (case sensitivity)
- Terminal capabilities (readline, colors)

## Backlog Archive Workflow (task-282)

**File**: `.github/workflows/backlog-archive.yml`

```yaml
name: Archive Done Tasks

on:
  schedule:
    # Run every Sunday at midnight UTC
    - cron: '0 0 * * 0'

  workflow_dispatch:
    inputs:
      days-threshold:
        description: 'Archive tasks older than N days'
        required: false
        default: '7'
        type: choice
        options:
          - '7'
          - '14'
          - '30'
      dry-run:
        description: 'Dry run (no changes)'
        type: boolean
        default: false
      filter-states:
        description: 'States to archive (comma-separated)'
        required: false
        default: 'Done'

jobs:
  archive:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install backlog CLI
        run: |
          pip install uv
          uv tool install backlog-md

      - name: Configure Git
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"

      - name: Run archive script
        env:
          DAYS_THRESHOLD: ${{ inputs.days-threshold || '7' }}
          DRY_RUN: ${{ inputs.dry-run || 'false' }}
          FILTER_STATE: ${{ inputs.filter-states || 'Done' }}
        run: |
          chmod +x scripts/bash/archive-tasks.sh
          ./scripts/bash/archive-tasks.sh

      - name: Create archive summary
        if: always()
        run: |
          cat > archive-summary.md <<EOF
          # Archive Summary

          - **Threshold**: ${{ inputs.days-threshold || 7 }} days
          - **Filter**: ${{ inputs.filter-states || 'Done' }}
          - **Dry Run**: ${{ inputs.dry-run || false }}
          - **Date**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")

          ## Changed Files
          \`\`\`
          $(git status --porcelain)
          \`\`\`
          EOF

      - name: Commit and push changes
        if: ${{ !inputs.dry-run }}
        run: |
          if [ -n "$(git status --porcelain)" ]; then
            git add backlog/
            git commit -s -m "chore(backlog): archive Done tasks older than ${{ inputs.days-threshold || 7 }} days [skip ci]"
            git push
            echo "✅ Changes committed and pushed"
          else
            echo "ℹ️ No changes to commit"
          fi

      - name: Upload archive summary
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: archive-summary-${{ github.run_id }}
          path: archive-summary.md

      - name: Comment on trigger issue
        if: github.event_name == 'workflow_dispatch' && github.event.issue
        uses: actions/github-script@v7
        with:
          script: |
            const summary = require('fs').readFileSync('archive-summary.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: summary
            });
```

## Stale Task Detection Workflow (task-285)

**File**: `.github/workflows/stale-check.yml`

```yaml
name: Stale Task Detection

on:
  pull_request:
    types: [opened, synchronize, reopened]
  push:
    branches: [main]
  schedule:
    # Run daily at 9am UTC
    - cron: '0 9 * * *'

jobs:
  check-stale-tasks:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      issues: write
      pull-requests: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install backlog CLI
        run: |
          pip install uv
          uv tool install backlog-md

      - name: Run stale check script
        id: stale-check
        run: |
          chmod +x scripts/ci/check-stale-tasks.sh
          OUTPUT=$(./scripts/ci/check-stale-tasks.sh 2>&1)
          echo "output<<EOF" >> $GITHUB_OUTPUT
          echo "$OUTPUT" >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT
        continue-on-error: true

      - name: Parse stale tasks
        id: parse
        run: |
          STALE_COUNT=$(echo "${{ steps.stale-check.outputs.output }}" | grep -oP 'Found \K\d+' || echo "0")
          echo "stale_count=$STALE_COUNT" >> $GITHUB_OUTPUT

      - name: Comment on PR
        if: github.event_name == 'pull_request' && steps.parse.outputs.stale_count != '0'
        uses: actions/github-script@v7
        with:
          script: |
            const staleCount = ${{ steps.parse.outputs.stale_count }};
            const comment = `## ℹ️ Stale Task Notification

            Found **${staleCount}** Done task(s) older than 7 days.

            Consider running the archive workflow:
            \`\`\`bash
            # Manual archive
            ./scripts/bash/archive-tasks.sh

            # Or trigger GitHub Actions workflow
            gh workflow run backlog-archive.yml
            \`\`\`

            <details>
            <summary>Full output</summary>

            \`\`\`
            ${{ steps.stale-check.outputs.output }}
            \`\`\`
            </details>`;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });

      - name: Create tracking issue
        if: github.event_name == 'schedule' && steps.parse.outputs.stale_count != '0'
        uses: actions/github-script@v7
        with:
          script: |
            const staleCount = ${{ steps.parse.outputs.stale_count }};
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `Stale tasks detected: ${staleCount} tasks older than 7 days`,
              body: `**Automated stale task report**\n\nFound ${staleCount} Done tasks older than 7 days.\n\nRun archive workflow to clean up:\n\`\`\`bash\ngh workflow run backlog-archive.yml\n\`\`\``,
              labels: ['maintenance', 'automated']
            });
```

## Command Validation Workflow (task-278)

**File**: `.github/workflows/validate-commands.yml`

```yaml
name: Validate Command Structure

on:
  pull_request:
    paths:
      - '.claude/commands/**'
  push:
    branches: [main]
    paths:
      - '.claude/commands/**'

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Run validation script
        run: |
          chmod +x scripts/ci/validate-commands.sh
          ./scripts/ci/validate-commands.sh

      - name: Check naming conventions
        run: |
          EXIT_CODE=0
          for file in .claude/commands/*.md; do
            filename=$(basename "$file")
            if [[ ! "$filename" =~ ^[a-z0-9-]+\.md$ ]]; then
              echo "❌ Invalid filename: $filename (must be lowercase-with-hyphens.md)"
              EXIT_CODE=1
            fi
          done
          exit $EXIT_CODE

      - name: Validate YAML frontmatter
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - run: |
          pip install pyyaml
          python scripts/ci/validate-command-frontmatter.py
```

## Build and Publish Workflow

**File**: `.github/workflows/build-publish.yml`

```yaml
name: Build and Publish (Reusable)

on:
  workflow_call:
    inputs:
      publish-pypi:
        type: boolean
        default: false
      publish-docker:
        type: boolean
        default: false
      docker-image:
        type: string
        default: ''
    secrets:
      PYPI_TOKEN:
        required: false
      GITHUB_TOKEN:
        required: true

jobs:
  build-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Build package
        run: uv build

      - name: Generate SBOM
        run: |
          pip install cyclonedx-bom
          cyclonedx-py -o sbom.json --format json

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: python-dist
          path: |
            dist/
            sbom.json

      - name: Publish to PyPI
        if: ${{ inputs.publish-pypi }}
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
        run: |
          pip install twine
          twine upload dist/*

  build-docker:
    if: ${{ inputs.publish-docker }}
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ inputs.docker-image }}
          tags: |
            type=semver,pattern={{version}}
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

## Workflow Best Practices

### Caching Strategy

**uv dependencies**:
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/uv
    key: uv-${{ runner.os }}-${{ hashFiles('pyproject.toml', 'uv.lock') }}
```

**Docker layers**:
```yaml
- uses: docker/build-push-action@v5
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

### Secret Management

**Required Secrets**:
- `PYPI_TOKEN`: PyPI publishing
- `CODECOV_TOKEN`: Coverage uploads
- `COSIGN_PASSWORD`: Image signing

**Access via**:
```yaml
- env:
    API_TOKEN: ${{ secrets.API_TOKEN }}
```

### Matrix Testing Best Practices

**Fast feedback**:
```yaml
strategy:
  fail-fast: true  # Stop on first failure
```

**Comprehensive coverage**:
```yaml
strategy:
  fail-fast: false  # Run all combinations
```

## Success Metrics

**Workflow Performance**:
- **PR validation**: < 5 minutes
- **Full CI**: < 10 minutes
- **Cache hit rate**: > 80%

**Reliability**:
- **Workflow success rate**: > 99%
- **Flaky test rate**: < 1%

## Related Tasks

| Task ID | Title | Workflow |
|---------|-------|----------|
| task-168 | macOS CI Matrix | matrix-test.yml |
| task-282 | Archive Workflow | backlog-archive.yml |
| task-285 | Stale Task Detection | stale-check.yml |
| task-278 | Command Validation | validate-commands.yml |
| task-248 | Security Pipeline | security-scan.yml (exists) |

## Appendix: Workflow Triggers Reference

```yaml
# Pull requests
on:
  pull_request:
    types: [opened, synchronize, reopened]
    paths:
      - 'src/**'  # Only on source changes

# Push to branches
on:
  push:
    branches: [main, develop]

# Scheduled (cron)
on:
  schedule:
    - cron: '0 0 * * 0'  # Sunday midnight

# Manual trigger
on:
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        options: [dev, staging, prod]

# Reusable workflow
on:
  workflow_call:
    inputs:
      param:
        type: string
        required: true
```
