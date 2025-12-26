---
description: Plan It - Complete upfront analysis and design (assess + specify + research + plan)
mode: agent
loop: outer
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

{{INCLUDE:.claude/commands/flow/_constitution-check.md}}

{{INCLUDE:.claude/commands/flow/_rigor-rules.md}}

{{INCLUDE:.claude/commands/flow/_workflow-state.md}}

## Meta-Workflow: Research (Plan It)

This meta-workflow executes the complete planning phase by running these sub-workflows in sequence:

1. **Assess** - Evaluate SDD workflow suitability
2. **Specify** - Create PRD and implementation tasks
3. **Research** - Deep research (conditional: if complexity ≥ 7)
4. **Plan** - Create ADRs and technical design

**Required input state**: `To Do`
**Output state**: `Planned`

## Step 1: Verify Task State

```bash
# Get current task from branch or arguments
TASK_ID="${TASK_ID:-$(git branch --show-current 2>/dev/null | grep -Eo 'task-[0-9]+' || echo '')}"

if [ -z "$TASK_ID" ]; then
  echo "❌ No task ID found. Run from a feature branch or specify task ID."
  echo "Usage: /flow:meta-research [task-id]"
  exit 1
fi

# Check task state using backlog.md
CURRENT_STATE=$(backlog task "$TASK_ID" --plain 2>/dev/null | grep "^Status:" | awk '{print $2" "$3}')

if [ "$CURRENT_STATE" != "To Do" ]; then
  echo "❌ Task $TASK_ID is in state '$CURRENT_STATE' but requires 'To Do'"
  echo "This meta-workflow can only run from 'To Do' state."
  exit 1
fi

echo "✓ Task $TASK_ID verified in 'To Do' state"
echo "✓ Starting meta-workflow: research (Plan It)"
echo ""
```

## Step 2: Execute Sub-Workflows

Execute each sub-workflow in sequence. The orchestrator ensures proper state transitions and backlog integration.

### 2.1 Run /flow:assess

Evaluate SDD workflow suitability and determine complexity:

**Execute**: `/flow:assess`

Wait for assess to complete before proceeding. This will:
- Analyze feature complexity
- Determine if research phase is needed
- Transition task to `Assessed` state
- Create assessment report in `docs/assess/`

### 2.2 Run /flow:specify

Create comprehensive product requirements document:

**Execute**: `/flow:specify`

Wait for specify to complete. This will:
- Create PRD in `docs/prd/`
- Generate backlog tasks in `backlog/tasks/`
- Define acceptance criteria
- Transition task to `Specified` state

### 2.3 Run /flow:research (Conditional)

**Condition**: Execute only if complexity ≥ 7 OR explicitly requested

```bash
# Check complexity score from assessment
COMPLEXITY=$(grep -oP 'complexity_score:\s*\K\d+' "docs/assess/$TASK_ID-assessment.md" 2>/dev/null || echo "0")

if [ "$COMPLEXITY" -ge 7 ]; then
  echo "✓ Complexity score: $COMPLEXITY (≥7) - Running research phase"
  # Execute /flow:research below
elif echo "$ARGUMENTS" | grep -q "force-research\|--research"; then
  echo "✓ Research explicitly requested via arguments"
  # Execute /flow:research below
else
  echo "⊘ Skipping research (complexity: $COMPLEXITY < 7, not forced)"
  # Skip to plan
  exit 0
fi
```

If condition is met, **Execute**: `/flow:research`

This will:
- Conduct market/technical research
- Validate business assumptions
- Create research report in `docs/research/`
- Transition task to `Researched` state

### 2.4 Run /flow:plan

Create architecture decision records and technical design:

**Execute**: `/flow:plan`

Wait for plan to complete. This will:
- Create ADRs in `docs/adr/`
- Design system architecture
- Create platform/infrastructure specs
- Transition task to `Planned` state

## Step 3: Verify Completion

After all sub-workflows complete, verify the task reached the final state:

```bash
# Check final task state
FINAL_STATE=$(backlog task "$TASK_ID" --plain 2>/dev/null | grep "^Status:" | awk '{print $2}')

if [ "$FINAL_STATE" = "Planned" ]; then
  echo ""
  echo "✅ Meta-workflow 'research' completed successfully!"
  echo "   Task $TASK_ID transitioned: To Do → Planned"
  echo ""
  echo "Artifacts created:"
  echo "  - docs/assess/$TASK_ID-assessment.md"
  echo "  - docs/prd/$TASK_ID.md"
  echo "  - docs/research/$TASK_ID-research.md (if complexity ≥ 7)"
  echo "  - docs/adr/ADR-*.md"
  echo "  - backlog/tasks/*.md"
  echo ""
  echo "Next step: Run /flow:meta-build to implement the feature"
else
  echo "⚠️ Warning: Expected state 'Planned' but task is in '$FINAL_STATE'"
  echo "One or more sub-workflows may have failed. Review errors above."
  exit 1
fi
```

## Execution Summary

This meta-workflow consolidates 4 workflow commands into 1:

**Instead of running separately:**
```bash
/flow:assess
/flow:specify
/flow:research  # if complexity ≥ 7
/flow:plan
```

**You run once:**
```bash
/flow:meta-research
```

All sub-workflows integrate with backlog.md for state management, task tracking, and artifact linking.

## See Also

- `/flow:meta-build` - Create It (implement + validate)
- `/flow:meta-run` - Deploy It (operate)
- `flowspec_workflow.yml` - Configuration reference
- `docs/adr/003-meta-workflow-simplification.md` - Design rationale
