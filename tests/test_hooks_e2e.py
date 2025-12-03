"""End-to-end tests for jp-spec-kit hooks system.

This test suite validates the complete hooks workflow from configuration
to execution, including integration between all components:
- Event emission via CLI
- Hook configuration validation
- Script execution and security
- Audit logging
- Error handling and fail modes

These tests complement unit/integration tests by validating entire
workflows as a user would experience them.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest
from typer.testing import CliRunner

from specify_cli.hooks.cli import hooks_app

runner = CliRunner()


# --- Fixtures ---


@pytest.fixture
def e2e_workspace(tmp_path: Path) -> Path:
    """Create complete workspace for E2E testing."""
    workspace = tmp_path / "project"
    workspace.mkdir()

    # Create hooks directory
    hooks_dir = workspace / ".specify" / "hooks"
    hooks_dir.mkdir(parents=True)

    return workspace


@pytest.fixture
def quality_gate_config(e2e_workspace: Path) -> Path:
    """Create realistic quality gate hooks configuration."""
    hooks_dir = e2e_workspace / ".specify" / "hooks"
    config_file = hooks_dir / "hooks.yaml"

    config_content = """
version: "1.0"
hooks:
  - name: run-unit-tests
    events:
      - type: implement.completed
    script: run-tests.sh
    timeout: 60
    fail_mode: stop
    env:
      TEST_ENV: ci

  - name: update-changelog
    events:
      - type: spec.created
      - type: spec.updated
    script: update-changelog.sh
    timeout: 30
    fail_mode: continue

  - name: notify-slack
    events:
      - type: validate.completed
    command: echo "Validation completed for $HOOK_EVENT"
    timeout: 10
    fail_mode: continue
"""

    config_file.write_text(config_content)

    # Create test scripts
    test_script = hooks_dir / "run-tests.sh"
    test_script.write_text(
        "#!/bin/bash\n"
        "echo 'Running tests...'\n"
        "echo 'Test environment: '$TEST_ENV\n"
        "sleep 0.1\n"
        "echo 'Tests passed'\n"
        "exit 0\n"
    )
    test_script.chmod(0o755)

    changelog_script = hooks_dir / "update-changelog.sh"
    changelog_script.write_text(
        "#!/bin/bash\n"
        "echo 'Updating changelog...'\n"
        "echo 'Feature: '$HOOK_EVENT\n"
        "exit 0\n"
    )
    changelog_script.chmod(0o755)

    return config_file


@pytest.fixture
def failing_hook_config(e2e_workspace: Path) -> Path:
    """Create configuration with a failing hook."""
    hooks_dir = e2e_workspace / ".specify" / "hooks"
    config_file = hooks_dir / "hooks.yaml"

    config_content = """
version: "1.0"
hooks:
  - name: quality-check-strict
    events:
      - type: implement.completed
    script: quality-check.sh
    timeout: 30
    fail_mode: stop

  - name: optional-notification
    events:
      - type: implement.completed
    script: notify.sh
    timeout: 10
    fail_mode: continue
"""

    config_file.write_text(config_content)

    # Create failing script
    quality_script = hooks_dir / "quality-check.sh"
    quality_script.write_text(
        "#!/bin/bash\n"
        "echo 'Quality check failed' >&2\n"
        "exit 1\n"
    )
    quality_script.chmod(0o755)

    # Create success script (should not run due to fail_mode: stop)
    notify_script = hooks_dir / "notify.sh"
    notify_script.write_text(
        "#!/bin/bash\n"
        "echo 'Notification sent'\n"
        "exit 0\n"
    )
    notify_script.chmod(0o755)

    return config_file


@pytest.fixture
def timeout_hook_config(e2e_workspace: Path) -> Path:
    """Create configuration with a hook that times out."""
    hooks_dir = e2e_workspace / ".specify" / "hooks"
    config_file = hooks_dir / "hooks.yaml"

    config_content = """
version: "1.0"
hooks:
  - name: slow-process
    events:
      - type: spec.created
    script: slow.sh
    timeout: 1
    fail_mode: continue
"""

    config_file.write_text(config_content)

    # Create script that exceeds timeout
    slow_script = hooks_dir / "slow.sh"
    slow_script.write_text(
        "#!/bin/bash\n"
        "echo 'Starting slow process...'\n"
        "sleep 5\n"
        "echo 'This should not print'\n"
        "exit 0\n"
    )
    slow_script.chmod(0o755)

    return config_file


@pytest.fixture
def wildcard_hook_config(e2e_workspace: Path) -> Path:
    """Create configuration with wildcard event matching."""
    hooks_dir = e2e_workspace / ".specify" / "hooks"
    config_file = hooks_dir / "hooks.yaml"

    config_content = """
version: "1.0"
hooks:
  - name: catch-all-tasks
    events:
      - type: task.*
    script: task-handler.sh
    timeout: 30
    fail_mode: continue

  - name: spec-events-only
    events:
      - type: spec.created
    script: spec-handler.sh
    timeout: 30
    fail_mode: continue
"""

    config_file.write_text(config_content)

    # Create scripts
    task_script = hooks_dir / "task-handler.sh"
    task_script.write_text(
        "#!/bin/bash\n"
        "echo 'Task event handled'\n"
        "exit 0\n"
    )
    task_script.chmod(0o755)

    spec_script = hooks_dir / "spec-handler.sh"
    spec_script.write_text(
        "#!/bin/bash\n"
        "echo 'Spec event handled'\n"
        "exit 0\n"
    )
    spec_script.chmod(0o755)

    return config_file


# --- E2E Test Cases ---


class TestFullWorkflowEmitAndExecute:
    """Test complete event → hook → execution workflow."""

    def test_quality_gate_workflow(
        self, e2e_workspace: Path, quality_gate_config: Path
    ):
        """Test realistic quality gate workflow: emit → hooks execute → audit log."""
        # Step 1: Validate configuration
        result = runner.invoke(
            hooks_app,
            [
                "validate",
                "--project-root",
                str(e2e_workspace),
            ],
        )
        assert result.exit_code == 0
        assert "Validation passed" in result.stdout

        # Step 2: List hooks to verify configuration
        result = runner.invoke(
            hooks_app,
            [
                "list",
                "--project-root",
                str(e2e_workspace),
            ],
        )
        assert result.exit_code == 0
        assert "run-unit-tests" in result.stdout
        assert "update-changelog" in result.stdout
        assert "notify-slack" in result.stdout

        # Step 3: Emit implement.completed event
        result = runner.invoke(
            hooks_app,
            [
                "emit",
                "implement.completed",
                "--spec-id",
                "auth-feature",
                "--file",
                "src/auth/login.py",
                "--file",
                "src/auth/signup.py",
                "--project-root",
                str(e2e_workspace),
            ],
        )
        assert result.exit_code == 0
        assert "run-unit-tests" in result.stdout
        assert "All hooks succeeded" in result.stdout

        # Step 4: Verify audit log
        audit_log_path = e2e_workspace / ".specify" / "hooks" / "audit.log"
        assert audit_log_path.exists()

        audit_lines = audit_log_path.read_text().strip().split("\n")
        assert len(audit_lines) >= 1

        # Parse and verify audit entry
        audit_record = json.loads(audit_lines[-1])
        assert audit_record["hook_name"] == "run-unit-tests"
        assert audit_record["event_type"] == "implement.completed"
        assert audit_record["success"] is True
        assert audit_record["exit_code"] == 0
        assert "duration_ms" in audit_record

        # Step 5: View audit log via CLI
        result = runner.invoke(
            hooks_app,
            [
                "audit",
                "--tail",
                "5",
                "--project-root",
                str(e2e_workspace),
            ],
        )
        assert result.exit_code == 0
        assert "run-unit-tests" in result.stdout

    def test_multiple_events_trigger_different_hooks(
        self, e2e_workspace: Path, quality_gate_config: Path
    ):
        """Test that different events trigger correct hooks."""
        # Emit spec.created (should trigger update-changelog)
        result = runner.invoke(
            hooks_app,
            [
                "emit",
                "spec.created",
                "--spec-id",
                "new-feature",
                "--project-root",
                str(e2e_workspace),
            ],
        )
        assert result.exit_code == 0
        assert "update-changelog" in result.stdout
        assert "run-unit-tests" not in result.stdout

        # Emit validate.completed (should trigger notify-slack)
        result = runner.invoke(
            hooks_app,
            [
                "emit",
                "validate.completed",
                "--spec-id",
                "new-feature",
                "--project-root",
                str(e2e_workspace),
            ],
        )
        assert result.exit_code == 0
        assert "notify-slack" in result.stdout

        # Verify audit log has both events
        audit_log_path = e2e_workspace / ".specify" / "hooks" / "audit.log"
        audit_lines = audit_log_path.read_text().strip().split("\n")
        assert len(audit_lines) >= 2

        event_types = [json.loads(line)["event_type"] for line in audit_lines]
        assert "spec.created" in event_types
        assert "validate.completed" in event_types


class TestDryRunMode:
    """Test dry-run mode doesn't execute hooks."""

    def test_dry_run_shows_matching_hooks_but_doesnt_execute(
        self, e2e_workspace: Path, quality_gate_config: Path
    ):
        """Test dry-run shows what would run without executing."""
        result = runner.invoke(
            hooks_app,
            [
                "emit",
                "implement.completed",
                "--spec-id",
                "test",
                "--dry-run",
                "--project-root",
                str(e2e_workspace),
            ],
        )

        assert result.exit_code == 0
        assert "DRY RUN MODE" in result.stdout

        # Verify no audit log created
        audit_log_path = e2e_workspace / ".specify" / "hooks" / "audit.log"
        assert not audit_log_path.exists()


class TestDisabledHooks:
    """Test disabled hooks are skipped."""

    def test_disabled_hook_not_executed(self, e2e_workspace: Path):
        """Test that disabled hooks are not executed."""
        hooks_dir = e2e_workspace / ".specify" / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)

        config_file = hooks_dir / "hooks.yaml"
        config_content = """
version: "1.0"
hooks:
  - name: enabled-hook
    events:
      - type: spec.created
    command: echo "Enabled"
    timeout: 10
    fail_mode: continue

  - name: disabled-hook
    events:
      - type: spec.created
    command: echo "Disabled"
    timeout: 10
    fail_mode: continue
    enabled: false
"""
        config_file.write_text(config_content)

        result = runner.invoke(
            hooks_app,
            [
                "emit",
                "spec.created",
                "--spec-id",
                "test",
                "--project-root",
                str(e2e_workspace),
            ],
        )

        assert result.exit_code == 0
        assert "enabled-hook" in result.stdout
        assert "disabled-hook" not in result.stdout


class TestFailModeStop:
    """Test fail_mode: stop halts workflow."""

    def test_fail_stop_halts_on_first_failure(
        self, e2e_workspace: Path, failing_hook_config: Path
    ):
        """Test that fail_mode: stop prevents subsequent hooks from running."""
        result = runner.invoke(
            hooks_app,
            [
                "emit",
                "implement.completed",
                "--spec-id",
                "test",
                "--project-root",
                str(e2e_workspace),
            ],
        )

        # Emit should succeed even though hook failed
        assert result.exit_code == 0

        # First hook should have executed and failed
        assert "quality-check-strict" in result.stdout

        # Verify audit log shows only failed hook, not subsequent ones
        audit_log_path = e2e_workspace / ".specify" / "hooks" / "audit.log"
        audit_lines = audit_log_path.read_text().strip().split("\n")

        # Should only have 1 entry (quality-check-strict)
        assert len(audit_lines) == 1

        audit_record = json.loads(audit_lines[0])
        assert audit_record["hook_name"] == "quality-check-strict"
        assert audit_record["success"] is False


class TestTimeoutEnforcement:
    """Test hook timeout is enforced."""

    def test_timeout_kills_slow_hook(
        self, e2e_workspace: Path, timeout_hook_config: Path
    ):
        """Test that hooks exceeding timeout are killed."""
        start_time = time.time()

        runner.invoke(
            hooks_app,
            [
                "emit",
                "spec.created",
                "--spec-id",
                "test",
                "--project-root",
                str(e2e_workspace),
            ],
        )

        elapsed_time = time.time() - start_time

        # Should complete quickly (timeout=1s, not the script's sleep 5s)
        assert elapsed_time < 3.0  # Allow some overhead

        # Verify audit log shows timeout
        audit_log_path = e2e_workspace / ".specify" / "hooks" / "audit.log"
        audit_lines = audit_log_path.read_text().strip().split("\n")

        audit_record = json.loads(audit_lines[0])
        assert audit_record["hook_name"] == "slow-process"
        assert audit_record["success"] is False
        assert audit_record["error"] is not None
        assert "timed out" in audit_record["error"].lower()


class TestSecurityPathValidation:
    """Test scripts outside hooks dir are blocked."""

    def test_path_traversal_blocked(self, e2e_workspace: Path):
        """Test that path traversal in script path is blocked."""
        hooks_dir = e2e_workspace / ".specify" / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)

        config_file = hooks_dir / "hooks.yaml"
        config_content = """
version: "1.0"
hooks:
  - name: evil-hook
    events:
      - type: spec.created
    script: ../../etc/passwd
    timeout: 10
    fail_mode: continue
"""
        config_file.write_text(config_content)

        # Validation should catch this
        result = runner.invoke(
            hooks_app,
            [
                "validate",
                "--project-root",
                str(e2e_workspace),
            ],
        )

        assert result.exit_code == 1
        assert "path traversal" in result.stdout.lower()

    def test_absolute_path_blocked(self, e2e_workspace: Path):
        """Test that absolute paths in script field are blocked."""
        hooks_dir = e2e_workspace / ".specify" / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)

        config_file = hooks_dir / "hooks.yaml"
        config_content = """
version: "1.0"
hooks:
  - name: absolute-path-hook
    events:
      - type: spec.created
    script: /usr/bin/evil.sh
    timeout: 10
    fail_mode: continue
"""
        config_file.write_text(config_content)

        # Validation should catch this
        result = runner.invoke(
            hooks_app,
            [
                "validate",
                "--project-root",
                str(e2e_workspace),
            ],
        )

        assert result.exit_code == 1
        assert "relative path" in result.stdout.lower()


class TestAuditLogIntegrity:
    """Test audit log captures all executions."""

    def test_audit_log_records_all_executions(
        self, e2e_workspace: Path, quality_gate_config: Path
    ):
        """Test that every hook execution is logged to audit log."""
        # Emit multiple events
        events = [
            ("spec.created", "feature-1"),
            ("spec.updated", "feature-1"),
            ("implement.completed", "feature-1"),
            ("validate.completed", "feature-1"),
        ]

        for event_type, spec_id in events:
            runner.invoke(
                hooks_app,
                [
                    "emit",
                    event_type,
                    "--spec-id",
                    spec_id,
                    "--project-root",
                    str(e2e_workspace),
                ],
            )

        # Verify audit log
        audit_log_path = e2e_workspace / ".specify" / "hooks" / "audit.log"
        audit_lines = audit_log_path.read_text().strip().split("\n")

        # Should have entries for:
        # - spec.created → update-changelog
        # - spec.updated → update-changelog
        # - implement.completed → run-unit-tests
        # - validate.completed → notify-slack
        assert len(audit_lines) == 4

        # Verify all entries are valid JSON
        for line in audit_lines:
            record = json.loads(line)
            assert "hook_name" in record
            assert "event_type" in record
            assert "success" in record
            assert "timestamp" in record

    def test_audit_json_output(self, e2e_workspace: Path, quality_gate_config: Path):
        """Test audit log can be queried with JSON output."""
        # Execute a hook
        runner.invoke(
            hooks_app,
            [
                "emit",
                "implement.completed",
                "--spec-id",
                "test",
                "--project-root",
                str(e2e_workspace),
            ],
        )

        # Query audit log with JSON output
        result = runner.invoke(
            hooks_app,
            [
                "audit",
                "--json",
                "--project-root",
                str(e2e_workspace),
            ],
        )

        assert result.exit_code == 0

        # Parse JSON
        output = json.loads(result.stdout)
        assert "entries" in output
        assert "count" in output
        assert output["count"] >= 1


class TestWildcardEventMatching:
    """Test task.* matches task.created, task.completed."""

    def test_wildcard_matches_multiple_events(
        self, e2e_workspace: Path, wildcard_hook_config: Path
    ):
        """Test that wildcard patterns match multiple event types."""
        # Emit task.created (should match task.*)
        result = runner.invoke(
            hooks_app,
            [
                "emit",
                "task.created",
                "--task-id",
                "task-123",
                "--project-root",
                str(e2e_workspace),
            ],
        )
        assert result.exit_code == 0
        assert "catch-all-tasks" in result.stdout

        # Emit task.completed (should match task.*)
        result = runner.invoke(
            hooks_app,
            [
                "emit",
                "task.completed",
                "--task-id",
                "task-123",
                "--project-root",
                str(e2e_workspace),
            ],
        )
        assert result.exit_code == 0
        assert "catch-all-tasks" in result.stdout

        # Emit spec.created (should match spec.created only)
        result = runner.invoke(
            hooks_app,
            [
                "emit",
                "spec.created",
                "--spec-id",
                "feature",
                "--project-root",
                str(e2e_workspace),
            ],
        )
        assert result.exit_code == 0
        assert "spec-events-only" in result.stdout
        assert "catch-all-tasks" not in result.stdout


class TestScaffoldCreatesValidConfig:
    """Test scaffolded hooks.yaml is valid."""

    def test_init_creates_valid_hooks_config(self, e2e_workspace: Path):
        """Test that scaffolded hooks.yaml passes validation."""
        hooks_dir = e2e_workspace / ".specify" / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)

        # Create minimal scaffolded config
        config_file = hooks_dir / "hooks.yaml"
        scaffolded_content = """
version: "1.0"
hooks:
  - name: example-quality-gate
    events:
      - type: implement.completed
    command: echo "Quality gate passed"
    timeout: 60
    fail_mode: stop
"""
        config_file.write_text(scaffolded_content)

        # Validate scaffolded config
        result = runner.invoke(
            hooks_app,
            [
                "validate",
                "--project-root",
                str(e2e_workspace),
            ],
        )

        assert result.exit_code == 0
        assert "Validation passed" in result.stdout


class TestHookTestCommand:
    """Test individual hook testing."""

    def test_test_hook_with_mock_event(
        self, e2e_workspace: Path, quality_gate_config: Path
    ):
        """Test that hooks can be tested individually with mock events."""
        result = runner.invoke(
            hooks_app,
            [
                "test",
                "run-unit-tests",
                "implement.completed",
                "--spec-id",
                "test-feature",
                "--project-root",
                str(e2e_workspace),
            ],
        )

        assert result.exit_code == 0
        assert "Hook succeeded" in result.stdout
        assert "Tests passed" in result.stdout
