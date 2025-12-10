"""Tests for specify config validation command (AC9).

These tests verify AC9: Support reconfiguration via `specify config validation`.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from specify_cli import app

runner = CliRunner()


@pytest.fixture
def workflow_content() -> str:
    """Return sample workflow YAML content."""
    return """# JPSpec Workflow Configuration
version: "1.0"

transitions:
  - name: assess
    from: "To Do"
    to: "Assessed"
    validation: NONE

  - name: research
    from: "Assessed"
    to: "Researched"
    validation: NONE

  - name: specify
    from: "Researched"
    to: "Specified"
    validation: NONE

  - name: plan
    from: "Specified"
    to: "Planned"
    validation: NONE

  - name: implement
    from: "Planned"
    to: "Implemented"
    validation: NONE

  - name: validate
    from: "Implemented"
    to: "Validated"
    validation: NONE

  - name: operate
    from: "Validated"
    to: "Operated"
    validation: NONE
"""


@pytest.fixture
def initialized_project(
    tmp_path: Path, workflow_content: str, monkeypatch: pytest.MonkeyPatch
) -> Path:
    """Create a temp directory with jpspec_workflow.yml and chdir to it."""
    workflow_file = tmp_path / "jpspec_workflow.yml"
    workflow_file.write_text(workflow_content)
    monkeypatch.chdir(tmp_path)
    return tmp_path


class TestConfigValidationShow:
    """Tests for specify config validation --show."""

    def test_show_displays_config(self, initialized_project: Path) -> None:
        """Test --show displays current configuration."""
        result = runner.invoke(app, ["config", "validation", "--show"])
        assert result.exit_code == 0
        assert "Validation Configuration" in result.output
        assert "assess" in result.output
        assert "plan" in result.output

    def test_show_no_workflow_file(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test error when no jpspec_workflow.yml exists."""
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["config", "validation", "--show"])
        assert result.exit_code == 1
        assert "No jpspec_workflow.yml" in result.output


class TestConfigValidationDefaultBehavior:
    """Tests for default behavior (no flags)."""

    def test_default_shows_config(self, initialized_project: Path) -> None:
        """Test default behavior shows configuration."""
        result = runner.invoke(app, ["config", "validation"])
        assert result.exit_code == 0
        assert "Validation Configuration" in result.output


class TestConfigValidationSingleUpdate:
    """Tests for updating single transition."""

    def test_update_single_transition_none(self, initialized_project: Path) -> None:
        """Test updating single transition to NONE."""
        result = runner.invoke(
            app, ["config", "validation", "-t", "plan", "-m", "none"]
        )
        assert result.exit_code == 0
        assert "Updated" in result.output

    def test_update_single_transition_keyword(self, initialized_project: Path) -> None:
        """Test updating single transition to KEYWORD with custom keyword."""
        result = runner.invoke(
            app,
            ["config", "validation", "-t", "specify", "-m", "keyword", "-k", "LGTM"],
        )
        assert result.exit_code == 0
        workflow = (initialized_project / "jpspec_workflow.yml").read_text()
        assert 'KEYWORD["LGTM"]' in workflow

    def test_update_single_transition_keyword_default(
        self, initialized_project: Path
    ) -> None:
        """Test updating single transition to KEYWORD uses default keyword."""
        result = runner.invoke(
            app, ["config", "validation", "-t", "specify", "-m", "keyword"]
        )
        assert result.exit_code == 0
        workflow = (initialized_project / "jpspec_workflow.yml").read_text()
        assert 'KEYWORD["APPROVED"]' in workflow

    def test_update_single_transition_pull_request(
        self, initialized_project: Path
    ) -> None:
        """Test updating single transition to PULL_REQUEST."""
        result = runner.invoke(
            app, ["config", "validation", "-t", "plan", "-m", "pull-request"]
        )
        assert result.exit_code == 0
        workflow = (initialized_project / "jpspec_workflow.yml").read_text()
        assert "PULL_REQUEST" in workflow

    def test_update_invalid_transition(self, initialized_project: Path) -> None:
        """Test error for invalid transition name."""
        result = runner.invoke(
            app, ["config", "validation", "-t", "invalid", "-m", "none"]
        )
        assert result.exit_code == 1
        assert "Unknown transition" in result.output

    def test_update_invalid_mode(self, initialized_project: Path) -> None:
        """Test error for invalid mode."""
        result = runner.invoke(
            app, ["config", "validation", "-t", "plan", "-m", "invalid"]
        )
        assert result.exit_code == 1
        assert "Invalid mode" in result.output

    def test_transition_without_mode(self, initialized_project: Path) -> None:
        """Test error when --transition without --mode."""
        result = runner.invoke(app, ["config", "validation", "-t", "plan"])
        assert result.exit_code == 1
        assert "--mode is required" in result.output

    def test_mode_without_transition(self, initialized_project: Path) -> None:
        """Test error when --mode without --transition."""
        result = runner.invoke(app, ["config", "validation", "-m", "none"])
        assert result.exit_code == 1
        assert "--transition is required" in result.output


class TestConfigValidationColorOutput:
    """Tests for colored output based on validation mode."""

    def test_none_mode_shows_in_output(self, initialized_project: Path) -> None:
        """Test NONE mode is displayed in output."""
        result = runner.invoke(app, ["config", "validation", "--show"])
        assert result.exit_code == 0
        assert "NONE" in result.output

    def test_keyword_mode_shows_in_output(self, initialized_project: Path) -> None:
        """Test KEYWORD mode is displayed after update."""
        # First update to KEYWORD
        runner.invoke(
            app, ["config", "validation", "-t", "plan", "-m", "keyword", "-k", "TEST"]
        )
        result = runner.invoke(app, ["config", "validation", "--show"])
        assert result.exit_code == 0
        assert "KEYWORD" in result.output

    def test_pull_request_mode_shows_in_output(self, initialized_project: Path) -> None:
        """Test PULL_REQUEST mode is displayed after update."""
        # First update to PULL_REQUEST
        runner.invoke(app, ["config", "validation", "-t", "plan", "-m", "pull-request"])
        result = runner.invoke(app, ["config", "validation", "--show"])
        assert result.exit_code == 0
        assert "PULL_REQUEST" in result.output


class TestConfigValidationPreservesOtherTransitions:
    """Tests ensuring updates don't affect other transitions."""

    def test_update_preserves_other_transitions(
        self, initialized_project: Path
    ) -> None:
        """Test that updating one transition doesn't change others."""
        # Update plan to PULL_REQUEST
        runner.invoke(app, ["config", "validation", "-t", "plan", "-m", "pull-request"])

        # Verify plan changed
        workflow = (initialized_project / "jpspec_workflow.yml").read_text()
        assert "validation: PULL_REQUEST" in workflow

        # Verify other transitions still NONE
        assert workflow.count("validation: NONE") >= 6

    def test_multiple_updates_preserved(self, initialized_project: Path) -> None:
        """Test that multiple sequential updates are preserved."""
        # Update plan to PULL_REQUEST
        runner.invoke(app, ["config", "validation", "-t", "plan", "-m", "pull-request"])
        # Update specify to KEYWORD
        runner.invoke(
            app, ["config", "validation", "-t", "specify", "-m", "keyword", "-k", "OK"]
        )

        workflow = (initialized_project / "jpspec_workflow.yml").read_text()
        assert "PULL_REQUEST" in workflow
        assert 'KEYWORD["OK"]' in workflow
