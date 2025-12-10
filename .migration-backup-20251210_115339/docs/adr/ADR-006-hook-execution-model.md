# ADR-006: Hook Execution Model

**Status**: Proposed
**Date**: 2025-12-02
**Author**: @software-architect
**Context**: Agent Hooks Feature (task-202, task-205, task-210)

---

## Context

The event model (ADR-005) defines WHAT events occur in the workflow. This ADR defines HOW hooks execute in response to those events.

**Key Requirements**:
1. **Security**: Hooks execute arbitrary scripts/commands - requires sandboxing
2. **Reliability**: Hook failures must not break workflows (fail-safe)
3. **Performance**: Hook execution latency <100ms from event to script start
4. **Observability**: All executions logged for debugging and compliance

**Security Threat Model**:
- Malicious scripts in repository (code review catches this)
- Command injection via event payloads
- Path traversal to execute arbitrary binaries
- Resource exhaustion (infinite loops, forkbombs)
- Privilege escalation attempts

---

## Decision

Implement a **sequential hook runner** with strict security sandbox and fail-open error handling.

### 1. Execution Flow

```
Event Emitted
    ↓
Hook Matcher (match event type + filters)
    ↓
Hook Dispatcher (for each matching hook)
    ↓
Security Validation (path allowlist, timeout check)
    ↓
Script Execution (subprocess with sandbox)
    ↓
Audit Logging (JSONL to .specify/hooks/audit.log)
    ↓
Error Handling (fail-open or fail-stop based on hook config)
```

**Sequential Execution** (v1):
- Hooks execute one at a time in configuration order
- Next hook waits for previous to complete
- Timeout per hook (default 30s, max 600s)

**Rationale for Sequential**:
- Simpler implementation and debugging
- Predictable ordering for dependent hooks
- Easier resource management
- Parallel execution deferred to v2 when proven necessary

### 2. Security Sandbox

**Path Allowlist** (strictest):
```python
def validate_script_path(script_path: str, project_root: str) -> bool:
    """
    Validate hook script is within allowed directory.

    Raises SecurityError if:
    - Path contains ".." (path traversal)
    - Path is absolute (must be relative to .specify/hooks/)
    - Path resolves outside .specify/hooks/
    """
    allowed_dir = Path(project_root) / ".specify/hooks"
    script_full_path = (allowed_dir / script_path).resolve()

    # Check for path traversal
    if ".." in script_path:
        raise SecurityError("Path traversal detected in hook script")

    # Check script is within allowed directory
    if not script_full_path.is_relative_to(allowed_dir):
        raise SecurityError(f"Hook script must be in .specify/hooks/, got: {script_path}")

    # Check script exists
    if not script_full_path.exists():
        raise SecurityError(f"Hook script not found: {script_path}")

    return True
```

**Timeout Enforcement**:
```python
def execute_with_timeout(script_path: str, timeout: int, event_json: str):
    """
    Execute script with hard timeout.

    - timeout seconds: SIGTERM sent to process
    - timeout + 5 seconds: SIGKILL sent to process
    """
    try:
        result = subprocess.run(
            [script_path],
            input=event_json.encode(),
            capture_output=True,
            timeout=timeout,
            cwd=project_root,
            env=sanitized_env,
        )
        return result
    except subprocess.TimeoutExpired:
        # Process killed after timeout
        logger.error(f"Hook {script_path} timed out after {timeout}s")
        raise HookTimeoutError(f"Hook timed out after {timeout}s")
```

**Environment Sanitization**:
```python
def sanitize_environment(hook_env: Dict[str, str]) -> Dict[str, str]:
    """
    Create clean environment for hook execution.

    - Start with minimal base env (PATH, HOME, USER)
    - Add hook-specific env vars from config
    - Validate no shell metacharacters in values
    """
    base_env = {
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", ""),
        "USER": os.environ.get("USER", ""),
    }

    # Add hook-specific vars
    safe_env = base_env.copy()
    for key, value in hook_env.items():
        # Check for shell injection attempts
        if any(char in value for char in [";", "|", "&", "$", "`"]):
            logger.warning(f"Skipping env var {key} with shell metacharacters")
            continue
        safe_env[key] = value

    return safe_env
```

**Working Directory Constraints**:
```python
def validate_working_directory(working_dir: str, project_root: str) -> Path:
    """
    Validate working directory is within project.

    - Default to project_root if not specified
    - Must be subdirectory of project_root
    - No path traversal allowed
    """
    if not working_dir:
        return Path(project_root)

    wd_path = (Path(project_root) / working_dir).resolve()

    if not wd_path.is_relative_to(project_root):
        raise SecurityError(f"Working directory must be within project: {working_dir}")

    return wd_path
```

### 3. Error Handling Modes

**Fail-Open (Default)**:
```yaml
hooks:
  - name: "update-changelog"
    fail_mode: "continue"  # default
```

- Hook errors logged but don't block workflow
- Exit code logged to audit log
- User sees warning in CLI output
- Workflow continues normally

**Use Cases**: Documentation updates, notifications, non-critical automation

**Fail-Stop (Opt-In)**:
```yaml
hooks:
  - name: "run-tests"
    fail_mode: "stop"
```

- Hook errors block workflow with exit code 1
- Clear error message shown to user
- Workflow terminates immediately
- User must fix hook or disable it to continue

**Use Cases**: Critical quality gates (tests, security scans)

**Error Scenarios**:
```python
class HookError(Exception):
    """Base class for hook execution errors."""

class HookNotFoundError(HookError):
    """Hook script does not exist."""

class HookTimeoutError(HookError):
    """Hook exceeded timeout."""

class HookSecurityError(HookError):
    """Security validation failed."""

class HookExecutionError(HookError):
    """Hook script exited with non-zero code."""
```

**Error Handling Logic**:
```python
def execute_hook(hook: Hook, event: Event) -> HookResult:
    """Execute single hook with error handling."""
    try:
        # Security validation
        validate_script_path(hook.script, project_root)
        working_dir = validate_working_directory(hook.working_directory, project_root)

        # Prepare environment
        env = sanitize_environment(hook.env)
        event_json = json.dumps(event.to_dict())

        # Execute with timeout
        result = subprocess.run(
            [working_dir / hook.script],
            input=event_json.encode(),
            capture_output=True,
            timeout=hook.timeout,
            cwd=working_dir,
            env=env,
        )

        # Check exit code
        if result.returncode != 0:
            raise HookExecutionError(
                f"Hook '{hook.name}' exited with code {result.returncode}\n"
                f"stderr: {result.stderr.decode()}"
            )

        return HookResult(
            hook_name=hook.name,
            status="success",
            exit_code=result.returncode,
            stdout=result.stdout.decode(),
            stderr=result.stderr.decode(),
        )

    except HookTimeoutError as e:
        if hook.fail_mode == "stop":
            raise
        logger.warning(f"Hook {hook.name} timed out: {e}")
        return HookResult(hook_name=hook.name, status="timeout", error=str(e))

    except HookSecurityError as e:
        # Security errors always fail-stop (never continue)
        logger.error(f"Security error in hook {hook.name}: {e}")
        raise

    except HookExecutionError as e:
        if hook.fail_mode == "stop":
            raise
        logger.warning(f"Hook {hook.name} failed: {e}")
        return HookResult(hook_name=hook.name, status="failed", error=str(e))
```

### 4. Event Payload Delivery

**Method**: Standard input (stdin)

**Rationale**:
- Avoids shell injection (no command-line argument parsing)
- Supports large payloads (command-line args have size limits)
- Standard practice (similar to Git hooks)

**Script Interface**:
```bash
#!/bin/bash
# .specify/hooks/run-tests.sh

# Read event from stdin
EVENT=$(cat)

# Parse event JSON
FEATURE=$(echo "$EVENT" | jq -r '.feature')
TASK_ID=$(echo "$EVENT" | jq -r '.context.task_id')

echo "Running tests for feature: $FEATURE (task: $TASK_ID)"

# Run tests
pytest tests/ -v

# Exit with test exit code
exit $?
```

**Python Script Example**:
```python
#!/usr/bin/env python3
# .specify/hooks/update-changelog.py

import sys
import json

# Read event from stdin
event = json.load(sys.stdin)

feature = event["feature"]
timestamp = event["timestamp"]

# Update changelog
with open("CHANGELOG.md", "a") as f:
    f.write(f"\n## {feature} ({timestamp})\n")

print(f"Added {feature} to CHANGELOG.md")
sys.exit(0)
```

### 5. Audit Logging

**Format**: JSON Lines (JSONL)

**Location**: `.specify/hooks/audit.log`

**Log Entries**:
```jsonl
{"timestamp": "2025-12-02T15:30:45.123Z", "event_id": "evt_123", "hook": "run-tests", "status": "started", "pid": 12345}
{"timestamp": "2025-12-02T15:31:15.456Z", "event_id": "evt_123", "hook": "run-tests", "status": "success", "exit_code": 0, "duration_ms": 30333, "stdout_lines": 120}
{"timestamp": "2025-12-02T15:32:00.789Z", "event_id": "evt_124", "hook": "deploy", "status": "failed", "exit_code": 1, "duration_ms": 1234, "error": "Webhook timeout"}
{"timestamp": "2025-12-02T15:33:00.000Z", "event_id": "evt_125", "hook": "missing-hook", "status": "error", "error": "Hook script not found: missing.sh"}
```

**Log Fields**:
- `timestamp`: ISO 8601 UTC
- `event_id`: Correlate with event that triggered hook
- `hook`: Hook name from config
- `status`: started | success | failed | timeout | error
- `exit_code`: Process exit code (if completed)
- `duration_ms`: Execution time in milliseconds
- `pid`: Process ID (for debugging)
- `stdout_lines`: Number of stdout lines (not full content)
- `stderr_lines`: Number of stderr lines (not full content)
- `error`: Error message if hook failed

**Log Rotation**:
```python
def rotate_audit_log_if_needed(log_path: Path):
    """
    Rotate audit log when it exceeds 10MB.

    - Keep last 5 rotated files
    - Format: audit.log.1, audit.log.2, etc.
    """
    max_size = 10 * 1024 * 1024  # 10MB
    max_files = 5

    if log_path.stat().st_size > max_size:
        # Rotate existing files
        for i in range(max_files - 1, 0, -1):
            old_file = log_path.with_suffix(f".log.{i}")
            new_file = log_path.with_suffix(f".log.{i+1}")
            if old_file.exists():
                old_file.rename(new_file)

        # Rotate current log
        log_path.rename(log_path.with_suffix(".log.1"))
```

### 6. Hook Runner CLI

**Primary Command**:
```bash
# Emit event and run matching hooks
specify hooks run \
  --event-type "implement.completed" \
  --payload '{"feature": "auth", "task_id": "task-189"}'

# Emit from JSON file
specify hooks run --event-file event.json

# Dry-run (show matching hooks, no execution)
specify hooks run --event-type "task.completed" --dry-run
```

**Implementation**:
```python
@cli.command("hooks run")
@click.option("--event-type", required=True)
@click.option("--payload", type=str)
@click.option("--event-file", type=click.Path(exists=True))
@click.option("--dry-run", is_flag=True)
def hooks_run(event_type: str, payload: str, event_file: str, dry_run: bool):
    """Emit event and execute matching hooks."""

    # Load or construct event
    if event_file:
        with open(event_file) as f:
            event_data = json.load(f)
        event = Event(**event_data)
    else:
        payload_dict = json.loads(payload) if payload else {}
        event = Event(
            event_type=event_type,
            event_id=generate_event_id(),
            **payload_dict
        )

    # Load hook configuration
    hooks_config = load_hooks_config(".specify/hooks/hooks.yaml")

    # Match hooks to event
    matching_hooks = match_hooks(hooks_config, event)

    if dry_run:
        console.print(f"[blue]Matched {len(matching_hooks)} hooks for {event_type}:")
        for hook in matching_hooks:
            console.print(f"  - {hook.name}: {hook.description}")
        return

    # Execute hooks sequentially
    for hook in matching_hooks:
        console.print(f"[yellow]Running hook: {hook.name}...")
        try:
            result = execute_hook(hook, event)
            if result.status == "success":
                console.print(f"[green]✓ {hook.name} completed")
            elif result.status == "failed" and hook.fail_mode == "stop":
                console.print(f"[red]✗ {hook.name} failed (blocking)")
                sys.exit(1)
            else:
                console.print(f"[yellow]⚠ {hook.name} {result.status}")
        except Exception as e:
            console.print(f"[red]✗ {hook.name} error: {e}")
            if hook.fail_mode == "stop":
                sys.exit(1)
```

---

## Consequences

### Positive

1. **Security**: Multi-layer sandbox (path allowlist, timeout, env sanitization) prevents most attack vectors
2. **Reliability**: Fail-open default ensures hooks don't break workflows
3. **Observability**: Comprehensive audit log enables debugging and compliance
4. **Simplicity**: Sequential execution is easier to understand and debug than parallel
5. **Familiar Pattern**: stdin event delivery matches Git hooks, pre-commit framework

### Negative

1. **Performance**: Sequential execution means total hook time = sum of all hook times
   - Mitigation: Defer parallel execution to v2, optimize critical paths, enforce timeout limits
2. **Limited Isolation**: Hooks run with same privileges as CLI user
   - Mitigation: Document security model, recommend code review for all hooks
3. **No Network Controls**: v1 doesn't restrict network access from hooks
   - Mitigation: Document in threat model, defer to v2 with sandbox enhancements

### Neutral

1. **Sequential Ordering**: Hooks execute in config order
   - Trade-off: Predictable but slower vs. parallel but complex
2. **Synchronous Dispatch**: Workflow waits for hooks to complete
   - Trade-off: Simple but blocking vs. async but requires event queue

---

## Alternatives Considered

### Alternative 1: Docker Container Sandbox

**Approach**: Execute each hook in isolated Docker container.

**Example**:
```yaml
hooks:
  - name: "run-tests"
    docker_image: "python:3.11"
    command: "pytest tests/"
```

**Rejected Because**:
- Requires Docker daemon (heavy dependency)
- High latency (container startup 1-3s)
- Complex volume mounting for project access
- Overkill for local development workflows

**Note**: Could revisit for enterprise deployments with strict isolation requirements.

### Alternative 2: Python Plugin Architecture

**Approach**: Hooks are Python functions loaded dynamically.

**Example**:
```python
# .specify/hooks/run_tests.py
def on_implement_completed(event):
    import pytest
    return pytest.main(["-v"])
```

**Rejected Because**:
- Ties hooks to Python (not tool-agnostic)
- No support for shell scripts, other languages
- Security: arbitrary Python code is harder to sandbox than subprocess
- Requires plugin discovery and loading mechanism

### Alternative 3: Parallel Execution with asyncio

**Approach**: Execute all matching hooks concurrently using asyncio.

**Example**:
```python
async def execute_hooks_parallel(hooks, event):
    tasks = [execute_hook_async(hook, event) for hook in hooks]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

**Rejected for v1 Because**:
- Adds complexity (async/await, error handling across tasks)
- Harder to debug (interleaved output, race conditions)
- Most use cases don't need parallelism
- Can be added in v2 with --parallel flag

**Advantages if Implemented in v2**:
- Faster total execution time
- Better resource utilization

### Alternative 4: Hook Chaining/Pipelines

**Approach**: Output of one hook becomes input to next.

**Example**:
```yaml
hooks:
  - name: "run-tests"
    output: "test-results.json"
  - name: "upload-coverage"
    input: "test-results.json"
```

**Rejected for v1 Because**:
- Increased complexity (file handling, format negotiation)
- Tight coupling between hooks
- Not required for identified use cases

**Note**: Can be achieved in v1 by hooks writing to files explicitly.

---

## Implementation Guidance

### Hook Runner Module

**Location**: `src/specify_cli/hooks/runner.py`

**Key Functions**:
```python
class HookRunner:
    """Executes hooks in response to events."""

    def __init__(self, config_path: Path, project_root: Path):
        self.config = load_hooks_config(config_path)
        self.project_root = project_root
        self.audit_logger = AuditLogger(project_root / ".specify/hooks/audit.log")

    def run_hooks(self, event: Event) -> List[HookResult]:
        """Run all hooks matching event."""
        matching_hooks = self._match_hooks(event)

        results = []
        for hook in matching_hooks:
            result = self._execute_hook(hook, event)
            results.append(result)

            # Fail-stop on critical hooks
            if result.status != "success" and hook.fail_mode == "stop":
                raise HookExecutionError(f"Critical hook {hook.name} failed")

        return results

    def _execute_hook(self, hook: Hook, event: Event) -> HookResult:
        """Execute single hook with sandbox and logging."""
        # Security validation
        validate_script_path(hook.script, self.project_root)

        # Start audit log entry
        self.audit_logger.log_start(event.event_id, hook.name)

        try:
            # Execute with timeout
            result = execute_with_timeout(
                script_path=self.project_root / ".specify/hooks" / hook.script,
                timeout=hook.timeout,
                event_json=json.dumps(event.to_dict()),
                working_dir=self.project_root,
                env=sanitize_environment(hook.env),
            )

            # Log success
            self.audit_logger.log_success(
                event.event_id,
                hook.name,
                result.returncode,
                result.duration_ms,
            )

            return HookResult(status="success", exit_code=result.returncode)

        except HookTimeoutError as e:
            self.audit_logger.log_timeout(event.event_id, hook.name)
            raise
        except Exception as e:
            self.audit_logger.log_error(event.event_id, hook.name, str(e))
            raise
```

---

## Testing Strategy

### Security Tests

```python
def test_path_traversal_blocked():
    """Verify path traversal attacks are blocked."""
    hook = Hook(name="evil", script="../../etc/passwd")
    with pytest.raises(HookSecurityError, match="Path traversal"):
        validate_script_path(hook.script, "/tmp/project")

def test_timeout_enforcement():
    """Verify long-running hooks are killed."""
    hook = Hook(name="slow", script="sleep-forever.sh", timeout=1)
    with pytest.raises(HookTimeoutError):
        execute_hook(hook, test_event)

def test_shell_injection_blocked():
    """Verify shell metacharacters in env vars are blocked."""
    hook_env = {"CMD": "echo 'test'; rm -rf /"}
    safe_env = sanitize_environment(hook_env)
    assert "CMD" not in safe_env  # Blocked due to semicolon
```

### Error Handling Tests

```python
def test_fail_open_mode():
    """Verify fail-open hooks don't block workflow."""
    hook = Hook(name="optional", script="failing.sh", fail_mode="continue")
    result = execute_hook(hook, test_event)
    assert result.status == "failed"
    # Workflow should continue (no exception raised)

def test_fail_stop_mode():
    """Verify fail-stop hooks block workflow."""
    hook = Hook(name="critical", script="failing.sh", fail_mode="stop")
    with pytest.raises(HookExecutionError):
        execute_hook(hook, test_event)
```

### Audit Logging Tests

```python
def test_audit_log_format():
    """Verify audit log entries are valid JSONL."""
    runner = HookRunner(config_path, project_root)
    runner.run_hooks(test_event)

    with open(project_root / ".specify/hooks/audit.log") as f:
        for line in f:
            entry = json.loads(line)  # Should not raise
            assert "timestamp" in entry
            assert "event_id" in entry
            assert "hook" in entry
            assert "status" in entry
```

---

## References

- **ADR-005**: Event Model Architecture - Defines events that trigger hooks
- **ADR-003**: Stop Hook Quality Gate - Example of existing hook pattern
- **PRD**: `docs/prd/agent-hooks-prd.md` - Security threat model (Appendix C)
- **task-202**: Implement Hook Runner/Dispatcher
- **task-205**: Create Hook Security Framework

---

## Revision History

- **2025-12-02**: Initial decision (v1.0) - @software-architect
