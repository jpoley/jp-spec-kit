---
description: Deploy It - Production deployment and operational readiness
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

## Meta-Workflow: Run (Deploy It)

This meta-workflow executes the deployment phase:

1. **Operate** - Deploy to production and create operational artifacts

**Required input state**: `Validated`
**Output state**: `Deployed`

## Step 1: Verify Task State

```bash
# Get current task from branch or arguments
TASK_ID="${TASK_ID:-$(git branch --show-current 2>/dev/null | grep -Eo 'task-[0-9]+' || echo '')}"

if [ -z "$TASK_ID" ]; then
  echo "❌ No task ID found. Run from a feature branch or specify task ID."
  echo "Usage: /flow:meta-run [task-id]"
  exit 1
fi

# Check task state using backlog.md
CURRENT_STATE=$(backlog task "$TASK_ID" --plain 2>/dev/null | grep "^Status:" | awk '{print $2}')

if [ "$CURRENT_STATE" != "Validated" ]; then
  echo "❌ Task $TASK_ID is in state '$CURRENT_STATE' but requires 'Validated'"
  echo "This meta-workflow can only run from 'Validated' state."
  echo ""
  echo "Did you run /flow:meta-build first?"
  exit 1
fi

echo "✓ Task $TASK_ID verified in 'Validated' state"
echo "✓ Starting meta-workflow: run (Deploy It)"
echo ""
```

## Step 2: Execute Sub-Workflow

### 2.1 Run /flow:operate

Execute deployment and create operational artifacts:

**Execute**: `/flow:operate`

Wait for operate to complete. This will:
- Generate deployment configurations (Kubernetes, Docker, Terraform, etc.)
- Create operational runbooks in `docs/runbooks/`
- Set up monitoring and alerting (optional)
- Execute CI/CD pipeline (if configured)
- Create deployment logs in `.logs/deployment/`
- Transition task to `Deployed` state

## Step 3: Verify Deployment

After operate completes, verify the task reached the deployed state:

```bash
# Check final task state
FINAL_STATE=$(backlog task "$TASK_ID" --plain 2>/dev/null | grep "^Status:" | awk '{print $2}')

if [ "$FINAL_STATE" = "Deployed" ]; then
  echo ""
  echo "✅ Meta-workflow 'run' completed successfully!"
  echo "   Task $TASK_ID transitioned: Validated → Deployed"
  echo ""
  echo "Artifacts created:"
  echo "  - docs/runbooks/$TASK_ID-runbook.md"
  echo "  - deploy/ (deployment manifests)"
  echo "  - .logs/deployment/$TASK_ID-deploy.log"
  echo ""
  echo "Deployment complete! Feature is now in production."
  echo ""
  echo "Next steps:"
  echo "  - Monitor application metrics and logs"
  echo "  - Review runbook for operational procedures"
  echo "  - Set up alerts and dashboards as needed"
else
  echo "⚠️ Warning: Expected state 'Deployed' but task is in '$FINAL_STATE'"
  echo "Deployment may have failed. Review errors above."
  exit 1
fi
```

## Execution Summary

This meta-workflow consolidates deployment operations:

**Instead of:**
```bash
/flow:operate  # Manual deployment steps
```

**You run:**
```bash
/flow:meta-run  # Automated deployment with runbooks
```

All operations integrate with backlog.md for state management and deployment tracking.

## See Also

- `/flow:meta-research` - Plan It (assess + specify + research + plan)
- `/flow:meta-build` - Create It (implement + validate)
- `flowspec_workflow.yml` - Configuration reference
- `docs/adr/003-meta-workflow-simplification.md` - Design rationale
