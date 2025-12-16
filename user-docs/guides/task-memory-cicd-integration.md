# Task Memory CI/CD Integration Guide

**Version**: 1.0
**Last Updated**: 2025-12-11

## Overview

This guide explains how Task Memory integrates with CI/CD pipelines to ensure memory files are valid, secure, and properly linked to backlog tasks. The integration provides automated validation on every PR and push.

## Workflows

Task Memory uses two GitHub Actions workflows:

| Workflow | File | Purpose |
|----------|------|---------|
| Task Memory Validation | `.github/workflows/task-memory-validation.yml` | Comprehensive validation |
| Memory Size Check | `.github/workflows/memory-size-check.yml` | Lightweight size monitoring |

## Validation Checks

### 1. Size Validation

**Limits**:
- Warning threshold: 25KB
- Error threshold: 100KB (blocks merge)

**Rationale**: Large memory files indicate accumulated context that should be refactored. They increase Claude Code context consumption and slow down agents.

**CI Behavior**:
```
# Warning (non-blocking)
::warning file=backlog/memory/task-42.md::Memory file exceeds 25KB: 28672 bytes

# Error (blocking)
::error file=backlog/memory/task-42.md::Memory file exceeds 100KB: 115200 bytes
```

**Resolution**:
```bash
# Compact the memory file
specify memory compact task-42

# Or manually archive and recreate
mv backlog/memory/task-42.md backlog/memory/archive/task-42-v1.md
backlog task edit task-42 -s "To Do"
backlog task edit task-42 -s "In Progress"
```

### 2. Secret Detection (gitleaks)

Scans memory files for accidentally committed secrets:

**Detected Patterns**:
- API keys and tokens
- Passwords and credentials
- AWS/GCP/Azure secrets
- Private keys
- Database connection strings

**CI Behavior**:
```
::error::Secrets detected in task memory files!
```

**Resolution**:
```bash
# Edit memory to remove secrets
nvim backlog/memory/task-42.md

# Replace with reference
# ❌ API_KEY=sk_live_abc123
# ✓ API Key: See 1Password "Engineering Team" vault
```

### 3. Format Validation

Ensures memory files follow the standard structure:

**Checks**:
- Filename format: `task-NNN.md`
- Required header: `# Task Memory:`
- Required section: `## Context`

**CI Behavior**:
```
::warning file=backlog/memory/task-42.md::Missing '## Context' section
::error file=backlog/memory/invalid.md::Invalid filename format
```

### 4. AC Coverage Validation

Validates that memory files track acceptance criteria progress:

**Checks**:
- Memory file has corresponding backlog task
- Memory documents AC progress (e.g., "AC#1", "acceptance criteria")
- Memory contains structured context

**CI Behavior**:
```
✓ task-42: Memory documents AC progress
✓ task-42: Memory contains structured context
::notice file=backlog/memory/task-99.md::Consider documenting AC progress
```

### 5. PR Comments

Automatically posts memory change summary on PRs:

```markdown
## Task Memory Changes

### Changed Files
- `backlog/memory/task-42.md` (12KB)
- `backlog/memory/task-43.md` (deleted)

### Statistics
- Files changed: 2
- Total active memories: 15
- Total size: 187KB
```

## Configuration

### Workflow Triggers

Both workflows trigger on:
- Pull requests modifying `backlog/memory/**`
- Push to `main` branch modifying `backlog/memory/**`

```yaml
on:
  pull_request:
    paths:
      - 'backlog/memory/**'
  push:
    branches:
      - main
    paths:
      - 'backlog/memory/**'
```

### Customizing Thresholds

Edit `.github/workflows/task-memory-validation.yml`:

```yaml
- name: Check memory file sizes
  run: |
    MAX_SIZE=102400   # 100KB - change this
    WARN_SIZE=25600   # 25KB - change this
```

### Disabling Checks

To disable a specific check, comment out the step:

```yaml
# - name: Scan memory files for secrets
#   run: |
#     ...
```

## Local Validation

Run the same checks locally before pushing:

### Size Check
```bash
# Check all memory files
for file in backlog/memory/*.md; do
  size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file")
  size_kb=$((size / 1024))
  echo "$file: ${size_kb}KB"
done
```

### Secret Scan
```bash
# Install gitleaks
brew install gitleaks  # macOS
# or download from https://github.com/gitleaks/gitleaks/releases

# Scan memory directory
gitleaks detect --source=backlog/memory --no-git
```

### Format Check
```bash
# Check filename format
for file in backlog/memory/*.md; do
  filename=$(basename "$file")
  if ! echo "$filename" | grep -qE '^task-[0-9]+\.md$'; then
    echo "Invalid: $filename"
  fi
done

# Check required sections
for file in backlog/memory/*.md; do
  grep -L "^# Task Memory:" "$file" 2>/dev/null
  grep -L "^## Context" "$file" 2>/dev/null
done
```

## Pre-commit Hook

Add a pre-commit hook to validate locally:

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Check for secrets in staged memory files
STAGED_MEMORY=$(git diff --cached --name-only | grep '^backlog/memory/')

if [ -n "$STAGED_MEMORY" ]; then
  echo "Checking memory files for secrets..."

  for file in $STAGED_MEMORY; do
    if [ -f "$file" ]; then
      # Check file size
      size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file")
      if [ $size -gt 102400 ]; then
        echo "ERROR: $file exceeds 100KB"
        exit 1
      fi

      # Basic secret patterns
      if grep -qiE '(api[_-]?key|secret|password)\s*[:=]\s*[^\s]{8,}' "$file"; then
        echo "WARNING: Potential secret in $file"
        echo "Review before committing."
      fi
    fi
  done
fi
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

## GitHub Actions Summary

After each run, a summary is posted to the Actions tab:

```
## Task Memory Validation Complete

✓ Size validation passed
✓ Secret detection passed
✓ Format validation passed
✓ AC coverage validation passed
```

## Troubleshooting

### CI Fails: Memory File Too Large

**Symptom**: `Memory file exceeds 100KB`

**Solution**:
1. Review the memory file for unnecessary content
2. Move detailed research to `docs/research/`
3. Archive old decisions
4. Use `specify memory compact task-NNN`

### CI Fails: Secrets Detected

**Symptom**: `Secrets detected in task memory files!`

**Solution**:
1. Remove the secret from the memory file
2. If already committed, follow secret rotation procedures
3. Reference secrets by vault location instead

### CI Warning: No Corresponding Task

**Symptom**: `No corresponding backlog task found`

**Solution**:
1. Ensure the task exists in `backlog/tasks/`
2. Check filename matches task ID
3. If task was archived, archive the memory too

### CI Warning: Missing Sections

**Symptom**: `Missing '## Context' section`

**Solution**:
```bash
# Add missing section to memory file
nvim backlog/memory/task-42.md

# Add at the beginning:
# ## Context
# [Brief task description]
```

## Integration with Other Tools

### Dependabot

Memory validation doesn't conflict with Dependabot. Memory files aren't dependencies.

### Branch Protection

Recommended branch protection rules:
```
- Require status checks: Task Memory Validation
- Require branches to be up to date
```

### CODEOWNERS

Add memory review requirements:
```
# .github/CODEOWNERS
backlog/memory/ @team-leads
```

## Metrics and Monitoring

### Workflow Run History

View historical runs:
```
https://github.com/YOUR_ORG/YOUR_REPO/actions/workflows/task-memory-validation.yml
```

### Failure Rate

Track validation failure rate in GitHub Insights or export to metrics systems.

### Memory Growth

Monitor total memory size over time using the workflow's statistics output.

## Related Documentation

- [Task Memory User Guide](task-memory-user-guide.md)
- [Task Memory Architecture](../architecture/task-memory-detailed.md)
- [Backlog Quick Start](backlog-quickstart.md)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

**Version**: 1.0 | **Last Updated**: 2025-12-11
