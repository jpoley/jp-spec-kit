# Flowspec Workflow Architecture

## Overview

The Flowspec workflow synchronizes the `/flowspec` command interface with the backlog.md task management system. This document defines the architecture, design decisions, and implementation approach.

## Problem Statement

Two distinct workflows need synchronization:

1. **Agent Loop Workflow** (`/flowspec` commands)
   - Defines which agents execute at each phase
   - Orchestrates inner/outer loop execution
   - Task-agnostic (works with any task system)

2. **Task State Workflow** (backlog.md)
   - Defines task states and transitions
   - Tracks progress through stages
   - Provides task management UI/CLI

**Challenge**: Keep these synchronized so that:
- `/flowspec` commands respect task states
- Task state changes trigger appropriate workflows
- Users can customize both independently
- The system remains maintainable and understandable

## Design Decisions

### 1. Configuration-Driven Approach

**Decision**: Use declarative YAML configuration to define the workflow mapping.

**Rationale**:
- Explicit and human-readable
- Version-controlled and reviewable
- User-customizable without code changes
- Easy to validate against schema
- Clear separation of concerns

**Alternative Considered**: Hardcode workflow in Python
- **Rejected**: Not user-customizable, harder to extend

### 2. Single Source of Truth

**Decision**: `flowspec_workflow.yml` in project root as the authoritative workflow definition.

**File Location**: `{project-root}/flowspec_workflow.yml`

**Rationale**:
- Central location for users to find and modify
- Version controlled with project
- Loaded at CLI runtime
- Can be validated by schema

### 3. State-Based Transitions

**Decision**: Task state determines which `/flowspec` commands are valid.

**State Model**:
```
To Do → Specified → Researched → Planned → In Implementation → Validated → Deployed → Done
         (specify)  (research)   (plan)   (implement)        (validate)  (operate)
```

**Rationale**:
- Clear progression through phases
- Prevents executing commands out of order
- Aligns with spec-driven development workflow
- States are visible in backlog.md UI

### 4. Agent Loop Classification

**Decision**: Map agents to inner/outer loop phases.

**Rationale**:
- Inner loop agents: PM, architect, engineers, QA, security (iterate on code/specs)
- Outer loop agents: SRE, release manager (operate production systems)
- Clear separation enables parallel work
- Aligns with documented agent classification

### 5. Extensibility Through Configuration

**Decision**: Users can customize workflow by editing `flowspec_workflow.yml`.

**Customizable Elements**:
- Add/remove phases
- Reorder phases
- Change which agents participate
- Modify state names
- Set optional vs mandatory phases

**Validation**: Schema ensures customizations are valid

### 6. Validation Layer

**Decision**: Separate validation logic from command execution.

**Components**:
- JSON Schema validates config syntax/structure
- WorkflowConfig class validates semantic rules
- CLI command validates state transitions at execution time

**Rationale**:
- Clear separation of concerns
- Can validate without executing
- Users get clear error messages

## Architecture Components

### 1. Configuration File (`flowspec_workflow.yml`)

Defines:
- Custom task states
- Workflow phases (maps to `/flowspec` commands)
- Agent assignments
- State transitions
- Optional vs mandatory phases
- Agent loop classification

**Schema**: `flowspec_workflow.schema.json`

### 2. Python Classes

#### WorkflowConfig
- Loads YAML configuration
- Parses and structures workflow data
- Provides query API: get_agents(), get_next_state(), etc.
- Validates against schema

#### WorkflowValidator
- Validates workflow configuration
- Checks state transitions
- Validates agent assignments
- Provides detailed error messages

### 3. Task State Management

Backlog.md integrations:
- Create custom states from `flowspec_workflow.yml`
- Enforce state transitions
- Validate state changes against workflow

### 4. CLI Enhancements

New command: `specify workflow validate`
- Validates workflow configuration
- Shows warnings for customizations
- Tests state transitions

## Implementation Phases

### Phase 1: Design & Schema (Foundation)
- Define workflow schema structure
- Create JSON schema for validation
- Document architecture decisions

### Phase 2: Configuration & Core
- Create default `flowspec_workflow.yml`
- Implement WorkflowConfig class
- Implement WorkflowValidator

### Phase 3: Integration
- Update `/flowspec` commands to use workflow config
- Document backlog.md state mappings
- Implement state transition validation

### Phase 4: User Experience
- Create customization guide
- Create configuration examples
- Add validation CLI command

### Phase 5: Testing & Quality
- Unit tests for config loading
- Integration tests for constraints
- Documentation tests

### Phase 6: Documentation
- Update CLAUDE.md
- Create troubleshooting guide
- Update README

## Workflow Configuration Structure

```yaml
version: "1.0"
description: "Default Flowspec specification-driven development workflow"

# Custom backlog.md states
states:
  - name: "Specified"
    description: "Feature specification created"

  - name: "Researched"
    description: "Business viability researched"

  # ... more states

# Workflow phases (maps to /flowspec commands)
workflows:
  specify:
    command: "/flow:specify"
    agents: ["product-requirements-manager"]
    input_states: ["To Do"]
    output_state: "Specified"
    description: "Create feature specification from requirements"

  research:
    command: "/flow:research"
    agents: ["researcher", "business-validator"]
    input_states: ["Specified"]
    output_state: "Researched"

  # ... more workflows

# Valid state transitions
transitions:
  - from: "To Do"
    to: "Specified"
    via: "specify"

  # ... more transitions

# Agent classification
agent_loops:
  inner_loop: [...]
  outer_loop: [...]
```

## State Transition Validation

**Valid Sequence**:
1. Task created in "To Do" state
2. User runs `/flow:specify` → task moves to "Specified"
3. User runs `/flow:research` → task moves to "Researched"
4. User runs `/flow:plan` → task moves to "Planned"
5. User runs `/flow:implement` → task moves to "In Implementation"
6. User runs `/flow:validate` → task moves to "Validated"
7. User runs `/flow:operate` → task moves to "Deployed"
8. User marks task as "Done" in backlog.md

**Invalid Sequence Examples**:
- Running `/flow:implement` on a "To Do" task → Error
- Running `/flow:research` on a "Planned" task → Error
- Manually changing state without workflow → Warning/error

## User Customization Examples

### Example 1: Skipping the Research Phase

Remove research workflow:
```yaml
workflows:
  # specify stays same

  # Remove research

  plan:
    input_states: ["Specified"]  # Changed from ["Researched"]
    # rest same
```

### Example 2: Adding Custom Phase

Add security audit before deployment:
```yaml
states:
  # ... existing states
  - name: "Security Audited"
    description: "Security audit completed"

workflows:
  # ... existing workflows
  security-audit:
    command: "/flow:audit"  # Hypothetical new command
    agents: ["secure-by-design-engineer"]
    input_states: ["Validated"]
    output_state: "Security Audited"

transitions:
  # Update Validated → Deployed transition
  - from: "Security Audited"
    to: "Deployed"
    via: "operate"
```

## Error Handling

**Schema Validation Errors**:
- Invalid YAML syntax
- Missing required fields
- Wrong field types

**Semantic Validation Errors**:
- Circular state transitions
- Unreachable states
- Missing workflow definitions
- Invalid agent names

**Runtime Errors**:
- State transition not allowed
- Task not in correct state for workflow
- Agent not available

All errors include helpful messages to guide user fixes.

## Testing Strategy

### Unit Tests
- WorkflowConfig loading and parsing
- State transition logic
- Agent assignment logic
- Validation error messages

### Integration Tests
- `/flowspec` commands enforce state constraints
- Backlog.md state changes work correctly
- Custom workflows work as expected
- Configuration changes apply immediately

### Validation Tests
- Schema validation works
- Semantic validation catches errors
- Custom configurations validate
- Migration from existing workflows works

## Backward Compatibility

**Initial Release**:
- Default workflow matches current `/flowspec` implementation
- Existing tasks work without modification
- No breaking changes to `/flowspec` commands

**Future Extensions**:
- Add new workflow phases
- Add new agents
- Change state names (with migration guide)

## Extensibility

Users can extend the workflow by:
1. Editing `flowspec_workflow.yml`
2. Adding custom states
3. Reordering phases
4. Changing agent assignments
5. Creating optional phases
6. Adding parallel workflows

All validated against schema and semantic rules.

## Success Criteria

1. **Clarity**: Users understand workflow definition in YAML
2. **Customizability**: Users can modify workflow without code changes
3. **Validation**: System prevents invalid state transitions
4. **Synchronization**: Backlog.md states match `/flowspec` phases
5. **Documentation**: Clear guides for customization
6. **Testing**: >80% test coverage for workflow logic
7. **Performance**: No noticeable latency from config loading

## Future Enhancements

1. **Workflow Visualization**: Generate diagrams from config
2. **Multi-Workflow Support**: Different workflows for different features
3. **Conditional Phases**: Skip phases based on feature properties
4. **Workflow Analytics**: Track phase duration and bottlenecks
5. **Integration with CI/CD**: Trigger workflows on GitHub Actions
6. **Role-Based Access**: Enforce who can execute which phases

## References

- Agent Loop Classification: `docs/reference/agent-loop-classification.md`
- Backlog.md User Guide: `docs/guides/backlog-user-guide.md`
- Inner Loop Principles: `docs/reference/inner-loop.md`
- Outer Loop Principles: `docs/reference/outer-loop.md`
