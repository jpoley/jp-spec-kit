# Hook Security Framework

## Overview

The Flowspec hook security framework provides defense-in-depth protection for hook script execution through sandboxing, validation, monitoring, and audit logging. This document defines the security architecture, controls, and implementation requirements for task-205.

## Security Principles

1. **Fail-Safe Defaults**: Security controls enabled by default, opt-out requires explicit configuration
2. **Least Privilege**: Hooks run with minimal permissions necessary for their function
3. **Defense in Depth**: Multiple layers of security controls (validation, sandboxing, monitoring, auditing)
4. **Transparency**: All security events logged to immutable audit trail
5. **Usability**: Security controls don't impede legitimate use cases

## Threat Model

### Threat Actors

1. **Malicious Insider**: Developer with repository write access commits malicious hook
2. **Compromised Developer**: Attacker gains access to developer's workstation
3. **Supply Chain Attack**: Malicious dependency injects hooks during installation
4. **Unintentional Damage**: Developer creates destructive hook without malicious intent

### Attack Vectors

| Vector | Threat | Likelihood | Impact | Mitigation |
|--------|--------|------------|--------|------------|
| Command Injection | Shell metacharacters in event payload execute arbitrary commands | Medium | High | Event payload passed via stdin (JSON), not shell args |
| Path Traversal | Hook references script outside `.specify/hooks/` (e.g., `../../etc/passwd`) | Medium | High | Path validation rejects `..` and absolute paths |
| Resource Exhaustion | Infinite loop or forkbomb in hook script | Low | Medium | Timeout enforcement with SIGKILL |
| Privilege Escalation | Hook exploits setuid binary or sudo to gain root | Low | Critical | Hooks run as current user, no privilege escalation |
| Data Exfiltration | Hook sends secrets to external server | Medium | High | Audit logging (v1), network controls (v2) |
| Destructive Operations | Hook deletes critical files or corrupts repository | Low | High | Dangerous command detection with warnings |

## Security Controls

### 1. Script Allowlist

**Control**: Only execute scripts from the `.specify/hooks/` directory (or subdirectories).

**Implementation**:
```python
import os
from pathlib import Path

def validate_script_path(script_path: str, hooks_dir: Path) -> Path:
    """
    Validate that script path is within allowed directory.

    Raises:
        ValueError: If path is invalid or outside hooks directory
    """
    # Resolve absolute path
    resolved = Path(script_path).resolve()
    hooks_dir_resolved = hooks_dir.resolve()

    # Check if path is within hooks directory
    try:
        resolved.relative_to(hooks_dir_resolved)
    except ValueError:
        raise ValueError(
            f"Hook script path '{script_path}' is outside allowed directory "
            f"'{hooks_dir}'. All scripts must be in .specify/hooks/"
        )

    # Reject absolute paths and path traversal
    if script_path.startswith('/') or '..' in script_path:
        raise ValueError(
            f"Hook script path '{script_path}' contains forbidden components. "
            f"Use relative paths without '..' segments."
        )

    # Verify script exists and is executable
    if not resolved.exists():
        raise ValueError(f"Hook script '{script_path}' does not exist")

    if not os.access(resolved, os.X_OK):
        raise ValueError(f"Hook script '{script_path}' is not executable. "
                        f"Run: chmod +x {resolved}")

    return resolved
```

**Test Cases**:
- ✅ `.specify/hooks/test.sh` → ALLOW
- ✅ `.specify/hooks/subdir/test.sh` → ALLOW
- ❌ `../../etc/passwd` → REJECT (path traversal)
- ❌ `/bin/rm` → REJECT (absolute path)
- ❌ `.specify/hooks/../../../etc/passwd` → REJECT (resolved outside hooks_dir)

### 2. Timeout Enforcement

**Control**: Terminate scripts that exceed configured timeout (default 30s, max 600s).

**Implementation**:
```python
import subprocess
import signal
from typing import Optional

class TimeoutError(Exception):
    """Raised when script execution exceeds timeout"""
    pass

def execute_with_timeout(
    cmd: list[str],
    timeout: int,
    cwd: Path,
    env: dict[str, str]
) -> subprocess.CompletedProcess:
    """
    Execute command with timeout enforcement.

    Args:
        cmd: Command and arguments to execute
        timeout: Timeout in seconds
        cwd: Working directory
        env: Environment variables

    Returns:
        CompletedProcess with stdout, stderr, returncode

    Raises:
        TimeoutError: If command exceeds timeout
    """
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False  # Don't raise on non-zero exit
        )
        return result
    except subprocess.TimeoutExpired:
        raise TimeoutError(
            f"Hook exceeded timeout of {timeout}s. "
            f"Increase timeout in hooks.yaml or optimize script."
        )
```

**Timeout Configuration**:
```yaml
# .specify/hooks/hooks.yaml
defaults:
  timeout: 30  # Global default (30 seconds)

hooks:
  - name: "quick-check"
    timeout: 5  # Override for fast checks

  - name: "run-tests"
    timeout: 300  # 5 minutes for test suite

  - name: "long-build"
    timeout: 600  # Max allowed: 10 minutes
```

**Process Termination Strategy**:
1. Send SIGTERM after timeout (graceful shutdown)
2. Wait 5 seconds for cleanup
3. Send SIGKILL if still running (forceful termination)

### 3. Environment Variable Sanitization

**Control**: Prevent shell injection via environment variables and sanitize sensitive values.

**Implementation**:
```python
import re
import os
from typing import Dict, Set

# Environment variables that should never be passed to hooks
BLOCKED_ENV_VARS: Set[str] = {
    'LD_PRELOAD',      # Library injection
    'LD_LIBRARY_PATH', # Library path manipulation
    'PYTHONPATH',      # Python module injection
    'PATH',            # Command hijacking (use explicit PATH)
    'IFS',             # Shell field separator manipulation
}

# Pattern for shell metacharacters
SHELL_METACHAR_PATTERN = re.compile(r'[;&|`$<>(){}]')

def sanitize_environment(
    hook_env: Dict[str, str],
    base_env: Optional[Dict[str, str]] = None
) -> Dict[str, str]:
    """
    Sanitize environment variables for hook execution.

    Args:
        hook_env: Environment variables from hooks.yaml
        base_env: Base environment (defaults to minimal safe env)

    Returns:
        Sanitized environment dictionary

    Raises:
        ValueError: If dangerous environment variables detected
    """
    if base_env is None:
        # Minimal safe environment
        base_env = {
            'PATH': '/usr/local/bin:/usr/bin:/bin',
            'HOME': os.environ.get('HOME', '/tmp'),
            'USER': os.environ.get('USER', 'unknown'),
            'LANG': 'C.UTF-8',
        }

    env = base_env.copy()

    for key, value in hook_env.items():
        # Block dangerous environment variables
        if key in BLOCKED_ENV_VARS:
            raise ValueError(
                f"Hook environment variable '{key}' is blocked for security. "
                f"Blocked vars: {', '.join(BLOCKED_ENV_VARS)}"
            )

        # Warn on shell metacharacters (allow but log)
        if SHELL_METACHAR_PATTERN.search(value):
            # Log warning but allow (might be legitimate JSON, etc.)
            # Warning logged in audit log
            pass

        env[key] = value

    return env
```

**Environment Variable Guidelines**:
- ✅ Simple values: `FEATURE_NAME=auth`, `TIMEOUT=30`
- ✅ JSON/structured data: `EVENT_PAYLOAD='{"type":"task.completed"}'`
- ⚠️ Shell metacharacters: Allowed but logged (may be legitimate)
- ❌ Blocked variables: `LD_PRELOAD`, `PYTHONPATH`, etc.

### 4. Working Directory Restrictions

**Control**: Constrain working directory to project root or subdirectories.

**Implementation**:
```python
def validate_working_directory(
    working_dir: str,
    project_root: Path
) -> Path:
    """
    Validate that working directory is within project root.

    Args:
        working_dir: Requested working directory (relative to project root)
        project_root: Absolute path to project root

    Returns:
        Absolute path to validated working directory

    Raises:
        ValueError: If working_dir is outside project root
    """
    # Resolve absolute path
    if working_dir == '.':
        return project_root

    resolved = (project_root / working_dir).resolve()

    # Verify it's within project root
    try:
        resolved.relative_to(project_root)
    except ValueError:
        raise ValueError(
            f"Working directory '{working_dir}' is outside project root. "
            f"Hooks must run within the project."
        )

    return resolved
```

**Configuration**:
```yaml
hooks:
  - name: "frontend-tests"
    working_directory: "./frontend"  # Allowed (within project)

  - name: "backend-tests"
    working_directory: "./backend"   # Allowed

  - name: "invalid"
    working_directory: "/tmp"        # REJECTED (outside project)
```

### 5. Dangerous Command Detection

**Control**: Warn users about destructive operations in hook scripts.

**Implementation**:
```python
from pathlib import Path
import re
from typing import List, Tuple

# Patterns for dangerous commands
DANGEROUS_PATTERNS = [
    (r'\brm\s+-rf\s+/', "Recursive deletion of root directory"),
    (r'\bdd\s+.*of=/dev/', "Writing to block device"),
    (r':\(\)\{.*;\}', "Fork bomb pattern"),
    (r'curl.*\|\s*sh', "Executing remote code via curl"),
    (r'wget.*\|\s*sh', "Executing remote code via wget"),
    (r'chmod\s+777', "World-writable permissions"),
    (r'>>/etc/', "Writing to system configuration"),
]

def scan_for_dangerous_commands(script_path: Path) -> List[Tuple[str, str]]:
    """
    Scan hook script for dangerous command patterns.

    Args:
        script_path: Path to hook script

    Returns:
        List of (pattern, description) tuples for detected dangers
    """
    with open(script_path, 'r') as f:
        content = f.read()

    findings = []
    for pattern, description in DANGEROUS_PATTERNS:
        if re.search(pattern, content):
            findings.append((pattern, description))

    return findings

def validate_hook_script(script_path: Path) -> None:
    """
    Validate hook script and warn about dangerous operations.

    Raises:
        Warning: If dangerous patterns detected (non-blocking)
    """
    findings = scan_for_dangerous_commands(script_path)

    if findings:
        warnings = '\n'.join(f"  - {desc}" for _, desc in findings)
        print(f"⚠️  WARNING: Hook '{script_path.name}' contains dangerous operations:\n{warnings}")
        print(f"    Review script carefully before execution.")
```

**Warning Example**:
```bash
$ specify hooks validate
⚠️  WARNING: Hook 'cleanup.sh' contains dangerous operations:
  - Recursive deletion of root directory
  - World-writable permissions
    Review script carefully before execution.
```

### 6. Audit Logging

**Control**: Immutable audit trail of all hook executions for forensics and compliance.

**Schema**:
```json
{
  "timestamp": "2025-12-02T15:30:45.123Z",
  "event_id": "evt_01HQZX123ABC",
  "event_type": "implement.completed",
  "hook_name": "run-tests",
  "hook_version": "1.0",
  "status": "success|failed|timeout|error",
  "exit_code": 0,
  "duration_ms": 30333,
  "script_path": ".specify/hooks/run-tests.sh",
  "working_directory": "/home/user/project",
  "environment_keys": ["PYTEST_ARGS", "FEATURE_NAME"],
  "pid": 12345,
  "user": "jpoley",
  "stdout_lines": 42,
  "stderr_lines": 0,
  "security_warnings": [],
  "metadata": {
    "cli_version": "0.0.179",
    "python_version": "3.11.9"
  }
}
```

**Implementation**:
```python
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List

class AuditLogger:
    """Immutable audit logger for hook executions"""

    def __init__(self, audit_log_path: Path):
        self.audit_log_path = audit_log_path
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_execution(
        self,
        event_id: str,
        event_type: str,
        hook_name: str,
        status: str,
        exit_code: int,
        duration_ms: int,
        script_path: str,
        environment: Dict[str, str],
        stdout: str,
        stderr: str,
        security_warnings: List[str] = None
    ) -> None:
        """
        Log hook execution to audit trail.

        Args:
            event_id: Unique event identifier
            event_type: Event type that triggered hook
            hook_name: Name of hook from configuration
            status: success|failed|timeout|error
            exit_code: Script exit code
            duration_ms: Execution duration in milliseconds
            script_path: Path to executed script
            environment: Environment variables (keys only for privacy)
            stdout: Standard output from script
            stderr: Standard error from script
            security_warnings: List of security warnings during validation
        """
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_id": event_id,
            "event_type": event_type,
            "hook_name": hook_name,
            "status": status,
            "exit_code": exit_code,
            "duration_ms": duration_ms,
            "script_path": script_path,
            "environment_keys": list(environment.keys()),
            "stdout_lines": len(stdout.splitlines()) if stdout else 0,
            "stderr_lines": len(stderr.splitlines()) if stderr else 0,
            "security_warnings": security_warnings or [],
            "user": os.environ.get('USER', 'unknown'),
            "metadata": {
                "cli_version": get_version(),
                "python_version": platform.python_version(),
            }
        }

        # Append to audit log (JSONL format)
        with open(self.audit_log_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def log_security_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        context: Dict[str, Any]
    ) -> None:
        """
        Log security event (validation failure, policy violation, etc.)

        Args:
            event_type: Type of security event (path_traversal, timeout, etc.)
            severity: critical|high|medium|low
            description: Human-readable description
            context: Additional context (hook name, script path, etc.)
        """
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "security_event",
            "event_type": event_type,
            "severity": severity,
            "description": description,
            "context": context,
            "user": os.environ.get('USER', 'unknown'),
        }

        with open(self.audit_log_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')
```

**Log Rotation**:
- Rotate at 10MB file size
- Keep last 5 files (50MB total)
- Rotation preserves chronological order
- Old logs archived to `.specify/hooks/audit.log.1`, `.specify/hooks/audit.log.2`, etc.

**Log Retention**:
- Default: 30 days
- Configurable via `audit_retention_days` in hooks.yaml
- Automated cleanup on `specify hooks cleanup`

### 7. Configuration Validation

**Control**: Validate hooks.yaml against JSON schema before loading.

**Schema Validation**:
```python
import jsonschema
import yaml

HOOKS_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["version", "hooks"],
    "properties": {
        "version": {"type": "string", "enum": ["1.0"]},
        "defaults": {
            "type": "object",
            "properties": {
                "timeout": {"type": "integer", "minimum": 1, "maximum": 600},
                "working_directory": {"type": "string"},
                "shell": {"type": "string"},
                "fail_mode": {"enum": ["continue", "stop"]}
            }
        },
        "hooks": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "events"],
                "properties": {
                    "name": {
                        "type": "string",
                        "pattern": "^[a-z0-9-]+$"
                    },
                    "description": {"type": "string"},
                    "events": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "object",
                            "required": ["type"],
                            "properties": {
                                "type": {"type": "string"},
                                "filter": {"type": "object"}
                            }
                        }
                    },
                    "script": {"type": "string"},
                    "command": {"type": "string"},
                    "timeout": {"type": "integer", "minimum": 1, "maximum": 600},
                    "env": {"type": "object"},
                    "fail_mode": {"enum": ["continue", "stop"]},
                    "enabled": {"type": "boolean"}
                },
                "oneOf": [
                    {"required": ["script"]},
                    {"required": ["command"]}
                ]
            }
        }
    }
}

def validate_hooks_config(config_path: Path) -> Dict[str, Any]:
    """
    Validate hooks.yaml against schema.

    Returns:
        Validated configuration dict

    Raises:
        ValueError: If configuration is invalid
    """
    with open(config_path) as f:
        config = yaml.safe_load(f)

    try:
        jsonschema.validate(config, HOOKS_SCHEMA)
    except jsonschema.ValidationError as e:
        raise ValueError(f"Invalid hooks.yaml: {e.message}")

    return config
```

## Security Testing

### Unit Tests

```python
# tests/test_security.py

def test_path_traversal_rejected():
    """Verify path traversal attempts are blocked"""
    with pytest.raises(ValueError, match="outside allowed directory"):
        validate_script_path("../../etc/passwd", Path(".specify/hooks"))

def test_absolute_path_rejected():
    """Verify absolute paths are blocked"""
    with pytest.raises(ValueError, match="forbidden components"):
        validate_script_path("/bin/rm", Path(".specify/hooks"))

def test_dangerous_command_detection():
    """Verify dangerous commands are flagged"""
    script = Path("/tmp/malicious.sh")
    script.write_text("#!/bin/bash\nrm -rf /")

    findings = scan_for_dangerous_commands(script)
    assert len(findings) > 0
    assert any("Recursive deletion" in desc for _, desc in findings)

def test_environment_sanitization():
    """Verify dangerous env vars are blocked"""
    with pytest.raises(ValueError, match="is blocked"):
        sanitize_environment({"LD_PRELOAD": "/tmp/evil.so"})

def test_timeout_enforcement():
    """Verify scripts are killed after timeout"""
    cmd = ["sleep", "60"]

    with pytest.raises(TimeoutError):
        execute_with_timeout(cmd, timeout=1, cwd=Path.cwd(), env={})
```

### Integration Tests

```python
# tests/integration/test_hook_security.py

def test_malicious_hook_blocked(tmp_path):
    """Verify malicious hook cannot execute"""
    hooks_dir = tmp_path / ".specify" / "hooks"
    hooks_dir.mkdir(parents=True)

    # Attempt path traversal
    config = {
        "version": "1.0",
        "hooks": [{
            "name": "malicious",
            "events": [{"type": "test.event"}],
            "script": "../../etc/passwd"
        }]
    }

    with pytest.raises(ValueError, match="outside allowed directory"):
        load_and_validate_hooks(config, tmp_path)

def test_timeout_kills_infinite_loop(tmp_path):
    """Verify infinite loop is terminated"""
    hooks_dir = tmp_path / ".specify" / "hooks"
    hooks_dir.mkdir(parents=True)

    script = hooks_dir / "infinite.sh"
    script.write_text("#!/bin/bash\nwhile true; do sleep 1; done")
    script.chmod(0o755)

    config = {
        "version": "1.0",
        "hooks": [{
            "name": "infinite",
            "events": [{"type": "test.event"}],
            "script": ".specify/hooks/infinite.sh",
            "timeout": 2
        }]
    }

    result = run_hook(config["hooks"][0], {}, tmp_path)
    assert result.status == "timeout"
    assert result.duration_ms < 3000
```

### Penetration Testing

**Test Cases**:
1. **Command Injection**: Attempt to inject shell commands via event payload
2. **Path Traversal**: Attempt to reference scripts outside `.specify/hooks/`
3. **Resource Exhaustion**: Attempt to consume all CPU/memory via forkbomb
4. **Privilege Escalation**: Attempt to gain root via setuid binary exploitation
5. **Data Exfiltration**: Attempt to exfiltrate secrets via network requests

## Compliance and Reporting

### SOC2 Controls

| Control ID | Description | Implementation |
|------------|-------------|----------------|
| CC6.1 | Logical access controls | Script allowlist, environment sanitization |
| CC6.6 | Audit logging | Immutable audit trail in `.specify/hooks/audit.log` |
| CC7.2 | Change monitoring | Security events logged when hooks modified |
| CC7.3 | Malware protection | Dangerous command detection |

### Audit Reports

```bash
# Generate security audit report
specify hooks audit --security-report --start-date 2025-12-01 --end-date 2025-12-31

# Output:
# Security Audit Report: 2025-12-01 to 2025-12-31
# ================================================
#
# Hook Executions: 1,234
# Security Events: 5
#   - path_traversal: 2
#   - timeout: 3
#
# Top Hooks by Execution:
#   1. run-tests: 456 executions (0 failures)
#   2. update-docs: 234 executions (1 failure)
#
# Security Recommendations:
#   - Review timeout configuration for 'long-build' hook (avg 580s, approaching 600s limit)
#   - Script 'cleanup.sh' contains dangerous operations, consider review
```

## Implementation Checklist (task-205)

Security framework implementation steps:

### Phase 1: Core Validation (Week 1)
- [ ] Implement `validate_script_path()` with path traversal prevention
- [ ] Implement `sanitize_environment()` with blocked var checks
- [ ] Implement `validate_working_directory()` with project root constraint
- [ ] Implement JSON schema validation for hooks.yaml
- [ ] Write unit tests for all validation functions

### Phase 2: Execution Sandbox (Week 2)
- [ ] Implement `execute_with_timeout()` with SIGTERM/SIGKILL
- [ ] Implement environment variable passing via subprocess
- [ ] Implement working directory constraint in subprocess
- [ ] Write integration tests for timeout enforcement
- [ ] Write integration tests for environment sanitization

### Phase 3: Monitoring & Detection (Week 3)
- [ ] Implement `scan_for_dangerous_commands()` with pattern detection
- [ ] Implement `AuditLogger` class with JSONL format
- [ ] Implement `log_execution()` for all hook runs
- [ ] Implement `log_security_event()` for violations
- [ ] Implement log rotation at 10MB threshold
- [ ] Write tests for audit logging

### Phase 4: Documentation & Testing (Week 4)
- [ ] Write security documentation (threat model, controls, guidelines)
- [ ] Write penetration testing suite
- [ ] Run security review with checklist
- [ ] Generate compliance mapping (SOC2, etc.)
- [ ] Create example secure hooks for documentation

## References

- [OWASP Command Injection](https://owasp.org/www-community/attacks/Command_Injection)
- [CWE-78: OS Command Injection](https://cwe.mitre.org/data/definitions/78.html)
- [Python subprocess Security](https://docs.python.org/3/library/subprocess.html#security-considerations)
- [SOC2 Trust Services Criteria](https://www.aicpa.org/resources/download/trust-services-criteria)
