# Workflow Schema Reference

This document describes the JSON Schema used to validate `flowspec_workflow.yml` configuration files.

## Overview

The workflow schema (`memory/flowspec_workflow.schema.json`) validates the structure and content of workflow configuration files. It ensures that:

- All required fields are present
- Field types are correct
- Command names follow the `/flow:` pattern
- Arrays have required minimum items
- No typos via `additionalProperties: false`

## Schema Location

```
memory/flowspec_workflow.schema.json
```

## Top-Level Structure

```yaml
version: "1.0"                    # Required: Version string (format: X.Y)
description: "..."                # Optional: Human-readable description
states: [...]                     # Required: Array of state definitions
workflows: {...}                  # Required: Object mapping workflow names to definitions
transitions: [...]                # Required: Array of state transitions
agent_loops: {...}                # Optional: Agent loop classifications
```

## Field Definitions

### version (required)

The configuration version number.

| Property | Value |
|----------|-------|
| Type | `string` |
| Pattern | `^\d+\.\d+$` |
| Examples | `"1.0"`, `"2.0"`, `"10.5"` |

**Valid:**
```yaml
version: "1.0"
```

**Invalid:**
```yaml
version: "1"        # Missing minor version
version: "1.0.0"    # Too many parts
version: "v1.0"     # No 'v' prefix allowed
```

### states (required)

Array of custom workflow states beyond the default "To Do" and "Done".

| Property | Value |
|----------|-------|
| Type | `array` |
| Min Items | 1 |
| Unique Items | Yes |
| Item Type | `state` object |

#### State Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique state name (min 1 char) |
| `description` | string | No | Human-readable description |

**Example:**
```yaml
states:
  - name: "Specified"
    description: "Feature specification created"
  - name: "Planned"
    description: "Technical plan created"
  - name: "In Implementation"
```

### workflows (required)

Object mapping workflow names to their definitions.

| Property | Value |
|----------|-------|
| Type | `object` |
| Min Properties | 1 |
| Property Name Pattern | `^[a-z][a-z0-9_]*$` |

#### Workflow Object

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `command` | string | Yes | - | The `/flow:` command (pattern: `^/flow:[a-z][a-z0-9_]*$`) |
| `agents` | array | Yes | - | List of agent names (min 1, unique) |
| `input_states` | array | Yes | - | Valid source states (min 1, unique) |
| `output_state` | string | Yes | - | Destination state after completion |
| `description` | string | No | - | Human-readable description |
| `optional` | boolean | No | `false` | Whether this phase can be skipped |

**Example:**
```yaml
workflows:
  specify:
    command: "/flow:specify"
    agents:
      - "product-requirements-manager"
    input_states:
      - "To Do"
    output_state: "Specified"
    description: "Create feature specification"
    optional: false

  research:
    command: "/flow:research"
    agents:
      - "researcher"
      - "business-validator"
    input_states:
      - "Specified"
    output_state: "Researched"
```

### transitions (required)

Array of state transitions forming a DAG (Directed Acyclic Graph).

| Property | Value |
|----------|-------|
| Type | `array` |
| Min Items | 1 |
| Item Type | `transition` object |

#### Transition Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `from` | string | Yes | Source state name |
| `to` | string | Yes | Destination state name |
| `via` | string | Yes | Workflow name that triggers this transition |

**Example:**
```yaml
transitions:
  - from: "To Do"
    to: "Specified"
    via: "specify"
  - from: "Specified"
    to: "Researched"
    via: "research"
  - from: "Deployed"
    to: "Done"
    via: "completion"
```

### agent_loops (optional)

Classification of agents into inner and outer development loops.

| Property | Value |
|----------|-------|
| Type | `object` |
| Additional Properties | No |

#### Agent Loops Properties

| Field | Type | Description |
|-------|------|-------------|
| `inner_loop` | array | Agents in the inner development loop (frequent execution) |
| `outer_loop` | array | Agents in the outer loop (operational, less frequent) |

**Example:**
```yaml
agent_loops:
  inner_loop:
    - "product-requirements-manager"
    - "software-architect"
    - "frontend-engineer"
    - "backend-engineer"
  outer_loop:
    - "sre-agent"
    - "release-manager"
```

## Validation Rules

### Command Pattern

All workflow commands must match the pattern `/flow:[a-z][a-z0-9_]*`:

| Pattern | Valid | Reason |
|---------|-------|--------|
| `/flow:specify` | Yes | Correct format |
| `/flow:implement` | Yes | Correct format |
| `/flow:security_audit` | Yes | Underscores allowed |
| `flow:specify` | No | Missing leading slash |
| `/speckit:specify` | No | Wrong prefix |
| `/flow:Specify` | No | Uppercase not allowed |
| `/flow:` | No | Empty action |

### Uniqueness Constraints

The following must be unique within their respective arrays:

- State objects (entire object must be unique)
- Agent names within a workflow
- Input states within a workflow
- Agent names within `inner_loop`
- Agent names within `outer_loop`

### Additional Properties

All objects use `additionalProperties: false` to catch typos:

```yaml
# This will FAIL validation
workflows:
  specify:
    comand: "/flow:specify"  # Typo: "comand" instead of "command"
    agents: ["pm"]
    input_states: ["To Do"]
    output_state: "Done"
```

## Complete Example

```yaml
version: "1.0"
description: "Default Flowspec specification-driven development workflow"

states:
  - name: "Specified"
    description: "Feature specification created"
  - name: "Researched"
    description: "Business viability researched"
  - name: "Planned"
    description: "Technical plan created"
  - name: "In Implementation"
    description: "Feature being implemented"
  - name: "Validated"
    description: "Feature validated"
  - name: "Deployed"
    description: "Feature deployed"

workflows:
  specify:
    command: "/flow:specify"
    agents:
      - "product-requirements-manager"
    input_states:
      - "To Do"
    output_state: "Specified"
    description: "Create feature specification"
    optional: false

  research:
    command: "/flow:research"
    agents:
      - "researcher"
      - "business-validator"
    input_states:
      - "Specified"
    output_state: "Researched"
    description: "Validate business viability"
    optional: false

  plan:
    command: "/flow:plan"
    agents:
      - "software-architect"
      - "platform-engineer"
    input_states:
      - "Researched"
    output_state: "Planned"
    description: "Create technical plan"
    optional: false

  implement:
    command: "/flow:implement"
    agents:
      - "frontend-engineer"
      - "backend-engineer"
      - "code-reviewer"
    input_states:
      - "Planned"
    output_state: "In Implementation"
    description: "Implement feature"
    optional: false

  validate:
    command: "/flow:validate"
    agents:
      - "quality-guardian"
      - "secure-by-design-engineer"
      - "tech-writer"
      - "release-manager"
    input_states:
      - "In Implementation"
    output_state: "Validated"
    description: "Validate implementation"
    optional: false

  operate:
    command: "/flow:operate"
    agents:
      - "sre-agent"
    input_states:
      - "Validated"
    output_state: "Deployed"
    description: "Deploy to production"
    optional: true

transitions:
  - from: "To Do"
    to: "Specified"
    via: "specify"
  - from: "Specified"
    to: "Researched"
    via: "research"
  - from: "Researched"
    to: "Planned"
    via: "plan"
  - from: "Planned"
    to: "In Implementation"
    via: "implement"
  - from: "In Implementation"
    to: "Validated"
    via: "validate"
  - from: "Validated"
    to: "Deployed"
    via: "operate"
  - from: "Deployed"
    to: "Done"
    via: "completion"

agent_loops:
  inner_loop:
    - "product-requirements-manager"
    - "software-architect"
    - "platform-engineer"
    - "researcher"
    - "business-validator"
    - "frontend-engineer"
    - "backend-engineer"
    - "quality-guardian"
    - "secure-by-design-engineer"
    - "tech-writer"
  outer_loop:
    - "sre-agent"
    - "release-manager"
```

## Common Validation Errors

### Missing Required Field

```
Error: 'command' is a required property
Path: workflows/specify
Fix: Add the missing 'command' field to the workflow definition
```

### Invalid Version Format

```
Error: '1' does not match '^\\d+\\.\\d+$'
Path: version
Fix: Use format "X.Y" (e.g., "1.0")
```

### Invalid Command Pattern

```
Error: 'flow:specify' does not match '^/flow:[a-z][a-z0-9_]*$'
Path: workflows/specify/command
Fix: Add leading slash: "/flow:specify"
```

### Extra Property (Typo)

```
Error: Additional properties are not allowed ('comand' was unexpected)
Path: workflows/specify
Fix: Check spelling - should be 'command' not 'comand'
```

### Empty Array

```
Error: [] is too short
Path: states
Fix: Add at least one state definition
```

## Programmatic Validation

### Python Example

```python
import json
import yaml
from jsonschema import validate, ValidationError, Draft7Validator

# Load schema
with open("memory/flowspec_workflow.schema.json") as f:
    schema = json.load(f)

# Load config
with open("flowspec_workflow.yml") as f:
    config = yaml.safe_load(f)

# Simple validation (raises on first error)
try:
    validate(instance=config, schema=schema)
    print("Configuration is valid!")
except ValidationError as e:
    print(f"Validation error: {e.message}")
    print(f"Path: {'/'.join(str(p) for p in e.absolute_path)}")

# Collect all errors
validator = Draft7Validator(schema)
errors = list(validator.iter_errors(config))
for error in errors:
    print(f"- {error.message} at {'/'.join(str(p) for p in error.absolute_path)}")
```

## Related Documentation

- [Workflow Design Spec](../../memory/WORKFLOW_DESIGN_SPEC.md) - Full design specification
- [Inner Loop Reference](./inner-loop.md) - Inner loop agent documentation
- [Outer Loop Reference](./outer-loop.md) - Outer loop agent documentation
- [Agent Loop Classification](./agent-loop-classification.md) - Agent classification guide
