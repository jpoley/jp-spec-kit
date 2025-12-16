"""YAML schema validation for security configuration.

This module provides schema validation for security-config.yml files,
ensuring configuration files are well-formed and valid.
"""

from dataclasses import dataclass
from enum import Enum


class SchemaErrorType(Enum):
    """Types of schema validation errors."""

    INVALID_TYPE = "invalid_type"
    MISSING_FIELD = "missing_field"
    UNKNOWN_FIELD = "unknown_field"
    INVALID_VALUE = "invalid_value"
    INVALID_RANGE = "invalid_range"


@dataclass
class SchemaError:
    """Schema validation error."""

    path: str  # e.g., "scanners.semgrep.enabled"
    error_type: SchemaErrorType
    message: str
    expected: str | None = None
    actual: str | None = None


class ConfigSchema:
    """Schema definition for security configuration.

    Validates YAML configuration against expected structure.
    """

    VALID_SCANNERS = {"semgrep", "codeql", "bandit"}
    VALID_FAIL_ON = {"critical", "high", "medium", "low", "none"}
    VALID_FORMATS = {"markdown", "html", "json", "sarif"}
    VALID_CONFIDENCE_LEVELS = {"low", "medium", "high"}

    def validate(self, config_data: dict) -> list[SchemaError]:
        """Validate configuration data against schema.

        Args:
            config_data: Parsed YAML configuration.

        Returns:
            List of validation errors (empty if valid).
        """
        errors: list[SchemaError] = []

        if not isinstance(config_data, dict):
            errors.append(
                SchemaError(
                    path="",
                    error_type=SchemaErrorType.INVALID_TYPE,
                    message="Configuration must be a dictionary",
                    expected="dict",
                    actual=type(config_data).__name__,
                )
            )
            return errors

        # Validate scanners section
        if "scanners" in config_data:
            errors.extend(self._validate_scanners(config_data["scanners"]))

        # Validate fail_on
        if "fail_on" in config_data:
            errors.extend(self._validate_fail_on(config_data["fail_on"]))

        # Validate exclusions
        if "exclusions" in config_data:
            errors.extend(self._validate_exclusions(config_data["exclusions"]))

        # Validate triage
        if "triage" in config_data:
            errors.extend(self._validate_triage(config_data["triage"]))

        # Validate reporting
        if "reporting" in config_data:
            errors.extend(self._validate_reporting(config_data["reporting"]))

        # Validate top-level fields
        errors.extend(self._validate_top_level(config_data))

        return errors

    def _validate_scanners(self, scanners: dict) -> list[SchemaError]:
        """Validate scanners section."""
        errors: list[SchemaError] = []

        if not isinstance(scanners, dict):
            errors.append(
                SchemaError(
                    path="scanners",
                    error_type=SchemaErrorType.INVALID_TYPE,
                    message="Scanners must be a dictionary",
                    expected="dict",
                    actual=type(scanners).__name__,
                )
            )
            return errors

        for scanner_name, scanner_config in scanners.items():
            if scanner_name not in self.VALID_SCANNERS:
                errors.append(
                    SchemaError(
                        path=f"scanners.{scanner_name}",
                        error_type=SchemaErrorType.UNKNOWN_FIELD,
                        message=f"Unknown scanner: {scanner_name}",
                        expected=f"one of {self.VALID_SCANNERS}",
                        actual=scanner_name,
                    )
                )
                continue

            if not isinstance(scanner_config, dict):
                errors.append(
                    SchemaError(
                        path=f"scanners.{scanner_name}",
                        error_type=SchemaErrorType.INVALID_TYPE,
                        message="Scanner config must be a dictionary",
                        expected="dict",
                        actual=type(scanner_config).__name__,
                    )
                )
                continue

            # Validate enabled field
            if "enabled" in scanner_config:
                if not isinstance(scanner_config["enabled"], bool):
                    errors.append(
                        SchemaError(
                            path=f"scanners.{scanner_name}.enabled",
                            error_type=SchemaErrorType.INVALID_TYPE,
                            message="enabled must be a boolean",
                            expected="bool",
                            actual=type(scanner_config["enabled"]).__name__,
                        )
                    )

            # Validate scanner-specific fields
            if scanner_name == "semgrep":
                errors.extend(
                    self._validate_semgrep(scanner_config, f"scanners.{scanner_name}")
                )
            elif scanner_name == "codeql":
                errors.extend(
                    self._validate_codeql(scanner_config, f"scanners.{scanner_name}")
                )
            elif scanner_name == "bandit":
                errors.extend(
                    self._validate_bandit(scanner_config, f"scanners.{scanner_name}")
                )

        return errors

    def _validate_semgrep(self, config: dict, path: str) -> list[SchemaError]:
        """Validate Semgrep-specific configuration."""
        errors: list[SchemaError] = []

        if "timeout" in config:
            if not isinstance(config["timeout"], int) or config["timeout"] < 0:
                errors.append(
                    SchemaError(
                        path=f"{path}.timeout",
                        error_type=SchemaErrorType.INVALID_VALUE,
                        message="timeout must be a non-negative integer",
                    )
                )

        if "registry_rulesets" in config:
            if not isinstance(config["registry_rulesets"], list):
                errors.append(
                    SchemaError(
                        path=f"{path}.registry_rulesets",
                        error_type=SchemaErrorType.INVALID_TYPE,
                        message="registry_rulesets must be a list",
                        expected="list",
                        actual=type(config["registry_rulesets"]).__name__,
                    )
                )

        return errors

    def _validate_codeql(self, config: dict, path: str) -> list[SchemaError]:
        """Validate CodeQL-specific configuration."""
        errors: list[SchemaError] = []

        if "languages" in config:
            if not isinstance(config["languages"], list):
                errors.append(
                    SchemaError(
                        path=f"{path}.languages",
                        error_type=SchemaErrorType.INVALID_TYPE,
                        message="languages must be a list",
                        expected="list",
                        actual=type(config["languages"]).__name__,
                    )
                )

        if "query_suites" in config:
            if not isinstance(config["query_suites"], list):
                errors.append(
                    SchemaError(
                        path=f"{path}.query_suites",
                        error_type=SchemaErrorType.INVALID_TYPE,
                        message="query_suites must be a list",
                        expected="list",
                        actual=type(config["query_suites"]).__name__,
                    )
                )

        return errors

    def _validate_bandit(self, config: dict, path: str) -> list[SchemaError]:
        """Validate Bandit-specific configuration."""
        errors: list[SchemaError] = []

        if "confidence_level" in config:
            if config["confidence_level"] not in self.VALID_CONFIDENCE_LEVELS:
                errors.append(
                    SchemaError(
                        path=f"{path}.confidence_level",
                        error_type=SchemaErrorType.INVALID_VALUE,
                        message=f"Invalid confidence level: {config['confidence_level']}",
                        expected=f"one of {self.VALID_CONFIDENCE_LEVELS}",
                        actual=config["confidence_level"],
                    )
                )

        if "skips" in config:
            if not isinstance(config["skips"], list):
                errors.append(
                    SchemaError(
                        path=f"{path}.skips",
                        error_type=SchemaErrorType.INVALID_TYPE,
                        message="skips must be a list",
                        expected="list",
                        actual=type(config["skips"]).__name__,
                    )
                )

        return errors

    def _validate_fail_on(self, fail_on: str) -> list[SchemaError]:
        """Validate fail_on field."""
        errors: list[SchemaError] = []

        if not isinstance(fail_on, str):
            errors.append(
                SchemaError(
                    path="fail_on",
                    error_type=SchemaErrorType.INVALID_TYPE,
                    message="fail_on must be a string",
                    expected="str",
                    actual=type(fail_on).__name__,
                )
            )
        elif fail_on.lower() not in self.VALID_FAIL_ON:
            errors.append(
                SchemaError(
                    path="fail_on",
                    error_type=SchemaErrorType.INVALID_VALUE,
                    message=f"Invalid fail_on value: {fail_on}",
                    expected=f"one of {self.VALID_FAIL_ON}",
                    actual=fail_on,
                )
            )

        return errors

    def _validate_exclusions(self, exclusions: dict) -> list[SchemaError]:
        """Validate exclusions section."""
        errors: list[SchemaError] = []

        if not isinstance(exclusions, dict):
            errors.append(
                SchemaError(
                    path="exclusions",
                    error_type=SchemaErrorType.INVALID_TYPE,
                    message="exclusions must be a dictionary",
                    expected="dict",
                    actual=type(exclusions).__name__,
                )
            )
            return errors

        for field in ["paths", "patterns", "file_extensions"]:
            if field in exclusions:
                if not isinstance(exclusions[field], list):
                    errors.append(
                        SchemaError(
                            path=f"exclusions.{field}",
                            error_type=SchemaErrorType.INVALID_TYPE,
                            message=f"{field} must be a list",
                            expected="list",
                            actual=type(exclusions[field]).__name__,
                        )
                    )

        return errors

    def _validate_triage(self, triage: dict) -> list[SchemaError]:
        """Validate triage section."""
        errors: list[SchemaError] = []

        if not isinstance(triage, dict):
            errors.append(
                SchemaError(
                    path="triage",
                    error_type=SchemaErrorType.INVALID_TYPE,
                    message="triage must be a dictionary",
                    expected="dict",
                    actual=type(triage).__name__,
                )
            )
            return errors

        if "enabled" in triage and not isinstance(triage["enabled"], bool):
            errors.append(
                SchemaError(
                    path="triage.enabled",
                    error_type=SchemaErrorType.INVALID_TYPE,
                    message="enabled must be a boolean",
                    expected="bool",
                    actual=type(triage["enabled"]).__name__,
                )
            )

        if "confidence_threshold" in triage:
            threshold = triage["confidence_threshold"]
            if not isinstance(threshold, (int, float)):
                errors.append(
                    SchemaError(
                        path="triage.confidence_threshold",
                        error_type=SchemaErrorType.INVALID_TYPE,
                        message="confidence_threshold must be a number",
                        expected="float",
                        actual=type(threshold).__name__,
                    )
                )
            elif not 0.0 <= threshold <= 1.0:
                errors.append(
                    SchemaError(
                        path="triage.confidence_threshold",
                        error_type=SchemaErrorType.INVALID_RANGE,
                        message="confidence_threshold must be between 0.0 and 1.0",
                        expected="0.0-1.0",
                        actual=str(threshold),
                    )
                )

        for bool_field in ["auto_dismiss_fp", "cluster_similar"]:
            if bool_field in triage and not isinstance(triage[bool_field], bool):
                errors.append(
                    SchemaError(
                        path=f"triage.{bool_field}",
                        error_type=SchemaErrorType.INVALID_TYPE,
                        message=f"{bool_field} must be a boolean",
                        expected="bool",
                        actual=type(triage[bool_field]).__name__,
                    )
                )

        return errors

    def _validate_reporting(self, reporting: dict) -> list[SchemaError]:
        """Validate reporting section."""
        errors: list[SchemaError] = []

        if not isinstance(reporting, dict):
            errors.append(
                SchemaError(
                    path="reporting",
                    error_type=SchemaErrorType.INVALID_TYPE,
                    message="reporting must be a dictionary",
                    expected="dict",
                    actual=type(reporting).__name__,
                )
            )
            return errors

        if "format" in reporting:
            if reporting["format"] not in self.VALID_FORMATS:
                errors.append(
                    SchemaError(
                        path="reporting.format",
                        error_type=SchemaErrorType.INVALID_VALUE,
                        message=f"Invalid format: {reporting['format']}",
                        expected=f"one of {self.VALID_FORMATS}",
                        actual=reporting["format"],
                    )
                )

        if "max_remediations" in reporting:
            max_rem = reporting["max_remediations"]
            if not isinstance(max_rem, int) or max_rem < 0:
                errors.append(
                    SchemaError(
                        path="reporting.max_remediations",
                        error_type=SchemaErrorType.INVALID_VALUE,
                        message="max_remediations must be a non-negative integer",
                    )
                )

        return errors

    def _validate_top_level(self, config: dict) -> list[SchemaError]:
        """Validate top-level fields."""
        errors: list[SchemaError] = []

        if "parallel_scans" in config:
            if not isinstance(config["parallel_scans"], bool):
                errors.append(
                    SchemaError(
                        path="parallel_scans",
                        error_type=SchemaErrorType.INVALID_TYPE,
                        message="parallel_scans must be a boolean",
                        expected="bool",
                        actual=type(config["parallel_scans"]).__name__,
                    )
                )

        if "max_findings" in config:
            max_findings = config["max_findings"]
            if not isinstance(max_findings, int) or max_findings < 0:
                errors.append(
                    SchemaError(
                        path="max_findings",
                        error_type=SchemaErrorType.INVALID_VALUE,
                        message="max_findings must be a non-negative integer",
                    )
                )

        return errors
