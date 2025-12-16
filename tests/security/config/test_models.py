"""Tests for security configuration models."""

from pathlib import Path

from flowspec_cli.security.config.models import (
    SecurityConfig,
    ScannerType,
    FailOnSeverity,
    SemgrepConfig,
    CodeQLConfig,
    BanditConfig,
    TriageConfig,
    ExclusionConfig,
    ReportingConfig,
)


class TestScannerType:
    """Tests for ScannerType enum."""

    def test_values(self):
        """Test scanner type values."""
        assert ScannerType.SEMGREP.value == "semgrep"
        assert ScannerType.CODEQL.value == "codeql"
        assert ScannerType.BANDIT.value == "bandit"


class TestFailOnSeverity:
    """Tests for FailOnSeverity enum."""

    def test_values(self):
        """Test fail_on severity values."""
        assert FailOnSeverity.CRITICAL.value == "critical"
        assert FailOnSeverity.HIGH.value == "high"
        assert FailOnSeverity.MEDIUM.value == "medium"
        assert FailOnSeverity.LOW.value == "low"
        assert FailOnSeverity.NONE.value == "none"


class TestSemgrepConfig:
    """Tests for SemgrepConfig."""

    def test_defaults(self):
        """Test default values."""
        config = SemgrepConfig()

        assert config.enabled is True
        assert config.custom_rules_dir is None
        assert config.registry_rulesets == ["p/default"]
        assert config.timeout == 300

    def test_custom_config(self):
        """Test custom configuration."""
        config = SemgrepConfig(
            enabled=False,
            custom_rules_dir=Path(".security/rules"),
            registry_rulesets=["p/security-audit", "p/python"],
            timeout=600,
        )

        assert config.enabled is False
        assert config.custom_rules_dir == Path(".security/rules")
        assert "p/security-audit" in config.registry_rulesets


class TestCodeQLConfig:
    """Tests for CodeQLConfig."""

    def test_defaults(self):
        """Test default values."""
        config = CodeQLConfig()

        assert config.enabled is True
        assert config.languages == []
        assert config.query_suites == ["security-extended"]

    def test_custom_config(self):
        """Test custom configuration."""
        config = CodeQLConfig(
            enabled=True,
            languages=["python", "javascript"],
            query_suites=["security-and-quality"],
        )

        assert "python" in config.languages
        assert "javascript" in config.languages


class TestBanditConfig:
    """Tests for BanditConfig."""

    def test_defaults(self):
        """Test default values."""
        config = BanditConfig()

        assert config.enabled is True
        assert config.skips == []
        assert config.confidence_level == "medium"

    def test_custom_config(self):
        """Test custom configuration."""
        config = BanditConfig(
            skips=["B101", "B102"],
            confidence_level="high",
        )

        assert "B101" in config.skips
        assert config.confidence_level == "high"


class TestTriageConfig:
    """Tests for TriageConfig."""

    def test_defaults(self):
        """Test default values."""
        config = TriageConfig()

        assert config.enabled is True
        assert config.confidence_threshold == 0.7
        assert config.auto_dismiss_fp is False
        assert config.cluster_similar is True

    def test_custom_config(self):
        """Test custom configuration."""
        config = TriageConfig(
            enabled=True,
            confidence_threshold=0.9,
            auto_dismiss_fp=True,
        )

        assert config.confidence_threshold == 0.9
        assert config.auto_dismiss_fp is True


class TestExclusionConfig:
    """Tests for ExclusionConfig."""

    def test_defaults(self):
        """Test default values."""
        config = ExclusionConfig()

        assert config.paths == []
        assert config.patterns == []
        assert config.file_extensions == []

    def test_matches_path_exact(self):
        """Test path matching with exact paths."""
        config = ExclusionConfig(paths=["node_modules/", ".venv/"])

        assert config.matches_path("node_modules/package/index.js") is True
        assert config.matches_path(".venv/lib/python3.11/site.py") is True
        assert config.matches_path("src/app.py") is False

    def test_matches_path_patterns(self):
        """Test path matching with glob patterns."""
        config = ExclusionConfig(patterns=["*_test.py", "*.min.js"])

        assert config.matches_path("test_app.py") is False  # Pattern is *_test.py
        assert config.matches_path("app_test.py") is True
        assert config.matches_path("bundle.min.js") is True
        assert config.matches_path("bundle.js") is False

    def test_matches_path_extensions(self):
        """Test path matching with file extensions."""
        config = ExclusionConfig(file_extensions=[".pyc", ".pyo"])

        assert config.matches_path("app.pyc") is True
        assert config.matches_path("app.pyo") is True
        assert config.matches_path("app.py") is False


class TestReportingConfig:
    """Tests for ReportingConfig."""

    def test_defaults(self):
        """Test default values."""
        config = ReportingConfig()

        assert config.format == "markdown"
        assert config.output_dir is None
        assert config.include_false_positives is False
        assert config.max_remediations == 10

    def test_custom_config(self):
        """Test custom configuration."""
        config = ReportingConfig(
            format="html",
            output_dir=Path("reports/"),
            include_false_positives=True,
            max_remediations=5,
        )

        assert config.format == "html"
        assert config.output_dir == Path("reports/")


class TestSecurityConfig:
    """Tests for SecurityConfig."""

    def test_defaults(self):
        """Test default configuration values."""
        config = SecurityConfig()

        assert config.semgrep.enabled is True
        assert config.codeql.enabled is True
        assert config.bandit.enabled is True
        assert config.fail_on == FailOnSeverity.HIGH
        assert config.parallel_scans is True
        assert config.max_findings == 1000

    def test_get_enabled_scanners(self):
        """Test getting list of enabled scanners."""
        config = SecurityConfig()

        enabled = config.get_enabled_scanners()

        assert ScannerType.SEMGREP in enabled
        assert ScannerType.CODEQL in enabled
        assert ScannerType.BANDIT in enabled

    def test_get_enabled_scanners_partial(self):
        """Test getting enabled scanners with some disabled."""
        config = SecurityConfig()
        config.codeql.enabled = False

        enabled = config.get_enabled_scanners()

        assert ScannerType.SEMGREP in enabled
        assert ScannerType.CODEQL not in enabled
        assert ScannerType.BANDIT in enabled

    def test_should_fail_critical(self):
        """Test should_fail with critical severity."""
        config = SecurityConfig(fail_on=FailOnSeverity.HIGH)

        assert config.should_fail("critical") is True
        assert config.should_fail("high") is True
        assert config.should_fail("medium") is False
        assert config.should_fail("low") is False

    def test_should_fail_medium(self):
        """Test should_fail with medium threshold."""
        config = SecurityConfig(fail_on=FailOnSeverity.MEDIUM)

        assert config.should_fail("critical") is True
        assert config.should_fail("high") is True
        assert config.should_fail("medium") is True
        assert config.should_fail("low") is False

    def test_should_fail_none(self):
        """Test should_fail with none (never fail)."""
        config = SecurityConfig(fail_on=FailOnSeverity.NONE)

        assert config.should_fail("critical") is False
        assert config.should_fail("high") is False
        assert config.should_fail("medium") is False
        assert config.should_fail("low") is False

    def test_to_dict(self):
        """Test serialization to dictionary."""
        config = SecurityConfig()

        data = config.to_dict()

        assert "scanners" in data
        assert "semgrep" in data["scanners"]
        assert data["scanners"]["semgrep"]["enabled"] is True
        assert data["fail_on"] == "high"
        assert data["parallel_scans"] is True
        assert "triage" in data
        assert "exclusions" in data
        assert "reporting" in data
