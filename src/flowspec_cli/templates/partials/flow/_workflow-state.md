# Workflow State Validation

## Step 0: Workflow State Validation (REQUIRED)

**CRITICAL**: This command requires a task to be in the correct workflow state before execution.

### Light Mode Detection

First, check if this project is in light mode:

```bash
# Check for light mode marker
if [ -f ".flowspec-light-mode" ]; then
  echo "Project is in LIGHT MODE (~60% faster workflow)"
fi
```

**Light Mode Behavior**:
- `/flow:research` -> **SKIPPED** (inform user and suggest `/flow:plan` instead)
- `/flow:plan` -> Uses `plan-light.md` template (high-level only)
- `/flow:specify` -> Uses `spec-light.md` template (combined stories + AC)

If in light mode and the current command is `/flow:research`, inform the user:
```text
ℹ️ This project is in Light Mode

Light mode skips the research phase for faster iteration.
Current state: workflow:Specified

Suggestions:
  - Run /flow:plan to proceed directly to planning
  - To enable research, delete .flowspec-light-mode and use full mode
  - See docs/guides/when-to-use-light-mode.md for details
```

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
| /flow:assess | workflow:To Do, (no workflow label) | workflow:Assessed |
| /flow:specify | workflow:Assessed | workflow:Specified |
| /flow:research | workflow:Specified | workflow:Researched |
| /flow:plan | workflow:Specified, workflow:Researched | workflow:Planned |
| /flow:implement | workflow:Planned | workflow:In Implementation |
| /flow:validate | workflow:In Implementation | workflow:Validated |

### 3. Handle Invalid State

If the task's workflow state doesn't match the required input states:

```text
⚠️ Cannot run /flow:<command>

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

- `workflow:Assessed` - SDD suitability evaluated (/flow:assess complete)
- `workflow:Specified` - Requirements captured (/flow:specify complete)
- `workflow:Researched` - Technical research completed (/flow:research complete)
- `workflow:Planned` - Architecture planned (/flow:plan complete)
- `workflow:In Implementation` - Code being written (/flow:implement in progress)
- `workflow:Validated` - QA and security validated (/flow:validate complete) - this is the final workflow state

## Programmatic State Checking

The state guard module can also be used programmatically:

```python
from flowspec_cli.workflow import check_workflow_state, get_valid_workflows

# Check if current state allows command execution
can_proceed, message = check_workflow_state("implement", current_state)

if not can_proceed:
    print(message)
    # Shows error with suggestions

# Get valid commands for a state
valid_commands = get_valid_workflows("Specified")
# Returns: ['/flow:research', '/flow:plan']
```

## Bypassing State Checks (Power Users Only)

State checks can be bypassed in special circumstances:
- Emergency hotfixes
- Iterative refinement of specifications
- Recovery from failed workflows

Use `--skip-state-check` flag or explicitly acknowledge the bypass.

**Warning**: Bypassing state checks may result in incomplete artifacts or broken workflows.
