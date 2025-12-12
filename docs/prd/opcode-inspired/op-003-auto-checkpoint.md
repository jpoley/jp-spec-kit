# OP-003: Auto-Checkpoint on Phase Transitions

> **Status**: Draft
> **Priority**: High
> **Inspired By**: [opcode checkpoint system](https://github.com/winfunc/opcode/blob/main/src-tauri/src/checkpoint/)
> **Dependencies**: None (can be implemented standalone)

## Executive Summary

Automatically create checkpoints before and after workflow phase transitions, enabling rollback to known-good states. Unlike opcode's file-based snapshot system, flowspec will use a git-based approach that leverages existing version control workflows while adding workflow-aware metadata.

## Problem Statement

### Current State
- No automatic snapshots at phase boundaries
- Rollback requires manual git operations
- No correlation between git state and workflow state
- If `/flow:implement` goes wrong, recovery is manual
- No safety net before destructive operations

### Desired State
- Auto-checkpoint before phases that modify code
- Checkpoints tagged with workflow state
- Simple rollback to phase boundaries
- Git-integrated (not parallel storage)
- Lightweight (metadata only, not file duplication)

## Design Decision: Git-Based vs File Snapshots

### Why Not Opcode's Approach?

Opcode uses a full file snapshot system:
- Content-addressable storage with zstd compression
- File metadata (hash, permissions, size)
- Separate timeline tree per session
- ~500 LOC Rust implementation

This is comprehensive but:
- Duplicates git's functionality
- Adds storage overhead
- Requires separate restore tooling
- Doesn't integrate with PR/merge workflows

### Why Git-Based?

Flowspec users are developers who already use git:
- **Zero storage overhead**: Uses git's existing object store
- **Familiar commands**: `git checkout`, `git reset`
- **PR integration**: Checkpoints are branches/tags
- **Existing tooling**: gitk, GitLens, etc.
- **Simpler implementation**: ~150 LOC Python

### Hybrid Approach

We'll use git for file state + custom metadata for workflow context:
- Git stash/branch/tag for file state
- JSON metadata for workflow state
- Correlation between git refs and workflow phases

## User Stories

### US-1: Auto-checkpoint before implementation
**As a** developer running `/flow:implement`
**I want** automatic checkpoint before code changes
**So that** I can rollback if implementation goes wrong

**Acceptance Criteria**:
- [ ] Checkpoint created automatically before implement phase
- [ ] Includes uncommitted changes (git stash)
- [ ] Named with timestamp and phase
- [ ] Can rollback with single command

### US-2: Rollback to phase boundary
**As a** developer whose implementation failed
**I want to** rollback to pre-implement state
**So that** I can try a different approach

**Acceptance Criteria**:
- [ ] `specify checkpoint rollback` restores pre-phase state
- [ ] Uncommitted changes restored from stash
- [ ] Task state reverted in backlog.md
- [ ] Clear confirmation before destructive action

### US-3: View checkpoint history
**As a** developer
**I want to** see checkpoint history for my task
**So that** I can choose which state to restore

**Acceptance Criteria**:
- [ ] `specify checkpoint list` shows all checkpoints
- [ ] Shows phase, timestamp, task ID, commit hash
- [ ] Shows diff summary from current state
- [ ] Interactive selection for rollback

### US-4: Configure checkpoint behavior
**As a** developer
**I want to** configure when checkpoints are created
**So that** I can balance safety vs. overhead

**Acceptance Criteria**:
- [ ] Configure via `flowspec_workflow.yml`
- [ ] Options: manual, before_modify, before_all, smart
- [ ] Can disable for specific phases
- [ ] Retention policy for old checkpoints

## Technical Design

### Checkpoint Data Model

```python
# src/specify_cli/checkpoint/models.py

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List
from enum import Enum
import json

class CheckpointType(Enum):
    PRE_PHASE = "pre_phase"      # Before phase execution
    POST_PHASE = "post_phase"    # After successful phase
    MANUAL = "manual"            # User-created
    AUTO = "auto"                # Smart auto-checkpoint

@dataclass
class Checkpoint:
    """Represents a workflow checkpoint."""

    # Identification
    id: str                       # UUID
    task_id: Optional[str]        # Associated backlog task
    phase: str                    # Workflow phase name
    checkpoint_type: CheckpointType

    # Git state
    branch: str                   # Branch name at checkpoint
    commit_hash: str              # Commit hash (or HEAD if uncommitted)
    stash_ref: Optional[str]      # Git stash reference if uncommitted changes
    has_uncommitted: bool         # Whether stash was created

    # Workflow state
    workflow_state: str           # Task state at checkpoint (e.g., "Planned")
    previous_phase: Optional[str] # Previous phase if any

    # Metadata
    timestamp: datetime
    description: Optional[str]
    user: str                     # Git user.name

    # Metrics (optional)
    metrics_snapshot: Optional[dict] = None

    def to_dict(self) -> dict:
        d = asdict(self)
        d["timestamp"] = self.timestamp.isoformat()
        d["checkpoint_type"] = self.checkpoint_type.value
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Checkpoint":
        d["timestamp"] = datetime.fromisoformat(d["timestamp"])
        d["checkpoint_type"] = CheckpointType(d["checkpoint_type"])
        return cls(**d)


@dataclass
class CheckpointRegistry:
    """Registry of all checkpoints for a project."""

    checkpoints: List[Checkpoint] = field(default_factory=list)
    current_checkpoint_id: Optional[str] = None

    def add(self, checkpoint: Checkpoint):
        self.checkpoints.append(checkpoint)
        self.current_checkpoint_id = checkpoint.id

    def find_by_id(self, checkpoint_id: str) -> Optional[Checkpoint]:
        for cp in self.checkpoints:
            if cp.id == checkpoint_id:
                return cp
        return None

    def find_by_task(self, task_id: str) -> List[Checkpoint]:
        return [cp for cp in self.checkpoints if cp.task_id == task_id]

    def find_by_phase(self, phase: str) -> List[Checkpoint]:
        return [cp for cp in self.checkpoints if cp.phase == phase]

    def get_latest_pre_phase(self, phase: str) -> Optional[Checkpoint]:
        """Get the most recent pre-phase checkpoint for a phase."""
        candidates = [
            cp for cp in self.checkpoints
            if cp.phase == phase and cp.checkpoint_type == CheckpointType.PRE_PHASE
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda cp: cp.timestamp)

    def to_dict(self) -> dict:
        return {
            "checkpoints": [cp.to_dict() for cp in self.checkpoints],
            "current_checkpoint_id": self.current_checkpoint_id,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "CheckpointRegistry":
        return cls(
            checkpoints=[Checkpoint.from_dict(cp) for cp in d.get("checkpoints", [])],
            current_checkpoint_id=d.get("current_checkpoint_id"),
        )
```

### Git Operations

```python
# src/specify_cli/checkpoint/git_ops.py

import subprocess
import uuid
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime

class GitOperations:
    """Git operations for checkpoint management."""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    def _run(self, *args) -> Tuple[int, str, str]:
        """Run a git command."""
        result = subprocess.run(
            ["git", *args],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()

    def get_current_branch(self) -> str:
        """Get current branch name."""
        _, stdout, _ = self._run("rev-parse", "--abbrev-ref", "HEAD")
        return stdout

    def get_current_commit(self) -> str:
        """Get current commit hash."""
        _, stdout, _ = self._run("rev-parse", "HEAD")
        return stdout

    def get_user_name(self) -> str:
        """Get git user.name."""
        _, stdout, _ = self._run("config", "user.name")
        return stdout or "unknown"

    def has_uncommitted_changes(self) -> bool:
        """Check for uncommitted changes."""
        code, _, _ = self._run("diff", "--quiet")
        if code != 0:
            return True
        code, _, _ = self._run("diff", "--staged", "--quiet")
        return code != 0

    def has_untracked_files(self) -> bool:
        """Check for untracked files."""
        _, stdout, _ = self._run("ls-files", "--others", "--exclude-standard")
        return bool(stdout)

    def create_stash(self, message: str, include_untracked: bool = True) -> Optional[str]:
        """Create a git stash and return the stash reference."""
        if not self.has_uncommitted_changes() and not (include_untracked and self.has_untracked_files()):
            return None

        args = ["stash", "push", "-m", message]
        if include_untracked:
            args.append("--include-untracked")

        code, _, stderr = self._run(*args)
        if code != 0:
            raise RuntimeError(f"Failed to create stash: {stderr}")

        # Get stash reference
        _, stdout, _ = self._run("stash", "list")
        if stdout:
            # First line is our stash
            return stdout.split("\n")[0].split(":")[0]  # e.g., "stash@{0}"

        return None

    def apply_stash(self, stash_ref: str, drop: bool = False) -> bool:
        """Apply a stash."""
        action = "pop" if drop else "apply"
        code, _, stderr = self._run("stash", action, stash_ref)
        return code == 0

    def drop_stash(self, stash_ref: str) -> bool:
        """Drop a stash."""
        code, _, _ = self._run("stash", "drop", stash_ref)
        return code == 0

    def create_tag(self, tag_name: str, message: str) -> bool:
        """Create an annotated tag."""
        code, _, stderr = self._run("tag", "-a", tag_name, "-m", message)
        return code == 0

    def delete_tag(self, tag_name: str) -> bool:
        """Delete a tag."""
        code, _, _ = self._run("tag", "-d", tag_name)
        return code == 0

    def get_tag_commit(self, tag_name: str) -> Optional[str]:
        """Get the commit hash for a tag."""
        code, stdout, _ = self._run("rev-parse", f"{tag_name}^{{}}")
        return stdout if code == 0 else None

    def checkout_commit(self, commit: str) -> bool:
        """Checkout a specific commit."""
        code, _, stderr = self._run("checkout", commit)
        return code == 0

    def reset_hard(self, commit: str) -> bool:
        """Hard reset to a commit."""
        code, _, stderr = self._run("reset", "--hard", commit)
        return code == 0

    def get_diff_stat(self, from_ref: str, to_ref: str = "HEAD") -> str:
        """Get diff stat between two refs."""
        _, stdout, _ = self._run("diff", "--stat", from_ref, to_ref)
        return stdout
```

### Checkpoint Manager

```python
# src/specify_cli/checkpoint/manager.py

import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional

from .models import Checkpoint, CheckpointRegistry, CheckpointType
from .git_ops import GitOperations

class CheckpointManager:
    """Manages workflow checkpoints."""

    REGISTRY_FILE = ".flowspec/checkpoints.json"

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.git = GitOperations(project_path)
        self.registry = self._load_registry()

    def _registry_path(self) -> Path:
        return self.project_path / self.REGISTRY_FILE

    def _load_registry(self) -> CheckpointRegistry:
        path = self._registry_path()
        if path.exists():
            with open(path) as f:
                return CheckpointRegistry.from_dict(json.load(f))
        return CheckpointRegistry()

    def _save_registry(self):
        path = self._registry_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(self.registry.to_dict(), f, indent=2)

    def create_checkpoint(
        self,
        phase: str,
        checkpoint_type: CheckpointType,
        task_id: Optional[str] = None,
        workflow_state: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Checkpoint:
        """Create a new checkpoint."""
        checkpoint_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now()

        # Create tag name
        tag_name = f"flowspec/{phase}/{checkpoint_type.value}/{checkpoint_id}"

        # Handle uncommitted changes
        stash_ref = None
        has_uncommitted = self.git.has_uncommitted_changes() or self.git.has_untracked_files()

        if has_uncommitted:
            stash_message = f"flowspec checkpoint {checkpoint_id} - {phase} {checkpoint_type.value}"
            stash_ref = self.git.create_stash(stash_message)

        # Create checkpoint
        checkpoint = Checkpoint(
            id=checkpoint_id,
            task_id=task_id,
            phase=phase,
            checkpoint_type=checkpoint_type,
            branch=self.git.get_current_branch(),
            commit_hash=self.git.get_current_commit(),
            stash_ref=stash_ref,
            has_uncommitted=has_uncommitted,
            workflow_state=workflow_state or "unknown",
            previous_phase=self._get_previous_phase(phase),
            timestamp=timestamp,
            description=description,
            user=self.git.get_user_name(),
        )

        # Create git tag for the checkpoint
        tag_message = json.dumps(checkpoint.to_dict(), indent=2)
        self.git.create_tag(tag_name, tag_message)

        # If we stashed, restore working state
        if stash_ref:
            self.git.apply_stash(stash_ref, drop=False)

        # Save to registry
        self.registry.add(checkpoint)
        self._save_registry()

        return checkpoint

    def _get_previous_phase(self, current_phase: str) -> Optional[str]:
        """Get the previous phase in the workflow."""
        phases = ["assess", "specify", "research", "plan", "implement", "validate", "operate"]
        try:
            idx = phases.index(current_phase)
            return phases[idx - 1] if idx > 0 else None
        except ValueError:
            return None

    def rollback_to_checkpoint(
        self,
        checkpoint_id: str,
        update_task_state: bool = True,
    ) -> bool:
        """Rollback to a checkpoint."""
        checkpoint = self.registry.find_by_id(checkpoint_id)
        if not checkpoint:
            raise ValueError(f"Checkpoint not found: {checkpoint_id}")

        # Reset to checkpoint commit
        success = self.git.reset_hard(checkpoint.commit_hash)
        if not success:
            return False

        # Restore stashed changes if any
        if checkpoint.stash_ref:
            self.git.apply_stash(checkpoint.stash_ref)

        # Update task state in backlog if requested
        if update_task_state and checkpoint.task_id:
            self._update_task_state(
                checkpoint.task_id,
                checkpoint.workflow_state,
            )

        return True

    def _update_task_state(self, task_id: str, state: str):
        """Update task state in backlog.md."""
        try:
            from ..mcp.backlog import task_edit
            task_edit(id=task_id, status=state)
        except Exception:
            pass  # Silently fail - rollback is more important

    def list_checkpoints(
        self,
        task_id: Optional[str] = None,
        phase: Optional[str] = None,
        limit: int = 20,
    ) -> list[Checkpoint]:
        """List checkpoints with optional filters."""
        checkpoints = self.registry.checkpoints

        if task_id:
            checkpoints = [cp for cp in checkpoints if cp.task_id == task_id]

        if phase:
            checkpoints = [cp for cp in checkpoints if cp.phase == phase]

        # Sort by timestamp descending
        checkpoints = sorted(checkpoints, key=lambda cp: cp.timestamp, reverse=True)

        return checkpoints[:limit]

    def cleanup_old_checkpoints(self, keep_count: int = 10) -> int:
        """Remove old checkpoints, keeping the most recent."""
        if len(self.registry.checkpoints) <= keep_count:
            return 0

        # Sort by timestamp
        sorted_checkpoints = sorted(
            self.registry.checkpoints,
            key=lambda cp: cp.timestamp,
        )

        # Remove oldest
        to_remove = sorted_checkpoints[:-keep_count]
        removed = 0

        for cp in to_remove:
            tag_name = f"flowspec/{cp.phase}/{cp.checkpoint_type.value}/{cp.id}"
            self.git.delete_tag(tag_name)

            if cp.stash_ref:
                self.git.drop_stash(cp.stash_ref)

            self.registry.checkpoints.remove(cp)
            removed += 1

        self._save_registry()
        return removed
```

### Workflow Integration

```python
# src/specify_cli/workflow/checkpoint_integration.py

from contextlib import contextmanager
from typing import Optional, Generator
from pathlib import Path

from ..checkpoint.manager import CheckpointManager
from ..checkpoint.models import CheckpointType

# Phases that modify code and should have pre-checkpoints
MODIFY_PHASES = {"implement", "validate", "operate"}

# All phases that could benefit from checkpoints
ALL_PHASES = {"assess", "specify", "research", "plan", "implement", "validate", "operate"}

@contextmanager
def checkpoint_phase(
    phase: str,
    task_id: Optional[str] = None,
    workflow_state: Optional[str] = None,
    project_path: Optional[Path] = None,
    strategy: str = "before_modify",  # manual, before_modify, before_all, smart
) -> Generator[CheckpointManager, None, None]:
    """Context manager for phase checkpoint.

    Usage:
        with checkpoint_phase("implement", task_id="task-123") as mgr:
            # ... execute phase ...
            pass
        # Post-checkpoint created on success
    """
    if project_path is None:
        project_path = Path.cwd()

    mgr = CheckpointManager(project_path)

    # Determine if we should create pre-checkpoint
    create_pre = False
    if strategy == "before_all":
        create_pre = phase in ALL_PHASES
    elif strategy == "before_modify":
        create_pre = phase in MODIFY_PHASES
    elif strategy == "smart":
        # Smart: checkpoint if there are uncommitted changes before modify phases
        create_pre = (
            phase in MODIFY_PHASES and
            (mgr.git.has_uncommitted_changes() or mgr.git.has_untracked_files())
        )

    # Create pre-phase checkpoint
    pre_checkpoint = None
    if create_pre:
        pre_checkpoint = mgr.create_checkpoint(
            phase=phase,
            checkpoint_type=CheckpointType.PRE_PHASE,
            task_id=task_id,
            workflow_state=workflow_state,
            description=f"Before {phase} phase",
        )

    try:
        yield mgr

        # Create post-phase checkpoint on success
        mgr.create_checkpoint(
            phase=phase,
            checkpoint_type=CheckpointType.POST_PHASE,
            task_id=task_id,
            workflow_state=workflow_state,
            description=f"After {phase} phase completed",
        )

    except Exception:
        # On failure, don't create post-checkpoint
        # User can rollback to pre-checkpoint
        raise
```

### CLI Commands

```python
# src/specify_cli/commands/checkpoint.py

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm

from ..checkpoint.manager import CheckpointManager

@click.group()
def checkpoint():
    """Manage workflow checkpoints."""
    pass

@checkpoint.command()
@click.option("--task", type=str, help="Filter by task ID")
@click.option("--phase", type=str, help="Filter by phase name")
@click.option("--limit", type=int, default=20, help="Number of checkpoints to show")
def list(task, phase, limit):
    """List checkpoints."""
    console = Console()
    mgr = CheckpointManager(Path.cwd())

    checkpoints = mgr.list_checkpoints(task_id=task, phase=phase, limit=limit)

    if not checkpoints:
        console.print("[dim]No checkpoints found[/dim]")
        return

    table = Table(title="Workflow Checkpoints")
    table.add_column("ID", style="cyan")
    table.add_column("Phase")
    table.add_column("Type")
    table.add_column("Task")
    table.add_column("Timestamp")
    table.add_column("Stash")

    for cp in checkpoints:
        table.add_row(
            cp.id,
            cp.phase,
            cp.checkpoint_type.value,
            cp.task_id or "-",
            cp.timestamp.strftime("%Y-%m-%d %H:%M"),
            "Yes" if cp.has_uncommitted else "No",
        )

    console.print(table)

@checkpoint.command()
@click.argument("checkpoint_id")
@click.option("--force", is_flag=True, help="Skip confirmation")
def rollback(checkpoint_id, force):
    """Rollback to a checkpoint."""
    console = Console()
    mgr = CheckpointManager(Path.cwd())

    # Find checkpoint
    cp = mgr.registry.find_by_id(checkpoint_id)
    if not cp:
        console.print(f"[red]Checkpoint not found: {checkpoint_id}[/red]")
        return

    # Show what will happen
    console.print(f"\n[bold]Rollback to checkpoint:[/bold]")
    console.print(f"  Phase: {cp.phase}")
    console.print(f"  Type: {cp.checkpoint_type.value}")
    console.print(f"  Task: {cp.task_id or 'N/A'}")
    console.print(f"  Commit: {cp.commit_hash[:8]}")
    console.print(f"  Has stash: {'Yes' if cp.has_uncommitted else 'No'}")

    # Show diff
    diff_stat = mgr.git.get_diff_stat(cp.commit_hash)
    if diff_stat:
        console.print(f"\n[bold]Changes that will be reverted:[/bold]")
        console.print(diff_stat)

    if not force:
        console.print("\n[yellow]Warning: This will discard current changes![/yellow]")
        if not Confirm.ask("Continue?"):
            console.print("[dim]Cancelled[/dim]")
            return

    # Perform rollback
    success = mgr.rollback_to_checkpoint(checkpoint_id)

    if success:
        console.print(f"\n[green]Successfully rolled back to checkpoint {checkpoint_id}[/green]")
    else:
        console.print(f"\n[red]Rollback failed[/red]")

@checkpoint.command()
@click.option("--phase", type=str, required=True, help="Phase name")
@click.option("--task", type=str, help="Task ID")
@click.option("--description", type=str, help="Checkpoint description")
def create(phase, task, description):
    """Manually create a checkpoint."""
    console = Console()
    mgr = CheckpointManager(Path.cwd())

    from ..checkpoint.models import CheckpointType

    cp = mgr.create_checkpoint(
        phase=phase,
        checkpoint_type=CheckpointType.MANUAL,
        task_id=task,
        description=description,
    )

    console.print(f"[green]Created checkpoint {cp.id}[/green]")
    console.print(f"  Phase: {cp.phase}")
    console.print(f"  Commit: {cp.commit_hash[:8]}")
    console.print(f"  Stash: {'Yes' if cp.has_uncommitted else 'No'}")

@checkpoint.command()
@click.option("--keep", type=int, default=10, help="Number of checkpoints to keep")
def cleanup(keep):
    """Remove old checkpoints."""
    console = Console()
    mgr = CheckpointManager(Path.cwd())

    removed = mgr.cleanup_old_checkpoints(keep_count=keep)
    console.print(f"[green]Removed {removed} old checkpoints[/green]")
```

## Configuration

```yaml
# flowspec_workflow.yml (additions)

checkpoint:
  # Checkpoint strategy: manual, before_modify, before_all, smart
  strategy: "before_modify"

  # Phases that always get pre-checkpoints (override strategy)
  always_checkpoint: ["implement"]

  # Phases that never get checkpoints
  never_checkpoint: []

  # Retention: max checkpoints to keep per task
  max_per_task: 10

  # Auto-cleanup on create
  auto_cleanup: true

  # Include untracked files in stash
  include_untracked: true
```

## File Structure

```
src/specify_cli/
├── checkpoint/
│   ├── __init__.py
│   ├── models.py       # Checkpoint, CheckpointRegistry
│   ├── git_ops.py      # Git operations wrapper
│   └── manager.py      # CheckpointManager
├── workflow/
│   └── checkpoint_integration.py
└── commands/
    └── checkpoint.py   # CLI commands

.flowspec/
└── checkpoints.json    # Checkpoint registry
```

## Testing Strategy

### Unit Tests
```python
# tests/test_checkpoint.py

def test_checkpoint_creation(tmp_git_repo):
    mgr = CheckpointManager(tmp_git_repo)
    cp = mgr.create_checkpoint("implement", CheckpointType.PRE_PHASE)

    assert cp.id is not None
    assert cp.phase == "implement"
    assert cp.commit_hash is not None

def test_rollback_with_stash(tmp_git_repo):
    # Create file
    (tmp_git_repo / "test.txt").write_text("original")

    mgr = CheckpointManager(tmp_git_repo)
    cp = mgr.create_checkpoint("implement", CheckpointType.PRE_PHASE)

    # Modify file
    (tmp_git_repo / "test.txt").write_text("modified")

    # Rollback
    mgr.rollback_to_checkpoint(cp.id)

    # Verify
    assert (tmp_git_repo / "test.txt").read_text() == "original"
```

### Integration Tests
- Test with real git repository
- Test stash creation/application
- Test tag creation/deletion
- Test rollback with backlog state update

## Acceptance Criteria Summary

- [ ] Checkpoints created automatically before modify phases
- [ ] Git stash used for uncommitted changes
- [ ] Git tags created for checkpoint metadata
- [ ] `specify checkpoint list` shows all checkpoints
- [ ] `specify checkpoint rollback <id>` restores state
- [ ] `specify checkpoint create` for manual checkpoints
- [ ] Checkpoint cleanup removes old checkpoints
- [ ] Configuration via `flowspec_workflow.yml`
- [ ] Task state updated on rollback
- [ ] Works with standard git workflows

## Migration from Opcode

For users migrating from opcode's checkpoint system:
- Opcode checkpoints are not compatible (different storage format)
- Recommend: commit opcode checkpoint files to git, then use flowspec
- No automatic migration (fundamentally different approaches)

## Open Questions

1. Should we support checkpoint across branches?
2. How to handle conflicts when applying stash?
3. Should checkpoints be pushed to remote (tags)?

## References

- [opcode checkpoint/mod.rs](https://github.com/winfunc/opcode/blob/main/src-tauri/src/checkpoint/mod.rs)
- [opcode checkpoint/storage.rs](https://github.com/winfunc/opcode/blob/main/src-tauri/src/checkpoint/storage.rs)
- [git stash documentation](https://git-scm.com/docs/git-stash)
