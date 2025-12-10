"""Tests for security configuration schema validation."""

import pytest

from specify_cli.security.config.schema import (
    ConfigSchema,
    SchemaErrorType,
)


class TestConfigSchema:
    """Tests for ConfigSchema validation."""

    @pytest.fixture
    def schema(self):
        """Create a schema instance."""
        return ConfigSchema()

    def test_validate_empty_config(self, schema):
        """Test validating empty configuration."""
        errors = schema.validate({})
        assert len(errors) == 0

    def test_validate_non_dict(self, schema):
        """Test validating non-dict configuration."""
        errors = schema.validate("invalid")

        assert len(errors) == 1
        assert errors[0].error_type == SchemaErrorType.INVALID_TYPE

    def test_validate_valid_config(self, schema):
        """Test validating a complete valid configuration."""
        config = {
            "scanners": {
                "semgrep": {"enabled": True, "timeout": 300},
                "codeql": {"enabled": False},
                "bandit": {"enabled": True, "confidence_level": "high"},
            },
            "fail_on": "high",
            "exclusions": {
                "paths": ["node_modules/"],
                "patterns": ["*_test.py"],
            },
            "triage": {
                "enabled": True,
                "confidence_threshold": 0.8,
            },
            "reporting": {
                "format": "markdown",
                "max_remediations": 5,
            },
            "parallel_scans": True,
            "max_findings": 500,
        }

        errors = schema.validate(config)
        assert len(errors) == 0


class TestScannerValidation:
    """Tests for scanner configuration validation."""

    @pytest.fixture
    def schema(self):
        return ConfigSchema()

    def test_unknown_scanner(self, schema):
        """Test error for unknown scanner."""
        config = {"scanners": {"unknown_scanner": {"enabled": True}}}

        errors = schema.validate(config)

        assert len(errors) == 1
        assert errors[0].error_type == SchemaErrorType.UNKNOWN_FIELD
        assert "unknown_scanner" in errors[0].message

    def test_invalid_scanner_config_type(self, schema):
        """Test error for non-dict scanner config."""
        config = {"scanners": {"semgrep": "invalid"}}

        errors = schema.validate(config)

        assert len(errors) == 1
        assert errors[0].error_type == SchemaErrorType.INVALID_TYPE

    def test_invalid_enabled_type(self, schema):
        """Test error for non-bool enabled field."""
        config = {"scanners": {"semgrep": {"enabled": "yes"}}}

        errors = schema.validate(config)

        assert len(errors) == 1
        assert errors[0].error_type == SchemaErrorType.INVALID_TYPE
        assert "enabled" in errors[0].path

    def test_semgrep_invalid_timeout(self, schema):
        """Test error for invalid Semgrep timeout."""
        config = {"scanners": {"semgrep": {"timeout": -1}}}

        errors = schema.validate(config)

        assert len(errors) == 1
        assert errors[0].error_type == SchemaErrorType.INVALID_VALUE
        assert "timeout" in errors[0].path

    def test_semgrep_invalid_rulesets_type(self, schema):
        """Test error for non-list rulesets."""
        config = {"scanners": {"semgrep": {"registry_rulesets": "p/default"}}}

        errors = schema.validate(config)

        assert len(errors) == 1
        assert errors[0].error_type == SchemaErrorType.INVALID_TYPE

    def test_codeql_invalid_languages_type(self, schema):
        """Test error for non-list languages."""
        config = {"scanners": {"codeql": {"languages": "python"}}}

        errors = schema.validate(config)

        assert len(errors) == 1
        assert errors[0].error_type == SchemaErrorType.INVALID_TYPE

    def test_bandit_invalid_confidence_level(self, schema):
        """Test error for invalid confidence level."""
        config = {"scanners": {"bandit": {"confidence_level": "very_high"}}}

        errors = schema.validate(config)

        assert len(errors) == 1
        assert errors[0].error_type == SchemaErrorType.INVALID_VALUE

    def test_bandit_invalid_skips_type(self, schema):
        """Test error for non-list skips."""
        config = {"scanners": {"bandit": {"skips": "B101"}}}

        errors = schema.validate(config)

        assert len(errors) == 1
        assert errors[0].error_type == SchemaErrorType.INVALID_TYPE


class TestFailOnValidation:
    """Tests for fail_on validation."""

    @pytest.fixture
    def schema(self):
        return ConfigSchema()

    def test_valid_fail_on_values(self, schema):
        """Test all valid fail_on values."""
        for value in ["critical", "high", "medium", "low", "none"]:
            errors = schema.validate({"fail_on": value})
            assert len(errors) == 0, f"Failed for: {value}"

    def test_invalid_fail_on_value(self, schema):
        """Test error for invalid fail_on value."""
        errors = schema.validate({"fail_on": "severe"})

        assert len(errors) == 1
        assert errors[0].error_type == SchemaErrorType.INVALID_VALUE

    def test_invalid_fail_on_type(self, schema):
        """Test error for non-string fail_on."""
        errors = schema.validate({"fail_on": 1})

        assert len(errors) == 1
        assert errors[0].error_type == SchemaErrorType.INVALID_TYPE


class TestExclusionsValidation:
    """Tests for exclusions validation."""

    @pytest.fixture
    def schema(self):
        return ConfigSchema()

    def test_valid_exclusions(self, schema):
        """Test valid exclusions configuration."""
        config = {
            "exclusions": {
                "paths": ["node_modules/", ".venv/"],
                "patterns": ["*_test.py", "*.min.js"],
                "file_extensions": [".pyc", ".pyo"],
            }
        }

        errors = schema.validate(config)
        assert len(errors) == 0

    def test_invalid_exclusions_type(self, schema):
        """Test error for non-dict exclusions."""
        errors = schema.validate({"exclusions": "node_modules/"})

        assert len(errors) == 1
        assert errors[0].error_type == SchemaErrorType.INVALID_TYPE

    def test_invalid_paths_type(self, schema):
        """Test error for non-list paths."""
        errors = schema.validate({"exclusions": {"paths": "node_modules/"}})

        assert len(errors) == 1
        assert errors[0].error_type == SchemaErrorType.INVALID_TYPE


class TestTriageValidation:
    """Tests for triage validation."""

    @pytest.fixture
    def schema(self):
        return ConfigSchema()

    def test_valid_triage(self, schema):
        """Test valid triage configuration."""
        config = {
            "triage": {
                "enabled": True,
                "confidence_threshold": 0.8,
                "auto_dismiss_fp": True,
                "cluster_similar": False,
            }
        }

        errors = schema.validate(config)
        assert len(errors) == 0

    def test_invalid_triage_type(self, schema):
        """Test error for non-dict triage."""
        errors = schema.validate({"triage": True})

        assert len(errors) == 1
        assert errors[0].error_type == SchemaErrorType.INVALID_TYPE

    def test_invalid_confidence_threshold_type(self, schema):
        """Test error for non-numeric confidence threshold."""
        errors = schema.validate({"triage": {"confidence_threshold": "high"}})

        assert len(errors) == 1
        assert errors[0].error_type == SchemaErrorType.INVALID_TYPE

    def test_confidence_threshold_too_high(self, schema):
        """Test error for confidence threshold > 1.0."""
        errors = schema.validate({"triage": {"confidence_threshold": 1.5}})

        assert len(errors) == 1
        assert errors[0].error_type == SchemaErrorType.INVALID_RANGE

    def test_confidence_threshold_too_low(self, schema):
        """Test error for confidence threshold < 0.0."""
        errors = schema.validate({"triage": {"confidence_threshold": -0.1}})

        assert len(errors) == 1
        assert errors[0].error_type == SchemaErrorType.INVALID_RANGE

    def test_invalid_auto_dismiss_type(self, schema):
        """Test error for non-bool auto_dismiss_fp."""
        errors = schema.validate({"triage": {"auto_dismiss_fp": "yes"}})

        assert len(errors) == 1
        assert errors[0].error_type == SchemaErrorType.INVALID_TYPE


class TestReportingValidation:
    """Tests for reporting validation."""

    @pytest.fixture
    def schema(self):
        return ConfigSchema()

    def test_valid_reporting(self, schema):
        """Test valid reporting configuration."""
        config = {
            "reporting": {
                "format": "markdown",
                "max_remediations": 10,
            }
        }

        errors = schema.validate(config)
        assert len(errors) == 0

    def test_valid_formats(self, schema):
        """Test all valid format values."""
        for fmt in ["markdown", "html", "json", "sarif"]:
            errors = schema.validate({"reporting": {"format": fmt}})
            assert len(errors) == 0, f"Failed for format: {fmt}"

    def test_invalid_format(self, schema):
        """Test error for invalid format."""
        errors = schema.validate({"reporting": {"format": "pdf"}})

        assert len(errors) == 1
        assert errors[0].error_type == SchemaErrorType.INVALID_VALUE

    def test_invalid_max_remediations(self, schema):
        """Test error for invalid max_remediations."""
        errors = schema.validate({"reporting": {"max_remediations": -1}})

        assert len(errors) == 1
        assert errors[0].error_type == SchemaErrorType.INVALID_VALUE


class TestTopLevelValidation:
    """Tests for top-level field validation."""

    @pytest.fixture
    def schema(self):
        return ConfigSchema()

    def test_invalid_parallel_scans_type(self, schema):
        """Test error for non-bool parallel_scans."""
        errors = schema.validate({"parallel_scans": "yes"})

        assert len(errors) == 1
        assert errors[0].error_type == SchemaErrorType.INVALID_TYPE

    def test_invalid_max_findings(self, schema):
        """Test error for invalid max_findings."""
        errors = schema.validate({"max_findings": -100})

        assert len(errors) == 1
        assert errors[0].error_type == SchemaErrorType.INVALID_VALUE
