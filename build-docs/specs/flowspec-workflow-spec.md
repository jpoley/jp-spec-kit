# Flowspec Workflow Configuration Specification

**Version:** 1.0.0
**Status:** Authoritative
**Last Updated:** 2025-11-30

---

## 1. Overview

### 1.1 Purpose

This specification defines the schema and semantics for `flowspec_workflow.yml`, a YAML configuration file that describes:

1. **Task States** - Valid lifecycle states for development tasks
2. **Workflows** - Slash commands (`/flow:*`) that orchestrate agents
3. **Agents** - Specialized AI personas with defined responsibilities
4. **Transitions** - Valid state changes between lifecycle stages
5. **Agent Loops** - Classification of agents by execution model (inner/outer)

### 1.2 Use Cases

- **Workflow Orchestration**: Define how `/flow:*` commands execute
- **Agent Assignment**: Map agents to workflows with clear responsibilities
- **State Machine Validation**: Ensure tasks progress through valid states
- **UI Tool Generation**: Serve as the data source for workflow editors/visualizers

### 1.3 Design Principles

1. **Single Source of Truth**: This file is authoritative for workflow behavior
2. **Machine-Parseable**: Valid YAML that tools can programmatically consume
3. **Human-Readable**: Clear structure with inline documentation
4. **Extensible**: Schema supports future workflow/agent additions
5. **Validated**: Tests ensure schema compliance and state machine integrity

---

## 2. File Structure

```yaml
version: "1.0"

states:
  - <state_name>
  ...

workflows:
  <workflow_name>:
    command: <string>
    description: <string>
    agents:
      - <agent_object>
    input_states:
      - <state_name>
    output_state: <state_name>
    optional: <boolean>
    # ... additional properties

transitions:
  - from: <state_name>
    to: <state_name>
    via: <workflow_name | "manual" | "rework" | "rollback">
    description: <string>

agent_loops:
  inner:
    description: <string>
    characteristics:
      - <string>
    agents:
      - <agent_name>
  outer:
    description: <string>
    characteristics:
      - <string>
    agents:
      - <agent_name>

metadata:
  schema_version: <string>
  last_updated: <date>
  state_count: <integer>
  workflow_count: <integer>
  agent_count: <integer>
  inner_loop_agent_count: <integer>
  outer_loop_agent_count: <integer>
  transition_count: <integer>
  documentation:
    - <path>
```

---

## 3. Schema Definitions

### 3.1 Root Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | string | Yes | Schema version (e.g., "1.0") |
| `states` | array[string] | Yes | Ordered list of valid task states |
| `workflows` | object | Yes | Map of workflow name to workflow definition |
| `transitions` | array[Transition] | Yes | Valid state transitions |
| `agent_loops` | AgentLoops | Yes | Inner/outer loop classification |
| `metadata` | Metadata | Yes | Configuration metadata and counts |

### 3.2 States Array

An ordered list of state names (strings). Order is significant:
- **First element**: Initial state (must be "To Do")
- **Last element**: Terminal state (must be "Done")

**Constraints:**
- Minimum 2 states (initial + terminal)
- No duplicates
- All states referenced in workflows/transitions must exist

**Example:**
```yaml
states:
  - "To Do"          # Initial state
  - "Specified"
  - "Researched"
  - "Planned"
  - "In Implementation"
  - "Validated"
  - "Deployed"
  - "Done"           # Terminal state
```

### 3.3 Workflow Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `command` | string | Yes | Slash command (e.g., "/flow:specify") |
| `description` | string | Yes | Human-readable workflow description |
| `agents` | array[Agent] | Yes | Agents assigned to this workflow |
| `input_states` | array[string] | Yes | Valid entry states for this workflow |
| `output_state` | string | Yes | State after workflow completion |
| `optional` | boolean | No | If true, workflow can be skipped (default: false) |
| `execution_mode` | string | No | "sequential" (default) or "parallel" |
| `creates_backlog_tasks` | boolean | No | Workflow creates new backlog tasks |
| `requires_backlog_tasks` | boolean | No | Requires existing tasks to run |
| `requires_human_approval` | boolean | No | Human approval gate required |
| `quality_gate` | string | No | CLI command that must pass first |
| `builds_constitution` | boolean | No | Contributes to project constitution |

**Command Naming Convention:**
- Pattern: `/flow:<workflow_name>`
- Example: Workflow "specify" → command "/flow:specify"

**Example:**
```yaml
workflows:
  implement:
    command: "/flow:implement"
    description: "Execute implementation using specialized engineer agents"
    agents:
      - name: "frontend-engineer"
        identity: "@frontend-engineer"
        description: "Senior Frontend Engineer"
        responsibilities:
          - "Component development"
          - "Frontend testing"
    input_states:
      - "Planned"
    output_state: "In Implementation"
    optional: false
    requires_backlog_tasks: true
    quality_gate: "specify gate"
```

### 3.4 Agent Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique agent identifier (kebab-case) |
| `identity` | string | Yes | Agent reference for backlog (e.g., "@pm-planner") |
| `description` | string | Yes | Human-readable role description |
| `responsibilities` | array[string] | Yes | List of agent responsibilities |

**Naming Conventions:**
- `name`: kebab-case identifier (e.g., "frontend-engineer")
- `identity`: @-prefixed reference (e.g., "@frontend-engineer")

**Example:**
```yaml
agents:
  - name: "software-architect"
    identity: "@software-architect"
    description: "Enterprise Software Architect using Gregor Hohpe's principles"
    responsibilities:
      - "Strategic framing (Penthouse-Engine Room continuum)"
      - "System architecture and component design"
      - "Architecture Decision Records (ADRs)"
      - "Platform Quality Framework (7 C's) assessment"
```

### 3.5 Transition Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `from` | string | Yes | Source state |
| `to` | string | Yes | Target state |
| `via` | string | Yes | Workflow name, "manual", "rework", or "rollback" |
| `description` | string | No | Human-readable transition description |

**Transition Types:**
- **Workflow**: Normal forward progression via a workflow
- **Manual**: Human-triggered transition (typically to "Done")
- **Rework**: Backward transition to address issues
- **Rollback**: Emergency backward transition from production

**Example:**
```yaml
transitions:
  # Forward workflow transition
  - from: "Planned"
    to: "In Implementation"
    via: "implement"
    description: "Implementation work started"

  # Manual terminal transition
  - from: "Deployed"
    to: "Done"
    via: "manual"
    description: "Production deployment confirmed successful"

  # Backward rework transition
  - from: "Validated"
    to: "In Implementation"
    via: "rework"
    description: "Rework needed based on validation findings"
```

### 3.6 Agent Loops Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `inner` | LoopDefinition | Yes | Inner loop (fast, local) agents |
| `outer` | LoopDefinition | Yes | Outer loop (CI/CD, governance) agents |

**LoopDefinition:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `description` | string | Yes | Loop purpose description |
| `characteristics` | array[string] | Yes | Loop execution characteristics |
| `agents` | array[string] | Yes | Agent names in this loop |

**Inner Loop Characteristics:**
- Immediate feedback (< 2s hot reload)
- Local execution before commit
- Code writing and testing focus
- Pre-commit validation

**Outer Loop Characteristics:**
- Post-commit execution
- CI/CD pipeline integration
- Production deployment focus
- Compliance and security gates

**Constraints:**
- Every agent in workflows must be classified
- No agent can appear in both loops

### 3.7 Metadata Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `schema_version` | string | Yes | Schema version for compatibility |
| `last_updated` | string | Yes | ISO date of last update |
| `state_count` | integer | Yes | Number of states (for validation) |
| `workflow_count` | integer | Yes | Number of workflows |
| `agent_count` | integer | Yes | Unique agents across workflows |
| `inner_loop_agent_count` | integer | Yes | Agents in inner loop |
| `outer_loop_agent_count` | integer | Yes | Agents in outer loop |
| `transition_count` | integer | Yes | Number of transitions |
| `documentation` | array[string] | No | Paths to related documentation |

---

## 4. Validation Rules

### 4.1 State Machine Integrity

1. **Reachability**: All states must be reachable from the initial state
2. **No Forward Cycles**: Primary workflow path must form a DAG
3. **Terminal Reachability**: "Done" state must be reachable from all states

### 4.2 Workflow Consistency

1. **Valid States**: All `input_states` and `output_state` must exist in `states`
2. **Transition Match**: Each workflow's output must have a matching transition
3. **Command Pattern**: Commands must follow `/flow:<name>` pattern

### 4.3 Agent Classification

1. **Complete Coverage**: Every workflow agent must be in `inner` or `outer` loop
2. **No Overlap**: No agent can be in both loops
3. **Count Accuracy**: Metadata counts must match actual counts

### 4.4 Metadata Accuracy

All metadata count fields must equal their corresponding actual values:
- `state_count` == len(states)
- `workflow_count` == len(workflows)
- `agent_count` == count of unique agents across all workflows
- `inner_loop_agent_count` == len(agent_loops.inner.agents)
- `outer_loop_agent_count` == len(agent_loops.outer.agents)

---

## 5. Current Workflow Reference

### 5.1 Complete Workflow List

| Workflow | Command | Agents | Input States | Output State |
|----------|---------|--------|--------------|--------------|
| specify | /flow:specify | product-requirements-manager | To Do | Specified |
| research | /flow:research | researcher, business-validator | Specified | Researched |
| plan | /flow:plan | software-architect, platform-engineer | Specified, Researched | Planned |
| implement | /flow:implement | frontend-engineer, backend-engineer, ai-ml-engineer, frontend-code-reviewer, backend-code-reviewer | Planned | In Implementation |
| validate | /flow:validate | quality-guardian, secure-by-design-engineer, tech-writer, release-manager | In Implementation | Validated |
| operate | /flow:operate | sre-agent | Validated | Deployed |

### 5.2 Complete Agent Registry

| Agent Name | Identity | Loop | Primary Workflow |
|------------|----------|------|------------------|
| product-requirements-manager | @pm-planner | outer | specify |
| researcher | @researcher | outer | research |
| business-validator | @business-validator | outer | research |
| software-architect | @software-architect | outer | plan |
| platform-engineer | @platform-engineer | outer | plan |
| frontend-engineer | @frontend-engineer | inner | implement |
| backend-engineer | @backend-engineer | inner | implement |
| ai-ml-engineer | @ai-ml-engineer | inner | implement |
| frontend-code-reviewer | @frontend-code-reviewer | inner | implement |
| backend-code-reviewer | @backend-code-reviewer | inner | implement |
| quality-guardian | @quality-guardian | outer | validate |
| secure-by-design-engineer | @secure-by-design-engineer | outer | validate |
| tech-writer | @tech-writer | outer | validate |
| release-manager | @release-manager | outer | validate |
| sre-agent | @sre-agent | outer | operate |

### 5.3 State Transition Graph

```
[To Do]
   |
   v (specify)
[Specified]
   |
   +----> (research) ----> [Researched]
   |                            |
   +----------------------------+
   |
   v (plan)
[Planned]
   |
   v (implement)
[In Implementation] <-----(rework)----+
   |                                   |
   v (validate)                        |
[Validated] <---------(rework)---------+
   |                                   |
   v (operate)                         |
[Deployed] <--------(rollback)---------+
   |
   v (manual)
[Done]
```

---

## 6. Extension Guidelines

### 6.1 Adding a New Workflow

1. Define workflow object with all required fields
2. Create at least one agent with responsibilities
3. Add transition(s) connecting to existing states
4. Classify agent(s) in appropriate loop
5. Update metadata counts
6. Create corresponding `/flow:<name>` command file

### 6.2 Adding a New Agent

1. Define agent object in workflow's `agents` array
2. Use kebab-case name and @-prefixed identity
3. List 3-6 specific responsibilities
4. Add agent name to `inner` or `outer` loop
5. Update `agent_count` and loop-specific count in metadata

### 6.3 Adding a New State

1. Add state to `states` array in logical order
2. Add transition(s) to/from the state
3. Update any workflow `input_states` or `output_state` as needed
4. Update `state_count` in metadata
5. Verify state reachability

---

## 7. JSON Schema (For UI Tools)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Flowspec Workflow Configuration",
  "type": "object",
  "required": ["version", "states", "workflows", "transitions", "agent_loops", "metadata"],
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+$"
    },
    "states": {
      "type": "array",
      "items": { "type": "string" },
      "minItems": 2,
      "uniqueItems": true
    },
    "workflows": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "required": ["command", "description", "agents", "input_states", "output_state"],
        "properties": {
          "command": { "type": "string", "pattern": "^/flow:" },
          "description": { "type": "string" },
          "agents": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["name", "identity", "description", "responsibilities"],
              "properties": {
                "name": { "type": "string", "pattern": "^[a-z][a-z0-9-]*$" },
                "identity": { "type": "string", "pattern": "^@[a-z][a-z0-9-]*$" },
                "description": { "type": "string" },
                "responsibilities": {
                  "type": "array",
                  "items": { "type": "string" },
                  "minItems": 1
                }
              }
            },
            "minItems": 1
          },
          "input_states": {
            "type": "array",
            "items": { "type": "string" },
            "minItems": 1
          },
          "output_state": { "type": "string" },
          "optional": { "type": "boolean", "default": false },
          "execution_mode": { "type": "string", "enum": ["sequential", "parallel"] },
          "creates_backlog_tasks": { "type": "boolean" },
          "requires_backlog_tasks": { "type": "boolean" },
          "requires_human_approval": { "type": "boolean" },
          "quality_gate": { "type": "string" },
          "builds_constitution": { "type": "boolean" }
        }
      }
    },
    "transitions": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["from", "to", "via"],
        "properties": {
          "from": { "type": "string" },
          "to": { "type": "string" },
          "via": { "type": "string" },
          "description": { "type": "string" }
        }
      }
    },
    "agent_loops": {
      "type": "object",
      "required": ["inner", "outer"],
      "properties": {
        "inner": { "$ref": "#/definitions/loop_definition" },
        "outer": { "$ref": "#/definitions/loop_definition" }
      }
    },
    "metadata": {
      "type": "object",
      "required": ["schema_version", "last_updated", "state_count", "workflow_count", "agent_count", "inner_loop_agent_count", "outer_loop_agent_count"],
      "properties": {
        "schema_version": { "type": "string" },
        "last_updated": { "type": "string", "format": "date" },
        "state_count": { "type": "integer", "minimum": 2 },
        "workflow_count": { "type": "integer", "minimum": 1 },
        "agent_count": { "type": "integer", "minimum": 1 },
        "inner_loop_agent_count": { "type": "integer", "minimum": 0 },
        "outer_loop_agent_count": { "type": "integer", "minimum": 0 },
        "transition_count": { "type": "integer", "minimum": 1 },
        "documentation": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    }
  },
  "definitions": {
    "loop_definition": {
      "type": "object",
      "required": ["description", "characteristics", "agents"],
      "properties": {
        "description": { "type": "string" },
        "characteristics": {
          "type": "array",
          "items": { "type": "string" }
        },
        "agents": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    }
  }
}
```

---

## 8. Implementation Notes

### 8.1 File Location

The workflow configuration file should be placed at the project root:
```
project/
├── flowspec_workflow.yml    # <-- This file
├── .specify/
├── .claude/
│   └── commands/
│       └── flowspec/
│           ├── specify.md
│           ├── research.md
│           ├── plan.md
│           ├── implement.md
│           ├── validate.md
│           └── operate.md
└── ...
```

### 8.2 Programmatic Access

```python
import yaml
from pathlib import Path

def load_workflow_config(path: Path = Path("flowspec_workflow.yml")) -> dict:
    """Load and return the workflow configuration."""
    with open(path) as f:
        return yaml.safe_load(f)

# Usage
config = load_workflow_config()
workflows = config["workflows"]
states = config["states"]
```

### 8.3 Validation Test Suite

The configuration includes a comprehensive test suite at `tests/test_workflow_config_valid.py` that validates:

1. YAML syntax and structure
2. Required sections presence
3. State machine integrity (reachability, no cycles)
4. Workflow consistency (valid states, transitions)
5. Agent classification completeness
6. Metadata accuracy

Run with: `pytest tests/test_workflow_config_valid.py -v`

---

## 9. Changelog

### Version 1.0.0 (2025-11-30)

- Initial specification release
- 8 states: To Do → Specified → Researched → Planned → In Implementation → Validated → Deployed → Done
- 6 workflows: specify, research, plan, implement, validate, operate
- 15 agents across inner (5) and outer (10) loops
- 12 transitions (7 forward, 3 manual/terminal, 2 rework/rollback)
- Complete JSON Schema for UI tooling
- Comprehensive validation test suite

---

## 10. References

- [Agent Loop Classification](docs/reference/agent-loop-classification.md)
- [Inner Loop Reference](docs/reference/inner-loop.md)
- [Outer Loop Reference](docs/reference/outer-loop.md)
- [Flowspec Command Implementations](.claude/commands/flow/*.md)
