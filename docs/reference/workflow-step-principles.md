# Workflow Step Tracking - Constitutional Principles

**Authority:** Architectural Governance
**Scope:** Flowspec workflow integration
**Related:** [ADR-002](../adr/ADR-002-workflow-step-tracking-architecture.md)

---

## Purpose

This document defines the non-negotiable principles governing workflow step tracking in Flowspec. These principles ensure consistency, reliability, and maintainability of the workflow state machine integration.

**Principle Source:** Gregor Hohpe's architectural philosophy applied to workflow orchestration.

---

## Principle 1: Single Source of Truth

### Statement

**`flowspec_workflow.yml` is the ONLY authoritative source for workflow states and transitions.**

### Rationale

Multiple sources of truth create inconsistency, drift, and maintenance burden. The workflow configuration must be the canonical definition that all other systems reference.

### Implementation Requirements

1. **WorkflowConfig class** MUST load states from `flowspec_workflow.yml`
2. **No hardcoded states** in Python code, CLI commands, or TUI rendering
3. **Validation logic** MUST query WorkflowConfig, never duplicate state lists
4. **Custom board columns** MAY map workflow steps to different status names, but workflow steps themselves come from flowspec_workflow.yml

### Violations

❌ **PROHIBITED:**
```python
# Hardcoded state list
VALID_STATES = ["To Do", "Planned", "In Implementation"]

# Duplicated workflow logic
if status == "Planned":
    next_status = "In Implementation"
```

✅ **REQUIRED:**
```python
# Load from canonical source
config = WorkflowConfig.load()
valid_states = config.all_states

# Query workflow logic
next_state = config.get_next_state(current_state, workflow)
```

### Verification

```bash
# Audit: Find hardcoded state references
rg -i "to do|planned|validated" --type py | grep -v "test" | grep -v "config.py"

# Should return minimal results (only test fixtures, docstrings)
```

---

## Principle 2: Optional Workflow Participation

### Statement

**Workflow step tracking MUST be optional. Simple tasks MUST work without workflow metadata.**

### Rationale

Not all projects use full SDD workflows. Forcing workflow participation creates unnecessary complexity and reduces adoption. The system must gracefully handle both simple kanban and complex workflow scenarios.

### Implementation Requirements

1. **`workflow_step` field** is OPTIONAL in task schema
2. **`workflow_feature` field** is OPTIONAL in task schema
3. **Default behavior** when fields absent: Treat as simple kanban task
4. **TUI rendering** gracefully handles None values (no display if absent)
5. **CLI commands** work identically for tasks with and without workflow_step
6. **No warnings or errors** for tasks lacking workflow metadata

### Examples

✅ **Valid Simple Task:**
```yaml
---
id: task-001
title: Fix typo in README
status: To Do
---
# No workflow_step - perfectly valid
```

✅ **Valid Workflow Task:**
```yaml
---
id: task-042
title: Implement OAuth2
status: In Progress
workflow_step: Planned
workflow_feature: user-auth
---
```

### Anti-Pattern

❌ **PROHIBITED:** Requiring workflow_step for all tasks
```python
# Bad: Forces workflow participation
if not task.workflow_step:
    raise ValueError("Task must have workflow_step")
```

✅ **REQUIRED:** Graceful handling
```python
# Good: Optional workflow tracking
if task.workflow_step:
    display_workflow_indicator(task.workflow_step)
```

### Verification

```bash
# Test: Create simple task without workflow fields
backlog task create "Simple task" --ac "Works"

# Should succeed without errors or warnings
```

---

## Principle 3: Automatic State Synchronization

### Statement

**Workflow steps MUST be updated automatically by `/flowspec` commands. Manual updates are allowed but discouraged.**

### Rationale

Manual state management is error-prone and defeats the purpose of workflow automation. The system should handle state transitions automatically based on workflow execution.

### Implementation Requirements

1. **Every `/flowspec` command** MUST call `WorkflowStateSynchronizer.update_task_workflow_step()`
2. **Updates happen** immediately after successful workflow execution
3. **Atomic updates** - workflow_step, status, and workflow_feature updated together
4. **Failure handling** - workflow step NOT updated if workflow execution fails
5. **Manual override available** - for exceptional cases and debugging

### Workflow Integration Pattern

```python
# Standard pattern for all /flowspec commands

try:
    # 1. Validate preconditions
    validator.validate_task_ready_for_workflow(task, workflow, feature)

    # 2. Execute workflow logic
    result = execute_workflow(task, workflow, feature)

    # 3. Update workflow step (only on success)
    sync = WorkflowStateSynchronizer()
    sync.update_task_workflow_step(
        task_id=task.task_id,
        workflow=workflow,
        feature=feature,
        auto_status=True
    )

except WorkflowError as e:
    # Workflow failed - do NOT update workflow_step
    log.error(f"Workflow failed: {e}")
    raise
```

### Manual Override (Exceptional Cases Only)

```bash
# Manual workflow step update - use with caution
backlog task edit task-042 --set-field workflow_step="Planned"

# Better: Let automation handle it
/flow:plan
```

### Verification

```bash
# Test: Workflow updates task state
backlog task create "Test task" --ac "Test" --set-field workflow_step="Specified"
/flow:plan  # Should set workflow_step to "Planned"
backlog task task-XXX --plain | grep "workflow_step: Planned"
```

---

## Principle 4: Fail-Fast Validation

### Statement

**Invalid workflow transitions MUST be rejected immediately with clear error messages.**

### Rationale

Failing fast prevents invalid states from propagating through the system. Clear error messages guide developers to correct usage patterns.

### Implementation Requirements

1. **Validation occurs** BEFORE workflow execution
2. **Clear error messages** explain what's wrong and how to fix it
3. **Suggested actions** provided when validation fails
4. **No partial updates** - workflow_step not changed if validation fails

### Error Message Standards

✅ **REQUIRED:** Clear, actionable errors
```
Error: Cannot execute /flow:implement on task-042

Current state: Specified
Required states: Planned

Suggested action: Run /flow:plan first to complete architecture planning.
```

❌ **PROHIBITED:** Vague errors
```
Error: Invalid state transition
```

### Validation Points

1. **Command entry** - Check workflow_step before executing `/flowspec` command
2. **Artifact validation** - Check required artifacts exist (if feature linked)
3. **State machine** - Verify transition exists in flowspec_workflow.yml
4. **Manual edits** - Validate workflow_step value when manually set

### Implementation Example

```python
def validate_task_ready_for_workflow(
    task: Task,
    workflow: str,
    feature: str | None
) -> tuple[bool, list[str]]:
    """Validate task ready for workflow execution."""
    errors = []
    config = WorkflowConfig.load()

    # Check workflow step
    current_step = task.workflow_step or "To Do"
    valid_inputs = config.get_input_states(workflow)

    if current_step not in valid_inputs:
        errors.append(
            f"Cannot execute {workflow} from state '{current_step}'. "
            f"Valid input states: {', '.join(valid_inputs)}. "
            f"Suggested action: Complete prerequisite workflows first."
        )

    # Check artifacts if feature linked
    if feature:
        missing_artifacts = check_required_artifacts(workflow, feature)
        if missing_artifacts:
            errors.append(
                f"Missing required artifacts: {', '.join(missing_artifacts)}. "
                f"Suggested action: Complete prerequisite workflows to generate artifacts."
            )

    return len(errors) == 0, errors
```

### Verification

```bash
# Test: Invalid transition rejected
backlog task create "Test" --ac "Test" --set-field workflow_step="To Do"
/flow:implement  # Should fail with clear error message

# Expected error:
# Cannot execute implement from state 'To Do'.
# Valid input states: Planned.
# Suggested action: Run /flow:plan first.
```

---

## Principle 5: Backward Compatibility

### Statement

**All changes MUST maintain backward compatibility with existing tasks and workflows.**

### Rationale

Breaking existing workflows destroys user trust and productivity. The system must evolve without invalidating existing work.

### Implementation Requirements

1. **Existing tasks** work unchanged (no workflow_step required)
2. **Existing CLI commands** continue to function identically
3. **Migration path** provided for adopting new features
4. **Deprecation warnings** given 2+ versions before removal
5. **Graceful degradation** when new features unavailable

### Compatibility Guarantees

✅ **GUARANTEED:** These continue to work
```bash
# Existing commands
backlog task create "Title" --ac "Criterion"
backlog task edit task-001 -s "In Progress"
backlog task list --plain

# Existing task format
---
id: task-001
title: Task
status: To Do
---
```

✅ **ADDITIVE:** New optional features
```bash
# New commands (optional to use)
backlog workflow-sync
backlog workflow-validate task-001 implement

# New fields (optional to include)
---
id: task-001
title: Task
status: To Do
workflow_step: Planned       # Optional
workflow_feature: auth       # Optional
---
```

### Migration Strategy

**Phase 1:** Add optional fields (no breaking changes)
**Phase 2:** Integrate with `/flowspec` (new functionality only)
**Phase 3:** Add validation (opt-in via config)
**Phase 4:** Document best practices (no enforcement)

### Anti-Pattern

❌ **PROHIBITED:** Breaking changes without migration path
```python
# Bad: Requires workflow_step immediately
class Task:
    def __init__(self, ..., workflow_step: str):  # Required!
        self.workflow_step = workflow_step
```

✅ **REQUIRED:** Graceful optional adoption
```python
# Good: Optional with sensible defaults
class Task:
    def __init__(self, ..., workflow_step: str | None = None):
        self.workflow_step = workflow_step
```

### Verification

```bash
# Test: Pre-existing tasks still work
# Create task using old format (no workflow fields)
cat > backlog/tasks/task-legacy.md <<EOF
---
id: task-legacy
title: Legacy task
status: To Do
---
Test
EOF

# Should work without errors
backlog task task-legacy --plain
backlog task edit task-legacy -s "In Progress"
```

---

## Principle 6: Observable State

### Statement

**All workflow state changes MUST be auditable and traceable.**

### Rationale

Workflow state changes affect downstream decisions. Audit trails enable debugging, compliance, and process improvement.

### Implementation Requirements

1. **Git commits** track all task file changes
2. **Timestamps** updated on every workflow_step change
3. **Commit messages** include workflow context
4. **State history** reconstructible from Git log
5. **Structured logging** for automated state changes

### Audit Trail Example

```bash
# Git history shows workflow progression
git log --oneline backlog/tasks/task-042.md

abc1234 workflow: transition task-042 to Validated via /flow:validate
def5678 workflow: transition task-042 to In Implementation via /flow:implement
ghi9012 workflow: transition task-042 to Planned via /flow:plan
```

### Logging Standards

```python
import logging
logger = logging.getLogger(__name__)

# Log workflow state transitions
logger.info(
    "Workflow state transition",
    extra={
        "task_id": task.task_id,
        "workflow": workflow,
        "from_state": current_step,
        "to_state": next_step,
        "feature": feature,
        "timestamp": datetime.now().isoformat(),
    }
)
```

### Commit Message Pattern

```bash
# Automated commits from /flowspec commands
git commit -m "workflow: transition task-042 to Planned via /flow:plan

Task: task-042 (Implement OAuth2 authentication)
Workflow: plan
Feature: user-auth
Previous state: Specified
New state: Planned

Generated artifacts:
- docs/adr/ADR-003-oauth2-architecture.md
- docs/platform/infrastructure-oauth2.md"
```

### Verification

```bash
# Query: Show all workflow transitions for task
git log --grep="task-042" --oneline backlog/tasks/task-042.md

# Query: Show all tasks in Planning phase today
git log --since="midnight" --grep="workflow: plan" --oneline
```

---

## Principle 7: Performance Efficiency

### Statement

**Workflow step tracking MUST NOT measurably degrade system performance.**

### Rationale

Performance degradation reduces developer experience and adoption. Workflow tracking is metadata, not the critical path - it must be lightweight.

### Performance Budgets

| Operation | Target | Maximum |
|-----------|--------|---------|
| Task parse (with workflow_step) | +0.1ms | +1ms |
| Task write (with workflow_step) | +0.5ms | +2ms |
| TUI render (100 tasks) | +1ms | +5ms |
| Workflow validation | +5ms | +20ms |
| State synchronization (all tasks) | +100ms | +500ms |

### Implementation Requirements

1. **Lazy loading** - WorkflowConfig loaded once, cached
2. **Minimal overhead** - Two optional string fields
3. **Indexed queries** - workflow_step indexed for filtering
4. **Batch operations** - Bulk sync more efficient than individual updates
5. **No blocking I/O** - Async where possible

### Performance Anti-Patterns

❌ **PROHIBITED:** Reloading config on every task
```python
# Bad: Loads config for every task in loop
for task in tasks:
    config = WorkflowConfig.load()  # Expensive!
    validate(task, config)
```

✅ **REQUIRED:** Load once, reuse
```python
# Good: Load once, cache, reuse
config = WorkflowConfig.load()  # Once
for task in tasks:
    validate(task, config)  # Reuse
```

### Verification

```bash
# Benchmark: Parse 100 tasks with workflow_step
hyperfine "backlog task list --limit 100"

# Target: <50ms total (0.5ms per task)
```

---

## Principle 8: Explicit Over Implicit

### Statement

**Workflow state transitions MUST be explicit and visible, never hidden or automatic without user action.**

### Rationale

Implicit state changes create confusion and reduce trust. Developers must know when and why states change.

### Implementation Requirements

1. **Transitions occur** only via explicit `/flowspec` command execution
2. **User confirmation** required for destructive transitions (rework, rollback)
3. **Clear feedback** provided after state changes
4. **No background automation** - state changes only during active workflows
5. **Manual triggers** for edge cases (rework, skip phases)

### Explicit Transition Pattern

```bash
# Explicit: User runs command, state updates
/flow:plan
# Output: Task task-042 transitioned: Specified → Planned

# Clear feedback about what changed
# Task: task-042
# Previous state: Specified
# New state: Planned
# Artifacts created:
#   - docs/adr/ADR-003-oauth2-architecture.md
```

### Anti-Pattern

❌ **PROHIBITED:** Implicit state changes
```python
# Bad: State changes without user action
if time.now() > deadline:
    task.workflow_step = "Planned"  # Silent automatic change
```

✅ **REQUIRED:** Explicit user-triggered transitions
```python
# Good: User explicitly runs workflow
if user_command == "/flow:plan":
    task.workflow_step = config.get_next_state(current, "plan")
    print(f"Transitioned {task.task_id}: {current} → {task.workflow_step}")
```

### Confirmation for Destructive Actions

```bash
# Rework transition - requires confirmation
backlog task edit task-042 --workflow-step Planned

# Prompt:
# WARNING: Task is currently in 'In Implementation'.
# Moving back to 'Planned' will require re-implementing.
# Continue? [y/N]:
```

### Verification

```bash
# Test: No automatic state changes
# Leave task idle for extended period
# Workflow step should NOT change without explicit command
```

---

## Principle 9: Composability

### Statement

**Workflow step tracking MUST compose with other backlog.md features without conflicts.**

### Rationale

Features must work together harmoniously. Workflow tracking is one dimension of task metadata - it shouldn't interfere with labels, assignees, priorities, etc.

### Composability Requirements

1. **Orthogonal features** - workflow_step independent of labels, assignees, priority
2. **Combined filtering** - Can filter by workflow_step AND label simultaneously
3. **No mutual exclusions** - All feature combinations valid
4. **Additive behavior** - workflow_step adds capabilities without removing others

### Composability Examples

✅ **Valid Compositions:**
```yaml
---
id: task-042
title: Implement OAuth2
status: In Progress
workflow_step: Planned
workflow_feature: user-auth
priority: high
labels: [backend, security, p0]
assignee: ["@backend-engineer", "@security-reviewer"]
milestone: v2.0
---
```

```bash
# Combined filtering works
backlog task list \
  --filter "workflow_step:Planned" \
  --filter "labels:backend" \
  --filter "priority:high"
```

### Anti-Pattern

❌ **PROHIBITED:** Feature conflicts
```python
# Bad: Workflow step blocks other features
if task.workflow_step:
    task.labels = []  # Clears labels! Conflict!
```

✅ **REQUIRED:** Orthogonal features
```python
# Good: Features coexist independently
task.workflow_step = "Planned"
task.labels.append("backend")  # Both work together
```

### Verification

```bash
# Test: All feature combinations
backlog task create "Test" \
  --ac "Test" \
  --priority high \
  --labels backend,security \
  --assignee @engineer \
  --set-field workflow_step="Planned" \
  --set-field workflow_feature="test"

# Should succeed without conflicts or warnings
```

---

## Principle 10: Progressive Disclosure

### Statement

**Complexity should be revealed progressively. Simple use cases remain simple, advanced features available when needed.**

### Rationale

Overwhelming users with all features upfront reduces adoption. Start simple, grow into complexity as needed.

### Progressive Disclosure Levels

**Level 1: Basic Kanban (No Workflow)**
```bash
backlog task create "Fix bug" --ac "Works"
backlog task edit task-001 -s "In Progress"
backlog task edit task-001 -s "Done"
```
*User sees:* Simple 3-column board, no workflow concepts

**Level 2: Automated Workflow (Transparent)**
```bash
/flow:specify
/flow:plan
/flow:implement
```
*User sees:* Workflow steps auto-update, minimal cognitive load

**Level 3: Advanced Workflow Management**
```bash
backlog workflow-validate task-042 implement
backlog workflow-sync
backlog task edit task-042 --workflow-step Planned
```
*User sees:* Full control, validation, manual overrides

### UI Progressive Disclosure

**TUI Level 1:** Basic board view (no workflow indicators)
**TUI Level 2:** Workflow step tags (when present)
**TUI Level 3:** Detailed workflow view with artifact links

### Documentation Progressive Disclosure

**Quick Start:** Ignore workflow_step entirely
**User Guide:** Introduce workflow_step with simple examples
**Advanced Guide:** Full state machine, manual overrides, troubleshooting

### Anti-Pattern

❌ **PROHIBITED:** Exposing all complexity upfront
```bash
# Bad: Forces users to learn everything immediately
backlog task create "Title" \
  --ac "Test" \
  --workflow-step "To Do" \           # Not needed for beginners
  --workflow-feature "feature" \      # Not needed for beginners
  --transition-validation NONE \      # Overwhelming
  --artifact-path ./docs/prd/...      # Overwhelming
```

✅ **REQUIRED:** Simple default, grow into complexity
```bash
# Good: Simple default
backlog task create "Title" --ac "Test"

# Good: Advanced features opt-in
backlog task create "Title" \
  --ac "Test" \
  --set-field workflow_step="To Do" \  # Optional advanced feature
  --set-field workflow_feature="auth"  # Optional advanced feature
```

### Verification

```bash
# Test: Complete workflow without advanced features
backlog task create "Simple task" --ac "Works"
backlog task edit task-XXX -s "In Progress"
backlog task edit task-XXX -s "Done"

# Should work without mentioning workflow_step once
```

---

## Principle Enforcement

### Automated Checks

```bash
# CI pipeline checks
.github/workflows/validate-principles.yml

jobs:
  validate-principles:
    runs-on: ubuntu-latest
    steps:
      - name: Check for hardcoded states
        run: |
          ! rg -i '"to do"|"planned"|"validated"' src/ --type py

      - name: Verify backward compatibility
        run: |
          # Test old task format still works
          python tests/test_backward_compatibility.py

      - name: Performance benchmarks
        run: |
          pytest tests/test_performance.py --benchmark-only
```

### Code Review Checklist

Before approving workflow-related PRs, verify:

- [ ] No hardcoded workflow states (Principle 1)
- [ ] workflow_step remains optional (Principle 2)
- [ ] Automatic sync implemented (Principle 3)
- [ ] Clear error messages provided (Principle 4)
- [ ] Backward compatibility maintained (Principle 5)
- [ ] Git commits include context (Principle 6)
- [ ] Performance benchmarks pass (Principle 7)
- [ ] State changes explicit (Principle 8)
- [ ] No feature conflicts (Principle 9)
- [ ] Simple use case unchanged (Principle 10)

### Architecture Review

Quarterly review of principles:

1. **Adherence audit** - Scan codebase for violations
2. **Performance review** - Check budgets still met
3. **User feedback** - Validate progressive disclosure working
4. **Principle updates** - Evolve principles based on learnings

---

## Summary

These 10 principles ensure workflow step tracking:

1. **Single Source of Truth** - flowspec_workflow.yml is canonical
2. **Optional Participation** - Simple tasks work without workflow metadata
3. **Automatic Synchronization** - `/flowspec` commands update workflow_step
4. **Fail-Fast Validation** - Invalid transitions rejected with clear errors
5. **Backward Compatibility** - Existing workflows continue unchanged
6. **Observable State** - All changes auditable via Git
7. **Performance Efficiency** - No measurable degradation
8. **Explicit Over Implicit** - User-triggered state changes only
9. **Composability** - Works with all other backlog.md features
10. **Progressive Disclosure** - Simple stays simple, complexity available

**Authority:** These principles have constitutional weight and override implementation preferences.

**Review Cycle:** Annual review, amendments require architecture board approval.

---

## References

- **Hohpe, G.** - *Enterprise Integration Patterns* (Single Source of Truth)
- **Hohpe, G.** - *The Software Architect Elevator* (Penthouse/Engine Room separation)
- **Hohpe, G.** - *Cloud Strategy* (Platform Quality Framework - 7 C's)
- [ADR-002: Workflow Step Tracking Architecture](../adr/ADR-002-workflow-step-tracking-architecture.md)
- [flowspec_workflow.yml](../../flowspec_workflow.yml)
