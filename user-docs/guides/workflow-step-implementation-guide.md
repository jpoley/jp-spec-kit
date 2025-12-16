# Workflow Step Tracking - Implementation Guide

**Related ADR:** [ADR-002: Workflow Step Tracking Architecture](../adr/ADR-002-workflow-step-tracking-architecture.md)

**Status:** Implementation Pending
**Target Version:** v0.0.150+

---

## Overview

This guide provides implementation details for adding workflow step tracking to backlog.md tasks, enabling integration with the `/flowspec` workflow state machine.

### Quick Summary

**What:** Add optional `workflow_step` and `workflow_feature` fields to tasks
**Why:** Enable state-based workflow enforcement and progress visibility
**How:** Hybrid two-level model (board status + workflow metadata)

---

## Implementation Phases

### Phase 1: Foundation (v0.0.150)

#### 1.1 Task Schema Extension

**File:** `src/specify_cli/backlog/parser.py`

Add workflow fields to Task dataclass:

```python
@dataclass
class Task:
    """Backlog task representation."""

    task_id: str
    title: str
    status: str
    priority: str | None = None
    labels: list[str] = field(default_factory=list)
    assignee: list[str] = field(default_factory=list)
    description: str = ""
    acceptance_criteria: list[dict] = field(default_factory=list)
    implementation_notes: str = ""
    created: str = ""
    updated: str = ""

    # NEW FIELDS (Phase 1)
    workflow_step: str | None = None
    workflow_feature: str | None = None
```

**Backward Compatibility:** Both fields optional (None default).

#### 1.2 YAML Frontmatter Parsing

**File:** `src/specify_cli/backlog/parser.py`

Update `_parse_frontmatter()` method:

```python
def _parse_frontmatter(self, frontmatter: dict) -> dict:
    """Parse task frontmatter from YAML."""
    return {
        "task_id": frontmatter.get("id", ""),
        "title": frontmatter.get("title", ""),
        "status": frontmatter.get("status", "To Do"),
        "priority": frontmatter.get("priority"),
        "labels": frontmatter.get("labels", []),
        "assignee": frontmatter.get("assignee", []),
        "created": frontmatter.get("created", ""),
        "updated": frontmatter.get("updated", ""),

        # NEW: Parse workflow fields if present
        "workflow_step": frontmatter.get("workflow_step"),
        "workflow_feature": frontmatter.get("workflow_feature"),
    }
```

#### 1.3 YAML Frontmatter Writing

**File:** `src/specify_cli/backlog/writer.py`

Update `_generate_frontmatter()` method:

```python
def _generate_frontmatter(self, task: Task) -> dict:
    """Generate YAML frontmatter for task file."""
    frontmatter = {
        "id": task.task_id,
        "title": task.title,
        "status": task.status,
        "created": task.created or self._get_timestamp(),
        "updated": self._get_timestamp(),
    }

    # Optional fields
    if task.priority:
        frontmatter["priority"] = task.priority
    if task.labels:
        frontmatter["labels"] = task.labels
    if task.assignee:
        frontmatter["assignee"] = task.assignee

    # NEW: Include workflow fields if set
    if task.workflow_step:
        frontmatter["workflow_step"] = task.workflow_step
    if task.workflow_feature:
        frontmatter["workflow_feature"] = task.workflow_feature

    return frontmatter
```

#### 1.4 CLI Display Updates

**File:** `src/specify_cli/backlog/cli.py` (or wherever task display logic lives)

Add workflow step to task view output:

```python
def display_task(task: Task, plain: bool = False) -> None:
    """Display task details."""
    print(f"Task {task.task_id} - {task.title}")
    print("=" * 50)
    print(f"Status: {task.status}")

    if task.workflow_step:
        print(f"Workflow Step: {task.workflow_step}")
    if task.workflow_feature:
        print(f"Feature: {task.workflow_feature}")

    print(f"Priority: {task.priority or 'Not set'}")
    # ... rest of display logic
```

#### 1.5 TUI Visual Indicators

**File:** `backlog/tui.py` (or TUI rendering code)

Add workflow step as visual tag/label:

```python
def render_task_card(task: Task) -> str:
    """Render task card for board view."""
    card = f"[{task.status}] │ {task.title}\n"

    # Add assignee if present
    if task.assignee:
        card += f"             │ {', '.join(task.assignee)}"

    # NEW: Add workflow step indicator
    if task.workflow_step:
        card += f"  workflow:{task.workflow_step}"

    return card
```

Example output:
```
[In Progress] │ Implement auth service
              │ @backend-engineer  workflow:Planned
```

---

### Phase 2: Workflow Synchronization (v0.0.155)

#### 2.1 WorkflowStateSynchronizer Class

**File:** `src/specify_cli/workflow/sync.py` (new file)

```python
"""Workflow state synchronization for backlog.md tasks."""

from pathlib import Path
from ..backlog.parser import TaskParser, Task
from ..backlog.writer import BacklogWriter
from .config import WorkflowConfig
from .exceptions import WorkflowStateError


class WorkflowStateSynchronizer:
    """Synchronizes backlog.md task status with flowspec workflow steps."""

    def __init__(self, backlog_dir: Path | None = None):
        """Initialize synchronizer.

        Args:
            backlog_dir: Path to backlog directory (defaults to ./backlog)
        """
        self.backlog_dir = backlog_dir or Path.cwd() / "backlog"
        self.parser = TaskParser()
        self.writer = BacklogWriter(self.backlog_dir)
        self.config = WorkflowConfig.load()

    def update_task_workflow_step(
        self,
        task_id: str,
        workflow: str,
        feature: str | None = None,
        auto_status: bool = True,
    ) -> Task:
        """Update task workflow step after /flowspec command completes.

        Args:
            task_id: Backlog task ID (e.g., "task-042")
            workflow: Workflow name (e.g., "implement")
            feature: Feature slug for artifact validation (optional)
            auto_status: Automatically update status based on workflow step

        Returns:
            Updated Task object

        Raises:
            WorkflowStateError: If workflow transition is invalid

        Example:
            >>> sync = WorkflowStateSynchronizer()
            >>> task = sync.update_task_workflow_step(
            ...     "task-042",
            ...     "implement",
            ...     "user-auth"
            ... )
            >>> task.workflow_step
            'In Implementation'
        """
        # Load current task
        task = self._load_task(task_id)
        current_step = task.workflow_step or "To Do"

        # Validate workflow transition
        try:
            next_step = self.config.get_next_state(current_step, workflow)
        except WorkflowStateError as e:
            raise WorkflowStateError(
                f"Cannot execute {workflow} on {task_id}: {e}"
            ) from e

        # Update workflow step
        task.workflow_step = next_step

        # Update feature if provided
        if feature:
            task.workflow_feature = feature

        # Auto-update status if enabled
        if auto_status:
            task.status = self._map_step_to_status(next_step, task.status)

        # Update timestamp
        task.updated = self._get_timestamp()

        # Write back to disk
        self._save_task(task)

        return task

    def sync_all_tasks(self) -> dict[str, str]:
        """Synchronize all tasks to ensure status/workflow_step alignment.

        Returns:
            Dictionary mapping task_id to sync action taken.

        Example:
            >>> sync = WorkflowStateSynchronizer()
            >>> results = sync.sync_all_tasks()
            >>> results
            {'task-042': 'aligned', 'task-043': 'updated status', ...}
        """
        results = {}
        tasks_dir = self.backlog_dir / "tasks"

        for task_file in tasks_dir.glob("task-*.md"):
            task = self.parser.parse_task_file(task_file)

            if not task.workflow_step:
                results[task.task_id] = "no workflow_step (skipped)"
                continue

            expected_status = self._map_step_to_status(
                task.workflow_step,
                task.status
            )

            if expected_status != task.status:
                task.status = expected_status
                task.updated = self._get_timestamp()
                self._save_task(task)
                results[task.task_id] = f"updated status to {expected_status}"
            else:
                results[task.task_id] = "aligned"

        return results

    def _load_task(self, task_id: str) -> Task:
        """Load task from backlog."""
        task_file = self.backlog_dir / "tasks" / f"{task_id}.md"
        if not task_file.exists():
            raise FileNotFoundError(f"Task not found: {task_id}")
        return self.parser.parse_task_file(task_file)

    def _save_task(self, task: Task) -> None:
        """Save task back to backlog."""
        self.writer.write_task(task, overwrite=True)

    def _map_step_to_status(self, workflow_step: str, current_status: str) -> str:
        """Map workflow step to appropriate board status.

        Default mapping:
        - "To Do" -> "To Do"
        - "Assessed", "Specified", "Researched", "Planned" -> "In Progress"
        - "In Implementation" -> "In Progress"
        - "Validated" -> "In Review"
        - "Deployed", "Done" -> "Done"

        Args:
            workflow_step: Current workflow step
            current_status: Current task status (for smart defaults)

        Returns:
            Appropriate board status
        """
        # Load custom mapping from backlog config if available
        custom_mapping = self._load_custom_mapping()
        if workflow_step in custom_mapping:
            return custom_mapping[workflow_step]

        # Default mapping
        DEFAULT_MAPPING = {
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

        return DEFAULT_MAPPING.get(workflow_step, current_status)

    def _load_custom_mapping(self) -> dict[str, str]:
        """Load custom workflow_step to status mapping from config."""
        config_file = self.backlog_dir / "config.yml"
        if not config_file.exists():
            return {}

        import yaml
        with open(config_file) as f:
            config = yaml.safe_load(f)

        return config.get("workflow_step_mappings", {})

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
```

#### 2.2 Integration with /flowspec Commands

**Pattern for all /flowspec commands:**

```python
# Example: .claude/commands/flow.implement.md

from specify_cli.workflow.sync import WorkflowStateSynchronizer

# After /flow:implement completes successfully
sync = WorkflowStateSynchronizer()

# Update all tasks related to this feature
for task_id in implementation_tasks:
    sync.update_task_workflow_step(
        task_id=task_id,
        workflow="implement",
        feature=feature_slug,
        auto_status=True
    )
```

**Specific integrations:**

```python
# /flow:assess
sync.update_task_workflow_step(task_id, "assess", feature)
# Sets workflow_step = "Assessed"

# /flow:specify
sync.update_task_workflow_step(task_id, "specify", feature)
# Sets workflow_step = "Specified"

# /flow:plan
sync.update_task_workflow_step(task_id, "plan", feature)
# Sets workflow_step = "Planned"

# /flow:implement
sync.update_task_workflow_step(task_id, "implement", feature)
# Sets workflow_step = "In Implementation"

# /flow:validate
sync.update_task_workflow_step(task_id, "validate", feature)
# Sets workflow_step = "Validated"

# /flow:operate
sync.update_task_workflow_step(task_id, "operate", feature)
# Sets workflow_step = "Deployed"
```

---

### Phase 3: Validation (v0.0.160)

#### 3.1 Workflow Precondition Checks

**File:** `src/specify_cli/workflow/validator.py`

Add to existing WorkflowValidator:

```python
def validate_task_ready_for_workflow(
    self,
    task: Task,
    workflow: str,
    feature: str | None = None,
) -> tuple[bool, list[str]]:
    """Validate task is ready for workflow execution.

    Checks:
    1. Task workflow_step is valid for this workflow
    2. Required artifacts exist (if feature provided)
    3. Acceptance criteria defined (for implement/validate)

    Args:
        task: Task to validate
        workflow: Workflow to execute (e.g., "implement")
        feature: Feature slug for artifact validation

    Returns:
        (is_valid, error_messages)

    Example:
        >>> validator = WorkflowValidator()
        >>> valid, errors = validator.validate_task_ready_for_workflow(
        ...     task,
        ...     "implement",
        ...     "user-auth"
        ... )
        >>> if not valid:
        ...     print("\\n".join(errors))
    """
    errors = []
    config = WorkflowConfig.load()

    # Check workflow step
    current_step = task.workflow_step or "To Do"
    valid_inputs = config.get_input_states(workflow)

    if current_step not in valid_inputs:
        errors.append(
            f"Task {task.task_id} is in '{current_step}' but {workflow} "
            f"requires one of: {', '.join(valid_inputs)}"
        )

    # Check required artifacts if feature provided
    if feature:
        artifact_errors = self._validate_artifacts(workflow, feature)
        errors.extend(artifact_errors)

    # Check acceptance criteria for implementation
    if workflow == "implement" and not task.acceptance_criteria:
        errors.append(
            f"Task {task.task_id} has no acceptance criteria. "
            "Cannot implement without testable requirements."
        )

    return len(errors) == 0, errors

def _validate_artifacts(self, workflow: str, feature: str) -> list[str]:
    """Validate required artifacts exist for workflow.

    Uses flowspec_workflow.yml transitions to find required artifacts.
    """
    errors = []
    config = WorkflowConfig.load()

    # Get required input artifacts for this workflow
    transitions = config.get_transitions()
    for transition in transitions:
        if transition.get("via") != workflow:
            continue

        input_artifacts = transition.get("input_artifacts", [])
        for artifact in input_artifacts:
            if not artifact.get("required"):
                continue

            # Resolve path template
            path_template = artifact["path"]
            resolved_path = path_template.replace("{feature}", feature)

            # Check existence
            artifact_path = Path.cwd() / resolved_path
            if not artifact_path.exists():
                errors.append(
                    f"Required artifact missing: {resolved_path} "
                    f"(type: {artifact['type']})"
                )

    return errors
```

#### 3.2 CLI Validation Commands

**File:** `src/specify_cli/cli.py`

Add new subcommands:

```python
@backlog.command()
@click.argument("task_id")
@click.argument("workflow")
@click.option("--feature", help="Feature slug for artifact validation")
def workflow_validate(task_id: str, workflow: str, feature: str | None):
    """Validate task is ready for workflow execution.

    Example:
        backlog workflow-validate task-042 implement --feature user-auth
    """
    from .backlog.parser import TaskParser
    from .workflow.validator import WorkflowValidator

    parser = TaskParser()
    task = parser.parse_task_file(Path(f"backlog/tasks/{task_id}.md"))

    validator = WorkflowValidator()
    valid, errors = validator.validate_task_ready_for_workflow(
        task, workflow, feature
    )

    if valid:
        click.echo(f"✓ Task {task_id} is ready for /{workflow}")
    else:
        click.echo(f"✗ Task {task_id} is NOT ready for /{workflow}:")
        for error in errors:
            click.echo(f"  - {error}")
        raise click.Abort()


@backlog.command()
def workflow_sync():
    """Synchronize all tasks to align status with workflow_step.

    Example:
        backlog workflow-sync
    """
    from .workflow.sync import WorkflowStateSynchronizer

    sync = WorkflowStateSynchronizer()
    results = sync.sync_all_tasks()

    updated = [tid for tid, action in results.items() if "updated" in action]
    aligned = [tid for tid, action in results.items() if action == "aligned"]
    skipped = [tid for tid, action in results.items() if "skipped" in action]

    click.echo(f"Synchronization complete:")
    click.echo(f"  Updated: {len(updated)}")
    click.echo(f"  Already aligned: {len(aligned)}")
    click.echo(f"  Skipped (no workflow_step): {len(skipped)}")

    if updated:
        click.echo("\nUpdated tasks:")
        for tid in updated:
            click.echo(f"  - {tid}: {results[tid]}")
```

---

### Phase 4: Documentation (v0.0.165)

See [task-095](../../backlog/tasks/task-095.md) for full documentation requirements.

**Key documents to create:**

1. **docs/guides/workflow-state-mapping.md**
   - Comprehensive mapping table
   - State transition diagrams
   - Examples and troubleshooting

2. **Update CLAUDE.md**
   - Add workflow_step to task workflow examples
   - Document when to use workflow_step vs. simple status

3. **Update backlog/CLAUDE.md**
   - Add workflow_step to command reference
   - Show workflow validation commands

---

## Testing Strategy

### Unit Tests

```python
# tests/test_workflow_sync.py

def test_update_task_workflow_step():
    """Test workflow step update functionality."""
    sync = WorkflowStateSynchronizer()

    # Create test task
    task = Task(
        task_id="task-test",
        title="Test task",
        status="To Do",
        workflow_step="Planned",
    )

    # Update to implementation
    updated = sync.update_task_workflow_step(
        task.task_id,
        "implement",
        "test-feature"
    )

    assert updated.workflow_step == "In Implementation"
    assert updated.status == "In Progress"
    assert updated.workflow_feature == "test-feature"


def test_invalid_workflow_transition():
    """Test validation of invalid workflow transitions."""
    sync = WorkflowStateSynchronizer()

    task = Task(
        task_id="task-test",
        title="Test task",
        status="To Do",
        workflow_step="To Do",
    )

    # Cannot implement without planning
    with pytest.raises(WorkflowStateError) as exc:
        sync.update_task_workflow_step(task.task_id, "implement")

    assert "To Do" in str(exc.value)
    assert "Planned" in str(exc.value)
```

### Integration Tests

```python
# tests/test_flowspec_workflow_integration.py

def test_flowspec_implement_updates_workflow_step(tmp_path):
    """Test /flow:implement updates task workflow_step."""
    # Setup: Create task with workflow_step = "Planned"
    # Execute: Run /flow:implement
    # Verify: workflow_step updated to "In Implementation"
    pass


def test_workflow_validation_blocks_invalid_transitions(tmp_path):
    """Test workflow validation prevents invalid state transitions."""
    # Setup: Create task with workflow_step = "To Do"
    # Execute: Try to run /flow:implement
    # Verify: Validation error raised
    pass
```

---

## Backward Compatibility

### Existing Tasks

**Guarantee:** All existing tasks continue to work unchanged.

**Mechanism:**
- `workflow_step` and `workflow_feature` are optional fields
- Parser handles missing fields gracefully (None default)
- TUI rendering checks for None before displaying
- CLI commands work identically for tasks without workflow_step

### Simple Kanban Boards

**Use Case:** Projects not using `/flowspec` workflows.

**Support:**
- Workflow fields remain None
- Board displays normally (3 columns: To Do, In Progress, Done)
- No visual clutter from workflow steps
- No performance impact

### Migration Path

**For existing projects:**

```bash
# Option 1: Do nothing - tasks work as-is

# Option 2: Manually add workflow_step to active tasks
backlog task edit task-042 --set-field workflow_step=Planned

# Option 3: Bulk migration script (if needed later)
python scripts/migrate_workflow_steps.py
```

---

## Performance Considerations

### Parsing Performance

**Impact:** Negligible (2 additional optional fields)
**Mitigation:** Fields parsed lazily with existing frontmatter

### TUI Rendering

**Impact:** Minimal (conditional string concatenation)
**Mitigation:** Only render workflow_step if present

**Benchmark target:** <5ms additional rendering time per 100 tasks

### Disk I/O

**Impact:** Minimal (frontmatter ~50 bytes larger when fields present)
**Mitigation:** YAML frontmatter already uses I/O efficiently

---

## Configuration Examples

### Default Backlog Config (No Custom Mapping)

```yaml
# backlog/config.yml
project_name: "example-project"
default_status: "To Do"
statuses: ["To Do", "In Progress", "Done"]

# No workflow_step_mappings - use defaults
```

### Custom Board Columns

```yaml
# backlog/config.yml
project_name: "enterprise-project"
default_status: "Backlog"
statuses: ["Backlog", "Active", "Review", "Shipped"]

# Custom workflow_step → status mappings
workflow_step_mappings:
  "To Do": "Backlog"
  "Assessed": "Backlog"
  "Specified": "Active"
  "Researched": "Active"
  "Planned": "Active"
  "In Implementation": "Active"
  "Validated": "Review"
  "Deployed": "Shipped"
  "Done": "Shipped"
```

---

## Troubleshooting

### Issue: Status and workflow_step Out of Sync

**Symptoms:**
```
Task task-042 shows status="Done" but workflow_step="Planned"
```

**Solution:**
```bash
backlog workflow-sync
```

### Issue: Cannot Execute Workflow

**Symptoms:**
```
Error: Cannot execute implement from To Do. Valid input states: Planned
```

**Solution:**
Check task workflow_step and run required precursor workflows:
```bash
backlog task task-042 --plain
# Shows workflow_step: To Do

# Run planning workflow first
/flow:plan
```

### Issue: Workflow Step Not Displaying

**Symptoms:**
Task has workflow_step in frontmatter but doesn't show in TUI.

**Solution:**
Check TUI version and rendering settings. Ensure using v0.0.150+.

---

## Next Steps

1. **Review ADR-002** for architectural context
2. **Implement Phase 1** (foundation) - target v0.0.150
3. **Coordinate with task-090/task-091** for WorkflowConfig integration
4. **Test with pilot project** before broad rollout
5. **Gather developer feedback** for Phase 2+ improvements

---

## References

- [ADR-002: Workflow Step Tracking Architecture](../adr/ADR-002-workflow-step-tracking-architecture.md)
- [flowspec_workflow.yml](../../flowspec_workflow.yml)
- [Backlog User Guide](./backlog-user-guide.md)
- [Workflow State Mapping](./workflow-state-mapping.md) (to be created in Phase 4)
