"""Tests for hooks CLI commands.

Tests the specify hooks CLI subcommands:
- emit: Event emission and hook triggering
- validate: Hook configuration validation
- list: Hook listing
- audit: Audit log viewing
- test: Individual hook testing
"""

from __future__ import annotations

import json

import pytest
from typer.testing import CliRunner

from specify_cli.hooks.cli import hooks_app
from specify_cli.hooks.security import AuditLogger

# Create CLI runner
runner = CliRunner()


# --- Fixtures ---


@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace with hooks directory."""
    hooks_dir = tmp_path / ".specify" / "hooks"
    hooks_dir.mkdir(parents=True)
    return tmp_path


@pytest.fixture
def sample_hooks_config(temp_workspace):
    """Create sample hooks.yaml for testing."""
    hooks_dir = temp_workspace / ".specify" / "hooks"
    config_file = hooks_dir / "hooks.yaml"

    config_content = """
version: "1.0"
hooks:
  - name: test-hook
    events:
      - type: spec.created
    script: test.sh
    timeout: 30
    fail_mode: continue

  - name: quality-gate
    events:
      - type: implement.completed
    command: echo "Quality gate passed"
    timeout: 60
    fail_mode: stop
"""

    config_file.write_text(config_content)

    # Create test script
    test_script = hooks_dir / "test.sh"
    test_script.write_text("#!/bin/bash\necho 'Test hook executed'\nexit 0\n")
    test_script.chmod(0o755)

    return config_file


@pytest.fixture
def sample_audit_log(temp_workspace):
    """Create sample audit log."""
    audit_log_path = temp_workspace / ".specify" / "hooks" / "audit.log"
    logger = AuditLogger(audit_log_path)

    # Add sample entries
    logger.log_execution(
        {
            "timestamp": "2025-12-02T10:00:00.000Z",
            "event_id": "evt_001",
            "event_type": "spec.created",
            "hook_name": "test-hook",
            "success": True,
            "exit_code": 0,
            "duration_ms": 123,
        }
    )
    logger.log_execution(
        {
            "timestamp": "2025-12-02T11:00:00.000Z",
            "event_id": "evt_002",
            "event_type": "implement.completed",
            "hook_name": "quality-gate",
            "success": False,
            "exit_code": 1,
            "duration_ms": 456,
            "error": "Tests failed",
        }
    )

    return audit_log_path


# --- Test: hooks emit ---


def test_emit_basic(temp_workspace, sample_hooks_config):
    """Test basic event emission."""
    result = runner.invoke(
        hooks_app,
        [
            "emit",
            "spec.created",
            "--spec-id",
            "test-feature",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0
    assert "Emitting event: spec.created" in result.stdout
    assert "test-hook" in result.stdout


def test_emit_dry_run(temp_workspace, sample_hooks_config):
    """Test emit with dry-run mode."""
    result = runner.invoke(
        hooks_app,
        [
            "emit",
            "spec.created",
            "--spec-id",
            "test",
            "--dry-run",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0
    assert "DRY RUN MODE" in result.stdout
    # Dry run doesn't show hook names in output, just whether hooks matched
    # The actual hook name logging is at DEBUG level


def test_emit_json_output(temp_workspace, sample_hooks_config):
    """Test emit with JSON output."""
    result = runner.invoke(
        hooks_app,
        [
            "emit",
            "spec.created",
            "--spec-id",
            "test",
            "--json",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0

    # Parse JSON output
    output = json.loads(result.stdout)
    assert "event" in output
    assert "hooks_executed" in output
    assert "results" in output
    assert output["event"]["event_type"] == "spec.created"


def test_emit_with_files(temp_workspace, sample_hooks_config):
    """Test emit with multiple files."""
    result = runner.invoke(
        hooks_app,
        [
            "emit",
            "implement.completed",
            "--spec-id",
            "auth",
            "-f",
            "src/auth/login.py",
            "-f",
            "src/auth/signup.py",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0
    assert "Emitting event: implement.completed" in result.stdout


def test_emit_no_matching_hooks(temp_workspace, sample_hooks_config):
    """Test emit when no hooks match the event."""
    result = runner.invoke(
        hooks_app,
        [
            "emit",
            "unknown.event",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0
    assert "No hooks matched this event" in result.stdout


def test_emit_invalid_event_type(temp_workspace):
    """Test emit with invalid event type still works (no strict validation)."""
    # Event emission should not validate event type - that's up to hooks config
    result = runner.invoke(
        hooks_app,
        [
            "emit",
            "invalid.event",
            "--project-root",
            str(temp_workspace),
        ],
    )

    # Should succeed even with no hooks matched
    assert result.exit_code == 0


# --- Test: hooks validate ---


def test_validate_valid_config(temp_workspace, sample_hooks_config):
    """Test validation of valid config."""
    result = runner.invoke(
        hooks_app,
        [
            "validate",
            "--file",
            str(sample_hooks_config),
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0
    assert "Validation passed" in result.stdout


def test_validate_default_config(temp_workspace, sample_hooks_config):
    """Test validation without explicit --file (uses default)."""
    result = runner.invoke(
        hooks_app,
        [
            "validate",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0
    assert "Validation passed" in result.stdout


def test_validate_missing_config(temp_workspace):
    """Test validation when config doesn't exist."""
    result = runner.invoke(
        hooks_app,
        [
            "validate",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 1
    assert "not found" in result.stdout


def test_validate_invalid_config(temp_workspace):
    """Test validation with invalid YAML."""
    hooks_dir = temp_workspace / ".specify" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    config_file = hooks_dir / "hooks.yaml"

    # Invalid YAML
    config_file.write_text("invalid: yaml: syntax: error:")

    result = runner.invoke(
        hooks_app,
        [
            "validate",
            "--file",
            str(config_file),
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 1


def test_validate_missing_script(temp_workspace):
    """Test validation when script file doesn't exist."""
    hooks_dir = temp_workspace / ".specify" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    config_file = hooks_dir / "hooks.yaml"

    config_content = """
version: "1.0"
hooks:
  - name: missing-script
    events:
      - type: spec.created
    script: nonexistent.sh
"""
    config_file.write_text(config_content)

    result = runner.invoke(
        hooks_app,
        [
            "validate",
            "--file",
            str(config_file),
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 1
    assert "not found" in result.stdout.lower()


# --- Test: hooks list ---


def test_list_hooks(temp_workspace, sample_hooks_config):
    """Test listing hooks."""
    result = runner.invoke(
        hooks_app,
        [
            "list",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0
    assert "test-hook" in result.stdout
    assert "quality-gate" in result.stdout
    assert "spec.created" in result.stdout
    # "implement.completed" may be truncated in table output
    assert "implement.comp" in result.stdout


def test_list_no_hooks(temp_workspace):
    """Test listing when no hooks configured."""
    hooks_dir = temp_workspace / ".specify" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    config_file = hooks_dir / "hooks.yaml"

    config_content = """
version: "1.0"
hooks: []
"""
    config_file.write_text(config_content)

    result = runner.invoke(
        hooks_app,
        [
            "list",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0
    assert "No hooks configured" in result.stdout


def test_list_no_config(temp_workspace):
    """Test listing when no hooks.yaml exists."""
    result = runner.invoke(
        hooks_app,
        [
            "list",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0
    # Empty config returns "No hooks configured" instead of "No hooks configuration found"
    # because load_hooks_config returns empty config when file not found
    assert "No hooks" in result.stdout


# --- Test: hooks audit ---


def test_audit_basic(temp_workspace, sample_audit_log):
    """Test viewing audit log."""
    result = runner.invoke(
        hooks_app,
        [
            "audit",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0
    assert "test-hook" in result.stdout
    assert "quality-gate" in result.stdout
    assert "spec.created" in result.stdout
    # "implement.completed" may be truncated in table output
    assert "implement.comp" in result.stdout


def test_audit_tail(temp_workspace, sample_audit_log):
    """Test audit with custom tail count."""
    result = runner.invoke(
        hooks_app,
        [
            "audit",
            "--tail",
            "1",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0
    # Should only show most recent entry
    assert "quality-gate" in result.stdout


def test_audit_json_output(temp_workspace, sample_audit_log):
    """Test audit with JSON output."""
    result = runner.invoke(
        hooks_app,
        [
            "audit",
            "--json",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0

    # Parse JSON output
    output = json.loads(result.stdout)
    assert "entries" in output
    assert "count" in output
    assert output["count"] == 2


def test_audit_no_log(temp_workspace):
    """Test audit when no log file exists."""
    result = runner.invoke(
        hooks_app,
        [
            "audit",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0
    assert "No audit log found" in result.stdout


def test_audit_empty_log(temp_workspace):
    """Test audit with empty log file."""
    audit_log_path = temp_workspace / ".specify" / "hooks" / "audit.log"
    audit_log_path.parent.mkdir(parents=True, exist_ok=True)
    audit_log_path.touch()

    result = runner.invoke(
        hooks_app,
        [
            "audit",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0
    assert "empty" in result.stdout.lower()


# --- Test: hooks test ---


def test_test_hook_success(temp_workspace, sample_hooks_config):
    """Test testing a hook that succeeds."""
    result = runner.invoke(
        hooks_app,
        [
            "test",
            "test-hook",
            "spec.created",
            "--spec-id",
            "test-feature",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0
    assert "Testing hook: test-hook" in result.stdout
    assert "succeeded" in result.stdout.lower()


def test_test_hook_failure(temp_workspace):
    """Test testing a hook that fails."""
    hooks_dir = temp_workspace / ".specify" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)

    # Create failing hook
    config_file = hooks_dir / "hooks.yaml"
    config_content = """
version: "1.0"
hooks:
  - name: failing-hook
    events:
      - type: spec.created
    script: fail.sh
"""
    config_file.write_text(config_content)

    # Create failing script
    fail_script = hooks_dir / "fail.sh"
    fail_script.write_text("#!/bin/bash\necho 'Hook failed'\nexit 1\n")
    fail_script.chmod(0o755)

    result = runner.invoke(
        hooks_app,
        [
            "test",
            "failing-hook",
            "spec.created",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 1
    assert "failed" in result.stdout.lower()


def test_test_hook_not_found(temp_workspace, sample_hooks_config):
    """Test testing a hook that doesn't exist."""
    result = runner.invoke(
        hooks_app,
        [
            "test",
            "nonexistent-hook",
            "spec.created",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 1
    assert "Hook not found" in result.stdout


def test_test_hook_with_output(temp_workspace):
    """Test hook that produces stdout/stderr."""
    hooks_dir = temp_workspace / ".specify" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)

    # Create hook with output
    config_file = hooks_dir / "hooks.yaml"
    config_content = """
version: "1.0"
hooks:
  - name: output-hook
    events:
      - type: spec.created
    script: output.sh
"""
    config_file.write_text(config_content)

    # Create script with stdout/stderr
    script = hooks_dir / "output.sh"
    script.write_text(
        "#!/bin/bash\necho 'This is stdout'\necho 'This is stderr' >&2\nexit 0\n"
    )
    script.chmod(0o755)

    result = runner.invoke(
        hooks_app,
        [
            "test",
            "output-hook",
            "spec.created",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0
    assert "This is stdout" in result.stdout
    assert "This is stderr" in result.stdout


# --- Integration Tests ---


def test_full_workflow(temp_workspace, sample_hooks_config):
    """Test full workflow: validate -> list -> emit -> audit."""
    # 1. Validate
    result = runner.invoke(
        hooks_app,
        [
            "validate",
            "--project-root",
            str(temp_workspace),
        ],
    )
    assert result.exit_code == 0

    # 2. List
    result = runner.invoke(
        hooks_app,
        [
            "list",
            "--project-root",
            str(temp_workspace),
        ],
    )
    assert result.exit_code == 0

    # 3. Emit
    result = runner.invoke(
        hooks_app,
        [
            "emit",
            "spec.created",
            "--spec-id",
            "test",
            "--project-root",
            str(temp_workspace),
        ],
    )
    assert result.exit_code == 0

    # 4. Audit
    result = runner.invoke(
        hooks_app,
        [
            "audit",
            "--project-root",
            str(temp_workspace),
        ],
    )
    assert result.exit_code == 0
    assert "test-hook" in result.stdout


def test_emit_creates_audit_entry(temp_workspace, sample_hooks_config):
    """Test that emit creates audit log entries."""
    # Emit event
    result = runner.invoke(
        hooks_app,
        [
            "emit",
            "spec.created",
            "--spec-id",
            "test",
            "--project-root",
            str(temp_workspace),
        ],
    )
    assert result.exit_code == 0

    # Check audit log was created
    audit_log_path = temp_workspace / ".specify" / "hooks" / "audit.log"
    assert audit_log_path.exists()

    # Verify audit entry
    result = runner.invoke(
        hooks_app,
        [
            "audit",
            "--json",
            "--project-root",
            str(temp_workspace),
        ],
    )
    assert result.exit_code == 0

    output = json.loads(result.stdout)
    assert output["count"] >= 1
    assert any(e["hook_name"] == "test-hook" for e in output["entries"])


# --- Agent Progress Events Tests ---


def test_emit_agent_progress_event(temp_workspace, sample_hooks_config):
    """Test emitting agent.progress event with progress and message flags."""
    result = runner.invoke(
        hooks_app,
        [
            "emit",
            "agent.progress",
            "--task-id",
            "task-229",
            "--spec-id",
            "agent-hooks",
            "--progress",
            "60",
            "--message",
            "Implementing hooks",
            "--json",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0
    output = json.loads(result.stdout)

    # Verify event structure
    event = output["event"]
    assert event["event_type"] == "agent.progress"
    assert event["feature"] == "agent-hooks"
    assert event["context"]["task_id"] == "task-229"
    assert event["context"]["progress_percent"] == 60
    assert event["context"]["status_message"] == "Implementing hooks"
    assert "agent_id" in event["context"]
    assert "machine" in event["context"]


def test_emit_agent_started_event(temp_workspace, sample_hooks_config):
    """Test emitting agent.started event."""
    result = runner.invoke(
        hooks_app,
        [
            "emit",
            "agent.started",
            "--task-id",
            "task-229",
            "--spec-id",
            "agent-hooks",
            "--json",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0
    output = json.loads(result.stdout)

    event = output["event"]
    assert event["event_type"] == "agent.started"
    assert "agent_id" in event["context"]
    assert "machine" in event["context"]


def test_emit_agent_event_with_custom_agent_id(temp_workspace, sample_hooks_config):
    """Test emitting agent event with custom agent_id."""
    result = runner.invoke(
        hooks_app,
        [
            "emit",
            "agent.progress",
            "--agent-id",
            "claude-code@kinsale",
            "--progress",
            "50",
            "--json",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0
    output = json.loads(result.stdout)

    event = output["event"]
    assert event["context"]["agent_id"] == "claude-code@kinsale"


def test_multi_machine_agent_simulation(temp_workspace, sample_hooks_config):
    """Test simulating multi-machine agent events with different machines."""
    # Emit from "muckross"
    result1 = runner.invoke(
        hooks_app,
        [
            "emit",
            "agent.started",
            "--agent-id",
            "claude-code@muckross",
            "--task-id",
            "task-198",
            "--json",
            "--project-root",
            str(temp_workspace),
        ],
    )
    assert result1.exit_code == 0
    event1 = json.loads(result1.stdout)["event"]
    assert event1["context"]["agent_id"] == "claude-code@muckross"

    # Emit from "galway"
    result2 = runner.invoke(
        hooks_app,
        [
            "emit",
            "agent.progress",
            "--agent-id",
            "claude-code@galway",
            "--task-id",
            "task-198",
            "--progress",
            "30",
            "--message",
            "Security scanning in progress",
            "--json",
            "--project-root",
            str(temp_workspace),
        ],
    )
    assert result2.exit_code == 0
    event2 = json.loads(result2.stdout)["event"]
    assert event2["context"]["agent_id"] == "claude-code@galway"
    assert event2["context"]["progress_percent"] == 30

    # Emit from "kinsale"
    result3 = runner.invoke(
        hooks_app,
        [
            "emit",
            "agent.completed",
            "--agent-id",
            "claude-code@kinsale",
            "--task-id",
            "task-229",
            "--message",
            "Implementation complete",
            "--json",
            "--project-root",
            str(temp_workspace),
        ],
    )
    assert result3.exit_code == 0
    event3 = json.loads(result3.stdout)["event"]
    assert event3["context"]["agent_id"] == "claude-code@kinsale"
    assert event3["context"]["status_message"] == "Implementation complete"
