"""Tests for workflow transition validation engine."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from specify_cli.workflow.transition import (
    Artifact,
    TransitionSchema,
    ValidationMode,
)
from specify_cli.workflow.validation_engine import (
    TransitionValidator,
    TransitionValidationResult,
)


class TestTransitionValidationResult:
    """Tests for TransitionValidationResult dataclass."""

    def test_validation_result_creation(self) -> None:
        """Test creating a validation result."""
        result = TransitionValidationResult(
            passed=True,
            message="Validation passed",
            mode=ValidationMode.NONE,
        )
        assert result.passed is True
        assert result.message == "Validation passed"
        assert result.mode == ValidationMode.NONE
        assert result.skipped is False
        assert result.details == {}

    def test_validation_result_with_details(self) -> None:
        """Test validation result with details."""
        result = TransitionValidationResult(
            passed=False,
            message="Missing artifact",
            mode=ValidationMode.NONE,
            details={"missing": ["prd"]},
        )
        assert result.passed is False
        assert result.details == {"missing": ["prd"]}

    def test_validation_result_skipped(self) -> None:
        """Test validation result with skipped flag."""
        result = TransitionValidationResult(
            passed=True,
            message="Skipped",
            mode=ValidationMode.KEYWORD,
            skipped=True,
        )
        assert result.skipped is True

    def test_to_dict(self) -> None:
        """Test serialization to dictionary."""
        result = TransitionValidationResult(
            passed=True,
            message="OK",
            mode=ValidationMode.KEYWORD,
            skipped=False,
            details={"key": "value"},
        )
        d = result.to_dict()
        assert d["passed"] is True
        assert d["message"] == "OK"
        assert d["mode"] == "KEYWORD"
        assert d["skipped"] is False
        assert d["details"] == {"key": "value"}


class TestTransitionValidatorInit:
    """Tests for TransitionValidator initialization."""

    def test_validator_creation_default(self) -> None:
        """Test creating validator with default settings."""
        validator = TransitionValidator()
        assert validator.skip_validation is False

    def test_validator_creation_skip_mode(self) -> None:
        """Test creating validator with skip mode."""
        validator = TransitionValidator(skip_validation=True)
        assert validator.skip_validation is True


class TestValidationModeNone:
    """Tests for NONE validation mode."""

    @pytest.fixture
    def validator(self) -> TransitionValidator:
        """Create a validator instance."""
        return TransitionValidator()

    @pytest.fixture
    def none_transition(self) -> TransitionSchema:
        """Create a transition with NONE validation."""
        return TransitionSchema(
            name="test",
            from_state="A",
            to_state="B",
            validation=ValidationMode.NONE,
        )

    def test_none_mode_always_passes(
        self,
        validator: TransitionValidator,
        none_transition: TransitionSchema,
    ) -> None:
        """Test NONE mode always passes."""
        result = validator.validate(none_transition, {})
        assert result.passed is True
        assert result.mode == ValidationMode.NONE

    def test_none_mode_no_artifacts_required(
        self,
        validator: TransitionValidator,
    ) -> None:
        """Test NONE mode with no artifact requirements."""
        transition = TransitionSchema(
            name="test",
            from_state="A",
            to_state="B",
            validation=ValidationMode.NONE,
            output_artifacts=[],
        )
        result = validator.validate(transition, {})
        assert result.passed is True


class TestValidationModeKeyword:
    """Tests for KEYWORD validation mode."""

    @pytest.fixture
    def validator(self) -> TransitionValidator:
        """Create a validator instance."""
        return TransitionValidator()

    @pytest.fixture
    def keyword_transition(self) -> TransitionSchema:
        """Create a transition with KEYWORD validation."""
        return TransitionSchema(
            name="test",
            from_state="A",
            to_state="B",
            validation=ValidationMode.KEYWORD,
            validation_keyword="APPROVED",
        )

    def test_keyword_validation_with_correct_keyword(
        self,
        validator: TransitionValidator,
        keyword_transition: TransitionSchema,
    ) -> None:
        """Test keyword validation passes with correct keyword."""
        result = validator.validate(
            keyword_transition,
            {"validation_keyword": "APPROVED"},
        )
        assert result.passed is True
        assert result.mode == ValidationMode.KEYWORD

    def test_keyword_validation_with_incorrect_keyword(
        self,
        validator: TransitionValidator,
        keyword_transition: TransitionSchema,
    ) -> None:
        """Test keyword validation fails with incorrect keyword."""
        result = validator.validate(
            keyword_transition,
            {"validation_keyword": "WRONG"},
        )
        assert result.passed is False
        assert "APPROVED" in result.message

    def test_keyword_validation_case_sensitive(
        self,
        validator: TransitionValidator,
        keyword_transition: TransitionSchema,
    ) -> None:
        """Test keyword validation is case-sensitive."""
        result = validator.validate(
            keyword_transition,
            {"validation_keyword": "approved"},
        )
        assert result.passed is False

    def test_keyword_validation_no_keyword_configured(
        self,
        validator: TransitionValidator,
    ) -> None:
        """Test error when no keyword is configured at runtime."""
        # Create valid transition first
        transition = TransitionSchema(
            name="test",
            from_state="A",
            to_state="B",
            validation=ValidationMode.KEYWORD,
            validation_keyword="TEMP",
        )
        # Force no keyword to test runtime validation
        transition.validation_keyword = None
        result = validator.validate(transition, {})
        assert result.passed is False
        assert "no keyword" in result.message.lower()

    def test_keyword_prompt_with_correct_input(
        self,
        validator: TransitionValidator,
        keyword_transition: TransitionSchema,
    ) -> None:
        """Test interactive keyword prompt with correct input."""
        with patch("builtins.input", return_value="APPROVED"):
            result = validator.validate(keyword_transition, {})
            assert result.passed is True

    def test_keyword_prompt_with_incorrect_input(
        self,
        validator: TransitionValidator,
        keyword_transition: TransitionSchema,
    ) -> None:
        """Test interactive keyword prompt with incorrect input."""
        with patch("builtins.input", return_value="WRONG"):
            result = validator.validate(keyword_transition, {})
            assert result.passed is False

    def test_keyword_prompt_cancelled(
        self,
        validator: TransitionValidator,
        keyword_transition: TransitionSchema,
    ) -> None:
        """Test interactive keyword prompt when cancelled."""
        with patch("builtins.input", side_effect=KeyboardInterrupt):
            result = validator.validate(keyword_transition, {})
            assert result.passed is False
            assert "cancelled" in result.message.lower()


class TestValidationModePullRequest:
    """Tests for PULL_REQUEST validation mode."""

    @pytest.fixture
    def validator(self) -> TransitionValidator:
        """Create a validator instance."""
        return TransitionValidator()

    @pytest.fixture
    def pr_transition(self) -> TransitionSchema:
        """Create a transition with PULL_REQUEST validation."""
        return TransitionSchema(
            name="test",
            from_state="A",
            to_state="B",
            validation=ValidationMode.PULL_REQUEST,
        )

    def test_pull_request_validation_with_merged_pr(
        self,
        validator: TransitionValidator,
        pr_transition: TransitionSchema,
    ) -> None:
        """Test PR validation passes when merged PR found."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = (
            '[{"number": 42, "title": "feat: auth", "mergedAt": "2024-01-01"}]'
        )

        with patch("subprocess.run", return_value=mock_result):
            result = validator.validate(pr_transition, {"feature": "auth"})
            assert result.passed is True
            assert result.details.get("pr_number") == 42

    def test_pull_request_validation_no_merged_pr(
        self,
        validator: TransitionValidator,
        pr_transition: TransitionSchema,
    ) -> None:
        """Test PR validation fails when no merged PR found."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "[]"

        with patch("subprocess.run", return_value=mock_result):
            result = validator.validate(pr_transition, {"feature": "auth"})
            assert result.passed is False
            assert "no merged pr" in result.message.lower()

    def test_pull_request_validation_specific_pr_merged(
        self,
        validator: TransitionValidator,
        pr_transition: TransitionSchema,
    ) -> None:
        """Test PR validation with specific PR number that is merged."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = (
            '{"number": 123, "title": "test", "state": "MERGED", "merged": true}'
        )

        with patch("subprocess.run", return_value=mock_result):
            result = validator.validate(
                pr_transition,
                {"feature": "auth", "pr_number": 123},
            )
            assert result.passed is True

    def test_pull_request_validation_pr_not_merged(
        self,
        validator: TransitionValidator,
        pr_transition: TransitionSchema,
    ) -> None:
        """Test PR validation fails when PR is not merged."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = (
            '{"number": 123, "title": "test", "state": "OPEN", "merged": false}'
        )

        with patch("subprocess.run", return_value=mock_result):
            result = validator.validate(
                pr_transition,
                {"feature": "auth", "pr_number": 123},
            )
            assert result.passed is False
            assert "not merged" in result.message.lower()

    def test_pull_request_validation_no_feature(
        self,
        validator: TransitionValidator,
        pr_transition: TransitionSchema,
    ) -> None:
        """Test PR validation fails without feature name."""
        result = validator.validate(pr_transition, {})
        assert result.passed is False
        assert "feature" in result.message.lower()

    def test_pull_request_validation_invalid_feature_name(
        self,
        validator: TransitionValidator,
        pr_transition: TransitionSchema,
    ) -> None:
        """Test PR validation fails with invalid feature name."""
        # Test with special characters that could manipulate search query
        invalid_names = [
            "feat; rm -rf",  # Command injection attempt
            "auth' OR '1'='1",  # SQL-like injection
            "test in:body",  # Search query manipulation
            "feat<script>",  # XSS-like attempt
            "auth OR repo:malicious",  # GitHub search manipulation
        ]
        for invalid_name in invalid_names:
            result = validator.validate(pr_transition, {"feature": invalid_name})
            assert result.passed is False
            assert result.message == "Invalid feature name format"

    def test_pull_request_validation_valid_feature_names(
        self,
        validator: TransitionValidator,
        pr_transition: TransitionSchema,
    ) -> None:
        """Test PR validation accepts valid feature names."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "[]"  # No merged PRs, but validation passes format check

        valid_names = [
            "auth",
            "user-authentication",
            "feature_name",
            "Feature123",
            "my-feature_v2",
        ]
        with patch("subprocess.run", return_value=mock_result):
            for valid_name in valid_names:
                result = validator.validate(pr_transition, {"feature": valid_name})
                # These should pass the format check but fail because no merged PRs
                assert "Invalid feature name format" not in result.message

    def test_pull_request_validation_gh_cli_error(
        self,
        validator: TransitionValidator,
        pr_transition: TransitionSchema,
    ) -> None:
        """Test PR validation handles gh CLI errors."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "not authenticated"

        with patch("subprocess.run", return_value=mock_result):
            result = validator.validate(pr_transition, {"feature": "auth"})
            assert result.passed is False
            assert "not authenticated" in result.message

    def test_pull_request_validation_gh_not_installed(
        self,
        validator: TransitionValidator,
        pr_transition: TransitionSchema,
    ) -> None:
        """Test PR validation handles missing gh CLI."""
        with patch("subprocess.run", side_effect=FileNotFoundError):
            result = validator.validate(pr_transition, {"feature": "auth"})
            assert result.passed is False
            assert "not found" in result.message.lower()


class TestArtifactChecking:
    """Tests for artifact existence checking."""

    @pytest.fixture
    def validator(self) -> TransitionValidator:
        """Create a validator instance."""
        return TransitionValidator()

    def test_artifact_check_passes_when_no_artifacts(
        self,
        validator: TransitionValidator,
    ) -> None:
        """Test artifact check passes with no required artifacts."""
        transition = TransitionSchema(
            name="test",
            from_state="A",
            to_state="B",
            validation=ValidationMode.NONE,
            output_artifacts=[],
        )
        result = validator.validate(transition, {})
        assert result.passed is True

    def test_artifact_check_fails_when_artifacts_missing(
        self,
        validator: TransitionValidator,
        tmp_path: Path,
    ) -> None:
        """Test artifact check fails when required artifacts missing."""
        transition = TransitionSchema(
            name="test",
            from_state="A",
            to_state="B",
            validation=ValidationMode.NONE,
            output_artifacts=[
                Artifact(type="prd", path="./docs/prd/{feature}.md", required=True),
            ],
        )
        result = validator.validate(
            transition,
            {"feature": "auth", "base_path": str(tmp_path)},
        )
        assert result.passed is False
        assert "prd" in result.message.lower()

    def test_artifact_check_passes_when_artifact_exists(
        self,
        validator: TransitionValidator,
        tmp_path: Path,
    ) -> None:
        """Test artifact check passes when artifact exists."""
        # Create the artifact
        prd_dir = tmp_path / "docs" / "prd"
        prd_dir.mkdir(parents=True)
        (prd_dir / "auth.md").write_text("# PRD")

        transition = TransitionSchema(
            name="test",
            from_state="A",
            to_state="B",
            validation=ValidationMode.NONE,
            output_artifacts=[
                Artifact(type="prd", path="./docs/prd/{feature}.md", required=True),
            ],
        )
        result = validator.validate(
            transition,
            {"feature": "auth", "base_path": str(tmp_path)},
        )
        assert result.passed is True

    def test_artifact_check_optional_artifacts_not_required(
        self,
        validator: TransitionValidator,
        tmp_path: Path,
    ) -> None:
        """Test optional artifacts don't fail validation when missing."""
        transition = TransitionSchema(
            name="test",
            from_state="A",
            to_state="B",
            validation=ValidationMode.NONE,
            output_artifacts=[
                Artifact(type="prd", path="./docs/prd/{feature}.md", required=False),
            ],
        )
        result = validator.validate(
            transition,
            {"feature": "auth", "base_path": str(tmp_path)},
        )
        assert result.passed is True

    def test_multiple_artifacts_passes_when_at_least_one_exists(
        self,
        validator: TransitionValidator,
        tmp_path: Path,
    ) -> None:
        """Test multiple artifacts pass when at least one matching file exists."""
        # Create the directory and a matching file
        adr_dir = tmp_path / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        (adr_dir / "ADR-001-authentication.md").write_text("# ADR 001")

        transition = TransitionSchema(
            name="test",
            from_state="A",
            to_state="B",
            validation=ValidationMode.NONE,
            output_artifacts=[
                Artifact(
                    type="adr",
                    path="./docs/adr/ADR-{NNN}-{slug}.md",
                    required=True,
                    multiple=True,
                ),
            ],
        )
        result = validator.validate(
            transition,
            {"feature": "auth", "base_path": str(tmp_path)},
        )
        assert result.passed is True

    def test_multiple_artifacts_fails_when_none_exist(
        self,
        validator: TransitionValidator,
        tmp_path: Path,
    ) -> None:
        """Test multiple artifacts fail when no matching files exist."""
        # Create the directory but no matching files
        adr_dir = tmp_path / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        (adr_dir / "README.md").write_text("# ADRs")  # Non-matching file

        transition = TransitionSchema(
            name="test",
            from_state="A",
            to_state="B",
            validation=ValidationMode.NONE,
            output_artifacts=[
                Artifact(
                    type="adr",
                    path="./docs/adr/ADR-{NNN}-{slug}.md",
                    required=True,
                    multiple=True,
                ),
            ],
        )
        result = validator.validate(
            transition,
            {"feature": "auth", "base_path": str(tmp_path)},
        )
        assert result.passed is False
        assert "adr" in result.details.get("missing_artifacts", [])

    def test_optional_multiple_artifacts_passes_when_missing(
        self,
        validator: TransitionValidator,
        tmp_path: Path,
    ) -> None:
        """Test optional multiple artifacts don't fail when missing."""
        # Create empty directory
        adr_dir = tmp_path / "docs" / "adr"
        adr_dir.mkdir(parents=True)

        transition = TransitionSchema(
            name="test",
            from_state="A",
            to_state="B",
            validation=ValidationMode.NONE,
            output_artifacts=[
                Artifact(
                    type="adr",
                    path="./docs/adr/ADR-{NNN}-{slug}.md",
                    required=False,
                    multiple=True,
                ),
            ],
        )
        result = validator.validate(
            transition,
            {"feature": "auth", "base_path": str(tmp_path)},
        )
        assert result.passed is True


class TestSkipValidationFlag:
    """Tests for --skip-validation flag."""

    def test_skip_validation_bypasses_none_mode(self) -> None:
        """Test skip flag bypasses NONE mode."""
        validator = TransitionValidator(skip_validation=True)
        transition = TransitionSchema(
            name="test",
            from_state="A",
            to_state="B",
            validation=ValidationMode.NONE,
        )
        result = validator.validate(transition, {})
        assert result.passed is True
        assert result.skipped is True

    def test_skip_validation_bypasses_keyword_mode(self) -> None:
        """Test skip flag bypasses KEYWORD mode."""
        validator = TransitionValidator(skip_validation=True)
        transition = TransitionSchema(
            name="test",
            from_state="A",
            to_state="B",
            validation=ValidationMode.KEYWORD,
            validation_keyword="SECRET",
        )
        result = validator.validate(transition, {})
        assert result.passed is True
        assert result.skipped is True

    def test_skip_validation_bypasses_pull_request_mode(self) -> None:
        """Test skip flag bypasses PULL_REQUEST mode."""
        validator = TransitionValidator(skip_validation=True)
        transition = TransitionSchema(
            name="test",
            from_state="A",
            to_state="B",
            validation=ValidationMode.PULL_REQUEST,
        )
        result = validator.validate(transition, {})
        assert result.passed is True
        assert result.skipped is True

    def test_skip_validation_bypasses_missing_artifacts(self) -> None:
        """Test skip flag also bypasses artifact checking."""
        validator = TransitionValidator(skip_validation=True)
        transition = TransitionSchema(
            name="test",
            from_state="A",
            to_state="B",
            validation=ValidationMode.NONE,
            output_artifacts=[
                Artifact(type="prd", path="./nonexistent.md", required=True),
            ],
        )
        result = validator.validate(transition, {"base_path": "/tmp"})
        assert result.passed is True
        assert result.skipped is True


class TestLogging:
    """Tests for audit logging."""

    def test_none_mode_logs_decision(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test NONE mode logs validation decision."""
        import logging

        caplog.set_level(logging.INFO)
        validator = TransitionValidator()
        transition = TransitionSchema(
            name="test_transition",
            from_state="A",
            to_state="B",
            validation=ValidationMode.NONE,
        )
        validator.validate(transition, {})
        assert "test_transition" in caplog.text

    def test_keyword_success_logs_decision(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test KEYWORD success logs validation decision."""
        import logging

        caplog.set_level(logging.INFO)
        validator = TransitionValidator()
        transition = TransitionSchema(
            name="test_transition",
            from_state="A",
            to_state="B",
            validation=ValidationMode.KEYWORD,
            validation_keyword="OK",
        )
        validator.validate(transition, {"validation_keyword": "OK"})
        assert "KEYWORD" in caplog.text
        assert "passed" in caplog.text.lower()

    def test_keyword_failure_logs_decision(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test KEYWORD failure logs validation decision."""
        import logging

        caplog.set_level(logging.WARNING)
        validator = TransitionValidator()
        transition = TransitionSchema(
            name="test_transition",
            from_state="A",
            to_state="B",
            validation=ValidationMode.KEYWORD,
            validation_keyword="OK",
        )
        validator.validate(transition, {"validation_keyword": "WRONG"})
        assert "failed" in caplog.text.lower()

    def test_skip_validation_logs_warning(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test skip validation logs warning."""
        import logging

        caplog.set_level(logging.WARNING)
        validator = TransitionValidator(skip_validation=True)
        transition = TransitionSchema(
            name="test",
            from_state="A",
            to_state="B",
            validation=ValidationMode.KEYWORD,
            validation_keyword="OK",
        )
        validator.validate(transition, {})
        assert "skip" in caplog.text.lower()
