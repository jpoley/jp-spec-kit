# CI/CD Role-Based Validation Guide

## Overview

The role-based validation workflows ensure that the role-based command architecture remains consistent, valid, and properly synchronized across the codebase. This guide explains the validation jobs, how they work, and how to troubleshoot failures.

## Validation Workflow

**Location**: `.github/workflows/role-validation.yml`

**Triggers**:
- Push to `main` branch
- Pull requests to `main` branch
- Changes to role-related files:
  - `templates/commands/**`
  - `specflow_workflow.yml`
  - `schemas/**`
  - `.claude/commands/**`
  - `.github/agents/**`
  - Validation scripts

## Validation Jobs

### 1. Schema Validation (`validate-schema`)

**Purpose**: Ensures `specflow_workflow.yml` conforms to the JSON schema.

**Checks**:
- ✓ Valid YAML syntax
- ✓ Required sections present (version, states, workflows, transitions)
- ✓ Role definitions structure
- ✓ Version format (e.g., "2.0")
- ✓ Schema compatibility

**Script**: `scripts/validate-workflow-config.py`

**Example Run**:
```bash
python scripts/validate-workflow-config.py specflow_workflow.yml schemas/specflow_workflow.schema.json
```

**Common Failures**:
- Missing required roles (pm, arch, dev, sec, qa, ops, all)
- Invalid version format
- Malformed YAML
- Missing required fields in roles

**Fix**:
```bash
# Validate locally
python scripts/validate-workflow-config.py

# Check for syntax errors
yamllint specflow_workflow.yml
```

---

### 2. Command Structure Validation (`validate-commands`)

**Purpose**: Verifies role command files exist and follow conventions.

**Checks**:
- ✓ Command files exist for all defined commands
- ✓ File naming conventions (lowercase-with-hyphens)
- ✓ Agent-to-role mappings are valid
- ✓ No orphaned commands

**Script**: Inline Python in workflow

**Example**:
```yaml
# Role: dev
# Commands: [build, debug, refactor]
# Expected files:
#   - templates/commands/dev/build.md
#   - templates/commands/dev/debug.md
#   - templates/commands/dev/refactor.md
```

**Common Failures**:
- Missing command file: `templates/commands/{role}/{command}.md`
- Invalid command name (uppercase, spaces, special chars)
- Command defined in role but file doesn't exist

**Fix**:
```bash
# Check which files are missing
ls -la templates/commands/dev/

# Create missing command file
touch templates/commands/dev/missing-command.md
```

---

### 3. Agent Sync Validation (`validate-agent-sync`)

**Purpose**: Detects drift between command templates and generated Copilot agents.

**Checks**:
- ✓ Generated agents match command templates
- ✓ No stale agent files
- ✓ Frontmatter is correctly formatted
- ✓ Handoffs are properly defined

**Script**: `scripts/bash/sync-copilot-agents.sh --validate`

**How It Works**:
1. Reads command templates from `templates/commands/`
2. Generates expected agent files (in memory)
3. Compares with actual files in `.github/agents/`
4. Reports any differences

**Common Failures**:
- "Drift detected: dev-build.agent.md" - Generated agent differs from committed file
- "Missing: qa-test.agent.md" - Agent file should exist but doesn't

**Fix**:
```bash
# Regenerate agents
bash scripts/bash/sync-copilot-agents.sh

# Verify changes
git diff .github/agents/

# Commit regenerated agents
git add .github/agents/
git commit -m "chore: sync Copilot agents"
```

---

### 4. PM Role Validation (`validate-pm-role`)

**Purpose**: Validates Product Manager role configuration.

**Checks**:
- ✓ Required commands: assess, define, discover
- ✓ Required agents: @product-requirements-manager, @workflow-assessor, @researcher, @business-validator
- ✓ PRD template structure (if exists)

**Common Failures**:
- Missing PM command (e.g., no `templates/commands/pm/assess.md`)
- Missing required agent in role definition
- PRD template missing required sections

**Fix**:
```bash
# Check role definition
grep -A 10 "pm:" specflow_workflow.yml

# Verify command files
ls -la templates/commands/pm/
```

---

### 5. Dev Role Validation (`validate-dev-role`)

**Purpose**: Validates Developer role configuration and runs tests.

**Checks**:
- ✓ Required commands: build, debug, refactor
- ✓ Required agents: @frontend-engineer, @backend-engineer
- ✓ Unit tests pass
- ✓ ADR naming conventions (if ADRs exist)

**Common Failures**:
- Missing dev command
- Test failures
- ADRs not following naming convention (ADR-NNN-title.md)

**Fix**:
```bash
# Run tests locally
uv run pytest tests/ -v

# Check ADR format
ls -la docs/adr/

# Rename ADR if needed
mv docs/adr/my-decision.md docs/adr/ADR-001-my-decision.md
```

---

### 6. Security Role Validation (`validate-sec-role`)

**Purpose**: Validates Security role and runs security scans.

**Checks**:
- ✓ Required commands: scan, triage, fix, audit
- ✓ Required agent: @secure-by-design-engineer
- ✓ Bandit security scan
- ✓ Security config files exist

**Common Failures**:
- Missing security command
- Security vulnerabilities found (high/medium/low)
- Missing `.github/security-config.yml`

**Fix**:
```bash
# Run bandit locally
uv tool run bandit -r src/ -ll

# Create security config if missing
touch .github/security-config.yml
```

---

### 7. QA Role Validation (`validate-qa-role`)

**Purpose**: Validates QA role, checks test coverage, and documentation links.

**Checks**:
- ✓ Required commands: test, verify, review
- ✓ Required agents: @quality-guardian, @release-manager
- ✓ Test coverage ≥ 70%
- ✓ Documentation links are valid

**Common Failures**:
- Test coverage below threshold
- Broken documentation links
- Missing QA command

**Fix**:
```bash
# Check coverage locally
uv run pytest tests/ --cov=src/specify_cli --cov-report=term-missing

# Find broken links
grep -r "\[.*\](.*)" docs/ | grep -v "^#"
```

---

### 8. Team Mode Validation (`validate-team-mode`)

**Purpose**: Ensures team mode compliance (no committed .vscode/settings.json).

**Checks**:
- ✓ Detects team mode (contributor count > 1)
- ✓ No `.vscode/settings.json` in Git (if team mode)
- ✓ `.vscode/settings.json` in `.gitignore`

**Team Mode Detection**:
```bash
CONTRIBUTOR_COUNT=$(git log --format='%ae' | sort -u | wc -l)
if [ $CONTRIBUTOR_COUNT -gt 1 ]; then
  # Team mode enabled
fi
```

**Common Failures**:
- ".vscode/settings.json is committed in team mode"

**Fix**:
```bash
# Remove from Git
git rm --cached .vscode/settings.json

# Add to .gitignore
echo ".vscode/settings.json" >> .gitignore

# Commit
git add .gitignore
git commit -m "chore: fix team mode - gitignore .vscode/settings.json"
```

**See**: [Team Mode Workflow Guide](./team-mode-workflow.md)

---

### 9. Ops Role Validation (`validate-ops-role`)

**Purpose**: Validates Ops/SRE role and CI/CD workflow files.

**Checks**:
- ✓ Required commands: deploy, monitor, respond, scale
- ✓ Required agent: @sre-agent
- ✓ CI/CD workflow files exist

**Common Failures**:
- Missing ops command
- No GitHub Actions workflows found

**Fix**:
```bash
# Check workflows
ls -la .github/workflows/

# Create missing command
touch templates/commands/ops/missing-command.md
```

---

## Running Validations Locally

### Quick Validation

```bash
# Validate workflow schema
python scripts/validate-workflow-config.py

# Validate role structure
python scripts/validate-role-schema.py

# Check agent sync
bash scripts/bash/sync-copilot-agents.sh --validate
```

### Individual Job Testing

```bash
# Test PM role validation
python3 << 'EOF'
import yaml
with open('specflow_workflow.yml') as f:
    config = yaml.safe_load(f)
pm_role = config['roles']['definitions']['pm']
print(f"Commands: {pm_role['commands']}")
print(f"Agents: {pm_role['agents']}")
EOF

# Test agent sync
bash scripts/bash/sync-copilot-agents.sh --dry-run --verbose

# Test coverage
uv run pytest tests/ --cov=src/specify_cli --cov-report=term-missing
```

---

## Troubleshooting CI/CD Failures

### Workflow: validate-schema

**Error**: "Missing required roles: {'ops'}"

**Cause**: Role definition missing in `specflow_workflow.yml`

**Fix**:
```yaml
roles:
  definitions:
    ops:
      display_name: "SRE/DevOps"
      icon: "🚀"
      commands: ["deploy", "monitor", "respond", "scale"]
      agents: ["@sre-agent"]
```

---

### Workflow: validate-commands

**Error**: "Missing command file: templates/commands/dev/build.md"

**Cause**: Command defined in role but file doesn't exist

**Fix**:
```bash
# Create the missing file
touch templates/commands/dev/build.md

# Or remove from role definition if not needed
```

---

### Workflow: validate-agent-sync

**Error**: "Drift detected: dev-build.agent.md"

**Cause**: Command template changed but agent not regenerated

**Fix**:
```bash
# Regenerate agents
bash scripts/bash/sync-copilot-agents.sh

# Commit changes
git add .github/agents/
git commit -m "chore: sync agents after command template changes"
```

---

### Workflow: validate-team-mode

**Error**: ".vscode/settings.json is committed in team mode"

**Cause**: VS Code settings committed when multiple contributors exist

**Fix**:
```bash
# Remove from Git
git rm --cached .vscode/settings.json

# Add to .gitignore
echo ".vscode/settings.json" >> .gitignore

# Commit
git add .gitignore
git commit -m "chore: fix team mode compliance"
```

---

## Integration with Other Workflows

The role validation workflow integrates with:

1. **CI Workflow** (`.github/workflows/ci.yml`):
   - Runs tests, linting, and build
   - Complements role validation with code quality checks

2. **Security Workflow** (`.github/workflows/security-scan.yml`):
   - Deep security scanning with multiple tools
   - Role validation runs basic security checks

3. **Dev Setup Validation** (`.github/workflows/dev-setup-validation.yml`):
   - Validates symlink structure for development
   - Ensures `specify dev-setup` works correctly

## Best Practices

### For Contributors

1. **Validate before committing**:
   ```bash
   python scripts/validate-role-schema.py
   bash scripts/bash/sync-copilot-agents.sh --validate
   ```

2. **Regenerate agents after template changes**:
   ```bash
   # If you modify templates/commands/
   bash scripts/bash/sync-copilot-agents.sh
   git add .github/agents/
   ```

3. **Check team mode compliance**:
   ```bash
   # Don't commit .vscode/settings.json in team mode
   git status .vscode/settings.json
   ```

### For Maintainers

1. **Keep schema up-to-date**:
   - Update `schemas/specflow_workflow.schema.json` when adding features
   - Validate backwards compatibility

2. **Document new roles**:
   - Add to validation jobs when introducing new roles
   - Update this guide with new checks

3. **Monitor CI failures**:
   - Review role validation job logs
   - Address systemic issues (e.g., missing agent assignments)

## References

- [Team Mode Workflow Guide](./team-mode-workflow.md)
- [Workflow Customization Guide](./workflow-customization.md)
- [Role-Based Command Namespaces ADR](../adr/ADR-role-based-command-namespaces.md)
- [Agent Loop Classification](../reference/agent-loop-classification.md)
