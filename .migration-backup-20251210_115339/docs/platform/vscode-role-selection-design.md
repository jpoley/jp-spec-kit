# VS Code Role Selection & Integration Design

**Feature**: Role-Based Agent Handoffs in VS Code Copilot
**Status**: Designed
**Date**: 2025-12-09
**Author**: Platform Engineer Agent
**Related**: vscode-copilot-agents-plan.md

---

## Executive Summary

This design enables users to select their primary role during `/jpspec:init` or `/jpspec:reset`, which customizes VS Code Copilot agent visibility, handoffs, and chat interface prominence based on their role in the development team.

**Business Impact**:
- **Reduced cognitive load**: Users see only role-relevant commands
- **Faster workflow navigation**: Role-specific handoff chains guide next steps
- **Team flexibility**: Multiple roles per user, team-wide role configuration
- **Platform adoption**: Improved VS Code Copilot UX increases JP Spec Kit adoption

**Design Principles**:
1. **Progressive disclosure**: Show only what's relevant to the user's role
2. **Zero lock-in**: Role selection is advisory, not restrictive (all agents accessible)
3. **Team-aware**: Support individual and team role configurations
4. **Configuration as code**: All role settings version-controlled in git

---

## 1. Role Selection UX Design

### 1.1 Role Definitions

JP Spec Kit defines five primary roles based on workflow phases:

| Role | Primary Workflows | Agent Focus | Use Case |
|------|-------------------|-------------|----------|
| **Product Manager (PM)** | assess, specify, research | product-requirements-manager, researcher, business-validator | Feature definition, requirements, business validation |
| **Developer (Dev)** | plan, implement, operate | software-architect, platform-engineer, frontend/backend-engineer | Technical design, coding, deployment |
| **Security Engineer (Sec)** | security_*, validate | secure-by-design-engineer, security scanners | Security scanning, triage, vulnerability fixes |
| **QA Engineer (QA)** | validate | quality-guardian, tech-writer, release-manager | Testing, documentation, quality validation |
| **Full Workflow (All)** | All commands | All agents | Full SDD workflow, solo developers, learning mode |

### 1.2 Interactive Role Selection (init.md)

Add to `/jpspec:init` after Step 6 (Generate Constitution):

```markdown
### Step 6.5: VS Code Role Configuration (Optional)

If VS Code is detected (`.vscode/` directory exists) or user requests:

```
╔══════════════════════════════════════════════════════════════╗
║         VS Code Copilot Role Configuration                   ║
╚══════════════════════════════════════════════════════════════╝

Select your primary role to customize VS Code chat handoffs:

  1. Product Manager (PM)
     Focus: Requirements, research, business validation
     Commands: /jpspec:assess, /jpspec:specify, /jpspec:research

  2. Developer (Dev)
     Focus: Architecture, implementation, deployment
     Commands: /jpspec:plan, /jpspec:implement, /jpspec:operate

  3. Security Engineer (Sec)
     Focus: Security scanning, triage, vulnerability fixes
     Commands: /jpspec:security_*, /jpspec:validate (security only)

  4. QA Engineer (QA)
     Focus: Testing, documentation, quality validation
     Commands: /jpspec:validate

  5. Full Workflow (All) [default]
     Focus: Complete SDD workflow (all phases)
     Commands: All /jpspec and /speckit commands

  6. Skip - Don't configure role-based UI
     (All agents remain equally visible)

Choice [5]: _
```

**Multi-role support**:
```
Would you like to add secondary roles? (y/N): y

Select secondary roles (comma-separated):
  [1] Product Manager
  [2] Developer
  [3] Security Engineer
  [4] QA Engineer

Secondary roles []: 2,4
```

**Team vs Individual mode**:
```
Configure role for:
  1. This machine only (user-specific)
  2. Entire team (version-controlled)

Mode [1]: 2
```
```

### 1.3 Reset Command Integration (reset.md)

Add to `/jpspec:reset` after Step 3 (Prompt for Validation Modes):

```markdown
### Step 3.5: VS Code Role Reconfiguration (Optional)

If `--vscode-role` flag is provided OR user requests during prompts:

```
== VS Code Role Configuration ==

Current role: Developer (Dev)
Secondary roles: QA Engineer

Update role configuration? (y/N): y

[Same prompts as init.md Step 6.5]
```

**New flags for reset.md**:
- `--vscode-role {pm|dev|sec|qa|all}`: Set primary role (non-interactive)
- `--vscode-secondary {pm,dev,sec,qa}`: Set secondary roles (non-interactive)
- `--vscode-mode {user|team}`: Set configuration scope (non-interactive)
```

### 1.4 Non-Interactive Mode (CLI)

For automation and scripting:

```bash
# Initialize with role selection
specify init --here --vscode-role dev --vscode-secondary qa,sec

# Reset role configuration
specify reset --vscode-role pm --vscode-mode team

# Disable role-based UI
specify reset --vscode-role all
```

---

## 2. Configuration Storage Design

### 2.1 Recommended Approach: Dual Configuration Strategy

**Decision**: Use **both** `.vscode/settings.json` (user-specific) and `specflow_workflow.yml` (team-wide).

| Storage Location | Scope | Version Control | Use Case |
|------------------|-------|-----------------|----------|
| `.vscode/settings.json` | User/machine-specific | Gitignored (default) | Individual developer preferences |
| `specflow_workflow.yml` | Team-wide | Committed to git | Consistent team role definitions |

**Rationale**:
- **User autonomy**: Developers can override team defaults for their local environment
- **Team consistency**: Default role configurations shared via git
- **VS Code native**: `.vscode/settings.json` is the canonical place for editor configuration
- **Single source of truth**: `specflow_workflow.yml` remains authoritative for workflow logic

### 2.2 Configuration Schema

#### specflow_workflow.yml (Team-wide defaults)

Add new top-level section:

```yaml
# JPSpec Workflow Configuration
version: "1.1"

# ... existing states, workflows, transitions ...

# ==============================================================================
# VS CODE ROLE CONFIGURATION (Team Defaults)
# ==============================================================================
# Default role assignments for VS Code Copilot agent visibility.
# Users can override in .vscode/settings.json.

vscode_roles:
  # Default role if not specified in .vscode/settings.json
  default_role: "all"

  # Role definitions
  roles:
    pm:
      name: "Product Manager"
      description: "Requirements, research, business validation"
      workflows:
        - "assess"
        - "specify"
        - "research"
      agents:
        - "jpspec-assess"
        - "jpspec-specify"
        - "jpspec-research"

    dev:
      name: "Developer"
      description: "Architecture, implementation, deployment"
      workflows:
        - "plan"
        - "implement"
        - "operate"
      agents:
        - "jpspec-plan"
        - "jpspec-implement"
        - "jpspec-operate"

    sec:
      name: "Security Engineer"
      description: "Security scanning, triage, vulnerability fixes"
      workflows:
        - "security_workflow"
        - "security_triage"
        - "security_fix"
        - "validate"  # Only security aspects
      agents:
        - "jpspec-security_workflow"
        - "jpspec-security_triage"
        - "jpspec-security_fix"
        - "jpspec-security_report"
        - "jpspec-security_web"

    qa:
      name: "QA Engineer"
      description: "Testing, documentation, quality validation"
      workflows:
        - "validate"
      agents:
        - "jpspec-validate"
        - "speckit-checklist"

    all:
      name: "Full Workflow"
      description: "Complete SDD workflow (all phases)"
      workflows: "*"  # All workflows
      agents: "*"     # All agents

  # Agent visibility modes
  visibility:
    primary_only: false    # If true, show ONLY primary role agents
    hide_others: false     # If true, hide non-role agents (vs de-prioritize)
    show_speckit: true     # Always show speckit utilities
```

#### .vscode/settings.json (User overrides)

```json
{
  "chat.promptFiles": true,

  // JP Spec Kit Role Configuration (overrides specflow_workflow.yml)
  "jpspec.vscode.role": {
    "primary": "dev",
    "secondary": ["qa", "sec"],
    "visibility": "de-prioritize",  // "hide" | "de-prioritize" | "show-all"
    "mode": "user"  // "user" | "team"
  },

  // VS Code Copilot Agent Pinning (native VS Code feature)
  "chat.agent.pinnedAgents": [
    "jpspec-plan",
    "jpspec-implement",
    "jpspec-validate"
  ]
}
```

### 2.3 Configuration Resolution Order

1. Read `.vscode/settings.json` → Extract `jpspec.vscode.role.*`
2. Read `specflow_workflow.yml` → Extract `vscode_roles.*`
3. Merge with precedence: `.vscode/settings.json` > `specflow_workflow.yml` > defaults
4. Apply to agent generation and handoff configuration

---

## 3. VS Code Integration Architecture

### 3.1 Agent Filtering Strategy

**Approach**: Generate **role-specific agent sets** via `sync-copilot-agents.sh`.

```bash
# Generate agents for all roles (default)
scripts/bash/sync-copilot-agents.sh

# Output structure:
.github/agents/
  jpspec-assess.agent.md       # PM, All
  jpspec-specify.agent.md      # PM, All
  jpspec-research.agent.md     # PM, All
  jpspec-plan.agent.md         # Dev, All
  jpspec-implement.agent.md    # Dev, All
  jpspec-validate.agent.md     # QA, Sec, All
  jpspec-operate.agent.md      # Dev, All
  jpspec-security_*.agent.md   # Sec, All
  speckit-*.agent.md           # All roles (utilities)
```

**Agent metadata** (added to frontmatter):

```yaml
---
name: "jpspec-plan"
description: "Execute planning workflow using architect and platform engineer"
target: "chat"
tools: [...]
handoffs: [...]

# NEW: Role metadata
roles:
  - "dev"
  - "all"
priority: "high"  # For role-based sorting
---
```

### 3.2 Handoff Customization by Role

Role-specific handoff chains guide users through their workflow:

#### PM Role Handoff Chain

```yaml
# jpspec-assess.agent.md (PM role)
handoffs:
  - label: "✓ Assessment Complete → Specify Requirements"
    agent: "jpspec-specify"
    prompt: "Assessment complete. Create the PRD."
    send: false
  # No other handoffs shown for PM role

# jpspec-specify.agent.md (PM role)
handoffs:
  - label: "✓ Specification Complete → Conduct Research"
    agent: "jpspec-research"
    prompt: "PRD complete. Conduct market and technical research."
    send: false
  - label: "🔀 Hand off to Developer → Plan Architecture"
    agent: "jpspec-plan"
    prompt: "PRD complete. Ready for technical design. (Developer role)"
    send: false

# jpspec-research.agent.md (PM role)
handoffs:
  - label: "✓ Research Complete → Hand off to Developer"
    agent: "jpspec-plan"
    prompt: "Research complete. Ready for technical design. (Developer role)"
    send: false
```

#### Dev Role Handoff Chain

```yaml
# jpspec-plan.agent.md (Dev role)
handoffs:
  - label: "✓ Planning Complete → Begin Implementation"
    agent: "jpspec-implement"
    prompt: "Architecture designed. Begin implementation."
    send: false

# jpspec-implement.agent.md (Dev role)
handoffs:
  - label: "✓ Implementation Complete → Run Validation"
    agent: "jpspec-validate"
    prompt: "Code complete. Run QA validation. (QA role)"
    send: false

# jpspec-validate.agent.md (Dev role)
handoffs:
  - label: "✓ Validation Complete → Deploy to Production"
    agent: "jpspec-operate"
    prompt: "Validation passed. Deploy to production."
    send: false
```

#### Cross-role Handoffs

**Key insight**: Handoffs crossing role boundaries indicate **human approval gates**.

```yaml
# PM → Dev handoff (requires PR approval in team mode)
handoffs:
  - label: "🔀 Hand off to Developer → Plan Architecture"
    agent: "jpspec-plan"
    prompt: "PRD complete. Ready for technical design. (Developer role)"
    send: false
    approval_required: true  # NEW: Indicates cross-role gate

# Dev → QA handoff (requires review)
handoffs:
  - label: "🔀 Hand off to QA → Run Validation"
    agent: "jpspec-validate"
    prompt: "Implementation complete. Ready for QA validation. (QA role)"
    send: false
    approval_required: true
```

### 3.3 Chat Interface Prominence

**Objective**: Make role-relevant agents "auto-loaded" or more visible in VS Code chat.

#### Option 1: VS Code Agent Pinning (Native)

Leverage VS Code's native `chat.agent.pinnedAgents` setting:

```json
{
  "chat.agent.pinnedAgents": [
    "jpspec-plan",
    "jpspec-implement",
    "jpspec-operate"
  ]
}
```

**Implementation**:
- `/jpspec:init` and `/jpspec:reset` write to `.vscode/settings.json`
- Pin agents based on selected role
- Users can manually customize pinned agents

#### Option 2: Agent Ordering via Metadata

Add `priority` field to agent frontmatter:

```yaml
---
name: "jpspec-plan"
priority: 1  # High priority for Dev role
roles:
  - "dev"
  - "all"
---
```

**Agent sorting algorithm**:
1. Pinned agents first (from VS Code settings)
2. Primary role agents (priority: 1-10)
3. Secondary role agents (priority: 11-20)
4. Utility agents (speckit-*, priority: 21-30)
5. All other agents (priority: 31+)

#### Option 3: Role-Specific Agent Directories (Advanced)

Generate role-specific `.github/agents-{role}/` directories:

```
.github/
  agents/           # All agents (default)
  agents-pm/        # PM role only
  agents-dev/       # Dev role only
  agents-qa/        # QA role only
  agents-sec/       # Sec role only
```

Configure VS Code to use role-specific directory:

```json
{
  "chat.agents.directory": ".github/agents-dev/"
}
```

**Trade-offs**:
- ✅ Clean separation, no filtering needed
- ✅ Easy to switch roles (change directory path)
- ❌ Disk space overhead (23 agents × 5 roles = 115 files)
- ❌ More complex sync script

**Recommendation**: **Option 1 + Option 2** (pinning + priority metadata).

---

## 4. sync-copilot-agents.sh Enhancement Design

### 4.1 CLI Interface Changes

Add new flags for role-aware generation:

```bash
sync-copilot-agents.sh [OPTIONS]

New Options:
  --role {pm|dev|sec|qa|all}   Generate agents for specific role only
  --with-roles                 Add role metadata to all agents (default)
  --team-mode                  Use specflow_workflow.yml role config (default)
  --user-mode                  Use .vscode/settings.json role config

Examples:
  sync-copilot-agents.sh --role dev
  # Generates only agents relevant to Developer role

  sync-copilot-agents.sh --with-roles
  # Generates all agents with role metadata in frontmatter
```

### 4.2 Role Metadata Injection

**New function**: `get_role_metadata()`

```bash
get_role_metadata() {
    local namespace="$1"
    local command="$2"
    local config_file="${3:-specflow_workflow.yml}"

    # Read role config from specflow_workflow.yml
    # (or .vscode/settings.json if --user-mode)

    # Extract roles for this agent
    local roles
    roles=$(python3 << PYTHON
import yaml
with open("$config_file") as f:
    config = yaml.safe_load(f)
    vscode_roles = config.get("vscode_roles", {}).get("roles", {})

    agent_name = "${namespace}-${command}"
    matching_roles = []

    for role_id, role_config in vscode_roles.items():
        agents = role_config.get("agents", [])
        if agent_name in agents or agents == "*":
            matching_roles.append(role_id)

    print("\n".join(matching_roles))
PYTHON
)

    # Output role metadata YAML
    if [[ -n "$roles" ]]; then
        echo "roles:"
        while IFS= read -r role; do
            echo "  - \"$role\""
        done <<< "$roles"

        # Calculate priority based on role
        local priority=50  # Default
        if grep -q "\"all\"" <<< "$roles"; then
            priority=10
        elif grep -q "\"dev\"" <<< "$roles"; then
            priority=5
        elif grep -q "\"pm\"" <<< "$roles"; then
            priority=3
        fi
        echo "priority: $priority"
    fi
}
```

### 4.3 Enhanced Frontmatter Generation

Modify `generate_frontmatter()` to include role metadata:

```bash
generate_frontmatter() {
    local namespace="$1"
    local command="$2"
    local description="$3"

    local name="${namespace}-${command}"
    local handoffs
    local tools
    local role_metadata  # NEW

    handoffs=$(get_handoffs "$namespace" "$command")
    tools=$(get_tools "$namespace")
    role_metadata=$(get_role_metadata "$namespace" "$command")  # NEW

    echo "---"
    echo "name: \"$name\""
    echo "description: \"$description\""
    echo "target: \"chat\""
    echo "$tools"

    # NEW: Add role metadata
    if [[ -n "$role_metadata" ]]; then
        echo "$role_metadata"
    fi

    if [[ -n "$handoffs" ]]; then
        echo "$handoffs"
    fi
    echo "---"
}
```

### 4.4 Role-Filtered Generation (Optional)

**New function**: `should_include_agent()`

```bash
should_include_agent() {
    local agent_name="$1"
    local target_role="${ROLE_FILTER:-all}"  # From --role flag

    if [[ "$target_role" == "all" ]]; then
        return 0  # Include all agents
    fi

    # Check if agent belongs to target role
    local agent_roles
    agent_roles=$(get_role_metadata "$namespace" "$command" | grep -oP '- "\K[^"]+')

    if grep -q "$target_role" <<< "$agent_roles"; then
        return 0  # Include
    else
        return 1  # Skip
    fi
}
```

**Modified processing loop**:

```bash
process_namespace() {
    # ... existing code ...

    for file in "$namespace_dir"/*.md; do
        if [[ -f "$file" || -L "$file" ]]; then
            local agent_name="${namespace}-$(basename "$file" .md)"

            # NEW: Filter by role if specified
            if ! should_include_agent "$agent_name"; then
                log_verbose "Skipping (role filter): $agent_name"
                continue
            fi

            ((TOTAL_FILES++))
            process_command "$file" "$namespace" || true
        fi
    done
}
```

### 4.5 VS Code Settings Generation

**New function**: `generate_vscode_settings()`

```bash
generate_vscode_settings() {
    local primary_role="$1"
    local secondary_roles="${2:-}"
    local mode="${3:-user}"

    # Read existing settings
    local settings_file=".vscode/settings.json"
    mkdir -p .vscode

    if [[ ! -f "$settings_file" ]]; then
        echo "{}" > "$settings_file"
    fi

    # Merge JP Spec Kit role config
    python3 << PYTHON
import json
from pathlib import Path

settings_file = Path("$settings_file")
settings = json.loads(settings_file.read_text())

# Add JP Spec Kit role config
settings["jpspec.vscode.role"] = {
    "primary": "$primary_role",
    "secondary": "$secondary_roles".split(",") if "$secondary_roles" else [],
    "visibility": "de-prioritize",
    "mode": "$mode"
}

# Add pinned agents based on role
role_agents = {
    "pm": ["jpspec-assess", "jpspec-specify", "jpspec-research"],
    "dev": ["jpspec-plan", "jpspec-implement", "jpspec-operate"],
    "sec": ["jpspec-security_workflow", "jpspec-security_triage", "jpspec-validate"],
    "qa": ["jpspec-validate", "speckit-checklist"],
    "all": []  # No pinning for all role
}

pinned = role_agents.get("$primary_role", [])
if pinned:
    settings["chat.agent.pinnedAgents"] = pinned

settings_file.write_text(json.dumps(settings, indent=2))
PYTHON

    log_success "Updated .vscode/settings.json with role: $primary_role"
}
```

**Integration with init/reset**:

```bash
# Called from /jpspec:init or /jpspec:reset after role selection
if [[ "$vscode_role" != "skip" ]]; then
    generate_vscode_settings "$primary_role" "$secondary_roles" "$mode"

    # Regenerate agents with role metadata
    scripts/bash/sync-copilot-agents.sh --with-roles
fi
```

---

## 5. Multi-Role Support Design

### 5.1 Primary vs Secondary Roles

**Primary role**: Determines agent pinning and default handoffs
**Secondary roles**: Additional agents shown with lower priority

```json
{
  "jpspec.vscode.role": {
    "primary": "dev",
    "secondary": ["qa", "sec"]
  }
}
```

**Agent visibility logic**:

```python
def get_agent_priority(agent_name, user_config):
    primary_role = user_config["primary"]
    secondary_roles = user_config.get("secondary", [])

    agent_roles = get_agent_roles(agent_name)  # From metadata

    if primary_role in agent_roles:
        return 1  # High priority
    elif any(role in agent_roles for role in secondary_roles):
        return 2  # Medium priority
    elif "all" in agent_roles:
        return 3  # Low priority (utilities)
    else:
        return 4  # Hidden or de-prioritized
```

### 5.2 Role Switching

**Quick role switch** (no regeneration):

```bash
# Update .vscode/settings.json only
specify config set vscode.role.primary dev

# Or manually edit .vscode/settings.json
# VS Code reloads settings automatically
```

**Full role reconfiguration** (with agent regeneration):

```bash
specify reset --vscode-role qa --vscode-secondary dev
# → Updates specflow_workflow.yml
# → Regenerates agents with new role metadata
# → Updates .vscode/settings.json
```

### 5.3 Team vs Individual Role Selection

**Team mode** (`mode: "team"`):
- Role config stored in `specflow_workflow.yml`
- Committed to git
- Enforced via CI/CD
- All team members see same default role assignments

**User mode** (`mode: "user"`):
- Role config stored in `.vscode/settings.json`
- Gitignored (not committed)
- Personal preference, no team enforcement

**Resolution**:
```python
def resolve_role_config():
    user_config = read_vscode_settings().get("jpspec.vscode.role", {})
    team_config = read_specflow_workflow().get("vscode_roles", {})

    if user_config.get("mode") == "user":
        # User override takes precedence
        return user_config
    else:
        # Use team default
        return {
            "primary": team_config.get("default_role", "all"),
            "secondary": [],
            "mode": "team"
        }
```

---

## 6. CI/CD Integration Design

### 6.1 Role-Based CI Workflows

**Use case**: Run different CI checks based on role-authored changes.

```yaml
# .github/workflows/role-based-ci.yml
name: Role-Based CI

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  detect-role:
    runs-on: ubuntu-latest
    outputs:
      changed_roles: ${{ steps.detect.outputs.roles }}
    steps:
      - uses: actions/checkout@v4

      - name: Detect changed role artifacts
        id: detect
        run: |
          # Check which docs/ subdirectories changed
          if git diff --name-only origin/main | grep -q "^docs/prd/"; then
            echo "pm" >> roles.txt
          fi
          if git diff --name-only origin/main | grep -q "^docs/adr/"; then
            echo "dev" >> roles.txt
          fi
          if git diff --name-only origin/main | grep -q "^docs/security/"; then
            echo "sec" >> roles.txt
          fi
          if git diff --name-only origin/main | grep -q "^docs/qa/"; then
            echo "qa" >> roles.txt
          fi

          echo "roles=$(cat roles.txt | tr '\n' ',')" >> $GITHUB_OUTPUT

  pm-validation:
    needs: detect-role
    if: contains(needs.detect-role.outputs.changed_roles, 'pm')
    runs-on: ubuntu-latest
    steps:
      - name: Validate PRD artifacts
        run: |
          # Check PRD structure, DVF+V assessment, etc.
          specify validate prd docs/prd/*.md

  dev-validation:
    needs: detect-role
    if: contains(needs.detect-role.outputs.changed_roles, 'dev')
    runs-on: ubuntu-latest
    steps:
      - name: Run tests and linting
        run: |
          pytest tests/
          ruff check .

      - name: Validate ADRs
        run: |
          specify validate adr docs/adr/*.md

  sec-validation:
    needs: detect-role
    if: contains(needs.detect-role.outputs.changed_roles, 'sec')
    runs-on: ubuntu-latest
    steps:
      - name: Security scanning
        run: |
          bandit -r src/
          trivy fs .

      - name: SLSA compliance check
        run: |
          specify validate security docs/security/*.md

  qa-validation:
    needs: detect-role
    if: contains(needs.detect-role.outputs.changed_roles, 'qa')
    runs-on: ubuntu-latest
    steps:
      - name: Test coverage validation
        run: |
          pytest --cov=src --cov-report=json
          specify validate coverage coverage.json

      - name: Documentation check
        run: |
          specify validate docs docs/qa/*.md
```

### 6.2 Team Role Validation

**Enforce team role assignments** in CI:

```yaml
# .github/workflows/validate-roles.yml
name: Validate Team Roles

on:
  pull_request:
    paths:
      - 'specflow_workflow.yml'
      - '.vscode/settings.json'

jobs:
  validate-roles:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check role configuration
        run: |
          # Validate specflow_workflow.yml role definitions
          specify workflow validate

          # Check .vscode/settings.json not committed in team mode
          if grep -q '"mode": "team"' specflow_workflow.yml; then
            if git ls-files | grep -q '.vscode/settings.json'; then
              echo "ERROR: .vscode/settings.json committed in team mode"
              exit 1
            fi
          fi

      - name: Validate role-agent mapping
        run: |
          # Ensure all agents have valid role assignments
          python3 << 'PYTHON'
          import yaml
          from pathlib import Path

          config = yaml.safe_load(Path("specflow_workflow.yml").read_text())
          roles = config["vscode_roles"]["roles"]

          # Check all referenced agents exist
          for role_id, role_config in roles.items():
              agents = role_config.get("agents", [])
              if agents == "*":
                  continue

              for agent_name in agents:
                  agent_file = Path(f".github/agents/{agent_name}.agent.md")
                  if not agent_file.exists():
                      raise ValueError(f"Agent {agent_name} not found for role {role_id}")

          print("✓ All role-agent mappings valid")
          PYTHON
```

---

## 7. Observability Design

### 7.1 Role Usage Analytics

**Telemetry collection** (privacy-preserving):

```python
# src/specify_cli/telemetry.py

from enum import Enum
from pathlib import Path
import json
from datetime import datetime

class RoleEvent(Enum):
    ROLE_SELECTED = "role.selected"
    ROLE_SWITCHED = "role.switched"
    AGENT_INVOKED = "agent.invoked"
    HANDOFF_CLICKED = "handoff.clicked"

def track_role_event(event: RoleEvent, metadata: dict):
    """Track role-related events for analytics."""

    # Check if telemetry enabled
    config = load_config()
    if not config.get("telemetry", {}).get("enabled", False):
        return

    event_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event.value,
        "metadata": {
            # Hash sensitive data
            "role_hash": hash_role(metadata.get("role")),
            "agent": metadata.get("agent"),
            "workflow": metadata.get("workflow"),
            # No PII or project-specific data
        }
    }

    # Write to local telemetry file
    telemetry_file = Path(".jpspec/telemetry.jsonl")
    telemetry_file.parent.mkdir(exist_ok=True)

    with telemetry_file.open("a") as f:
        f.write(json.dumps(event_data) + "\n")

# Usage in init.md and reset.md
track_role_event(RoleEvent.ROLE_SELECTED, {
    "role": primary_role,
    "mode": "team" if team_mode else "user"
})
```

### 7.2 Agent Usage Metrics

**Metrics to track**:
- Most-used agents per role
- Handoff click-through rate
- Role switching frequency
- Cross-role handoff patterns

**Dashboard query examples**:

```sql
-- Most popular agents by role
SELECT role_hash, agent, COUNT(*) as invocations
FROM telemetry_events
WHERE event = 'agent.invoked'
GROUP BY role_hash, agent
ORDER BY invocations DESC
LIMIT 20;

-- Handoff success rate
SELECT
  agent,
  COUNT(*) as total_handoffs,
  SUM(CASE WHEN handoff_completed THEN 1 ELSE 0 END) as completed
FROM telemetry_events
WHERE event = 'handoff.clicked'
GROUP BY agent;

-- Role switching patterns
SELECT
  from_role_hash,
  to_role_hash,
  COUNT(*) as switches
FROM telemetry_events
WHERE event = 'role.switched'
GROUP BY from_role_hash, to_role_hash;
```

### 7.3 Feedback Mechanism

**In-app feedback prompt** (after workflow completion):

```markdown
## Workflow Complete

╔══════════════════════════════════════════════════════════════╗
║         How was your role-based workflow experience?         ║
╚══════════════════════════════════════════════════════════════╝

Role: Developer (Dev)
Agents used: jpspec-plan, jpspec-implement, jpspec-validate

Rate your experience (1-5): _

What worked well?
> _

What could be improved?
> _

[Send Feedback]  [Skip]
```

**Feedback data structure**:

```json
{
  "timestamp": "2025-12-09T10:30:00Z",
  "role_hash": "abc123",
  "rating": 4,
  "comments": {
    "positive": "Role handoffs guided me perfectly",
    "negative": "Wanted to see security agents too"
  },
  "agents_used": ["jpspec-plan", "jpspec-implement", "jpspec-validate"],
  "workflow_duration_minutes": 120
}
```

---

## 8. Implementation Tasks

### 8.1 Planning Tasks

| Task ID | Description | Priority | Depends On |
|---------|-------------|----------|------------|
| task-TBD-1 | Design: Role selection UX in init.md and reset.md | HIGH | None |
| task-TBD-2 | Design: Configuration storage (specflow_workflow.yml + .vscode/settings.json) | HIGH | None |
| task-TBD-3 | Design: VS Code integration architecture | HIGH | task-TBD-2 |
| task-TBD-4 | Design: sync-copilot-agents.sh role enhancements | MEDIUM | task-TBD-2 |
| task-TBD-5 | Design: Multi-role support and team mode | MEDIUM | task-TBD-3 |
| task-TBD-6 | Design: CI/CD role validation workflows | LOW | task-TBD-5 |
| task-TBD-7 | Design: Telemetry and observability | LOW | None |

### 8.2 Phase 1: Foundation (HIGH priority)

| Task ID | Description | Acceptance Criteria |
|---------|-------------|---------------------|
| task-TBD-8 | Add role definitions to specflow_workflow.yml | ✓ 5 roles defined (pm, dev, sec, qa, all)<br>✓ Agent mappings complete<br>✓ Schema validated |
| task-TBD-9 | Implement role selection prompts in init.md | ✓ Interactive prompts work<br>✓ Multi-role support<br>✓ Team vs user mode selection |
| task-TBD-10 | Implement role selection prompts in reset.md | ✓ Re-configuration works<br>✓ Preserves existing config<br>✓ CLI flags supported |
| task-TBD-11 | Implement .vscode/settings.json generation | ✓ JSON structure correct<br>✓ Merges with existing settings<br>✓ Agent pinning configured |

### 8.3 Phase 2: Agent Metadata (HIGH priority)

| Task ID | Description | Acceptance Criteria |
|---------|-------------|---------------------|
| task-TBD-12 | Add get_role_metadata() to sync-copilot-agents.sh | ✓ Reads specflow_workflow.yml<br>✓ Extracts agent roles<br>✓ Calculates priority |
| task-TBD-13 | Enhance generate_frontmatter() with role metadata | ✓ Role metadata in frontmatter<br>✓ Priority field set<br>✓ Backward compatible |
| task-TBD-14 | Regenerate all agents with role metadata | ✓ 23 agents updated<br>✓ Role metadata present<br>✓ No unresolved includes |
| task-TBD-15 | Test role-filtered handoffs in VS Code | ✓ PM role shows PM handoffs only<br>✓ Dev role shows Dev handoffs<br>✓ Cross-role handoffs marked |

### 8.4 Phase 3: Advanced Features (MEDIUM priority)

| Task ID | Description | Acceptance Criteria |
|---------|-------------|---------------------|
| task-TBD-16 | Implement role switching (specify config) | ✓ CLI command works<br>✓ Settings updated<br>✓ No agent regeneration |
| task-TBD-17 | Implement team mode validation in CI | ✓ GitHub Actions workflow created<br>✓ Role config validated<br>✓ Fails on invalid mappings |
| task-TBD-18 | Add role-based CI workflow triggers | ✓ Detects changed role artifacts<br>✓ Runs role-specific checks<br>✓ Matrix jobs configured |
| task-TBD-19 | Implement telemetry tracking | ✓ Privacy-preserving<br>✓ JSONL format<br>✓ Opt-in via config |

### 8.5 Phase 4: Documentation (MEDIUM priority)

| Task ID | Description | Acceptance Criteria |
|---------|-------------|---------------------|
| task-TBD-20 | Document role selection in user guide | ✓ Role definitions explained<br>✓ Examples for each role<br>✓ Team vs user mode documented |
| task-TBD-21 | Create role-based workflow examples | ✓ PM workflow example<br>✓ Dev workflow example<br>✓ Cross-role handoff example |
| task-TBD-22 | Update VS Code Copilot integration docs | ✓ Role configuration steps<br>✓ Troubleshooting guide<br>✓ Screenshots included |

---

## 9. Success Criteria

### Technical Success

- [x] Role selection integrated into `/jpspec:init` and `/jpspec:reset`
- [ ] Configuration stored in both `specflow_workflow.yml` and `.vscode/settings.json`
- [ ] Agent metadata includes role and priority fields
- [ ] sync-copilot-agents.sh generates role-aware frontmatter
- [ ] VS Code agent pinning configured based on role
- [ ] Multi-role support (primary + secondary) working
- [ ] Team mode enforced via CI/CD
- [ ] Telemetry captures role usage (privacy-preserving)

### User Acceptance

- [ ] PM role users see only PM-relevant agents prominently
- [ ] Dev role users see dev-specific handoff chains
- [ ] Role switching works without agent regeneration
- [ ] Cross-role handoffs clearly marked and functional
- [ ] Team role defaults work in shared repositories
- [ ] User role overrides work for individual preferences
- [ ] Documentation clear for all roles and modes

### Performance

- [ ] Role selection adds < 5 seconds to init/reset
- [ ] Agent generation with role metadata < 2 seconds
- [ ] VS Code settings.json update < 100ms
- [ ] No performance degradation in VS Code Copilot

---

## 10. Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| VS Code API changes break agent pinning | Low | High | Monitor VS Code release notes; fallback to priority metadata |
| Users confused by role selection | Medium | Medium | Clear documentation; sensible defaults (role: "all") |
| Team mode conflicts with user preferences | Medium | Low | Explicit user override support in settings.json |
| Role metadata bloats agent files | Low | Low | Metadata is <10 lines; minimal impact |
| Telemetry privacy concerns | Medium | High | Opt-in only; hash all sensitive data; clear privacy policy |
| CI role validation false positives | Medium | Medium | Comprehensive test suite; manual override option |

---

## 11. Trade-offs and Alternatives Considered

### Configuration Storage

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **A: specflow_workflow.yml only** | Single source of truth, version-controlled | No user overrides, not VS Code native | ❌ Rejected |
| **B: .vscode/settings.json only** | VS Code native, user-friendly | Not team-sharable, gitignored by default | ❌ Rejected |
| **C: Dual strategy (both)** | Team defaults + user overrides, best of both | Slightly more complex | ✅ **Selected** |
| **D: New .jpspec/roles.yml** | Clean separation | Yet another config file to manage | ❌ Rejected |

### Agent Filtering

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| **Hide other agents completely** | Clean UI, focused workflow | Limits flexibility, users may need other agents | ❌ Rejected |
| **De-prioritize other agents** | Flexible, all agents accessible | UI less clean | ✅ **Selected** |
| **Generate role-specific directories** | Clean separation | Disk overhead, complex sync | ❌ Deferred (future) |

### Multi-Role Support

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| **Single role only** | Simplest implementation | Inflexible for multi-hat developers | ❌ Rejected |
| **Primary + secondary roles** | Balance flexibility and simplicity | Moderate complexity | ✅ **Selected** |
| **Unlimited roles** | Maximum flexibility | Complex UI, overwhelming | ❌ Rejected |

---

## 12. Future Enhancements

### Phase 5 (Future)

1. **AI-Suggested Roles**
   - Analyze project structure and suggest appropriate role
   - Example: "Detected React frontend → Suggest role: Developer (Frontend)"

2. **Role Analytics Dashboard**
   - Web UI showing role usage patterns
   - Team collaboration metrics
   - Agent efficiency by role

3. **Dynamic Role Switching**
   - Context-aware role detection based on current task
   - Example: Working in `docs/prd/` → Auto-suggest PM role

4. **Role-Based Templates**
   - Custom command templates per role
   - Role-specific artifact templates

5. **Enterprise SSO Integration**
   - Map company roles to JP Spec Kit roles
   - Auto-configure based on LDAP/AD groups

---

## 13. Next Steps

1. **Review and approval**: Platform team reviews this design document
2. **Create implementation tasks**: Use task breakdown in Section 8
3. **Spike investigation**: Test VS Code agent pinning with prototype
4. **Implement Phase 1**: Foundation (role selection, configuration storage)
5. **User testing**: Early feedback from PM, Dev, QA roles

---

*Design by Platform Engineer Agent on 2025-12-09*
