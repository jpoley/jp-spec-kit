"""Tests for workflow transition validation engine.

Tests cover:
- AC1: NONE validation mode (immediate pass-through)
- AC2: KEYWORD validation with exact string matching
- AC3: PULL_REQUEST validation with GitHub API check
- AC4: Validation mode parser (parse_validation_mode) - tested in test_workflow_transition.py
- AC5: Integration into workflow transition logic
- AC6: CLI prompts for KEYWORD mode
- AC7: Helpful error messages for failed validations
- AC8: --skip-validation flag for emergency override
- AC9: Logging of validation decisions
"""

from unittest.mock import MagicMock, patch

import pytest

from specify_cli.workflow.transition import (
    Artifact,
    TransitionSchema,
    ValidationMode,
)
from specify_cli.workflow.validation_engine import (
    TransitionValidator,
    ValidationResult,
)


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_validation_result_creation(self):
        """ValidationResult can be created with required fields."""
        result = ValidationResult(
            passed=True,
            message="Test passed",
            mode=ValidationMode.NONE,
        )
        assert result.passed is True
        assert result.message == "Test passed"
        assert result.mode == ValidationMode.NONE
        assert result.skipped is False
        assert result.details == {}

    def test_validation_result_with_details(self):
        """ValidationResult can include details dictionary."""
        result = ValidationResult(
            passed=False,
            message="Test failed",
            mode=ValidationMode.KEYWORD,
            details={"expected": "APPROVED", "provided": "APPROVE"},
        )
        assert result.passed is False
        assert result.details == {"expected": "APPROVED", "provided": "APPROVE"}

    def test_validation_result_skipped(self):
        """ValidationResult can be marked as skipped."""
        result = ValidationResult(
            passed=True,
            message="Skipped",
            mode=ValidationMode.NONE,
            skipped=True,
        )
        assert result.skipped is True


class TestTransitionValidatorInit:
    """Tests for TransitionValidator initialization."""

    def test_validator_creation_default(self):
        """Validator can be created with default settings."""
        validator = TransitionValidator()
        assert validator.skip_validation is False

    def test_validator_creation_skip_mode(self):
        """AC8: Validator can be created with skip_validation flag."""
        validator = TransitionValidator(skip_validation=True)
        assert validator.skip_validation is True


class TestValidationModeNone:
    """Tests for NONE validation mode (AC1)."""

    def test_none_mode_always_passes(self):
        """AC1: NONE validation mode provides immediate pass-through."""
        validator = TransitionValidator()
        transition = TransitionSchema(
            name="test",
            from_state="Start",
            to_state="End",
            validation=ValidationMode.NONE,
        )
        context = {"feature": "test-feature", "base_path": "/tmp/test"}

        result = validator.validate(transition, context)

        assert result.passed is True
        assert result.mode == ValidationMode.NONE
        assert result.skipped is False
        assert "No validation gate required" in result.message

    def test_none_mode_no_artifacts_required(self):
        """NONE mode passes even without artifacts (if none are required)."""
        validator = TransitionValidator()
        transition = TransitionSchema(
            name="test",
            from_state="Start",
            to_state="End",
            validation=ValidationMode.NONE,
            output_artifacts=[],
        )
        context = {"feature": "test-feature", "base_path": "/tmp/test"}

        result = validator.validate(transition, context)

        assert result.passed is True
        assert result.mode == ValidationMode.NONE


class TestValidationModeKeyword:
    """Tests for KEYWORD validation mode (AC2, AC6, AC7)."""

    def test_keyword_validation_with_correct_keyword(self):
        """AC2: KEYWORD validation passes with exact string match."""
        validator = TransitionValidator()
        transition = TransitionSchema(
            name="test",
            from_state="Start",
            to_state="End",
            validation=ValidationMode.KEYWORD,
            validation_keyword="APPROVED",
        )
        context = {
            "feature": "test-feature",
            "base_path": "/tmp/test",
            "validation_keyword": "APPROVED",  # Provide keyword in context
        }

        result = validator.validate(transition, context)

        assert result.passed is True
        assert result.mode == ValidationMode.KEYWORD
        assert "APPROVED" in result.message

    def test_keyword_validation_with_incorrect_keyword(self):
        """AC2, AC7: KEYWORD validation fails with helpful error message."""
        validator = TransitionValidator()
        transition = TransitionSchema(
            name="test",
            from_state="Start",
            to_state="End",
            validation=ValidationMode.KEYWORD,
            validation_keyword="APPROVED",
        )
        context = {
            "feature": "test-feature",
            "base_path": "/tmp/test",
            "validation_keyword": "APPROVE",  # Wrong keyword
        }

        result = validator.validate(transition, context)

        assert result.passed is False
        assert result.mode == ValidationMode.KEYWORD
        assert "APPROVED" in result.message  # Expected keyword mentioned
        assert "APPROVE" in result.message  # Provided keyword mentioned
        assert result.details["expected"] == "APPROVED"
        assert result.details["provided"] == "APPROVE"

    def test_keyword_validation_case_sensitive(self):
        """AC2: KEYWORD validation is case-sensitive."""
        validator = TransitionValidator()
        transition = TransitionSchema(
            name="test",
            from_state="Start",
            to_state="End",
            validation=ValidationMode.KEYWORD,
            validation_keyword="APPROVED",
        )
        context = {
            "feature": "test-feature",
            "base_path": "/tmp/test",
            "validation_keyword": "approved",  # lowercase
        }

        result = validator.validate(transition, context)

        assert result.passed is False
        assert result.mode == ValidationMode.KEYWORD

    def test_keyword_validation_no_keyword_configured(self):
        """AC7: KEYWORD mode without keyword is prevented by schema validation."""
        # TransitionSchema validates this in __post_init__, so we can't even create
        # a KEYWORD transition without a keyword. This is a good design decision.
        with pytest.raises(ValueError, match="KEYWORD validation mode requires"):
            TransitionSchema(
                name="test",
                from_state="Start",
                to_state="End",
                validation=ValidationMode.KEYWORD,
                validation_keyword=None,  # No keyword configured
            )

    @patch("builtins.input", return_value="APPROVED")
    @patch("builtins.print")
    def test_keyword_prompt_with_correct_input(self, mock_print, mock_input):
        """AC6: KEYWORD mode prompts user and accepts correct keyword."""
        validator = TransitionValidator()
        transition = TransitionSchema(
            name="test",
            from_state="Start",
            to_state="End",
            validation=ValidationMode.KEYWORD,
            validation_keyword="APPROVED",
        )
        context = {
            "feature": "test-feature",
            "base_path": "/tmp/test",
            # No validation_keyword in context - will prompt
        }

        result = validator.validate(transition, context)

        assert result.passed is True
        assert result.mode == ValidationMode.KEYWORD
        mock_input.assert_called_once()
        # Verify prompt was displayed
        assert any(
            "KEYWORD VALIDATION" in str(call) for call in mock_print.call_args_list
        )

    @patch("builtins.input", return_value="WRONG")
    @patch("builtins.print")
    def test_keyword_prompt_with_incorrect_input(self, mock_print, mock_input):
        """AC6, AC7: KEYWORD prompt shows helpful error on incorrect input."""
        validator = TransitionValidator()
        transition = TransitionSchema(
            name="test",
            from_state="Start",
            to_state="End",
            validation=ValidationMode.KEYWORD,
            validation_keyword="APPROVED",
        )
        context = {"feature": "test-feature", "base_path": "/tmp/test"}

        result = validator.validate(transition, context)

        assert result.passed is False
        assert result.mode == ValidationMode.KEYWORD
        mock_input.assert_called_once()

    @patch("builtins.input", side_effect=KeyboardInterrupt)
    @patch("builtins.print")
    def test_keyword_prompt_cancelled(self, mock_print, mock_input):
        """AC6: KEYWORD prompt can be cancelled with Ctrl+C."""
        validator = TransitionValidator()
        transition = TransitionSchema(
            name="test",
            from_state="Start",
            to_state="End",
            validation=ValidationMode.KEYWORD,
            validation_keyword="APPROVED",
        )
        context = {"feature": "test-feature", "base_path": "/tmp/test"}

        result = validator.validate(transition, context)

        assert result.passed is False
        assert result.mode == ValidationMode.KEYWORD
        assert "cancelled" in result.message.lower()


class TestValidationModePullRequest:
    """Tests for PULL_REQUEST validation mode (AC3, AC7)."""

    @patch("subprocess.run")
    def test_pull_request_validation_with_merged_pr(self, mock_run):
        """AC3: PULL_REQUEST validation passes when PR is merged."""
        # Mock gh CLI response for merged PR
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='[{"number": 42, "title": "Add feature", "mergedAt": "2024-01-01T12:00:00Z"}]',
            stderr="",
        )

        validator = TransitionValidator()
        transition = TransitionSchema(
            name="test",
            from_state="Start",
            to_state="End",
            validation=ValidationMode.PULL_REQUEST,
        )
        context = {"feature": "test-feature", "base_path": "/tmp/test"}

        result = validator.validate(transition, context)

        assert result.passed is True
        assert result.mode == ValidationMode.PULL_REQUEST
        assert "42" in result.message  # PR number mentioned
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_pull_request_validation_no_merged_pr(self, mock_run):
        """AC3, AC7: PULL_REQUEST validation fails with helpful message when no PR."""
        # Mock gh CLI response for no PRs
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="[]",
            stderr="",
        )

        validator = TransitionValidator()
        transition = TransitionSchema(
            name="test",
            from_state="Start",
            to_state="End",
            validation=ValidationMode.PULL_REQUEST,
        )
        context = {"feature": "test-feature", "base_path": "/tmp/test"}

        result = validator.validate(transition, context)

        assert result.passed is False
        assert result.mode == ValidationMode.PULL_REQUEST
        assert "No merged PR found" in result.message
        assert "test-feature" in result.message

    @patch("subprocess.run")
    def test_pull_request_validation_specific_pr_merged(self, mock_run):
        """AC3: PULL_REQUEST validation can check specific PR number."""
        # Mock gh CLI response for specific PR
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"number": 42, "title": "Add feature", "state": "MERGED", "merged": true, "mergedAt": "2024-01-01T12:00:00Z"}',
            stderr="",
        )

        validator = TransitionValidator()
        transition = TransitionSchema(
            name="test",
            from_state="Start",
            to_state="End",
            validation=ValidationMode.PULL_REQUEST,
        )
        context = {
            "feature": "test-feature",
            "base_path": "/tmp/test",
            "pr_number": 42,  # Check specific PR
        }

        result = validator.validate(transition, context)

        assert result.passed is True
        assert result.mode == ValidationMode.PULL_REQUEST
        assert result.details["pr_number"] == 42

    @patch("subprocess.run")
    def test_pull_request_validation_pr_not_merged(self, mock_run):
        """AC3, AC7: PULL_REQUEST validation fails if PR exists but not merged."""
        # Mock gh CLI response for open PR
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"number": 42, "title": "Add feature", "state": "OPEN", "merged": false}',
            stderr="",
        )

        validator = TransitionValidator()
        transition = TransitionSchema(
            name="test",
            from_state="Start",
            to_state="End",
            validation=ValidationMode.PULL_REQUEST,
        )
        context = {
            "feature": "test-feature",
            "base_path": "/tmp/test",
            "pr_number": 42,
        }

        result = validator.validate(transition, context)

        assert result.passed is False
        assert result.mode == ValidationMode.PULL_REQUEST
        assert "not merged" in result.message.lower()
        assert "OPEN" in result.message

    def test_pull_request_validation_no_feature(self):
        """AC7: PULL_REQUEST validation fails with helpful error if no feature."""
        validator = TransitionValidator()
        transition = TransitionSchema(
            name="test",
            from_state="Start",
            to_state="End",
            validation=ValidationMode.PULL_REQUEST,
        )
        context = {"base_path": "/tmp/test"}  # No feature name

        result = validator.validate(transition, context)

        assert result.passed is False
        assert result.mode == ValidationMode.PULL_REQUEST
        assert "feature name not provided" in result.message

    @patch("subprocess.run")
    def test_pull_request_validation_gh_cli_error(self, mock_run):
        """AC7: PULL_REQUEST validation handles gh CLI errors gracefully."""
        # Mock gh CLI failure
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="gh: command not found",
        )

        validator = TransitionValidator()
        transition = TransitionSchema(
            name="test",
            from_state="Start",
            to_state="End",
            validation=ValidationMode.PULL_REQUEST,
        )
        context = {"feature": "test-feature", "base_path": "/tmp/test"}

        result = validator.validate(transition, context)

        assert result.passed is False
        assert result.mode == ValidationMode.PULL_REQUEST
        assert "Failed to query GitHub" in result.message

    @patch("subprocess.run", side_effect=FileNotFoundError)
    def test_pull_request_validation_gh_not_installed(self, mock_run):
        """AC7: PULL_REQUEST validation gives helpful error if gh not installed."""
        validator = TransitionValidator()
        transition = TransitionSchema(
            name="test",
            from_state="Start",
            to_state="End",
            validation=ValidationMode.PULL_REQUEST,
        )
        context = {"feature": "test-feature", "base_path": "/tmp/test"}

        result = validator.validate(transition, context)

        assert result.passed is False
        assert result.mode == ValidationMode.PULL_REQUEST
        assert "gh" in result.message.lower()
        assert "install" in result.message.lower()


class TestArtifactChecking:
    """Tests for artifact existence checking."""

    def test_artifact_check_passes_when_no_artifacts(self):
        """Validation passes when no artifacts are required."""
        validator = TransitionValidator()
        transition = TransitionSchema(
            name="test",
            from_state="Start",
            to_state="End",
            validation=ValidationMode.NONE,
            output_artifacts=[],
        )
        context = {"feature": "test", "base_path": "/tmp/test"}

        result = validator.validate(transition, context)

        assert result.passed is True

    def test_artifact_check_fails_when_artifacts_missing(self, tmp_path):
        """AC7: Validation fails with helpful error when artifacts missing."""
        validator = TransitionValidator()
        transition = TransitionSchema(
            name="test",
            from_state="Start",
            to_state="End",
            validation=ValidationMode.NONE,
            output_artifacts=[
                Artifact(type="prd", path="./docs/prd/{feature}.md", required=True),
            ],
        )
        context = {"feature": "test-feature", "base_path": str(tmp_path)}

        result = validator.validate(transition, context)

        assert result.passed is False
        assert "prd" in result.message.lower()
        assert "missing" in result.message.lower()
        assert result.details["missing_artifacts"] == ["prd"]

    def test_artifact_check_passes_when_artifact_exists(self, tmp_path):
        """Validation passes when required artifact exists."""
        # Create artifact
        docs_dir = tmp_path / "docs" / "prd"
        docs_dir.mkdir(parents=True)
        (docs_dir / "test-feature.md").write_text("# PRD")

        validator = TransitionValidator()
        transition = TransitionSchema(
            name="test",
            from_state="Start",
            to_state="End",
            validation=ValidationMode.NONE,
            output_artifacts=[
                Artifact(type="prd", path="./docs/prd/{feature}.md", required=True),
            ],
        )
        context = {"feature": "test-feature", "base_path": str(tmp_path)}

        result = validator.validate(transition, context)

        assert result.passed is True

    def test_artifact_check_optional_artifacts_not_required(self, tmp_path):
        """Optional artifacts don't block validation if missing."""
        validator = TransitionValidator()
        transition = TransitionSchema(
            name="test",
            from_state="Start",
            to_state="End",
            validation=ValidationMode.NONE,
            output_artifacts=[
                Artifact(type="prd", path="./docs/prd/{feature}.md", required=False),
            ],
        )
        context = {"feature": "test-feature", "base_path": str(tmp_path)}

        result = validator.validate(transition, context)

        assert result.passed is True


class TestSkipValidationFlag:
    """Tests for --skip-validation flag (AC8)."""

    def test_skip_validation_bypasses_none_mode(self):
        """AC8: Skip flag bypasses NONE validation."""
        validator = TransitionValidator(skip_validation=True)
        transition = TransitionSchema(
            name="test",
            from_state="Start",
            to_state="End",
            validation=ValidationMode.NONE,
        )
        context = {"feature": "test", "base_path": "/tmp/test"}

        result = validator.validate(transition, context)

        assert result.passed is True
        assert result.skipped is True
        assert "skipped" in result.message.lower()

    def test_skip_validation_bypasses_keyword_mode(self):
        """AC8: Skip flag bypasses KEYWORD validation."""
        validator = TransitionValidator(skip_validation=True)
        transition = TransitionSchema(
            name="test",
            from_state="Start",
            to_state="End",
            validation=ValidationMode.KEYWORD,
            validation_keyword="APPROVED",
        )
        context = {"feature": "test", "base_path": "/tmp/test"}

        result = validator.validate(transition, context)

        assert result.passed is True
        assert result.skipped is True

    def test_skip_validation_bypasses_pull_request_mode(self):
        """AC8: Skip flag bypasses PULL_REQUEST validation."""
        validator = TransitionValidator(skip_validation=True)
        transition = TransitionSchema(
            name="test",
            from_state="Start",
            to_state="End",
            validation=ValidationMode.PULL_REQUEST,
        )
        context = {"feature": "test", "base_path": "/tmp/test"}

        result = validator.validate(transition, context)

        assert result.passed is True
        assert result.skipped is True

    def test_skip_validation_bypasses_missing_artifacts(self, tmp_path):
        """AC8: Skip flag even bypasses missing artifact checks."""
        validator = TransitionValidator(skip_validation=True)
        transition = TransitionSchema(
            name="test",
            from_state="Start",
            to_state="End",
            validation=ValidationMode.NONE,
            output_artifacts=[
                Artifact(type="prd", path="./docs/prd/{feature}.md", required=True),
            ],
        )
        context = {"feature": "test-feature", "base_path": str(tmp_path)}

        result = validator.validate(transition, context)

        assert result.passed is True
        assert result.skipped is True


class TestLogging:
    """Tests for audit trail logging (AC9)."""

    def test_none_mode_logs_decision(self, caplog):
        """AC9: NONE mode validation is logged."""
        import logging

        caplog.set_level(logging.INFO)
        validator = TransitionValidator()
        transition = TransitionSchema(
            name="test-transition",
            from_state="Start",
            to_state="End",
            validation=ValidationMode.NONE,
        )
        context = {"feature": "test", "base_path": "/tmp/test"}

        validator.validate(transition, context)

        assert any(
            "NONE validation mode" in record.message for record in caplog.records
        )
        assert any("test-transition" in record.message for record in caplog.records)

    def test_keyword_success_logs_decision(self, caplog):
        """AC9: KEYWORD validation success is logged."""
        import logging

        caplog.set_level(logging.INFO)
        validator = TransitionValidator()
        transition = TransitionSchema(
            name="test-transition",
            from_state="Start",
            to_state="End",
            validation=ValidationMode.KEYWORD,
            validation_keyword="APPROVED",
        )
        context = {
            "feature": "test",
            "base_path": "/tmp/test",
            "validation_keyword": "APPROVED",
        }

        validator.validate(transition, context)

        assert any(
            "KEYWORD validation passed" in record.message for record in caplog.records
        )

    def test_keyword_failure_logs_decision(self, caplog):
        """AC9: KEYWORD validation failure is logged."""
        validator = TransitionValidator()
        transition = TransitionSchema(
            name="test-transition",
            from_state="Start",
            to_state="End",
            validation=ValidationMode.KEYWORD,
            validation_keyword="APPROVED",
        )
        context = {
            "feature": "test",
            "base_path": "/tmp/test",
            "validation_keyword": "WRONG",
        }

        validator.validate(transition, context)

        assert any(
            "KEYWORD validation failed" in record.message for record in caplog.records
        )

    def test_skip_validation_logs_warning(self, caplog):
        """AC9: Skip validation mode logs warning."""
        validator = TransitionValidator(skip_validation=True)
        transition = TransitionSchema(
            name="test-transition",
            from_state="Start",
            to_state="End",
            validation=ValidationMode.KEYWORD,
            validation_keyword="APPROVED",
        )
        context = {"feature": "test", "base_path": "/tmp/test"}

        validator.validate(transition, context)

        assert any("SKIPPING validation" in record.message for record in caplog.records)
