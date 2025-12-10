"""Tests for hooks runner module."""

import json
import os
import stat
from pathlib import Path

import pytest

from specify_cli.hooks import Event, EventType
from specify_cli.hooks.runner import HookResult, HookRunner
from specify_cli.hooks.schema import EventMatcher, HookDefinition


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
def success_script(workspace_root: Path) -> Path:
    """Create a test script that succeeds."""
    hooks_dir = workspace_root / ".specify" / "hooks"
    script = hooks_dir / "success.sh"
    script.write_text("#!/bin/bash\necho 'Success'\nexit 0\n")
    # Make executable
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    return script


@pytest.fixture
def failure_script(workspace_root: Path) -> Path:
    """Create a test script that fails."""
    hooks_dir = workspace_root / ".specify" / "hooks"
    script = hooks_dir / "failure.sh"
    script.write_text("#!/bin/bash\necho 'Error' >&2\nexit 1\n")
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    return script


@pytest.fixture
def timeout_script(workspace_root: Path) -> Path:
    """Create a test script that times out."""
    hooks_dir = workspace_root / ".specify" / "hooks"
    script = hooks_dir / "timeout.sh"
    script.write_text("#!/bin/bash\nsleep 10\necho 'Done'\n")
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    return script


@pytest.fixture
def event_reader_script(workspace_root: Path) -> Path:
    """Create a test script that reads HOOK_EVENT environment variable."""
    hooks_dir = workspace_root / ".specify" / "hooks"
    script = hooks_dir / "read_event.sh"
    script.write_text("#!/bin/bash\necho $HOOK_EVENT\n")
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    return script


class TestHookResult:
    """Test HookResult dataclass."""

    def test_hook_result_success(self):
        """Test HookResult for successful execution."""
        result = HookResult(
            hook_name="test-hook",
            success=True,
            exit_code=0,
            stdout="Success",
            stderr="",
            duration_ms=123,
        )

        assert result.hook_name == "test-hook"
        assert result.success is True
        assert result.exit_code == 0
        assert result.stdout == "Success"
        assert result.stderr == ""
        assert result.duration_ms == 123
        assert result.error is None

    def test_hook_result_failure(self):
        """Test HookResult for failed execution."""
        result = HookResult(
            hook_name="test-hook",
            success=False,
            exit_code=1,
            stdout="",
            stderr="Error message",
            duration_ms=123,
            error="Test error",
        )

        assert result.success is False
        assert result.exit_code == 1
        assert result.error == "Test error"

    def test_hook_result_to_dict(self):
        """Test HookResult.to_dict() conversion."""
        result = HookResult(
            hook_name="test-hook",
            success=True,
            exit_code=0,
            stdout="Success",
            stderr="",
            duration_ms=123,
            error="Test error",
        )

        d = result.to_dict()

        assert d["hook_name"] == "test-hook"
        assert d["success"] is True
        assert d["exit_code"] == 0
        assert d["stdout"] == "Success"
        assert d["stderr"] == ""
        assert d["duration_ms"] == 123
        assert d["error"] == "Test error"


class TestHookRunner:
    """Test HookRunner class."""

    def test_init_default_audit_log(self, workspace_root: Path):
        """Test runner initialization with default audit log path."""
        runner = HookRunner(workspace_root=workspace_root)

        assert runner.workspace_root == workspace_root
        assert runner.audit_log_path == workspace_root / ".specify/hooks/audit.log"
        # Verify audit log directory was created
        assert runner.audit_log_path.parent.exists()

    def test_init_custom_audit_log(self, workspace_root: Path, tmp_path: Path):
        """Test runner initialization with custom audit log path."""
        custom_log = tmp_path / "custom.log"
        runner = HookRunner(workspace_root=workspace_root, audit_log_path=custom_log)

        assert runner.audit_log_path == custom_log

    def test_run_hook_script_success(
        self, workspace_root: Path, success_script: Path, sample_event: Event
    ):
        """Test running a successful script hook."""
        hook = HookDefinition(
            name="success-hook",
            events=[EventMatcher(type="spec.*")],
            script="success.sh",
            timeout=5,
        )

        runner = HookRunner(workspace_root=workspace_root)
        result = runner.run_hook(hook, sample_event)

        assert result.hook_name == "success-hook"
        assert result.success is True
        assert result.exit_code == 0
        assert "Success" in result.stdout
        assert result.stderr == ""
        assert result.duration_ms >= 0
        assert result.error is None

    def test_run_hook_script_failure(
        self, workspace_root: Path, failure_script: Path, sample_event: Event
    ):
        """Test running a failing script hook."""
        hook = HookDefinition(
            name="failure-hook",
            events=[EventMatcher(type="spec.*")],
            script="failure.sh",
            timeout=5,
        )

        runner = HookRunner(workspace_root=workspace_root)
        result = runner.run_hook(hook, sample_event)

        assert result.hook_name == "failure-hook"
        assert result.success is False
        assert result.exit_code == 1
        assert "Error" in result.stderr
        assert result.duration_ms >= 0
        assert result.error is None

    def test_run_hook_timeout(
        self, workspace_root: Path, timeout_script: Path, sample_event: Event
    ):
        """Test hook timeout enforcement."""
        hook = HookDefinition(
            name="timeout-hook",
            events=[EventMatcher(type="spec.*")],
            script="timeout.sh",
            timeout=1,  # 1 second timeout
        )

        runner = HookRunner(workspace_root=workspace_root)
        result = runner.run_hook(hook, sample_event)

        assert result.hook_name == "timeout-hook"
        assert result.success is False
        assert result.exit_code == -1
        assert result.error is not None
        assert "timed out" in result.error.lower()

    def test_run_hook_command(self, workspace_root: Path, sample_event: Event):
        """Test running a command hook (not script)."""
        hook = HookDefinition(
            name="command-hook",
            events=[EventMatcher(type="spec.*")],
            command="echo 'Command output'",
            timeout=5,
        )

        runner = HookRunner(workspace_root=workspace_root)
        result = runner.run_hook(hook, sample_event)

        assert result.hook_name == "command-hook"
        assert result.success is True
        assert result.exit_code == 0
        assert "Command output" in result.stdout

    def test_run_hook_event_passed_to_script(
        self, workspace_root: Path, event_reader_script: Path, sample_event: Event
    ):
        """Test that event is passed to script via HOOK_EVENT environment variable."""
        hook = HookDefinition(
            name="event-reader",
            events=[EventMatcher(type="spec.*")],
            script="read_event.sh",
            timeout=5,
        )

        runner = HookRunner(workspace_root=workspace_root)
        result = runner.run_hook(hook, sample_event)

        assert result.success is True
        # Verify event JSON was passed
        event_json = result.stdout.strip()
        assert event_json != ""
        # Parse and verify it's valid JSON
        event_data = json.loads(event_json)
        assert event_data["event_type"] == EventType.SPEC_CREATED.value
        assert event_data["feature"] == "test-feature"

    def test_run_hook_custom_env(self, workspace_root: Path, sample_event: Event):
        """Test hook with custom environment variables."""
        hook = HookDefinition(
            name="env-hook",
            events=[EventMatcher(type="spec.*")],
            command="echo $CUSTOM_VAR",
            env={"CUSTOM_VAR": "custom-value"},
            timeout=5,
        )

        runner = HookRunner(workspace_root=workspace_root)
        result = runner.run_hook(hook, sample_event)

        assert result.success is True
        assert "custom-value" in result.stdout

    def test_run_hook_working_directory(
        self, workspace_root: Path, sample_event: Event
    ):
        """Test hook with custom working directory."""
        # Create subdirectory
        subdir = workspace_root / "subdir"
        subdir.mkdir()

        hook = HookDefinition(
            name="wd-hook",
            events=[EventMatcher(type="spec.*")],
            command="pwd",
            working_directory="subdir",
            timeout=5,
        )

        runner = HookRunner(workspace_root=workspace_root)
        result = runner.run_hook(hook, sample_event)

        assert result.success is True
        assert str(subdir) in result.stdout

    def test_run_hook_audit_logging(
        self, workspace_root: Path, success_script: Path, sample_event: Event
    ):
        """Test that hook execution is logged to audit log."""
        hook = HookDefinition(
            name="audit-test",
            events=[EventMatcher(type="spec.*")],
            script="success.sh",
            timeout=5,
        )

        runner = HookRunner(workspace_root=workspace_root)
        runner.run_hook(hook, sample_event)

        # Verify audit log was created
        assert runner.audit_log_path.exists()

        # Read and verify audit log entry
        audit_lines = runner.audit_log_path.read_text().strip().split("\n")
        assert len(audit_lines) == 1

        audit_record = json.loads(audit_lines[0])
        assert audit_record["hook_name"] == "audit-test"
        assert audit_record["event_type"] == EventType.SPEC_CREATED.value
        assert audit_record["success"] is True
        assert audit_record["exit_code"] == 0
        assert "timestamp" in audit_record
        assert "duration_ms" in audit_record


class TestSecurityValidation:
    """Test security validation features."""

    def test_validate_script_path_success(self, workspace_root: Path):
        """Test valid script path passes validation."""
        hooks_dir = workspace_root / ".specify" / "hooks"
        script = hooks_dir / "valid.sh"
        script.write_text("#!/bin/bash\necho 'test'\n")

        runner = HookRunner(workspace_root=workspace_root)
        validated_path = runner._validate_script_path("valid.sh")

        assert validated_path == script

    def test_validate_script_path_traversal_blocked(self, workspace_root: Path):
        """Test path traversal is blocked."""
        runner = HookRunner(workspace_root=workspace_root)

        with pytest.raises(ValueError, match="path traversal"):
            runner._validate_script_path("../etc/passwd")

    def test_validate_script_path_absolute_blocked(self, workspace_root: Path):
        """Test absolute paths are blocked."""
        runner = HookRunner(workspace_root=workspace_root)

        with pytest.raises(ValueError, match="relative path"):
            runner._validate_script_path("/usr/bin/evil.sh")

    def test_validate_script_path_outside_hooks_dir_blocked(self, workspace_root: Path):
        """Test scripts outside .specify/hooks/ are blocked."""
        runner = HookRunner(workspace_root=workspace_root)

        # Try to escape hooks directory (path traversal caught first)
        with pytest.raises(ValueError, match="path traversal"):
            runner._validate_script_path("../../evil.sh")

    def test_validate_script_not_found(self, workspace_root: Path):
        """Test validation fails for non-existent script."""
        runner = HookRunner(workspace_root=workspace_root)

        with pytest.raises(ValueError, match="not found"):
            runner._validate_script_path("nonexistent.sh")

    def test_sanitize_env_includes_hook_metadata(
        self, workspace_root: Path, sample_event: Event
    ):
        """Test sanitized environment includes hook metadata."""
        hook = HookDefinition(
            name="test-hook",
            events=[EventMatcher(type="spec.*")],
            script="test.sh",
        )

        runner = HookRunner(workspace_root=workspace_root)
        env = runner._sanitize_env(hook, sample_event)

        # Verify hook metadata
        assert env["HOOK_NAME"] == "test-hook"
        assert env["HOOK_WORKSPACE"] == str(workspace_root)
        assert "HOOK_EVENT" in env

        # Verify event JSON
        event_data = json.loads(env["HOOK_EVENT"])
        assert event_data["event_type"] == EventType.SPEC_CREATED.value

    def test_sanitize_env_includes_system_vars(
        self, workspace_root: Path, sample_event: Event
    ):
        """Test sanitized environment includes essential system variables."""
        hook = HookDefinition(
            name="test-hook",
            events=[EventMatcher(type="spec.*")],
            script="test.sh",
        )

        runner = HookRunner(workspace_root=workspace_root)
        env = runner._sanitize_env(hook, sample_event)

        # Verify essential system variables are present (if set)
        if "PATH" in os.environ:
            assert "PATH" in env
        if "HOME" in os.environ:
            assert "HOME" in env

    def test_resolve_working_directory_current(self, workspace_root: Path):
        """Test resolving current directory (.)."""
        runner = HookRunner(workspace_root=workspace_root)
        wd = runner._resolve_working_directory(".")

        assert wd == workspace_root

    def test_resolve_working_directory_subdirectory(self, workspace_root: Path):
        """Test resolving subdirectory."""
        subdir = workspace_root / "subdir"
        subdir.mkdir()

        runner = HookRunner(workspace_root=workspace_root)
        wd = runner._resolve_working_directory("subdir")

        assert wd == subdir

    def test_resolve_working_directory_traversal_blocked(self, workspace_root: Path):
        """Test path traversal in working directory is blocked."""
        runner = HookRunner(workspace_root=workspace_root)

        with pytest.raises(ValueError, match="path traversal"):
            runner._resolve_working_directory("../etc")

    def test_resolve_working_directory_absolute_blocked(self, workspace_root: Path):
        """Test absolute working directory is blocked."""
        runner = HookRunner(workspace_root=workspace_root)

        with pytest.raises(ValueError, match="must be relative"):
            runner._resolve_working_directory("/tmp")

    def test_resolve_working_directory_outside_project_blocked(
        self, workspace_root: Path
    ):
        """Test working directory outside project is blocked."""
        runner = HookRunner(workspace_root=workspace_root)

        # Path traversal check happens first
        with pytest.raises(ValueError, match="path traversal"):
            runner._resolve_working_directory("../../outside")


class TestMaxTimeout:
    """Test maximum timeout enforcement."""

    def test_timeout_under_max(
        self, workspace_root: Path, success_script: Path, sample_event: Event
    ):
        """Test timeout under maximum is accepted."""
        hook = HookDefinition(
            name="test-hook",
            events=[EventMatcher(type="spec.*")],
            script="success.sh",
            timeout=300,  # 5 minutes
        )

        runner = HookRunner(workspace_root=workspace_root)
        # Should not raise error
        result = runner.run_hook(hook, sample_event)
        assert result.success is True

    def test_timeout_clamped_to_max(
        self, workspace_root: Path, success_script: Path, sample_event: Event
    ):
        """Test timeout over maximum is clamped to MAX_TIMEOUT_SECONDS."""
        hook = HookDefinition(
            name="test-hook",
            events=[EventMatcher(type="spec.*")],
            script="success.sh",
            timeout=700,  # Over 600s max
        )

        runner = HookRunner(workspace_root=workspace_root)
        # Should not raise error, timeout will be clamped to 600s
        result = runner.run_hook(hook, sample_event)
        assert result.success is True


class TestErrorHandling:
    """Test error handling and fail-safe behavior."""

    def test_run_hook_invalid_script_path(
        self, workspace_root: Path, sample_event: Event
    ):
        """Test running hook with invalid script path."""
        hook = HookDefinition(
            name="invalid-hook",
            events=[EventMatcher(type="spec.*")],
            script="../../evil.sh",
            timeout=5,
        )

        runner = HookRunner(workspace_root=workspace_root)
        result = runner.run_hook(hook, sample_event)

        # Should return error result, not raise exception
        assert result.success is False
        assert result.exit_code == -1
        assert result.error is not None

    def test_run_hook_unsupported_method(
        self, workspace_root: Path, sample_event: Event
    ):
        """Test running hook with unsupported execution method (webhook)."""
        hook = HookDefinition(
            name="webhook-hook",
            events=[EventMatcher(type="spec.*")],
            webhook={"url": "http://example.com"},
            timeout=5,
        )

        runner = HookRunner(workspace_root=workspace_root)
        result = runner.run_hook(hook, sample_event)

        # Should return error result for unsupported method
        assert result.success is False
        assert result.exit_code == -1
        assert "not supported" in result.error.lower()
