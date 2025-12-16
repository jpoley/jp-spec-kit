# Pre-commit Hooks Guide

This guide explains how to use the pre-commit hooks provided by flowspec to maintain code quality and catch issues before they enter your repository.

## Overview

Pre-commit hooks run automatically before each commit, catching issues like:
- Trailing whitespace and formatting issues
- Syntax errors in YAML, JSON, TOML files
- Merge conflict markers left in code
- Security vulnerabilities (secrets, unsafe code)
- Linting and style violations

## Installation

### 1. Install pre-commit

```bash
# Using pip
pip install pre-commit

# Using uv
uv pip install pre-commit

# Using homebrew (macOS)
brew install pre-commit
```

### 2. Initialize hooks

If you ran `flowspec init`, you already have a `.pre-commit-config.yaml` file. Install the hooks with:

```bash
pre-commit install
```

### 3. Run manually (optional)

Run hooks against all files:

```bash
pre-commit run --all-files
```

Run a specific hook:

```bash
pre-commit run trailing-whitespace --all-files
```

## Configuration Templates

Flowspec provides project-type-specific pre-commit configurations:

### Universal Template (all projects)

The base template includes hooks that work for any project:
- Trailing whitespace removal
- End-of-file fixer
- YAML/JSON/TOML syntax checking
- Merge conflict detection
- Large file detection
- Private key detection

### Python Projects

Python projects get additional hooks:
- **Ruff**: Fast Python linter and formatter
- **Bandit**: Security vulnerability scanner
- **Mypy** (optional): Static type checking

### Node.js Projects

Node.js/TypeScript projects get:
- **Prettier**: Code formatter
- **ESLint**: JavaScript/TypeScript linter
- **npm audit** (optional): Security vulnerability scanner

## Customizing Hooks

### Enabling Optional Hooks

The template includes commented-out advanced hooks. Uncomment them in `.pre-commit-config.yaml`:

```yaml
# Before (disabled):
# - repo: https://github.com/pre-commit/mirrors-mypy
#   rev: v1.13.0
#   hooks:
#     - id: mypy

# After (enabled):
- repo: https://github.com/pre-commit/mirrors-mypy
  rev: v1.13.0
  hooks:
    - id: mypy
```

### Excluding Files

Exclude specific files or directories from a hook:

```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.8.3
  hooks:
    - id: ruff
      exclude: ^(migrations/|vendor/)
```

### Skipping Hooks Temporarily

Bypass all hooks for an emergency commit:

```bash
git commit --no-verify -m "emergency fix"
```

> **Warning**: Use `--no-verify` sparingly. Consider logging bypasses for audit purposes.

## Flowspec Security Scanning

Enable fast security scanning before commits by uncommenting the flowspec hook:

```yaml
- repo: local
  hooks:
    - id: flowspec-security-fast
      name: Flowspec Security Scan (fast)
      entry: specify security scan --fast --changed-only --fail-on critical
      language: system
      pass_filenames: false
      stages: [pre-commit]
```

This runs a fast security scan (<10 seconds) on changed files only, failing only on critical issues.

## Updating Hooks

Keep hooks up to date:

```bash
pre-commit autoupdate
```

This updates all hooks to their latest versions.

## Troubleshooting

### Hook fails to install

```bash
# Clear cache and reinstall
pre-commit clean
pre-commit install
```

### Hook takes too long

Some hooks (like mypy) can be slow. Consider:
1. Running them only in CI, not pre-commit
2. Using `--changed-only` flags where available
3. Excluding large directories

### ESLint fails with dependencies

Ensure your project has the required ESLint plugins installed:

```bash
npm install -D eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
```

## CI Integration

Pre-commit hooks can also run in CI:

```yaml
# .github/workflows/pre-commit.yml
name: pre-commit
on: [push, pull_request]
jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - uses: pre-commit/action@v3.0.1
```

## See Also

- [Pre-commit documentation](https://pre-commit.com/)
- [Ruff documentation](https://docs.astral.sh/ruff/)
- [Flowspec security scanning](/docs/guides/security-scanning.md)
