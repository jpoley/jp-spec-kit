# flowspec_workflow.yml Schema Validation

This document provides examples and guidance for validating `flowspec_workflow.yml` configuration files using the JSON Schema at `memory/flowspec_workflow.schema.json`.

## Overview

The JSON Schema validates:

- **Structure**: Ensures all required fields are present (version, states, workflows, transitions)
- **Types**: Validates correct data types (strings, arrays, objects, booleans, integers)
- **Formats**: Enforces patterns like `/flow:*` for commands, `@agent-name` for agent identities
- **Relationships**: Validates uniqueness constraints, minimum items, and allowed values
- **Completeness**: Checks artifact definitions, agent loops, and metadata

## Quick Validation

### Using Python

```python
import json
import yaml
from jsonschema import validate, ValidationError

# Load schema
with open('memory/flowspec_workflow.schema.json') as f:
    schema = json.load(f)

# Load workflow config
with open('flowspec_workflow.yml') as f:
    workflow = yaml.safe_load(f)

# Validate
try:
    validate(instance=workflow, schema=schema)
    print("✅ Configuration is valid")
except ValidationError as e:
    print(f"❌ Validation error: {e.message}")
    print(f"   At path: {' -> '.join(str(p) for p in e.absolute_path)}")
```

### Using jsonschema CLI

```bash
# Install jsonschema CLI tool
pip install check-jsonschema

# Validate workflow YAML
check-jsonschema --schemafile memory/flowspec_workflow.schema.json flowspec_workflow.yml
```

## Schema Structure

### Top-Level Properties

| Property       | Required | Type   | Description                                          |
|----------------|----------|--------|------------------------------------------------------|
| `version`      | Yes      | string | Config version (e.g., "1.0", "1.1")                  |
| `states`       | Yes      | array  | List of workflow states (strings or objects)         |
| `workflows`    | Yes      | object | Workflow definitions keyed by workflow name          |
| `transitions`  | Yes      | array  | State transition definitions                         |
| `agent_loops`  | No       | object | Agent classification (inner/outer loops)             |
| `metadata`     | No       | object | Optional metadata (counts, dates, etc.)              |

### States

States can be defined in two formats:

**Simple format** (strings):
```yaml
states:
  - "To Do"
  - "Assessed"
  - "Specified"
```

**Object format** (with descriptions):
```yaml
states:
  - name: "Specified"
    description: "Feature specification created"
  - name: "Planned"
    description: "Technical architecture planned"
```

### Workflows

Workflow definitions must include:

| Field           | Required | Type    | Description                                    |
|-----------------|----------|---------|------------------------------------------------|
| `command`       | Yes      | string  | Slash command (pattern: `/flow:[a-z][a-z0-9_]*`)      |
| `agents`        | Yes      | array   | Agent names or agent objects                   |
| `input_states`  | Yes      | array   | Valid states to start this workflow            |
| `output_state`  | Yes      | string  | State after workflow completes                 |
| `description`   | No       | string  | Human-readable description                     |
| `optional`      | No       | boolean | Whether workflow can be skipped (default false)|

**Additional workflow properties**:
- `execution_mode`: "sequential" or "parallel"
- `creates_backlog_tasks`: boolean (default false)
- `requires_backlog_tasks`: boolean (default false)
- `requires_human_approval`: boolean (default false)
- `builds_constitution`: boolean (default false)

### Agents

Agents can be simple strings or detailed objects:

**Simple format**:
```yaml
agents:
  - "product-requirements-manager"
  - "software-architect"
```

**Object format**:
```yaml
agents:
  - name: "product-requirements-manager"
    identity: "@pm-planner"
    description: "Senior Product Strategy Advisor"
    responsibilities:
      - "Create comprehensive PRDs"
      - "Define user stories and acceptance criteria"
```

### Transitions

Transition definitions:

| Field               | Required | Type   | Description                                  |
|---------------------|----------|--------|----------------------------------------------|
| `from`              | Yes      | string | Source state name                            |
| `to`                | Yes      | string | Destination state name                       |
| `via`               | Yes      | string | Workflow name or type (manual/rework/etc.)   |
| `name`              | No       | string | Unique transition name                       |
| `description`       | No       | string | Human-readable description                   |
| `input_artifacts`   | No       | array  | Required input artifacts                     |
| `output_artifacts`  | No       | array  | Produced output artifacts                    |
| `validation`        | No       | enum   | "NONE", "KEYWORD", or "PULL_REQUEST"         |

### Artifacts

Artifact definitions for transitions:

| Field      | Required | Type    | Description                                       |
|------------|----------|---------|---------------------------------------------------|
| `type`     | Yes      | string  | Artifact type (e.g., "prd", "adr", "tests")       |
| `path`     | Yes      | string  | Path pattern (supports {feature}, {NNN}, {slug})  |
| `required` | No       | boolean | Whether artifact is required (default false)      |
| `multiple` | No       | boolean | Whether multiple artifacts expected (default false)|

### Agent Loops

Two formats supported:

**New format** (with descriptions):
```yaml
agent_loops:
  inner:
    description: "Fast execution - optimized for developer velocity"
    agents:
      - "frontend-engineer"
      - "backend-engineer"
  outer:
    description: "Governance-focused - optimized for safety"
    agents:
      - "sre-agent"
      - "security-engineer"
```

**Deprecated format** (still supported):
```yaml
agent_loops:
  inner_loop:
    - "frontend-engineer"
    - "backend-engineer"
  outer_loop:
    - "sre-agent"
```

## Validation Examples

### Valid Configuration

```yaml
version: "1.0"
states:
  - "Specified"
  - "Planned"
workflows:
  specify:
    command: "/flow:specify"
    agents:
      - "product-requirements-manager"
    input_states:
      - "To Do"
    output_state: "Specified"
    optional: false
transitions:
  - from: "To Do"
    to: "Specified"
    via: "specify"
```

### Common Validation Errors

#### 1. Invalid version format
```yaml
version: "1.0.0"  # ❌ Three parts not allowed
version: "v1.0"   # ❌ Must be numeric
version: "1.0"    # ✅ Valid
```

#### 2. Invalid command pattern
```yaml
command: "flow:specify"     # ❌ Missing leading slash
command: "/specify"           # ❌ Missing flow: prefix
command: "/flow:Specify"    # ❌ Uppercase not allowed
command: "/flow:specify"    # ✅ Valid
```

#### 3. Empty required arrays
```yaml
agents: []          # ❌ At least one agent required
input_states: []    # ❌ At least one state required
states: []          # ❌ At least one state required
```

#### 4. Duplicate items
```yaml
agents: ["pm", "pm"]                    # ❌ Duplicates not allowed
input_states: ["To Do", "To Do"]        # ❌ Duplicates not allowed
states: ["Specified", "Specified"]      # ❌ Duplicates not allowed
```

#### 5. Invalid agent identity
```yaml
identity: "pm-planner"    # ❌ Missing @ prefix
identity: "@PM-Planner"   # ❌ Uppercase not allowed
identity: "@pm-planner"   # ✅ Valid
```

#### 6. Extra properties
```yaml
workflows:
  specify:
    command: "/flow:specify"
    agents: ["pm"]
    input_states: ["To Do"]
    output_state: "Specified"
    extra_field: "value"  # ❌ Additional properties not allowed
```

## Programmatic Validation

### Full Error Reporting

```python
from jsonschema import Draft7Validator
import json
import yaml

# Load schema and config
with open('memory/flowspec_workflow.schema.json') as f:
    schema = json.load(f)

with open('flowspec_workflow.yml') as f:
    config = yaml.safe_load(f)

# Get all validation errors
validator = Draft7Validator(schema)
errors = list(validator.iter_errors(config))

if not errors:
    print("✅ Configuration is valid")
else:
    print(f"❌ Found {len(errors)} validation errors:")
    for i, error in enumerate(errors, 1):
        path = " -> ".join(str(p) for p in error.absolute_path)
        print(f"{i}. {error.message}")
        if path:
            print(f"   At: {path}")
```

### Validation in CI/CD

```bash
#!/bin/bash
# validate-workflow.sh

# Install dependencies
pip install jsonschema pyyaml

# Validate
python3 << 'EOF'
import json
import yaml
from jsonschema import validate
import sys

try:
    with open('memory/flowspec_workflow.schema.json') as f:
        schema = json.load(f)
    with open('flowspec_workflow.yml') as f:
        workflow = yaml.safe_load(f)
    validate(instance=workflow, schema=schema)
    print("✅ Workflow configuration is valid")
    sys.exit(0)
except Exception as e:
    print(f"❌ Validation failed: {e}")
    sys.exit(1)
EOF
```

## Schema Versioning

The schema supports versioning through:

1. **Config version field**: `version: "1.0"` in the YAML
2. **Schema version**: `metadata.schema_version` field
3. **Schema $id**: `https://flowspec/schemas/flowspec_workflow.schema.json`

When updating the schema:
- Maintain backward compatibility when possible
- Document breaking changes
- Update test fixtures
- Increment schema version in metadata

## Testing

Run the comprehensive test suite:

```bash
# Run all schema validation tests
pytest tests/test_workflow_schema.py -v

# Run specific test class
pytest tests/test_workflow_schema.py::TestWorkflowsValidation -v

# Test schema against actual workflow
python3 -c "
import json, yaml
from jsonschema import validate

with open('memory/flowspec_workflow.schema.json') as f:
    schema = json.load(f)
with open('flowspec_workflow.yml') as f:
    workflow = yaml.safe_load(f)
validate(instance=workflow, schema=schema)
print('✅ flowspec_workflow.yml is valid')
"
```

## Related Documentation

- **Workflow Configuration Guide**: `docs/guides/flowspec-workflow-guide.md`
- **Artifact Path Patterns**: `docs/reference/artifact-path-patterns.md`
- **Agent Loop Classification**: `docs/reference/agent-loop-classification.md`
- **Schema Definition**: `memory/flowspec_workflow.schema.json`
- **Workflow YAML**: `flowspec_workflow.yml`

## References

- **JSON Schema Specification**: https://json-schema.org/draft-07/schema
- **Python jsonschema Library**: https://python-jsonschema.readthedocs.io/
- **YAML Specification**: https://yaml.org/spec/1.2/spec.html
