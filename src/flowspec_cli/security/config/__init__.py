"""Security configuration module.

This module provides configuration management for security scanning,
supporting YAML-based configuration files with schema validation.

Example:
    >>> from flowspec_cli.security.config import load_config, SecurityConfig
    >>> config = load_config()  # Loads from default location
    >>> print(config.fail_on)
    FailOnSeverity.HIGH
"""

from flowspec_cli.security.config.models import (
    SecurityConfig,
    ScannerType,
    FailOnSeverity,
    ScannerConfig,
    SemgrepConfig,
    CodeQLConfig,
    BanditConfig,
    TriageConfig,
    ExclusionConfig,
    ReportingConfig,
)
from flowspec_cli.security.config.loader import (
    ConfigLoader,
    ConfigLoadError,
    load_config,
)
from flowspec_cli.security.config.schema import (
    ConfigSchema,
    SchemaError,
    SchemaErrorType,
)

__all__ = [
    # Models
    "SecurityConfig",
    "ScannerType",
    "FailOnSeverity",
    "ScannerConfig",
    "SemgrepConfig",
    "CodeQLConfig",
    "BanditConfig",
    "TriageConfig",
    "ExclusionConfig",
    "ReportingConfig",
    # Loader
    "ConfigLoader",
    "ConfigLoadError",
    "load_config",
    # Schema
    "ConfigSchema",
    "SchemaError",
    "SchemaErrorType",
]
