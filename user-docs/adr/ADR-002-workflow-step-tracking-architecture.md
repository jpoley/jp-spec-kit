# ADR-002: Workflow Step Tracking Architecture for Backlog.md

**Status:** Proposed
**Date:** 2025-11-30
**Author:** Enterprise Software Architect
**Context:** flowspec workflow integration

---

## Strategic Context (Penthouse View)

### Business Problem

Flowspec orchestrates complex software development workflows through `/flowspec` commands (assess, specify, research, plan, implement, validate, operate). Currently, backlog.md tasks use simple statuses ("To Do", "In Progress", "Done") that don't reflect **which workflow phase** a task is in.

**The Core Tension:** Developers need visibility into workflow progression without cluttering their task board with 9+ status columns.

### Business Value

**Primary Value Streams:**

1. **Developer Experience** - Engineers see at a glance which workflow phase each task is in
2. **Workflow Orchestration** - `/flowspec` commands can enforce state-based preconditions
3. **Progress Transparency** - Stakeholders understand where work is in the development lifecycle
4. **Compliance Tracking** - For regulated industries, workflow phase tracking provides audit trail

**Success Metrics:**

- Reduced confusion about task state (measured by Slack/issue questions)
- Increased adoption of `/flowspec` workflow commands (usage metrics)
- Zero invalid state transitions (constraint enforcement)

---

## Architectural Decision

### The Hohpe Lens: Two-Level State Model

After analyzing the problem through Hohpe's architectural lens, I recommend **Option D: Hybrid Two-Level State Model**.

```
┌─────────────────────────────────────────────────────────┐
│ BACKLOG.MD TASK                                         │
├─────────────────────────────────────────────────────────┤
│ Status: In Progress  ◄── Board Column (User-Visible)   │
│ Workflow Step: Planned  ◄── Phase Metadata (Detailed)  │
└─────────────────────────────────────────────────────────┘
```

**Rationale:** This follows Hohpe's principle of **"Levels of Abstraction"** - the board shows developer-friendly statuses while metadata tracks precise workflow phases.

### Decision: Hybrid Two-Level Model

**Implementation:**

1. **Board Statuses (3-5 columns)** - Keep simple, developer-friendly:
   - "To Do" (not started)
   - "In Progress" (actively working)
   - "In Review" (validation/approval)
   - "Done" (complete)

2. **Workflow Steps (metadata field)** - Track precise workflow phase:
   - Stored in YAML frontmatter: `workflow_step: Planned`
   - Maps to `flowspec_workflow.yml` states
   - Updated automatically by `/flowspec` commands
   - Optional for simple workflows (backward compatible)

3. **Visual Indicators** - TUI shows workflow step as label/tag:
   ```
   [In Progress] │ Implement auth service
                 │ @backend  workflow:Planned
   ```

---

## Engine Room View: Technical Architecture

### Data Model Changes

**Task YAML Frontmatter:**

```yaml
---
id: task-042
title: Implement authentication service
status: In Progress
workflow_step: Planned              # NEW FIELD (optional)
workflow_feature: user-auth         # NEW FIELD - links to feature spec
labels: [backend, security]
assignee: ["@backend-engineer"]
created: 2025-11-28
priority: high
---
```

**Key Design Decisions:**

1. **Optional Field** - `workflow_step` is OPTIONAL for backward compatibility
2. **Separate from Status** - Decouples board organization from workflow progression
3. **Feature Linking** - `workflow_feature` enables artifact validation (e.g., "can't implement without ADR")

### State Synchronization

```python
# src/specify_cli/workflow/sync.py

class WorkflowStateSynchronizer:
    """Synchronizes backlog.md status with flowspec workflow steps."""

    def update_task_workflow_step(
        self,
        task_id: str,
        workflow: str,
        feature: str
    ) -> None:
        """Update task workflow step after /flowspec command completes.

        Args:
            task_id: Backlog task ID
            workflow: Workflow name (e.g., "implement")
            feature: Feature slug for artifact validation

        Example:
            >>> sync.update_task_workflow_step(
            ...     "task-042",
            ...     "implement",
            ...     "user-auth"
            ... )
            # Sets workflow_step to "In Implementation"
            # Sets status to "In Progress" if still "To Do"
        """
        config = WorkflowConfig.load()

        # Get current task state
        task = self._load_task(task_id)
        current_step = task.get("workflow_step", "To Do")

        # Calculate next workflow step
        next_step = config.get_next_state(current_step, workflow)

        # Update task metadata
        updates = {
            "workflow_step": next_step,
            "workflow_feature": feature,
        }

        # Auto-update status if appropriate
        if task.status == "To Do" and next_step != "To Do":
            updates["status"] = "In Progress"

        self._update_task(task_id, updates)
```

### Integration with flowspec_workflow.yml

**Workflow configuration already defines states:**

```yaml
states:
  - "To Do"
  - "Assessed"
  - "Specified"
  - "Researched"
  - "Planned"
  - "In Implementation"
  - "Validated"
  - "Deployed"
  - "Done"
```

**Mapping to Board Statuses:**

```python
# Automatic mapping logic
WORKFLOW_STEP_TO_STATUS = {
    "To Do": "To Do",
    "Assessed": "In Progress",
    "Specified": "In Progress",
    "Researched": "In Progress",
    "Planned": "In Progress",
    "In Implementation": "In Progress",
    "Validated": "In Review",
    "Deployed": "Done",
    "Done": "Done",
}
```

---

## Architecture Decision Records (ADRs)

### Options Considered

#### Option A: Expand Board Columns to Match Workflow States

**Approach:** Use all 9 flowspec workflow states as board columns.

**Pros:**
- Direct 1:1 mapping
- No additional metadata needed
- Clear visual separation

**Cons:**
- Board becomes cluttered (9 columns vs. typical 3-4)
- Horizontal scrolling required
- Poor UX for terminal interface
- Forces all projects to use full workflow

**Hohpe Assessment:** Violates "Simplicity" principle - complexity leak from domain model into UI.

---

#### Option B: Workflow Step as Metadata Field Only

**Approach:** Add `workflow_step` field, keep existing statuses unchanged.

**Pros:**
- Maximum flexibility
- Backward compatible
- Clean separation of concerns

**Cons:**
- Workflow step not visible on board without extra UI
- No enforcement of status/step alignment
- Potential confusion about which field is "truth"

**Hohpe Assessment:** Good separation but lacks visual feedback - "levels without bridges."

---

#### Option C: Labels for Workflow Phase

**Approach:** Use labels like `workflow:Planned`, `workflow:Validated`.

**Pros:**
- No schema changes
- Works with existing label system
- Filterable/searchable

**Cons:**
- Label namespace pollution
- Manual management (error-prone)
- Labels are multi-valued (workflow step should be single)
- No semantic validation

**Hohpe Assessment:** "Making things fit" anti-pattern - using labels for state management.

---

#### Option D: Hybrid Two-Level Model (RECOMMENDED)

**Approach:** Board statuses (3-4) for visual organization + `workflow_step` metadata for precise tracking.

**Pros:**
- Best of both worlds: simple board + detailed tracking
- Backward compatible (workflow_step optional)
- Supports both simple and complex workflows
- Clear separation: status = organization, workflow_step = lifecycle phase
- Visual indicators in TUI without clutter

**Cons:**
- Two fields to maintain (mitigated by auto-sync)
- Requires documentation for developers

**Hohpe Assessment:**
- **Levels of Abstraction** ✓ - Board vs. metadata separation
- **Composability** ✓ - Optional workflow tracking layers on top of basic board
- **Consistency** ✓ - Single source of truth (flowspec_workflow.yml)
- **Consumption** ✓ - Simple default, power when needed

---

## Platform Quality Assessment (7 C's)

### 1. Clarity

**Rating: 8/10**

- Developer mental model: "Status is where it lives on the board, workflow step is where it is in the lifecycle"
- Clear documentation needed for workflow_step vs. status distinction
- Visual indicators provide immediate context

**Improvement:** Add inline help in TUI: "Press ? for workflow step explanations"

### 2. Consistency

**Rating: 9/10**

- Single source of truth: `flowspec_workflow.yml` defines all workflow steps
- Automatic synchronization prevents drift
- Follows existing backlog.md patterns (optional metadata fields)

**Improvement:** Add config validation on `backlog task edit` commands

### 3. Composability

**Rating: 10/10**

- Works with simple workflows (no workflow_step needed)
- Works with complex SDD workflows (full tracking)
- Integrates with existing label/assignee system
- Feature linking enables artifact validation

**Example:** Research phase is optional - tasks can skip from Specified → Planned

### 4. Consumption (Developer Experience)

**Rating: 7/10**

**Easy:**
- Board view stays simple (3-4 columns)
- Workflow steps auto-update via `/flowspec` commands
- Visual tags show current phase

**Needs Work:**
- New field to learn (workflow_step vs. status)
- Confusion risk if manual edits misalign status/step

**Mitigation:** Add `backlog workflow sync` command to fix misalignments

### 5. Correctness (Validation)

**Rating: 9/10**

- Workflow steps validated against flowspec_workflow.yml states
- State transitions validated against allowed workflows
- Prevents invalid state changes

**Example Validation:**
```python
# In /flow:implement command
if task.workflow_step != "Planned":
    raise WorkflowError(
        f"Cannot implement from {task.workflow_step}. "
        f"Task must be in 'Planned' state."
    )
```

### 6. Completeness

**Rating: 8/10**

**Covers:**
- All workflow states from flowspec_workflow.yml
- Backward transitions (rework scenarios)
- Optional workflows (research, operate)
- Terminal states (Done, Deployed)

**Missing (Future):**
- Multi-task workflow coordination (batching)
- Workflow step history/audit trail
- Rollback automation

### 7. Changeability

**Rating: 9/10**

- Adding workflow states: Just update flowspec_workflow.yml
- Changing board columns: Just update backlog/config.yml statuses
- Custom project workflows: Override default mappings

**Example:**
```yaml
# project-specific backlog/config.yml
statuses: ["Backlog", "Active", "Review", "Shipped"]

workflow_step_mappings:
  "In Implementation": "Active"
  "Validated": "Review"
```

---

## Constitutional Principles (For memory/constitution.md)

### Principle 1: Workflow Step Tracking Standards

**Mandate:** All tasks participating in `/flowspec` workflows MUST track `workflow_step` metadata.

**Rationale:** Enables state-based workflow enforcement and artifact validation.

**Implementation:**
- `/flowspec` commands automatically set workflow_step
- Manual task creation can omit workflow_step (for simple tasks)
- `backlog workflow validate` command checks alignment

### Principle 2: State Machine Integration

**Mandate:** All workflow steps MUST be defined in `flowspec_workflow.yml`.

**Rationale:** Single source of truth prevents configuration drift.

**Implementation:**
- WorkflowConfig.load() validates all states on startup
- Invalid workflow_step values rejected with clear error message
- Schema validation enforces state existence

### Principle 3: Backward Compatibility

**Mandate:** Workflow step tracking MUST be optional.

**Rationale:** Not all projects use full SDD workflow; simple kanban boards should work unchanged.

**Implementation:**
- workflow_step field is optional in task schema
- Tasks without workflow_step treated as simple kanban
- TUI gracefully handles missing workflow_step (shows nothing)

### Principle 4: Automatic Synchronization

**Mandate:** Workflow steps MUST auto-update via `/flowspec` commands.

**Rationale:** Manual maintenance is error-prone and defeats automation purpose.

**Implementation:**
- Each `/flowspec` command updates workflow_step via WorkflowStateSynchronizer
- Status auto-updated if transitioning from "To Do"
- Feature linking (`workflow_feature`) enables artifact validation

---

## Migration Strategy

### Phase 1: Foundation (v0.0.150)

**Scope:** Add optional workflow_step field support

- [ ] Add `workflow_step` to task schema (optional)
- [ ] Add `workflow_feature` to task schema (optional)
- [ ] Implement WorkflowStateSynchronizer class
- [ ] Update backlog CLI to display workflow_step in task view
- [ ] Add TUI visual indicators (labels/tags)

**Risk:** Low - purely additive changes

### Phase 2: Integration (v0.0.155)

**Scope:** Integrate with `/flowspec` commands

- [ ] Update `/flow:assess` to set workflow_step = "Assessed"
- [ ] Update `/flow:specify` to set workflow_step = "Specified"
- [ ] Update `/flow:plan` to set workflow_step = "Planned"
- [ ] Update `/flow:implement` to set workflow_step = "In Implementation"
- [ ] Update `/flow:validate` to set workflow_step = "Validated"
- [ ] Update `/flow:operate` to set workflow_step = "Deployed"

**Risk:** Medium - requires coordination with task-090, task-091

### Phase 3: Validation (v0.0.160)

**Scope:** Add workflow state enforcement

- [ ] Implement workflow precondition checks (e.g., can't implement without plan)
- [ ] Add artifact validation (e.g., check for ADR before implement)
- [ ] Add `backlog workflow validate` command
- [ ] Add `backlog workflow sync` command for manual fixes

**Risk:** Medium - may reveal existing state inconsistencies

### Phase 4: Documentation (v0.0.165)

**Scope:** Complete task-095 documentation

- [ ] Create docs/guides/workflow-state-mapping.md
- [ ] Update CLAUDE.md with workflow_step guidance
- [ ] Add troubleshooting guide
- [ ] Create developer training materials

**Risk:** Low - documentation only

---

## Implementation Guidance

### For Task-090 (WorkflowConfig)

**WorkflowConfig already exists** (see src/specify_cli/workflow/config.py). This task is DONE but unmarked.

**Required additions:**

```python
def get_workflow_step_status_mapping(self) -> dict[str, str]:
    """Get default mapping from workflow steps to board statuses.

    Returns:
        Dictionary mapping workflow step names to status names.

    Example:
        >>> config.get_workflow_step_status_mapping()
        {'Planned': 'In Progress', 'Validated': 'In Review', ...}
    """
    # Could be defined in flowspec_workflow.yml or use smart defaults
```

### For Task-091 (Workflow Validation)

**WorkflowValidator needs workflow_step validation:**

```python
def validate_task_workflow_step(
    self,
    task: dict,
    config: WorkflowConfig
) -> tuple[bool, list[str]]:
    """Validate task workflow_step is valid and consistent.

    Checks:
    1. workflow_step exists in config.states
    2. status aligns with workflow_step (if mapping defined)
    3. Required artifacts exist for current workflow_step

    Returns:
        (is_valid, error_messages)
    """
```

### For Task-095 (Documentation)

**Key documentation sections:**

1. **Concept Overview** - Two-level model explanation
2. **State Mapping Table** - Workflow step → board status
3. **Manual Task Creation** - When to use workflow_step
4. **Troubleshooting** - Fixing misaligned states
5. **Custom Workflows** - Override mappings per project

---

## Risks and Mitigations

### Risk 1: Developer Confusion (Status vs. Workflow Step)

**Likelihood:** Medium
**Impact:** Medium

**Mitigation:**
- Clear naming: "status" = board column, "workflow_step" = lifecycle phase
- Visual distinction in TUI (status in column, workflow_step as tag)
- Documentation with examples
- Inline help in TUI

### Risk 2: State Drift (Manual Edits)

**Likelihood:** Medium
**Impact:** Low

**Mitigation:**
- `backlog workflow sync` command to detect and fix
- Validation in `/flowspec` commands before execution
- Periodic automated checks in CI

### Risk 3: Complexity Creep

**Likelihood:** Low
**Impact:** High

**Mitigation:**
- Keep workflow_step OPTIONAL
- Simple projects ignore this feature entirely
- Progressive disclosure: only visible when used

### Risk 4: Performance (Additional Metadata)

**Likelihood:** Low
**Impact:** Low

**Mitigation:**
- Workflow_step is lightweight (single string field)
- Indexed in backlog.md parser
- No performance impact on TUI rendering

---

## Alternatives Considered and Rejected

### Custom Board Columns Per Project

**Idea:** Let each project define custom columns matching their workflow.

**Why Rejected:**
- Violates DRY (flowspec_workflow.yml already defines states)
- Configuration complexity explosion
- Hard to share tasks across projects
- Hohpe: "Flexibility at wrong layer" - this is workflow config, not UI config

### Workflow Step as Substatus

**Idea:** Make workflow_step a sub-property of status.

**Why Rejected:**
- Complicates data model
- Hard to query independently
- Doesn't align with backlog.md flat structure
- Hohpe: "Premature hierarchical modeling"

### State History Tracking

**Idea:** Track full workflow_step history in task metadata.

**Why Rejected:**
- Out of scope for initial implementation
- Git history already provides audit trail
- Adds complexity without immediate value
- Can be added later if needed (Phase 5+)

---

## Success Criteria

**Objective Measures:**

1. **Zero Breaking Changes** - All existing tasks work unchanged
2. **Performance** - No measurable TUI rendering slowdown (<5ms per task)
3. **Adoption** - 80%+ of `/flowspec` workflow tasks use workflow_step within 2 months
4. **Error Rate** - <5% invalid state transitions (measured via validation errors)

**Subjective Measures:**

1. **Developer Feedback** - Positive sentiment in retrospectives
2. **Reduced Questions** - Fewer "where is this task?" questions in Slack
3. **Increased Workflow Usage** - More projects adopt full `/flowspec` workflow

---

## References

### Hohpe's Architectural Principles Applied

1. **Levels of Abstraction** - Board status (simple) vs. workflow step (detailed)
2. **Composition over Configuration** - Layered approach (basic + optional workflow)
3. **Single Source of Truth** - flowspec_workflow.yml defines all workflow states
4. **Fail Fast** - Validate workflow steps early (on task edit, before /flowspec execution)
5. **Progressive Disclosure** - Simple default (no workflow_step), power when needed

### Related Documents

- `flowspec_workflow.yml` - Authoritative workflow state definitions
- `backlog/config.yml` - Board column configuration
- `docs/reference/agent-loop-classification.md` - Inner/outer loop agents
- `docs/reference/artifact-path-patterns.md` - Artifact validation patterns

### Related Tasks

- task-090: Implement WorkflowConfig Python class (ACTUALLY DONE - needs status update)
- task-091: Implement workflow validation logic
- task-095: Document backlog.md state mapping
- task-096: Update /flowspec commands to check workflow constraints
- task-182: Extend flowspec init to configure transition validation modes

---

## Decision

**APPROVED for implementation as Option D: Hybrid Two-Level Model**

**Next Steps:**

1. Create implementation task for workflow_step field addition
2. Update task-090 status to Done (WorkflowConfig already implemented)
3. Coordinate with task-091 for validation integration
4. Schedule Phase 1 implementation for v0.0.150

**Review Date:** 2025-12-15 (after Phase 1 complete)

---

*This ADR follows Gregor Hohpe's architectural philosophy: strategic framing (why), engine room details (how), quality assessment (verification), and constitutional principles (governance).*
