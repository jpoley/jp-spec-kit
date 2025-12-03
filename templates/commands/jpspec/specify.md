---
mode: agent
description: Create or update feature specifications using PM planner agent (manages /speckit.tasks).
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Output Artifacts

All artifacts are written to standardized locations:

| Artifact Type | Output Location | Description |
|---------------|-----------------|-------------|
| Product Requirement Document | `./docs/prd/{feature}.md` | Comprehensive PRD with requirements, user stories, and acceptance criteria |

## Feature Naming

The `{feature}` slug is derived from the feature name:
- Convert to lowercase
- Replace spaces with hyphens
- Remove special characters
- Example: "User Authentication" → "user-authentication" → `./docs/prd/user-authentication.md`

## Outline

This command creates feature specifications using a specialized PM (Product Manager) planner agent.

1. **PM Planner Agent**: Creates PRDs (Product Requirement Documents)
   - Analyzes product requirements from user input
   - Creates comprehensive PRDs following best practices
   - Manages task breakdown and prioritization
   - Integrates with /speckit.tasks for task management
   - Ensures specifications are clear, complete, and actionable

## Execution Flow

1. Parse user input to understand feature requirements

2. **Specification Creation**:
   - Dispatch PM Planner agent to analyze requirements
   - Generate Product Requirement Document (PRD)
   - Define user stories and acceptance criteria
   - Identify dependencies and constraints

3. **Task Management**:
   - Coordinate with /speckit.tasks for task breakdown
   - Ensure traceability between requirements and tasks
   - Define success criteria and metrics

4. **Output**:
   - Complete feature specification document at `./docs/prd/{feature}.md`
   - PRD with detailed requirements
   - Task breakdown and dependencies
   - Success criteria and acceptance tests

## Completion Checklist

Before completing this command, verify:

- [ ] `./docs/prd/` directory exists
- [ ] PRD created at `./docs/prd/{feature}.md`
- [ ] All required sections are complete (problem statement, requirements, user stories, acceptance criteria)
- [ ] Dependencies and constraints are documented
- [ ] Success criteria and metrics are defined
- [ ] Follow-up implementation tasks have been created

## Transition Validation

This command transitions workflow state: **"Assessed" → "Specified"**

**Validation Mode**: Configured per project (see `.specify/workflow/transition-validation.yml`)

See task-175 for validation mode implementation details.

## Notes

- This command is a placeholder for future agent implementation
- Full PM Planner agent integration will be completed in a future task
- Manages interaction with /speckit.tasks workflow

---

## ⚠️ MANDATORY: Design→Implement Workflow

**This is a DESIGN command. Specification tasks MUST create implementation tasks before completion.**

After the PM Planner agent completes its work:

1. **Create implementation tasks** for each major deliverable:
   ```bash
   # Example: Create tasks from PRD sections
   backlog task create "Implement [Feature Core Functionality]" \
     -d "Implementation based on PRD from /jpspec:specify" \
     --ac "Implement core feature per PRD section 4" \
     --ac "Add validation per NFR section" \
     --ac "Write unit tests" \
     -l implement,backend \
     --priority high

   backlog task create "Implement [Feature UI Components]" \
     -d "Frontend implementation per PRD user stories" \
     --ac "Build UI components per PRD wireframes" \
     --ac "Implement accessibility per WCAG 2.1 AA" \
     --ac "Add integration tests" \
     -l implement,frontend
   ```

2. **Update specification task notes** with follow-up references:
   ```bash
   backlog task edit <spec-task-id> --append-notes $'Follow-up Implementation Tasks:\n- task-XXX: Implement core functionality\n- task-YYY: Implement UI components'
   ```

3. **Only then mark the specification task as Done**

**Failure to create implementation tasks means the specification work is incomplete.**

## Post-Completion: Emit Workflow Event

After successfully completing this command, emit the workflow event to trigger any configured hooks:

```bash
# Emit the spec.created event
specify hooks emit spec.created \
  --spec-id "$FEATURE_NAME" \
  --task-id "$TASK_ID" \
  -f "docs/prd/${FEATURE_NAME}.md"
```

This triggers any configured hooks in `.specify/hooks/hooks.yaml`. Common use cases:
- Auto-notify stakeholders of new PRD
- Generate architecture diagrams from spec
- Trigger dependency analysis

**Note**: If the `specify` CLI is not available or hooks are not configured, this step can be skipped without affecting the workflow.
