"""Security controls for flowspec hooks.

This module provides enhanced security validation and audit logging for hook execution:
- Dangerous pattern detection in script content
- Script integrity verification (SHA-256 hashing)
- Audit log integrity verification
- Path validation and access controls

Security features:
- Detects dangerous shell patterns (rm -rf /, fork bombs, etc.)
- Computes script hashes for audit trail
- Tamper-detection for audit logs
- Configurable security policies

Example:
    >>> from flowspec_cli.hooks.security import SecurityValidator, SecurityConfig
    >>> config = SecurityConfig(allowed_paths=[Path("/project")])
    >>> validator = SecurityValidator(config, workspace_root=Path("/project"))
    >>> warnings = validator.validate_script_content(Path("script.sh"))
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SecurityConfig:
    """Security configuration for hooks.

    Attributes:
        allowed_paths: Paths scripts can read from (for future use).
        blocked_commands: Commands to block (for future use).
        max_output_size: Maximum stdout/stderr size in bytes.
        allow_network: Whether to allow network access (v2 feature).

    Example:
        >>> config = SecurityConfig(
        ...     allowed_paths=[Path("/project")],
        ...     blocked_commands=["rm -rf /"],
        ...     max_output_size=1024 * 1024,  # 1MB
        ...     allow_network=False
        ... )
    """

    allowed_paths: list[Path] = field(default_factory=list)
    blocked_commands: list[str] = field(default_factory=list)
    max_output_size: int = 1024 * 1024  # 1MB max stdout/stderr
    allow_network: bool = False  # Network access (v2)


class SecurityValidator:
    """Validates hook execution against security policies.

    Performs content-based security checks on hook scripts:
    - Detects dangerous shell patterns (destructive commands, fork bombs)
    - Computes script hashes for integrity verification
    - Warns about potentially dangerous operations

    Attributes:
        config: Security configuration.
        workspace_root: Project workspace root directory.

    Example:
        >>> validator = SecurityValidator(
        ...     config=SecurityConfig(),
        ...     workspace_root=Path("/project")
        ... )
        >>> warnings = validator.validate_script_content(Path("hook.sh"))
        >>> if warnings:
        ...     print(f"Security warnings: {warnings}")
    """

    # Dangerous patterns that should trigger warnings
    # These patterns match destructive or malicious shell commands
    DANGEROUS_PATTERNS = [
        (r"rm\s+-rf\s+/", "Recursive deletion of root directory"),
        (r"rm\s+-rf\s+~", "Recursive deletion of home directory"),
        (r"rm\s+-rf\s+\$HOME", "Recursive deletion of home directory"),
        (r"dd\s+if=", "Direct disk access (dd command)"),
        (r">\s*/dev/sd[a-z]", "Writing to block device"),
        (r"mkfs\.", "Filesystem formatting"),
        (r":\(\)\s*\{\s*:\|:\s*&\s*\}\s*;:", "Fork bomb pattern"),
        (r"chmod\s+-R\s+777", "Overly permissive file permissions"),
        (r"curl.*\|\s*bash", "Piping remote content to bash"),
        (r"wget.*\|\s*sh", "Piping remote content to shell"),
        (r"eval\s+\$\(curl", "Evaluating remote code"),
        (r"base64\s+-d.*\|\s*bash", "Executing base64-encoded commands"),
    ]

    def __init__(self, config: SecurityConfig, workspace_root: Path):
        """Initialize validator with security configuration.

        Args:
            config: Security configuration.
            workspace_root: Project workspace root directory.

        Example:
            >>> config = SecurityConfig(allowed_paths=[Path("/project")])
            >>> validator = SecurityValidator(config, Path("/project"))
        """
        self.config = config
        self.workspace_root = workspace_root

    def validate_script_content(self, script_path: Path) -> list[str]:
        """Check script content for dangerous patterns.

        Scans script file for potentially dangerous shell commands and patterns.
        Returns a list of warning messages for any detected issues.

        Args:
            script_path: Path to script file to validate.

        Returns:
            List of warning messages. Empty list if no issues found.

        Raises:
            OSError: If script cannot be read.

        Example:
            >>> warnings = validator.validate_script_content(Path("hook.sh"))
            >>> if warnings:
            ...     for warning in warnings:
            ...         print(f"WARNING: {warning}")
        """
        warnings = []

        try:
            content = script_path.read_text(encoding="utf-8")
        except OSError as e:
            logger.error(f"Failed to read script {script_path}: {e}")
            raise

        # Check for dangerous patterns
        for pattern, description in self.DANGEROUS_PATTERNS:
            if re.search(pattern, content, re.MULTILINE):
                warnings.append(
                    f"Dangerous pattern detected in {script_path.name}: {description}"
                )
                logger.warning(
                    f"Security warning: {description} found in {script_path}"
                )

        return warnings

    def compute_script_hash(self, script_path: Path) -> str:
        """Compute SHA-256 hash for audit trail.

        Generates a cryptographic hash of the script content for integrity
        verification and audit logging. This enables detection of script
        modifications between executions.

        Args:
            script_path: Path to script file.

        Returns:
            Hexadecimal SHA-256 hash of script content.

        Raises:
            OSError: If script cannot be read.

        Example:
            >>> hash_value = validator.compute_script_hash(Path("hook.sh"))
            >>> print(f"Script hash: {hash_value}")
            Script hash: a3b5c7d9e1f2...
        """
        try:
            content = script_path.read_bytes()
            return hashlib.sha256(content).hexdigest()
        except OSError as e:
            logger.error(f"Failed to read script {script_path} for hashing: {e}")
            raise


class AuditLogger:
    """Enhanced audit logger with integrity verification.

    Provides tamper-resistant audit logging for hook executions.
    Each log entry includes a hash chain to detect modifications.

    Features:
    - JSONL format (one JSON object per line)
    - Integrity verification via hash chains
    - Tamper detection
    - Query and analysis of audit history

    Attributes:
        log_path: Path to audit log file.

    Example:
        >>> logger = AuditLogger(Path(".specify/hooks/audit.log"))
        >>> logger.log_execution({
        ...     "hook_name": "test",
        ...     "timestamp": "2025-12-02T12:34:56.789Z",
        ...     "success": True
        ... })
        >>> valid, errors = logger.verify_integrity()
        >>> assert valid, f"Audit log tampered: {errors}"
    """

    def __init__(self, log_path: Path):
        """Initialize audit logger.

        Args:
            log_path: Path to audit log file (will be created if needed).

        Example:
            >>> logger = AuditLogger(Path(".specify/hooks/audit.log"))
        """
        self.log_path = log_path
        # Ensure log directory exists
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_execution(self, entry: dict[str, Any]) -> None:
        """Log execution with integrity hash.

        Appends an audit entry with a hash chain for tamper detection.
        Each entry includes:
        - All fields from the entry dict
        - entry_hash: SHA-256 hash of (entry + previous_hash)

        Args:
            entry: Audit entry dictionary (must be JSON-serializable).

        Raises:
            OSError: If log file cannot be written.

        Example:
            >>> logger.log_execution({
            ...     "timestamp": "2025-12-02T12:34:56.789Z",
            ...     "hook_name": "run-tests",
            ...     "event_type": "implement.completed",
            ...     "success": True,
            ...     "exit_code": 0,
            ...     "duration_ms": 1234
            ... })
        """
        # Get previous hash for chain
        previous_hash = self._get_last_entry_hash()

        # Add entry hash (hash of entry + previous hash)
        entry_copy = entry.copy()
        entry_json = json.dumps(entry_copy, sort_keys=True)
        chain_input = f"{entry_json}{previous_hash}"
        entry_hash = hashlib.sha256(chain_input.encode("utf-8")).hexdigest()
        entry_copy["entry_hash"] = entry_hash

        # Append to log
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry_copy) + "\n")
        except OSError as e:
            logger.error(f"Failed to write audit log: {e}")
            raise

    def verify_integrity(self) -> tuple[bool, list[str]]:
        """Verify audit log hasn't been tampered with.

        Validates the hash chain in the audit log. Each entry's hash
        should match the hash of (entry + previous_hash).

        Returns:
            Tuple of (is_valid, error_messages).
            is_valid is True if log is intact, False if tampered.
            error_messages contains details of integrity violations.

        Example:
            >>> valid, errors = logger.verify_integrity()
            >>> if not valid:
            ...     print("Audit log tampered!")
            ...     for error in errors:
            ...         print(f"  - {error}")
        """
        if not self.log_path.exists():
            # Empty/missing log is valid
            return True, []

        errors = []
        previous_hash = ""

        try:
            with open(self.log_path, encoding="utf-8") as f:
                for line_num, line in enumerate(f, start=1):
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError as e:
                        errors.append(f"Line {line_num}: Invalid JSON: {e}")
                        continue

                    # Verify entry hash
                    if "entry_hash" not in entry:
                        errors.append(f"Line {line_num}: Missing entry_hash")
                        continue

                    stored_hash = entry["entry_hash"]
                    entry_copy = {k: v for k, v in entry.items() if k != "entry_hash"}
                    entry_json = json.dumps(entry_copy, sort_keys=True)
                    chain_input = f"{entry_json}{previous_hash}"
                    expected_hash = hashlib.sha256(
                        chain_input.encode("utf-8")
                    ).hexdigest()

                    if stored_hash != expected_hash:
                        errors.append(
                            f"Line {line_num}: Hash mismatch "
                            f"(expected {expected_hash[:8]}..., got {stored_hash[:8]}...)"
                        )

                    previous_hash = stored_hash

        except OSError as e:
            errors.append(f"Failed to read audit log: {e}")

        return len(errors) == 0, errors

    def get_recent_entries(self, count: int = 10) -> list[dict[str, Any]]:
        """Get recent audit entries for review.

        Retrieves the most recent N entries from the audit log.
        Useful for monitoring and debugging.

        Args:
            count: Number of recent entries to retrieve (default: 10).

        Returns:
            List of audit entry dictionaries, most recent first.

        Example:
            >>> entries = logger.get_recent_entries(count=5)
            >>> for entry in entries:
            ...     print(f"{entry['timestamp']}: {entry['hook_name']} -> {entry['success']}")
        """
        if not self.log_path.exists():
            return []

        entries = []

        try:
            with open(self.log_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        entries.append(entry)
                    except json.JSONDecodeError:
                        # Skip malformed lines
                        continue

            # Return most recent N entries (reverse order)
            return list(reversed(entries[-count:]))

        except OSError:
            return []

    def _get_last_entry_hash(self) -> str:
        """Get hash from last log entry for chain continuation.

        Returns:
            Hash from last entry, or empty string if no entries.
        """
        if not self.log_path.exists():
            return ""

        try:
            # Read last line (most recent entry)
            with open(self.log_path, "rb") as f:
                # Seek to end and read backwards to find last line
                f.seek(0, 2)  # End of file
                file_size = f.tell()
                if file_size == 0:
                    return ""

                # Read last 4KB to find last line
                chunk_size = min(4096, file_size)
                f.seek(-chunk_size, 2)
                chunk = f.read(chunk_size)

                # Find last newline-delimited JSON
                lines = chunk.decode("utf-8", errors="ignore").strip().split("\n")
                for line in reversed(lines):
                    line = line.strip()
                    if line:
                        try:
                            entry = json.loads(line)
                            return entry.get("entry_hash", "")
                        except json.JSONDecodeError:
                            continue

        except OSError:
            pass

        return ""
