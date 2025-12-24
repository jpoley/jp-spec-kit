"""Tests for the centralized logging module.

Tests the dual-path logging system (user projects vs internal dev),
decision logger, and event logger functionality.
"""

import json
from datetime import date
from pathlib import Path

import pytest

from flowspec_cli.logging.config import (
    LoggingConfig,
    _find_project_root,
    _is_flowspec_repo,
    clear_config_cache,
    get_config,
)
from flowspec_cli.logging.decision_logger import DecisionLogger
from flowspec_cli.logging.event_logger import EventLogger
from flowspec_cli.logging.schemas import (
    Decision,
    DecisionImpact,
    EventCategory,
    LogEvent,
    LogSource,
)


# Fixtures


@pytest.fixture
def temp_project_dir(tmp_path: Path) -> Path:
    """Create a temporary project directory (simulating a user project)."""
    project_dir = tmp_path / "my_project"
    project_dir.mkdir()
    (project_dir / ".git").mkdir()  # Git marker
    return project_dir


@pytest.fixture
def temp_flowspec_repo(tmp_path: Path) -> Path:
    """Create a temporary directory simulating the flowspec repo."""
    repo_dir = tmp_path / "flowspec"
    repo_dir.mkdir()
    (repo_dir / ".git").mkdir()
    (repo_dir / "src" / "flowspec_cli").mkdir(parents=True)
    (repo_dir / "pyproject.toml").write_text('name = "flowspec-cli"\nversion = "1.0.0"')
    return repo_dir


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear config cache before each test."""
    clear_config_cache()
    yield
    clear_config_cache()


# Config Tests


class TestLoggingConfig:
    """Tests for LoggingConfig."""

    def test_user_project_paths(self, temp_project_dir: Path) -> None:
        """User projects should use ./logs/ directory."""
        config = LoggingConfig(
            project_root=temp_project_dir,
            is_internal_dev=False,
        )

        assert config.events_dir == temp_project_dir / "logs" / "events"
        assert config.decisions_dir == temp_project_dir / "logs" / "decisions"
        assert not config.is_internal_dev

    def test_internal_dev_paths(self, temp_flowspec_repo: Path) -> None:
        """Internal dev should use .flowspec/logs/ directory."""
        config = LoggingConfig(
            project_root=temp_flowspec_repo,
            is_internal_dev=True,
        )

        assert config.events_dir == temp_flowspec_repo / ".flowspec" / "logs" / "events"
        assert (
            config.decisions_dir
            == temp_flowspec_repo / ".flowspec" / "logs" / "decisions"
        )
        assert config.is_internal_dev

    def test_ensure_dirs_creates_directories(self, temp_project_dir: Path) -> None:
        """ensure_dirs should create log directories."""
        config = LoggingConfig(
            project_root=temp_project_dir,
            is_internal_dev=False,
        )

        assert not config.events_dir.exists()
        assert not config.decisions_dir.exists()

        config.ensure_dirs()

        assert config.events_dir.exists()
        assert config.decisions_dir.exists()


class TestFlowspecRepoDetection:
    """Tests for detecting flowspec repository."""

    def test_detects_flowspec_repo(self, temp_flowspec_repo: Path) -> None:
        """Should correctly identify flowspec repo."""
        assert _is_flowspec_repo(temp_flowspec_repo)

    def test_rejects_user_project(self, temp_project_dir: Path) -> None:
        """Should not identify regular project as flowspec."""
        assert not _is_flowspec_repo(temp_project_dir)

    def test_rejects_partial_structure(self, tmp_path: Path) -> None:
        """Should reject directories with only some flowspec markers."""
        # Just src/flowspec_cli without pyproject.toml
        (tmp_path / "src" / "flowspec_cli").mkdir(parents=True)
        assert not _is_flowspec_repo(tmp_path)


class TestProjectRootFinding:
    """Tests for finding project root."""

    def test_finds_git_root(self, temp_project_dir: Path) -> None:
        """Should find project root by .git directory."""
        subdir = temp_project_dir / "src" / "module"
        subdir.mkdir(parents=True)

        root = _find_project_root(subdir)
        assert root == temp_project_dir

    def test_finds_pyproject_root(self, tmp_path: Path) -> None:
        """Should find project root by pyproject.toml."""
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"')
        subdir = tmp_path / "src"
        subdir.mkdir()

        root = _find_project_root(subdir)
        assert root == tmp_path


class TestGetConfig:
    """Tests for get_config function."""

    def test_auto_detects_user_project(self, temp_project_dir: Path) -> None:
        """Should auto-detect user project mode."""
        config = get_config(temp_project_dir)
        assert not config.is_internal_dev
        assert config.events_dir == temp_project_dir / "logs" / "events"

    def test_auto_detects_flowspec_repo(self, temp_flowspec_repo: Path) -> None:
        """Should auto-detect internal dev mode."""
        config = get_config(temp_flowspec_repo)
        assert config.is_internal_dev
        assert config.events_dir == temp_flowspec_repo / ".flowspec" / "logs" / "events"

    def test_caches_config(self, temp_project_dir: Path) -> None:
        """Should cache config for same project."""
        config1 = get_config(temp_project_dir)
        config2 = get_config(temp_project_dir)
        assert config1 is config2


# Schema Tests


class TestDecisionSchema:
    """Tests for Decision schema."""

    def test_creates_decision_with_defaults(self) -> None:
        """Should create decision with required fields and defaults."""
        decision = Decision(
            decision="Use PostgreSQL",
            context="Choosing database",
            rationale="ACID compliance",
        )

        assert decision.decision == "Use PostgreSQL"
        assert decision.context == "Choosing database"
        assert decision.rationale == "ACID compliance"
        assert decision.impact == DecisionImpact.MEDIUM
        assert decision.reversible is True
        assert decision.alternatives == []
        assert decision.related_tasks == []
        assert decision.timestamp  # Auto-generated
        assert decision.entry_id  # Auto-generated

    def test_to_dict_serializes_enums(self) -> None:
        """Should serialize enums to string values."""
        decision = Decision(
            decision="Test",
            context="Test context",
            rationale="Test rationale",
            impact=DecisionImpact.HIGH,
            _source_override=LogSource.HUMAN,
        )

        data = decision.to_dict()
        assert data["impact"] == "high"
        assert data["source"] == "human"


class TestLogEventSchema:
    """Tests for LogEvent schema."""

    def test_creates_event_with_required_fields(self) -> None:
        """Should create event with required fields."""
        event = LogEvent(
            category=EventCategory.WORKFLOW_COMPLETED,
            message="Completed workflow",
        )

        assert event.category == EventCategory.WORKFLOW_COMPLETED
        assert event.message == "Completed workflow"
        assert event.details == {}
        assert event.success is True
        assert event.timestamp
        assert event.entry_id

    def test_to_dict_serializes_category(self) -> None:
        """Should serialize category enum to string value."""
        event = LogEvent(
            category=EventCategory.SESSION_START,
            message="Session started",
        )

        data = event.to_dict()
        assert data["category"] == "session.start"


# Decision Logger Tests


class TestDecisionLogger:
    """Tests for DecisionLogger."""

    def test_logs_decision_to_file(self, temp_project_dir: Path) -> None:
        """Should write decision to JSONL file."""
        config = LoggingConfig(project_root=temp_project_dir, is_internal_dev=False)
        logger = DecisionLogger(config)

        entry = logger.log(
            decision="Use REST API",
            context="API design",
            rationale="Simplicity",
        )

        # Check file was created
        log_file = config.decisions_dir / f"{date.today().isoformat()}.jsonl"
        assert log_file.exists()

        # Check content
        content = log_file.read_text()
        data = json.loads(content.strip())
        assert data["decision"] == "Use REST API"
        assert data["entry_id"] == entry.entry_id

    def test_appends_to_existing_file(self, temp_project_dir: Path) -> None:
        """Should append to existing log file."""
        config = LoggingConfig(project_root=temp_project_dir, is_internal_dev=False)
        logger = DecisionLogger(config)

        logger.log(decision="First", context="Test", rationale="Test")
        logger.log(decision="Second", context="Test", rationale="Test")

        log_file = config.decisions_dir / f"{date.today().isoformat()}.jsonl"
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 2

    def test_read_today_returns_decisions(self, temp_project_dir: Path) -> None:
        """Should read back decisions from today's log."""
        config = LoggingConfig(project_root=temp_project_dir, is_internal_dev=False)
        logger = DecisionLogger(config)

        logger.log(decision="Test Decision", context="Testing", rationale="Test")

        decisions = logger.read_today()
        assert len(decisions) == 1
        assert decisions[0].decision == "Test Decision"


# Event Logger Tests


class TestEventLogger:
    """Tests for EventLogger."""

    def test_logs_event_to_file(self, temp_project_dir: Path) -> None:
        """Should write event to JSONL file."""
        config = LoggingConfig(project_root=temp_project_dir, is_internal_dev=False)
        logger = EventLogger(config)

        entry = logger.log(
            category=EventCategory.SESSION_START,
            message="Session started",
        )

        log_file = config.events_dir / f"{date.today().isoformat()}.jsonl"
        assert log_file.exists()

        content = log_file.read_text()
        data = json.loads(content.strip())
        assert data["category"] == "session.start"
        assert data["entry_id"] == entry.entry_id

    def test_log_session_start(self, temp_project_dir: Path) -> None:
        """Should log session start with convenience method."""
        config = LoggingConfig(project_root=temp_project_dir, is_internal_dev=False)
        logger = EventLogger(config)

        entry = logger.log_session_start(details={"project": "test"})

        assert entry.category == EventCategory.SESSION_START
        assert entry.details["project"] == "test"

    def test_log_workflow_completed(self, temp_project_dir: Path) -> None:
        """Should log workflow completion with convenience method."""
        config = LoggingConfig(project_root=temp_project_dir, is_internal_dev=False)
        logger = EventLogger(config)

        entry = logger.log_workflow_completed(
            phase="implement",
            task_id="task-42",
            duration_ms=5000,
        )

        assert entry.category == EventCategory.WORKFLOW_COMPLETED
        assert entry.workflow_phase == "implement"
        assert entry.task_id == "task-42"
        assert entry.duration_ms == 5000

    def test_log_task_status_changed(self, temp_project_dir: Path) -> None:
        """Should log task status change."""
        config = LoggingConfig(project_root=temp_project_dir, is_internal_dev=False)
        logger = EventLogger(config)

        entry = logger.log_task_status_changed(
            task_id="task-123",
            old_status="To Do",
            new_status="In Progress",
        )

        assert entry.category == EventCategory.TASK_STATUS_CHANGED
        assert entry.task_id == "task-123"
        assert entry.details["old_status"] == "To Do"
        assert entry.details["new_status"] == "In Progress"

    def test_log_hook_executed(self, temp_project_dir: Path) -> None:
        """Should log hook execution."""
        config = LoggingConfig(project_root=temp_project_dir, is_internal_dev=False)
        logger = EventLogger(config)

        entry = logger.log_hook_executed(
            hook_name="session-start",
            event_type="session.start",
            success=True,
            duration_ms=100,
        )

        assert entry.category == EventCategory.HOOK_EXECUTED
        assert entry.details["hook_name"] == "session-start"
        assert entry.success is True

    def test_log_git_commit(self, temp_project_dir: Path) -> None:
        """Should log git commit event."""
        config = LoggingConfig(project_root=temp_project_dir, is_internal_dev=False)
        logger = EventLogger(config)

        entry = logger.log_git_commit(
            commit_hash="abc123",
            message="Add feature X",
            files_changed=5,
        )

        assert entry.category == EventCategory.GIT_COMMIT
        assert entry.details["commit_hash"] == "abc123"
        assert entry.details["files_changed"] == 5

    def test_read_today_returns_events(self, temp_project_dir: Path) -> None:
        """Should read back events from today's log."""
        config = LoggingConfig(project_root=temp_project_dir, is_internal_dev=False)
        logger = EventLogger(config)

        logger.log(category=EventCategory.SESSION_START, message="Test event")

        events = logger.read_today()
        assert len(events) == 1
        assert events[0].message == "Test event"


# Integration Tests


class TestLoggingIntegration:
    """Integration tests for the logging system."""

    def test_dual_path_behavior(
        self, temp_project_dir: Path, temp_flowspec_repo: Path
    ) -> None:
        """User projects and flowspec repo should use different paths."""
        user_config = get_config(temp_project_dir)
        dev_config = get_config(temp_flowspec_repo)

        # User project logs to ./logs/
        assert "logs/events" in str(user_config.events_dir)
        assert ".flowspec" not in str(user_config.events_dir)

        # Dev repo logs to .flowspec/logs/
        assert ".flowspec/logs/events" in str(dev_config.events_dir)

    def test_environment_variable_override(
        self, temp_project_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should respect FLOWSPEC_PROJECT_ROOT environment variable."""
        clear_config_cache()
        monkeypatch.setenv("FLOWSPEC_PROJECT_ROOT", str(temp_project_dir))

        config = get_config()
        assert config.project_root == temp_project_dir
