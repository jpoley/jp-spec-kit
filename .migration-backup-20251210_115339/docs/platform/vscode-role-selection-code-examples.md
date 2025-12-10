# VS Code Role Selection - Code Examples

**Date**: 2025-12-09
**Author**: Platform Engineer Agent

This document provides concrete code examples for implementing role-based VS Code Copilot integration.

---

## 1. specflow_workflow.yml Schema Extension

**File**: `/specflow_workflow.yml`

```yaml
# JPSpec Workflow Configuration
version: "1.1"

# ... existing states, workflows, transitions ...

# ==============================================================================
# VS CODE ROLE CONFIGURATION (NEW)
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
        - "speckit-analyze"
        - "speckit-clarify"

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
        - "speckit-implement"
        - "speckit-tasks"

    sec:
      name: "Security Engineer"
      description: "Security scanning, triage, vulnerability fixes"
      workflows:
        - "security_workflow"
        - "security_triage"
        - "security_fix"
        - "security_report"
        - "security_web"
        - "validate"
      agents:
        - "jpspec-security_workflow"
        - "jpspec-security_triage"
        - "jpspec-security_fix"
        - "jpspec-security_report"
        - "jpspec-security_web"
        - "jpspec-validate"  # Only security aspects
        - "speckit-checklist"

    qa:
      name: "QA Engineer"
      description: "Testing, documentation, quality validation"
      workflows:
        - "validate"
      agents:
        - "jpspec-validate"
        - "speckit-checklist"
        - "speckit-tasks"

    all:
      name: "Full Workflow"
      description: "Complete SDD workflow (all phases)"
      workflows: "*"  # All workflows
      agents: "*"     # All agents

  # Agent visibility modes
  visibility:
    primary_only: false    # If true, show ONLY primary role agents
    hide_others: false     # If true, hide non-role agents (vs de-prioritize)
    show_speckit: true     # Always show speckit utilities regardless of role

metadata:
  schema_version: "1.1"
  last_updated: "2025-12-09"
  vscode_role_count: 5
```

---

## 2. .vscode/settings.json Generation

**Function**: `generate_vscode_settings()`

```bash
#!/usr/bin/env bash
# generate_vscode_settings.sh
# Called by /jpspec:init and /jpspec:reset

generate_vscode_settings() {
    local primary_role="$1"
    local secondary_roles="${2:-}"  # Comma-separated: "qa,sec"
    local mode="${3:-user}"

    local settings_file=".vscode/settings.json"
    mkdir -p .vscode

    # Create settings.json if it doesn't exist
    if [[ ! -f "$settings_file" ]]; then
        echo "{}" > "$settings_file"
    fi

    # Merge JP Spec Kit role config using Python
    python3 << PYTHON
import json
from pathlib import Path

settings_file = Path("$settings_file")
settings = json.loads(settings_file.read_text())

# Add JP Spec Kit role configuration
settings["jpspec.vscode.role"] = {
    "primary": "$primary_role",
    "secondary": "$secondary_roles".split(",") if "$secondary_roles" else [],
    "visibility": "de-prioritize",  # "hide" | "de-prioritize" | "show-all"
    "mode": "$mode"
}

# Add VS Code Copilot agent pinning based on role
role_agents = {
    "pm": ["jpspec-assess", "jpspec-specify", "jpspec-research"],
    "dev": ["jpspec-plan", "jpspec-implement", "jpspec-operate"],
    "sec": [
        "jpspec-security_workflow",
        "jpspec-security_triage",
        "jpspec-security_fix",
        "jpspec-validate"
    ],
    "qa": ["jpspec-validate", "speckit-checklist", "speckit-tasks"],
    "all": []  # No pinning for all role
}

pinned = role_agents.get("$primary_role", [])
if pinned:
    settings["chat.agent.pinnedAgents"] = pinned

# Write back to file
settings_file.write_text(json.dumps(settings, indent=2) + "\n")
PYTHON

    echo "✓ Updated .vscode/settings.json with role: $primary_role"
}

# Usage example
generate_vscode_settings "dev" "qa,sec" "user"
```

**Output** (`.vscode/settings.json`):

```json
{
  "chat.promptFiles": true,
  "jpspec.vscode.role": {
    "primary": "dev",
    "secondary": [
      "qa",
      "sec"
    ],
    "visibility": "de-prioritize",
    "mode": "user"
  },
  "chat.agent.pinnedAgents": [
    "jpspec-plan",
    "jpspec-implement",
    "jpspec-operate"
  ]
}
```

---

## 3. Role Selection Prompt (init.md)

**File**: `templates/commands/jpspec/init.md`

```markdown
### Step 6.5: VS Code Role Configuration (Optional)

Detect if VS Code is likely being used:

```bash
# Check for VS Code indicators
if [[ -d ".vscode" ]] || [[ -n "${VSCODE_PID:-}" ]] || [[ "${TERM_PROGRAM:-}" == "vscode" ]]; then
  VSCODE_DETECTED=true
else
  VSCODE_DETECTED=false
fi

# Prompt for role configuration
if [[ "$VSCODE_DETECTED" == true ]] || [[ "$CONFIGURE_VSCODE" == true ]]; then
  echo ""
  echo "╔══════════════════════════════════════════════════════════════╗"
  echo "║         VS Code Copilot Role Configuration                   ║"
  echo "╚══════════════════════════════════════════════════════════════╝"
  echo ""
  echo "Select your primary role to customize VS Code chat handoffs:"
  echo ""
  echo "  1. Product Manager (PM)"
  echo "     Focus: Requirements, research, business validation"
  echo "     Commands: /jpspec:assess, /jpspec:specify, /jpspec:research"
  echo ""
  echo "  2. Developer (Dev)"
  echo "     Focus: Architecture, implementation, deployment"
  echo "     Commands: /jpspec:plan, /jpspec:implement, /jpspec:operate"
  echo ""
  echo "  3. Security Engineer (Sec)"
  echo "     Focus: Security scanning, triage, vulnerability fixes"
  echo "     Commands: /jpspec:security_*, /jpspec:validate (security only)"
  echo ""
  echo "  4. QA Engineer (QA)"
  echo "     Focus: Testing, documentation, quality validation"
  echo "     Commands: /jpspec:validate"
  echo ""
  echo "  5. Full Workflow (All) [default]"
  echo "     Focus: Complete SDD workflow (all phases)"
  echo "     Commands: All /jpspec and /speckit commands"
  echo ""
  echo "  6. Skip - Don't configure role-based UI"
  echo "     (All agents remain equally visible)"
  echo ""
  read -p "Choice [5]: " role_choice
  role_choice=${role_choice:-5}

  # Map choice to role ID
  case $role_choice in
    1) PRIMARY_ROLE="pm" ;;
    2) PRIMARY_ROLE="dev" ;;
    3) PRIMARY_ROLE="sec" ;;
    4) PRIMARY_ROLE="qa" ;;
    5) PRIMARY_ROLE="all" ;;
    6) PRIMARY_ROLE="skip" ;;
    *) echo "Invalid choice, using default (all)"; PRIMARY_ROLE="all" ;;
  esac

  if [[ "$PRIMARY_ROLE" != "skip" ]]; then
    # Multi-role support
    echo ""
    read -p "Would you like to add secondary roles? (y/N): " add_secondary
    SECONDARY_ROLES=""
    if [[ "${add_secondary,,}" == "y" ]]; then
      echo ""
      echo "Select secondary roles (comma-separated numbers):"
      echo "  [1] Product Manager"
      echo "  [2] Developer"
      echo "  [3] Security Engineer"
      echo "  [4] QA Engineer"
      echo ""
      read -p "Secondary roles []: " secondary_input

      # Convert numbers to role IDs
      SECONDARY_ROLES=""
      IFS=',' read -ra CHOICES <<< "$secondary_input"
      for choice in "${CHOICES[@]}"; do
        choice=$(echo "$choice" | xargs)  # Trim whitespace
        case $choice in
          1) SECONDARY_ROLES="${SECONDARY_ROLES}pm," ;;
          2) SECONDARY_ROLES="${SECONDARY_ROLES}dev," ;;
          3) SECONDARY_ROLES="${SECONDARY_ROLES}sec," ;;
          4) SECONDARY_ROLES="${SECONDARY_ROLES}qa," ;;
        esac
      done
      # Remove trailing comma
      SECONDARY_ROLES="${SECONDARY_ROLES%,}"
    fi

    # Team vs User mode
    echo ""
    echo "Configure role for:"
    echo "  1. This machine only (user-specific, gitignored)"
    echo "  2. Entire team (version-controlled, shared)"
    echo ""
    read -p "Mode [1]: " mode_choice
    mode_choice=${mode_choice:-1}

    case $mode_choice in
      1) CONFIG_MODE="user" ;;
      2) CONFIG_MODE="team" ;;
      *) echo "Invalid choice, using user mode"; CONFIG_MODE="user" ;;
    esac

    # Generate VS Code settings
    generate_vscode_settings "$PRIMARY_ROLE" "$SECONDARY_ROLES" "$CONFIG_MODE"

    # If team mode, update specflow_workflow.yml
    if [[ "$CONFIG_MODE" == "team" ]]; then
      python3 << PYTHON
import yaml
from pathlib import Path

workflow_file = Path("specflow_workflow.yml")
config = yaml.safe_load(workflow_file.read_text())

# Update default role
if "vscode_roles" not in config:
    config["vscode_roles"] = {}
config["vscode_roles"]["default_role"] = "$PRIMARY_ROLE"

workflow_file.write_text(yaml.dump(config, sort_keys=False))
PYTHON
      echo "✓ Updated specflow_workflow.yml with team default role"
    fi

    # Regenerate agents with role metadata
    echo ""
    echo "Generating VS Code Copilot agents with role metadata..."
    scripts/bash/sync-copilot-agents.sh --with-roles
  fi
fi
```
```

---

## 4. sync-copilot-agents.sh Enhancement

**File**: `scripts/bash/sync-copilot-agents.sh`

### New Function: `get_role_metadata()`

```bash
#!/usr/bin/env bash

# Get role metadata for an agent
get_role_metadata() {
    local namespace="$1"
    local command="$2"
    local config_file="${3:-specflow_workflow.yml}"

    # Agent name
    local agent_name="${namespace}-${command}"

    # Read role config from specflow_workflow.yml using Python
    local role_data
    role_data=$(python3 << PYTHON
import yaml
from pathlib import Path

config_file = Path("$config_file")
if not config_file.exists():
    print("")  # No config, no roles
    exit(0)

config = yaml.safe_load(config_file.read_text())
vscode_roles = config.get("vscode_roles", {}).get("roles", {})

agent_name = "$agent_name"
matching_roles = []

for role_id, role_config in vscode_roles.items():
    agents = role_config.get("agents", [])

    # Check if agent matches this role
    if agents == "*":
        # "all" role includes all agents
        matching_roles.append(role_id)
    elif agent_name in agents:
        matching_roles.append(role_id)

# Print roles as comma-separated
print(",".join(matching_roles))
PYTHON
)

    # If no roles found, skip metadata
    if [[ -z "$role_data" ]]; then
        echo ""
        return
    fi

    # Convert comma-separated to YAML array
    local roles_yaml=""
    IFS=',' read -ra ROLES <<< "$role_data"
    for role in "${ROLES[@]}"; do
        roles_yaml="${roles_yaml}  - \"${role}\"\n"
    done

    # Calculate priority based on roles
    local priority=50  # Default low priority
    if [[ "$role_data" == *"all"* ]]; then
        priority=10  # Utility agents (always shown)
    elif [[ "$role_data" == *"dev"* ]]; then
        priority=5   # High priority for dev role
    elif [[ "$role_data" == *"pm"* ]]; then
        priority=3   # High priority for PM role
    elif [[ "$role_data" == *"qa"* || "$role_data" == *"sec"* ]]; then
        priority=7   # Medium-high priority
    fi

    # Output YAML
    echo "roles:"
    echo -e "$roles_yaml"
    echo "priority: $priority"
}

# Example usage
get_role_metadata "jpspec" "plan"
# Output:
# roles:
#   - "dev"
#   - "all"
# priority: 5
```

### Modified Function: `generate_frontmatter()`

```bash
# Generate Copilot agent frontmatter with role metadata
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

    # NEW: Add role metadata if present
    if [[ -n "$role_metadata" ]]; then
        echo "$role_metadata"
    fi

    if [[ -n "$handoffs" ]]; then
        echo "$handoffs"
    fi
    echo "---"
}
```

### Enhanced CLI Options

```bash
# Parse arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --with-roles)
                WITH_ROLES=true
                shift
                ;;
            --role)
                ROLE_FILTER="$2"
                shift 2
                ;;
            --team-mode)
                CONFIG_SOURCE="specflow_workflow.yml"
                shift
                ;;
            --user-mode)
                CONFIG_SOURCE=".vscode/settings.json"
                shift
                ;;
            # ... existing flags ...
        esac
    done
}

# Default values
WITH_ROLES=true  # Add role metadata by default
ROLE_FILTER="all"  # Generate all agents (or specific role with --role)
CONFIG_SOURCE="specflow_workflow.yml"  # Team mode by default
```

---

## 5. Agent Frontmatter Example (Generated)

**File**: `.github/agents/jpspec-plan.agent.md`

```yaml
---
name: "jpspec-plan"
description: "Execute planning workflow using architect and platform engineer"
target: "chat"
tools:
  - "Read"
  - "Write"
  - "Edit"
  - "Grep"
  - "Glob"
  - "Bash"
  - "mcp__backlog__*"
  - "mcp__serena__*"
  - "Skill"
roles:
  - "dev"
  - "all"
priority: 5
handoffs:
  - label: "✓ Planning Complete → Begin Implementation"
    agent: "jpspec-implement"
    prompt: "Planning is complete. Begin implementing the feature according to the technical design."
    send: false
---

## User Input

```text
$ARGUMENTS
```

[... rest of agent content ...]
```

---

## 6. CI/CD Role Validation Workflow

**File**: `.github/workflows/validate-roles.yml`

```yaml
name: Validate Team Roles

on:
  pull_request:
    paths:
      - 'specflow_workflow.yml'
      - '.vscode/settings.json'

jobs:
  validate-role-config:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install pyyaml

      - name: Validate specflow_workflow.yml role definitions
        run: |
          python3 << 'PYTHON'
          import yaml
          from pathlib import Path

          config_file = Path("specflow_workflow.yml")
          config = yaml.safe_load(config_file.read_text())

          # Check vscode_roles section exists
          assert "vscode_roles" in config, "Missing vscode_roles section"

          # Check all required role definitions exist
          required_roles = ["pm", "dev", "sec", "qa", "all"]
          roles = config["vscode_roles"].get("roles", {})

          for role_id in required_roles:
              assert role_id in roles, f"Missing role definition: {role_id}"
              assert "name" in roles[role_id], f"Role {role_id} missing 'name'"
              assert "agents" in roles[role_id], f"Role {role_id} missing 'agents'"

          print("✓ All role definitions valid")
          PYTHON

      - name: Validate role-agent mappings
        run: |
          python3 << 'PYTHON'
          import yaml
          from pathlib import Path

          config = yaml.safe_load(Path("specflow_workflow.yml").read_text())
          roles = config["vscode_roles"]["roles"]

          # Check all referenced agents exist
          for role_id, role_config in roles.items():
              agents = role_config.get("agents", [])
              if agents == "*":
                  continue  # "all" role includes all agents

              for agent_name in agents:
                  agent_file = Path(f".github/agents/{agent_name}.agent.md")
                  assert agent_file.exists(), f"Agent {agent_name} not found for role {role_id}"

          print("✓ All role-agent mappings valid")
          PYTHON

      - name: Check .vscode/settings.json not committed in team mode
        run: |
          # Read default_role from specflow_workflow.yml
          DEFAULT_ROLE=$(python3 -c "
          import yaml
          config = yaml.safe_load(open('specflow_workflow.yml'))
          print(config.get('vscode_roles', {}).get('default_role', 'all'))
          ")

          # If default_role is set (team mode), .vscode/settings.json should not be committed
          if [[ "$DEFAULT_ROLE" != "all" ]]; then
            if git ls-files | grep -q '^.vscode/settings.json$'; then
              echo "ERROR: .vscode/settings.json is committed in team mode"
              echo "This file should be gitignored for user-specific configuration"
              exit 1
            fi
          fi

          echo "✓ No team mode conflicts"
```

---

## 7. Role Usage Telemetry

**File**: `src/specify_cli/telemetry.py`

```python
from enum import Enum
from pathlib import Path
import json
from datetime import datetime
import hashlib

class RoleEvent(Enum):
    """Role-related telemetry events."""
    ROLE_SELECTED = "role.selected"
    ROLE_SWITCHED = "role.switched"
    AGENT_INVOKED = "agent.invoked"
    HANDOFF_CLICKED = "handoff.clicked"

def hash_role(role: str) -> str:
    """Hash role for privacy-preserving telemetry."""
    return hashlib.sha256(role.encode()).hexdigest()[:8]

def track_role_event(event: RoleEvent, metadata: dict):
    """
    Track role-related events for analytics.

    Args:
        event: Event type (from RoleEvent enum)
        metadata: Event metadata (role, agent, workflow, etc.)

    Example:
        track_role_event(RoleEvent.ROLE_SELECTED, {
            "role": "dev",
            "mode": "team"
        })
    """
    from specify_cli.config import load_config

    # Check if telemetry enabled
    config = load_config()
    if not config.get("telemetry", {}).get("enabled", False):
        return

    event_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event.value,
        "metadata": {
            # Hash sensitive data
            "role_hash": hash_role(metadata.get("role", "unknown")),
            "agent": metadata.get("agent"),  # Agent names are not PII
            "workflow": metadata.get("workflow"),
            "mode": metadata.get("mode"),
            # No project names, file paths, or other PII
        }
    }

    # Write to local telemetry file
    telemetry_file = Path(".jpspec/telemetry.jsonl")
    telemetry_file.parent.mkdir(exist_ok=True)

    with telemetry_file.open("a") as f:
        f.write(json.dumps(event_data) + "\n")

# Usage in init.md / reset.md commands
from specify_cli.telemetry import track_role_event, RoleEvent

# After role selection
track_role_event(RoleEvent.ROLE_SELECTED, {
    "role": primary_role,
    "mode": "team" if team_mode else "user",
    "secondary_roles_count": len(secondary_roles)
})
```

**Telemetry Output** (`.jpspec/telemetry.jsonl`):

```jsonl
{"timestamp": "2025-12-09T15:30:00Z", "event": "role.selected", "metadata": {"role_hash": "a1b2c3d4", "agent": null, "workflow": null, "mode": "team"}}
{"timestamp": "2025-12-09T15:35:00Z", "event": "agent.invoked", "metadata": {"role_hash": "a1b2c3d4", "agent": "jpspec-plan", "workflow": "plan", "mode": null}}
{"timestamp": "2025-12-09T15:40:00Z", "event": "handoff.clicked", "metadata": {"role_hash": "a1b2c3d4", "agent": "jpspec-implement", "workflow": "implement", "mode": null}}
```

---

## 8. Query Telemetry Data (Analytics)

```python
# scripts/python/analyze_role_usage.py
import json
from pathlib import Path
from collections import Counter, defaultdict

def analyze_telemetry():
    """Analyze role usage patterns from telemetry data."""

    telemetry_file = Path(".jpspec/telemetry.jsonl")
    if not telemetry_file.exists():
        print("No telemetry data found")
        return

    # Parse events
    events = []
    with telemetry_file.open() as f:
        for line in f:
            events.append(json.loads(line))

    # Role selection breakdown
    role_selections = Counter()
    for event in events:
        if event["event"] == "role.selected":
            role_hash = event["metadata"]["role_hash"]
            role_selections[role_hash] += 1

    print("Role Selection Frequency:")
    for role_hash, count in role_selections.most_common():
        print(f"  {role_hash}: {count} times")

    # Most-used agents
    agent_invocations = Counter()
    for event in events:
        if event["event"] == "agent.invoked":
            agent = event["metadata"]["agent"]
            agent_invocations[agent] += 1

    print("\nMost-Used Agents:")
    for agent, count in agent_invocations.most_common(10):
        print(f"  {agent}: {count} invocations")

    # Handoff click-through rate
    handoff_clicks = len([e for e in events if e["event"] == "handoff.clicked"])
    agent_completions = len([e for e in events if e["event"] == "agent.invoked"])

    if agent_completions > 0:
        ctr = (handoff_clicks / agent_completions) * 100
        print(f"\nHandoff Click-Through Rate: {ctr:.1f}%")

if __name__ == "__main__":
    analyze_telemetry()
```

**Output**:

```
Role Selection Frequency:
  a1b2c3d4: 15 times
  e5f6g7h8: 8 times
  i9j0k1l2: 3 times

Most-Used Agents:
  jpspec-implement: 42 invocations
  jpspec-plan: 38 invocations
  jpspec-validate: 25 invocations
  jpspec-specify: 18 invocations
  jpspec-assess: 15 invocations

Handoff Click-Through Rate: 87.3%
```

---

*Code examples by Platform Engineer Agent on 2025-12-09*
