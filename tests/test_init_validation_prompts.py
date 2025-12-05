"""Tests for interactive validation mode prompts in specify init (AC1-4, AC8).

These tests verify:
- AC1: Add validation mode prompts to specify init command
- AC2: Support NONE selection (default, press Enter)
- AC3: Support KEYWORD selection with custom keyword input
- AC4: Support PULL_REQUEST selection
- AC8: Display summary of configured validation modes at end
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from specify_cli import (
    WORKFLOW_TRANSITIONS,
    display_validation_summary,
    prompt_validation_modes,
)

runner = CliRunner()


@pytest.fixture
def mock_github_releases(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """Mock the download_and_extract functions to avoid GitHub API calls.

    This fixture mocks the high-level download functions in specify_cli
    to create a minimal project structure without hitting the network.
    """

    def mock_download_two_stage(project_path, ai_assistants, script_type, is_current_dir=False, **kwargs):
        """Mock two-stage download - create minimal project structure."""
        tracker = kwargs.get("tracker")

        # Create the expected directory structure
        project_path.mkdir(parents=True, exist_ok=True)

        # Create .claude directories
        claude_dir = project_path / ".claude"
        claude_dir.mkdir(exist_ok=True)
        (claude_dir / "commands").mkdir(exist_ok=True)
        (claude_dir / "commands" / "jpspec").mkdir(exist_ok=True)
        (claude_dir / "commands" / "speckit").mkdir(exist_ok=True)
        (claude_dir / "skills").mkdir(exist_ok=True)

        # Create minimal placeholder files
        (claude_dir / "commands" / "jpspec" / "assess.md").write_text("# assess")
        (claude_dir / "commands" / "speckit" / "plan.md").write_text("# plan")
        (claude_dir / "skills" / "architect.md").write_text("# architect")

        # Create scripts directory
        scripts_dir = project_path / "scripts" / "bash"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        (scripts_dir / "placeholder.sh").write_text("#!/bin/bash\necho ok")

        # Create docs directory
        docs_dir = project_path / "docs"
        docs_dir.mkdir(exist_ok=True)
        (docs_dir / "placeholder.md").write_text("# docs")

        # Update tracker steps if tracker provided
        if tracker:
            tracker.complete("fetch-base", "mocked")
            tracker.complete("fetch-extension", "mocked")
            tracker.complete("extract-base", "mocked")
            tracker.complete("extract-extension", "mocked")
            tracker.complete("merge", "mocked")

        return project_path

    def mock_download_single(project_path, ai_assistants, script_type, **kwargs):
        """Mock single-stage download - same as two-stage."""
        tracker = kwargs.get("tracker")
        result = mock_download_two_stage(project_path, ai_assistants, script_type, **kwargs)
        if tracker:
            tracker.complete("fetch", "mocked")
            tracker.complete("download", "mocked")
            tracker.complete("extract", "mocked")
            tracker.complete("zip-list", "mocked")
            tracker.complete("extracted-summary", "mocked")
        return result

    monkeypatch.setattr(
        "specify_cli.download_and_extract_two_stage", mock_download_two_stage
    )
    monkeypatch.setattr(
        "specify_cli.download_and_extract_template", mock_download_single
    )


class TestPromptValidationModes:
    """Tests for the prompt_validation_modes() helper function."""

    def test_all_defaults_returns_all_none(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that pressing Enter for all prompts returns all NONE modes."""
        # Mock typer.prompt to return default "1" for mode and empty for keyword
        mock_prompt = MagicMock(side_effect=["1"] * 7)
        monkeypatch.setattr("specify_cli.typer.prompt", mock_prompt)

        result = prompt_validation_modes()

        assert len(result) == 7
        for mode in result.values():
            assert mode == "none"

    def test_keyword_selection_prompts_for_keyword(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that selecting KEYWORD (option 2) prompts for the keyword."""
        # Simulate: select KEYWORD for specify transition, then enter custom keyword
        prompt_responses = [
            "1",  # assess: NONE
            "1",  # specify: We'll override below
            "1",  # research: NONE
            "1",  # plan: NONE
            "1",  # implement: NONE
            "1",  # validate: NONE
            "1",  # operate: NONE
        ]
        prompt_responses[1] = "2"  # Change specify to KEYWORD

        # For KEYWORD, we need an additional prompt for the keyword value
        prompt_index = [0]

        def mock_prompt(message: str, default: str = "") -> str:
            idx = prompt_index[0]
            prompt_index[0] += 1

            # Return keyword when prompted for keyword
            if "keyword" in message.lower():
                return "PRD_APPROVED"

            # Return the choice for transition prompts
            if idx < len(prompt_responses):
                return prompt_responses[idx]
            return default

        monkeypatch.setattr("specify_cli.typer.prompt", mock_prompt)

        result = prompt_validation_modes()

        assert result["specify"] == 'KEYWORD["PRD_APPROVED"]'
        assert result["assess"] == "none"

    def test_pull_request_selection(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that selecting PULL_REQUEST (option 3) sets the correct mode."""
        # Select PULL_REQUEST for plan transition
        call_count = [0]

        def mock_prompt(message: str, default: str = "") -> str:
            call_count[0] += 1
            # Plan is the 4th transition
            if call_count[0] == 4:
                return "3"  # PULL_REQUEST
            return "1"  # NONE for others

        monkeypatch.setattr("specify_cli.typer.prompt", mock_prompt)

        result = prompt_validation_modes()

        assert result["plan"] == "pull-request"
        assert result["assess"] == "none"
        assert result["specify"] == "none"

    def test_invalid_choice_defaults_to_none(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that invalid choices default to NONE."""
        call_count = [0]

        def mock_prompt(message: str, default: str = "") -> str:
            call_count[0] += 1
            if call_count[0] == 1:
                return "invalid"
            return "1"

        monkeypatch.setattr("specify_cli.typer.prompt", mock_prompt)

        result = prompt_validation_modes()

        # First transition should be NONE due to invalid choice
        assert result["assess"] == "none"

    def test_empty_keyword_uses_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that empty keyword input uses APPROVED as default."""
        call_count = [0]

        def mock_prompt(message: str, default: str = "") -> str:
            call_count[0] += 1
            if call_count[0] == 1:
                return "2"  # KEYWORD for first transition
            if "keyword" in message.lower():
                return ""  # Empty keyword
            return "1"

        monkeypatch.setattr("specify_cli.typer.prompt", mock_prompt)

        result = prompt_validation_modes()

        assert result["assess"] == 'KEYWORD["APPROVED"]'

    def test_keyboard_interrupt_exits(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that Ctrl+C during prompts raises typer.Exit."""
        import typer

        def mock_prompt(message: str, default: str = "") -> str:
            raise KeyboardInterrupt()

        monkeypatch.setattr("specify_cli.typer.prompt", mock_prompt)

        with pytest.raises(typer.Exit):
            prompt_validation_modes()

    def test_all_transitions_covered(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that all 7 standard transitions are covered."""
        mock_prompt = MagicMock(return_value="1")
        monkeypatch.setattr("specify_cli.typer.prompt", mock_prompt)

        result = prompt_validation_modes()

        expected_transitions = {t["name"] for t in WORKFLOW_TRANSITIONS}
        assert set(result.keys()) == expected_transitions


class TestDisplayValidationSummary:
    """Tests for the display_validation_summary() helper function."""

    def test_empty_modes_shows_default_message(
        self, capsys: pytest.CaptureFixture
    ) -> None:
        """Test that empty modes dict shows default message."""
        with patch("specify_cli.console.print") as mock_print:
            display_validation_summary({})

            # Verify the default message was printed
            printed_calls = [str(call) for call in mock_print.call_args_list]
            assert any(
                "All transitions using NONE" in str(call) for call in printed_calls
            )

    def test_all_none_shows_default_message(self) -> None:
        """Test that all NONE modes shows default message."""
        modes = {
            "assess": "none",
            "specify": "none",
            "plan": "none",
        }

        with patch("specify_cli.console.print") as mock_print:
            display_validation_summary(modes)

            printed_calls = [str(call) for call in mock_print.call_args_list]
            assert any(
                "All transitions using NONE" in str(call) for call in printed_calls
            )

    def test_non_default_modes_displayed(self) -> None:
        """Test that non-default modes are displayed in summary."""
        modes = {
            "assess": "none",
            "specify": 'KEYWORD["PRD"]',
            "plan": "pull-request",
        }

        with patch("specify_cli.console.print") as mock_print:
            display_validation_summary(modes)

            printed_calls = [str(call) for call in mock_print.call_args_list]
            # Should show the custom modes
            all_output = " ".join(str(c) for c in printed_calls)
            assert "specify" in all_output
            assert "plan" in all_output

    def test_keyword_mode_uppercase_display(self) -> None:
        """Test that KEYWORD modes are displayed in uppercase."""
        modes = {"specify": 'keyword["test"]'}

        with patch("specify_cli.console.print") as mock_print:
            display_validation_summary(modes)

            printed_calls = [str(call) for call in mock_print.call_args_list]
            all_output = " ".join(str(c) for c in printed_calls)
            assert "KEYWORD" in all_output

    def test_pull_request_mode_formatted(self) -> None:
        """Test that pull-request mode is displayed as PULL_REQUEST."""
        modes = {"plan": "pull-request"}

        with patch("specify_cli.console.print") as mock_print:
            display_validation_summary(modes)

            printed_calls = [str(call) for call in mock_print.call_args_list]
            all_output = " ".join(str(c) for c in printed_calls)
            assert "PULL_REQUEST" in all_output


class TestInitInteractivePrompts:
    """Tests for interactive prompts during specify init."""

    def test_non_interactive_skips_prompts(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mock_github_releases
    ) -> None:
        """Test that non-interactive mode (no TTY) skips validation prompts."""
        from specify_cli import app

        # Mock stdin.isatty to return False
        monkeypatch.setattr("sys.stdin.isatty", lambda: False)
        monkeypatch.setattr("sys.stdout.isatty", lambda: False)

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
            ],
            input="n\n",  # Decline backlog-md install
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"
        # Should generate workflow file with defaults
        workflow_file = project_dir / "jpspec_workflow.yml"
        assert workflow_file.exists()
        content = workflow_file.read_text()
        # All should be NONE (default)
        assert content.count("validation: NONE") >= 7

    def test_no_validation_prompts_flag_skips_interactive(
        self, tmp_path: Path, mock_github_releases
    ) -> None:
        """Test that --no-validation-prompts skips interactive prompts."""
        from specify_cli import app

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
            ],
            input="n\n",  # Decline backlog-md install
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"
        workflow_file = project_dir / "jpspec_workflow.yml"
        assert workflow_file.exists()
        content = workflow_file.read_text()
        # All should be NONE
        assert content.count("validation: NONE") >= 7


class TestWorkflowTransitionsConstant:
    """Tests for WORKFLOW_TRANSITIONS constant."""

    def test_has_seven_transitions(self) -> None:
        """Test that WORKFLOW_TRANSITIONS has all 7 standard transitions."""
        assert len(WORKFLOW_TRANSITIONS) == 7

    def test_all_have_required_fields(self) -> None:
        """Test that all transitions have required fields."""
        required_fields = {"name", "from", "to", "default"}
        for t in WORKFLOW_TRANSITIONS:
            assert required_fields.issubset(t.keys()), f"Missing fields in {t}"

    def test_all_defaults_are_none(self) -> None:
        """Test that all default validation modes are NONE."""
        for t in WORKFLOW_TRANSITIONS:
            assert t["default"] == "NONE", f"Non-NONE default in {t['name']}"
