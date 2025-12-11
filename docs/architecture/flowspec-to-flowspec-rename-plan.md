# Command Namespace Rename: flowspec → flowspec

**Architecture Plan**
**Status**: Planning
**Author**: Enterprise Software Architect
**Date**: 2025-12-10
**Scope**: Complete namespace rename across jp-spec-kit codebase

---

## Executive Summary

This document provides a comprehensive architecture plan for renaming the `flowspec` command namespace to `flowspec` (and `/flow:` to `/flow:`) across the jp-spec-kit project. The rename addresses a critical UX issue where `/spec` command completion conflicts between `flowspec` and `speckit` commands.

**Impact Scope**: 397 files requiring changes across:
- Command directories and templates (32 files)
- GitHub agents and prompts (46 files)
- Tests (14 test files + coverage files)
- Source code (20 Python files)
- Configuration files (3 YAML/JSON schema files)
- Documentation (300+ markdown files)

**Estimated Effort**: 8-12 hours (excluding testing and validation)

**Risk Level**: MEDIUM (large surface area, but precedent exists from previous `jpspec` → `flowspec` rename)

---

## 1. Strategic Framing (Penthouse View)

### 1.1 Business Justification

**Problem Statement**:
When users type `/spec` in command completion (VS Code Copilot, Claude Desktop):
- `/flow:*` commands appear
- `/speckit:*` commands appear
- Creates cognitive load and poor UX

**Solution**:
Rename `/flow:*` → `/flow:*` to:
- Eliminate namespace collision
- Improve command discoverability
- Maintain semantic clarity ("flow" = workflow commands)

**Strategic Benefits**:
1. **Improved Developer Experience**: Clear separation between workflow commands (`/flow:*`) and utility commands (`/speckit:*`)
2. **Reduced Cognitive Load**: Less mental mapping required when selecting commands
3. **Future-Proof Namespace**: Opens `/spec*` namespace for future expansion
4. **Consistent Branding**: "FlowSpec" aligns with "Spec-Driven Development" positioning

### 1.2 Risk Assessment

| Risk Category | Level | Mitigation |
|--------------|-------|------------|
| **Breaking Changes** | HIGH | Create deprecation aliases, update migration guide |
| **Test Coverage Gaps** | MEDIUM | Comprehensive test suite update, regression testing |
| **Documentation Drift** | MEDIUM | Automated verification of docs consistency |
| **User Migration Burden** | LOW | Most users haven't adopted yet (pre-1.0 release) |
| **Regression Bugs** | MEDIUM | Phased rollout, extensive testing |

**Risk Mitigation Strategy**:
- Leverage existing precedent from `jpspec` → `flowspec` rename (Dec 2024)
- Comprehensive test coverage before/after rename
- Migration guide for existing users
- Deprecation warnings (not breaking immediately)

### 1.3 Backward Compatibility Strategy

**Phase 1: Dual Support (v0.3.x)**
- Both `/flow:*` and `/flow:*` commands work
- `/flow:*` shows deprecation warning
- `flowspec_workflow.yml` still supported (deprecated)
- Update documentation to reference new names

**Phase 2: Deprecation (v0.4.x)**
- `/flow:*` commands marked deprecated in CLI help
- Warning messages guide users to `/flow:*`
- `flowspec_workflow.yml` becomes primary config

**Phase 3: Removal (v1.0.0)**
- Remove `/flow:*` command aliases
- Only `flowspec_workflow.yml` supported
- Legacy `flowspec_workflow.yml` → migration error

**Timeline**: 2-3 release cycles (~3-6 months)

---

## 2. Architectural Blueprint (Engine Room View)

### 2.1 Phased Rename Approach

```
Phase 1: Infrastructure (Files & Directories)
  ├─ Directory renames (.claude/commands/flowspec → flow)
  ├─ Template renames (templates/commands/flowspec → flow)
  ├─ Schema renames (flowspec_workflow.* → flowspec_workflow.*)
  └─ Test file renames (test_flowspec_*.py → test_flowspec_*.py)

Phase 2: Content Updates (String Replacements)
  ├─ Source code (*.py files)
  ├─ GitHub agents (*.agent.md files)
  ├─ GitHub prompts (*.prompt.md files)
  ├─ Documentation (*.md files)
  ├─ Shell scripts (*.sh files)
  └─ Configuration (*.yml, *.json files)

Phase 3: Symlinks & Aliases
  ├─ Create backward-compatible symlinks
  ├─ Add deprecation warnings
  └─ Update CLI help text

Phase 4: Validation & Testing
  ├─ Run full test suite
  ├─ Verify command execution
  ├─ Test workflow state transitions
  └─ Validate MCP server integration
```

### 2.2 Dependency Analysis

**Critical Path** (must be done in order):

1. **Schema & Config Files** (blocking all else)
   - `flowspec_workflow.schema.json` → `flowspec_workflow.schema.json`
   - `flowspec_workflow.yml` → `flowspec_workflow.yml`
   - `src/specify_cli/workflow/config.py` (constant updates)

2. **Source Code** (blocking tests)
   - All `*.py` files in `src/specify_cli/workflow/`
   - CLI command registration in `src/specify_cli/__init__.py`
   - Task context in `src/specify_cli/task_context.py`

3. **Tests** (blocking validation)
   - Test file renames
   - Test assertion updates
   - Fixture updates

4. **Commands & Templates** (blocking E2E testing)
   - `.claude/commands/flowspec/` → `.claude/commands/flow/`
   - `templates/commands/flowspec/` → `templates/commands/flow/`
   - Agent handoff updates in `*.agent.md`

5. **Documentation** (non-blocking, can be parallel)
   - All `*.md` files
   - Diagrams (excalidraw, mermaid)

**Parallel Workstreams**:
- Documentation updates (can run in parallel with code changes)
- Shell script updates (isolated from Python code)
- GitHub workflow updates (isolated from core logic)

### 2.3 Symlink Handling Strategy

**Current State**:
```bash
.claude/commands/flowspec/assess.md → templates/commands/flowspec/assess.md
.claude/commands/flowspec/implement.md → templates/commands/flowspec/implement.md
# ... 17 total symlinks
```

**Rename Strategy**:
1. **Break existing symlinks** (they become dangling after directory rename)
2. **Rename target directory** (`templates/commands/flowspec/` → `templates/commands/flow/`)
3. **Recreate symlinks with new paths**:
   ```bash
   .claude/commands/flow/assess.md → templates/commands/flow/assess.md
   ```
4. **Create backward-compatible symlinks** (deprecation phase):
   ```bash
   .claude/commands/flowspec/ → .claude/commands/flow/  # Directory symlink
   ```

**Implementation**:
```bash
# Remove old symlinks
rm -rf .claude/commands/flowspec/

# Rename template directory
mv templates/commands/flowspec/ templates/commands/flow/

# Recreate symlinks
mkdir -p .claude/commands/flow/
for file in templates/commands/flow/*.md; do
  ln -s "$(realpath $file)" ".claude/commands/flow/$(basename $file)"
done

# Create backward-compatible directory symlink (Phase 1 only)
ln -s flow .claude/commands/flowspec
```

### 2.4 Test Infrastructure Considerations

**Test Files Requiring Rename** (14 files):
```
tests/test_flowspec_assess.py → tests/test_flowspec_assess.py
tests/test_flowspec_backlog_integration.py → tests/test_flowspec_backlog_integration.py
tests/test_flowspec_e2e.py → tests/test_flowspec_e2e.py
tests/test_flowspec_implement_backlog.py → tests/test_flowspec_implement_backlog.py
tests/test_flowspec_operate_backlog.py → tests/test_flowspec_operate_backlog.py
tests/test_flowspec_plan_backlog.py → tests/test_flowspec_plan_backlog.py
tests/test_flowspec_research_backlog.py → tests/test_flowspec_research_backlog.py
tests/test_flowspec_specify_backlog.py → tests/test_flowspec_specify_backlog.py
tests/test_flowspec_validate_backlog.py → tests/test_flowspec_validate_backlog.py
tests/test_flowspec_workflow_integration.py → tests/test_flowspec_workflow_integration.py
tests/test_flowspec_workflow_roles.py → tests/test_flowspec_workflow_roles.py
```

**Test Fixture Updates**:
- Fixture files in `tests/fixtures/` referencing `flowspec_workflow.yml`
- Mock config loaders expecting old filenames
- Test data referencing old command names

**Test Assertions Updates**:
```python
# Before
assert "flowspec_workflow.yml" in files
assert cmd == "/flow:assess"

# After
assert "flowspec_workflow.yml" in files
assert cmd == "/flow:assess"
```

---

## 3. Architecture Decision Record (ADR)

**ADR-XXX: Rename Command Namespace from flowspec to flowspec**

### Context

The current command namespace `/flow:*` creates UX friction:
1. Conflicts with `/speckit:*` commands when typing `/spec`
2. Users must type more characters to disambiguate
3. Command completion shows both namespaces confusingly

Workflow commands (assess, specify, plan, implement, validate, operate) are conceptually distinct from utility commands (configure, analyze, tasks) and deserve a separate namespace.

### Decision Drivers

1. **User Experience**: Minimize keystrokes for common commands
2. **Namespace Clarity**: Separate workflow commands from utility commands
3. **Future Extensibility**: Open `/spec*` namespace for future expansion
4. **Semantic Meaning**: "Flow" accurately describes workflow progression
5. **Implementation Cost**: Precedent exists from `jpspec` → `flowspec` rename

### Options Considered

#### Option 1: Full Rename (flowspec → flowspec, /flow: → /flow:)
**Pros**:
- Complete consistency (internal names match external commands)
- Clear semantic distinction ("flow" = workflow)
- Opens `/spec*` namespace for future use
- Eliminates all namespace conflicts

**Cons**:
- Large surface area (397 files)
- Requires comprehensive testing
- Breaking change for existing users
- Documentation update burden

**Decision**: SELECTED

#### Option 2: Command-Only Rename (/flow: → /flow:, keep internal flowspec)
**Pros**:
- Smaller surface area (only command registration)
- Less test churn
- Faster implementation

**Cons**:
- Creates inconsistency (external names ≠ internal names)
- Confusing for contributors reading code
- Still requires documentation updates
- Doesn't solve internal namespace clarity

**Decision**: REJECTED (inconsistency risk)

#### Option 3: Keep flowspec, Rename speckit
**Pros**:
- Smaller surface area (only speckit changes)
- Doesn't affect workflow commands

**Cons**:
- `speckit` is the better name (spec = specification tools)
- Workflow commands are less frequent (should require more typing)
- Inverts the correct semantic hierarchy

**Decision**: REJECTED (wrong semantic prioritization)

### Consequences

**Positive**:
- Improved command discoverability and UX
- Clear semantic separation (workflow vs. utility)
- Opens namespace for future expansion
- Better aligns with product positioning

**Negative**:
- Large one-time migration cost (8-12 hours)
- Breaking change for early adopters (mitigated by deprecation phase)
- Documentation must be comprehensively updated
- Risk of missed references in edge cases

**Neutral**:
- Establishes precedent for namespace management
- Reinforces importance of UX testing before 1.0 release

### Implementation Plan

See sections 4-7 below.

---

## 4. File Rename Strategy

### 4.1 File Classification Matrix

| Category | Risk Level | File Count | Examples | Dependencies |
|----------|-----------|------------|----------|--------------|
| **A: Schema & Config** | CRITICAL | 3 | `flowspec_workflow.yml`, `*.schema.json` | Blocks all else |
| **B: Source Code** | HIGH | 20 | `src/specify_cli/workflow/*.py` | Blocks tests |
| **C: Command Directories** | HIGH | 2 | `.claude/commands/flowspec/`, `templates/commands/flowspec/` | Blocks E2E tests |
| **D: GitHub Agents** | MEDIUM | 15 | `.github/agents/flowspec-*.agent.md` | Parallel with B |
| **E: GitHub Prompts** | MEDIUM | 31 | `.github/prompts/flowspec.*.prompt.md` | Parallel with B |
| **F: Tests** | MEDIUM | 14 | `tests/test_flowspec_*.py` | Depends on B |
| **G: Documentation** | LOW | 300+ | `docs/**/*.md` | Parallel (non-blocking) |
| **H: Shell Scripts** | LOW | 7 | `scripts/**/*.sh` | Parallel (non-blocking) |
| **I: JSON Configs** | LOW | 6 | `*.mcp.json`, plugins | Parallel (non-blocking) |

### 4.2 Category A: Schema & Config Files (CRITICAL)

**Files**:
```
memory/flowspec_workflow.yml → memory/flowspec_workflow.yml
schemas/flowspec_workflow.schema.json → schemas/flowspec_workflow.schema.json
flowspec_workflow.yml → flowspec_workflow.yml (project root)
```

**Rename Script**:
```bash
#!/bin/bash
# Phase 1: Rename schema and config files

# Rename schema
git mv schemas/flowspec_workflow.schema.json schemas/flowspec_workflow.schema.json

# Rename memory config
git mv memory/flowspec_workflow.yml memory/flowspec_workflow.yml

# Rename root config
git mv flowspec_workflow.yml flowspec_workflow.yml

# Update schema references
sed -i '' 's/flowspec_workflow\.schema\.json/flowspec_workflow.schema.json/g' schemas/flowspec_workflow.schema.json
sed -i '' 's/flowspec_workflow\.yml/flowspec_workflow.yml/g' schemas/flowspec_workflow.schema.json
```

**Critical Update**: `src/specify_cli/workflow/config.py`
```python
# Before
DEFAULT_CONFIG_NAMES = [
    "flowspec_workflow.yml",
    "flowspec_workflow.yaml",
]

DEFAULT_SCHEMA_PATHS = [
    "schemas/flowspec_workflow.schema.json",
    "memory/flowspec_workflow.schema.json",
]

# After (with backward compatibility)
DEFAULT_CONFIG_NAMES = [
    "flowspec_workflow.yml",      # v0.3+ (preferred)
    "flowspec_workflow.yaml",
    "flowspec_workflow.yml",      # v0.2 (deprecated)
    "flowspec_workflow.yaml",
]

DEFAULT_SCHEMA_PATHS = [
    "schemas/flowspec_workflow.schema.json",  # v0.3+ (preferred)
    "schemas/flowspec_workflow.schema.json",  # v0.2 (deprecated)
    "memory/flowspec_workflow.schema.json",
    "memory/flowspec_workflow.schema.json",
]
```

### 4.3 Category B: Source Code (HIGH)

**Files** (20 Python files):
```
src/specify_cli/workflow/config.py
src/specify_cli/workflow/validator.py
src/specify_cli/workflow/assessor.py
src/specify_cli/workflow/state_guard.py
src/specify_cli/task_context.py
src/specify_cli/__init__.py
src/specify_cli/hooks/events.py
src/specify_cli/hooks/cli.py
src/specify_cli/security/config/models.py
src/specify_cli/security/config/loader.py
src/specify_cli/security/exporters/sarif.py
src/specify_cli/security/integrations/hooks.py
src/specify_cli/security/integrations/cicd.py
src/specify_cli/security/mcp_server.py
src/specify_cli/memory/mcp.py
src/specify_cli/vscode/settings_generator.py
```

**Rename Script**:
```bash
#!/bin/bash
# Phase 2: Update source code references

# Find all Python files with flowspec references
find src/specify_cli -name "*.py" -type f | while read file; do
  # Create backup
  cp "$file" "$file.bak"

  # Replace flowspec → flowspec (case-sensitive)
  sed -i '' 's/flowspec/flowspec/g' "$file"

  # Replace FLOWSPEC → FLOWSPEC (constants)
  sed -i '' 's/FLOWSPEC/FLOWSPEC/g' "$file"

  # Replace /flow: → /flow:
  sed -i '' 's/\/flow:/\/flow:/g' "$file"

  # Display changes
  echo "Updated: $file"
  diff "$file.bak" "$file" || true
done
```

**Special Attention**:
- CLI command registration in `__init__.py`
- Docstrings and comments (manual review)
- Error messages referencing old names

### 4.4 Category C: Command Directories (HIGH)

**Directories**:
```
.claude/commands/flowspec/ → .claude/commands/flow/
templates/commands/flowspec/ → templates/commands/flow/
```

**Rename Script**:
```bash
#!/bin/bash
# Phase 3: Rename command directories and recreate symlinks

# Remove existing symlinks
rm -rf .claude/commands/flowspec/

# Rename template directory
git mv templates/commands/flowspec templates/commands/flow

# Create new flow directory
mkdir -p .claude/commands/flow/

# Recreate symlinks
for file in templates/commands/flow/*.md; do
  basename_file=$(basename "$file")
  ln -s "../../../templates/commands/flow/$basename_file" ".claude/commands/flow/$basename_file"
done

# Create backward-compatible symlink (Phase 1 deprecation)
ln -s flow .claude/commands/flowspec
```

**Command Files** (17 files in each directory):
```
_backlog-instructions.md
_constitution-check.md
_workflow-state.md
assess.md
implement.md
init.md
operate.md
plan.md
research.md
reset.md
security_fix.md
security_report.md
security_triage.md
security_web.md
security_workflow.md
specify.md
validate.md
```

### 4.5 Category D: GitHub Agents (MEDIUM)

**Files** (15 agents):
```
.github/agents/flowspec-assess.agent.md → .github/agents/flow-assess.agent.md
.github/agents/flowspec-implement.agent.md → .github/agents/flow-implement.agent.md
.github/agents/flowspec-init.agent.md → .github/agents/flow-init.agent.md
.github/agents/flowspec-operate.agent.md → .github/agents/flow-operate.agent.md
.github/agents/flowspec-plan.agent.md → .github/agents/flow-plan.agent.md
.github/agents/flowspec-prune-branch.agent.md → .github/agents/flow-prune-branch.agent.md
.github/agents/flowspec-research.agent.md → .github/agents/flow-research.agent.md
.github/agents/flowspec-reset.agent.md → .github/agents/flow-reset.agent.md
.github/agents/flowspec-security_fix.agent.md → .github/agents/flow-security_fix.agent.md
.github/agents/flowspec-security_report.agent.md → .github/agents/flow-security_report.agent.md
.github/agents/flowspec-security_triage.agent.md → .github/agents/flow-security_triage.agent.md
.github/agents/flowspec-security_web.agent.md → .github/agents/flow-security_web.agent.md
.github/agents/flowspec-security_workflow.agent.md → .github/agents/flow-security_workflow.agent.md
.github/agents/flowspec-specify.agent.md → .github/agents/flow-specify.agent.md
.github/agents/flowspec-validate.agent.md → .github/agents/flow-validate.agent.md
```

**Rename Script**:
```bash
#!/bin/bash
# Phase 4: Rename GitHub agent files

cd .github/agents/

for file in flowspec-*.agent.md; do
  newfile="${file/flowspec-/flow-}"
  git mv "$file" "$newfile"
  echo "Renamed: $file → $newfile"
done
```

**Content Updates** (handoffs):
```yaml
# Before
handoffs:
  - label: "Conduct Research"
    agent: "flowspec-research"

# After
handoffs:
  - label: "Conduct Research"
    agent: "flow-research"
```

### 4.6 Category E: GitHub Prompts (MEDIUM)

**Files** (31 prompts):
```
.github/prompts/flowspec._backlog-instructions.prompt.md
.github/prompts/flowspec._constitution-check.prompt.md
.github/prompts/flowspec._DEPRECATED_*.prompt.md (10 files)
.github/prompts/flowspec.assess.prompt.md
.github/prompts/flowspec.implement.prompt.md
.github/prompts/flowspec.init.prompt.md
.github/prompts/flowspec.operate.prompt.md
.github/prompts/flowspec.plan.prompt.md
.github/prompts/flowspec.research.prompt.md
.github/prompts/flowspec.reset.prompt.md
.github/prompts/flowspec.security_*.prompt.md (5 files)
.github/prompts/flowspec.specify.prompt.md
.github/prompts/flowspec.validate.prompt.md
```

**Rename Pattern**:
```bash
flowspec.{command}.prompt.md → flow.{command}.prompt.md
```

**Rename Script**:
```bash
#!/bin/bash
# Phase 5: Rename GitHub prompt files

cd .github/prompts/

for file in flowspec.*.prompt.md; do
  newfile="${file/flowspec./flow.}"
  git mv "$file" "$newfile"
  echo "Renamed: $file → $newfile"
done
```

### 4.7 Category F: Tests (MEDIUM)

**Test Files** (14 files):
```bash
git mv tests/test_flowspec_assess.py tests/test_flowspec_assess.py
git mv tests/test_flowspec_backlog_integration.py tests/test_flowspec_backlog_integration.py
git mv tests/test_flowspec_e2e.py tests/test_flowspec_e2e.py
git mv tests/test_flowspec_implement_backlog.py tests/test_flowspec_implement_backlog.py
git mv tests/test_flowspec_operate_backlog.py tests/test_flowspec_operate_backlog.py
git mv tests/test_flowspec_plan_backlog.py tests/test_flowspec_plan_backlog.py
git mv tests/test_flowspec_research_backlog.py tests/test_flowspec_research_backlog.py
git mv tests/test_flowspec_specify_backlog.py tests/test_flowspec_specify_backlog.py
git mv tests/test_flowspec_validate_backlog.py tests/test_flowspec_validate_backlog.py
git mv tests/test_flowspec_workflow_integration.py tests/test_flowspec_workflow_integration.py
git mv tests/test_flowspec_workflow_roles.py tests/test_flowspec_workflow_roles.py
```

**Content Updates**:
```python
# Update test imports
from specify_cli.workflow.config import WorkflowConfig

# Update test fixtures
@pytest.fixture
def flowspec_config():
    return WorkflowConfig.load("flowspec_workflow.yml")

# Update test assertions
assert "flowspec_workflow.yml" in files
assert result.command == "/flow:assess"
```

### 4.8 Category G: Documentation (LOW)

**File Count**: 300+ markdown files

**High-Priority Docs**:
```
CLAUDE.md
README.md
CONTRIBUTING.md
docs/guides/flowspec-backlog-workflow.md → docs/guides/flowspec-backlog-workflow.md
docs/guides/flowspec-workflow-guide.md → docs/guides/flowspec-workflow-guide.md
docs/reference/flowspec-security-commands.md → docs/reference/flowspec-security-commands.md
docs/flowspec-workflow-reference.md → docs/flowspec-workflow-reference.md
docs/flowspec-workflow-spec.md → docs/flowspec-workflow-spec.md
```

**Rename Script** (documentation files):
```bash
#!/bin/bash
# Phase 6: Rename documentation files

find docs -name "*flowspec*" -type f | while read file; do
  newfile="${file/flowspec/flowspec}"
  git mv "$file" "$newfile"
  echo "Renamed: $file → $newfile"
done
```

**Content Update Strategy**:
- Automated find/replace for most files
- Manual review for architectural diagrams
- Update code examples and command references

### 4.9 Category H: Shell Scripts (LOW)

**Files** (7 scripts):
```
scripts/bash/install-claude-code-config.sh
scripts/bash/setup-claude-code.sh
.github/workflows/scripts/create-release-packages.sh
```

**Update Script**:
```bash
#!/bin/bash
# Phase 7: Update shell scripts

find scripts .github/workflows -name "*.sh" -type f | while read file; do
  sed -i '' 's/flowspec/flowspec/g' "$file"
  sed -i '' 's/\/flow:/\/flow:/g' "$file"
  echo "Updated: $file"
done
```

### 4.10 Category I: JSON Configs (LOW)

**Files**:
```
.mcp.json
.vscode/settings.json
.vscode/tasks.json
package.json (if exists)
```

**Update Script**:
```bash
#!/bin/bash
# Phase 8: Update JSON configs

find . -maxdepth 2 -name "*.json" -type f | while read file; do
  # Skip node_modules
  if [[ "$file" == *"node_modules"* ]]; then
    continue
  fi

  sed -i '' 's/flowspec/flowspec/g' "$file"
  sed -i '' 's/\/flow:/\/flow:/g' "$file"
  echo "Updated: $file"
done
```

---

## 5. Content Update Strategy

### 5.1 String Replacement Patterns

**Pattern 1: Command References**
```bash
# Pattern
/flow:

# Replacement
/flow:

# Examples
/flow:assess → /flow:assess
/flow:implement → /flow:implement
```

**Pattern 2: Config File References**
```bash
# Pattern
flowspec_workflow

# Replacement
flowspec_workflow

# Examples
flowspec_workflow.yml → flowspec_workflow.yml
flowspec_workflow.schema.json → flowspec_workflow.schema.json
```

**Pattern 3: Internal Identifiers**
```bash
# Pattern
flowspec

# Replacement
flowspec

# Examples
FlowspecConfig → FlowspecConfig
flowspec_validator → flowspec_validator
FLOWSPEC_PATH → FLOWSPEC_PATH
```

**Pattern 4: Agent Names**
```bash
# Pattern
flowspec-{command}

# Replacement
flow-{command}

# Examples
flowspec-assess → flow-assess
flowspec-implement → flow-implement
```

**Pattern 5: Prompt Names**
```bash
# Pattern
flowspec.{command}.prompt.md

# Replacement
flow.{command}.prompt.md

# Examples
flowspec.assess.prompt.md → flow.assess.prompt.md
```

### 5.2 Regex Patterns for Safe Replacement

**Python Source Code**:
```regex
# Match flowspec identifiers (avoid partial matches)
\bflowspec\b → flowspec
\bFlowspec\b → Flowspec
\bFLOWSPEC\b → FLOWSPEC

# Match command strings
["/]flowspec: → /flow:
["']flowspec["'] → "flowspec"

# Match file paths
flowspec_workflow\. → flowspec_workflow.
```

**Markdown Documentation**:
```regex
# Match command references
`/flow:(\w+)` → `/flow:\1`

# Match code blocks
```bash
/flow:assess
```
→
```bash
/flow:assess
```

# Match file references
`flowspec_workflow\.yml` → `flowspec_workflow.yml`

# Match headers
## Flowspec → ## Flowspec
### /flow: → ### /flow:
```

**YAML/JSON Configuration**:
```regex
# Match keys
"flowspec": → "flowspec":
flowspec: → flowspec:

# Match command strings
command: "/flow: → command: "/flow:
```

### 5.3 Exclusions (DO NOT REPLACE)

**Git History References**:
```
# Keep git branch names as-is
.git/refs/*/rename-jpspec-to-flowspec
.git/logs/*/rename-jpspec-to-flowspec
```

**Historical Documentation**:
```
# Keep migration guides referencing old names
docs/migrations/jpspec-to-flowspec.md
docs/CHANGELOG.md (keep historical entries)
```

**Comments Explaining Changes**:
```python
# GOOD: Keep historical context
# Prior to v0.3, this was called flowspec_workflow.yml

# BAD: Don't blindly replace historical references
# This function was renamed from flowspec_validator → flowspec_validator
```

### 5.4 Automated Replacement Script

```bash
#!/bin/bash
# comprehensive-rename.sh
# Comprehensive find/replace across all file types

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counter for changes
total_files_changed=0

echo -e "${GREEN}Starting comprehensive flowspec → flowspec rename${NC}"
echo "=============================================="

# Function to process files
process_files() {
  local pattern="$1"
  local description="$2"

  echo -e "\n${YELLOW}Processing: $description${NC}"

  find . -type f \
    -not -path "./.git/*" \
    -not -path "./node_modules/*" \
    -not -path "./.venv/*" \
    -not -path "*/__pycache__/*" \
    -not -path "*.pyc" \
    -not -path "*/tests/fixtures/*" \
    $pattern | while read file; do

    # Skip binary files
    if file "$file" | grep -q "text"; then
      # Create backup
      cp "$file" "$file.rename.bak"

      # Perform replacements
      sed -i '' \
        -e 's/\bflowspec_workflow\b/flowspec_workflow/g' \
        -e 's/\bflowspec\b/flowspec/g' \
        -e 's/\bFlowspec\b/Flowspec/g' \
        -e 's/\bFLOWSPEC\b/FLOWSPEC/g' \
        -e 's|/flow:|/flow:|g' \
        -e 's/flowspec-/flow-/g' \
        "$file"

      # Check if file changed
      if ! cmp -s "$file" "$file.rename.bak"; then
        echo "  ✓ Updated: $file"
        total_files_changed=$((total_files_changed + 1))
      else
        # No changes, remove backup
        rm "$file.rename.bak"
      fi
    fi
  done
}

# Process different file types
process_files '-name "*.py"' "Python source files"
process_files '-name "*.md"' "Markdown documentation"
process_files '-name "*.yml" -o -name "*.yaml"' "YAML configuration"
process_files '-name "*.json"' "JSON configuration"
process_files '-name "*.sh"' "Shell scripts"
process_files '-name "*.toml"' "TOML configuration"

echo -e "\n${GREEN}Rename complete!${NC}"
echo "Total files changed: $total_files_changed"
echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Review changes: git diff"
echo "2. Run tests: pytest tests/"
echo "3. Check for missed references: rg 'flowspec' --type-not py"
echo "4. Remove backup files: find . -name '*.rename.bak' -delete"
```

---

## 6. Testing Strategy

### 6.1 Pre-Rename Baseline

**Capture Current State**:
```bash
# Run full test suite
pytest tests/ -v --tb=short > pre-rename-test-results.txt

# Capture test coverage
pytest tests/ --cov=src/specify_cli --cov-report=html --cov-report=term > pre-rename-coverage.txt

# Capture linting state
ruff check . > pre-rename-lint.txt 2>&1

# Count references
rg 'flowspec' --stats > pre-rename-references.txt
```

**Baseline Metrics**:
- Total tests: ~150 (estimate)
- Test coverage: ~85%
- Linting issues: 0 (required)
- `flowspec` references: ~5000 (estimate)

### 6.2 Post-Rename Validation

**Test Suite Validation**:
```bash
# Run full test suite
pytest tests/ -v --tb=short

# Expected: Same test count as baseline
# Expected: All tests pass
# Expected: No import errors
```

**Coverage Validation**:
```bash
# Generate coverage report
pytest tests/ --cov=src/specify_cli --cov-report=html --cov-report=term

# Expected: Coverage ≥ baseline (85%)
# Expected: No new uncovered lines
```

**Linting Validation**:
```bash
# Run linter
ruff check . --fix
ruff format .

# Expected: 0 linting errors
# Expected: Consistent formatting
```

**Reference Validation**:
```bash
# Check for remaining old references
rg 'flowspec' --type py --type md --type yaml --type json

# Expected: Only in historical docs, changelogs, git history
# Expected: No references in active code or templates
```

### 6.3 Integration Testing

**Workflow Command Execution**:
```bash
# Test each workflow command
/flow:assess "Test feature"
/flow:specify
/flow:plan
/flow:implement
/flow:validate
/flow:operate

# Expected: Commands execute without error
# Expected: Artifacts created in correct locations
# Expected: State transitions work correctly
```

**Backlog Integration**:
```bash
# Test backlog task creation
backlog task list --plain

# Expected: Tasks reference /flow: commands
# Expected: State transitions use flowspec_workflow.yml
```

**MCP Server Integration**:
```bash
# Test MCP server startup
tessl mcp start

# Expected: Server starts without errors
# Expected: Workflow config loaded correctly
```

### 6.4 Regression Test Suite

**Critical Path Tests**:
1. **Config Loading** (`test_flowspec_workflow_integration.py`):
   - Load `flowspec_workflow.yml` successfully
   - Parse all workflows and states
   - Validate schema compliance

2. **Command Registration** (`test_cli.py`):
   - All `/flow:*` commands registered
   - Help text shows correct command names
   - Deprecation warnings for `/flow:*` (Phase 1)

3. **State Transitions** (`test_flowspec_workflow_roles.py`):
   - Assess → Specified → Planned → Implementation
   - Validate artifact creation
   - Check state guard validation

4. **Backlog Integration** (`test_flowspec_backlog_integration.py`):
   - Create tasks from `/flow:specify`
   - Update task state from `/flow:implement`
   - Archive tasks from `/flow:operate`

5. **Agent Handoffs** (`test_flowspec_e2e.py`):
   - Agent handoff configuration correct
   - Handoff prompts reference `/flow:*` commands
   - Agent identities correct (`@flow-*`)

### 6.5 Documentation Validation

**Automated Link Checking**:
```bash
# Install link checker
npm install -g markdown-link-check

# Check all markdown files
find docs -name "*.md" -exec markdown-link-check {} \;

# Expected: No broken links
# Expected: All command references valid
```

**Code Example Validation**:
```bash
# Extract code blocks from documentation
find docs -name "*.md" -exec grep -A 10 '```bash' {} \;

# Manual review: All examples use /flow: commands
# Manual review: All config references use flowspec_workflow.yml
```

**Consistency Check**:
```bash
# Check for inconsistent references
rg '/flow:' docs/
rg 'flowspec_workflow' docs/

# Expected: Only in migration guides or historical context
```

---

## 7. Backlog Tasks

The following tasks should be created in backlog.md using the backlog MCP tool:

### Task 1: Architecture & Documentation
```markdown
**Title**: Create ADR for flowspec → flowspec rename

**Description**:
Document architectural decision to rename command namespace from flowspec to flowspec.

**Acceptance Criteria**:
- [ ] ADR created in docs/adr/ADR-{NNN}-flowspec-flowspec-rename.md
- [ ] Decision rationale documented (UX improvement)
- [ ] Options considered and evaluated
- [ ] Consequences analyzed (positive and negative)
- [ ] Implementation plan referenced

**Labels**: documentation, architecture
**Priority**: high
**Assignee**: @architect
```

### Task 2: Schema & Config Rename
```markdown
**Title**: Rename workflow schema and config files

**Description**:
Rename schema files and root configuration from flowspec to flowspec.

**Acceptance Criteria**:
- [ ] schemas/flowspec_workflow.schema.json → schemas/flowspec_workflow.schema.json
- [ ] memory/flowspec_workflow.yml → memory/flowspec_workflow.yml
- [ ] flowspec_workflow.yml → flowspec_workflow.yml (root)
- [ ] src/specify_cli/workflow/config.py updated with new default paths
- [ ] Backward compatibility maintained (old names still work with deprecation)

**Labels**: backend, critical
**Priority**: high
**Dependencies**: None (must be done first)
```

### Task 3: Source Code Rename
```markdown
**Title**: Update Python source code for flowspec rename

**Description**:
Replace all flowspec references in Python source code with flowspec.

**Acceptance Criteria**:
- [ ] All `flowspec` → `flowspec` in src/**/*.py
- [ ] All `FLOWSPEC` → `FLOWSPEC` in constants
- [ ] All `/flow:` → `/flow:` in command strings
- [ ] Docstrings and comments updated
- [ ] Error messages updated
- [ ] No broken imports

**Labels**: backend
**Priority**: high
**Dependencies**: Task 2 (schema rename)
```

### Task 4: Command Directory Rename
```markdown
**Title**: Rename command directories and recreate symlinks

**Description**:
Rename .claude/commands/flowspec and templates/commands/flowspec to flow.

**Acceptance Criteria**:
- [ ] templates/commands/flowspec → templates/commands/flow
- [ ] .claude/commands/flowspec symlinks recreated pointing to flow
- [ ] Backward-compatible symlink created (flowspec → flow)
- [ ] All 17 command files accessible via /flow: namespace
- [ ] Old /flow: commands show deprecation warning

**Labels**: backend, infrastructure
**Priority**: high
**Dependencies**: Task 2 (schema rename)
```

### Task 5: GitHub Agents Rename
```markdown
**Title**: Rename GitHub Copilot agent files

**Description**:
Rename all .github/agents/flowspec-*.agent.md files to flow-*.agent.md.

**Acceptance Criteria**:
- [ ] All 15 agent files renamed (flowspec-* → flow-*)
- [ ] Agent handoff references updated (flowspec-research → flow-research)
- [ ] Agent identity fields updated
- [ ] No broken references in handoff chains

**Labels**: infrastructure
**Priority**: medium
**Dependencies**: Task 4 (command directory rename)
```

### Task 6: GitHub Prompts Rename
```markdown
**Title**: Rename GitHub Copilot prompt files

**Description**:
Rename all .github/prompts/flowspec.*.prompt.md files to flow.*.prompt.md.

**Acceptance Criteria**:
- [ ] All 31 prompt files renamed (flowspec.* → flow.*)
- [ ] Prompt content updated to reference /flow: commands
- [ ] No broken references to old command names

**Labels**: infrastructure
**Priority**: medium
**Dependencies**: Task 4 (command directory rename)
```

### Task 7: Test Suite Rename
```markdown
**Title**: Rename test files and update test content

**Description**:
Rename test files from test_flowspec_* to test_flowspec_* and update assertions.

**Acceptance Criteria**:
- [ ] All 14 test files renamed (test_flowspec_* → test_flowspec_*)
- [ ] Test imports updated
- [ ] Test fixtures updated (flowspec_config)
- [ ] Test assertions updated (command names, config files)
- [ ] All tests pass
- [ ] Coverage ≥ baseline (85%)

**Labels**: testing
**Priority**: high
**Dependencies**: Task 3 (source code rename)
```

### Task 8: Documentation Updates
```markdown
**Title**: Update documentation for flowspec rename

**Description**:
Update all documentation files to reference flowspec and /flow: commands.

**Acceptance Criteria**:
- [ ] README.md updated
- [ ] CLAUDE.md updated
- [ ] CONTRIBUTING.md updated
- [ ] docs/**/*.md files updated
- [ ] Code examples updated
- [ ] Command references updated
- [ ] No broken links
- [ ] Migration guide created

**Labels**: documentation
**Priority**: high
**Dependencies**: Task 7 (test suite complete)
```

### Task 9: Migration Guide
```markdown
**Title**: Create migration guide for flowspec → flowspec

**Description**:
Document migration path for existing users upgrading from flowspec to flowspec.

**Acceptance Criteria**:
- [ ] Migration guide created (docs/migrations/flowspec-to-flowspec.md)
- [ ] Deprecation timeline documented (v0.3, v0.4, v1.0)
- [ ] Step-by-step migration instructions
- [ ] Common issues and troubleshooting
- [ ] Backward compatibility notes
- [ ] Example migration script

**Labels**: documentation
**Priority**: medium
**Dependencies**: Task 8 (documentation updates)
```

### Task 10: Integration & Validation
```markdown
**Title**: End-to-end integration testing and validation

**Description**:
Comprehensive testing of renamed commands across all workflows.

**Acceptance Criteria**:
- [ ] All /flow: commands execute successfully
- [ ] Workflow state transitions work
- [ ] Backlog integration works
- [ ] MCP server integration works
- [ ] No references to old names (except historical)
- [ ] Linting passes (ruff check)
- [ ] All tests pass
- [ ] Coverage maintained

**Labels**: testing, qa
**Priority**: high
**Dependencies**: Task 7, Task 8
```

---

## 8. Implementation Checklist

### Phase 1: Preparation (1-2 hours)

- [ ] Create feature branch: `git checkout -b feature/flowspec-to-flowspec-rename`
- [ ] Capture baseline metrics (tests, coverage, linting)
- [ ] Create backup branch: `git branch backup/pre-flowspec-rename`
- [ ] Review this architecture plan with team
- [ ] Get approval to proceed

### Phase 2: Infrastructure Rename (2-3 hours)

- [ ] **Task 2**: Rename schema and config files
  - [ ] Rename files (git mv)
  - [ ] Update config.py default paths
  - [ ] Test config loading

- [ ] **Task 4**: Rename command directories
  - [ ] Rename templates/commands/flowspec → flow
  - [ ] Recreate symlinks in .claude/commands/flow
  - [ ] Create backward-compatible symlink
  - [ ] Verify command discovery

- [ ] **Task 5**: Rename GitHub agents
  - [ ] Rename all 15 agent files
  - [ ] Update handoff references
  - [ ] Test agent discovery

- [ ] **Task 6**: Rename GitHub prompts
  - [ ] Rename all 31 prompt files
  - [ ] Update prompt content

### Phase 3: Code & Tests (3-4 hours)

- [ ] **Task 3**: Update Python source code
  - [ ] Run automated replacement script
  - [ ] Manual review of critical files
  - [ ] Fix imports and references
  - [ ] Verify no broken imports

- [ ] **Task 7**: Rename and update tests
  - [ ] Rename test files
  - [ ] Update test content
  - [ ] Run test suite
  - [ ] Fix failing tests
  - [ ] Verify coverage

### Phase 4: Documentation (2-3 hours)

- [ ] **Task 8**: Update documentation
  - [ ] Run automated replacement script
  - [ ] Manual review of key docs
  - [ ] Update code examples
  - [ ] Fix broken links

- [ ] **Task 9**: Create migration guide
  - [ ] Write migration steps
  - [ ] Document deprecation timeline
  - [ ] Create example scripts

### Phase 5: Validation (1-2 hours)

- [ ] **Task 10**: Integration testing
  - [ ] Test all /flow: commands
  - [ ] Test workflow state transitions
  - [ ] Test backlog integration
  - [ ] Test MCP server
  - [ ] Run full test suite
  - [ ] Run linting
  - [ ] Check for remaining references

### Phase 6: Documentation & PR (1 hour)

- [ ] **Task 1**: Create ADR
  - [ ] Document decision
  - [ ] Explain rationale
  - [ ] List consequences

- [ ] Create pull request
  - [ ] Comprehensive description
  - [ ] Link to architecture plan
  - [ ] Screenshots of before/after
  - [ ] Test results summary

- [ ] Code review
  - [ ] Address feedback
  - [ ] Final validation

- [ ] Merge and release
  - [ ] Merge to main
  - [ ] Tag release (v0.3.0)
  - [ ] Publish release notes

---

## 9. Risk Mitigation

### 9.1 Rollback Plan

**If Critical Issues Discovered**:

1. **Immediate rollback**:
   ```bash
   git checkout main
   git branch -D feature/flowspec-to-flowspec-rename
   git checkout backup/pre-flowspec-rename
   git checkout -b feature/flowspec-to-flowspec-rename-v2
   ```

2. **Identify root cause**:
   - Review failed tests
   - Check error logs
   - Identify missed references

3. **Incremental fix**:
   - Fix specific issues
   - Re-run validation
   - Continue phased rollout

### 9.2 Validation Gates

**Gate 1: Schema & Config** (blocking Gate 2)
- [ ] Config files renamed
- [ ] Config loading works
- [ ] Backward compatibility verified

**Gate 2: Source Code** (blocking Gate 3)
- [ ] All Python files updated
- [ ] No import errors
- [ ] Linting passes

**Gate 3: Tests** (blocking Gate 4)
- [ ] Test files renamed
- [ ] All tests pass
- [ ] Coverage maintained

**Gate 4: Documentation** (blocking merge)
- [ ] All docs updated
- [ ] No broken links
- [ ] Migration guide complete

**Gate 5: Integration** (blocking release)
- [ ] E2E workflows work
- [ ] No references to old names
- [ ] Release notes ready

### 9.3 Monitoring Post-Release

**Week 1 After Release**:
- Monitor GitHub issues for rename-related bugs
- Check community feedback (Discord, GitHub Discussions)
- Watch for confusion in command usage

**Month 1 After Release**:
- Track adoption of `/flow:` commands vs. `/flow:` (deprecated)
- Identify users still on old config files
- Plan deprecation timeline enforcement

---

## 10. Success Criteria

### 10.1 Technical Success

- [ ] All 397 files updated correctly
- [ ] All tests pass (100% success rate)
- [ ] Test coverage ≥ 85% (maintained)
- [ ] Linting passes (0 errors)
- [ ] No references to `flowspec` in active code
- [ ] Backward compatibility maintained (Phase 1)

### 10.2 User Experience Success

- [ ] Command completion shows `/flow:` and `/speckit:` separately
- [ ] Users can type `/flow` without ambiguity
- [ ] Migration guide available and clear
- [ ] Deprecation warnings helpful (Phase 1)
- [ ] No breaking changes for existing users (Phase 1)

### 10.3 Documentation Success

- [ ] All documentation consistent with new names
- [ ] Code examples use `/flow:` commands
- [ ] Migration path clearly documented
- [ ] ADR explains decision rationale
- [ ] No broken links in documentation

---

## 11. Timeline

**Total Estimated Effort**: 8-12 hours

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| **Preparation** | 1-2 hours | Baseline metrics, branch created |
| **Infrastructure** | 2-3 hours | Files renamed, symlinks recreated |
| **Code & Tests** | 3-4 hours | Source updated, tests pass |
| **Documentation** | 2-3 hours | Docs updated, migration guide |
| **Validation** | 1-2 hours | E2E tests, final checks |
| **PR & Review** | 1 hour | Pull request, code review |

**Total Timeline**: 1-2 days (serial execution)

**Parallel Execution**: Can reduce to ~6 hours if documentation and code changes happen in parallel.

---

## 12. Conclusion

This architecture plan provides a comprehensive blueprint for renaming the `flowspec` namespace to `flowspec` across the jp-spec-kit project. The phased approach minimizes risk while maintaining backward compatibility during the transition.

**Key Success Factors**:
1. **Precedent**: Similar rename (`jpspec` → `flowspec`) completed successfully in Dec 2024
2. **Comprehensive Testing**: Full test suite and coverage validation
3. **Phased Rollout**: Deprecation phases reduce user impact
4. **Clear Documentation**: Migration guide and ADR explain rationale

**Next Steps**:
1. Review this plan with team
2. Get approval to proceed
3. Create backlog tasks using MCP tool
4. Execute Phase 1: Preparation
5. Begin incremental implementation

**Questions for Review**:
- Is the deprecation timeline acceptable (2-3 release cycles)?
- Should we add telemetry to track `/flow:` usage before removal?
- Any edge cases not covered in this plan?
- Should we create a release announcement template?

---

**Document Status**: DRAFT
**Version**: 1.0
**Last Updated**: 2025-12-10
**Approver**: TBD
