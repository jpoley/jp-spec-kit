---
mode: agent
description: Execute research and business validation workflow using specialized agents.
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
| Research Report | `./docs/research/{feature}-research.md` | Comprehensive research findings and business validation |

## Feature Naming

The `{feature}` slug is derived from the feature name:
- Convert to lowercase
- Replace spaces with hyphens
- Remove special characters
- Example: "User Authentication" → "user-authentication" → `./docs/research/user-authentication-research.md`

## Outline

This command orchestrates research and business validation using two specialized agents:

1. **Researcher Agent**: Goes out and does research on an idea
   - Conducts market research
   - Analyzes competitive landscape
   - Gathers technical feasibility data
   - Identifies industry trends and best practices

2. **Business Validator Agent**: Provides realistic validation based on certain criteria
   - Evaluates business viability
   - Assesses market potential
   - Validates against business constraints
   - Provides risk assessment

## Execution Flow

1. Parse user input to understand research topic and validation requirements

2. **Research Phase**:
   - Dispatch Researcher agent to gather information
   - Collect findings on market, technical, and competitive aspects
   - Document research results

3. **Validation Phase**:
   - Dispatch Business Validator agent with research findings
   - Apply validation criteria (market size, feasibility, ROI potential, etc.)
   - Generate validation report

4. **Output**:
   - Consolidated research document at `./docs/research/{feature}-research.md`
   - Business validation assessment
   - Recommendations for next steps

## Completion Checklist

Before completing this command, verify:

- [ ] `./docs/research/` directory exists
- [ ] Research report created at `./docs/research/{feature}-research.md`
- [ ] Market research findings are documented
- [ ] Competitive landscape analysis is complete
- [ ] Technical feasibility is assessed
- [ ] Business validation includes clear Go/No-Go/Proceed-with-Caution recommendation
- [ ] Follow-up implementation or spike tasks have been created

## Transition Validation

This command can transition workflow state: **"Assessed" → "Researched"** or **"Specified" → "Researched"**

**Validation Mode**: Configured per project (see `.specify/workflow/transition-validation.yml`)

See task-175 for validation mode implementation details.

## Notes

- This command is a placeholder for future agent implementation
- Full agent integration will be completed in a future task

---

## ⚠️ MANDATORY: Design→Implement Workflow

**This is a DESIGN command. Research tasks MUST create implementation tasks before completion.**

After the research and business validation agents complete their work:

1. **Create implementation tasks** based on research findings and recommendations:
   ```bash
   # Example: Create tasks from research recommendations
   backlog task create "Implement [Recommended Solution]" \
     -d "Implementation based on research findings from /jpspec:research" \
     --ac "Implement approach recommended in research report" \
     --ac "Address feasibility concerns identified in validation" \
     --ac "Monitor metrics identified in business case" \
     -l implement,research-followup \
     --priority high

   backlog task create "Technical Spike: [Validate Key Assumption]" \
     -d "Validation spike based on research critical assumptions" \
     --ac "Validate assumption X from research report" \
     --ac "Document findings and update implementation plan" \
     -l spike,research-followup
   ```

2. **Update research task notes** with follow-up references:
   ```bash
   backlog task edit <research-task-id> --append-notes $'Research Outcome: Go/No-Go/Proceed with Caution\n\nFollow-up Implementation Tasks:\n- task-XXX: Implement recommended solution\n- task-YYY: Validation spike for assumption A'
   ```

3. **Only then mark the research task as Done**

**Research without actionable follow-up tasks provides no value. Every research effort must produce implementation direction.**

**Note**: If research concludes with "No-Go" recommendation, create a documentation task to record the decision and rationale for future reference.

### Post-Completion: Emit Workflow Event

After successfully completing this command, emit the workflow event to trigger any configured hooks:

```bash
# Emit the research.completed event
specify hooks emit research.completed \
  --spec-id "$FEATURE_NAME" \
  --task-id "$TASK_ID" \
  -f "docs/research/${FEATURE_NAME}-research.md" \
  -f "docs/research/${FEATURE_NAME}-validation.md"
```

This triggers any configured hooks in `.specify/hooks/hooks.yaml`. Common use cases:
- Auto-notify team of research findings
- Update competitive analysis dashboards
- Trigger business case review workflows

**Note**: If the `specify` CLI is not available or hooks are not configured, this step can be skipped without affecting the workflow.
