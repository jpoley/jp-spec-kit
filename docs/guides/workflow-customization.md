# Workflow Customization Guide

This guide explains how to customize the Flowspec workflow by modifying `flowspec_workflow.yml`.

## Overview

The `flowspec_workflow.yml` file is the single source of truth for your development workflow. It defines:

- **States**: Task progression stages (e.g., Specified, Planned, Validated)
- **Workflows**: `/flowspec` commands with agent assignments
- **Transitions**: Valid state changes between states
- **Agent Loops**: Inner/outer loop classification for agents

**Location**: `{project-root}/flowspec_workflow.yml`

By editing this file, you can customize your workflow without modifying any code.

## Configuration File Structure

```yaml
version: "1.1"

# Task states (required)
states:
  - "To Do"
  - "Specified"
  - "Planned"
  # ... more states

# Workflow definitions (required)
workflows:
  specify:
    command: "/flow:specify"
    description: "Create feature specifications"
    agents:
      - name: "product-requirements-manager"
        identity: "@pm-planner"
        description: "Senior Product Strategy Advisor"
        responsibilities:
          - "Create comprehensive PRDs"
          - "Define user stories"
    input_states: ["To Do"]
    output_state: "Specified"
    optional: false
  # ... more workflows

# State transitions (required)
transitions:
  - name: "specify"
    from: "To Do"
    to: "Specified"
    via: "specify"
    description: "Requirements captured"
    output_artifacts:
      - type: "prd"
        path: "./docs/prd/{feature}.md"
    validation: "NONE"
  # ... more transitions

# Agent loop classification (optional)
agent_loops:
  inner:
    description: "Fast execution"
    agents:
      - "frontend-engineer"
      - "backend-engineer"
  outer:
    description: "Governance-focused"
    agents:
      - "quality-guardian"
      - "sre-agent"

# Metadata (optional)
metadata:
  schema_version: "1.1"
  last_updated: "2025-12-01"
```

## Common Customizations

### 1. Adding a Custom Phase

**Use Case**: Add a security audit phase between validation and deployment.

**Step-by-Step**:

1. **Add the state**:
   ```yaml
   states:
     - "To Do"
     - "Specified"
     # ... existing states
     - "Validated"
     - "Security Audited"  # New state
     - "Deployed"
     - "Done"
   ```

2. **Define the workflow**:
   ```yaml
   workflows:
     # ... existing workflows

     security-audit:
       command: "/flow:security-audit"
       description: "Comprehensive security audit before deployment"
       agents:
         - name: "secure-by-design-engineer"
           identity: "@security-engineer"
           description: "Senior Security Engineer"
           responsibilities:
             - "Penetration testing"
             - "Compliance verification"
             - "Threat modeling validation"
       input_states: ["Validated"]
       output_state: "Security Audited"
       optional: false
   ```

3. **Add transitions**:
   ```yaml
   transitions:
     # ... existing transitions

     - name: "security_audit"
       from: "Validated"
       to: "Security Audited"
       via: "security-audit"
       description: "Security audit completed"
       output_artifacts:
         - type: "security_audit_report"
           path: "./docs/security/{feature}-audit.md"
       validation: "NONE"

     # Update the deployment transition
     - name: "operate"
       from: "Security Audited"  # Changed from "Validated"
       to: "Deployed"
       via: "operate"
       # ... rest unchanged
   ```

4. **Validate the configuration**:
   ```bash
   specify workflow validate
   ```

### 2. Removing a Phase

**Use Case**: Skip the research phase for all projects.

**Step-by-Step**:

1. **Remove the state**:
   ```yaml
   states:
     - "To Do"
     - "Specified"
     # Remove "Researched"
     - "Planned"
     # ... rest
   ```

2. **Remove the workflow**:
   ```yaml
   workflows:
     specify:
       # ... unchanged

     # Remove research workflow entirely

     plan:
       input_states: ["Specified"]  # Changed from ["Specified", "Researched"]
       # ... rest unchanged
   ```

3. **Update transitions**:
   ```yaml
   transitions:
     # Remove research transition

     # Keep only plan_from_specified, remove plan_from_researched
     - name: "plan_from_specified"
       from: "Specified"
       to: "Planned"
       via: "plan"
       # ... rest
   ```

4. **Validate**:
   ```bash
   specify workflow validate
   ```

### 3. Reordering Phases

**Use Case**: Run validation before implementation (TDD-style).

**Step-by-Step**:

1. **Reorder states** (optional, for clarity):
   ```yaml
   states:
     - "To Do"
     - "Specified"
     - "Planned"
     - "Test Designed"    # New state (validation planning)
     - "In Implementation"
     - "Validated"
     - "Deployed"
     - "Done"
   ```

2. **Modify workflow input/output states**:
   ```yaml
   workflows:
     validate:
       input_states: ["Planned"]  # Changed from ["In Implementation"]
       output_state: "Test Designed"  # Changed from "Validated"

     implement:
       input_states: ["Test Designed"]  # Changed from ["Planned"]
       # ... rest unchanged
   ```

3. **Update transitions accordingly**

4. **Validate**:
   ```bash
   specify workflow validate
   ```

### 4. Adding Custom Agents

**Use Case**: Add organization-specific agents (e.g., compliance officer).

**Step-by-Step**:

1. **Add agent to workflow**:
   ```yaml
   workflows:
     validate:
       agents:
         - name: "quality-guardian"
           # ... existing agent

         - name: "compliance-officer"  # New custom agent
           identity: "@compliance-officer"
           description: "SOC2 Compliance Officer"
           responsibilities:
             - "SOC2 compliance verification"
             - "GDPR compliance checks"
             - "Audit trail validation"
       # ... rest unchanged
   ```

2. **Add to agent loop classification** (optional):
   ```yaml
   agent_loops:
     outer:
       agents:
         # ... existing agents
         - "compliance-officer"
   ```

3. **Create agent definition file** (if using custom templates):
   Create `.agents/compliance-officer.md` with agent instructions

4. **Test the workflow**:
   ```bash
   /flow:validate
   # Should now include compliance-officer agent
   ```

### 5. Creating Optional Phases

**Use Case**: Make research phase optional (can be skipped).

```yaml
workflows:
  research:
    # ... existing config
    optional: true  # Add this flag

# Ensure plan workflow accepts both Specified and Researched
workflows:
  plan:
    input_states: ["Specified", "Researched"]
    # ... rest
```

## Advanced Customizations

### Parallel Execution

For workflows where agents can work in parallel:

```yaml
workflows:
  plan:
    command: "/flow:plan"
    execution_mode: "parallel"  # Agents execute concurrently
    agents:
      - name: "software-architect"
        # ...
      - name: "platform-engineer"
        # ...
```

### Artifact Validation Gates

Control when tasks can transition based on artifact existence:

```yaml
transitions:
  - name: "implement"
    from: "Planned"
    to: "In Implementation"
    via: "implement"
    input_artifacts:
      - type: "adr"
        path: "./docs/adr/ADR-*.md"
        required: true  # Blocks transition if missing
    output_artifacts:
      - type: "source_code"
        path: "./src/"
      - type: "tests"
        path: "./tests/"
        required: true
    validation: "NONE"
```

### Human Approval Workflows

Require manual approval before proceeding:

```yaml
workflows:
  validate:
    # ... existing config
    requires_human_approval: true  # Blocks automatic transition

transitions:
  - name: "validate"
    from: "In Implementation"
    to: "Validated"
    via: "validate"
    validation: "KEYWORD[APPROVED]"  # User must type "APPROVED" to proceed
```

### Backlog Task Integration

Control which workflows create or require backlog tasks:

```yaml
workflows:
  specify:
    # ... existing config
    creates_backlog_tasks: true  # This workflow creates tasks

  implement:
    # ... existing config
    requires_backlog_tasks: true  # This workflow needs tasks to exist
```

## Validation and Testing

### Validate Configuration

Always validate after making changes:

```bash
specify workflow validate

# Example output:
# ✓ Configuration structure valid (schema v1.1)
# ✓ No cycles detected in state transitions
# ✓ All states reachable from "To Do"
# ✓ Terminal states configured
# ⚠ Warning: Unknown agent 'custom-agent' in workflow 'validate'
```

### Common Validation Errors

#### 1. Unreachable States

**Error**:
```
[ERROR] UNREACHABLE_STATE: State 'Security Audited' is not reachable from initial state 'To Do'.
```

**Fix**: Add a transition path from an existing state to the new state.

#### 2. Circular Dependencies

**Error**:
```
[ERROR] CYCLE_DETECTED: Cycle detected in state transitions: Planned -> In Implementation -> Planned.
```

**Fix**: Remove or modify transitions to break the cycle. Workflows must be a DAG (directed acyclic graph).

#### 3. Undefined State References

**Error**:
```
[ERROR] UNDEFINED_OUTPUT_STATE: Workflow 'implement' references undefined output state 'Implemented'.
```

**Fix**: Add the state to the `states` list, or fix the typo in the workflow definition.

#### 4. Missing Workflow References

**Error**:
```
[ERROR] UNDEFINED_WORKFLOW_REFERENCE: Transition references undefined workflow 'deploy'.
```

**Fix**: Add the workflow definition, or update the transition to reference an existing workflow.

#### 5. Invalid Input State

**Error**:
```
[ERROR] UNDEFINED_INPUT_STATE: Workflow 'implement' references undefined input state 'Ready'.
```

**Fix**: Add 'Ready' to the states list, or change the input_states to reference existing states.

### Test Your Customizations

1. **Create a test task**:
   ```bash
   backlog task create "Test custom workflow"
   ```

2. **Run through the workflow**:
   ```bash
   /flow:assess
   /flow:specify
   # ... continue through your custom phases
   ```

3. **Check state transitions**:
   ```bash
   backlog task view task-123
   # Verify state matches expected output
   ```

## Configuration Examples

For complete working examples, see:

- [Minimal Workflow](../examples/workflows/minimal-workflow.yml) - Only specify + implement
- [Security Audit Workflow](../examples/workflows/security-audit-workflow.yml) - With security audit phase
- [Parallel Workflows](../examples/workflows/parallel-workflows.yml) - Multiple feature tracks
- [Custom Agents Workflow](../examples/workflows/custom-agents-workflow.yml) - Organization-specific agents

## Best Practices

### 1. Always Validate

Run `specify workflow validate` after every change:

```bash
vim flowspec_workflow.yml
# ... make changes ...
specify workflow validate
```

### 2. Version Control

Commit workflow changes with clear commit messages:

```bash
git add flowspec_workflow.yml
git commit -s -m "feat(workflow): add security audit phase

- Add Security Audited state
- Add security-audit workflow
- Update transitions for new phase"
```

### 3. Document Custom Workflows

Add comments to explain custom phases:

```yaml
workflows:
  security-audit:
    # Custom phase required for SOC2 compliance
    # Must complete before production deployment
    command: "/flow:security-audit"
    # ...
```

### 4. Keep It Simple

Start with the default workflow and customize gradually:

1. Use default workflow for first project
2. Identify pain points or missing steps
3. Add one customization at a time
4. Test thoroughly before adding more

### 5. Test with Small Tasks

Test workflow customizations on small, low-risk tasks before using on critical features.

### 6. Maintain State Reachability

Every custom state must be reachable from "To Do":

```
To Do → ... → Custom State → ... → Done
```

Use `specify workflow validate` to verify reachability.

### 7. Use Descriptive Names

Choose clear, unambiguous names:

- ✓ "Security Audited" (clear)
- ✗ "Stage 3" (unclear)

- ✓ "In Implementation" (clear)
- ✗ "WIP" (ambiguous)

## Warnings and Limitations

### Unknown Agents

Custom agents will generate warnings but won't block execution:

```
[WARNING] UNKNOWN_AGENT: Workflow 'validate' references unknown agent 'compliance-officer'.
```

This is by design - you can use custom agents without modifying Flowspec code.

### Breaking Changes

Removing states or workflows can break existing tasks:

**Before removing a state**:
1. Check if any tasks are in that state: `backlog task list --status "Old State"`
2. Move those tasks to a different state
3. Then remove the state from configuration

### Schema Compatibility

Check the `version` field in `flowspec_workflow.yml`:

```yaml
version: "1.1"  # Must match Flowspec's expected schema version
```

Incompatible versions will cause validation errors.

### Performance Considerations

Very complex workflows (50+ states, 100+ transitions) may impact performance. Keep workflows focused and simple when possible.

## Troubleshooting

When customizations cause issues, this section helps diagnose and resolve problems quickly.

> **📖 For comprehensive troubleshooting coverage**, see [Workflow Troubleshooting Guide](./workflow-troubleshooting.md).

### ⚠️ Critical Issues to Avoid

These are the most common problems when customizing workflows. **Avoiding these saves significant debugging time.**

#### Circular Dependencies (Most Common Error)

**What it is**: A cycle in state transitions where states reference each other in a loop.

**Example of the problem**:
```yaml
transitions:
  - from: "Planned"
    to: "In Implementation"
  - from: "In Implementation"
    to: "Planned"  # ❌ Creates cycle!
```

**Why it's critical**: Workflows must be a Directed Acyclic Graph (DAG). Cycles violate this constraint and prevent the workflow from being valid.

**How to avoid**:
- Draw your state diagram before implementing
- Use `via: "rework"` for legitimate backward transitions (e.g., returning to planning after failed validation)
- Run `specify workflow validate` after every change

**Fix**: Remove or modify the transition creating the cycle:
```yaml
transitions:
  - from: "In Implementation"
    to: "Planned"
    via: "rework"  # ✓ Explicit rework transition is allowed
```

#### Unreachable States (Second Most Common)

**What it is**: A state that has no transition path from the initial "To Do" state.

**Example of the problem**:
```yaml
states:
  - "To Do"
  - "Specified"
  - "Security Audited"  # ❌ No way to reach this state!
  - "Done"

transitions:
  - from: "To Do"
    to: "Specified"
  - from: "Specified"
    to: "Done"
  # Missing transition to "Security Audited"
```

**Why it's critical**: Tasks can never enter unreachable states, making them useless configuration bloat.

**How to avoid**:
- Every state (except "To Do") must have at least one incoming transition
- Every state (except terminal states) must have at least one outgoing transition
- Use `specify workflow validate` to detect unreachable states

**Fix**: Add a transition path to the state:
```yaml
transitions:
  - from: "Specified"
    to: "Security Audited"
    via: "security-audit"
  - from: "Security Audited"
    to: "Done"
    via: "complete"
```

### Quick Reference: Common Issues

| Issue | Symptom | Quick Fix |
|-------|---------|-----------|
| Config not found | `WorkflowConfigNotFoundError` | Create `flowspec_workflow.yml` in project root |
| State typo | `UNDEFINED_OUTPUT_STATE` | Check spelling matches `states:` list exactly |
| Wrong workflow order | "Cannot execute from state X" | Check `input_states` for the workflow |
| Circular dependency | `CYCLE_DETECTED` | Use `via: "rework"` for backward transitions |
| Unreachable state | `UNREACHABLE_STATE` | Add transition path from existing state |
| Unknown agent | `UNKNOWN_AGENT` warning | Safe to ignore, or define custom agent |

### Diagnostic Commands

Run these when troubleshooting:

```bash
# 1. Validate configuration (catches most issues)
specify workflow validate

# 2. Check YAML syntax
python -c "import yaml; yaml.safe_load(open('flowspec_workflow.yml'))"

# 3. View current task state
backlog task view task-123

# 4. See valid workflows for a state
grep -A 5 "input_states" flowspec_workflow.yml
```

## Rollback and Recovery

### Undo Configuration Changes

If customizations cause issues:

1. **Restore from git**:
   ```bash
   git checkout flowspec_workflow.yml
   ```

2. **Reload configuration**:
   ```bash
   # Restart Claude Code, or use:
   specify workflow validate --reload
   ```

### Backup Before Editing

```bash
cp flowspec_workflow.yml flowspec_workflow.yml.backup.$(date +%Y%m%d)
vim flowspec_workflow.yml
```

### Emergency Defaults

If all else fails, restore the default configuration:

```bash
# Copy from template (Flowspec installation)
cp ~/.local/share/specify-cli/templates/flowspec_workflow.yml ./flowspec_workflow.yml
```

## Related Documentation

- [Workflow State Mapping](./workflow-state-mapping.md) - State and command mapping
- [Workflow Architecture](./workflow-architecture.md) - Overall design
- [Configuration Examples](../examples/workflows/) - Working example configs
- [Workflow Troubleshooting](./workflow-troubleshooting.md) - Common issues
- [Agent Loop Classification](../reference/agent-loop-classification.md) - Inner vs outer loop

## Summary

- `flowspec_workflow.yml` is the single source of truth for workflow configuration
- Customize by adding/removing/reordering states, workflows, and transitions
- Always validate after changes: `specify workflow validate`
- Test customizations on small tasks first
- Keep workflows simple and maintainable
- Document custom phases with comments
- Use version control for workflow changes
- Maintain state reachability from "To Do" to "Done"
