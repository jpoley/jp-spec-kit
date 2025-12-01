# Workflow State Mapping Guide

This guide explains how backlog.md task states map to `/jpspec` workflow commands in the JP Spec Kit Spec-Driven Development (SDD) workflow.

## Overview

JP Spec Kit uses a state machine to coordinate task progression through the SDD lifecycle. Each task state corresponds to a workflow phase, and each phase is executed by running a `/jpspec` command.

**Key Concept**: Task states represent **where you are** in the development lifecycle, while `/jpspec` commands represent **how to move forward**.

## State Mapping Table

| Task State | Created By | Next Command | Agents Involved |
|-----------|-----------|--------------|-----------------|
| **To Do** | Manual (task creation) | `/jpspec:assess` | workflow-assessor |
| **Assessed** | `/jpspec:assess` | `/jpspec:specify` | product-requirements-manager |
| **Specified** | `/jpspec:specify` | `/jpspec:research` or `/jpspec:plan` | researcher, business-validator (research) OR software-architect, platform-engineer (plan) |
| **Researched** | `/jpspec:research` | `/jpspec:plan` | software-architect, platform-engineer |
| **Planned** | `/jpspec:plan` | `/jpspec:implement` | frontend-engineer, backend-engineer, ai-ml-engineer, code-reviewers |
| **In Implementation** | `/jpspec:implement` | `/jpspec:validate` | quality-guardian, secure-by-design-engineer, tech-writer, release-manager |
| **Validated** | `/jpspec:validate` | `/jpspec:operate` or manual → Done | sre-agent (operate) |
| **Deployed** | `/jpspec:operate` | Manual → Done | — |
| **Done** | Manual | — | — |

## State Lifecycle Diagrams

### Primary Forward Path (Full SDD Workflow)

```
To Do
  ↓ /jpspec:assess
Assessed
  ↓ /jpspec:specify
Specified
  ↓ /jpspec:research
Researched
  ↓ /jpspec:plan
Planned
  ↓ /jpspec:implement
In Implementation
  ↓ /jpspec:validate
Validated
  ↓ /jpspec:operate
Deployed
  ↓ manual
Done
```

### Optional Research Path (Spec-Light Mode)

For simpler features that don't require research:

```
To Do
  ↓ /jpspec:assess
Assessed
  ↓ /jpspec:specify
Specified
  ↓ /jpspec:plan (skipping research)
Planned
  ↓ /jpspec:implement
In Implementation
  ↓ /jpspec:validate
Validated
  ↓ /jpspec:operate
Deployed
  ↓ manual
Done
```

### Early Exit Paths

You can manually move to "Done" from several states:

```
Validated → Done (validation complete, deployment deferred)
In Implementation → Done (implementation complete, validation deferred)
Deployed → Done (production deployment confirmed)
```

### Rework/Rollback Paths

When issues are found, you can move backward:

```
In Implementation → Planned (rework needed based on implementation findings)
Validated → In Implementation (rework needed based on validation findings)
Deployed → Validated (rollback from production)
```

## How States Are Created

### From jpspec_workflow.yml

States are defined in the `jpspec_workflow.yml` configuration file at the project root:

```yaml
states:
  - "To Do"
  - "Assessed"
  - "Specified"
  - "Researched"
  - "Planned"
  - "In Implementation"
  - "Validated"
  - "Deployed"
  - "Done"
```

These states are automatically available in `backlog.md` for task management.

### Built-in States

Two states are always present and cannot be removed:

- **To Do**: Initial state for all new tasks
- **Done**: Terminal state indicating work is complete

### Custom States

You can add custom states by editing `jpspec_workflow.yml`:

```yaml
states:
  - "To Do"
  - "Assessed"
  - "Specified"
  - "Security Audited"  # Custom state
  - "Researched"
  # ... rest of states
```

**Important**: When adding custom states, you must also define:
1. A workflow that outputs to this state
2. Transitions that connect it to the state graph

See [Workflow Customization Guide](./workflow-customization.md) for details.

## State Transition Rules

### Forward Transitions (Automatic)

When you run a `/jpspec` command, the task state automatically transitions to the workflow's output state:

```bash
# Task is in "Planned" state
/jpspec:implement

# After completion, task is now in "In Implementation" state
```

### Valid Input States

Each `/jpspec` command can only run from specific states. These are defined in `jpspec_workflow.yml`:

```yaml
workflows:
  implement:
    input_states: ["Planned"]
    output_state: "In Implementation"
```

If you try to run a command from an invalid state, you'll get an error:

```bash
# Task is in "To Do" state
/jpspec:implement

# Error: Cannot execute 'implement' from state 'To Do'.
# Valid input states: ['Planned']
```

### Manual Transitions

Some transitions must be done manually using the backlog CLI:

```bash
# Mark task as Done
backlog task edit task-123 -s Done

# Rework: move back to Planned
backlog task edit task-123 -s Planned
```

### Enforcement

The workflow configuration validates transitions to prevent invalid state changes:

```yaml
transitions:
  - name: "implement"
    from: "Planned"
    to: "In Implementation"
    via: "implement"
```

If a transition is not defined in `jpspec_workflow.yml`, it will be rejected.

## Examples

### Example 1: Standard Feature Development

```bash
# 1. Create task (state: To Do)
backlog task create "Add user authentication"

# 2. Assess workflow suitability
/jpspec:assess
# → State: Assessed

# 3. Create specification
/jpspec:specify
# → State: Specified

# 4. Plan architecture (skipping research)
/jpspec:plan
# → State: Planned

# 5. Implement feature
/jpspec:implement
# → State: In Implementation

# 6. Validate quality, security, docs
/jpspec:validate
# → State: Validated

# 7. Deploy to production
/jpspec:operate
# → State: Deployed

# 8. Confirm deployment success
backlog task edit task-123 -s Done
# → State: Done
```

### Example 2: Research-Heavy Feature

```bash
# 1-3: Same as above (To Do → Assessed → Specified)

# 4. Conduct research
/jpspec:research
# → State: Researched

# 5. Plan architecture
/jpspec:plan
# → State: Planned

# 6-8: Same as above (Planned → ... → Done)
```

### Example 3: Validation Issues Found

```bash
# Task is in "Validated" state
# Validation found issues that need fixing

# Move back to Implementation
backlog task edit task-123 -s "In Implementation" \
  --notes "Fixing security issues found in validation"

# Re-implement fixes
/jpspec:implement

# Re-validate
/jpspec:validate
# → State: Validated
```

## State Validation

### Check Current State

```bash
# View task details
backlog task view task-123

# See current state in task metadata
```

### Validate Workflow Configuration

Check that your state transitions are valid:

```bash
specify workflow validate

# Output:
# ✓ Configuration valid
# ✓ No cycles detected
# ✓ All states reachable from "To Do"
# ✓ Terminal states configured
```

### Valid Workflows for Current State

To see which `/jpspec` commands can run from the current state:

```python
# This information is available in the workflow config
from specify_cli.workflow.config import WorkflowConfig

config = WorkflowConfig.load()
workflows = config.get_valid_workflows("Planned")
# Returns: ['implement']
```

## Troubleshooting

### Error: "Cannot execute 'X' from state 'Y'"

**Cause**: You're trying to run a workflow from an invalid state.

**Solution**:
1. Check the current task state: `backlog task view task-123`
2. Check valid input states for the workflow in `jpspec_workflow.yml`
3. Run the correct workflow sequence, or manually change state if appropriate

### Error: "State 'X' not found in configuration"

**Cause**: A state is referenced that doesn't exist in `jpspec_workflow.yml`.

**Solution**:
1. Check for typos in state name
2. Verify state is defined in `jpspec_workflow.yml`
3. Run `specify workflow validate` to check configuration

### Warning: "State 'X' is not reachable"

**Cause**: A custom state has no transition path from "To Do".

**Solution**:
1. Add transitions to connect the state to the workflow graph
2. See [Workflow Customization Guide](./workflow-customization.md#adding-custom-states)

### States Don't Match jpspec_workflow.yml

**Cause**: The workflow configuration may have been modified but not reloaded.

**Solution**:
1. Restart Claude Code or reload the configuration
2. Verify changes were saved to `jpspec_workflow.yml`
3. Run `specify workflow validate` to check for errors

## Advanced Topics

### Multiple Input States

Some workflows can accept multiple input states:

```yaml
workflows:
  plan:
    input_states: ["Specified", "Researched"]
    output_state: "Planned"
```

This allows skipping optional phases (like research) while maintaining workflow integrity.

### Optional vs Required Workflows

Workflows can be marked as optional:

```yaml
workflows:
  research:
    optional: true
```

Optional workflows can be skipped, but their state transitions must still be defined.

### Agent Loop Classification

States map to either "inner loop" (fast iteration) or "outer loop" (governance):

```yaml
agent_loops:
  inner:
    agents:
      - "frontend-engineer"
      - "backend-engineer"
      # ... fast iteration agents

  outer:
    agents:
      - "workflow-assessor"
      - "quality-guardian"
      # ... governance agents
```

See [Agent Loop Classification](../reference/agent-loop-classification.md) for details.

## Related Documentation

- [Workflow Architecture](./workflow-architecture.md) - Overall workflow design
- [Workflow Customization Guide](./workflow-customization.md) - How to modify workflows
- [Workflow Troubleshooting](./workflow-troubleshooting.md) - Common issues and fixes
- [Backlog User Guide](./backlog-user-guide.md) - Task management with backlog.md
- [Agent Loop Classification](../reference/agent-loop-classification.md) - Inner vs outer loop

## Summary

- Task states represent progression through the SDD lifecycle
- `/jpspec` commands transition tasks between states
- States are defined in `jpspec_workflow.yml`
- Transitions are validated to prevent invalid state changes
- Built-in states ("To Do", "Done") are always present
- Custom states can be added with proper workflow definitions
- Some workflows are optional, some have multiple input states
- Manual transitions are needed for completion and rework scenarios
