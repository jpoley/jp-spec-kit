"""Tests for batch --validation-mode flag in specify init (AC6).

These tests verify AC6: Add --validation-mode {none|keyword|pull-request} flag
for setting all transitions at once.
"""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from specify_cli import app

runner = CliRunner()


class TestBatchValidationModeFlag:
    """Tests for the --validation-mode batch flag."""

    def test_batch_none_sets_all_none(
        self, mock_github_releases, tmp_path: Path
    ) -> None:
        """Test --validation-mode none sets all transitions to NONE."""
        project_dir = tmp_path / "test-project"
        result = runner.invoke(
            app,
            [
                "init",
                str(project_dir),
                "--ai",
                "claude",
                "--no-git",
                "--ignore-agent-tools",
                "--validation-mode",
                "none",
            ],
            input="n\n",  # Decline backlog-md install
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"
        assert "Generated flowspec_workflow.yml" in result.output

        workflow_file = project_dir / "flowspec_workflow.yml"
        assert workflow_file.exists()
        content = workflow_file.read_text()
        # All transitions should be NONE
        assert content.count("validation: NONE") >= 7

    def test_batch_keyword_sets_all_keyword(
        self, mock_github_releases, tmp_path: Path
    ) -> None:
        """Test --validation-mode keyword sets all transitions to KEYWORD."""
        project_dir = tmp_path / "test-project"
        result = runner.invoke(
            app,
            [
                "init",
                str(project_dir),
                "--ai",
                "claude",
                "--no-git",
                "--ignore-agent-tools",
                "--validation-mode",
                "keyword",
            ],
            input="n\n",  # Decline backlog-md install
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"
        assert "Generated flowspec_workflow.yml" in result.output

        workflow_file = project_dir / "flowspec_workflow.yml"
        assert workflow_file.exists()
        content = workflow_file.read_text()
        # All transitions should use KEYWORD with default "APPROVED"
        assert content.count('KEYWORD["APPROVED"]') >= 7

    def test_batch_pull_request_sets_all_pull_request(
        self, mock_github_releases, tmp_path: Path
    ) -> None:
        """Test --validation-mode pull-request sets all to PULL_REQUEST."""
        project_dir = tmp_path / "test-project"
        result = runner.invoke(
            app,
            [
                "init",
                str(project_dir),
                "--ai",
                "claude",
                "--no-git",
                "--ignore-agent-tools",
                "--validation-mode",
                "pull-request",
            ],
            input="n\n",  # Decline backlog-md install
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"
        assert "Generated flowspec_workflow.yml" in result.output

        workflow_file = project_dir / "flowspec_workflow.yml"
        assert workflow_file.exists()
        content = workflow_file.read_text()
        # All transitions should be PULL_REQUEST
        assert content.count("validation: PULL_REQUEST") >= 7

    def test_invalid_batch_mode_fails(
        self, mock_github_releases, tmp_path: Path
    ) -> None:
        """Test that invalid --validation-mode value fails with error."""
        project_dir = tmp_path / "test-project"
        result = runner.invoke(
            app,
            [
                "init",
                str(project_dir),
                "--ai",
                "claude",
                "--no-git",
                "--ignore-agent-tools",
                "--validation-mode",
                "invalid",
            ],
            input="n\n",  # Decline backlog-md install
        )

        assert result.exit_code == 1
        assert "Invalid --validation-mode" in result.output

    def test_per_transition_overrides_batch(
        self, mock_github_releases, tmp_path: Path
    ) -> None:
        """Test that per-transition flags override batch mode."""
        project_dir = tmp_path / "test-project"
        result = runner.invoke(
            app,
            [
                "init",
                str(project_dir),
                "--ai",
                "claude",
                "--no-git",
                "--ignore-agent-tools",
                "--validation-mode",
                "none",
                "--validation-plan",
                "pull-request",
            ],
            input="n\n",  # Decline backlog-md install
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"
        assert "Generated flowspec_workflow.yml" in result.output

        workflow_file = project_dir / "flowspec_workflow.yml"
        assert workflow_file.exists()
        content = workflow_file.read_text()

        # Plan should be PULL_REQUEST (override)
        assert "validation: PULL_REQUEST" in content
        # Others should still be NONE from batch
        assert "validation: NONE" in content

    def test_no_validation_prompts_takes_precedence(
        self, mock_github_releases, tmp_path: Path
    ) -> None:
        """Test --no-validation-prompts takes precedence over --validation-mode."""
        project_dir = tmp_path / "test-project"
        result = runner.invoke(
            app,
            [
                "init",
                str(project_dir),
                "--ai",
                "claude",
                "--no-git",
                "--ignore-agent-tools",
                "--no-validation-prompts",
                "--validation-mode",
                "pull-request",
            ],
            input="n\n",  # Decline backlog-md install
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"

        workflow_file = project_dir / "flowspec_workflow.yml"
        assert workflow_file.exists()
        content = workflow_file.read_text()
        # Should be all NONE due to --no-validation-prompts precedence
        assert content.count("validation: NONE") >= 7


class TestValidationModeInWorkflowFile:
    """Tests verifying validation modes are correctly written to workflow file."""

    def test_workflow_file_has_version(
        self, mock_github_releases, tmp_path: Path
    ) -> None:
        """Test that generated workflow file has version field."""
        project_dir = tmp_path / "test-project"
        result = runner.invoke(
            app,
            [
                "init",
                str(project_dir),
                "--ai",
                "claude",
                "--no-git",
                "--ignore-agent-tools",
                "--validation-mode",
                "none",
            ],
            input="n\n",  # Decline backlog-md install
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"

        workflow_file = project_dir / "flowspec_workflow.yml"
        content = workflow_file.read_text()
        assert 'version: "1.0"' in content

    def test_workflow_file_has_transitions_section(
        self, mock_github_releases, tmp_path: Path
    ) -> None:
        """Test that generated workflow file has transitions section."""
        project_dir = tmp_path / "test-project"
        result = runner.invoke(
            app,
            [
                "init",
                str(project_dir),
                "--ai",
                "claude",
                "--no-git",
                "--ignore-agent-tools",
                "--validation-mode",
                "none",
            ],
            input="n\n",  # Decline backlog-md install
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"

        workflow_file = project_dir / "flowspec_workflow.yml"
        content = workflow_file.read_text()
        assert "transitions:" in content

    def test_workflow_file_has_all_transitions(
        self, mock_github_releases, tmp_path: Path
    ) -> None:
        """Test that workflow file contains all standard transitions."""
        project_dir = tmp_path / "test-project"
        result = runner.invoke(
            app,
            [
                "init",
                str(project_dir),
                "--ai",
                "claude",
                "--no-git",
                "--ignore-agent-tools",
                "--validation-mode",
                "none",
            ],
            input="n\n",  # Decline backlog-md install
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"

        workflow_file = project_dir / "flowspec_workflow.yml"
        content = workflow_file.read_text()

        expected_transitions = [
            "assess",
            "specify",
            "research",
            "plan",
            "implement",
            "validate",
            "operate",
        ]
        for t in expected_transitions:
            assert f"name: {t}" in content, f"Missing transition {t}"
