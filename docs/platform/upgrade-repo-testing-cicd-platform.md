# Platform Design: upgrade-repo Testing and CI/CD Infrastructure

**Author**: Platform Engineer
**Date**: 2026-01-06
**Status**: Design Proposal
**Epic**: task-579 - Flowspec Release Alignment
**Related Tasks**: task-579.01 through task-579.18

---

## Executive Summary

This platform design establishes comprehensive testing and CI/CD infrastructure for the flowspec `upgrade-repo` command fixes. The current upgrade-repo command is completely broken (as documented in `docs/building/fix-flowspec-plan.md`), causing incorrect deployments to target repositories. This design ensures all 18 subtasks under epic task-579 can be validated automatically before release.

### Key Deliverables

1. **Test Strategy**: Unit, integration, and E2E tests for upgrade-repo enhancements
2. **CI/CD Pipeline Design**: Pre-merge validation and release gates
3. **Quality Gates**: Automated verification of breaking changes
4. **Verification Automation**: Post-upgrade validation scripts
5. **Rollback Strategy**: Safe recovery from failed upgrades

---

## 1. Testing Strategy

### 1.1 Test Pyramid Structure

```
         ╱╲
        ╱E2E╲        E2E Tests (5-10 tests)
       ╱─────╲       - Full upgrade-repo on mock repos
      ╱ Integ ╲      Integration Tests (20-30 tests)
     ╱─────────╲     - Multi-component upgrades
    ╱   Unit    ╲    Unit Tests (50-100 tests)
   ╱─────────────╲   - Individual upgrade functions
  ╱───────────────╲
```

### 1.2 Unit Tests

**Location**: `tests/test_upgrade_repo_enhancements.py`

Test each upgrade-repo enhancement independently:

#### P0.1: /flow:operate Removal
```python
def test_upgrade_removes_flow_operate_from_workflow_config():
    """Verify workflow config v2.0 has no /flow:operate references."""

def test_upgrade_removes_deprecated_operate_command():
    """Verify _DEPRECATED_operate.md is removed."""

def test_upgrade_removes_operate_from_claude_md():
    """Verify CLAUDE.md has no /flow:operate references."""
```

#### P0.2: Agent File Naming
```python
def test_upgrade_creates_agents_with_dot_notation():
    """Verify agents use flow.assess.agent.md not flow-assess.agent.md."""

def test_upgrade_sets_pascalcase_agent_names():
    """Verify agent names are FlowAssess not flow-assess."""

def test_upgrade_includes_flow_assess_agent():
    """Verify flow.assess.agent.md is created."""
```

#### P0.3: MCP Configuration
```python
def test_upgrade_calls_generate_mcp_json():
    """Verify generate_mcp_json is invoked during upgrade."""

def test_upgrade_includes_required_mcp_servers():
    """Verify backlog, github, serena are in .mcp.json."""
```

#### P0.4: Skills Sync
```python
def test_upgrade_syncs_all_skills():
    """Verify all 21 skills are copied to target repo."""

def test_upgrade_preserves_existing_skills():
    """Verify custom skills are not overwritten."""
```

#### P0.5: Workflow Config v2.0
```python
def test_upgrade_updates_workflow_version():
    """Verify flowspec_workflow.yml version becomes 2.0."""

def test_upgrade_removes_operate_workflow():
    """Verify operate workflow is removed from config."""

def test_upgrade_preserves_custom_workflows():
    """Verify user's custom_workflows section is preserved."""
```

#### P0.6: Deprecated File Cleanup
```python
def test_upgrade_removes_specify_directory():
    """Verify .specify/ directory is deleted."""

def test_upgrade_removes_deprecated_commands():
    """Verify _DEPRECATED_* commands are removed."""

def test_upgrade_removes_broken_include_directives():
    """Verify {{INCLUDE:}} directives are removed."""
```

### 1.3 Integration Tests

**Location**: `tests/integration/test_upgrade_repo_workflow.py`

Test multi-step upgrade workflows:

```python
def test_full_upgrade_repo_workflow(tmp_project_v1):
    """
    End-to-end test of complete upgrade-repo workflow.

    Given: A v1.0 project with legacy structure
    When: upgrade-repo is executed
    Then: All P0 fixes are applied correctly
    """
    result = run_upgrade_repo(tmp_project_v1)

    # Verify agent files
    assert (tmp_project_v1 / ".github/agents/flow.assess.agent.md").exists()
    assert not (tmp_project_v1 / ".github/agents/flow-assess.agent.md").exists()

    # Verify MCP config
    mcp_config = json.loads((tmp_project_v1 / ".mcp.json").read_text())
    assert "backlog" in mcp_config["mcpServers"]
    assert "github" in mcp_config["mcpServers"]

    # Verify workflow config
    workflow_config = yaml.safe_load((tmp_project_v1 / "flowspec_workflow.yml").read_text())
    assert workflow_config["version"] == "2.0"
    assert "operate" not in workflow_config["workflows"]

    # Verify deprecated files removed
    assert not (tmp_project_v1 / ".specify").exists()
    assert not (tmp_project_v1 / ".claude/commands/flow/_DEPRECATED_operate.md").exists()

    # Verify skills synced
    skills_dir = tmp_project_v1 / ".claude/skills"
    assert len(list(skills_dir.glob("*.md"))) >= 21


def test_upgrade_preserves_user_customizations(tmp_project_with_custom):
    """
    Verify upgrade preserves user's custom content.

    Given: A project with custom workflows and constitution
    When: upgrade-repo is executed
    Then: User customizations are preserved
    """
    # Custom workflow should be preserved
    # Custom constitution should be preserved
    # Custom skills should not be overwritten
```

### 1.4 E2E Tests

**Location**: `tests/e2e/test_upgrade_repo_e2e.py`

Test upgrade-repo on realistic mock repositories:

```python
def test_upgrade_repo_on_minimal_project():
    """Test upgrade on minimal project (only required files)."""

def test_upgrade_repo_on_full_featured_project():
    """Test upgrade on project with all features enabled."""

def test_upgrade_repo_with_branch_option():
    """Test upgrade from git branch for testing."""

def test_upgrade_repo_dry_run():
    """Test dry-run shows correct preview without changes."""

def test_upgrade_repo_idempotent():
    """Running upgrade twice should be safe (idempotent)."""
```

### 1.5 Test Fixtures

**Location**: `tests/fixtures/mock_repos/`

Create mock repositories representing different upgrade scenarios:

```
tests/fixtures/mock_repos/
├── v1.0-minimal/           # Minimal v1.0 project
│   ├── .flowspec/
│   ├── .claude/
│   ├── flowspec_workflow.yml (v1.0)
│   └── CLAUDE.md (with /flow:operate)
├── v1.0-full/              # Full v1.0 project
│   ├── .flowspec/
│   ├── .claude/
│   ├── .github/agents/     # Legacy hyphen naming
│   ├── .specify/           # Should be removed
│   ├── flowspec_workflow.yml (v1.0)
│   └── .mcp.json (incomplete)
├── v1.0-custom/            # Project with user customizations
│   ├── memory/constitution.md (customized)
│   ├── flowspec_workflow.yml (custom_workflows)
│   └── .claude/skills/custom-skill.md
└── v2.0-current/           # Current v2.0 project (target state)
    ├── .github/agents/     # Dot notation
    ├── .mcp.json (complete)
    ├── flowspec_workflow.yml (v2.0)
    └── .claude/skills/     # All 21 skills
```

Fixture creation script:

```python
# tests/fixtures/create_mock_repos.py
def create_v1_minimal_repo(tmp_path: Path) -> Path:
    """Create minimal v1.0 project for testing."""
    # Copy v1.0 templates
    # Add legacy agent files (hyphens)
    # Add v1.0 workflow config with operate
    # Add /flow:operate references to CLAUDE.md

def create_v1_full_repo(tmp_path: Path) -> Path:
    """Create full v1.0 project with all legacy artifacts."""

def create_v1_custom_repo(tmp_path: Path) -> Path:
    """Create v1.0 project with user customizations."""

def create_v2_current_repo(tmp_path: Path) -> Path:
    """Create reference v2.0 project (target state)."""
```

---

## 2. CI/CD Pipeline Design

### 2.1 Pre-Merge Validation (Pull Request Checks)

**Workflow**: `.github/workflows/pr-upgrade-validation.yml`

```yaml
name: PR Upgrade Validation

on:
  pull_request:
    paths:
      - 'src/flowspec_cli/__init__.py'
      - 'templates/**'
      - 'tests/test_upgrade*.py'
      - 'tests/integration/test_upgrade*.py'
      - 'tests/e2e/test_upgrade*.py'

jobs:
  lint-and-format:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync
      - run: uv run ruff format --check .
      - run: uv run ruff check .

  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync
      - name: Run unit tests
        run: |
          uv run pytest tests/test_upgrade*.py -v \
            --cov=src/flowspec_cli \
            --cov-report=term-missing \
            --cov-fail-under=80

  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync
      - name: Run integration tests
        run: |
          uv run pytest tests/integration/test_upgrade*.py -v \
            --cov=src/flowspec_cli \
            --cov-report=term-missing

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync
      - name: Run E2E tests
        run: |
          uv run pytest tests/e2e/test_upgrade*.py -v \
            --cov=src/flowspec_cli \
            --cov-report=term-missing

  quality-gates:
    runs-on: ubuntu-latest
    needs: [lint-and-format, unit-tests, integration-tests, e2e-tests]
    steps:
      - uses: actions/checkout@v4
      - name: Run quality gates
        run: ./scripts/bash/quality-gates.sh
```

### 2.2 Quality Gates Script

**Location**: `scripts/bash/quality-gates.sh`

```bash
#!/usr/bin/env bash
# Quality gates for upgrade-repo validation
set -euo pipefail

echo "=== Flowspec Upgrade-Repo Quality Gates ==="

# Gate 1: No /flow:operate references
echo "Gate 1: Checking for /flow:operate references..."
if grep -r "/flow:operate" templates/ src/ .claude/ 2>/dev/null; then
    echo "❌ FAIL: Found /flow:operate references"
    exit 1
fi
echo "✅ PASS: No /flow:operate references found"

# Gate 2: Agent files use dot notation
echo "Gate 2: Checking agent file naming..."
if ls templates/.github/agents/flow-*.agent.md 2>/dev/null; then
    echo "❌ FAIL: Found hyphen-notation agent files"
    exit 1
fi
echo "✅ PASS: Agent files use dot notation"

# Gate 3: Agent names are PascalCase
echo "Gate 3: Checking agent name format..."
for agent in templates/.github/agents/*.agent.md; do
    if ! grep -q "^name: Flow[A-Z]" "$agent"; then
        echo "❌ FAIL: Agent $agent does not use PascalCase name"
        exit 1
    fi
done
echo "✅ PASS: All agent names are PascalCase"

# Gate 4: No {{INCLUDE:}} directives in templates
echo "Gate 4: Checking for broken INCLUDE directives..."
if grep -r "{{INCLUDE:" templates/.claude/commands/ 2>/dev/null; then
    echo "❌ FAIL: Found {{INCLUDE:}} directives in command templates"
    exit 1
fi
echo "✅ PASS: No broken INCLUDE directives"

# Gate 5: MCP config has required servers
echo "Gate 5: Validating MCP configuration template..."
if ! python3 -c "
import json
with open('templates/.mcp.json') as f:
    config = json.load(f)
    required = ['backlog', 'github', 'serena']
    missing = [s for s in required if s not in config.get('mcpServers', {})]
    if missing:
        print(f'Missing servers: {missing}')
        exit(1)
"; then
    echo "❌ FAIL: MCP config missing required servers"
    exit 1
fi
echo "✅ PASS: MCP config has required servers"

# Gate 6: Workflow config is v2.0
echo "Gate 6: Validating workflow config version..."
if ! python3 -c "
import yaml
with open('templates/flowspec_workflow.yml') as f:
    config = yaml.safe_load(f)
    if config.get('version') != '2.0':
        print(f'Version is {config.get(\"version\")}, expected 2.0')
        exit(1)
    if 'operate' in config.get('workflows', {}):
        print('Found operate workflow in v2.0 config')
        exit(1)
"; then
    echo "❌ FAIL: Workflow config validation failed"
    exit 1
fi
echo "✅ PASS: Workflow config is v2.0"

# Gate 7: All skills present
echo "Gate 7: Checking skills directory..."
skill_count=$(find templates/.claude/skills -name "*.md" | wc -l)
if [ "$skill_count" -lt 21 ]; then
    echo "❌ FAIL: Expected 21+ skills, found $skill_count"
    exit 1
fi
echo "✅ PASS: All skills present ($skill_count skills)"

echo ""
echo "=== All Quality Gates Passed ==="
```

### 2.3 Post-Merge Integration Tests

**Workflow**: `.github/workflows/post-merge-validation.yml`

```yaml
name: Post-Merge Validation

on:
  push:
    branches: [main]
    paths:
      - 'src/flowspec_cli/__init__.py'
      - 'templates/**'

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync
      - run: uv build

      - name: Install built package
        run: uv tool install dist/*.whl --force

      - name: Test upgrade-repo on mock repository
        run: |
          # Create mock v1.0 repo
          mkdir -p /tmp/test-repo
          cp -r tests/fixtures/mock_repos/v1.0-full/* /tmp/test-repo/

          # Run upgrade-repo
          cd /tmp/test-repo
          flowspec upgrade-repo --dry-run

          # Verify results
          ./scripts/bash/verify-upgrade.sh /tmp/test-repo
```

### 2.4 Release Gate Validation

**Workflow**: `.github/workflows/release-gate.yml`

```yaml
name: Release Gate Validation

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to release'
        required: true

jobs:
  pre-release-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync

      - name: Run all tests
        run: |
          uv run pytest tests/ -v \
            --cov=src/flowspec_cli \
            --cov-report=html \
            --cov-fail-under=80

      - name: Run quality gates
        run: ./scripts/bash/quality-gates.sh

      - name: Verify version consistency
        run: |
          VERSION="${{ github.event.inputs.version }}"
          # Check pyproject.toml
          if ! grep -q "version = \"$VERSION\"" pyproject.toml; then
            echo "Version mismatch in pyproject.toml"
            exit 1
          fi
          # Check __init__.py
          if ! grep -q "__version__ = \"$VERSION\"" src/flowspec_cli/__init__.py; then
            echo "Version mismatch in __init__.py"
            exit 1
          fi

      - name: Build package
        run: uv build

      - name: Upload release artifacts
        uses: actions/upload-artifact@v4
        with:
          name: release-${{ github.event.inputs.version }}
          path: dist/
```

---

## 3. Verification Automation

### 3.1 Post-Upgrade Verification Script

**Location**: `scripts/bash/verify-upgrade.sh`

```bash
#!/usr/bin/env bash
# Verify upgrade-repo completed successfully
# Usage: ./verify-upgrade.sh /path/to/upgraded/repo

set -euo pipefail

REPO_PATH="${1:-.}"
cd "$REPO_PATH"

echo "=== Verifying upgrade-repo results ==="
echo "Repository: $REPO_PATH"
echo ""

# Track failures
FAILED=0

# Verification: Agent files use dot notation
echo "✓ Checking agent file naming..."
if ls .github/agents/flow-*.agent.md 2>/dev/null; then
    echo "  ❌ FAIL: Found hyphen-notation agent files"
    FAILED=1
else
    echo "  ✅ PASS: No hyphen-notation agent files"
fi

# Verification: Agent names are PascalCase
echo "✓ Checking agent names in frontmatter..."
for agent in .github/agents/*.agent.md; do
    if [ -f "$agent" ]; then
        if ! grep -q "^name: Flow[A-Z]" "$agent"; then
            echo "  ❌ FAIL: $agent does not have PascalCase name"
            FAILED=1
        fi
    fi
done
echo "  ✅ PASS: All agents have PascalCase names"

# Verification: flow.assess.agent.md exists
echo "✓ Checking for flow.assess.agent.md..."
if [ ! -f ".github/agents/flow.assess.agent.md" ]; then
    echo "  ❌ FAIL: flow.assess.agent.md missing"
    FAILED=1
else
    echo "  ✅ PASS: flow.assess.agent.md exists"
fi

# Verification: .mcp.json has required servers
echo "✓ Checking MCP configuration..."
if ! python3 -c "
import json
with open('.mcp.json') as f:
    config = json.load(f)
    required = ['backlog', 'github', 'serena']
    missing = [s for s in required if s not in config.get('mcpServers', {})]
    if missing:
        print(f'  ❌ FAIL: Missing MCP servers: {missing}')
        exit(1)
"; then
    FAILED=1
else
    echo "  ✅ PASS: All required MCP servers configured"
fi

# Verification: flowspec_workflow.yml is v2.0
echo "✓ Checking workflow config version..."
if ! python3 -c "
import yaml
with open('flowspec_workflow.yml') as f:
    config = yaml.safe_load(f)
    if config.get('version') != '2.0':
        print(f'  ❌ FAIL: Workflow version is {config.get(\"version\")}, expected 2.0')
        exit(1)
    if 'operate' in config.get('workflows', {}):
        print('  ❌ FAIL: Found operate workflow in v2.0 config')
        exit(1)
"; then
    FAILED=1
else
    echo "  ✅ PASS: Workflow config is v2.0"
fi

# Verification: Deprecated files removed
echo "✓ Checking for deprecated artifacts..."
if [ -d ".specify" ]; then
    echo "  ❌ FAIL: .specify directory still exists"
    FAILED=1
else
    echo "  ✅ PASS: .specify directory removed"
fi

if [ -f ".claude/commands/flow/_DEPRECATED_operate.md" ]; then
    echo "  ❌ FAIL: _DEPRECATED_operate.md still exists"
    FAILED=1
else
    echo "  ✅ PASS: _DEPRECATED_operate.md removed"
fi

# Verification: No /flow:operate references
echo "✓ Checking for /flow:operate references..."
if grep -r "/flow:operate" . 2>/dev/null | grep -v ".git" | grep -v "verify-upgrade.sh"; then
    echo "  ❌ FAIL: Found /flow:operate references"
    FAILED=1
else
    echo "  ✅ PASS: No /flow:operate references"
fi

# Verification: No {{INCLUDE:}} directives
echo "✓ Checking for broken INCLUDE directives..."
if grep -r "{{INCLUDE:" .claude/commands/ .github/ 2>/dev/null; then
    echo "  ❌ FAIL: Found {{INCLUDE:}} directives"
    FAILED=1
else
    echo "  ✅ PASS: No broken INCLUDE directives"
fi

# Verification: Skills synced (at least 21 skills)
echo "✓ Checking skills directory..."
skill_count=$(find .claude/skills -name "*.md" 2>/dev/null | wc -l)
if [ "$skill_count" -lt 21 ]; then
    echo "  ❌ FAIL: Expected 21+ skills, found $skill_count"
    FAILED=1
else
    echo "  ✅ PASS: Skills synced ($skill_count skills)"
fi

# Verification: Agent count (should be 6)
echo "✓ Checking agent count..."
agent_count=$(find .github/agents -name "*.agent.md" 2>/dev/null | wc -l)
if [ "$agent_count" -ne 6 ]; then
    echo "  ⚠️  WARNING: Expected 6 agents, found $agent_count"
else
    echo "  ✅ PASS: 6 agents present"
fi

echo ""
if [ $FAILED -eq 0 ]; then
    echo "=== All Verifications Passed ==="
    exit 0
else
    echo "=== Verification Failed ==="
    exit 1
fi
```

### 3.2 MCP Config Validator

**Location**: `scripts/bash/validate-mcp-config.sh`

```bash
#!/usr/bin/env bash
# Validate .mcp.json configuration
# Usage: ./validate-mcp-config.sh [path/to/.mcp.json]

set -euo pipefail

MCP_FILE="${1:-.mcp.json}"

echo "Validating MCP configuration: $MCP_FILE"

# Check file exists
if [ ! -f "$MCP_FILE" ]; then
    echo "❌ File not found: $MCP_FILE"
    exit 1
fi

# Validate JSON syntax
if ! python3 -c "import json; json.load(open('$MCP_FILE'))" 2>/dev/null; then
    echo "❌ Invalid JSON syntax"
    exit 1
fi

# Validate schema
python3 << 'EOF'
import json
import sys

with open('$MCP_FILE') as f:
    config = json.load(f)

# Required top-level key
if 'mcpServers' not in config:
    print("❌ Missing 'mcpServers' key")
    sys.exit(1)

# Required servers
required_servers = ['backlog', 'github', 'serena']
servers = config['mcpServers']

for server in required_servers:
    if server not in servers:
        print(f"❌ Missing required server: {server}")
        sys.exit(1)

    # Validate server structure
    if 'command' not in servers[server]:
        print(f"❌ Server '{server}' missing 'command' field")
        sys.exit(1)

print("✅ MCP configuration is valid")
EOF
```

### 3.3 Workflow Config Validator

**Location**: `scripts/bash/validate-workflow-config.sh`

```bash
#!/usr/bin/env bash
# Validate flowspec_workflow.yml configuration
# Usage: ./validate-workflow-config.sh [path/to/flowspec_workflow.yml]

set -euo pipefail

WORKFLOW_FILE="${1:-flowspec_workflow.yml}"

echo "Validating workflow configuration: $WORKFLOW_FILE"

# Check file exists
if [ ! -f "$WORKFLOW_FILE" ]; then
    echo "❌ File not found: $WORKFLOW_FILE"
    exit 1
fi

# Validate YAML syntax and schema
python3 << 'EOF'
import yaml
import sys

with open('$WORKFLOW_FILE') as f:
    config = yaml.safe_load(f)

# Check version
if config.get('version') != '2.0':
    print(f"❌ Expected version 2.0, got {config.get('version')}")
    sys.exit(1)

# Check no operate workflow
if 'operate' in config.get('workflows', {}):
    print("❌ Found deprecated 'operate' workflow")
    sys.exit(1)

# Check required workflows
required_workflows = ['assess', 'specify', 'plan', 'implement', 'validate']
workflows = config.get('workflows', {})

for workflow in required_workflows:
    if workflow not in workflows:
        print(f"❌ Missing required workflow: {workflow}")
        sys.exit(1)

# Check states
required_states = ['To Do', 'Assessed', 'Specified', 'Planned', 'In Implementation', 'Validated', 'Done']
states = config.get('states', [])

for state in required_states:
    if state not in states:
        print(f"❌ Missing required state: {state}")
        sys.exit(1)

# Check no 'Deployed' state (outer loop)
if 'Deployed' in states:
    print("❌ Found deprecated 'Deployed' state (outer loop)")
    sys.exit(1)

print("✅ Workflow configuration is valid")
EOF
```

---

## 4. Rollback Strategy

### 4.1 Current Backup Mechanism

The `upgrade-repo` command already creates timestamped backups:

```python
# From src/flowspec_cli/__init__.py line 5858
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
backup_dir = project_path / f".flowspec-backup-{timestamp}"

# Backed up directories
for dir_name in [".flowspec", ".claude", ".github", "templates"]:
    src = project_path / dir_name
    if src.exists():
        shutil.copytree(src, backup_dir / dir_name, dirs_exist_ok=True)
```

**Backup location**: `.flowspec-backup-YYYYMMDD-HHMMSS/`

### 4.2 Manual Rollback Procedure

**Location**: `docs/guides/upgrade-rollback.md`

```markdown
# Upgrade Rollback Guide

## Quick Rollback

If `flowspec upgrade-repo` causes issues, rollback manually:

```bash
# 1. Find the backup directory
ls -lt | grep flowspec-backup

# 2. Restore from backup
BACKUP_DIR=".flowspec-backup-20260106-143022"

# Restore directories
rm -rf .flowspec .claude .github templates
cp -r $BACKUP_DIR/.flowspec .
cp -r $BACKUP_DIR/.claude .
cp -r $BACKUP_DIR/.github .
cp -r $BACKUP_DIR/templates .

# 3. Verify restoration
git status
git diff

# 4. Commit rollback (if needed)
git add .
git commit -m "Rollback upgrade-repo changes"
```

## Automated Rollback (Future Enhancement)

```bash
# Proposed command (not yet implemented)
flowspec rollback-upgrade

# Or specify backup
flowspec rollback-upgrade --backup .flowspec-backup-20260106-143022
```
```

### 4.3 Proposed `flowspec rollback-upgrade` Command

**Implementation Notes**: Add to `src/flowspec_cli/__init__.py`

```python
@app.command()
def rollback_upgrade(
    backup_dir: Optional[str] = typer.Option(
        None, "--backup", help="Specific backup directory to restore from"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be restored"
    ),
):
    """
    Rollback upgrade-repo changes to previous state.

    Restores from the most recent .flowspec-backup-* directory
    unless --backup specifies a different backup.
    """
    project_path = Path.cwd()

    if backup_dir:
        backup_path = project_path / backup_dir
    else:
        # Find most recent backup
        backups = sorted(
            project_path.glob(".flowspec-backup-*"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        if not backups:
            console.print("[red]No backup directories found[/red]")
            raise typer.Exit(1)
        backup_path = backups[0]

    console.print(f"[cyan]Rolling back from:[/cyan] {backup_path.name}")

    if dry_run:
        console.print("[yellow]DRY RUN - would restore:[/yellow]")
        for dir_name in [".flowspec", ".claude", ".github", "templates"]:
            src = backup_path / dir_name
            if src.exists():
                console.print(f"  - {dir_name}/")
        return

    # Perform rollback
    for dir_name in [".flowspec", ".claude", ".github", "templates"]:
        backup_src = backup_path / dir_name
        target = project_path / dir_name

        if backup_src.exists():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(backup_src, target)
            console.print(f"[green]Restored:[/green] {dir_name}/")

    console.print("\n[bold green]Rollback complete![/bold green]")
    console.print(f"[dim]Restored from: {backup_path.name}[/dim]")
```

---

## 5. Developer Workflow Integration

### 5.1 Pre-Commit Hook

**Location**: `scripts/bash/pre-commit-upgrade-check.sh`

```bash
#!/usr/bin/env bash
# Pre-commit hook to validate upgrade-repo changes
# Install: ln -s ../../scripts/bash/pre-commit-upgrade-check.sh .git/hooks/pre-commit

set -e

# Only run if upgrade-repo related files changed
if ! git diff --cached --name-only | grep -qE "src/flowspec_cli/__init__.py|templates/"; then
    exit 0
fi

echo "Running upgrade-repo validation checks..."

# Run quality gates
./scripts/bash/quality-gates.sh

# Run relevant tests
uv run pytest tests/test_upgrade*.py -x

echo "✅ All pre-commit checks passed"
```

### 5.2 Local Testing Workflow

**Developer guide**: `docs/guides/testing-upgrade-repo-locally.md`

```markdown
# Testing upgrade-repo Locally

## Setup

```bash
# 1. Install development dependencies
uv sync

# 2. Create test fixtures
python tests/fixtures/create_mock_repos.py

# 3. Install flowspec locally
uv tool install . --force
```

## Run Tests

```bash
# Unit tests only
pytest tests/test_upgrade*.py -v

# Integration tests
pytest tests/integration/test_upgrade*.py -v

# E2E tests (slower)
pytest tests/e2e/test_upgrade*.py -v

# All upgrade tests
pytest tests/ -k upgrade -v

# With coverage
pytest tests/ -k upgrade --cov=src/flowspec_cli --cov-report=html
open htmlcov/index.html
```

## Manual Testing

```bash
# 1. Create test repo
mkdir /tmp/test-upgrade
cp -r tests/fixtures/mock_repos/v1.0-full/* /tmp/test-upgrade/

# 2. Run upgrade (dry-run first)
cd /tmp/test-upgrade
flowspec upgrade-repo --dry-run

# 3. Run actual upgrade
flowspec upgrade-repo

# 4. Verify results
/path/to/flowspec/scripts/bash/verify-upgrade.sh .

# 5. Clean up
cd -
rm -rf /tmp/test-upgrade
```

## Test Upgrade from Branch

```bash
# Test changes from a feature branch
flowspec upgrade-repo --branch jan6-2

# This builds templates from the branch locally
```
```

---

## 6. Quality Metrics and Success Criteria

### 6.1 Test Coverage Requirements

| Test Type | Target Coverage | Minimum Threshold |
|-----------|----------------|-------------------|
| Unit Tests | 90% | 80% |
| Integration Tests | 85% | 75% |
| E2E Tests | 70% | 60% |
| Overall | 85% | 80% |

### 6.2 Quality Gate Success Criteria

All quality gates must pass before merge:

1. ✅ **Zero `/flow:operate` references** in codebase
2. ✅ **Agent files use dot notation** (flow.X.agent.md)
3. ✅ **Agent names are PascalCase** (FlowAssess)
4. ✅ **No `{{INCLUDE:}}` directives** in templates
5. ✅ **MCP config has required servers** (backlog, github, serena)
6. ✅ **Workflow config is v2.0** (no operate workflow)
7. ✅ **All 21+ skills present** in templates

### 6.3 Verification Checklist for task-579.18

Final verification on auth.poley.dev:

- [ ] `flowspec upgrade-repo` runs successfully
- [ ] Agent files created: `flow.assess.agent.md`, `flow.specify.agent.md`, etc.
- [ ] Agent names visible in VSCode: `FlowAssess`, `FlowSpecify`, etc.
- [ ] `.mcp.json` has backlog, github, serena, playwright-test, trivy, semgrep
- [ ] `flowspec_workflow.yml` is version 2.0
- [ ] `.specify/` directory removed
- [ ] `_DEPRECATED_operate.md` removed
- [ ] 21 skills in `.claude/skills/`
- [ ] No `{{INCLUDE:}}` directives in `.github/prompts/`
- [ ] No `/flow:operate` in `CLAUDE.md` or anywhere else
- [ ] No `/spec:*` commands

---

## 7. Implementation Roadmap

### Phase 1: Test Infrastructure (Week 1)

**Days 1-2**: Test Fixtures
- [ ] Create mock repository fixtures (v1.0-minimal, v1.0-full, v1.0-custom, v2.0-current)
- [ ] Implement `create_mock_repos.py` fixture generator
- [ ] Test fixtures with pytest parametrize

**Days 3-4**: Unit Tests
- [ ] Write unit tests for each P0 task (task-579.01 through 579.06)
- [ ] Add tests for MCP generation, skills sync, workflow migration
- [ ] Achieve 80%+ unit test coverage

**Day 5**: Integration Tests
- [ ] Write full upgrade-repo workflow integration tests
- [ ] Test preservation of user customizations
- [ ] Test idempotency (running upgrade twice)

### Phase 2: CI/CD Pipelines (Week 2)

**Days 1-2**: Quality Gates
- [ ] Implement `quality-gates.sh` script
- [ ] Add quality gate checks to CI pipeline
- [ ] Test locally and in CI environment

**Days 3-4**: CI/CD Workflows
- [ ] Create PR validation workflow
- [ ] Create post-merge validation workflow
- [ ] Create release gate workflow

**Day 5**: Verification Scripts
- [ ] Implement `verify-upgrade.sh` script
- [ ] Implement MCP and workflow config validators
- [ ] Test on auth.poley.dev (dry-run)

### Phase 3: E2E Tests & Documentation (Week 3)

**Days 1-2**: E2E Tests
- [ ] Write E2E tests for realistic upgrade scenarios
- [ ] Test branch-based upgrades
- [ ] Test dry-run mode

**Days 3-4**: Documentation
- [ ] Write `upgrade-rollback.md` guide
- [ ] Write `testing-upgrade-repo-locally.md` guide
- [ ] Update existing docs with new testing procedures

**Day 5**: Final Verification
- [ ] Run full test suite
- [ ] Run all quality gates
- [ ] Verify on auth.poley.dev (actual upgrade)
- [ ] Sign off on task-579.18

---

## 8. Monitoring and Observability

### 8.1 Metrics to Track

**CI/CD Metrics**:
- Test execution time (target: <5 minutes for PR checks)
- Test pass rate (target: >95%)
- Code coverage trend (track over time)
- Quality gate pass rate

**Upgrade Metrics** (track in telemetry):
- upgrade-repo invocations
- upgrade success rate
- upgrade duration
- rollback frequency

### 8.2 Alerting

**GitHub Actions Alerts**:
- Failed quality gates on PR
- Test failures on main branch
- Coverage drop below threshold

**Runtime Alerts** (future):
- upgrade-repo failures (captured in telemetry)
- MCP configuration errors
- Workflow config validation failures

---

## 9. Security Considerations

### 9.1 Template Injection Prevention

**Risk**: User-provided data in templates could execute arbitrary code

**Mitigation**:
- Templates use static content only
- No dynamic template rendering with user input
- Placeholder replacement uses safe string substitution

### 9.2 Backup Security

**Risk**: Backups may contain sensitive data (tokens, credentials)

**Mitigation**:
- Backups stored locally in project (not uploaded)
- Add `.flowspec-backup-*` to `.gitignore`
- Document backup cleanup in rollback guide

### 9.3 Supply Chain Security

**Risk**: Malicious templates from compromised GitHub releases

**Mitigation**:
- Pin template versions with `--base-version` and `--extension-version`
- Verify checksums of downloaded archives (future enhancement)
- Use branch-based upgrades for testing only (not production)

---

## 10. Future Enhancements

### 10.1 Automated Rollback Command

Implement `flowspec rollback-upgrade` as described in Section 4.3.

### 10.2 Upgrade Health Checks

Add post-upgrade health checks:
```bash
flowspec health-check
```

Validates:
- MCP servers are connectable
- Skills can be loaded
- Workflow config is valid
- Agent files are well-formed

### 10.3 Upgrade Telemetry

Track upgrade patterns:
- Most common upgrade paths (v1.0 → v2.0)
- Failure modes and error messages
- Average upgrade duration
- Rollback frequency

### 10.4 Differential Upgrades

Only upgrade changed files:
```bash
flowspec upgrade-repo --diff
```

Shows what changed between versions and allows selective upgrades.

---

## 11. References

### Internal Documents
- [Flowspec Release Alignment Plan](../building/fix-flowspec-plan.md)
- [Epic Task 579](../../backlog/tasks/task-579%20-%20EPIC-Flowspec-Release-Alignment-Fix-upgrade-repo-and-Agent-Integration.md)
- [Verification Task 579.18](../../backlog/tasks/task-579.18%20-%20P5-Verification-Test-upgrade-repo-fixes-on-auth.poley.dev.md)

### Code Locations
- Main CLI: `src/flowspec_cli/__init__.py`
- Tests: `tests/test_upgrade*.py`
- CI/CD: `.github/workflows/ci.yml`
- Templates: `templates/`

### External Resources
- [pytest Documentation](https://docs.pytest.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [uv Documentation](https://docs.astral.sh/uv/)

---

## Appendix A: Test File Structure

```
tests/
├── fixtures/
│   ├── mock_repos/
│   │   ├── v1.0-minimal/
│   │   ├── v1.0-full/
│   │   ├── v1.0-custom/
│   │   └── v2.0-current/
│   └── create_mock_repos.py
├── test_upgrade_repo_enhancements.py       # Unit tests for each P0 fix
├── integration/
│   └── test_upgrade_repo_workflow.py       # Multi-component integration tests
├── e2e/
│   └── test_upgrade_repo_e2e.py            # End-to-end realistic scenarios
└── conftest.py                             # Shared fixtures
```

## Appendix B: CI/CD Workflow Structure

```
.github/workflows/
├── pr-upgrade-validation.yml               # Pre-merge PR checks
├── post-merge-validation.yml               # Post-merge integration tests
├── release-gate.yml                        # Release validation
└── ci.yml (existing)                       # General CI (lint, test, build)
```

## Appendix C: Script Structure

```
scripts/bash/
├── quality-gates.sh                        # Automated quality checks
├── verify-upgrade.sh                       # Post-upgrade verification
├── validate-mcp-config.sh                  # MCP config validator
├── validate-workflow-config.sh             # Workflow config validator
└── pre-commit-upgrade-check.sh             # Pre-commit hook
```

---

**Sign-off**: This platform design provides comprehensive testing, CI/CD, and verification infrastructure for the flowspec upgrade-repo fixes. All 18 subtasks under epic task-579 can be validated automatically through this infrastructure before release.

**Next Steps**:
1. Create test fixtures (mock repositories)
2. Implement unit tests for P0 tasks
3. Set up quality gates script
4. Configure CI/CD pipelines
5. Test on auth.poley.dev (dry-run)
6. Execute final verification (task-579.18)
