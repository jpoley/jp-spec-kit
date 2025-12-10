"""Tests for security configuration loader."""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from specify_cli.security.config.loader import (
    ConfigLoader,
    ConfigLoadError,
    load_config,
)
from specify_cli.security.config.models import (
    SecurityConfig,
    FailOnSeverity,
    ScannerType,
)


class TestConfigLoader:
    """Tests for ConfigLoader."""

    @pytest.fixture
    def loader(self):
        """Create a config loader."""
        return ConfigLoader()

    def test_load_default_when_no_file(self, loader):
        """Test loading returns default config when no file found."""
        with TemporaryDirectory() as tmpdir:
            import os

            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                config = loader.load()
                assert isinstance(config, SecurityConfig)
                assert config.fail_on == FailOnSeverity.HIGH
            finally:
                os.chdir(old_cwd)

    def test_load_from_file(self, loader):
        """Test loading configuration from file."""
        with TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "security-config.yml"
            config_path.write_text("""
scanners:
  semgrep:
    enabled: true
    timeout: 600
  codeql:
    enabled: false

fail_on: medium

exclusions:
  paths:
    - node_modules/
    - .venv/

triage:
  confidence_threshold: 0.9
""")

            config = loader.load(config_path)

            assert config.semgrep.enabled is True
            assert config.semgrep.timeout == 600
            assert config.codeql.enabled is False
            assert config.fail_on == FailOnSeverity.MEDIUM
            assert "node_modules/" in config.exclusions.paths
            assert config.triage.confidence_threshold == 0.9

    def test_load_nonexistent_file(self, loader):
        """Test loading non-existent file raises error."""
        with pytest.raises(ConfigLoadError, match="not found"):
            loader.load(Path("/nonexistent/path/config.yml"))

    def test_load_invalid_yaml(self, loader):
        """Test loading invalid YAML raises error."""
        with TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "security-config.yml"
            config_path.write_text("invalid: yaml: content: [")

            with pytest.raises(ConfigLoadError, match="Invalid YAML"):
                loader.load(config_path)

    def test_load_empty_file(self, loader):
        """Test loading empty file returns defaults."""
        with TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "security-config.yml"
            config_path.write_text("")

            config = loader.load(config_path)

            assert isinstance(config, SecurityConfig)
            assert config.fail_on == FailOnSeverity.HIGH

    def test_load_with_validation_error(self, loader):
        """Test loading with validation errors."""
        with TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "security-config.yml"
            config_path.write_text("""
fail_on: invalid_severity
""")

            with pytest.raises(ConfigLoadError, match="validation failed"):
                loader.load(config_path)

    def test_load_without_validation(self):
        """Test loading without validation."""
        loader = ConfigLoader(validate=False)

        with TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "security-config.yml"
            config_path.write_text("""
fail_on: high
""")

            config = loader.load(config_path)
            assert config.fail_on == FailOnSeverity.HIGH


class TestLoadFromString:
    """Tests for loading configuration from string."""

    @pytest.fixture
    def loader(self):
        return ConfigLoader()

    def test_load_valid_string(self, loader):
        """Test loading valid YAML string."""
        yaml_content = """
scanners:
  semgrep:
    enabled: true
fail_on: critical
"""
        config = loader.load_from_string(yaml_content)

        assert config.semgrep.enabled is True
        assert config.fail_on == FailOnSeverity.CRITICAL

    def test_load_empty_string(self, loader):
        """Test loading empty string returns defaults."""
        config = loader.load_from_string("")
        assert isinstance(config, SecurityConfig)

    def test_load_invalid_string(self, loader):
        """Test loading invalid YAML string raises error."""
        with pytest.raises(ConfigLoadError, match="Invalid YAML"):
            loader.load_from_string("invalid: yaml: [")


class TestScannerParsing:
    """Tests for scanner configuration parsing."""

    @pytest.fixture
    def loader(self):
        return ConfigLoader()

    def test_parse_semgrep_config(self, loader):
        """Test parsing Semgrep configuration."""
        config = loader.load_from_string("""
scanners:
  semgrep:
    enabled: true
    custom_rules_dir: .security/rules
    registry_rulesets:
      - p/security-audit
      - p/python
    timeout: 600
    extra_args:
      - --verbose
""")

        assert config.semgrep.enabled is True
        assert config.semgrep.custom_rules_dir == Path(".security/rules")
        assert "p/security-audit" in config.semgrep.registry_rulesets
        assert config.semgrep.timeout == 600
        assert "--verbose" in config.semgrep.extra_args

    def test_parse_codeql_config(self, loader):
        """Test parsing CodeQL configuration."""
        config = loader.load_from_string("""
scanners:
  codeql:
    enabled: true
    languages:
      - python
      - javascript
    query_suites:
      - security-and-quality
    database_path: .codeql/db
""")

        assert config.codeql.enabled is True
        assert "python" in config.codeql.languages
        assert "javascript" in config.codeql.languages
        assert config.codeql.database_path == Path(".codeql/db")

    def test_parse_bandit_config(self, loader):
        """Test parsing Bandit configuration."""
        config = loader.load_from_string("""
scanners:
  bandit:
    enabled: true
    skips:
      - B101
      - B102
    confidence_level: high
""")

        assert config.bandit.enabled is True
        assert "B101" in config.bandit.skips
        assert config.bandit.confidence_level == "high"


class TestExclusionParsing:
    """Tests for exclusion configuration parsing."""

    @pytest.fixture
    def loader(self):
        return ConfigLoader()

    def test_parse_exclusions(self, loader):
        """Test parsing exclusions configuration."""
        config = loader.load_from_string("""
exclusions:
  paths:
    - node_modules/
    - .venv/
    - vendor/
  patterns:
    - "*_test.py"
    - "*.min.js"
  file_extensions:
    - .pyc
    - .pyo
""")

        assert "node_modules/" in config.exclusions.paths
        assert ".venv/" in config.exclusions.paths
        assert "*_test.py" in config.exclusions.patterns
        assert ".pyc" in config.exclusions.file_extensions


class TestTriageParsing:
    """Tests for triage configuration parsing."""

    @pytest.fixture
    def loader(self):
        return ConfigLoader()

    def test_parse_triage(self, loader):
        """Test parsing triage configuration."""
        config = loader.load_from_string("""
triage:
  enabled: true
  confidence_threshold: 0.85
  auto_dismiss_fp: true
  cluster_similar: false
""")

        assert config.triage.enabled is True
        assert config.triage.confidence_threshold == 0.85
        assert config.triage.auto_dismiss_fp is True
        assert config.triage.cluster_similar is False


class TestReportingParsing:
    """Tests for reporting configuration parsing."""

    @pytest.fixture
    def loader(self):
        return ConfigLoader()

    def test_parse_reporting(self, loader):
        """Test parsing reporting configuration."""
        config = loader.load_from_string("""
reporting:
  format: html
  output_dir: reports/security
  include_false_positives: true
  max_remediations: 5
""")

        assert config.reporting.format == "html"
        assert config.reporting.output_dir == Path("reports/security")
        assert config.reporting.include_false_positives is True
        assert config.reporting.max_remediations == 5


class TestTopLevelOptions:
    """Tests for top-level option parsing."""

    @pytest.fixture
    def loader(self):
        return ConfigLoader()

    def test_parse_top_level(self, loader):
        """Test parsing top-level options."""
        config = loader.load_from_string("""
parallel_scans: false
max_findings: 500
""")

        assert config.parallel_scans is False
        assert config.max_findings == 500


class TestLoadConfigFunction:
    """Tests for load_config convenience function."""

    def test_load_config_returns_default(self):
        """Test load_config returns default when no file."""
        with TemporaryDirectory() as tmpdir:
            import os

            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                config = load_config()
                assert isinstance(config, SecurityConfig)
            finally:
                os.chdir(old_cwd)

    def test_load_config_from_path(self):
        """Test load_config with explicit path."""
        with TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text("fail_on: critical")

            config = load_config(config_path)

            assert config.fail_on == FailOnSeverity.CRITICAL


class TestCompleteConfig:
    """Tests for complete configuration scenarios."""

    @pytest.fixture
    def loader(self):
        return ConfigLoader()

    def test_full_config(self, loader):
        """Test loading a complete configuration."""
        config = loader.load_from_string("""
scanners:
  semgrep:
    enabled: true
    custom_rules_dir: .security/semgrep-rules
    registry_rulesets:
      - p/security-audit
      - p/owasp-top-ten
    timeout: 600
  codeql:
    enabled: false
  bandit:
    enabled: true
    skips:
      - B101
    confidence_level: high

fail_on: high

exclusions:
  paths:
    - node_modules/
    - .venv/
    - build/
  patterns:
    - "*_test.py"
    - "test_*.py"
  file_extensions:
    - .pyc
    - .min.js

triage:
  enabled: true
  confidence_threshold: 0.8
  auto_dismiss_fp: false
  cluster_similar: true

reporting:
  format: markdown
  output_dir: docs/security
  include_false_positives: false
  max_remediations: 10

parallel_scans: true
max_findings: 1000
""")

        # Verify scanners
        assert config.semgrep.enabled is True
        assert config.semgrep.custom_rules_dir == Path(".security/semgrep-rules")
        assert config.codeql.enabled is False
        assert config.bandit.enabled is True

        # Verify enabled scanners
        enabled = config.get_enabled_scanners()
        assert ScannerType.SEMGREP in enabled
        assert ScannerType.CODEQL not in enabled
        assert ScannerType.BANDIT in enabled

        # Verify fail_on behavior
        assert config.should_fail("critical") is True
        assert config.should_fail("high") is True
        assert config.should_fail("medium") is False

        # Verify exclusions
        assert config.exclusions.matches_path("node_modules/pkg/index.js") is True
        assert config.exclusions.matches_path("src/app.py") is False

        # Verify triage
        assert config.triage.confidence_threshold == 0.8

        # Verify reporting
        assert config.reporting.format == "markdown"
        assert config.reporting.output_dir == Path("docs/security")
