"""Security configuration models.

This module defines the data models for security configuration,
supporting scanner selection, severity thresholds, and AI settings.
"""

import fnmatch
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class ScannerType(Enum):
    """Supported security scanners."""

    SEMGREP = "semgrep"
    CODEQL = "codeql"
    BANDIT = "bandit"


class FailOnSeverity(Enum):
    """Severity threshold for failing scans."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"  # Never fail


@dataclass
class ScannerConfig:
    """Configuration for a specific scanner."""

    enabled: bool = True
    rulesets: list[str] = field(default_factory=list)
    extra_args: list[str] = field(default_factory=list)


@dataclass
class SemgrepConfig(ScannerConfig):
    """Semgrep-specific configuration."""

    custom_rules_dir: Path | None = None
    registry_rulesets: list[str] = field(default_factory=lambda: ["p/default"])
    timeout: int = 300  # seconds


@dataclass
class CodeQLConfig(ScannerConfig):
    """CodeQL-specific configuration."""

    languages: list[str] = field(default_factory=list)
    query_suites: list[str] = field(default_factory=lambda: ["security-extended"])
    database_path: Path | None = None


@dataclass
class BanditConfig(ScannerConfig):
    """Bandit-specific configuration."""

    skips: list[str] = field(default_factory=list)  # e.g., ["B101", "B102"]
    confidence_level: str = "medium"  # low, medium, high


@dataclass
class TriageConfig:
    """AI triage configuration."""

    enabled: bool = True
    confidence_threshold: float = 0.7  # 0.0-1.0
    auto_dismiss_fp: bool = False  # Auto-dismiss findings below threshold
    cluster_similar: bool = True  # Group similar findings


@dataclass
class ExclusionConfig:
    """Path and pattern exclusion configuration."""

    paths: list[str] = field(default_factory=list)
    patterns: list[str] = field(default_factory=list)
    file_extensions: list[str] = field(default_factory=list)

    def matches_path(self, path: Path | str) -> bool:
        """Check if path should be excluded.

        Args:
            path: Path to check.

        Returns:
            True if path matches any exclusion.
        """
        path_str = str(path)

        # Check exact paths
        for excl_path in self.paths:
            if path_str.startswith(excl_path) or excl_path in path_str:
                return True

        # Check patterns
        for pattern in self.patterns:
            if fnmatch.fnmatch(path_str, pattern):
                return True

        # Check file extensions
        if isinstance(path, str):
            path = Path(path)
        if path.suffix in self.file_extensions:
            return True

        return False


@dataclass
class ReportingConfig:
    """Report generation configuration."""

    format: str = "markdown"  # markdown, html, json, sarif
    output_dir: Path | None = None
    include_false_positives: bool = False
    max_remediations: int = 10


@dataclass
class SecurityConfig:
    """Complete security configuration.

    This is the top-level configuration object that contains
    all security scanning settings.

    Example config file (.flowspec/security-config.yml):
        scanners:
          semgrep:
            enabled: true
            custom_rules_dir: .security/rules
          codeql:
            enabled: false

        fail_on: high

        exclusions:
          paths:
            - node_modules/
            - .venv/
          patterns:
            - "*_test.py"

        triage:
          confidence_threshold: 0.8
          auto_dismiss_fp: true

        reporting:
          format: markdown
    """

    # Scanners
    semgrep: SemgrepConfig = field(default_factory=SemgrepConfig)
    codeql: CodeQLConfig = field(default_factory=CodeQLConfig)
    bandit: BanditConfig = field(default_factory=BanditConfig)

    # Thresholds
    fail_on: FailOnSeverity = FailOnSeverity.HIGH

    # Exclusions
    exclusions: ExclusionConfig = field(default_factory=ExclusionConfig)

    # AI Triage
    triage: TriageConfig = field(default_factory=TriageConfig)

    # Reporting
    reporting: ReportingConfig = field(default_factory=ReportingConfig)

    # General
    parallel_scans: bool = True
    max_findings: int = 1000  # Limit findings to prevent overwhelming output

    def get_enabled_scanners(self) -> list[ScannerType]:
        """Get list of enabled scanners.

        Returns:
            List of enabled ScannerType values.
        """
        enabled = []
        if self.semgrep.enabled:
            enabled.append(ScannerType.SEMGREP)
        if self.codeql.enabled:
            enabled.append(ScannerType.CODEQL)
        if self.bandit.enabled:
            enabled.append(ScannerType.BANDIT)
        return enabled

    def should_fail(self, severity: str) -> bool:
        """Check if scan should fail based on severity.

        Args:
            severity: Severity level to check.

        Returns:
            True if scan should fail for this severity.
        """
        if self.fail_on == FailOnSeverity.NONE:
            return False

        severity_order = {
            "critical": 0,
            "high": 1,
            "medium": 2,
            "low": 3,
            "info": 4,
        }

        threshold_order = {
            FailOnSeverity.CRITICAL: 0,
            FailOnSeverity.HIGH: 1,
            FailOnSeverity.MEDIUM: 2,
            FailOnSeverity.LOW: 3,
        }

        finding_level = severity_order.get(severity.lower(), 4)
        threshold_level = threshold_order.get(self.fail_on, 1)

        return finding_level <= threshold_level

    def to_dict(self) -> dict:
        """Serialize configuration to dictionary.

        Returns:
            Dictionary representation of config.
        """
        return {
            "scanners": {
                "semgrep": {
                    "enabled": self.semgrep.enabled,
                    "rulesets": self.semgrep.rulesets,
                    "custom_rules_dir": str(self.semgrep.custom_rules_dir)
                    if self.semgrep.custom_rules_dir
                    else None,
                    "registry_rulesets": self.semgrep.registry_rulesets,
                    "timeout": self.semgrep.timeout,
                },
                "codeql": {
                    "enabled": self.codeql.enabled,
                    "languages": self.codeql.languages,
                    "query_suites": self.codeql.query_suites,
                },
                "bandit": {
                    "enabled": self.bandit.enabled,
                    "skips": self.bandit.skips,
                    "confidence_level": self.bandit.confidence_level,
                },
            },
            "fail_on": self.fail_on.value,
            "exclusions": {
                "paths": self.exclusions.paths,
                "patterns": self.exclusions.patterns,
                "file_extensions": self.exclusions.file_extensions,
            },
            "triage": {
                "enabled": self.triage.enabled,
                "confidence_threshold": self.triage.confidence_threshold,
                "auto_dismiss_fp": self.triage.auto_dismiss_fp,
                "cluster_similar": self.triage.cluster_similar,
            },
            "reporting": {
                "format": self.reporting.format,
                "output_dir": str(self.reporting.output_dir)
                if self.reporting.output_dir
                else None,
                "include_false_positives": self.reporting.include_false_positives,
                "max_remediations": self.reporting.max_remediations,
            },
            "parallel_scans": self.parallel_scans,
            "max_findings": self.max_findings,
        }
