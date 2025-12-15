"""Telemetry configuration system with opt-in consent.

This module provides configuration management for telemetry:
- TelemetryConfig dataclass for settings
- Persistent storage in .flowspec/telemetry-config.json
- Environment variable override (FLOWSPEC_TELEMETRY_DISABLED)
- Fail-safe defaults (telemetry disabled if config unreadable)

The configuration hierarchy (highest priority first):
1. FLOWSPEC_TELEMETRY_DISABLED=1 environment variable (overrides all)
2. .flowspec/telemetry-config.json file
3. Default (disabled until user opts in)
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Configuration file location
CONFIG_DIR = ".flowspec"
CONFIG_FILE = "telemetry-config.json"

# Environment variable for override
ENV_TELEMETRY_DISABLED = "FLOWSPEC_TELEMETRY_DISABLED"
ENV_TELEMETRY_DEBUG = "FLOWSPEC_TELEMETRY_DEBUG"


@dataclass
class TelemetryConfig:
    """Telemetry configuration settings.

    Attributes:
        enabled: Whether telemetry is enabled (opt-in, defaults to False)
        consent_given_at: ISO timestamp when consent was given
        consent_version: Version of privacy notice user consented to
        data_retention_days: How long to keep telemetry data (default 90)
    """

    enabled: bool = False
    consent_given_at: str | None = None
    consent_version: str = "1.0"
    data_retention_days: int = 90
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary for JSON serialization."""
        return {
            "enabled": self.enabled,
            "consent_given_at": self.consent_given_at,
            "consent_version": self.consent_version,
            "data_retention_days": self.data_retention_days,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TelemetryConfig:
        """Create config from dictionary."""
        return cls(
            enabled=data.get("enabled", False),
            consent_given_at=data.get("consent_given_at"),
            consent_version=data.get("consent_version", "1.0"),
            data_retention_days=data.get("data_retention_days", 90),
            metadata=data.get("metadata", {}),
        )

    def record_consent(self) -> None:
        """Record that user gave consent at current time."""
        self.enabled = True
        self.consent_given_at = datetime.now(timezone.utc).isoformat()

    def revoke_consent(self) -> None:
        """Record that user revoked consent."""
        self.enabled = False
        # Keep consent_given_at for audit trail


def get_config_path(project_root: Path | None = None) -> Path:
    """Get the path to the telemetry config file.

    Args:
        project_root: Project root directory. Defaults to cwd.

    Returns:
        Path to telemetry-config.json
    """
    root = project_root or Path.cwd()
    return root / CONFIG_DIR / CONFIG_FILE


def load_telemetry_config(project_root: Path | None = None) -> TelemetryConfig:
    """Load telemetry configuration from file.

    Args:
        project_root: Project root directory. Defaults to cwd.

    Returns:
        TelemetryConfig instance. Returns default (disabled) config
        if file doesn't exist or is unreadable.
    """
    config_path = get_config_path(project_root)

    if not config_path.exists():
        return TelemetryConfig()

    try:
        with config_path.open("r") as f:
            data = json.load(f)
        return TelemetryConfig.from_dict(data)
    except (json.JSONDecodeError, OSError, KeyError) as e:
        # Fail-safe: return disabled config on any error
        if os.environ.get(ENV_TELEMETRY_DEBUG):
            logger.warning(f"Failed to load telemetry config: {e}")
        return TelemetryConfig()


def save_telemetry_config(
    config: TelemetryConfig,
    project_root: Path | None = None,
) -> bool:
    """Save telemetry configuration to file.

    Args:
        config: Configuration to save
        project_root: Project root directory. Defaults to cwd.

    Returns:
        True if saved successfully, False otherwise.
    """
    config_path = get_config_path(project_root)

    try:
        # Create directory if needed
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Write config
        with config_path.open("w") as f:
            json.dump(config.to_dict(), f, indent=2)
            f.write("\n")

        return True
    except OSError as e:
        if os.environ.get(ENV_TELEMETRY_DEBUG):
            logger.warning(f"Failed to save telemetry config: {e}")
        return False


def is_telemetry_enabled(project_root: Path | None = None) -> bool:
    """Check if telemetry is enabled.

    This is the primary function for checking telemetry status.
    It checks (in order):
    1. Environment variable FLOWSPEC_TELEMETRY_DISABLED
    2. Config file .flowspec/telemetry-config.json
    3. Default (False - disabled until user opts in)

    Args:
        project_root: Project root directory. Defaults to cwd.

    Returns:
        True if telemetry is enabled, False otherwise.
        Fails safe (returns False) on any error.
    """
    # Check environment variable override first
    env_disabled = os.environ.get(ENV_TELEMETRY_DISABLED, "").lower()
    if env_disabled in ("1", "true", "yes"):
        return False

    # Check config file
    try:
        config = load_telemetry_config(project_root)
        return config.enabled
    except Exception:
        # Fail-safe: return False on any error
        return False


def enable_telemetry(project_root: Path | None = None) -> bool:
    """Enable telemetry and record consent.

    Args:
        project_root: Project root directory. Defaults to cwd.

    Returns:
        True if enabled successfully, False otherwise.
    """
    config = load_telemetry_config(project_root)
    config.record_consent()
    return save_telemetry_config(config, project_root)


def disable_telemetry(project_root: Path | None = None) -> bool:
    """Disable telemetry and revoke consent.

    Args:
        project_root: Project root directory. Defaults to cwd.

    Returns:
        True if disabled successfully, False otherwise.
    """
    config = load_telemetry_config(project_root)
    config.revoke_consent()
    return save_telemetry_config(config, project_root)


__all__ = [
    "TelemetryConfig",
    "get_config_path",
    "load_telemetry_config",
    "save_telemetry_config",
    "is_telemetry_enabled",
    "enable_telemetry",
    "disable_telemetry",
    "ENV_TELEMETRY_DISABLED",
    "ENV_TELEMETRY_DEBUG",
]
