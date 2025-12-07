"""Unit tests for rebase_checker module.

Tests cover:
- MergeCommit dataclass parsing
- Git command execution and error handling
- Merge commit detection
- Branch rebased status checking
- Worktree support
- Error message formatting
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from specify_cli.hooks.rebase_checker import (
    BranchNotFoundError,
    GitCommandError,
    MergeCommit,
    NotAGitRepositoryError,
    RebaseCheckResult,
    RebaseCheckerError,
    _run_git_command,
    branch_exists,
    check_rebase_status,
    find_merge_commits,
    format_rebase_error,
    get_current_branch,
    get_merge_base,
    is_branch_rebased,
)


class TestMergeCommit:
    """Tests for MergeCommit dataclass."""

    def test_from_log_line_valid(self) -> None:
        """Test parsing a valid log line."""
        line = "abc123def|abc123d|Merge branch 'feature' into main|parent1 parent2"
        commit = MergeCommit.from_log_line(line)

        assert commit.sha == "abc123def"
        assert commit.short_sha == "abc123d"
        assert commit.subject == "Merge branch 'feature' into main"
        assert commit.parents == ["parent1", "parent2"]

    def test_from_log_line_with_pipe_in_subject(self) -> None:
        """Test parsing a log line with pipe in commit message."""
        line = "abc123def|abc123d|Fix issue | with pipe|parent1 parent2"
        commit = MergeCommit.from_log_line(line)

        # Should handle the pipe correctly
        assert commit.sha == "abc123def"
        assert commit.short_sha == "abc123d"
        assert "Fix issue" in commit.subject

    def test_from_log_line_empty_parents(self) -> None:
        """Test parsing with no parents (shouldn't happen for merges)."""
        line = "abc123def|abc123d|Some subject|"
        commit = MergeCommit.from_log_line(line)

        assert commit.parents == []

    def test_from_log_line_invalid(self) -> None:
        """Test error on invalid log line format."""
        with pytest.raises(ValueError, match="Invalid log line format"):
            MergeCommit.from_log_line("invalid|line")


class TestRebaseCheckResult:
    """Tests for RebaseCheckResult dataclass."""

    def test_error_message_rebased(self) -> None:
        """Test no error message when rebased."""
        result = RebaseCheckResult(
            is_rebased=True,
            merge_commits=[],
            base_branch="main",
            current_branch="feature",
            merge_base="abc123",
        )

        assert result.error_message is None

    def test_error_message_single_commit(self) -> None:
        """Test error message with single merge commit."""
        commit = MergeCommit(
            sha="abc123def",
            short_sha="abc123d",
            subject="Merge branch 'main' into feature",
            parents=["p1", "p2"],
        )
        result = RebaseCheckResult(
            is_rebased=False,
            merge_commits=[commit],
            base_branch="main",
            current_branch="feature",
            merge_base="abc123",
        )

        error_msg = result.error_message
        assert error_msg is not None
        assert "1 merge commit" in error_msg
        assert "abc123d" in error_msg
        assert "feature" in error_msg

    def test_error_message_multiple_commits(self) -> None:
        """Test error message with multiple merge commits."""
        commits = [
            MergeCommit(f"sha{i}", f"sh{i}", f"Merge {i}", ["p1", "p2"])
            for i in range(3)
        ]
        result = RebaseCheckResult(
            is_rebased=False,
            merge_commits=commits,
            base_branch="main",
            current_branch="feature",
            merge_base="abc123",
        )

        error_msg = result.error_message
        assert error_msg is not None
        assert "3 merge commits" in error_msg

    def test_error_message_truncates_at_five(self) -> None:
        """Test that error message only shows first 5 commits."""
        commits = [
            MergeCommit(f"sha{i}", f"short{i}", f"Merge {i}", ["p1", "p2"])
            for i in range(10)
        ]
        result = RebaseCheckResult(
            is_rebased=False,
            merge_commits=commits,
            base_branch="main",
            current_branch="feature",
            merge_base="abc123",
        )

        error_msg = result.error_message
        assert error_msg is not None
        assert "short0" in error_msg
        assert "short4" in error_msg
        assert "short5" not in error_msg
        assert "and 5 more" in error_msg


class TestGitCommandRunner:
    """Tests for _run_git_command function."""

    @patch("subprocess.run")
    def test_successful_command(self, mock_run: MagicMock) -> None:
        """Test successful git command execution."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="output",
            stderr="",
        )

        result = _run_git_command(["status"])

        mock_run.assert_called_once()
        assert result.returncode == 0
        assert result.stdout == "output"

    @patch("subprocess.run")
    def test_command_failure_with_check(self, mock_run: MagicMock) -> None:
        """Test that failed command raises GitCommandError when check=True."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="error message",
        )

        with pytest.raises(GitCommandError) as exc_info:
            _run_git_command(["invalid"], check=True)

        assert exc_info.value.returncode == 1
        assert "error message" in str(exc_info.value)

    @patch("subprocess.run")
    def test_command_failure_without_check(self, mock_run: MagicMock) -> None:
        """Test that failed command returns result when check=False."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="error",
        )

        result = _run_git_command(["invalid"], check=False)

        assert result.returncode == 1

    @patch("subprocess.run")
    def test_not_a_git_repository(self, mock_run: MagicMock) -> None:
        """Test detection of 'not a git repository' error."""
        mock_run.return_value = MagicMock(
            returncode=128,
            stdout="",
            stderr="fatal: not a git repository",
        )

        with pytest.raises(NotAGitRepositoryError):
            _run_git_command(["status"])

    @patch("subprocess.run")
    def test_command_timeout(self, mock_run: MagicMock) -> None:
        """Test handling of command timeout."""
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired("git", 30)

        with pytest.raises(GitCommandError) as exc_info:
            _run_git_command(["status"])

        assert "timed out" in str(exc_info.value)

    @patch("subprocess.run")
    def test_git_not_found(self, mock_run: MagicMock) -> None:
        """Test handling when git is not installed."""
        mock_run.side_effect = FileNotFoundError("git not found")

        with pytest.raises(GitCommandError) as exc_info:
            _run_git_command(["status"])

        assert "not found" in str(exc_info.value)


class TestGetCurrentBranch:
    """Tests for get_current_branch function."""

    @patch("specify_cli.hooks.rebase_checker._run_git_command")
    def test_normal_branch(self, mock_run: MagicMock) -> None:
        """Test getting current branch on a normal branch."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="feature/add-tests\n",
        )

        branch = get_current_branch()

        assert branch == "feature/add-tests"

    @patch("specify_cli.hooks.rebase_checker._run_git_command")
    def test_detached_head(self, mock_run: MagicMock) -> None:
        """Test getting branch in detached HEAD state."""
        # First call fails (symbolic-ref), second succeeds (rev-parse)
        mock_run.side_effect = [
            MagicMock(returncode=1, stdout="", stderr=""),
            MagicMock(returncode=0, stdout="HEAD\n", stderr=""),
        ]

        branch = get_current_branch()

        assert branch == "HEAD"


class TestBranchExists:
    """Tests for branch_exists function."""

    @patch("specify_cli.hooks.rebase_checker._run_git_command")
    def test_local_branch_exists(self, mock_run: MagicMock) -> None:
        """Test checking if a local branch exists."""
        mock_run.return_value = MagicMock(returncode=0)

        result = branch_exists("main")

        assert result is True

    @patch("specify_cli.hooks.rebase_checker._run_git_command")
    def test_remote_branch_exists(self, mock_run: MagicMock) -> None:
        """Test checking if a remote-tracking branch exists."""
        # First call fails (local), second succeeds (remote)
        mock_run.side_effect = [
            MagicMock(returncode=1),
            MagicMock(returncode=0),
        ]

        result = branch_exists("main")

        assert result is True

    @patch("specify_cli.hooks.rebase_checker._run_git_command")
    def test_branch_not_found(self, mock_run: MagicMock) -> None:
        """Test when branch doesn't exist locally or remotely."""
        mock_run.return_value = MagicMock(returncode=1)

        result = branch_exists("nonexistent")

        assert result is False


class TestGetMergeBase:
    """Tests for get_merge_base function."""

    @patch("specify_cli.hooks.rebase_checker.branch_exists")
    @patch("specify_cli.hooks.rebase_checker._run_git_command")
    def test_successful_merge_base(
        self, mock_run: MagicMock, mock_exists: MagicMock
    ) -> None:
        """Test getting merge base between two branches."""
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="abc123def456\n",
        )

        result = get_merge_base("main", "feature")

        assert result == "abc123def456"

    @patch("specify_cli.hooks.rebase_checker.branch_exists")
    def test_base_branch_not_found(self, mock_exists: MagicMock) -> None:
        """Test error when base branch doesn't exist."""
        mock_exists.return_value = False

        with pytest.raises(BranchNotFoundError) as exc_info:
            get_merge_base("nonexistent", "feature")

        assert "nonexistent" in str(exc_info.value)

    @patch("specify_cli.hooks.rebase_checker.branch_exists")
    @patch("specify_cli.hooks.rebase_checker._run_git_command")
    def test_uses_remote_tracking_branch(
        self, mock_run: MagicMock, mock_exists: MagicMock
    ) -> None:
        """Test using origin/main when local main doesn't exist."""
        # First call says 'main' doesn't exist, second says 'origin/main' does
        mock_exists.side_effect = [False, True]
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="abc123\n",
        )

        result = get_merge_base("main", "feature")

        assert result == "abc123"
        # Verify origin/main was used
        call_args = mock_run.call_args[0][0]
        assert "origin/main" in call_args


class TestFindMergeCommits:
    """Tests for find_merge_commits function."""

    @patch("specify_cli.hooks.rebase_checker.get_current_branch")
    @patch("specify_cli.hooks.rebase_checker.get_merge_base")
    @patch("specify_cli.hooks.rebase_checker._run_git_command")
    def test_no_merge_commits(
        self,
        mock_run: MagicMock,
        mock_merge_base: MagicMock,
        mock_branch: MagicMock,
    ) -> None:
        """Test when branch has no merge commits."""
        mock_branch.return_value = "feature"
        mock_merge_base.return_value = "abc123"
        mock_run.return_value = MagicMock(returncode=0, stdout="")

        result = find_merge_commits("main")

        assert result == []

    @patch("specify_cli.hooks.rebase_checker.get_current_branch")
    @patch("specify_cli.hooks.rebase_checker.get_merge_base")
    @patch("specify_cli.hooks.rebase_checker._run_git_command")
    def test_with_merge_commits(
        self,
        mock_run: MagicMock,
        mock_merge_base: MagicMock,
        mock_branch: MagicMock,
    ) -> None:
        """Test when branch has merge commits."""
        mock_branch.return_value = "feature"
        mock_merge_base.return_value = "abc123"
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="sha1|s1|Merge main|p1 p2\nsha2|s2|Merge develop|p3 p4\n",
        )

        result = find_merge_commits("main")

        assert len(result) == 2
        assert result[0].short_sha == "s1"
        assert result[1].short_sha == "s2"

    @patch("specify_cli.hooks.rebase_checker.get_current_branch")
    @patch("specify_cli.hooks.rebase_checker.get_merge_base")
    @patch("specify_cli.hooks.rebase_checker._run_git_command")
    def test_explicit_current_branch(
        self,
        mock_run: MagicMock,
        mock_merge_base: MagicMock,
        mock_branch: MagicMock,
    ) -> None:
        """Test specifying current branch explicitly."""
        mock_merge_base.return_value = "abc123"
        mock_run.return_value = MagicMock(returncode=0, stdout="")

        find_merge_commits("main", "my-feature")

        # get_current_branch should not be called when explicit
        mock_branch.assert_not_called()


class TestIsBranchRebased:
    """Tests for is_branch_rebased function."""

    @patch("specify_cli.hooks.rebase_checker.find_merge_commits")
    def test_rebased_branch(self, mock_find: MagicMock) -> None:
        """Test that branch with no merge commits is rebased."""
        mock_find.return_value = []

        result = is_branch_rebased("main")

        assert result is True

    @patch("specify_cli.hooks.rebase_checker.find_merge_commits")
    def test_not_rebased_branch(self, mock_find: MagicMock) -> None:
        """Test that branch with merge commits is not rebased."""
        mock_find.return_value = [MergeCommit("sha", "sh", "Merge", ["p1", "p2"])]

        result = is_branch_rebased("main")

        assert result is False


class TestCheckRebaseStatus:
    """Tests for check_rebase_status function."""

    @patch("specify_cli.hooks.rebase_checker.get_current_branch")
    @patch("specify_cli.hooks.rebase_checker.get_merge_base")
    @patch("specify_cli.hooks.rebase_checker.find_merge_commits")
    def test_rebased_result(
        self,
        mock_find: MagicMock,
        mock_merge_base: MagicMock,
        mock_branch: MagicMock,
    ) -> None:
        """Test full status check for rebased branch."""
        mock_branch.return_value = "feature"
        mock_merge_base.return_value = "abc123"
        mock_find.return_value = []

        result = check_rebase_status("main")

        assert result.is_rebased is True
        assert result.merge_commits == []
        assert result.base_branch == "main"
        assert result.current_branch == "feature"
        assert result.merge_base == "abc123"
        assert result.remediation is None

    @patch("specify_cli.hooks.rebase_checker.get_current_branch")
    @patch("specify_cli.hooks.rebase_checker.get_merge_base")
    @patch("specify_cli.hooks.rebase_checker.find_merge_commits")
    def test_not_rebased_result(
        self,
        mock_find: MagicMock,
        mock_merge_base: MagicMock,
        mock_branch: MagicMock,
    ) -> None:
        """Test full status check for branch with merge commits."""
        mock_branch.return_value = "feature"
        mock_merge_base.return_value = "abc123"
        mock_find.return_value = [MergeCommit("sha", "sh", "Merge", ["p1", "p2"])]

        result = check_rebase_status("main")

        assert result.is_rebased is False
        assert len(result.merge_commits) == 1
        assert result.remediation == "git rebase -i main"


class TestFormatRebaseError:
    """Tests for format_rebase_error function."""

    def test_format_rebased(self) -> None:
        """Test that rebased result returns empty string."""
        result = RebaseCheckResult(
            is_rebased=True,
            merge_commits=[],
            base_branch="main",
            current_branch="feature",
            merge_base="abc123",
        )

        formatted = format_rebase_error(result)

        assert formatted == ""

    def test_format_with_commits(self) -> None:
        """Test formatting with merge commits."""
        commit = MergeCommit("sha123", "sha123", "Merge main", ["p1", "p2"])
        result = RebaseCheckResult(
            is_rebased=False,
            merge_commits=[commit],
            base_branch="main",
            current_branch="feature",
            merge_base="abc123",
            remediation="git rebase -i main",
        )

        formatted = format_rebase_error(result)

        assert "Branch is not rebased" in formatted
        assert "sha123" in formatted
        assert "Merge main" in formatted
        assert "git rebase -i main" in formatted

    def test_format_without_remediation(self) -> None:
        """Test formatting without remediation instructions."""
        commit = MergeCommit("sha123", "sha123", "Merge", ["p1", "p2"])
        result = RebaseCheckResult(
            is_rebased=False,
            merge_commits=[commit],
            base_branch="main",
            current_branch="feature",
            merge_base="abc123",
            remediation="git rebase -i main",
        )

        formatted = format_rebase_error(result, include_remediation=False)

        assert "git rebase" not in formatted

    def test_format_without_commits(self) -> None:
        """Test formatting without commit list."""
        commit = MergeCommit("sha123", "sha123", "Merge", ["p1", "p2"])
        result = RebaseCheckResult(
            is_rebased=False,
            merge_commits=[commit],
            base_branch="main",
            current_branch="feature",
            merge_base="abc123",
        )

        formatted = format_rebase_error(result, include_commits=False)

        assert "sha123" not in formatted

    def test_format_truncates_long_subject(self) -> None:
        """Test that long commit subjects are truncated."""
        long_subject = "A" * 100
        commit = MergeCommit("sha123", "sha123", long_subject, ["p1", "p2"])
        result = RebaseCheckResult(
            is_rebased=False,
            merge_commits=[commit],
            base_branch="main",
            current_branch="feature",
            merge_base="abc123",
        )

        formatted = format_rebase_error(result)

        # Should truncate to 50 chars + "..."
        assert "A" * 50 in formatted
        assert "..." in formatted


class TestExceptions:
    """Tests for custom exception classes."""

    def test_rebase_checker_error_is_exception(self) -> None:
        """Test that RebaseCheckerError is an Exception."""
        error = RebaseCheckerError("test error")
        assert isinstance(error, Exception)

    def test_git_command_error_attributes(self) -> None:
        """Test GitCommandError attributes."""
        error = GitCommandError("git status", 1, "error output")

        assert error.command == "git status"
        assert error.returncode == 1
        assert error.stderr == "error output"
        assert "git status" in str(error)
        assert "exit 1" in str(error)

    def test_branch_not_found_error_attributes(self) -> None:
        """Test BranchNotFoundError attributes."""
        error = BranchNotFoundError("feature-x")

        assert error.branch == "feature-x"
        assert "feature-x" in str(error)

    def test_not_a_git_repository_error(self) -> None:
        """Test NotAGitRepositoryError with and without path."""
        error1 = NotAGitRepositoryError()
        error2 = NotAGitRepositoryError(Path("/some/path"))

        assert "git repository" in str(error1)
        assert error1.path is None
        assert "/some/path" in str(error2)
        assert error2.path == Path("/some/path")


class TestWorktreeSupport:
    """Tests for git worktree support."""

    @patch("specify_cli.hooks.rebase_checker._run_git_command")
    def test_operations_accept_cwd(self, mock_run: MagicMock) -> None:
        """Test that all operations accept cwd parameter."""
        mock_run.return_value = MagicMock(returncode=0, stdout="main\n")

        worktree_path = Path("/tmp/my-worktree")

        # These should all accept cwd parameter without error
        get_current_branch(cwd=worktree_path)
        branch_exists("main", cwd=worktree_path)

        # Verify cwd was passed to git commands
        for call in mock_run.call_args_list:
            if "cwd" in call.kwargs:
                assert call.kwargs["cwd"] == worktree_path

    @patch("specify_cli.hooks.rebase_checker.get_current_branch")
    @patch("specify_cli.hooks.rebase_checker.get_merge_base")
    @patch("specify_cli.hooks.rebase_checker.find_merge_commits")
    def test_check_rebase_status_accepts_cwd(
        self,
        mock_find: MagicMock,
        mock_merge_base: MagicMock,
        mock_branch: MagicMock,
    ) -> None:
        """Test check_rebase_status with worktree path."""
        mock_branch.return_value = "feature"
        mock_merge_base.return_value = "abc123"
        mock_find.return_value = []

        worktree_path = Path("/tmp/worktree")
        result = check_rebase_status("main", cwd=worktree_path)

        # Verify cwd was passed through
        mock_branch.assert_called_once_with(worktree_path)
        mock_merge_base.assert_called_once()
        assert result.is_rebased is True


class TestIntegration:
    """Integration-style tests (still mocked but test full flow)."""

    @patch("specify_cli.hooks.rebase_checker._run_git_command")
    @patch("specify_cli.hooks.rebase_checker.branch_exists")
    def test_full_rebase_check_flow(
        self, mock_exists: MagicMock, mock_run: MagicMock
    ) -> None:
        """Test complete flow from check_rebase_status to formatted error."""
        # Setup mocks for the full flow
        mock_exists.return_value = True

        # Mock the various git commands
        def git_command_side_effect(args, cwd=None, check=True):
            if "symbolic-ref" in args:
                return MagicMock(returncode=0, stdout="feature/add-tests\n")
            elif "merge-base" in args:
                return MagicMock(returncode=0, stdout="abc123def\n")
            elif "log" in args:
                # Return one merge commit
                return MagicMock(
                    returncode=0,
                    stdout="sha123|sha123|Merge branch 'main' into feature|p1 p2\n",
                )
            return MagicMock(returncode=0, stdout="")

        mock_run.side_effect = git_command_side_effect

        # Run the check
        result = check_rebase_status("main")

        # Verify result
        assert result.is_rebased is False
        assert len(result.merge_commits) == 1
        assert result.current_branch == "feature/add-tests"
        assert result.merge_base == "abc123def"

        # Format the error
        error = format_rebase_error(result)
        assert "not rebased" in error.lower()
        assert "sha123" in error
        assert "git rebase -i main" in error
