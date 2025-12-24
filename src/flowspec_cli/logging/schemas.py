"""Data schemas for logging entries.

All log entries use JSONL format (one JSON object per line).
Each entry includes a timestamp and source information.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import uuid


class LogSource(str, Enum):
    """Source of a log entry."""

    AGENT = "agent"  # AI agent decision/action
    HUMAN = "human"  # Human operator decision/action
    HOOK = "hook"  # Claude or git hook
    BACKLOG = "backlog"  # Backlog status change
    WORKFLOW = "workflow"  # Flowspec workflow command
    SYSTEM = "system"  # System-generated event


class DecisionImpact(str, Enum):
    """Impact level of a decision."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventCategory(str, Enum):
    """Category of an event."""

    # Lifecycle events
    SESSION_START = "session.start"
    SESSION_END = "session.end"

    # Workflow events
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"

    # Task events
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_STATUS_CHANGED = "task.status_changed"
    TASK_COMPLETED = "task.completed"
    TASK_ARCHIVED = "task.archived"

    # Hook events
    HOOK_EXECUTED = "hook.executed"
    HOOK_FAILED = "hook.failed"

    # Git events
    GIT_COMMIT = "git.commit"
    GIT_PUSH = "git.push"
    GIT_BRANCH = "git.branch"

    # Decision events
    DECISION_MADE = "decision.made"

    # Error events
    ERROR_OCCURRED = "error.occurred"


@dataclass
class BaseLogEntry:
    """Base class for all log entries."""

    timestamp: str = field(init=False)
    entry_id: str = field(init=False)
    # source is init=False with post_init assignment to avoid inheritance issues
    source: LogSource = field(default=LogSource.SYSTEM, init=False)

    def __post_init__(self) -> None:
        """Generate timestamp and entry ID."""
        object.__setattr__(
            self,
            "timestamp",
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        )
        object.__setattr__(self, "entry_id", f"log_{uuid.uuid4().hex[:12]}")

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        # Convert enums to their values
        for key, value in result.items():
            if isinstance(value, Enum):
                result[key] = value.value
            elif isinstance(value, list):
                result[key] = [v.value if isinstance(v, Enum) else v for v in value]
        return result


@dataclass
class Decision(BaseLogEntry):
    """A decision log entry.

    Records significant decisions made during development.
    """

    decision: str  # What was decided
    context: str  # What prompted this decision
    rationale: str  # Why this choice was made
    alternatives: list[str] = field(default_factory=list)
    impact: DecisionImpact = DecisionImpact.MEDIUM
    reversible: bool = True
    related_tasks: list[str] = field(default_factory=list)
    category: Optional[str] = None  # e.g., "architecture", "implementation", "tooling"
    # Override source for this entry (stored in base class)
    _source_override: Optional[LogSource] = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Initialize base fields."""
        super().__post_init__()
        # Set source from override or default to AGENT for decisions
        source = self._source_override if self._source_override else LogSource.AGENT
        object.__setattr__(self, "source", source)


@dataclass
class LogEvent(BaseLogEntry):
    """An event log entry.

    Records significant events during development.
    """

    category: EventCategory
    message: str
    details: dict = field(default_factory=dict)
    task_id: Optional[str] = None
    workflow_phase: Optional[str] = None
    duration_ms: Optional[int] = None
    success: bool = True
    # Override source for this entry (stored in base class)
    _source_override: Optional[LogSource] = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Initialize base fields."""
        super().__post_init__()
        # Set source from override or default to SYSTEM for events
        if self._source_override:
            object.__setattr__(self, "source", self._source_override)
