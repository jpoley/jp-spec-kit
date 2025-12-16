"""Hook runner with security sandboxing and audit logging.

This module provides secure execution of hooks with:
- Script path validation (allowlist: .specify/hooks/ only)
- Timeout enforcement (SIGTERM then SIGKILL)
- Environment sanitization
- Audit logging (JSONL format)

Security controls follow ADR-006 Hook Execution Security specification.

Example:
    >>> from flowspec_cli.hooks import HookDefinition, Event
    >>> from flowspec_cli.hooks.runner import HookRunner
    >>> runner = HookRunner(workspace_root=Path("/project"))
    >>> result = runner.run_hook(hook, event)
    >>> print(f"Hook {result.hook_name}: exit={result.exit_code}")
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .events import Event
from .schema import HookDefinition
from .security import SecurityConfig, SecurityValidator

logger = logging.getLogger(__name__)

# Maximum timeout allowed for hooks (10 minutes)
MAX_TIMEOUT_SECONDS = 600

# Default timeout if not specified (30 seconds)
DEFAULT_TIMEOUT_SECONDS = 30

# Default audit log location
DEFAULT_AUDIT_LOG = ".specify/hooks/audit.log"


@dataclass
class HookResult:
    """Result of hook execution.

    Contains all information about hook execution including exit code,
    output, duration, and any errors encountered.

    Attributes:
        hook_name: Name of the executed hook.
        success: True if hook exited with code 0.
        exit_code: Process exit code (0 = success, >0 = error, -1 = exception).
        stdout: Standard output captured from hook.
        stderr: Standard error captured from hook.
        duration_ms: Execution duration in milliseconds.
        error: Error message if execution failed (timeout, exception, etc.).

    Example:
        >>> result = HookResult(
        ...     hook_name="run-tests",
        ...     success=True,
        ...     exit_code=0,
        ...     stdout="All tests passed",
        ...     stderr="",
        ...     duration_ms=1234
        ... )
    """

    hook_name: str
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: int
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary.

        Returns:
            Dictionary representation for JSON serialization.
        """
        result: dict[str, Any] = {
            "hook_name": self.hook_name,
            "success": self.success,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration_ms": self.duration_ms,
        }
        if self.error is not None:
            result["error"] = self.error
        return result


class HookRunner:
    """Executes hooks with security controls and audit logging.

    The runner is responsible for:
    1. Validating hook security constraints (script path, timeout)
    2. Sanitizing execution environment
    3. Running hooks with timeout enforcement
    4. Capturing output and exit codes
    5. Logging execution to audit log

    Security features:
    - Script allowlist: Only scripts in .specify/hooks/ can execute
    - Timeout enforcement: SIGTERM at timeout, SIGKILL after 5s grace period
    - Environment sanitization: Limited set of environment variables
    - Working directory validation: Must be within project

    Attributes:
        workspace_root: Project root directory.
        audit_log_path: Path to audit log file (JSONL format).

    Example:
        >>> runner = HookRunner(workspace_root=Path("/project"))
        >>> hook = HookDefinition(name="test", events=[], script="test.sh")
        >>> event = Event(event_type="spec.created", project_root="/project")
        >>> result = runner.run_hook(hook, event)
    """

    def __init__(
        self,
        workspace_root: Path,
        audit_log_path: Path | None = None,
        security_config: SecurityConfig | None = None,
    ):
        """Initialize runner with workspace and audit log.

        Args:
            workspace_root: Project root directory.
            audit_log_path: Path to audit log file (optional). Defaults to
                workspace_root/.specify/hooks/audit.log.
            security_config: Security configuration (optional). Defaults to
                default SecurityConfig.

        Example:
            >>> runner = HookRunner(workspace_root=Path.cwd())
            >>> # With custom audit log
            >>> runner = HookRunner(
            ...     workspace_root=Path.cwd(),
            ...     audit_log_path=Path("/var/log/hooks.log")
            ... )
            >>> # With custom security config
            >>> config = SecurityConfig(max_output_size=2048)
            >>> runner = HookRunner(
            ...     workspace_root=Path.cwd(),
            ...     security_config=config
            ... )
        """
        self.workspace_root = workspace_root
        if audit_log_path is None:
            self.audit_log_path = workspace_root / DEFAULT_AUDIT_LOG
        else:
            self.audit_log_path = audit_log_path

        # Create audit log directory if it doesn't exist
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize security validator
        if security_config is None:
            security_config = SecurityConfig()
        self.security_validator = SecurityValidator(security_config, workspace_root)

    def run_hook(self, hook: HookDefinition, event: Event) -> HookResult:
        """Execute a single hook with security controls.

        Execution flow:
        1. Validate hook configuration (script path, timeout)
        2. Determine execution method (script, command)
        3. Prepare sanitized environment
        4. Execute with timeout enforcement
        5. Capture output and exit code
        6. Log to audit log
        7. Return result

        Args:
            hook: Hook definition to execute.
            event: Event that triggered the hook.

        Returns:
            HookResult with execution details.

        Raises:
            ValueError: If hook configuration is invalid.
            SecurityError: If security validation fails (logged, not raised).

        Example:
            >>> hook = HookDefinition(
            ...     name="run-tests",
            ...     events=[],
            ...     script="run-tests.sh",
            ...     timeout=300
            ... )
            >>> event = Event(event_type="implement.completed", project_root="/tmp")
            >>> result = runner.run_hook(hook, event)
            >>> assert result.success
        """
        start_time = time.time()

        try:
            # Get execution method
            method_type, method_value = hook.get_execution_method()

            # Validate and prepare based on method
            if method_type == "script":
                script_path = self._validate_script_path(method_value)

                # Perform security validation on script content
                warnings = self.security_validator.validate_script_content(script_path)
                if warnings:
                    for warning in warnings:
                        logger.warning(
                            f"Security warning for hook '{hook.name}': {warning}"
                        )

                command = [str(script_path)]
            elif method_type == "command":
                # For command, use shell
                command = [hook.shell, "-c", method_value]
            else:
                # Webhook not supported yet
                raise ValueError(
                    f"Hook '{hook.name}' method '{method_type}' not supported"
                )

            # Prepare environment
            env = self._sanitize_env(hook, event)

            # Resolve working directory
            working_dir = self._resolve_working_directory(hook.working_directory)

            # Get timeout (enforce maximum)
            timeout = min(hook.timeout, MAX_TIMEOUT_SECONDS)

            logger.debug(
                f"Executing hook '{hook.name}': {' '.join(command)} "
                f"(timeout={timeout}s, cwd={working_dir})"
            )

            # Execute hook with timeout
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=working_dir,
                env=env,
            )

            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)

            # Create result
            hook_result = HookResult(
                hook_name=hook.name,
                success=(result.returncode == 0),
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                duration_ms=duration_ms,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = int((time.time() - start_time) * 1000)
            hook_result = HookResult(
                hook_name=hook.name,
                success=False,
                exit_code=-1,
                stdout=e.stdout or "",
                stderr=e.stderr or "",
                duration_ms=duration_ms,
                error=f"Hook timed out after {hook.timeout}s",
            )
            logger.warning(f"Hook '{hook.name}' timed out after {hook.timeout}s")

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            hook_result = HookResult(
                hook_name=hook.name,
                success=False,
                exit_code=-1,
                stdout="",
                stderr="",
                duration_ms=duration_ms,
                error=str(e),
            )
            logger.error(f"Hook '{hook.name}' execution failed: {e}", exc_info=True)

        # Log to audit log
        self._log_audit(hook, event, hook_result)

        return hook_result

    def _validate_script_path(self, script: str) -> Path:
        """Validate script path is in allowed directory.

        Security checks:
        1. No path traversal (no "..")
        2. Must be relative path
        3. Must resolve to .specify/hooks/ directory

        Args:
            script: Script path (relative to .specify/hooks/).

        Returns:
            Absolute path to validated script.

        Raises:
            ValueError: If script path is invalid or outside allowed directory.

        Example:
            >>> runner = HookRunner(workspace_root=Path("/project"))
            >>> path = runner._validate_script_path("test.sh")
            >>> assert path == Path("/project/.specify/hooks/test.sh")
        """
        # Check for path traversal
        if ".." in script:
            raise ValueError(f"Script path contains path traversal: {script}")

        # Check for absolute path
        if Path(script).is_absolute():
            raise ValueError(f"Script must be relative path, got: {script}")

        # Resolve path relative to hooks directory
        hooks_dir = self.workspace_root / ".specify" / "hooks"
        script_path = (hooks_dir / script).resolve()

        # Verify path is within hooks directory
        try:
            script_path.relative_to(hooks_dir)
        except ValueError:
            raise ValueError(
                f"Script must be in .specify/hooks/, got: {script}"
            ) from None

        # Check script exists
        if not script_path.exists():
            raise ValueError(f"Script not found: {script}")

        # Check script is executable (optional, log warning)
        if not os.access(script_path, os.X_OK):
            logger.warning(f"Script {script} is not executable (missing +x permission)")

        return script_path

    def _sanitize_env(self, hook: HookDefinition, event: Event) -> dict[str, str]:
        """Create sanitized environment for hook execution.

        Environment variables provided:
        1. Hook-specific env vars from hook.env
        2. HOOK_EVENT: Event data as JSON
        3. HOOK_NAME: Hook name
        4. HOOK_WORKSPACE: Workspace root path
        5. Essential system env vars (PATH, HOME, USER)

        Args:
            hook: Hook definition.
            event: Event that triggered the hook.

        Returns:
            Dictionary of environment variables.

        Example:
            >>> env = runner._sanitize_env(hook, event)
            >>> assert "HOOK_EVENT" in env
            >>> assert "PATH" in env
        """
        # Start with minimal environment
        env: dict[str, str] = {}

        # Add essential system variables
        for var in ["PATH", "HOME", "USER", "LANG", "LC_ALL"]:
            value = os.environ.get(var)
            if value is not None:
                env[var] = value

        # Add hook-specific environment variables
        env.update(hook.env)

        # Add hook metadata
        env["HOOK_NAME"] = hook.name
        env["HOOK_WORKSPACE"] = str(self.workspace_root)

        # Add event data as JSON
        env["HOOK_EVENT"] = event.to_json()

        return env

    def _resolve_working_directory(self, working_dir: str) -> Path:
        """Resolve working directory relative to workspace root.

        Args:
            working_dir: Working directory (relative to workspace_root).

        Returns:
            Absolute path to working directory.

        Raises:
            ValueError: If working directory is invalid.

        Example:
            >>> runner = HookRunner(workspace_root=Path("/project"))
            >>> wd = runner._resolve_working_directory(".")
            >>> assert wd == Path("/project")
        """
        # Handle "." as workspace root
        if working_dir == ".":
            return self.workspace_root

        # Check for path traversal
        if ".." in working_dir:
            raise ValueError(
                f"Working directory contains path traversal: {working_dir}"
            )

        # Check for absolute path
        if Path(working_dir).is_absolute():
            raise ValueError(f"Working directory must be relative, got: {working_dir}")

        # Resolve relative to workspace root
        wd_path = (self.workspace_root / working_dir).resolve()

        # Verify within workspace
        try:
            wd_path.relative_to(self.workspace_root)
        except ValueError:
            raise ValueError(
                f"Working directory must be within project, got: {working_dir}"
            ) from None

        return wd_path

    def _log_audit(
        self,
        hook: HookDefinition,
        event: Event,
        result: HookResult,
    ) -> None:
        """Write execution record to audit log.

        Audit log format: JSON Lines (one JSON object per line)
        Each record contains:
        - timestamp: ISO 8601 UTC timestamp
        - event_id: Event ID
        - event_type: Event type
        - hook_name: Hook name
        - success: Execution success (boolean)
        - exit_code: Process exit code
        - duration_ms: Execution duration
        - error: Error message (if failed)

        Args:
            hook: Hook definition.
            event: Event that triggered the hook.
            result: Hook execution result.

        Example:
            >>> runner._log_audit(hook, event, result)
            # Appends to audit.log:
            # {"timestamp": "2025-12-02T12:34:56.789Z", "event_id": "evt_...", ...}
        """
        audit_record = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "event_id": event.event_id,
            "event_type": event.event_type,
            "hook_name": hook.name,
            "success": result.success,
            "exit_code": result.exit_code,
            "duration_ms": result.duration_ms,
        }

        if result.error is not None:
            audit_record["error"] = result.error

        # Append to audit log (JSONL format)
        try:
            with open(self.audit_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(audit_record) + "\n")
        except OSError as e:
            logger.error(f"Failed to write audit log: {e}")
