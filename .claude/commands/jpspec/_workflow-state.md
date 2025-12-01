# Workflow State Management

## Overview

JP Spec Kit tracks workflow state using labels on backlog tasks. This enables proper workflow constraint enforcement.

## Workflow State Labels

Tasks use labels with the `workflow:` prefix to track their current workflow state:

- `workflow:Assessed` - SDD suitability evaluated
- `workflow:Specified` - Requirements captured
- `workflow:Researched` - Technical research completed
- `workflow:Planned` - Architecture planned
- `workflow:In Implementation` - Code being written
- `workflow:Validated` - QA and security validated
- `workflow:Deployed` - Released to production

## Checking Workflow State

```bash
# Get current task's workflow state from labels
TASK_ID=$(backlog task list -s "In Progress" --plain | head -1 | awk '{print $2}')
TASK_LABELS=$(backlog task "$TASK_ID" --plain | grep "^Labels:" | cut -d: -f2-)

# Extract workflow state from labels
CURRENT_STATE=""
for label in $TASK_LABELS; do
  if [[ "$label" == workflow:* ]]; then
    CURRENT_STATE="${label#workflow:}"
    break
  fi
done

echo "Task: $TASK_ID"
echo "Workflow State: ${CURRENT_STATE:-Not Set}"
```

## Setting Workflow State

After completing a workflow, update the task's workflow state label:

```bash
# Remove old workflow label and add new one
backlog task edit "$TASK_ID" -l "workflow:Planned"
```

## State Transitions

Each `/jpspec:*` command has defined input and output states:

| Command | Input States | Output State |
|---------|--------------|--------------|
| /jpspec:assess | (new task) | Assessed |
| /jpspec:specify | Assessed | Specified |
| /jpspec:research | Specified | Researched |
| /jpspec:plan | Specified, Researched | Planned |
| /jpspec:implement | Planned | In Implementation |
| /jpspec:validate | In Implementation | Validated |
| /jpspec:operate | Validated | Deployed |
