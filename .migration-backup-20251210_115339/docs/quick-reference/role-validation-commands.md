# Role Validation Quick Reference

## Local Validation Commands

### Schema Validation
```bash
# Validate workflow config against schema
python scripts/validate-workflow-config.py

# With custom files
python scripts/validate-workflow-config.py custom_workflow.yml custom_schema.json
```

### Role Structure Validation
```bash
# Validate role structure
python scripts/validate-role-schema.py

# With custom workflow file
python scripts/validate-role-schema.py custom_workflow.yml
```

### Agent Sync Validation
```bash
# Check for agent drift (validation mode)
bash scripts/bash/sync-copilot-agents.sh --validate

# Preview what would be generated (dry-run)
bash scripts/bash/sync-copilot-agents.sh --dry-run

# Regenerate agents
bash scripts/bash/sync-copilot-agents.sh

# Regenerate with verbose output
bash scripts/bash/sync-copilot-agents.sh --verbose

# Generate for specific role only
bash scripts/bash/sync-copilot-agents.sh --role dev

# Generate with VS Code settings
bash scripts/bash/sync-copilot-agents.sh --with-vscode
```

### Test Validation
```bash
# Run all tests with coverage
uv run pytest tests/ -v --cov=src/specify_cli --cov-report=term-missing

# Unit tests only
uv run pytest tests/ -k "not integration"

# Check coverage threshold
uv run pytest tests/ --cov=src/specify_cli --cov-report=json
python3 -c "import json; cov = json.load(open('coverage.json')); print(f'Coverage: {cov[\"totals\"][\"percent_covered\"]:.1f}%')"
```

### Security Validation
```bash
# Run bandit security scan
uv tool run bandit -r src/ -ll

# With JSON output
uv tool run bandit -r src/ -ll -f json -o bandit-report.json

# Check specific security levels
uv tool run bandit -r src/ -ll -s B101,B102  # Skip specific tests
```

### Team Mode Validation
```bash
# Check contributor count
git log --format='%ae' | sort -u | wc -l

# Check if .vscode/settings.json is committed
git ls-files --error-unmatch .vscode/settings.json

# Verify gitignore
grep "\.vscode/settings\.json" .gitignore
```

### Documentation Validation
```bash
# Find broken links in docs
find docs -name "*.md" -type f | while read file; do
  grep -oP '\[.*?\]\(\K[^)]+' "$file" 2>/dev/null | while read link; do
    if [[ ! "$link" =~ ^https?:// ]]; then
      dir=$(dirname "$file")
      if [ ! -e "$dir/$link" ] && [ ! -e "$link" ]; then
        echo "$file: broken link -> $link"
      fi
    fi
  done
done
```

## CI/CD Workflow Triggers

### Manual Trigger
```bash
# Trigger workflow manually (if workflow_dispatch is enabled)
gh workflow run role-validation.yml
```

### Check Workflow Status
```bash
# List recent workflow runs
gh run list --workflow=role-validation.yml

# View specific run
gh run view <run-id>

# Watch workflow run
gh run watch
```

## Common Validation Scenarios

### Before Committing Role Changes
```bash
# Full validation suite
python scripts/validate-workflow-config.py && \
python scripts/validate-role-schema.py && \
bash scripts/bash/sync-copilot-agents.sh --validate && \
echo "✓ All validations passed"
```

### After Modifying Command Templates
```bash
# Regenerate agents and validate
bash scripts/bash/sync-copilot-agents.sh
git diff .github/agents/
git add .github/agents/
git commit -m "chore: sync agents after template changes"
```

### Team Mode Setup (New Project)
```bash
# Add to gitignore
echo ".vscode/settings.json" >> .gitignore

# Remove if already committed
git rm --cached .vscode/settings.json

# Each developer generates their own
bash scripts/bash/sync-copilot-agents.sh --with-vscode
```

### Fix Drift Detection
```bash
# Check what's out of sync
bash scripts/bash/sync-copilot-agents.sh --validate

# Regenerate if drift detected
bash scripts/bash/sync-copilot-agents.sh

# Verify sync
bash scripts/bash/sync-copilot-agents.sh --validate
```

## Role-Specific Commands

### PM Role
```bash
# Validate PM configuration
python3 << 'EOF'
import yaml
with open('specflow_workflow.yml') as f:
    config = yaml.safe_load(f)
pm = config['roles']['definitions']['pm']
print(f"Commands: {pm['commands']}")
print(f"Agents: {pm['agents']}")
EOF
```

### Dev Role
```bash
# Validate Dev configuration + run tests
python3 << 'EOF'
import yaml
with open('specflow_workflow.yml') as f:
    config = yaml.safe_load(f)
dev = config['roles']['definitions']['dev']
print(f"Commands: {dev['commands']}")
print(f"Agents: {dev['agents']}")
EOF
uv run pytest tests/ -v
```

### Security Role
```bash
# Validate Sec configuration + run scan
python3 << 'EOF'
import yaml
with open('specflow_workflow.yml') as f:
    config = yaml.safe_load(f)
sec = config['roles']['definitions']['sec']
print(f"Commands: {sec['commands']}")
print(f"Agents: {sec['agents']}")
EOF
uv tool run bandit -r src/ -ll
```

### QA Role
```bash
# Validate QA configuration + check coverage
python3 << 'EOF'
import yaml
with open('specflow_workflow.yml') as f:
    config = yaml.safe_load(f)
qa = config['roles']['definitions']['qa']
print(f"Commands: {qa['commands']}")
print(f"Agents: {qa['agents']}")
EOF
uv run pytest tests/ --cov=src/specify_cli --cov-report=term-missing
```

### Ops Role
```bash
# Validate Ops configuration + check workflows
python3 << 'EOF'
import yaml
with open('specflow_workflow.yml') as f:
    config = yaml.safe_load(f)
ops = config['roles']['definitions']['ops']
print(f"Commands: {ops['commands']}")
print(f"Agents: {ops['agents']}")
EOF
ls -la .github/workflows/
```

## Troubleshooting Commands

### Schema Validation Failures
```bash
# Check YAML syntax
yamllint specflow_workflow.yml

# Validate against schema with verbose output
python scripts/validate-workflow-config.py 2>&1 | less
```

### Missing Command Files
```bash
# List expected vs actual command files
python3 << 'EOF'
import yaml
from pathlib import Path

with open('specflow_workflow.yml') as f:
    config = yaml.safe_load(f)

for role, data in config['roles']['definitions'].items():
    if role == 'all':
        continue
    print(f"\nRole: {role}")
    for cmd in data['commands']:
        path = Path(f'templates/commands/{role}/{cmd}.md')
        status = "✓" if path.exists() else "✗"
        print(f"  {status} {path}")
EOF
```

### Agent Drift Issues
```bash
# Show detailed diff
bash scripts/bash/sync-copilot-agents.sh --dry-run --verbose

# Regenerate specific role only
bash scripts/bash/sync-copilot-agents.sh --role dev

# Force regeneration
# (No --force flag available in sync-copilot-agents.sh)
```

### Coverage Failures
```bash
# Show detailed coverage report
uv run pytest tests/ --cov=src/specify_cli --cov-report=html
open htmlcov/index.html

# Find untested files
uv run pytest tests/ --cov=src/specify_cli --cov-report=term-missing | grep "TOTAL"
```

## Integration with Git Hooks

### Pre-commit Hook
```bash
# Create .git/hooks/pre-commit
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
set -e

# Run validation if role files changed
CHANGED_FILES=$(git diff --cached --name-only)
if echo "$CHANGED_FILES" | grep -qE "(specflow_workflow\.yml|templates/commands/|\.github/agents/)"; then
    echo "Running role validation..."
    python scripts/validate-role-schema.py
    bash scripts/bash/sync-copilot-agents.sh --validate
fi
EOF
chmod +x .git/hooks/pre-commit
```

### Pre-push Hook
```bash
# Create .git/hooks/pre-push
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
set -e

echo "Running full validation suite..."
python scripts/validate-workflow-config.py
python scripts/validate-role-schema.py
bash scripts/bash/sync-copilot-agents.sh --validate
echo "✓ All validations passed"
EOF
chmod +x .git/hooks/pre-push
```

## CI/CD Integration

### Check Workflow in PR
```bash
# View PR checks
gh pr checks

# View specific workflow run
gh pr view --web  # Opens in browser to see checks
```

### Debug Failing CI Job
```bash
# Download logs
gh run download <run-id>

# View specific job logs
gh run view <run-id> --job=<job-id> --log
```

## References

- Full guide: `docs/guides/ci-cd-role-validation.md`
- Team mode: `docs/guides/team-mode-workflow.md`
- Workflow file: `.github/workflows/role-validation.yml`
- Validation scripts:
  - `scripts/validate-workflow-config.py`
  - `scripts/validate-role-schema.py`
  - `scripts/bash/sync-copilot-agents.sh`
