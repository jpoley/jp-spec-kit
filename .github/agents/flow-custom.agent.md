---
name: "flow-custom"
description: "Execute a user-defined custom workflow sequence from flowspec_workflow.yml"
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
---
## User Input

```text
$ARGUMENTS
```

You **MUST** parse the workflow name from the arguments. If no workflow name provided, list available custom workflows.

## Execution Instructions

This command executes user-customizable workflow sequences defined in `flowspec_workflow.yml`.

# Constitution Pre-flight Check

**CRITICAL**: This command requires constitution validation before execution (unless `--skip-validation` is provided).

## Step 0.5: Check Constitution Status

Before executing this workflow command, validate the project's constitution:

### 1. Check Constitution Exists

```bash
# Look for constitution file
if [ -f "memory/constitution.md" ]; then
  echo "[Y] Constitution found"
else
  echo "⚠️ No constitution found"
  echo ""
  echo "To create one:"
  echo "  1. Run: flowspec init --here"
  echo "  2. Then: Run /spec:constitution to customize"
  echo ""
  echo "Proceeding without constitution..."
fi
```

If no constitution exists:
- Warn the user
- Suggest creating one with `flowspec init --here`
- Continue with command (constitution is recommended but not required)

### 2. If Constitution Exists, Check Validation Status

```bash
# Detect tier from TIER comment (default: Medium if not found)
TIER=$(grep -o "TIER: \(Light\|Medium\|Heavy\)" memory/constitution.md | cut -d' ' -f2)
TIER=${TIER:-Medium}  # Default to Medium if not found

# Count NEEDS_VALIDATION markers
MARKER_COUNT=$(grep -c "NEEDS_VALIDATION" memory/constitution.md || echo 0)

# Extract section names from NEEDS_VALIDATION markers
SECTIONS=$(grep "NEEDS_VALIDATION" memory/constitution.md | sed 's/.*NEEDS_VALIDATION: /  - /')

echo "Constitution tier: $TIER"
echo "Unvalidated sections: $MARKER_COUNT"
```

### 3. Apply Tier-Based Enforcement

#### Light Tier - Warn Only

If `TIER = Light` and `MARKER_COUNT > 0`:

```text
⚠️ Constitution has N unvalidated sections:
$SECTIONS

Consider running /spec:constitution to customize your constitution.

Proceeding with command...
```

Then continue with the command.

#### Medium Tier - Warn and Confirm

If `TIER = Medium` and `MARKER_COUNT > 0`:

```text
⚠️ Constitution Validation Recommended

Your constitution has N unvalidated sections:
$SECTIONS

Medium tier projects should validate their constitution before workflow commands.

Options:
  1. Continue anyway (y/N)
  2. Run /spec:constitution to customize
  3. Run flowspec constitution validate to check status

Continue without validation? [y/N]: _
```

Wait for user response:
- If user responds `y` or `yes` -> Continue with command
- If user responds `n`, `no`, or empty/Enter -> Stop and show:
  ```text
  Command cancelled. Run /spec:constitution to customize your constitution.
  ```

#### Heavy Tier - Block Until Validated

If `TIER = Heavy` and `MARKER_COUNT > 0`:

```text
[X] Constitution Validation Required

Your constitution has N unvalidated sections:
$SECTIONS

Heavy tier constitutions require full validation before workflow commands.

To resolve:
  1. Run /spec:constitution to customize your constitution
  2. Run flowspec constitution validate to verify
  3. Remove all NEEDS_VALIDATION markers

Or use --skip-validation to bypass (not recommended).

Command blocked until constitution is validated.
```

**DO NOT PROCEED** with the command. Exit and wait for user to resolve.

### 4. Skip Validation Flag

If the command was invoked with `--skip-validation`:

```bash
# Check for skip flag in arguments
if [[ "$ARGUMENTS" == *"--skip-validation"* ]]; then
  echo "⚠️ Skipping constitution validation (--skip-validation)"
  # Remove the flag from arguments and continue
  ARGUMENTS="${ARGUMENTS/--skip-validation/}"
fi
```

When skip flag is present:
- Log warning
- Skip all validation checks
- Continue with command
- Note: For emergency use only

### 5. Fully Validated Constitution

If `MARKER_COUNT = 0`:

```text
[Y] Constitution validated
```

Continue with command normally.

## Summary: When to Block vs Warn

| Tier | Unvalidated Sections | Action |
|------|---------------------|--------|
| Light | 0 | [Y] Continue |
| Light | >0 | ⚠️ Warn, continue |
| Medium | 0 | [Y] Continue |
| Medium | >0 | ⚠️ Warn, ask confirmation, respect user choice |
| Heavy | 0 | [Y] Continue |
| Heavy | >0 | [X] Block, require validation |
| Any | >0 + `--skip-validation` | ⚠️ Warn, continue |

## Integration Example

```markdown
---
description: Your command description
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

{{INCLUDE:.claude/partials/flow/_constitution-check.md}}

{{INCLUDE:.claude/partials/flow/_workflow-state.md}}

## Execution Instructions

[Rest of your command implementation...]
```

## Related Commands

| Command | Purpose |
|---------|---------|
| `flowspec init --here` | Initialize constitution if missing |
| `/spec:constitution` | Interactive constitution customization |
| `flowspec constitution validate` | Check validation status and show report |
| `flowspec constitution show` | Display current constitution |


### Overview

The custom command:
1. Loads custom workflow definitions from `flowspec_workflow.yml`
2. Validates rigor enforcement rules
3. Executes workflow steps in sequence
4. Handles conditional logic (e.g., `complexity >= 7`)
5. Manages checkpoints for spec-ing mode
6. Logs all decisions and events to `.logs/`

### Usage

```bash
# List available custom workflows
/flow:custom

# Execute a specific custom workflow
/flow:custom quick_build
/flow:custom full_design
/flow:custom ship_it
```

### Implementation

Use the `WorkflowOrchestrator` to execute custom workflows:

```python
from pathlib import Path
from flowspec_cli.workflow.orchestrator import WorkflowOrchestrator

# Get workspace root
workspace_root = Path.cwd()

# Generate unique session ID
import datetime
session_id = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

# Initialize orchestrator
orchestrator = WorkflowOrchestrator(workspace_root, session_id)

# Parse workflow name from arguments
workflow_name = "$ARGUMENTS".strip()

if not workflow_name:
    # List available workflows
    workflows = orchestrator.list_custom_workflows()
    if not workflows:
        print("No custom workflows defined in flowspec_workflow.yml")
        print("\nExample custom_workflows section:")
        print("""
custom_workflows:
  quick_build:
    name: "Quick Build"
    mode: "vibing"
    steps:
      - workflow: "specify"
      - workflow: "implement"
      - workflow: "validate"
    rigor:
      log_decisions: true
      log_events: true
      backlog_integration: true
      memory_tracking: true
      follow_constitution: true
""")
    else:
        print(f"Available custom workflows ({len(workflows)}):\n")
        for wf_name in workflows:
            wf_def = orchestrator.custom_workflows[wf_name]
            print(f"  {wf_name}")
            print(f"    Name: {wf_def.get('name', 'N/A')}")
            print(f"    Mode: {wf_def.get('mode', 'N/A')}")
            print(f"    Steps: {len(wf_def.get('steps', []))}")
            if 'description' in wf_def:
                print(f"    Description: {wf_def['description']}")
            print()
else:
    # Execute the custom workflow
    try:
        # Optional: Get context for condition evaluation
        # For example, if assess was run, load complexity score
        context = {}

        # Execute workflow (get execution plan)
        result = orchestrator.execute_custom_workflow(workflow_name, context)

        if result.success:
            print(f"\n✓ Custom workflow '{workflow_name}' execution plan prepared")
            print(f"  Steps to execute: {result.steps_executed}")
            print(f"  Steps skipped: {result.steps_skipped}")
            
            # Execute each workflow step command
            print(f"\nExecuting {result.steps_executed} workflow steps...")
            
            for i, step_result in enumerate(result.step_results, 1):
                if step_result.skipped:
                    print(f"  [{i}] SKIPPED: {step_result.workflow_name} - {step_result.skip_reason}")
                    continue
                
                if step_result.command:
                    print(f"  [{i}] Invoking {step_result.command}...")
                    # AGENT EXECUTION POINT: This is where Claude Code invokes the workflow
                    # When running as an agent, replace this print with actual Skill invocation:
                    # await skill_tool.invoke(step_result.command)
                    print(f"      → Command: {step_result.command}")
                    print(f"      → Status: Ready for execution")
                else:
                    print(f"  [{i}] ERROR: No command for {step_result.workflow_name}")
            
            print(f"\n✓ Workflow execution plan complete")
            print(f"\nDecision log: .logs/decisions/session-{session_id}.jsonl")
            print(f"Event log: .logs/events/session-{session_id}.jsonl")
            print(f"\nNOTE: When running as an agent (Claude Code), the workflow commands")
            print(f"      above should be automatically invoked using the Skill tool.")
        else:
            print(f"\n✗ Custom workflow '{workflow_name}' failed")
            print(f"  Error: {result.error}")
            print(f"  Steps completed before failure: {result.steps_executed}")

    except ValueError as e:
        print(f"✗ Error: {e}")
        print(f"\nAvailable workflows:")
        for wf_name in orchestrator.list_custom_workflows():
            print(f"  - {wf_name}")
```

### Custom Workflow Definition

Custom workflows are defined in the `custom_workflows` section of `flowspec_workflow.yml`:

```yaml
custom_workflows:
  my_workflow:
    name: "My Custom Workflow"
    description: "Optional description"
    mode: "vibing"  # or "spec-ing"
    steps:
      - workflow: "specify"
      - workflow: "research"
        condition: "complexity >= 7"  # conditional execution
      - workflow: "plan"
        checkpoint: "Review architecture?"  # approval point in spec-ing mode
      - workflow: "implement"
    rigor:  # REQUIRED - cannot be disabled
      log_decisions: true
      log_events: true
      backlog_integration: true
      memory_tracking: true
      follow_constitution: true
```

### Execution Modes

- **vibing**: Autonomous execution, no checkpoints, full logging
- **spec-ing**: Stop at checkpoints for user approval

### Conditional Execution

Steps can include conditions evaluated against context:

```yaml
- workflow: "research"
  condition: "complexity >= 7"  # only run if complexity score >= 7
```

Supported operators: `>=`, `<=`, `==`, `!=`, `>`, `<`

### Rigor Enforcement

All custom workflows MUST have rigor rules set to `true`. This is enforced by the schema and cannot be disabled:

- `log_decisions`: Log to `.logs/decisions/*.jsonl`
- `log_events`: Log to `.logs/events/*.jsonl`
- `backlog_integration`: Integrate with backlog.md via MCP
- `memory_tracking`: Track task state across sessions
- `follow_constitution`: Follow `.specify/memory/constitution.md`

### Integration Point

The orchestrator reaches the workflow invocation point at `src/flowspec_cli/workflow/orchestrator.py:373-416`.

For full integration, wire dispatch logic to actual workflow modules:

```python
# Example dispatch pattern (to be implemented):
workflow_handlers = {
    "specify": specify_module.execute,
    "plan": plan_module.execute,
    "implement": implement_module.execute,
    "validate": validate_module.execute,
}

handler = workflow_handlers.get(workflow_name)
if handler:
    handler(workspace_root, ...)
```

### See Also

- `build-docs/simplify/flowspec-loop.md` - Inner loop architecture
- `schemas/flowspec_workflow.schema.json` - Custom workflow schema
- `src/flowspec_cli/workflow/orchestrator.py` - Orchestrator implementation
- `src/flowspec_cli/workflow/rigor.py` - Rigor enforcement
