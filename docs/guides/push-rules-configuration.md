# Push Rules Configuration Guide

This guide explains how to configure `push-rules.md` to enforce git workflow quality gates before pushing code.

## Overview

`push-rules.md` defines mandatory pre-push checks that must pass before code reaches the remote repository. These rules are enforced by Claude Code hooks and help maintain code quality.

## Quick Start

1. **Generate the file** during project initialization:
   ```bash
   specify init my-project
   ```

2. **Or copy the template** manually:
   ```bash
   cp templates/push-rules-template.md push-rules.md
   ```

3. **Customize** the YAML frontmatter to match your project's needs.

## File Structure

The file uses YAML frontmatter at the top for machine-readable configuration, followed by human-readable documentation:

```markdown
---
version: "1.0"
enabled: true
bypass_flag: "--skip-push-rules"

rebase_policy:
  enforcement: strict
  base_branch: main
  allow_merge_commits: false

lint:
  required: true
  command: "uv run ruff check ."

test:
  required: true
  command: "uv run pytest tests/ -x -q"
---

# Git Push Rules

(Human-readable documentation here...)
```

## Configuration Reference

### Top-Level Options

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `version` | string | `"1.0"` | Schema version (format: `X.Y`) |
| `enabled` | boolean | `true` | Enable/disable all push rules |
| `bypass_flag` | string | `"--skip-push-rules"` | Flag to bypass validation |

### Rebase Policy

Controls how rebasing is enforced.

```yaml
rebase_policy:
  enforcement: strict   # strict, warn, or disabled
  base_branch: main     # Branch to rebase against
  allow_merge_commits: false
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enforcement` | enum | `strict` | `strict` blocks, `warn` warns, `disabled` skips |
| `base_branch` | string | `main` | Target branch for rebase check |
| `allow_merge_commits` | boolean | `false` | Whether to allow merge commits |

**Enforcement Levels:**
- `strict`: Block push if merge commits detected
- `warn`: Show warning but allow push
- `disabled`: Skip rebase checking entirely

### Lint Configuration

Configure linting validation.

```yaml
lint:
  required: true
  command: "uv run ruff check ."
  allow_warnings: false
  timeout: 120
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `required` | boolean | `true` | Whether lint must pass |
| `command` | string | required | Shell command to run |
| `allow_warnings` | boolean | `false` | Allow non-zero but non-fatal exit |
| `timeout` | integer | `300` | Max seconds (1-3600) |

**Common lint commands:**
```yaml
# Python with ruff
command: "uv run ruff check ."

# Python with flake8
command: "python -m flake8 src/"

# JavaScript/TypeScript
command: "npm run lint"

# Go
command: "go vet ./..."
```

### Test Configuration

Configure test validation.

```yaml
test:
  required: true
  command: "uv run pytest tests/ -x -q"
  timeout: 300
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `required` | boolean | `true` | Whether tests must pass |
| `command` | string | required | Shell command to run |
| `timeout` | integer | `300` | Max seconds (1-3600) |

**Common test commands:**
```yaml
# Python with pytest
command: "uv run pytest tests/ -x -q"

# Python with unittest
command: "python -m unittest discover"

# JavaScript/TypeScript
command: "npm test"

# Go
command: "go test ./..."
```

### Branch Naming

Enforce branch naming conventions.

```yaml
branch_naming_pattern: "^(feature|fix|docs|refactor|test|chore)/[a-z0-9-]+$"
enforce_branch_naming: true
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `branch_naming_pattern` | string | See below | Regex for valid branch names |
| `enforce_branch_naming` | boolean | `true` | Whether to enforce naming |

**Default pattern:** `^(feature|fix|docs|refactor|test|chore)/[a-z0-9-]+$`

**Common patterns:**
```yaml
# Prefix with issue number
branch_naming_pattern: "^(feature|fix)/[0-9]+-[a-z0-9-]+$"

# Allow any prefix
branch_naming_pattern: "^[a-z]+/[a-z0-9-]+$"

# JIRA-style
branch_naming_pattern: "^[A-Z]+-[0-9]+[-_][a-z0-9-]+$"
```

### Janitor Settings

Configure the github-janitor cleanup agent.

```yaml
janitor_settings:
  run_after_validation: true
  prune_merged_branches: true
  clean_stale_worktrees: true
  protected_branches:
    - main
    - master
    - develop
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `run_after_validation` | boolean | `true` | Auto-run after validation |
| `prune_merged_branches` | boolean | `true` | Delete merged branches |
| `clean_stale_worktrees` | boolean | `true` | Remove orphaned worktrees |
| `protected_branches` | list | `[main, master, develop]` | Never delete these |

## Examples

### Minimal Configuration

```yaml
---
version: "1.0"
enabled: true
---
```
Uses all defaults - strict rebase, but no lint/test commands.

### Python Project

```yaml
---
version: "1.0"
enabled: true

rebase_policy:
  enforcement: strict
  base_branch: main

lint:
  required: true
  command: "uv run ruff check . && uv run ruff format --check ."

test:
  required: true
  command: "uv run pytest tests/ -x -q --cov=src --cov-fail-under=80"
  timeout: 600

branch_naming_pattern: "^(feature|fix|docs|refactor|test)/[a-z0-9-]+$"
---
```

### Node.js Project

```yaml
---
version: "1.0"
enabled: true

rebase_policy:
  enforcement: strict
  base_branch: main

lint:
  required: true
  command: "npm run lint && npm run typecheck"

test:
  required: true
  command: "npm test"
  timeout: 300

branch_naming_pattern: "^(feature|fix|docs|chore)/[a-z0-9-]+$"
---
```

### Lenient Configuration

```yaml
---
version: "1.0"
enabled: true

rebase_policy:
  enforcement: warn
  allow_merge_commits: true

lint:
  required: false

test:
  required: false

enforce_branch_naming: false
---
```

## Bypassing Validation

In emergency situations, use the bypass flag:

```bash
git push --skip-push-rules
```

**Important:**
- Bypasses are logged to `.specify/audit.log`
- Bypass should only be used in true emergencies
- Excessive bypasses indicate process problems

## Validation API

You can validate `push-rules.md` programmatically:

```python
from specify_cli.push_rules import load_push_rules, PushRulesValidationError

try:
    config = load_push_rules(Path("push-rules.md"))
    print(f"Version: {config.version}")
    print(f"Lint required: {config.is_lint_required()}")
except PushRulesValidationError as e:
    print(f"Invalid configuration: {e}")
```

## Troubleshooting

### "push-rules.md not found"

Run `specify init` to generate the file, or copy from `templates/push-rules-template.md`.

### "Invalid YAML"

Check YAML syntax. Common issues:
- Missing quotes around strings with special characters
- Incorrect indentation
- Tab characters instead of spaces

### "Validation failed"

Check the specific error message. Common issues:
- `version` must be `X.Y` format (e.g., "1.0")
- `bypass_flag` must start with `-`
- `timeout` must be 1-3600 seconds
- Regex patterns must be valid

### "Merge commits detected"

Your branch has merge commits. Rebase instead:

```bash
git rebase -i main
```

## CI Integration

While push rules provide local enforcement, you should also add CI checks as a backstop. This ensures rules are enforced even if developers bypass local hooks.

### GitHub Actions Example

Add this to `.github/workflows/enforce-rebase.yml`:

```yaml
name: Enforce Rebase

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  check-rebase:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history needed for merge detection

      - name: Check for merge commits
        run: |
          # Get merge base with target branch
          MERGE_BASE=$(git merge-base origin/${{ github.base_ref }} HEAD)

          # Find merge commits in PR
          MERGE_COMMITS=$(git log --merges --oneline "$MERGE_BASE..HEAD")

          if [ -n "$MERGE_COMMITS" ]; then
            echo "::error::Found merge commits in PR. Please rebase your branch."
            echo ""
            echo "Merge commits found:"
            echo "$MERGE_COMMITS"
            echo ""
            echo "To fix: git rebase -i origin/${{ github.base_ref }}"
            exit 1
          fi

          echo "No merge commits found - branch is rebased"
```

### Using the Rebase Checker in CI

You can also use the Python API directly:

```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.11'

- name: Install dependencies
  run: pip install specify-cli

- name: Check rebase status
  run: |
    python -c "
    from specify_cli.hooks.rebase_checker import check_rebase_status, format_rebase_error

    result = check_rebase_status('${{ github.base_ref }}', 'HEAD')
    if not result.is_rebased:
        print(format_rebase_error(result))
        exit(1)
    print('Branch is properly rebased')
    "
```

### Branch Protection Rules

For additional enforcement, configure GitHub branch protection:

1. Go to **Settings** > **Branches** > **Branch protection rules**
2. Add rule for `main` branch
3. Enable:
   - **Require a pull request before merging**
   - **Require status checks to pass** (add your CI job)
   - **Require branches to be up to date**

### GitLab CI Example

For GitLab, add to `.gitlab-ci.yml`:

```yaml
check-rebase:
  stage: test
  script:
    - git fetch origin $CI_MERGE_REQUEST_TARGET_BRANCH_NAME
    - MERGE_BASE=$(git merge-base origin/$CI_MERGE_REQUEST_TARGET_BRANCH_NAME HEAD)
    - |
      MERGE_COMMITS=$(git log --merges --oneline "$MERGE_BASE..HEAD")
      if [ -n "$MERGE_COMMITS" ]; then
        echo "Found merge commits - please rebase"
        echo "$MERGE_COMMITS"
        exit 1
      fi
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

## Related Documentation

- [ADR-012: Push Rules Enforcement Architecture](../adr/ADR-012-push-rules-enforcement-architecture.md)
- [Platform Design: Push Rules](../platform/push-rules-platform-design.md)
- [PRD: Git Push Rules Enforcement](../prd/git-push-rules-enforcement-prd.md)
