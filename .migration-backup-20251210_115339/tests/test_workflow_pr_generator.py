"""Unit tests for PR generator."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from specify_cli.workflow.pr_generator import (
    PRGenerator,
)


@pytest.fixture
def task_id():
    """Sample task ID for testing."""
    return "task-123"


@pytest.fixture
def acceptance_criteria():
    """Sample acceptance criteria."""
    return [
        {"text": "User can login", "checked": True},
        {"text": "Password is hashed", "checked": True},
        {"text": "Session is created", "checked": True},
    ]


@pytest.fixture
def test_plan():
    """Sample test plan."""
    return """- Tested login with valid credentials
- Tested login with invalid credentials
- Verified password hashing
- Verified session creation"""


class TestPRGenerator:
    """Test suite for PRGenerator."""

    def test_init(self, task_id):
        """Test generator initialization."""
        generator = PRGenerator(task_id)
        assert generator.task_id == task_id

    def test_generate_pr_title_with_scope(self, task_id):
        """Test PR title generation with scope."""
        generator = PRGenerator(task_id)
        title = generator._generate_pr_title(
            task_title="Add user authentication",
            scope="auth",
            pr_type="feat",
        )
        assert title == "feat(auth): add user authentication"

    def test_generate_pr_title_without_scope(self, task_id):
        """Test PR title generation without scope."""
        generator = PRGenerator(task_id)
        title = generator._generate_pr_title(
            task_title="Fix login bug",
            scope=None,
            pr_type="fix",
        )
        assert title == "fix: fix login bug"

    def test_generate_pr_title_strips_task_id(self, task_id):
        """Test that task ID prefix is stripped from title."""
        generator = PRGenerator(task_id)
        title = generator._generate_pr_title(
            task_title="task-123: Add feature X",
            scope=None,
            pr_type="feat",
        )
        assert title == "feat: add feature X"
        assert "task-123" not in title

    def test_generate_pr_title_strips_task_id_case_insensitive(self, task_id):
        """Test task ID stripping is case-insensitive."""
        generator = PRGenerator(task_id)
        title = generator._generate_pr_title(
            task_title="Task-456 - Fix bug",
            scope=None,
            pr_type="fix",
        )
        assert title == "fix: fix bug"

    def test_generate_pr_body(self, task_id, acceptance_criteria, test_plan):
        """Test PR body generation with all sections."""
        generator = PRGenerator(task_id)
        body = generator._generate_pr_body(
            acceptance_criteria=acceptance_criteria,
            test_plan=test_plan,
            implementation_notes="Implemented OAuth2 authentication",
            validation_results={"tests_passed": True, "coverage": 95.5},
        )

        # Verify structure
        assert "## Summary" in body
        assert f"Completes task: {task_id}" in body
        assert "Implemented OAuth2 authentication" in body
        assert "## Acceptance Criteria" in body
        assert "[x] User can login" in body
        assert "[x] Password is hashed" in body
        assert "[x] Session is created" in body
        assert "## Test Plan" in body
        assert "Tested login with valid credentials" in body
        assert "## Validation Results" in body
        assert "tests_passed" in body
        assert "coverage" in body

    def test_generate_pr_body_with_unchecked_acs(self, task_id, test_plan):
        """Test PR body with unchecked acceptance criteria."""
        acs = [
            {"text": "AC 1", "checked": True},
            {"text": "AC 2", "checked": False},
        ]

        generator = PRGenerator(task_id)
        body = generator._generate_pr_body(
            acceptance_criteria=acs,
            test_plan=test_plan,
        )

        assert "[x] AC 1" in body
        assert "[ ] AC 2" in body

    def test_generate_pr_body_with_legacy_acs(self, task_id, test_plan):
        """Test PR body with legacy string format ACs."""
        acs = ["AC 1", "AC 2", "AC 3"]

        generator = PRGenerator(task_id)
        body = generator._generate_pr_body(
            acceptance_criteria=acs,
            test_plan=test_plan,
        )

        # Legacy format treated as checked
        assert "[x] AC 1" in body
        assert "[x] AC 2" in body
        assert "[x] AC 3" in body

    def test_generate_pr_body_no_acs(self, task_id, test_plan):
        """Test PR body with no acceptance criteria."""
        generator = PRGenerator(task_id)
        body = generator._generate_pr_body(
            acceptance_criteria=[],
            test_plan=test_plan,
        )

        assert "## Acceptance Criteria" in body
        assert "No acceptance criteria defined." in body

    def test_generate_pr_body_validation_results_boolean(self, task_id, test_plan):
        """Test validation results with boolean values."""
        generator = PRGenerator(task_id)
        body = generator._generate_pr_body(
            acceptance_criteria=[],
            test_plan=test_plan,
            validation_results={
                "tests_passed": True,
                "linting_passed": False,
                "coverage_met": True,
            },
        )

        assert "✅ Pass" in body
        assert "❌ Fail" in body

    @patch("specify_cli.workflow.pr_generator.subprocess.run")
    @patch("specify_cli.workflow.pr_generator.input")
    def test_generate_success(
        self, mock_input, mock_run, task_id, acceptance_criteria, test_plan
    ):
        """Test successful PR generation."""
        # Mock user approval
        mock_input.return_value = "y"

        # Mock git branch check (branch is pushed)
        # Mock gh pr create
        mock_run.side_effect = [
            # Check upstream
            MagicMock(returncode=0, stdout="origin/main", stderr=""),
            # Check status
            MagicMock(returncode=0, stdout="## main...origin/main", stderr=""),
            # Create PR
            MagicMock(
                returncode=0,
                stdout="https://github.com/user/repo/pull/123",
                stderr="",
            ),
        ]

        generator = PRGenerator(task_id)
        result = generator.generate(
            task_title="Add user authentication",
            acceptance_criteria=acceptance_criteria,
            test_plan=test_plan,
            scope="auth",
            pr_type="feat",
        )

        assert result.success is True
        assert result.pr_url == "https://github.com/user/repo/pull/123"
        assert result.error_message is None

    @patch("specify_cli.workflow.pr_generator.input")
    def test_generate_user_cancels(
        self, mock_input, task_id, acceptance_criteria, test_plan
    ):
        """Test PR generation cancelled by user."""
        # Mock user rejection
        mock_input.return_value = "n"

        generator = PRGenerator(task_id)
        result = generator.generate(
            task_title="Add feature",
            acceptance_criteria=acceptance_criteria,
            test_plan=test_plan,
        )

        assert result.success is False
        assert result.pr_url is None
        assert "cancelled by user" in result.error_message

    @patch("specify_cli.workflow.pr_generator.subprocess.run")
    @patch("specify_cli.workflow.pr_generator.input")
    def test_generate_branch_not_pushed(
        self, mock_input, mock_run, task_id, acceptance_criteria, test_plan
    ):
        """Test PR generation when branch is not pushed."""
        # Mock user approval
        mock_input.return_value = "y"

        # Mock git checks (no upstream)
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="")

        generator = PRGenerator(task_id)
        result = generator.generate(
            task_title="Add feature",
            acceptance_criteria=acceptance_criteria,
            test_plan=test_plan,
        )

        assert result.success is False
        assert result.pr_url is None
        assert "not pushed to remote" in result.error_message

    @patch("specify_cli.workflow.pr_generator.subprocess.run")
    @patch("specify_cli.workflow.pr_generator.input")
    def test_generate_branch_ahead(
        self, mock_input, mock_run, task_id, acceptance_criteria, test_plan
    ):
        """Test PR generation when branch has unpushed commits."""
        # Mock user approval
        mock_input.return_value = "y"

        # Mock git checks (branch ahead)
        mock_run.side_effect = [
            # Check upstream
            MagicMock(returncode=0, stdout="origin/main", stderr=""),
            # Check status (ahead)
            MagicMock(
                returncode=0,
                stdout="## main...origin/main [ahead 2]",
                stderr="",
            ),
        ]

        generator = PRGenerator(task_id)
        result = generator.generate(
            task_title="Add feature",
            acceptance_criteria=acceptance_criteria,
            test_plan=test_plan,
        )

        assert result.success is False
        assert "not pushed to remote" in result.error_message

    @patch("specify_cli.workflow.pr_generator.subprocess.run")
    @patch("specify_cli.workflow.pr_generator.input")
    def test_generate_gh_cli_not_found(
        self, mock_input, mock_run, task_id, acceptance_criteria, test_plan
    ):
        """Test PR generation when gh CLI is not installed."""
        # Mock user approval
        mock_input.return_value = "y"

        # Mock git checks (branch pushed)
        # Mock gh CLI not found
        mock_run.side_effect = [
            # Check upstream
            MagicMock(returncode=0, stdout="origin/main", stderr=""),
            # Check status
            MagicMock(returncode=0, stdout="## main...origin/main", stderr=""),
            # gh not found
            FileNotFoundError("gh not found"),
        ]

        generator = PRGenerator(task_id)
        result = generator.generate(
            task_title="Add feature",
            acceptance_criteria=acceptance_criteria,
            test_plan=test_plan,
        )

        assert result.success is False
        assert result.pr_url is None
        assert "gh CLI not found" in result.error_message

    @patch("specify_cli.workflow.pr_generator.subprocess.run")
    @patch("specify_cli.workflow.pr_generator.input")
    def test_generate_gh_cli_fails(
        self, mock_input, mock_run, task_id, acceptance_criteria, test_plan
    ):
        """Test PR generation when gh CLI command fails."""
        # Mock user approval
        mock_input.return_value = "y"

        # Mock git checks (branch pushed)
        # Mock gh CLI failure
        from subprocess import CalledProcessError

        mock_run.side_effect = [
            # Check upstream
            MagicMock(returncode=0, stdout="origin/main", stderr=""),
            # Check status
            MagicMock(returncode=0, stdout="## main...origin/main", stderr=""),
            # gh pr create fails
            CalledProcessError(1, ["gh", "pr", "create"], stderr="API error"),
        ]

        generator = PRGenerator(task_id)
        result = generator.generate(
            task_title="Add feature",
            acceptance_criteria=acceptance_criteria,
            test_plan=test_plan,
        )

        assert result.success is False
        assert result.pr_url is None
        assert "Failed to create PR" in result.error_message

    @patch("specify_cli.workflow.pr_generator.subprocess.run")
    def test_generate_skip_approval(
        self, mock_run, task_id, acceptance_criteria, test_plan
    ):
        """Test PR generation without requiring approval."""
        # Mock git checks and gh pr create
        mock_run.side_effect = [
            # Check upstream
            MagicMock(returncode=0, stdout="origin/main", stderr=""),
            # Check status
            MagicMock(returncode=0, stdout="## main...origin/main", stderr=""),
            # Create PR
            MagicMock(
                returncode=0,
                stdout="https://github.com/user/repo/pull/123",
                stderr="",
            ),
        ]

        generator = PRGenerator(task_id)
        result = generator.generate(
            task_title="Add feature",
            acceptance_criteria=acceptance_criteria,
            test_plan=test_plan,
            require_approval=False,
        )

        assert result.success is True
        assert result.pr_url == "https://github.com/user/repo/pull/123"

    def test_request_approval_yes(self, task_id):
        """Test approval with 'yes' response."""
        generator = PRGenerator(task_id)

        with patch("specify_cli.workflow.pr_generator.input", return_value="y"):
            assert generator._request_approval() is True

        with patch("specify_cli.workflow.pr_generator.input", return_value="yes"):
            assert generator._request_approval() is True

    def test_request_approval_no(self, task_id):
        """Test rejection with 'no' response."""
        generator = PRGenerator(task_id)

        with patch("specify_cli.workflow.pr_generator.input", return_value="n"):
            assert generator._request_approval() is False

        with patch("specify_cli.workflow.pr_generator.input", return_value="no"):
            assert generator._request_approval() is False

        with patch("specify_cli.workflow.pr_generator.input", return_value=""):
            assert generator._request_approval() is False

    @patch("specify_cli.workflow.pr_generator.subprocess.run")
    def test_is_branch_pushed_true(self, mock_run, task_id):
        """Test branch push detection when branch is pushed."""
        mock_run.side_effect = [
            # Check upstream
            MagicMock(returncode=0, stdout="origin/main", stderr=""),
            # Check status
            MagicMock(returncode=0, stdout="## main...origin/main", stderr=""),
        ]

        generator = PRGenerator(task_id)
        assert generator._is_branch_pushed() is True

    @patch("specify_cli.workflow.pr_generator.subprocess.run")
    def test_is_branch_pushed_no_upstream(self, mock_run, task_id):
        """Test branch push detection when no upstream is configured."""
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="")

        generator = PRGenerator(task_id)
        assert generator._is_branch_pushed() is False

    @patch("specify_cli.workflow.pr_generator.subprocess.run")
    def test_create_pr_extracts_url(self, mock_run, task_id):
        """Test PR URL extraction from gh CLI output."""
        # Mock gh CLI with extra text
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Creating pull request https://github.com/user/repo/pull/123\nDone!",
            stderr="",
        )

        generator = PRGenerator(task_id)
        url = generator._create_pr("Test title", "Test body")
        assert url == "https://github.com/user/repo/pull/123"
