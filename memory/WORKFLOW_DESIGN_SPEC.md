# Flowspec Workflow Configuration - Design Specification

**Date**: 2025-11-28
**Branch**: workflow-config-design
**Status**: Design Complete - Ready for Implementation

## Executive Summary

This document specifies the design for a workflow configuration system that synchronizes `/flowspec` commands with backlog.md task states. The system allows users to customize their spec-driven development workflow without modifying code.

## Problem Statement

The Flowspec has two workflow systems that need synchronization:

1. **Agent Loop Workflow** (`/flowspec` commands)
   - 6 commands: specify, research, plan, implement, validate, operate
   - Each uses specific agents
   - Execute in sequence
   - Task-independent

2. **Task State Workflow** (backlog.md)
   - Task states: To Do, In Progress, Done
   - Backlog.md doesn't know about `/flowspec` workflow phases
   - No constraint enforcement between the two systems

**Current Gap**: Users can run `/flowspec` commands in any order, on tasks in any state. There's no synchronization between task state and workflow phase.

## Solution Overview

Create a **declarative workflow configuration** system that:
- Maps `/flowspec` commands to task states
- Specifies which agents participate in each phase
- Validates state transitions
- Allows user customization
- Provides validation and error checking

## Architecture

### Core Components

```
flowspec_workflow.yml          ← User-customizable configuration
    ↓
WorkflowConfig (Python)      ← Load and parse configuration
    ↓
WorkflowValidator (Python)   ← Validate configuration
    ↓
/flowspec commands             ← Enforce constraints
    ↓
backlog.md states            ← Reflect workflow phase
```

### File Structure

```
flowspec/
├── flowspec_workflow.yml                 ← Configuration (new)
├── memory/
│   ├── WORKFLOW_DESIGN_SPEC.md        ← This file
│   └── flowspec_workflow.schema.json    ← JSON schema for validation
├── src/specify_cli/
│   ├── workflow/                       ← New package
│   │   ├── __init__.py
│   │   ├── config.py                  ← WorkflowConfig class
│   │   └── validator.py               ← WorkflowValidator class
│   └── (existing CLI code)
├── docs/guides/
│   ├── workflow-architecture.md       ← Architecture overview
│   ├── workflow-state-mapping.md      ← State mapping guide
│   ├── workflow-customization.md      ← User customization guide
│   └── workflow-troubleshooting.md    ← Troubleshooting guide
├── docs/examples/
│   └── workflows/                     ← Configuration examples
└── tests/
    ├── test_workflow_config.py        ← Unit tests
    └── test_flowspec_workflow_integration.py ← Integration tests
```

## Configuration Structure

### flowspec_workflow.yml

```yaml
version: "1.0"
description: "Default Flowspec specification-driven development workflow"

# Custom backlog.md states (beyond default To Do/Done)
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

# Workflow phases mapped to /flowspec commands
workflows:
  specify:
    command: "/flow:specify"
    agents: ["product-requirements-manager"]
    input_states: ["To Do"]
    output_state: "Specified"
    description: "Create feature specification"
    optional: false

  research:
    command: "/flow:research"
    agents: ["researcher", "business-validator"]
    input_states: ["Specified"]
    output_state: "Researched"
    description: "Validate business viability"
    optional: false

  plan:
    command: "/flow:plan"
    agents: ["software-architect", "platform-engineer"]
    input_states: ["Researched"]
    output_state: "Planned"
    description: "Create technical plan"
    optional: false

  implement:
    command: "/flow:implement"
    agents: ["frontend-engineer", "backend-engineer", "code-reviewer"]
    input_states: ["Planned"]
    output_state: "In Implementation"
    description: "Implement feature"
    optional: false

  validate:
    command: "/flow:validate"
    agents: ["quality-guardian", "secure-by-design-engineer", "tech-writer", "release-manager"]
    input_states: ["In Implementation"]
    output_state: "Validated"
    description: "Validate implementation"
    optional: false

  operate:
    command: "/flow:operate"
    agents: ["sre-agent"]
    input_states: ["Validated"]
    output_state: "Deployed"
    description: "Deploy to production"
    optional: true

# State transitions (forms a DAG)
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

# Agent classification
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

### JSON Schema (flowspec_workflow.schema.json)

The schema validates:
- `version` is string "1.0"
- `states` is array with unique names
- `workflows` is object with valid workflow definitions
- `transitions` references valid states and workflows
- `agent_loops` contains valid agent names

## Python Implementation

### WorkflowConfig Class

**File**: `src/specify_cli/workflow/config.py`

**Responsibilities**:
- Load flowspec_workflow.yml from project root or memory/
- Parse YAML and structure as Python objects
- Validate against JSON schema
- Provide query API

**Public Methods**:
```python
class WorkflowConfig:
    def __init__(self, config_path: str = None)
    def get_agents(self, workflow: str) -> List[str]
    def get_next_state(self, current_state: str, workflow: str) -> str
    def get_input_states(self, workflow: str) -> List[str]
    def get_transitions(self) -> List[Transition]
    def is_valid_transition(self, from_state: str, to_state: str) -> bool
    def get_workflow_for_transition(self, from_state: str, to_state: str) -> str
    def validate() -> Tuple[bool, List[str]]
```

### WorkflowValidator Class

**File**: `src/specify_cli/workflow/validator.py`

**Responsibilities**:
- Validate config against JSON schema
- Check semantic rules:
  - No circular state transitions
  - All states reachable from "To Do"
  - All references are valid
  - Agent names exist

**Public Methods**:
```python
class WorkflowValidator:
    def validate_schema(config: dict) -> Tuple[bool, List[str]]
    def validate_semantics(config: dict) -> Tuple[bool, List[str]]
    def validate_transitions(config: dict) -> Tuple[bool, List[str]]
    def validate_all(config: dict) -> Tuple[bool, List[str]]
```

## Integration Points

### 1. /flowspec Command Execution

Each `/flowspec` command:
1. Loads WorkflowConfig
2. Checks current task state
3. Validates state is in `input_states`
4. Executes workflow with specified agents
5. Updates task state to `output_state`

**Pseudo-code**:
```python
def flowspec_specify(task_id, ...):
    config = WorkflowConfig()
    task = load_task(task_id)

    # Check state
    allowed_states = config.get_input_states("specify")
    if task.state not in allowed_states:
        raise WorkflowError(f"Cannot specify task in {task.state} state")

    # Execute
    agents = config.get_agents("specify")
    result = execute_agents(agents, task, ...)

    # Update state
    new_state = config.get_next_state(task.state, "specify")
    task.update_state(new_state)

    return result
```

### 2. Task State Creation in backlog.md

When user creates custom states in config, backlog.md is updated to include them:
- Read custom states from config
- Create backlog.md states if not present
- Validate backlog.md state transitions match config

### 3. CLI Validation Command

**Command**: `flowspec workflow validate [--file <path>] [--verbose]`

**Behavior**:
- Load configuration (from file or default)
- Run schema validation
- Run semantic validation
- Print results
- Exit with code 0 (success) or non-zero (failure)

## State Transition Model

### Valid Sequence (Happy Path)

```
To Do
  ↓ (specify)
Specified
  ↓ (research)
Researched
  ↓ (plan)
Planned
  ↓ (implement)
In Implementation
  ↓ (validate)
Validated
  ↓ (operate)
Deployed
  ↓ (completion)
Done
```

### Invalid Sequences (Error Cases)

1. **Wrong Order**: "To Do" → run implement (error: not in input_states)
2. **Wrong State**: "Planned" → run research (error: not in input_states)
3. **Circular**: Config creates cycle (error: validation detects)
4. **Unreachable**: State not reachable from "To Do" (error: validation detects)

### Error Messages

**Example 1** - Wrong State:
```
Error: Cannot execute '/flow:implement' on task in 'Specified' state
Reason: /flow:implement requires task to be in: ['Planned']
Suggestion: Run /flow:research and /flow:plan first
```

**Example 2** - Invalid Configuration:
```
Error: Invalid workflow configuration
File: flowspec_workflow.yml
Problem: State 'Security Reviewed' is unreachable from 'To Do'
Fix: Ensure all states are connected in transitions
```

## Customization Examples

### Example 1: Skip Research Phase

**Before**:
```yaml
workflows:
  specify: ...
  research: ...
  plan:
    input_states: ["Researched"]
```

**After** (remove research, update plan input):
```yaml
workflows:
  specify: ...
  # Remove research workflow
  plan:
    input_states: ["Specified"]  # Changed from ["Researched"]
```

### Example 2: Add Security Audit

**Add**:
```yaml
states:
  - name: "Security Audited"

workflows:
  security_audit:
    command: "/flow:audit"
    agents: ["secure-by-design-engineer"]
    input_states: ["Validated"]
    output_state: "Security Audited"
    optional: true

transitions:
  - from: "Validated"
    to: "Security Audited"
    via: "security_audit"
  - from: "Security Audited"
    to: "Deployed"
    via: "operate"
```

## Dependencies

### Python Packages (already in pyproject.toml)
- PyYAML: Load YAML configuration
- jsonschema: Validate against JSON schema

### New Package Structure
```
src/specify_cli/workflow/
├── __init__.py
├── config.py
└── validator.py
```

## Testing Strategy

### Unit Tests (test_workflow_config.py)
- Load valid configuration
- Load invalid YAML
- Missing fields
- Wrong types
- Query methods
- Config caching
- Validation

**Coverage**: >90%

### Integration Tests (test_flowspec_workflow_integration.py)
- State transitions work
- Invalid transitions are rejected
- Custom configurations work
- All 6 /flowspec commands enforce constraints

**Coverage**: >80%

### Validation Tests
- Schema validation detects errors
- Semantic validation detects issues
- CLI validation command works

## Success Criteria

1. **Functionality**:
   - All 6 /flowspec commands enforce state constraints ✓
   - State transitions are validated ✓
   - Users can customize workflows ✓
   - Configuration is validated at runtime ✓

2. **Usability**:
   - Clear error messages guide users ✓
   - Customization guide is comprehensive ✓
   - Examples show common scenarios ✓
   - Validation command helps debug ✓

3. **Quality**:
   - >80% test coverage ✓
   - No breaking changes ✓
   - Documentation is complete ✓
   - Code follows project style ✓

4. **Compatibility**:
   - Existing /flowspec commands still work ✓
   - Backlog.md integration smooth ✓
   - Configuration is version-controlled ✓
   - Can migrate from no-config to config ✓

## Future Enhancements (Out of Scope)

1. **Workflow Visualization**: Generate state diagrams from config
2. **Multi-Workflow Support**: Different workflows for different features
3. **Conditional Phases**: Skip phases based on feature properties
4. **Workflow Analytics**: Track phase duration and bottlenecks
5. **CI/CD Integration**: Trigger workflows on GitHub Actions
6. **Role-Based Access**: Enforce who can execute which phases

## Implementation Order

**Phase 1** (Foundation):
- Task 88: JSON Schema
- Task 89: Default flowspec_workflow.yml

**Phase 2** (Core):
- Task 90: WorkflowConfig class
- Task 91: WorkflowValidator class

**Phase 3** (Integration):
- Task 95: State mapping docs
- Task 96: Update /flowspec commands
- Task 99: Validation CLI

**Phase 4** (UX & Testing):
- Task 97: Customization guide
- Task 98: Examples
- Task 100: Unit tests
- Task 101: Integration tests

**Phase 5** (Documentation):
- Task 102: Update CLAUDE.md
- Task 103: Troubleshooting guide

**Phase 6** (Release):
- Task 104: Create PR

## Open Questions / Decisions Needed

1. **Config Location**: Root directory (flowspec_workflow.yml) or memory/?
   - **Decision**: Root directory for visibility and easy editing

2. **Default Behavior**: Strict (prevent all invalid transitions) or Permissive (warn only)?
   - **Decision**: Strict enforcement to prevent confusion

3. **Backlog.md Integration**: Create states automatically or manual step?
   - **Decision**: Document how to create states, don't auto-create (explicit is better)

4. **Configuration Version**: Always "1.0" or support multiple versions?
   - **Decision**: Version field for future compatibility

5. **Agent Validation**: Validate agent names against known agents?
   - **Decision**: Yes, use agent registry from CLI

## Appendices

### A. Terminology

- **Workflow**: A phase in the development process (specify, research, plan, etc.)
- **State**: A task's current position (To Do, Specified, Done, etc.)
- **Phase**: Synonym for workflow
- **Agent**: An AI agent that executes workflow tasks
- **Transition**: Movement from one state to another via a workflow
- **Configuration**: flowspec_workflow.yml file defining the workflow model

### B. Configuration Change Checklist

Before deploying configuration changes:
- [ ] Run `flowspec workflow validate`
- [ ] No circular transitions
- [ ] All states reachable
- [ ] All agents are valid
- [ ] Test state transitions manually
- [ ] Update team documentation
- [ ] Version control the change

### C. Troubleshooting Quick Links

- Configuration not found: docs/guides/workflow-troubleshooting.md#not-found
- Validation errors: docs/guides/workflow-troubleshooting.md#validation
- State transition errors: docs/guides/workflow-troubleshooting.md#transitions
- Custom workflows: docs/guides/workflow-customization.md

---

**End of Design Specification**

**Next Steps**: Create the 11 backlog tasks and implement in phases
