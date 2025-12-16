"""Security configuration loader.

This module handles loading and parsing security-config.yml files,
creating SecurityConfig instances from YAML configuration.
"""

from pathlib import Path

import yaml

from flowspec_cli.security.config.models import (
    SecurityConfig,
    SemgrepConfig,
    CodeQLConfig,
    BanditConfig,
    TriageConfig,
    ExclusionConfig,
    ReportingConfig,
    FailOnSeverity,
)
from flowspec_cli.security.config.schema import ConfigSchema, SchemaError


class ConfigLoadError(Exception):
    """Error loading security configuration."""

    def __init__(self, message: str, errors: list[SchemaError] | None = None):
        super().__init__(message)
        self.errors = errors or []


class ConfigLoader:
    """Load security configuration from YAML files.

    Example:
        >>> loader = ConfigLoader()
        >>> config = loader.load(Path(".flowspec/security-config.yml"))
        >>> print(config.fail_on)
    """

    DEFAULT_CONFIG_PATHS = [
        ".flowspec/security-config.yml",
        ".flowspec/security-config.yaml",
        ".security/config.yml",
        ".security/config.yaml",
        "security-config.yml",
    ]

    def __init__(self, validate: bool = True):
        """Initialize config loader.

        Args:
            validate: Whether to validate config against schema.
        """
        self.validate = validate
        self.schema = ConfigSchema()

    def load(self, config_path: Path | None = None) -> SecurityConfig:
        """Load configuration from file.

        Args:
            config_path: Path to config file. If None, searches default locations.

        Returns:
            SecurityConfig instance.

        Raises:
            ConfigLoadError: If config file not found or invalid.
        """
        if config_path is None:
            config_path = self._find_config_file()

        if config_path is None:
            # Return default config if no file found
            return SecurityConfig()

        if not config_path.exists():
            raise ConfigLoadError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path) as f:
                config_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigLoadError(f"Invalid YAML in {config_path}: {e}") from e

        if config_data is None:
            # Empty file - return defaults
            return SecurityConfig()

        if self.validate:
            errors = self.schema.validate(config_data)
            if errors:
                error_messages = [f"  - {e.path}: {e.message}" for e in errors]
                raise ConfigLoadError(
                    "Configuration validation failed:\n" + "\n".join(error_messages),
                    errors=errors,
                )

        return self._parse_config(config_data)

    def load_from_string(self, yaml_content: str) -> SecurityConfig:
        """Load configuration from YAML string.

        Args:
            yaml_content: YAML content as string.

        Returns:
            SecurityConfig instance.
        """
        try:
            config_data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise ConfigLoadError(f"Invalid YAML: {e}") from e

        if config_data is None:
            return SecurityConfig()

        if self.validate:
            errors = self.schema.validate(config_data)
            if errors:
                error_messages = [f"  - {e.path}: {e.message}" for e in errors]
                raise ConfigLoadError(
                    "Configuration validation failed:\n" + "\n".join(error_messages),
                    errors=errors,
                )

        return self._parse_config(config_data)

    def _find_config_file(self) -> Path | None:
        """Find configuration file in default locations.

        Returns:
            Path to config file, or None if not found.
        """
        for path_str in self.DEFAULT_CONFIG_PATHS:
            path = Path(path_str)
            if path.exists():
                return path
        return None

    def _parse_config(self, data: dict) -> SecurityConfig:
        """Parse configuration dictionary into SecurityConfig.

        Args:
            data: Parsed YAML data.

        Returns:
            SecurityConfig instance.
        """
        config = SecurityConfig()

        # Parse scanners
        if "scanners" in data:
            scanners = data["scanners"]

            if "semgrep" in scanners:
                config.semgrep = self._parse_semgrep(scanners["semgrep"])

            if "codeql" in scanners:
                config.codeql = self._parse_codeql(scanners["codeql"])

            if "bandit" in scanners:
                config.bandit = self._parse_bandit(scanners["bandit"])

        # Parse fail_on
        if "fail_on" in data:
            config.fail_on = FailOnSeverity(data["fail_on"].lower())

        # Parse exclusions
        if "exclusions" in data:
            config.exclusions = self._parse_exclusions(data["exclusions"])

        # Parse triage
        if "triage" in data:
            config.triage = self._parse_triage(data["triage"])

        # Parse reporting
        if "reporting" in data:
            config.reporting = self._parse_reporting(data["reporting"])

        # Parse top-level options
        if "parallel_scans" in data:
            config.parallel_scans = data["parallel_scans"]

        if "max_findings" in data:
            config.max_findings = data["max_findings"]

        return config

    def _parse_semgrep(self, data: dict) -> SemgrepConfig:
        """Parse Semgrep configuration."""
        config = SemgrepConfig()

        if "enabled" in data:
            config.enabled = data["enabled"]

        if "rulesets" in data:
            config.rulesets = data["rulesets"]

        if "extra_args" in data:
            config.extra_args = data["extra_args"]

        if "custom_rules_dir" in data and data["custom_rules_dir"]:
            config.custom_rules_dir = Path(data["custom_rules_dir"])

        if "registry_rulesets" in data:
            config.registry_rulesets = data["registry_rulesets"]

        if "timeout" in data:
            config.timeout = data["timeout"]

        return config

    def _parse_codeql(self, data: dict) -> CodeQLConfig:
        """Parse CodeQL configuration."""
        config = CodeQLConfig()

        if "enabled" in data:
            config.enabled = data["enabled"]

        if "rulesets" in data:
            config.rulesets = data["rulesets"]

        if "extra_args" in data:
            config.extra_args = data["extra_args"]

        if "languages" in data:
            config.languages = data["languages"]

        if "query_suites" in data:
            config.query_suites = data["query_suites"]

        if "database_path" in data and data["database_path"]:
            config.database_path = Path(data["database_path"])

        return config

    def _parse_bandit(self, data: dict) -> BanditConfig:
        """Parse Bandit configuration."""
        config = BanditConfig()

        if "enabled" in data:
            config.enabled = data["enabled"]

        if "rulesets" in data:
            config.rulesets = data["rulesets"]

        if "extra_args" in data:
            config.extra_args = data["extra_args"]

        if "skips" in data:
            config.skips = data["skips"]

        if "confidence_level" in data:
            config.confidence_level = data["confidence_level"]

        return config

    def _parse_exclusions(self, data: dict) -> ExclusionConfig:
        """Parse exclusions configuration."""
        config = ExclusionConfig()

        if "paths" in data:
            config.paths = data["paths"]

        if "patterns" in data:
            config.patterns = data["patterns"]

        if "file_extensions" in data:
            config.file_extensions = data["file_extensions"]

        return config

    def _parse_triage(self, data: dict) -> TriageConfig:
        """Parse triage configuration."""
        config = TriageConfig()

        if "enabled" in data:
            config.enabled = data["enabled"]

        if "confidence_threshold" in data:
            config.confidence_threshold = float(data["confidence_threshold"])

        if "auto_dismiss_fp" in data:
            config.auto_dismiss_fp = data["auto_dismiss_fp"]

        if "cluster_similar" in data:
            config.cluster_similar = data["cluster_similar"]

        return config

    def _parse_reporting(self, data: dict) -> ReportingConfig:
        """Parse reporting configuration."""
        config = ReportingConfig()

        if "format" in data:
            config.format = data["format"]

        if "output_dir" in data and data["output_dir"]:
            config.output_dir = Path(data["output_dir"])

        if "include_false_positives" in data:
            config.include_false_positives = data["include_false_positives"]

        if "max_remediations" in data:
            config.max_remediations = data["max_remediations"]

        return config


def load_config(
    config_path: Path | None = None, validate: bool = True
) -> SecurityConfig:
    """Convenience function to load security configuration.

    Args:
        config_path: Path to config file. If None, searches default locations.
        validate: Whether to validate config against schema.

    Returns:
        SecurityConfig instance.
    """
    loader = ConfigLoader(validate=validate)
    return loader.load(config_path)
