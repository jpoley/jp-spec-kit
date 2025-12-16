# Hook Testing Strategy

## Overview

This document defines the comprehensive testing strategy for the Flowspec hook system, covering unit tests, integration tests, end-to-end tests, and security tests. The strategy ensures reliability, security, and maintainability of the hook infrastructure.

## Testing Philosophy

1. **Test the Contract, Not the Implementation**: Focus on behavior and interfaces, not internal details
2. **Fail Fast**: Tests should fail immediately when problems are detected
3. **Isolation**: Each test should be independent and not rely on external state
4. **Realistic Scenarios**: Integration and E2E tests should mirror real-world usage
5. **Security-First**: Security tests are mandatory, not optional

## Test Pyramid

```
        /\
       /  \        E2E Tests (10%)
      /    \       - Full workflow scenarios
     /------\      - Real hooks.yaml configs
    /        \     - Actual script execution
   /          \
  /------------\   Integration Tests (30%)
 /              \  - Component interaction
/                \ - Event → hook dispatch
\----------------/ - Security boundaries
 \              /
  \            /  Unit Tests (60%)
   \          /   - Individual functions
    \        /    - Edge cases
     \------/     - Error handling
      \    /
       \  /
        \/
```

## Unit Tests

### Scope

Unit tests validate individual functions and classes in isolation using mocks and stubs.

### Test Organization

```
tests/
├── unit/
│   ├── test_event_model.py        # Event creation, validation, serialization
│   ├── test_hook_parser.py         # YAML parsing, schema validation
│   ├── test_event_matcher.py       # Event matching logic
│   ├── test_hook_runner.py         # Hook execution (mocked subprocess)
│   ├── test_security.py            # Security controls (path validation, etc.)
│   ├── test_audit_logger.py        # Audit logging (mocked I/O)
│   └── test_metrics.py             # Metrics aggregation
```

### Key Test Modules

#### 1. Event Model Tests (`test_event_model.py`)

```python
import pytest
from specify_cli.hooks.event_model import Event, EventType

class TestEventModel:
    """Unit tests for Event model"""

    def test_event_creation(self):
        """Verify event is created with required fields"""
        event = Event(
            event_type=EventType.IMPLEMENT_COMPLETED,
            feature="auth",
            context={"task_id": "task-189"}
        )

        assert event.event_type == EventType.IMPLEMENT_COMPLETED
        assert event.feature == "auth"
        assert event.context["task_id"] == "task-189"
        assert event.event_id.startswith("evt_")
        assert event.timestamp is not None

    def test_event_serialization(self):
        """Verify event serializes to JSON correctly"""
        event = Event(
            event_type=EventType.SPEC_CREATED,
            feature="user-profile"
        )

        payload = event.to_json()

        assert payload["event_type"] == "spec.created"
        assert payload["feature"] == "user-profile"
        assert "event_id" in payload
        assert "timestamp" in payload

    def test_event_deserialization(self):
        """Verify event can be reconstructed from JSON"""
        payload = {
            "event_id": "evt_test123",
            "event_type": "task.completed",
            "timestamp": "2025-12-02T15:30:45.123Z",
            "feature": "auth",
            "context": {"task_id": "task-189"}
        }

        event = Event.from_json(payload)

        assert event.event_id == "evt_test123"
        assert event.event_type == EventType.TASK_COMPLETED
        assert event.feature == "auth"

    @pytest.mark.parametrize("invalid_type", [
        "",
        "invalid.type",
        "task_completed",  # underscore instead of dot
        123,  # non-string
    ])
    def test_invalid_event_type(self, invalid_type):
        """Verify invalid event types are rejected"""
        with pytest.raises(ValueError, match="Invalid event type"):
            Event(event_type=invalid_type, feature="test")
```

#### 2. Hook Parser Tests (`test_hook_parser.py`)

```python
import pytest
from specify_cli.hooks.parser import HookParser, HookConfig
from pathlib import Path

class TestHookParser:
    """Unit tests for YAML hook parser"""

    def test_parse_valid_config(self, tmp_path):
        """Verify valid hooks.yaml is parsed correctly"""
        config_path = tmp_path / "hooks.yaml"
        config_path.write_text("""
version: "1.0"
hooks:
  - name: "test-hook"
    events:
      - type: "implement.completed"
    script: ".flowspec/hooks/test.sh"
    timeout: 60
""")

        parser = HookParser()
        config = parser.parse(config_path)

        assert config.version == "1.0"
        assert len(config.hooks) == 1
        assert config.hooks[0].name == "test-hook"
        assert config.hooks[0].timeout == 60

    def test_parse_missing_required_field(self, tmp_path):
        """Verify parser rejects config missing required fields"""
        config_path = tmp_path / "hooks.yaml"
        config_path.write_text("""
version: "1.0"
hooks:
  - name: "invalid-hook"
    # Missing 'events' field
    script: ".flowspec/hooks/test.sh"
""")

        parser = HookParser()
        with pytest.raises(ValueError, match="Missing required field: events"):
            parser.parse(config_path)

    def test_parse_invalid_hook_name(self, tmp_path):
        """Verify parser rejects invalid hook names"""
        config_path = tmp_path / "hooks.yaml"
        config_path.write_text("""
version: "1.0"
hooks:
  - name: "Invalid Name With Spaces"  # Invalid
    events:
      - type: "task.completed"
    script: ".flowspec/hooks/test.sh"
""")

        parser = HookParser()
        with pytest.raises(ValueError, match="Invalid hook name"):
            parser.parse(config_path)

    def test_parse_duplicate_hook_names(self, tmp_path):
        """Verify parser rejects duplicate hook names"""
        config_path = tmp_path / "hooks.yaml"
        config_path.write_text("""
version: "1.0"
hooks:
  - name: "duplicate"
    events:
      - type: "task.completed"
    script: ".flowspec/hooks/test1.sh"
  - name: "duplicate"
    events:
      - type: "spec.created"
    script: ".flowspec/hooks/test2.sh"
""")

        parser = HookParser()
        with pytest.raises(ValueError, match="Duplicate hook name"):
            parser.parse(config_path)
```

#### 3. Security Tests (`test_security.py`)

```python
import pytest
from pathlib import Path
from specify_cli.hooks.security import (
    validate_script_path,
    sanitize_environment,
    scan_for_dangerous_commands,
)

class TestSecurity:
    """Unit tests for security controls"""

    def test_path_traversal_rejected(self, tmp_path):
        """Verify path traversal attempts are blocked"""
        hooks_dir = tmp_path / ".specify" / "hooks"
        hooks_dir.mkdir(parents=True)

        with pytest.raises(ValueError, match="outside allowed directory"):
            validate_script_path("../../etc/passwd", hooks_dir)

    def test_absolute_path_rejected(self, tmp_path):
        """Verify absolute paths are blocked"""
        hooks_dir = tmp_path / ".specify" / "hooks"

        with pytest.raises(ValueError, match="forbidden components"):
            validate_script_path("/bin/rm", hooks_dir)

    def test_valid_relative_path_allowed(self, tmp_path):
        """Verify valid relative paths are allowed"""
        hooks_dir = tmp_path / ".specify" / "hooks"
        hooks_dir.mkdir(parents=True)

        script = hooks_dir / "test.sh"
        script.write_text("#!/bin/bash\necho test")
        script.chmod(0o755)

        result = validate_script_path(".flowspec/hooks/test.sh", hooks_dir)
        assert result == script.resolve()

    def test_environment_sanitization_blocks_dangerous_vars(self):
        """Verify dangerous environment variables are blocked"""
        with pytest.raises(ValueError, match="is blocked"):
            sanitize_environment({"LD_PRELOAD": "/tmp/evil.so"})

    def test_environment_sanitization_allows_safe_vars(self):
        """Verify safe environment variables are allowed"""
        env = sanitize_environment({
            "FEATURE_NAME": "auth",
            "TIMEOUT": "30",
        })

        assert env["FEATURE_NAME"] == "auth"
        assert env["TIMEOUT"] == "30"

    def test_dangerous_command_detection(self, tmp_path):
        """Verify dangerous commands are flagged"""
        script = tmp_path / "malicious.sh"
        script.write_text("""
#!/bin/bash
rm -rf /
dd if=/dev/zero of=/dev/sda
""")

        findings = scan_for_dangerous_commands(script)
        assert len(findings) >= 2
        assert any("Recursive deletion" in desc for _, desc in findings)
        assert any("block device" in desc for _, desc in findings)
```

### Coverage Requirements

- **Minimum Coverage**: 85% for all hook-related code
- **Critical Paths**: 100% for security functions
- **Edge Cases**: Explicit tests for error conditions, boundary values

## Integration Tests

### Scope

Integration tests validate component interactions without full system deployment.

### Test Organization

```
tests/
├── integration/
│   ├── test_event_dispatch.py      # Event → hook matching → dispatch
│   ├── test_hook_execution.py      # Hook runner → subprocess → audit log
│   ├── test_security_boundaries.py # Security controls in realistic scenarios
│   ├── test_backlog_integration.py # Backlog CLI → event emission
│   └── test_workflow_integration.py # /flowspec commands → event emission
```

### Key Test Modules

#### 1. Event Dispatch Tests (`test_event_dispatch.py`)

```python
import pytest
from specify_cli.hooks.dispatcher import HookDispatcher
from specify_cli.hooks.event_model import Event, EventType

class TestEventDispatch:
    """Integration tests for event → hook dispatch"""

    def test_simple_event_match(self, tmp_path):
        """Verify simple event type match triggers hook"""
        # Setup hooks.yaml
        hooks_config = tmp_path / ".specify" / "hooks" / "hooks.yaml"
        hooks_config.parent.mkdir(parents=True)
        hooks_config.write_text("""
version: "1.0"
hooks:
  - name: "test-hook"
    events:
      - type: "implement.completed"
    command: "echo 'hook triggered'"
""")

        # Create dispatcher
        dispatcher = HookDispatcher(config_path=hooks_config)

        # Emit event
        event = Event(
            event_type=EventType.IMPLEMENT_COMPLETED,
            feature="auth"
        )

        # Get matching hooks
        matches = dispatcher.find_matching_hooks(event)

        assert len(matches) == 1
        assert matches[0].name == "test-hook"

    def test_filtered_event_match(self, tmp_path):
        """Verify filtered event matches only when filter conditions met"""
        hooks_config = tmp_path / ".specify" / "hooks" / "hooks.yaml"
        hooks_config.parent.mkdir(parents=True)
        hooks_config.write_text("""
version: "1.0"
hooks:
  - name: "high-priority-only"
    events:
      - type: "task.completed"
        filter:
          priority: ["high", "critical"]
    command: "echo 'high priority task'"
""")

        dispatcher = HookDispatcher(config_path=hooks_config)

        # Event with high priority - should match
        event_high = Event(
            event_type=EventType.TASK_COMPLETED,
            context={"priority": "high"}
        )
        matches = dispatcher.find_matching_hooks(event_high)
        assert len(matches) == 1

        # Event with low priority - should NOT match
        event_low = Event(
            event_type=EventType.TASK_COMPLETED,
            context={"priority": "low"}
        )
        matches = dispatcher.find_matching_hooks(event_low)
        assert len(matches) == 0
```

#### 2. Hook Execution Tests (`test_hook_execution.py`)

```python
import pytest
from specify_cli.hooks.runner import HookRunner
from pathlib import Path

class TestHookExecution:
    """Integration tests for hook execution"""

    def test_script_execution_success(self, tmp_path):
        """Verify successful script execution"""
        # Create test script
        hooks_dir = tmp_path / ".specify" / "hooks"
        hooks_dir.mkdir(parents=True)

        script = hooks_dir / "success.sh"
        script.write_text("#!/bin/bash\necho 'test output'\nexit 0")
        script.chmod(0o755)

        # Execute hook
        runner = HookRunner(project_root=tmp_path)
        result = runner.execute_hook(
            script_path=script,
            timeout=5,
            environment={},
            working_directory=tmp_path
        )

        assert result.exit_code == 0
        assert result.status == "success"
        assert "test output" in result.stdout

    def test_script_execution_failure(self, tmp_path):
        """Verify failed script execution is handled correctly"""
        hooks_dir = tmp_path / ".specify" / "hooks"
        hooks_dir.mkdir(parents=True)

        script = hooks_dir / "failure.sh"
        script.write_text("#!/bin/bash\necho 'error' >&2\nexit 1")
        script.chmod(0o755)

        runner = HookRunner(project_root=tmp_path)
        result = runner.execute_hook(
            script_path=script,
            timeout=5,
            environment={},
            working_directory=tmp_path
        )

        assert result.exit_code == 1
        assert result.status == "failed"
        assert "error" in result.stderr

    def test_timeout_enforcement(self, tmp_path):
        """Verify timeout kills long-running scripts"""
        hooks_dir = tmp_path / ".specify" / "hooks"
        hooks_dir.mkdir(parents=True)

        script = hooks_dir / "infinite.sh"
        script.write_text("#!/bin/bash\nwhile true; do sleep 1; done")
        script.chmod(0o755)

        runner = HookRunner(project_root=tmp_path)
        result = runner.execute_hook(
            script_path=script,
            timeout=2,
            environment={},
            working_directory=tmp_path
        )

        assert result.status == "timeout"
        assert result.duration_ms < 3000  # Should be killed within ~2s
```

### Fixture Management

```python
# tests/conftest.py

import pytest
from pathlib import Path

@pytest.fixture
def project_root(tmp_path):
    """Create temporary project root with .flowspec/hooks/ structure"""
    hooks_dir = tmp_path / ".specify" / "hooks"
    hooks_dir.mkdir(parents=True)
    return tmp_path

@pytest.fixture
def hooks_config(project_root):
    """Create default hooks.yaml configuration"""
    config_path = project_root / ".specify" / "hooks" / "hooks.yaml"
    config_path.write_text("""
version: "1.0"
defaults:
  timeout: 30
hooks: []
""")
    return config_path

@pytest.fixture
def sample_event():
    """Create sample event for testing"""
    return Event(
        event_type=EventType.IMPLEMENT_COMPLETED,
        feature="test-feature",
        context={"task_id": "task-123"}
    )
```

## End-to-End Tests

### Scope

E2E tests validate full workflow scenarios with real hooks, scripts, and CLI commands.

### Test Organization

```
tests/
├── e2e/
│   ├── test_implement_workflow.py   # /flow:implement → run tests
│   ├── test_spec_workflow.py        # /flow:specify → update docs
│   ├── test_task_workflow.py        # backlog task → notifications
│   ├── test_security_enforcement.py # Security controls in real scenarios
│   └── fixtures/
│       ├── hooks/
│       │   ├── run-tests.sh
│       │   ├── update-docs.py
│       │   └── notify-slack.sh
│       └── configs/
│           ├── basic-hooks.yaml
│           ├── complex-hooks.yaml
│           └── security-test-hooks.yaml
```

### Key Test Scenarios

#### Scenario 1: Implement → Test Suite Execution

```python
import pytest
from specify_cli.cli import main
from pathlib import Path

class TestImplementWorkflow:
    """E2E test for implement.completed → run tests"""

    def test_implement_triggers_test_hook(self, project_root, monkeypatch):
        """
        GIVEN: hooks.yaml configured to run tests on implement.completed
        WHEN: /flow:implement is executed
        THEN: Test suite runs and results are logged
        """
        # Setup hooks.yaml
        hooks_config = project_root / ".specify" / "hooks" / "hooks.yaml"
        hooks_config.write_text("""
version: "1.0"
hooks:
  - name: "run-tests"
    events:
      - type: "implement.completed"
    script: ".flowspec/hooks/run-tests.sh"
    timeout: 300
    fail_mode: "stop"
""")

        # Create test script
        test_script = project_root / ".specify" / "hooks" / "run-tests.sh"
        test_script.write_text("""
#!/bin/bash
echo "Running tests..."
pytest tests/ -v
exit $?
""")
        test_script.chmod(0o755)

        # Create dummy test file
        tests_dir = project_root / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_example.py").write_text("""
def test_example():
    assert 1 + 1 == 2
""")

        # Change to project root
        monkeypatch.chdir(project_root)

        # Run /flow:implement
        result = main(["flow:implement", "test-feature"])

        # Verify hook was triggered
        audit_log = project_root / ".specify" / "hooks" / "audit.log"
        assert audit_log.exists()

        # Parse audit log
        import json
        with open(audit_log) as f:
            entries = [json.loads(line) for line in f]

        # Find hook execution entry
        hook_entries = [e for e in entries if e.get("hook_name") == "run-tests"]
        assert len(hook_entries) == 1

        # Verify success
        assert hook_entries[0]["status"] == "success"
        assert hook_entries[0]["exit_code"] == 0
```

#### Scenario 2: Security - Path Traversal Prevention

```python
class TestSecurityEnforcement:
    """E2E tests for security controls"""

    def test_path_traversal_blocked_at_runtime(self, project_root, monkeypatch):
        """
        GIVEN: hooks.yaml with path traversal attempt
        WHEN: Hook validation is run
        THEN: Validation fails and hook is not executed
        """
        hooks_config = project_root / ".specify" / "hooks" / "hooks.yaml"
        hooks_config.write_text("""
version: "1.0"
hooks:
  - name: "malicious"
    events:
      - type: "task.completed"
    script: "../../etc/passwd"  # Path traversal attempt
""")

        monkeypatch.chdir(project_root)

        # Run validation
        result = main(["hooks", "validate"])

        # Should fail validation
        assert result.exit_code != 0
        assert "outside allowed directory" in result.stderr

        # Verify audit log records security event
        audit_log = project_root / ".specify" / "hooks" / "audit.log"
        with open(audit_log) as f:
            entries = [json.loads(line) for line in f]

        security_events = [e for e in entries if e.get("type") == "security_event"]
        assert len(security_events) > 0
        assert "path_traversal" in security_events[0]["event_type"]
```

### Test Data Management

**Example Hook Scripts** (stored in `tests/e2e/fixtures/hooks/`):

```bash
# run-tests.sh
#!/bin/bash
set -e
echo "Running test suite..."
pytest tests/ -v --cov=src
echo "Tests completed successfully"

# update-docs.py
#!/usr/bin/env python3
import sys
import json

# Read event payload from stdin
event = json.loads(sys.stdin.read())

feature = event.get("feature", "unknown")
print(f"Updating documentation for {feature}...")

# Append to CHANGELOG.md
with open("CHANGELOG.md", "a") as f:
    f.write(f"\n- Added {feature} feature\n")

print("Documentation updated")

# notify-slack.sh
#!/bin/bash
# Simulate Slack notification (no actual network call in tests)
echo "Would send Slack notification: Task completed"
```

## Test Fixtures and Mocking

### Mocking Strategy

1. **External Systems**: Mock network calls (webhooks, APIs)
2. **File I/O**: Use `tmp_path` fixture for real files, mock for errors
3. **Subprocess**: Real execution in integration/E2E, mocked in unit tests
4. **Time**: Mock for consistent test behavior

### Example Mocks

```python
# Mock subprocess for unit tests
from unittest.mock import Mock, patch

@patch('subprocess.run')
def test_hook_runner_with_mock(mock_run):
    """Unit test with mocked subprocess"""
    mock_run.return_value = Mock(
        returncode=0,
        stdout="test output",
        stderr=""
    )

    runner = HookRunner()
    result = runner.execute_hook(script_path=Path("test.sh"), timeout=30)

    assert result.exit_code == 0
    mock_run.assert_called_once()
```

## CI/CD Integration

### Test Execution in CI

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Run unit tests
        run: pytest tests/unit/ -v --cov=src/specify_cli/hooks

      - name: Run integration tests
        run: pytest tests/integration/ -v

      - name: Run E2E tests
        run: pytest tests/e2e/ -v

      - name: Check coverage
        run: |
          coverage report --fail-under=85
          coverage html

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Test Matrix

| Python Version | OS | Test Suite |
|----------------|----|-----------|
| 3.11 | Ubuntu 22.04 | Full (unit + integration + E2E) |
| 3.12 | Ubuntu 22.04 | Full |
| 3.11 | macOS 14 | Full |
| 3.11 | Windows (best-effort) | Unit + Integration only |

## Performance Testing

### Load Tests

```python
import pytest
import time
from specify_cli.hooks.dispatcher import HookDispatcher

def test_event_dispatch_performance():
    """Verify event dispatch completes within performance budget"""
    dispatcher = HookDispatcher()

    # Create event
    event = Event(event_type=EventType.IMPLEMENT_COMPLETED, feature="test")

    # Measure dispatch time
    start = time.perf_counter()
    matches = dispatcher.find_matching_hooks(event)
    duration_ms = (time.perf_counter() - start) * 1000

    # Verify performance budget
    assert duration_ms < 50, f"Event dispatch took {duration_ms}ms (target: <50ms)"

def test_audit_logging_performance(tmp_path):
    """Verify audit logging doesn't block execution"""
    audit_log = tmp_path / "audit.log"
    logger = AuditLogger(audit_log)

    # Log 100 entries
    start = time.perf_counter()
    for i in range(100):
        logger.log_execution(
            event_id=f"evt_{i}",
            hook_name="test",
            status="success",
            exit_code=0,
            duration_ms=100
        )
    duration_ms = (time.perf_counter() - start) * 1000

    # Should complete in <1 second for 100 entries
    assert duration_ms < 1000, f"100 log writes took {duration_ms}ms"
```

## Test Documentation

### Test Plan Document

Each test should include:
- **Purpose**: What behavior is being validated
- **Given**: Initial state/preconditions
- **When**: Action being tested
- **Then**: Expected outcome
- **Edge Cases**: Boundary conditions tested

### Example Test Plan

```python
def test_hook_timeout_enforcement(self, tmp_path):
    """
    Purpose: Verify hooks are killed after configured timeout

    Given: Hook configured with 2 second timeout
           Script that runs infinite loop

    When: Hook is dispatched

    Then: Script is terminated after ~2 seconds
          Status is "timeout"
          Exit code is 124
          Audit log records timeout event

    Edge Cases:
    - Timeout = 1s (minimum)
    - Timeout = 600s (maximum)
    - Timeout = 0 (invalid, should use default)
    """
    # Test implementation...
```

## Implementation Checklist (task-209)

E2E testing implementation steps:

### Phase 1: Test Infrastructure (Week 1)
- [ ] Create `tests/e2e/` directory structure
- [ ] Create example hook scripts in `fixtures/hooks/`
- [ ] Create example configs in `fixtures/configs/`
- [ ] Set up pytest fixtures for E2E tests
- [ ] Configure CI to run E2E tests

### Phase 2: Workflow Tests (Week 2)
- [ ] Write E2E test: implement.completed → run tests
- [ ] Write E2E test: spec.created → update docs
- [ ] Write E2E test: task.completed → notifications
- [ ] Write E2E test: plan.created → generate artifacts
- [ ] Verify all workflows in CI

### Phase 3: Security Tests (Week 3)
- [ ] Write E2E test: path traversal prevention
- [ ] Write E2E test: timeout enforcement
- [ ] Write E2E test: environment sanitization
- [ ] Write E2E test: dangerous command detection
- [ ] Write E2E test: audit logging verification

### Phase 4: Documentation & Cleanup (Week 4)
- [ ] Document all E2E test scenarios
- [ ] Create test plan document
- [ ] Add test execution guide to docs
- [ ] Verify coverage meets 85% threshold
- [ ] Run full test suite on clean install

## References

- [Pytest Documentation](https://docs.pytest.org/)
- [Test Pyramid (Martin Fowler)](https://martinfowler.com/articles/practical-test-pyramid.html)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)
