# Workflow State Validation

## Step 0: Workflow State Validation (REQUIRED)

**CRITICAL**: This command requires a task to be in the correct workflow state before execution.

### 1. Get Current Task and State

```bash
# Find the task you're working on
# Option A: If task ID was provided in arguments, use that
# Option B: Look for task currently "In Progress"
backlog task list -s "In Progress" --plain

# Get task details and extract workflow state from labels
TASK_ID="<task-id>"  # Replace with actual task ID
backlog task "$TASK_ID" --plain
```

### 2. Check Workflow State

Extract the `workflow:*` label from the task. The state must match one of the **Required Input States** for this command:

| Command | Required Input States | Output State |
|---------|----------------------|--------------|
| /jpspec:assess | workflow:To Do, (no workflow label) | workflow:Assessed |
| /jpspec:specify | workflow:Assessed | workflow:Specified |
| /jpspec:research | workflow:Specified | workflow:Researched |
| /jpspec:plan | workflow:Specified, workflow:Researched | workflow:Planned |
| /jpspec:implement | workflow:Planned | workflow:In Implementation |
| /jpspec:validate | workflow:In Implementation | workflow:Validated |
| /jpspec:operate | workflow:Validated | workflow:Deployed |

### 3. Handle Invalid State

If the task's workflow state doesn't match the required input states:

```text
⚠️ Cannot run /jpspec:<command>

Current state: "<current-workflow-label>"
Required states: <list-of-valid-input-states>

Suggestions:
  - Valid workflows for current state: <list-valid-commands>
  - Use --skip-state-check to bypass (not recommended)
```

**DO NOT PROCEED** unless:
- The task is in a valid input state, OR
- User explicitly requests to skip the check

### 4. Update State After Completion

After successful workflow completion, update the task's workflow state:

```bash
# Remove old workflow label and add new one
# Replace <output-state> with the output state from the table above
backlog task edit "$TASK_ID" -l "workflow:<output-state>"
```

## Workflow State Labels Reference

Tasks use labels with the `workflow:` prefix to track their current workflow state:

- `workflow:Assessed` - SDD suitability evaluated (/jpspec:assess complete)
- `workflow:Specified` - Requirements captured (/jpspec:specify complete)
- `workflow:Researched` - Technical research completed (/jpspec:research complete)
- `workflow:Planned` - Architecture planned (/jpspec:plan complete)
- `workflow:In Implementation` - Code being written (/jpspec:implement in progress)
- `workflow:Validated` - QA and security validated (/jpspec:validate complete)
- `workflow:Deployed` - Released to production (/jpspec:operate complete)

## Programmatic State Checking

The state guard module can also be used programmatically:

```python
from specify_cli.workflow import check_workflow_state, get_valid_workflows

# Check if current state allows command execution
can_proceed, message = check_workflow_state("implement", current_state)

if not can_proceed:
    print(message)
    # Shows error with suggestions

# Get valid commands for a state
valid_commands = get_valid_workflows("Specified")
# Returns: ['/jpspec:research', '/jpspec:plan']
```

## Bypassing State Checks (Power Users Only)

State checks can be bypassed in special circumstances:
- Emergency hotfixes
- Iterative refinement of specifications
- Recovery from failed workflows

Use `--skip-state-check` flag or explicitly acknowledge the bypass.

**Warning**: Bypassing state checks may result in incomplete artifacts or broken workflows.
