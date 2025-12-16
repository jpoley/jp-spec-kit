"""Tests for telemetry configuration system.

Tests cover:
- TelemetryConfig dataclass
- Config file load/save
- is_telemetry_enabled with env var and config file
- Consent management
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from flowspec_cli.telemetry.config import (
    ENV_TELEMETRY_DISABLED,
    TelemetryConfig,
    disable_telemetry,
    enable_telemetry,
    get_config_path,
    is_telemetry_enabled,
    load_telemetry_config,
    save_telemetry_config,
)


@pytest.fixture
def temp_project(tmp_path: Path) -> Path:
    """Create a temporary project directory."""
    project_root = tmp_path / "test-project"
    project_root.mkdir()
    return project_root


@pytest.fixture(autouse=True)
def clean_env():
    """Ensure environment variables are clean before each test."""
    old_val = os.environ.pop(ENV_TELEMETRY_DISABLED, None)
    yield
    if old_val is not None:
        os.environ[ENV_TELEMETRY_DISABLED] = old_val
    else:
        os.environ.pop(ENV_TELEMETRY_DISABLED, None)


class TestTelemetryConfig:
    """Tests for TelemetryConfig dataclass."""

    def test_default_values(self) -> None:
        """Default config should have telemetry disabled."""
        config = TelemetryConfig()
        assert config.enabled is False
        assert config.consent_given_at is None
        assert config.consent_version == "1.0"
        assert config.data_retention_days == 90
        assert config.metadata == {}

    def test_to_dict(self) -> None:
        """Config should serialize to dictionary."""
        config = TelemetryConfig(
            enabled=True,
            consent_given_at="2025-01-01T00:00:00Z",
            consent_version="1.0",
            data_retention_days=30,
            metadata={"source": "test"},
        )
        data = config.to_dict()
        assert data["enabled"] is True
        assert data["consent_given_at"] == "2025-01-01T00:00:00Z"
        assert data["consent_version"] == "1.0"
        assert data["data_retention_days"] == 30
        assert data["metadata"] == {"source": "test"}

    def test_from_dict(self) -> None:
        """Config should deserialize from dictionary."""
        data = {
            "enabled": True,
            "consent_given_at": "2025-01-01T00:00:00Z",
            "consent_version": "2.0",
            "data_retention_days": 60,
            "metadata": {"key": "value"},
        }
        config = TelemetryConfig.from_dict(data)
        assert config.enabled is True
        assert config.consent_given_at == "2025-01-01T00:00:00Z"
        assert config.consent_version == "2.0"
        assert config.data_retention_days == 60
        assert config.metadata == {"key": "value"}

    def test_from_dict_with_defaults(self) -> None:
        """Missing fields should use defaults."""
        config = TelemetryConfig.from_dict({})
        assert config.enabled is False
        assert config.consent_given_at is None

    def test_record_consent(self) -> None:
        """record_consent should enable telemetry and set timestamp."""
        config = TelemetryConfig()
        assert config.enabled is False
        assert config.consent_given_at is None

        config.record_consent()

        assert config.enabled is True
        assert config.consent_given_at is not None
        assert "T" in config.consent_given_at  # ISO format

    def test_revoke_consent(self) -> None:
        """revoke_consent should disable telemetry but keep timestamp."""
        config = TelemetryConfig(enabled=True, consent_given_at="2025-01-01T00:00:00Z")
        config.revoke_consent()

        assert config.enabled is False
        assert config.consent_given_at == "2025-01-01T00:00:00Z"  # Preserved


class TestConfigPersistence:
    """Tests for config file load/save."""

    def test_get_config_path(self, temp_project: Path) -> None:
        """Config path should be .flowspec/telemetry-config.json."""
        path = get_config_path(temp_project)
        assert path == temp_project / ".flowspec" / "telemetry-config.json"

    def test_save_and_load_config(self, temp_project: Path) -> None:
        """Config should round-trip through save/load."""
        config = TelemetryConfig(
            enabled=True,
            consent_given_at="2025-01-01T00:00:00Z",
            data_retention_days=45,
        )

        save_telemetry_config(config, temp_project)
        loaded = load_telemetry_config(temp_project)

        assert loaded.enabled is True
        assert loaded.consent_given_at == "2025-01-01T00:00:00Z"
        assert loaded.data_retention_days == 45

    def test_load_missing_file(self, temp_project: Path) -> None:
        """Loading missing file should return default config."""
        config = load_telemetry_config(temp_project)
        assert config.enabled is False

    def test_load_corrupted_file(self, temp_project: Path) -> None:
        """Loading corrupted file should return default config (fail-safe)."""
        config_path = get_config_path(temp_project)
        config_path.parent.mkdir(parents=True)
        config_path.write_text("not valid json {{{")

        config = load_telemetry_config(temp_project)
        assert config.enabled is False

    def test_save_creates_directory(self, temp_project: Path) -> None:
        """Save should create .flowspec directory if needed."""
        config = TelemetryConfig(enabled=True)
        save_telemetry_config(config, temp_project)

        config_path = get_config_path(temp_project)
        assert config_path.exists()
        assert config_path.parent.exists()


class TestIsTelemetryEnabled:
    """Tests for is_telemetry_enabled function."""

    def test_disabled_by_default(self, temp_project: Path) -> None:
        """Telemetry should be disabled by default (no config)."""
        assert is_telemetry_enabled(temp_project) is False

    def test_enabled_via_config(self, temp_project: Path) -> None:
        """Telemetry should be enabled if config says so."""
        config = TelemetryConfig(enabled=True)
        save_telemetry_config(config, temp_project)

        assert is_telemetry_enabled(temp_project) is True

    def test_disabled_via_config(self, temp_project: Path) -> None:
        """Telemetry should be disabled if config says so."""
        config = TelemetryConfig(enabled=False)
        save_telemetry_config(config, temp_project)

        assert is_telemetry_enabled(temp_project) is False

    def test_env_var_overrides_config(self, temp_project: Path) -> None:
        """FLOWSPEC_TELEMETRY_DISABLED env var should override config."""
        config = TelemetryConfig(enabled=True)
        save_telemetry_config(config, temp_project)

        os.environ[ENV_TELEMETRY_DISABLED] = "1"
        assert is_telemetry_enabled(temp_project) is False

    def test_env_var_values(self, temp_project: Path) -> None:
        """Various env var values should disable telemetry."""
        config = TelemetryConfig(enabled=True)
        save_telemetry_config(config, temp_project)

        for value in ["1", "true", "yes", "TRUE", "YES"]:
            os.environ[ENV_TELEMETRY_DISABLED] = value
            assert is_telemetry_enabled(temp_project) is False

    def test_fail_safe_on_error(self, temp_project: Path) -> None:
        """Should return False on any error (fail-safe)."""
        # Corrupted config file
        config_path = get_config_path(temp_project)
        config_path.parent.mkdir(parents=True)
        config_path.write_text("corrupted")

        assert is_telemetry_enabled(temp_project) is False


class TestConsentHelpers:
    """Tests for enable_telemetry and disable_telemetry helpers."""

    def test_enable_telemetry(self, temp_project: Path) -> None:
        """enable_telemetry should enable and save config."""
        assert is_telemetry_enabled(temp_project) is False

        result = enable_telemetry(temp_project)

        assert result is True
        assert is_telemetry_enabled(temp_project) is True

        # Check consent was recorded
        config = load_telemetry_config(temp_project)
        assert config.consent_given_at is not None

    def test_disable_telemetry(self, temp_project: Path) -> None:
        """disable_telemetry should disable and save config."""
        enable_telemetry(temp_project)
        assert is_telemetry_enabled(temp_project) is True

        result = disable_telemetry(temp_project)

        assert result is True
        assert is_telemetry_enabled(temp_project) is False

    def test_disable_preserves_consent_timestamp(self, temp_project: Path) -> None:
        """Disabling should preserve the original consent timestamp."""
        enable_telemetry(temp_project)
        config = load_telemetry_config(temp_project)
        original_timestamp = config.consent_given_at

        disable_telemetry(temp_project)
        config = load_telemetry_config(temp_project)

        assert config.consent_given_at == original_timestamp
