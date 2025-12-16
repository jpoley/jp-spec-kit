"""Hook scaffolding for flowspec init.

This module provides hook directory structure and example hooks
that are created when users run `flowspec init`.
"""

from __future__ import annotations

from pathlib import Path

EXAMPLE_HOOKS_YAML = """# Flowspec Hooks Configuration
# Documentation: https://github.com/jpoley/flowspec/docs/guides/hooks.md

version: "1.0"

# Global defaults applied to all hooks
defaults:
  timeout: 30
  fail_mode: continue

hooks:
  # Run tests after implementation (enabled by default)
  - name: run-tests
    events:
      - type: implement.completed
    script: run-tests.sh
    description: Run test suite after implementation
    enabled: true

  # Update changelog on spec creation (opt-in, disabled by default)
  - name: update-changelog
    events:
      - type: spec.created
    script: update-changelog.sh
    description: Auto-update CHANGELOG.md
    enabled: false

  # Run linter on task completion (enabled by default)
  - name: lint-code
    events:
      - type: task.completed
    script: lint-code.sh
    description: Run code linter and formatter
    enabled: true
    timeout: 60

  # Quality gate before validation (enabled by default)
  - name: quality-gate
    events:
      - type: validate.started
    script: quality-gate.sh
    description: Check code quality metrics before validation
    enabled: true
    fail_mode: stop
"""

# Disabled hooks configuration for --no-hooks flag
DISABLED_HOOKS_YAML = """# Flowspec Hooks Configuration
# Documentation: https://github.com/jpoley/flowspec/docs/guides/hooks.md
# Note: All hooks disabled via --no-hooks flag. Enable individually as needed.

version: "1.0"

# Global defaults applied to all hooks
defaults:
  timeout: 30
  fail_mode: continue

hooks:
  # Run tests after implementation
  - name: run-tests
    events:
      - type: implement.completed
    script: run-tests.sh
    description: Run test suite after implementation
    enabled: false

  # Update changelog on spec creation
  - name: update-changelog
    events:
      - type: spec.created
    script: update-changelog.sh
    description: Auto-update CHANGELOG.md
    enabled: false

  # Run linter on task completion
  - name: lint-code
    events:
      - type: task.completed
    script: lint-code.sh
    description: Run code linter and formatter
    enabled: false
    timeout: 60

  # Quality gate before validation
  - name: quality-gate
    events:
      - type: validate.started
    script: quality-gate.sh
    description: Check code quality metrics before validation
    enabled: false
    fail_mode: stop
"""

EXAMPLE_RUN_TESTS_SCRIPT = """#!/bin/bash
# Hook: Run tests after implementation
# Triggered by: implement.completed

set -e

echo "Running test suite..."

# Parse event data from HOOK_EVENT env var
EVENT_TYPE=$(echo "$HOOK_EVENT" | jq -r '.event_type')
SPEC_ID=$(echo "$HOOK_EVENT" | jq -r '.feature // "unknown"')

echo "Event: $EVENT_TYPE"
echo "Spec: $SPEC_ID"

# Run your test command here
# Examples:
# pytest tests/
# npm test
# go test ./...
# mvn test

echo "Tests completed successfully"
"""

EXAMPLE_UPDATE_CHANGELOG_SCRIPT = """#!/bin/bash
# Hook: Update changelog on spec creation
# Triggered by: spec.created

set -e

echo "Updating CHANGELOG.md..."

# Parse event data
EVENT_TYPE=$(echo "$HOOK_EVENT" | jq -r '.event_type')
SPEC_ID=$(echo "$HOOK_EVENT" | jq -r '.feature // "unknown"')
TIMESTAMP=$(date +"%Y-%m-%d")

# Create CHANGELOG.md if it doesn't exist
if [ ! -f "CHANGELOG.md" ]; then
    echo "# Changelog" > CHANGELOG.md
    echo "" >> CHANGELOG.md
fi

# Add entry (simple implementation - customize as needed)
ENTRY="## [$SPEC_ID] - $TIMESTAMP\\n\\n- Feature specification created\\n"
sed -i "3i $ENTRY" CHANGELOG.md

echo "CHANGELOG.md updated for $SPEC_ID"
"""

EXAMPLE_LINT_CODE_SCRIPT = """#!/bin/bash
# Hook: Run linter on task completion
# Triggered by: task.completed

set -e

echo "Running code linter..."

# Parse event data
TASK_ID=$(echo "$HOOK_EVENT" | jq -r '.context.task_id // "unknown"')

echo "Task: $TASK_ID"

# Run your linter
# Examples:
# ruff check . --fix
# eslint --fix .
# golangci-lint run
# mvn checkstyle:check

echo "Linting completed"
"""

EXAMPLE_QUALITY_GATE_SCRIPT = """#!/bin/bash
# Hook: Quality gate before validation
# Triggered by: validate.started
# Fail mode: stop (blocks workflow if quality checks fail)

set -e

echo "Running quality gate checks..."

SPEC_ID=$(echo "$HOOK_EVENT" | jq -r '.feature // "unknown"')
echo "Spec: $SPEC_ID"

# Example quality checks
echo "Checking code coverage..."
# coverage report --fail-under=80

echo "Checking complexity..."
# radon cc . -a -nb

echo "Checking security..."
# bandit -r src/

echo "Quality gate passed"
"""

README_HOOKS = """# Hooks Directory

This directory contains custom hooks for the Flowspec workflow.

## Files

- `hooks.yaml` - Hook configuration file
- `*.sh` - Hook scripts (must be executable)
- `audit.log` - Execution audit log (auto-created)

## Enabled by Default

When hooks are scaffolded (without `--no-hooks`), these 3 hooks are **enabled**:

| Hook | Event | Description |
|------|-------|-------------|
| `run-tests` | `implement.completed` | Runs test suite after implementation |
| `lint-code` | `task.completed` | Runs linter and formatter on task completion |
| `quality-gate` | `validate.started` | Checks code quality before validation |

**Not enabled by default**: The `update-changelog` hook is opt-in (set `enabled: true` to use it).

To disable all hooks during init, use: `flowspec init --no-hooks`

## Getting Started

1. **Review configured hooks** in `hooks.yaml`
2. **Customize scripts** for your project's tooling
3. **Test a hook**:
   ```bash
   flowspec hooks test run-tests implement.completed
   ```
4. **Validate configuration**:
   ```bash
   flowspec hooks validate
   ```

## Available Events

- `spec.created`, `spec.updated`
- `plan.created`, `plan.updated`
- `task.created`, `task.completed`
- `implement.started`, `implement.completed`
- `validate.started`, `validate.completed`
- `deploy.started`, `deploy.completed`

## CLI Commands

```bash
# List configured hooks
flowspec hooks list

# Emit an event manually
flowspec hooks emit spec.created --spec-id my-feature

# View execution history
flowspec hooks audit --tail 20

# Test a hook
flowspec hooks test <hook-name> <event-type>

# Validate configuration
flowspec hooks validate
```

## Security

- Scripts must be in `.flowspec/hooks/` directory
- Timeout enforced (default: 30s)
- All executions are audit logged
- Scripts run in sandboxed environment

## Documentation

Full documentation: https://github.com/jpoley/flowspec/blob/main/docs/guides/hooks.md
"""


def scaffold_hooks(project_root: Path, no_hooks: bool = False) -> list[Path]:
    """Create hooks directory structure with examples.

    Args:
        project_root: Root directory of the project
        no_hooks: If True, create hooks.yaml with all hooks disabled

    Returns:
        List of paths to created files
    """
    hooks_dir = project_root / ".flowspec" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)

    created = []

    # Select hooks configuration based on --no-hooks flag
    hooks_config = DISABLED_HOOKS_YAML if no_hooks else EXAMPLE_HOOKS_YAML

    # Create hooks.yaml
    hooks_yaml = hooks_dir / "hooks.yaml"
    if not hooks_yaml.exists():
        hooks_yaml.write_text(hooks_config)
        created.append(hooks_yaml)

    # Create example scripts
    scripts = [
        ("run-tests.sh", EXAMPLE_RUN_TESTS_SCRIPT),
        ("update-changelog.sh", EXAMPLE_UPDATE_CHANGELOG_SCRIPT),
        ("lint-code.sh", EXAMPLE_LINT_CODE_SCRIPT),
        ("quality-gate.sh", EXAMPLE_QUALITY_GATE_SCRIPT),
    ]

    for script_name, script_content in scripts:
        script_path = hooks_dir / script_name
        if not script_path.exists():
            script_path.write_text(script_content)
            script_path.chmod(0o755)  # Make executable
            created.append(script_path)

    # Create README
    readme_path = hooks_dir / "README.md"
    if not readme_path.exists():
        readme_path.write_text(README_HOOKS)
        created.append(readme_path)

    return created


__all__ = ["scaffold_hooks"]
