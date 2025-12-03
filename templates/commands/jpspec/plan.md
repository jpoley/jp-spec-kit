---
mode: agent
description: Execute planning workflow using project architect and platform engineer agents (builds out /speckit.constitution).
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
| Architecture Decision Records | `./docs/adr/ADR-{NNN}-{slug}.md` | Sequential ADRs documenting architectural decisions |
| Implementation Plan | `./docs/plan/{feature}-plan.md` | Comprehensive implementation plan with architecture and platform design |

## Feature Naming

The `{feature}` slug is derived from the feature name:
- Convert to lowercase
- Replace spaces with hyphens
- Remove special characters
- Example: "User Authentication" → "user-authentication"

ADR numbering (`{NNN}`):
- Three-digit sequential number (001, 002, 003, etc.)
- Find next available number by checking existing ADRs in `./docs/adr/`
- Slug derived from ADR title
- Example: "Use PostgreSQL for User Store" → `ADR-042-use-postgresql-for-user-store.md`

## Outline

This command executes the planning workflow using two specialized agents:

1. **Project Architect Agent**: Designs architecture like Gregor Hohpe
   - Creates comprehensive system architecture
   - Defines architectural patterns and principles
   - Designs component interactions and boundaries
   - Establishes architectural decision records (ADRs)
   - Builds out /speckit.constitution with architectural principles

2. **Platform Engineer Agent**: Designs infrastructure and backend systems
   - Plans infrastructure architecture
   - Designs backend systems and services
   - Defines deployment and scaling strategies
   - Establishes platform engineering best practices
   - Contributes platform principles to /speckit.constitution

## Execution Flow

1. Parse user input to understand planning requirements and constraints

2. **Architecture Planning**:
   - Dispatch Project Architect agent
   - Generate system architecture design
   - Create architectural diagrams and documentation
   - Define architectural principles and patterns
   - Document key architectural decisions in ADRs

3. **Platform Planning**:
   - Dispatch Platform Engineer agent
   - Design infrastructure architecture
   - Plan backend systems and data flows
   - Define deployment pipelines and strategies
   - Establish observability and monitoring approach

4. **Constitution Integration**:
   - Build out /speckit.constitution with:
     - Architectural principles and constraints
     - Platform engineering standards
     - Infrastructure requirements
     - Deployment and operational guidelines

5. **Output**:
   - Complete implementation plan at `./docs/plan/{feature}-plan.md`
   - Architecture design documents
   - Infrastructure design specifications
   - ADRs at `./docs/adr/ADR-{NNN}-{slug}.md` for each major decision
   - Updated constitution with planning principles
   - Technical decision records

## Completion Checklist

Before completing this command, verify:

- [ ] `./docs/adr/` directory exists
- [ ] `./docs/plan/` directory exists
- [ ] Implementation plan created at `./docs/plan/{feature}-plan.md`
- [ ] All major architectural decisions have corresponding ADRs
- [ ] ADRs follow sequential numbering convention
- [ ] ADRs include context, decision, consequences, and alternatives
- [ ] Platform engineering requirements are documented
- [ ] Observability and monitoring approach is defined
- [ ] Follow-up implementation tasks have been created

## Transition Validation

This command transitions workflow state: **"Specified" → "Planned"** or **"Researched" → "Planned"**

**Validation Mode**: Configured per project (see `.specify/workflow/transition-validation.yml`)

See task-175 for validation mode implementation details.

## Notes

- This command is a placeholder for future agent implementation
- Full Project Architect and Platform Engineer agent integration will be completed in a future task
- Builds out and updates /speckit.constitution

---

## ⚠️ MANDATORY: Design→Implement Workflow

**This is a DESIGN command. Planning tasks MUST create implementation tasks before completion.**

After the architecture and platform agents complete their work:

1. **Create implementation tasks** for each architectural component:
   ```bash
   # Example: Create tasks from architecture decisions
   backlog task create "Implement [Component Name] Service" \
     -d "Implementation based on architecture from /jpspec:plan" \
     --ac "Implement service per architecture doc section X" \
     --ac "Follow integration patterns from ADR-001" \
     --ac "Add observability per platform requirements" \
     --ac "Write integration tests" \
     -l implement,architecture,backend \
     --priority high

   backlog task create "Implement [Infrastructure Component]" \
     -d "Infrastructure implementation per platform design" \
     --ac "Configure CI/CD per platform architecture" \
     --ac "Set up monitoring per observability requirements" \
     --ac "Implement security controls per ADR" \
     -l implement,infrastructure,devops
   ```

2. **Update planning task notes** with follow-up references:
   ```bash
   backlog task edit <plan-task-id> --append-notes $'Follow-up Implementation Tasks:\n- task-XXX: Implement service A\n- task-YYY: Implement infrastructure\n- task-ZZZ: Configure CI/CD pipeline'
   ```

3. **Only then mark the planning task as Done**

**Architecture without implementation tasks is incomplete design work.**

### Post-Completion: Emit Workflow Event

After successfully completing this command, emit the workflow event to trigger any configured hooks:

```bash
# Emit the plan.created event
specify hooks emit plan.created \
  --spec-id "$FEATURE_NAME" \
  --task-id "$TASK_ID" \
  -f "docs/adr/*.md" \
  -f "docs/plan/${FEATURE_NAME}-plan.md" \
  -f "docs/architecture/${FEATURE_NAME}-architecture.md" \
  -f "docs/platform/${FEATURE_NAME}-*.md"
```

This triggers any configured hooks in `.specify/hooks/hooks.yaml`. Common use cases:
- Auto-notify architecture review board
- Generate implementation tickets in external systems
- Trigger security review workflows

**Note**: If the `specify` CLI is not available or hooks are not configured, this step can be skipped without affecting the workflow.
