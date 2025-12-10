# Workflow Step Tracking - Visual Reference

**Related Documents:**
- [ADR-002: Workflow Step Tracking Architecture](../adr/ADR-002-workflow-step-tracking-architecture.md)
- [Workflow Step Implementation Guide](./workflow-step-implementation-guide.md)

---

## Overview

This document provides visual diagrams and examples for understanding the two-level state model (board status + workflow step).

---

## Two-Level State Model

### Concept Diagram

```
┌────────────────────────────────────────────────────────────┐
│                   BACKLOG.MD TASK                          │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Level 1: BOARD STATUS (User Organization)                │
│  ┌──────────┬──────────────┬────────────┬──────────┐      │
│  │  To Do   │ In Progress  │ In Review  │   Done   │      │
│  └──────────┴──────────────┴────────────┴──────────┘      │
│      ↑            ↑              ↑           ↑            │
│      │            │              │           │            │
│  Level 2: WORKFLOW STEP (Lifecycle Phase)                 │
│  ┌────────────────────────────────────────────────────┐   │
│  │ To Do → Assessed → Specified → Researched →        │   │
│  │ Planned → In Implementation → Validated →          │   │
│  │ Deployed → Done                                    │   │
│  └────────────────────────────────────────────────────┘   │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Default Mapping

```
Workflow Step           →   Board Status
───────────────────────     ──────────────
To Do                   →   To Do
Assessed                →   In Progress
Specified               →   In Progress
Researched              →   In Progress
Planned                 →   In Progress
In Implementation       →   In Progress
Validated               →   In Review
Deployed                →   Done
Done                    →   Done
```

---

## Workflow State Machine

### Full JPSpec Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                     JPSPEC WORKFLOW STATES                      │
└─────────────────────────────────────────────────────────────────┘

    ┌─────────┐
    │  To Do  │  Initial state
    └────┬────┘
         │ /jpspec:assess
         ▼
    ┌──────────┐
    │ Assessed │  SDD workflow suitability evaluated
    └────┬─────┘
         │ /jpspec:specify
         ▼
    ┌────────────┐
    │ Specified  │  Requirements captured
    └──┬─────┬───┘
       │     │
       │     │ /jpspec:research (optional)
       │     ▼
       │  ┌────────────┐
       │  │ Researched │  Technical/business research
       │  └──────┬─────┘
       │         │
       │         │ /jpspec:plan
       │         ▼
       │  ┌─────────┐
       └─►│ Planned │  Architecture designed
          └────┬────┘
               │ /jpspec:implement
               ▼
    ┌────────────────────┐
    │ In Implementation  │  Code being written
    └────────┬───────────┘
             │ /jpspec:validate
             ▼
    ┌───────────┐
    │ Validated │  QA/security approved
    └─────┬─────┘
          │ /jpspec:operate
          ▼
    ┌──────────┐
    │ Deployed │  In production
    └─────┬────┘
          │ manual
          ▼
    ┌──────┐
    │ Done │  Complete
    └──────┘
```

### Backward Transitions (Rework)

```
┌───────────────────────────────────────────────────────┐
│               REWORK TRANSITIONS                      │
└───────────────────────────────────────────────────────┘

    ┌────────────────────┐
    │ In Implementation  │
    └────┬──────────┬────┘
         │          │
         │          │ rework (design issues)
         │          ▼
         │    ┌─────────┐
         │    │ Planned │
         │    └─────────┘
         │
         │ /jpspec:validate
         ▼
    ┌───────────┐
    │ Validated │
    └─────┬─────┘
          │
          │ rework (validation failures)
          │
          └──────► Back to In Implementation


    ┌──────────┐
    │ Deployed │
    └─────┬────┘
          │
          │ rollback (production issues)
          │
          └──────► Back to Validated
```

---

## Task Examples

### Example 1: Simple Task (No Workflow)

```yaml
---
id: task-001
title: Fix typo in README
status: To Do
priority: low
labels: [docs]
---

# Simple tasks don't need workflow_step
# They use basic kanban: To Do → In Progress → Done
```

**Board Display:**
```
[To Do] │ Fix typo in README
        │ labels: docs
```

---

### Example 2: Full SDD Workflow Task

```yaml
---
id: task-042
title: Implement OAuth2 authentication
status: In Progress
workflow_step: Planned
workflow_feature: user-auth
priority: high
labels: [backend, security]
assignee: ["@backend-engineer"]
created: 2025-11-28
updated: 2025-11-30
---

# This task participates in /jpspec workflow
# Currently planned, ready for implementation
```

**Board Display:**
```
[In Progress] │ Implement OAuth2 authentication
              │ @backend-engineer  workflow:Planned
```

---

### Example 3: Task in Validation

```yaml
---
id: task-043
title: Add user profile page
status: In Review
workflow_step: Validated
workflow_feature: user-profile
priority: high
labels: [frontend]
assignee: ["@frontend-engineer"]
created: 2025-11-25
updated: 2025-11-30
---

# Implementation complete, QA validated
# Awaiting deployment
```

**Board Display:**
```
[In Review] │ Add user profile page
            │ @frontend-engineer  workflow:Validated
```

---

## Workflow Progression Examples

### Scenario 1: Happy Path (Full Workflow)

```
Day 1: Task Created
┌──────────────────────────────┐
│ status: To Do                │
│ workflow_step: (none)        │
└──────────────────────────────┘

Day 2: Assessment
┌──────────────────────────────┐
│ Run: /jpspec:assess          │
│ Result:                      │
│   status: In Progress        │
│   workflow_step: Assessed    │
└──────────────────────────────┘

Day 3: Specification
┌──────────────────────────────┐
│ Run: /jpspec:specify         │
│ Result:                      │
│   status: In Progress        │
│   workflow_step: Specified   │
└──────────────────────────────┘

Day 5: Planning (skip research)
┌──────────────────────────────┐
│ Run: /jpspec:plan            │
│ Result:                      │
│   status: In Progress        │
│   workflow_step: Planned     │
└──────────────────────────────┘

Day 8: Implementation
┌─────────────────────────────────────┐
│ Run: /jpspec:implement              │
│ Result:                             │
│   status: In Progress               │
│   workflow_step: In Implementation  │
└─────────────────────────────────────┘

Day 10: Validation
┌──────────────────────────────┐
│ Run: /jpspec:validate        │
│ Result:                      │
│   status: In Review          │
│   workflow_step: Validated   │
└──────────────────────────────┘

Day 11: Deployment
┌──────────────────────────────┐
│ Run: /jpspec:operate         │
│ Result:                      │
│   status: Done               │
│   workflow_step: Deployed    │
└──────────────────────────────┘

Day 12: Complete
┌──────────────────────────────┐
│ Manual: Mark as Done         │
│ Result:                      │
│   status: Done               │
│   workflow_step: Done        │
└──────────────────────────────┘
```

---

### Scenario 2: Rework During Implementation

```
Day 1-5: Implementation in progress
┌─────────────────────────────────────┐
│ status: In Progress                 │
│ workflow_step: In Implementation    │
└─────────────────────────────────────┘

Day 6: Discover design issues during coding
┌──────────────────────────────────────────────────┐
│ Manual rework transition:                        │
│   backlog task edit task-042 --workflow-step     │
│                              Planned              │
│ Result:                                          │
│   status: In Progress                            │
│   workflow_step: Planned                         │
│   (needs architecture refinement)                │
└──────────────────────────────────────────────────┘

Day 7: Update architecture
┌──────────────────────────────────┐
│ Re-run: /jpspec:plan             │
│ (updates ADRs)                   │
└──────────────────────────────────┘

Day 8: Resume implementation
┌─────────────────────────────────────┐
│ Re-run: /jpspec:implement           │
│ Result:                             │
│   status: In Progress               │
│   workflow_step: In Implementation  │
└─────────────────────────────────────┘
```

---

### Scenario 3: Validation Failure

```
Day 1: Submit for validation
┌──────────────────────────────┐
│ status: In Review            │
│ workflow_step: Validated     │
└──────────────────────────────┘

Day 2: Security scan finds vulnerabilities
┌──────────────────────────────────────────────────┐
│ Manual rework transition:                        │
│   backlog task edit task-042 --workflow-step     │
│                              "In Implementation"  │
│ Result:                                          │
│   status: In Progress                            │
│   workflow_step: In Implementation               │
│   (needs security fixes)                         │
└──────────────────────────────────────────────────┘

Day 3: Fix vulnerabilities and re-validate
┌──────────────────────────────┐
│ Re-run: /jpspec:validate     │
│ Result:                      │
│   status: In Review          │
│   workflow_step: Validated   │
└──────────────────────────────┘
```

---

## Board View Examples

### Simple 3-Column Board (No Workflow Steps)

```
┌─────────────┬──────────────────┬────────────┐
│   To Do     │  In Progress     │    Done    │
├─────────────┼──────────────────┼────────────┤
│             │                  │            │
│ task-001    │ task-002         │ task-005   │
│ Fix typo    │ Update deps      │ Add CI     │
│             │                  │            │
│ task-003    │ task-004         │            │
│ Refactor X  │ Add tests        │            │
│             │                  │            │
└─────────────┴──────────────────┴────────────┘
```

---

### SDD Workflow Board (With Workflow Steps)

```
┌────────────────┬─────────────────────────┬──────────────┬────────────┐
│    To Do       │     In Progress         │  In Review   │    Done    │
├────────────────┼─────────────────────────┼──────────────┼────────────┤
│                │                         │              │            │
│ task-001       │ task-042                │ task-044     │ task-050   │
│ New feature    │ Implement OAuth         │ User profile │ Search API │
│                │ @backend                │ @frontend    │            │
│                │ workflow:Planned        │ workflow:    │ workflow:  │
│                │                         │ Validated    │ Deployed   │
│                │                         │              │            │
│                │ task-043                │              │            │
│                │ Add rate limiting       │              │            │
│                │ @backend                │              │            │
│                │ workflow:In             │              │            │
│                │ Implementation          │              │            │
│                │                         │              │            │
│                │ task-045                │              │            │
│                │ Design analytics        │              │            │
│                │ @architect              │              │            │
│                │ workflow:Researched     │              │            │
│                │                         │              │            │
└────────────────┴─────────────────────────┴──────────────┴────────────┘
```

---

## Filtering and Querying

### List Tasks by Workflow Step

```bash
# All tasks in Planning phase
backlog task list --filter "workflow_step:Planned" --plain

# All tasks in Implementation
backlog task list --filter "workflow_step:In Implementation" --plain

# All tasks ready for deployment
backlog task list --filter "workflow_step:Validated" --plain
```

### Find Tasks Needing Specific Workflow

```bash
# Tasks that need /jpspec:implement
backlog task list --filter "workflow_step:Planned" --plain

# Tasks that need /jpspec:validate
backlog task list --filter "workflow_step:In Implementation" --plain

# Tasks that need /jpspec:operate
backlog task list --filter "workflow_step:Validated" --plain
```

---

## Custom Board Configurations

### Example 1: Startup (Minimal Process)

```yaml
# backlog/config.yml
statuses: ["Backlog", "Active", "Done"]

workflow_step_mappings:
  "To Do": "Backlog"
  "Assessed": "Backlog"
  "Specified": "Active"
  "Planned": "Active"
  "In Implementation": "Active"
  "Validated": "Done"
  "Deployed": "Done"
  "Done": "Done"
```

**Board:**
```
┌───────────┬────────────────┬────────┐
│  Backlog  │    Active      │  Done  │
└───────────┴────────────────┴────────┘
```

---

### Example 2: Enterprise (Detailed Governance)

```yaml
# backlog/config.yml
statuses: ["Proposed", "Analysis", "Design", "Build", "Test", "Deploy", "Live"]

workflow_step_mappings:
  "To Do": "Proposed"
  "Assessed": "Analysis"
  "Specified": "Analysis"
  "Researched": "Analysis"
  "Planned": "Design"
  "In Implementation": "Build"
  "Validated": "Test"
  "Deployed": "Deploy"
  "Done": "Live"
```

**Board:**
```
┌──────────┬──────────┬────────┬───────┬──────┬────────┬──────┐
│ Proposed │ Analysis │ Design │ Build │ Test │ Deploy │ Live │
└──────────┴──────────┴────────┴───────┴──────┴────────┴──────┘
```

---

## State Transition Validation

### Valid Transitions

```
✓ To Do → Assessed           (via /jpspec:assess)
✓ Assessed → Specified       (via /jpspec:specify)
✓ Specified → Researched     (via /jpspec:research)
✓ Specified → Planned        (via /jpspec:plan, skip research)
✓ Researched → Planned       (via /jpspec:plan)
✓ Planned → In Implementation (via /jpspec:implement)
✓ In Implementation → Validated (via /jpspec:validate)
✓ Validated → Deployed       (via /jpspec:operate)
✓ Deployed → Done            (manual)

✓ In Implementation → Planned (rework)
✓ Validated → In Implementation (rework)
✓ Deployed → Validated       (rollback)
```

### Invalid Transitions (Blocked)

```
✗ To Do → In Implementation
  Error: Cannot skip planning phase

✗ Specified → Validated
  Error: Cannot validate without implementation

✗ Planned → Deployed
  Error: Cannot deploy without implementation and validation

✗ Assessed → Deployed
  Error: Invalid workflow progression
```

---

## CLI Command Examples

### Creating Task with Workflow Step

```bash
# Create task and set workflow step
backlog task create "Implement user authentication" \
  --ac "OAuth2 provider integration" \
  --ac "Session management" \
  --ac "Password reset flow" \
  --priority high \
  --labels backend,security \
  --set-field workflow_step="To Do" \
  --set-field workflow_feature="user-auth"
```

### Updating Workflow Step

```bash
# Manual workflow step update (use with caution)
backlog task edit task-042 --set-field workflow_step="Planned"

# Better: Let /jpspec commands update automatically
/jpspec:plan
```

### Viewing Workflow Status

```bash
# View single task with workflow details
backlog task task-042 --plain

# Output:
# Task task-042 - Implement user authentication
# Status: In Progress
# Workflow Step: Planned
# Feature: user-auth
# Priority: high
# ...
```

### Synchronizing States

```bash
# Check and fix status/workflow_step alignment
backlog workflow-sync

# Output:
# Synchronization complete:
#   Updated: 3
#   Already aligned: 15
#   Skipped (no workflow_step): 7
#
# Updated tasks:
#   - task-042: updated status to In Progress
#   - task-043: updated status to In Review
#   - task-044: updated status to Done
```

---

## Troubleshooting Visuals

### Problem: Status and Workflow Step Misaligned

**Before:**
```
Task task-042
├─ status: Done              ← Board shows Done
└─ workflow_step: Planned    ← But workflow is still Planned
```

**After `backlog workflow-sync`:**
```
Task task-042
├─ status: In Progress       ← Fixed to match workflow step
└─ workflow_step: Planned    ← Still Planned (correct)
```

---

### Problem: Cannot Execute Workflow

**Scenario:**
```bash
$ /jpspec:implement

Error: Cannot execute implement on task-042
Current state: Specified
Valid input states: Planned

Hint: Run /jpspec:plan first
```

**Solution Flow:**
```
┌────────────┐
│ Specified  │  Current state
└──────┬─────┘
       │
       │ Need: /jpspec:plan
       ▼
┌─────────┐
│ Planned │  Required state
└────┬────┘
     │
     │ Now can: /jpspec:implement
     ▼
┌────────────────────┐
│ In Implementation  │  Target state
└────────────────────┘
```

---

## Integration Architecture

### Component Interaction

```
┌─────────────────────────────────────────────────────────────┐
│                    /JPSPEC COMMAND                          │
│                   (e.g., /jpspec:implement)                 │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ 1. Validate current state
                        ▼
┌───────────────────────────────────────────────────────────┐
│              WorkflowConfig.get_input_states()            │
│         (checks if current state valid for workflow)      │
└───────────────────────┬───────────────────────────────────┘
                        │
                        │ 2. Execute workflow logic
                        │    (create artifacts, run agents)
                        ▼
┌───────────────────────────────────────────────────────────┐
│         WorkflowStateSynchronizer.update_task()           │
│  (updates workflow_step, status, workflow_feature)       │
└───────────────────────┬───────────────────────────────────┘
                        │
                        │ 3. Write to disk
                        ▼
┌───────────────────────────────────────────────────────────┐
│              BacklogWriter.write_task()                   │
│         (persists updated YAML frontmatter)               │
└───────────────────────────────────────────────────────────┘
```

---

## Summary

### Key Takeaways

1. **Two-Level Model** - Board status for organization, workflow step for lifecycle tracking
2. **Optional Feature** - Simple tasks don't need workflow_step
3. **Automatic Updates** - `/jpspec` commands handle workflow_step changes
4. **Validation** - System prevents invalid state transitions
5. **Backward Compatible** - Existing workflows unaffected

### Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│             WORKFLOW STEP QUICK REFERENCE                │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ Field: workflow_step                                     │
│ Purpose: Track lifecycle phase                           │
│ Values: To Do, Assessed, Specified, Researched,          │
│         Planned, In Implementation, Validated,           │
│         Deployed, Done                                   │
│                                                          │
│ Field: workflow_feature                                  │
│ Purpose: Link to feature spec                            │
│ Values: Feature slug (e.g., "user-auth")                 │
│                                                          │
│ Commands:                                                │
│   backlog task task-042 --plain                          │
│   backlog workflow-sync                                  │
│   backlog workflow-validate task-042 implement           │
│                                                          │
│ Automatic Updates:                                       │
│   /jpspec:assess    → Assessed                           │
│   /jpspec:specify   → Specified                          │
│   /jpspec:research  → Researched                         │
│   /jpspec:plan      → Planned                            │
│   /jpspec:implement → In Implementation                  │
│   /jpspec:validate  → Validated                          │
│   /jpspec:operate   → Deployed                           │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## References

- [ADR-002: Workflow Step Tracking Architecture](../adr/ADR-002-workflow-step-tracking-architecture.md)
- [Workflow Step Implementation Guide](./workflow-step-implementation-guide.md)
- [jpspec_workflow.yml](../../jpspec_workflow.yml)
- [Backlog User Guide](./backlog-user-guide.md)
