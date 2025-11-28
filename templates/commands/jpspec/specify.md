---
description: Create or update feature specifications using PM planner agent (manages /speckit.tasks).
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

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
   - Complete feature specification document
   - PRD with detailed requirements
   - Task breakdown and dependencies
   - Success criteria and acceptance tests

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
