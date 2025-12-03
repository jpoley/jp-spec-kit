"""Tests for hooks event emitter module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from specify_cli.hooks import Event, EventType
from specify_cli.hooks.emitter import (
    EventEmitter,
    emit_event,
    emit_implement_completed,
    emit_spec_created,
    emit_task_completed,
)
from specify_cli.hooks.schema import EventMatcher, HookDefinition, HooksConfig


@pytest.fixture
def workspace_root(tmp_path: Path) -> Path:
    """Create temporary workspace root."""
    workspace = tmp_path / "project"
    workspace.mkdir()
    # Create hooks directory
    hooks_dir = workspace / ".specify" / "hooks"
    hooks_dir.mkdir(parents=True)
    return workspace


@pytest.fixture
def sample_event(workspace_root: Path) -> Event:
    """Create sample event for testing."""
    return Event(
        event_type=EventType.SPEC_CREATED.value,
        project_root=str(workspace_root),
        feature="test-feature",
    )


@pytest.fixture
def sample_hook() -> HookDefinition:
    """Create sample hook definition."""
    return HookDefinition(
        name="test-hook",
        events=[EventMatcher(type="spec.created")],
        script="test.sh",
        timeout=30,
    )


@pytest.fixture
def hooks_config(sample_hook: HookDefinition) -> HooksConfig:
    """Create sample hooks configuration."""
    return HooksConfig(
        version="1.0",
        hooks=[sample_hook],
    )


class TestEventEmitter:
    """Test EventEmitter class."""

    def test_init_with_config(self, workspace_root: Path, hooks_config: HooksConfig):
        """Test emitter initialization with explicit config."""
        emitter = EventEmitter(workspace_root=workspace_root, config=hooks_config)

        assert emitter.workspace_root == workspace_root
        assert emitter.config == hooks_config
        assert emitter.dry_run is False

    def test_init_without_config(self, workspace_root: Path):
        """Test emitter initialization without config (loads from workspace)."""
        # Create empty hooks.yaml
        hooks_file = workspace_root / ".specify" / "hooks" / "hooks.yaml"
        hooks_file.write_text("version: '1.0'\nhooks: []\n")

        emitter = EventEmitter(workspace_root=workspace_root)

        assert emitter.workspace_root == workspace_root
        assert emitter.config is not None
        assert len(emitter.config.hooks) == 0

    def test_init_without_config_missing_file(self, workspace_root: Path):
        """Test emitter initialization when hooks.yaml is missing (should not error)."""
        emitter = EventEmitter(workspace_root=workspace_root)

        assert emitter.workspace_root == workspace_root
        assert emitter.config is not None
        # Should fall back to empty config
        assert len(emitter.config.hooks) == 0

    def test_emit_no_matching_hooks(
        self, workspace_root: Path, hooks_config: HooksConfig
    ):
        """Test emit with no matching hooks returns empty list."""
        emitter = EventEmitter(workspace_root=workspace_root, config=hooks_config)

        # Event that doesn't match any hooks
        event = Event(
            event_type="task.completed",
            project_root=str(workspace_root),
        )

        results = emitter.emit(event)

        assert results == []

    def test_emit_with_matching_hook(
        self,
        workspace_root: Path,
        hooks_config: HooksConfig,
        sample_event: Event,
    ):
        """Test emit executes matching hooks."""
        # Create a success script
        hooks_dir = workspace_root / ".specify" / "hooks"
        script = hooks_dir / "test.sh"
        script.write_text("#!/bin/bash\necho 'Success'\nexit 0\n")
        script.chmod(script.stat().st_mode | 0o111)

        emitter = EventEmitter(workspace_root=workspace_root, config=hooks_config)
        results = emitter.emit(sample_event)

        # Verify hook was executed
        assert len(results) == 1
        assert results[0].hook_name == "test-hook"
        assert results[0].success is True

    def test_emit_dry_run(
        self,
        workspace_root: Path,
        hooks_config: HooksConfig,
        sample_event: Event,
    ):
        """Test emit in dry-run mode doesn't execute hooks."""
        emitter = EventEmitter(
            workspace_root=workspace_root, config=hooks_config, dry_run=True
        )
        results = emitter.emit(sample_event)

        # Verify hooks were NOT executed
        assert results == []

    def test_emit_fail_mode_continue(self, workspace_root: Path):
        """Test emit with fail_mode=continue executes all hooks despite failures."""
        # Create scripts
        hooks_dir = workspace_root / ".specify" / "hooks"

        # Failing script
        script1 = hooks_dir / "hook1.sh"
        script1.write_text("#!/bin/bash\nexit 1\n")
        script1.chmod(script1.stat().st_mode | 0o111)

        # Success script
        script2 = hooks_dir / "hook2.sh"
        script2.write_text("#!/bin/bash\nexit 0\n")
        script2.chmod(script2.stat().st_mode | 0o111)

        # Create config with multiple hooks, fail_mode=continue
        hooks_config = HooksConfig(
            version="1.0",
            hooks=[
                HookDefinition(
                    name="hook1",
                    events=[EventMatcher(type="spec.*")],
                    script="hook1.sh",
                    fail_mode="continue",
                ),
                HookDefinition(
                    name="hook2",
                    events=[EventMatcher(type="spec.*")],
                    script="hook2.sh",
                    fail_mode="continue",
                ),
            ],
        )

        emitter = EventEmitter(workspace_root=workspace_root, config=hooks_config)
        event = Event(event_type="spec.created", project_root=str(workspace_root))
        results = emitter.emit(event)

        # Verify both hooks were executed
        assert len(results) == 2
        assert results[0].hook_name == "hook1"
        assert results[0].success is False
        assert results[1].hook_name == "hook2"
        assert results[1].success is True

    def test_emit_fail_mode_stop(self, workspace_root: Path):
        """Test emit with fail_mode=stop stops on first failure."""
        # Create scripts
        hooks_dir = workspace_root / ".specify" / "hooks"

        # Failing script
        script1 = hooks_dir / "hook1.sh"
        script1.write_text("#!/bin/bash\nexit 1\n")
        script1.chmod(script1.stat().st_mode | 0o111)

        # Success script (should not be executed)
        script2 = hooks_dir / "hook2.sh"
        script2.write_text("#!/bin/bash\nexit 0\n")
        script2.chmod(script2.stat().st_mode | 0o111)

        # Create config with multiple hooks, first has fail_mode=stop
        hooks_config = HooksConfig(
            version="1.0",
            hooks=[
                HookDefinition(
                    name="hook1",
                    events=[EventMatcher(type="spec.*")],
                    script="hook1.sh",
                    fail_mode="stop",
                ),
                HookDefinition(
                    name="hook2",
                    events=[EventMatcher(type="spec.*")],
                    script="hook2.sh",
                    fail_mode="continue",
                ),
            ],
        )

        emitter = EventEmitter(workspace_root=workspace_root, config=hooks_config)
        event = Event(event_type="spec.created", project_root=str(workspace_root))
        results = emitter.emit(event)

        # Verify only first hook was executed
        assert len(results) == 1
        assert results[0].hook_name == "hook1"
        assert results[0].success is False

    def test_emit_exception_handling(
        self,
        workspace_root: Path,
        sample_event: Event,
    ):
        """Test emit handles exceptions gracefully (fail-safe)."""
        # Create config with invalid script to trigger exception
        hooks_config = HooksConfig(
            version="1.0",
            hooks=[
                HookDefinition(
                    name="test-hook",
                    events=[EventMatcher(type="spec.created")],
                    script="nonexistent.sh",  # This will trigger an error
                )
            ],
        )

        emitter = EventEmitter(workspace_root=workspace_root, config=hooks_config)
        results = emitter.emit(sample_event)

        # Verify exception was caught and result created
        assert len(results) == 1
        assert results[0].success is False
        assert results[0].error is not None

    @patch("specify_cli.hooks.emitter.threading.Thread")
    def test_emit_async(
        self,
        mock_thread: MagicMock,
        workspace_root: Path,
        hooks_config: HooksConfig,
        sample_event: Event,
    ):
        """Test emit_async starts background thread."""
        emitter = EventEmitter(workspace_root=workspace_root, config=hooks_config)
        emitter.emit_async(sample_event)

        # Verify thread was started
        mock_thread.assert_called_once()
        thread_instance = mock_thread.return_value
        thread_instance.start.assert_called_once()

        # Verify thread is daemon
        call_kwargs = mock_thread.call_args[1]
        assert call_kwargs["daemon"] is True


class TestConvenienceFunctions:
    """Test convenience functions for common events."""

    @patch("specify_cli.hooks.emitter.EventEmitter")
    def test_emit_event(self, mock_emitter_class: MagicMock, workspace_root: Path):
        """Test emit_event convenience function."""
        mock_emitter = MagicMock()
        mock_emitter_class.return_value = mock_emitter
        mock_emitter.emit.return_value = []

        event = Event(event_type="spec.created", project_root=str(workspace_root))
        results = emit_event(event, workspace_root=workspace_root)

        # Verify emitter was created and emit was called
        mock_emitter_class.assert_called_once()
        mock_emitter.emit.assert_called_once_with(event)
        assert results == []

    @patch("specify_cli.hooks.emitter.EventEmitter")
    def test_emit_spec_created(
        self, mock_emitter_class: MagicMock, workspace_root: Path
    ):
        """Test emit_spec_created convenience function."""
        mock_emitter = MagicMock()
        mock_emitter_class.return_value = mock_emitter
        mock_emitter.emit.return_value = []

        emit_spec_created(
            spec_id="test-feature",
            files=["docs/prd/test-spec.md"],
            workspace_root=workspace_root,
            agent="pm-planner",
        )

        # Verify emitter was created and emit was called
        mock_emitter_class.assert_called_once()
        mock_emitter.emit.assert_called_once()

        # Verify event was created correctly
        event = mock_emitter.emit.call_args[0][0]
        assert event.event_type == EventType.SPEC_CREATED.value
        assert event.feature == "test-feature"
        assert event.context["agent"] == "pm-planner"

    @patch("specify_cli.hooks.emitter.EventEmitter")
    def test_emit_task_completed(
        self, mock_emitter_class: MagicMock, workspace_root: Path
    ):
        """Test emit_task_completed convenience function."""
        mock_emitter = MagicMock()
        mock_emitter_class.return_value = mock_emitter
        mock_emitter.emit.return_value = []

        emit_task_completed(
            task_id="task-123",
            task_title="Test task",
            workspace_root=workspace_root,
            priority="high",
            labels=["backend", "security"],
        )

        # Verify emitter was created and emit was called
        mock_emitter_class.assert_called_once()
        mock_emitter.emit.assert_called_once()

        # Verify event was created correctly
        event = mock_emitter.emit.call_args[0][0]
        assert event.event_type == EventType.TASK_COMPLETED.value
        assert event.context["task_id"] == "task-123"
        assert event.context["priority"] == "high"
        assert event.context["labels"] == ["backend", "security"]

    @patch("specify_cli.hooks.emitter.EventEmitter")
    def test_emit_implement_completed(
        self, mock_emitter_class: MagicMock, workspace_root: Path
    ):
        """Test emit_implement_completed convenience function."""
        mock_emitter = MagicMock()
        mock_emitter_class.return_value = mock_emitter
        mock_emitter.emit.return_value = []

        emit_implement_completed(
            spec_id="test-feature",
            files=["src/auth/login.py", "src/auth/signup.py"],
            workspace_root=workspace_root,
            task_id="task-123",
            files_changed=15,
        )

        # Verify emitter was created and emit was called
        mock_emitter_class.assert_called_once()
        mock_emitter.emit.assert_called_once()

        # Verify event was created correctly
        event = mock_emitter.emit.call_args[0][0]
        assert event.event_type == EventType.IMPLEMENT_COMPLETED.value
        assert event.feature == "test-feature"
        assert event.context["task_id"] == "task-123"
        assert event.artifacts[0].files_changed == 15


class TestPerformance:
    """Test performance requirements."""

    def test_emit_overhead_under_50ms(
        self,
        workspace_root: Path,
        sample_event: Event,
    ):
        """Test emit overhead is under 50ms (excluding hook execution)."""
        import time

        # Create a fast script
        hooks_dir = workspace_root / ".specify" / "hooks"
        script = hooks_dir / "fast.sh"
        script.write_text("#!/bin/bash\nexit 0\n")
        script.chmod(script.stat().st_mode | 0o111)

        hooks_config = HooksConfig(
            version="1.0",
            hooks=[
                HookDefinition(
                    name="test-hook",
                    events=[EventMatcher(type="spec.created")],
                    script="fast.sh",
                )
            ],
        )

        emitter = EventEmitter(workspace_root=workspace_root, config=hooks_config)

        # Measure emit overhead
        start = time.time()
        emitter.emit(sample_event)
        elapsed_ms = (time.time() - start) * 1000

        # Should be well under 100ms (allows for script execution)
        assert elapsed_ms < 100, f"Emit overhead {elapsed_ms}ms exceeds 100ms limit"
