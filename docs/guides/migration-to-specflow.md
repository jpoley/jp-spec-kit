# Migration Guide: specify to specflow

This guide helps you migrate from the `specify` CLI command to the new `specflow` command.

## Why the Rename?

The CLI has been renamed from `specify` to `specflow` to:
- Establish clear branding identity
- Avoid conflicts with generic "specify" terms
- Improve discoverability on PyPI and in search engines

## Quick Migration

### 1. Update Your Installation

```bash
# Install new CLI
uv tool install specflow-cli --from git+https://github.com/jpoley/jp-spec-kit.git
```

### 2. Update Your Commands

Replace `specify` with `specflow` in all commands:

| Old Command | New Command |
|-------------|-------------|
| `specify init` | `specflow init` |
| `specify workflow validate` | `specflow workflow validate` |
| `specify dev-setup` | `specflow dev-setup` |
| `specify security scan` | `specflow security scan` |
| `specify upgrade` | `specflow upgrade` |

## Deprecation Timeline

The old `specify` command will continue to work during the transition period:

| Phase | Timeline | `specify` Command Behavior |
|-------|----------|---------------------------|
| **Soft Deprecation** | Now - Month 2 | Works with deprecation warning |
| **Hard Deprecation** | Month 4-6 | Fails with migration guide |
| **Removal** | v2.0.0+ | Command removed completely |

## What Stays the Same

The following have NOT changed:

- **Internal package name**: `specify_cli` (Python import paths unchanged)
- **Slash commands**: `/jpspec:*`, `/speckit:*` (Claude Code commands)
- **Directory names**: `.specify/` configuration directory
- **Rule file names**: `*-specify-*` rule files for AI agents

## Automatic Script Migration

### Bash Scripts

```bash
# Find and replace in your scripts
find . -name "*.sh" -exec sed -i 's/\bspecify\b/specflow/g' {} +
```

### CI/CD Workflows (GitHub Actions)

```yaml
# Old
- run: uv run specify workflow validate

# New
- run: uv run specflow workflow validate
```

### Shell Aliases

Update your shell configuration (`.bashrc`, `.zshrc`):

```bash
# New aliases
alias sf='specflow'
alias sfs='specflow security scan'
alias sfw='specflow workflow validate'
```

## Troubleshooting

### "specflow: command not found"

Install the CLI:

```bash
uv tool install specflow-cli --from git+https://github.com/jpoley/jp-spec-kit.git
```

### Deprecation Warning Appears

This is expected during the transition period. Update your scripts to use `specflow` to suppress the warning.

### Scripts Still Using Old Command

Search your codebase for remaining references:

```bash
grep -r "specify " --include="*.sh" --include="*.yml" --include="*.yaml" .
```

## Need Help?

- Open an issue: https://github.com/jpoley/jp-spec-kit/issues
- Check documentation: https://github.com/jpoley/jp-spec-kit/blob/main/docs/
