# Constitution Validation Guide

## Overview

The `specify constitution validate` command helps you ensure your project constitution is fully customized and ready to use. It scans for `NEEDS_VALIDATION` markers that indicate placeholder content requiring your attention.

## Quick Start

```bash
# Validate your constitution
specify constitution validate

# Validate with detailed output
specify constitution validate --verbose

# Validate a custom file
specify constitution validate --path path/to/constitution.md
```

## What It Does

The validation command:

1. **Locates your constitution** (default: `memory/constitution.md`)
2. **Scans for markers** in the format `<!-- NEEDS_VALIDATION: description -->`
3. **Reports results**:
   - Exit code 0 if fully validated (no markers)
   - Exit code 1 if validation needed (markers found) or file missing

## Understanding NEEDS_VALIDATION Markers

When you create a constitution using `flowspec init`, the generated template includes markers like:

```markdown
<!-- NEEDS_VALIDATION: Update team size -->
Team size: [Your team size]

<!-- NEEDS_VALIDATION: Update deployment frequency -->
Deployment frequency: [Your deployment cadence]
```

These markers indicate sections you should customize for your specific project.

## Validation Workflow

### Step 1: Run Validation

```bash
specify constitution validate
```

**If validation passes:**
```
╭─ Validation Passed ─────────────────────╮
│ ✓ Constitution is fully validated       │
│                                          │
│ No NEEDS_VALIDATION markers found.      │
│ Your constitution is ready to use.      │
╰──────────────────────────────────────────╯
```

**If markers found:**
```
Found 3 section(s) requiring validation:

  1. Update team size
  2. Update deployment frequency
  3. Specify tech stack

╭─ Action Required ──────────────────────╮
│ 1. Review each section above           │
│ 2. Update placeholder values            │
│ 3. Remove NEEDS_VALIDATION comment     │
╰─────────────────────────────────────────╯
```

### Step 2: Update Your Constitution

Edit `memory/constitution.md` and customize the marked sections:

**Before:**
```markdown
<!-- NEEDS_VALIDATION: Update team size -->
Team size: [Your team size]
```

**After:**
```markdown
Team size: 5 engineers
```

**Important:** Remove the entire `<!-- NEEDS_VALIDATION: ... -->` comment line once you've updated the content.

### Step 3: Re-validate

Run the command again to verify all markers are removed:

```bash
specify constitution validate
```

## Command Options

| Option | Description |
|--------|-------------|
| `--path <file>` | Path to constitution file (default: `memory/constitution.md`) |
| `--verbose`, `-v` | Show detailed validation output including file path |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Validation passed - no markers found |
| 1 | Validation failed - markers found or file missing |

## Integration with CI/CD

Add constitution validation to your CI pipeline to ensure it's kept up-to-date:

```yaml
# .github/workflows/validate.yml
name: Validate Constitution
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install specify
        run: pip install flowspec-cli
      - name: Validate constitution
        run: specify constitution validate
```

## Common Scenarios

### New Project Setup

```bash
# 1. Initialize project
flowspec init my-project --constitution medium

# 2. Enter project
cd my-project

# 3. Check what needs customization
specify constitution validate

# 4. Edit constitution
vim memory/constitution.md

# 5. Verify all markers removed
specify constitution validate
```

### Adding Constitution to Existing Project

```bash
# 1. Add constitution
flowspec init --here

# 2. Choose tier when prompted (or use --constitution flag)

# 3. Validate
specify constitution validate

# 4. Customize and re-validate
```

### Using a Custom Constitution Path

```bash
# Validate custom file
specify constitution validate --path docs/team-charter.md

# Useful for:
# - Non-standard locations
# - Multiple constitution files
# - Testing templates
```

## Troubleshooting

### "Constitution not found"

**Error:**
```
Error: Constitution not found at /path/to/memory/constitution.md
Tip: Run 'flowspec init --here' to create one
```

**Solution:**
Run `flowspec init --here` to create a constitution, or use `--path` to specify the correct location.

### Validation Keeps Failing

1. Ensure you've **removed the entire marker line**, not just updated the content:
   ```markdown
   <!-- NEEDS_VALIDATION: description -->  ← Remove this line!
   Your updated value here
   ```

2. Check for hidden markers using verbose mode:
   ```bash
   specify constitution validate --verbose
   ```

3. Manually search for markers:
   ```bash
   grep -n "NEEDS_VALIDATION" memory/constitution.md
   ```

### False Positives

If validation detects a marker you want to keep (e.g., in a code example), escape it:

```markdown
Example of a marker (not for validation):
\<!-- NEEDS_VALIDATION: This is just an example -->
```

## Best Practices

1. **Validate early and often** - Make it part of your setup checklist
2. **Validate before committing** - Ensures your team sees a complete constitution
3. **Use in CI** - Catch incomplete constitutions in pull requests
4. **Document your decisions** - Replace placeholders with specific, actionable values
5. **Review periodically** - Your constitution should evolve with your project

## Related Commands

| Command | Purpose |
|---------|---------|
| `flowspec init` | Create new project with constitution |
| `flowspec init --here` | Add constitution to existing project |
| `flowspec workflow validate` | Validate workflow configuration |

## See Also

- [Constitution Templates](../reference/constitution-templates.md)
- [Project Initialization Guide](./project-initialization.md)
- [Workflow Validation](./workflow-validation.md)
