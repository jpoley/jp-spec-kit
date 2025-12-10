"""Tests for upgrade commands (upgrade, upgrade-tools, upgrade-repo).

Tests cover:
- upgrade-tools command for CLI tool upgrades
- upgrade-repo command for repository template upgrades
- upgrade command as interactive dispatcher
- Version hint in version display
- Component upgrade helper functions
"""

import re
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from specify_cli import (
    UPGRADE_TOOLS_COMPONENTS,
    _get_installed_jp_spec_kit_version,
    _upgrade_backlog_md,
    _upgrade_jp_spec_kit,
    _upgrade_spec_kit,
    app,
)


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text."""
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_escape.sub("", text)


runner = CliRunner()


class TestUpgradeToolsComponents:
    """Tests for UPGRADE_TOOLS_COMPONENTS constant."""

    def test_contains_jp_spec_kit(self):
        """jp-spec-kit is a valid component."""
        assert "jp-spec-kit" in UPGRADE_TOOLS_COMPONENTS

    def test_contains_spec_kit(self):
        """spec-kit is a valid component."""
        assert "spec-kit" in UPGRADE_TOOLS_COMPONENTS

    def test_contains_backlog(self):
        """backlog is a valid component."""
        assert "backlog" in UPGRADE_TOOLS_COMPONENTS


class TestGetInstalledJpSpecKitVersion:
    """Tests for _get_installed_jp_spec_kit_version helper function."""

    def test_parses_version_from_specify_output(self):
        """Extracts version number from 'specify version' output."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "jp-spec-kit 0.2.317\nspec-kit 0.1.0\n"

        with patch("subprocess.run", return_value=mock_result):
            version = _get_installed_jp_spec_kit_version()
            assert version == "0.2.317"

    def test_returns_none_when_specify_not_found(self):
        """Returns None when specify binary is not installed."""
        with patch("subprocess.run", side_effect=FileNotFoundError()):
            version = _get_installed_jp_spec_kit_version()
            assert version is None

    def test_returns_none_on_command_failure(self):
        """Returns None when specify version command fails."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""

        with patch("subprocess.run", return_value=mock_result):
            version = _get_installed_jp_spec_kit_version()
            assert version is None


class TestUpgradeJpSpecKit:
    """Tests for _upgrade_jp_spec_kit helper function."""

    def test_already_at_latest_version(self):
        """Returns success when already at latest version."""
        with patch("specify_cli.__version__", "1.0.0"):
            with patch("specify_cli.get_github_latest_release", return_value="1.0.0"):
                success, message = _upgrade_jp_spec_kit(dry_run=False)
                assert success is True
                # Code returns "Already at version X" when current == target
                assert "Already at version" in message

    def test_dry_run_shows_would_upgrade(self):
        """Dry run shows what would be upgraded."""
        with patch("specify_cli.__version__", "1.0.0"):
            with patch("specify_cli.get_github_latest_release", return_value="2.0.0"):
                success, message = _upgrade_jp_spec_kit(dry_run=True)
                assert success is True
                # Code returns "Would install version X (current: Y)"
                assert "Would install" in message
                assert "1.0.0" in message
                assert "2.0.0" in message

    def test_handles_no_available_version(self):
        """Returns failure when available version cannot be determined."""
        with patch("specify_cli.__version__", "1.0.0"):
            with patch("specify_cli.get_github_latest_release", return_value=None):
                success, message = _upgrade_jp_spec_kit(dry_run=False)
                assert success is False
                assert "Could not determine latest version" in message

    def test_uv_upgrade_success_with_verification(self):
        """Successful uv tool upgrade verifies version changed."""
        with patch("specify_cli.__version__", "1.0.0"):
            with patch("specify_cli.get_github_latest_release", return_value="2.0.0"):
                mock_result = MagicMock()
                mock_result.returncode = 0
                with patch("subprocess.run", return_value=mock_result):
                    # Mock version verification to return new version
                    with patch(
                        "specify_cli._get_installed_jp_spec_kit_version",
                        return_value="2.0.0",
                    ):
                        success, message = _upgrade_jp_spec_kit(dry_run=False)
                        assert success is True
                        assert "Upgraded" in message
                        assert "2.0.0" in message

    def test_uv_upgrade_fallback_when_version_unchanged(self):
        """Falls back to git reinstall when uv upgrade returns 0 but version unchanged."""
        with patch("specify_cli.__version__", "1.0.0"):
            with patch("specify_cli.get_github_latest_release", return_value="2.0.0"):
                call_count = [0]

                def mock_subprocess_run(cmd, **kwargs):
                    call_count[0] += 1
                    result = MagicMock()
                    result.returncode = 0
                    return result

                with patch("subprocess.run", side_effect=mock_subprocess_run):
                    # First verify call returns old version, second returns new
                    version_calls = [0]

                    def mock_get_version():
                        version_calls[0] += 1
                        if version_calls[0] == 1:
                            return "1.0.0"  # First check - same as before
                        return "2.0.0"  # After git reinstall

                    with patch(
                        "specify_cli._get_installed_jp_spec_kit_version",
                        side_effect=mock_get_version,
                    ):
                        success, message = _upgrade_jp_spec_kit(dry_run=False)
                        assert success is True
                        # Should have tried both uv upgrade and git reinstall
                        assert call_count[0] >= 2

    def test_uv_not_found_fallback(self):
        """Falls back to reinstall when uv upgrade fails."""
        with patch("specify_cli.__version__", "1.0.0"):
            with patch("specify_cli.get_github_latest_release", return_value="2.0.0"):
                # First call (uv tool upgrade) raises FileNotFoundError
                # Second call (uv tool install) succeeds
                def mock_subprocess_run(cmd, **kwargs):
                    if "upgrade" in cmd:
                        raise FileNotFoundError()
                    result = MagicMock()
                    result.returncode = 0
                    return result

                with patch("subprocess.run", side_effect=mock_subprocess_run):
                    with patch(
                        "specify_cli._get_installed_jp_spec_kit_version",
                        return_value="2.0.0",
                    ):
                        success, message = _upgrade_jp_spec_kit(dry_run=False)
                        assert success is True
                        # Code returns "Installed version X (was: Y)"
                        assert "Installed" in message or "Upgraded" in message


class TestUpgradeBacklogMd:
    """Tests for _upgrade_backlog_md helper function."""

    def test_not_installed(self):
        """Returns failure when backlog-md not installed."""
        with patch("specify_cli.check_backlog_installed_version", return_value=None):
            success, message = _upgrade_backlog_md(dry_run=False)
            assert success is False
            assert "not installed" in message

    def test_already_at_latest_version(self):
        """Returns success when already at latest version."""
        with patch("specify_cli.check_backlog_installed_version", return_value="1.0.0"):
            with patch("specify_cli.get_npm_latest_version", return_value="1.0.0"):
                success, message = _upgrade_backlog_md(dry_run=False)
                assert success is True
                assert "Already at latest version" in message

    def test_dry_run_shows_would_upgrade(self):
        """Dry run shows what would be upgraded."""
        with patch("specify_cli.check_backlog_installed_version", return_value="1.0.0"):
            with patch("specify_cli.get_npm_latest_version", return_value="2.0.0"):
                success, message = _upgrade_backlog_md(dry_run=True)
                assert success is True
                assert "Would upgrade" in message

    def test_handles_no_available_version(self):
        """Returns failure when available version cannot be determined."""
        with patch("specify_cli.check_backlog_installed_version", return_value="1.0.0"):
            with patch("specify_cli.get_npm_latest_version", return_value=None):
                success, message = _upgrade_backlog_md(dry_run=False)
                assert success is False
                assert "Could not determine latest version" in message

    def test_no_package_manager(self):
        """Returns failure when no package manager found."""
        with patch("specify_cli.check_backlog_installed_version", return_value="1.0.0"):
            with patch("specify_cli.get_npm_latest_version", return_value="2.0.0"):
                with patch("specify_cli.detect_package_manager", return_value=None):
                    success, message = _upgrade_backlog_md(dry_run=False)
                    assert success is False
                    assert "No Node.js package manager" in message

    def test_package_manager_binary_removed(self):
        """Gracefully handles package manager binary removal after detection."""
        with patch("specify_cli.check_backlog_installed_version", return_value="1.0.0"):
            with patch("specify_cli.get_npm_latest_version", return_value="2.0.0"):
                with patch("specify_cli.detect_package_manager", return_value="npm"):
                    with patch("subprocess.run", side_effect=FileNotFoundError()):
                        success, message = _upgrade_backlog_md(dry_run=False)
                        assert success is False
                        assert "not found" in message.lower()
                        assert "npm" in message

    def test_uses_correct_package_name_npm(self):
        """Verifies npm install uses 'backlog.md' (with period, not hyphen)."""
        with patch("specify_cli.check_backlog_installed_version", return_value="1.0.0"):
            with patch("specify_cli.get_npm_latest_version", return_value="2.0.0"):
                with patch("specify_cli.detect_package_manager", return_value="npm"):
                    captured_cmd = []

                    def capture_cmd(cmd, **kwargs):
                        captured_cmd.extend(cmd)
                        result = MagicMock()
                        result.returncode = 0
                        return result

                    with patch("subprocess.run", side_effect=capture_cmd):
                        _upgrade_backlog_md(dry_run=False)
                        # Verify the package name uses period, not hyphen
                        cmd_str = " ".join(captured_cmd)
                        assert "backlog.md" in cmd_str
                        assert "backlog-md" not in cmd_str

    def test_uses_correct_package_name_pnpm(self):
        """Verifies pnpm add uses 'backlog.md' (with period, not hyphen)."""
        with patch("specify_cli.check_backlog_installed_version", return_value="1.0.0"):
            with patch("specify_cli.get_npm_latest_version", return_value="2.0.0"):
                with patch("specify_cli.detect_package_manager", return_value="pnpm"):
                    captured_cmd = []

                    def capture_cmd(cmd, **kwargs):
                        captured_cmd.extend(cmd)
                        result = MagicMock()
                        result.returncode = 0
                        return result

                    with patch("subprocess.run", side_effect=capture_cmd):
                        _upgrade_backlog_md(dry_run=False)
                        # Verify the package name uses period, not hyphen
                        cmd_str = " ".join(captured_cmd)
                        assert "backlog.md" in cmd_str
                        assert "backlog-md" not in cmd_str


class TestUpgradeSpecKit:
    """Tests for _upgrade_spec_kit helper function."""

    def test_already_at_latest_version(self):
        """Returns success when already at latest version."""
        with patch("specify_cli.get_spec_kit_installed_version", return_value="1.0.0"):
            with patch("specify_cli.get_github_latest_release", return_value="1.0.0"):
                success, message = _upgrade_spec_kit(dry_run=False)
                assert success is True
                assert "Already at latest version" in message

    def test_dry_run_shows_would_upgrade(self):
        """Dry run shows what would be upgraded."""
        with patch("specify_cli.get_spec_kit_installed_version", return_value="1.0.0"):
            with patch("specify_cli.get_github_latest_release", return_value="2.0.0"):
                success, message = _upgrade_spec_kit(dry_run=True)
                assert success is True
                assert "Would upgrade" in message
                assert "1.0.0" in message
                assert "2.0.0" in message

    def test_handles_no_available_version(self):
        """Returns failure when available version cannot be determined."""
        with patch("specify_cli.get_spec_kit_installed_version", return_value="1.0.0"):
            with patch("specify_cli.get_github_latest_release", return_value=None):
                success, message = _upgrade_spec_kit(dry_run=False)
                assert success is False
                assert "Could not determine latest spec-kit version" in message

    def test_reinstall_from_git_success(self):
        """Successful spec-kit upgrade via jp-spec-kit reinstall."""
        with patch("specify_cli.get_spec_kit_installed_version") as mock_installed:
            # Return old version first, then new version after install
            mock_installed.side_effect = ["1.0.0", "2.0.0"]
            with patch("specify_cli.get_github_latest_release", return_value="2.0.0"):
                mock_result = MagicMock()
                mock_result.returncode = 0
                with patch("subprocess.run", return_value=mock_result):
                    success, message = _upgrade_spec_kit(dry_run=False)
                    assert success is True
                    assert "Upgraded" in message

    def test_uv_not_found(self):
        """Returns failure when uv tool is not installed."""
        with patch("specify_cli.get_spec_kit_installed_version", return_value="1.0.0"):
            with patch("specify_cli.get_github_latest_release", return_value="2.0.0"):
                with patch("subprocess.run", side_effect=FileNotFoundError()):
                    success, message = _upgrade_spec_kit(dry_run=False)
                    assert success is False
                    assert "uv not found" in message


class TestUpgradeToolsCommand:
    """Tests for 'specify upgrade-tools' command."""

    def test_help_shows_correct_description(self):
        """Help text explains the command upgrades CLI tools."""
        result = runner.invoke(app, ["upgrade-tools", "--help"])
        assert result.exit_code == 0
        assert "CLI tools" in result.output
        assert "jp-spec-kit" in result.output
        assert "spec-kit" in result.output
        assert "backlog-md" in result.output

    def test_invalid_component_rejected(self):
        """Invalid component name is rejected."""
        with patch("specify_cli.show_banner"):
            result = runner.invoke(app, ["upgrade-tools", "-c", "invalid"])
            assert result.exit_code == 1
            assert "Unknown component" in result.output

    def test_dry_run_mode(self):
        """Dry run mode shows preview without making changes."""
        with patch("specify_cli.show_banner"):
            with patch("specify_cli.get_all_component_versions") as mock_versions:
                mock_versions.return_value = {
                    "jp_spec_kit": {"installed": "1.0.0", "available": "2.0.0"},
                    "spec_kit": {"installed": "1.0.0", "available": "2.0.0"},
                    "backlog_md": {"installed": "1.0.0", "available": "2.0.0"},
                }
                with patch(
                    "specify_cli._upgrade_jp_spec_kit",
                    return_value=(True, "Would upgrade"),
                ):
                    with patch(
                        "specify_cli._upgrade_spec_kit",
                        return_value=(True, "Would upgrade"),
                    ):
                        with patch(
                            "specify_cli._upgrade_backlog_md",
                            return_value=(True, "Would upgrade"),
                        ):
                            result = runner.invoke(app, ["upgrade-tools", "--dry-run"])
                            assert result.exit_code == 0
                            assert "DRY RUN" in result.output

    def test_single_component_upgrade(self):
        """Can upgrade a single component with -c flag."""
        with patch("specify_cli.show_banner"):
            with patch("specify_cli.get_all_component_versions") as mock_versions:
                mock_versions.return_value = {
                    "jp_spec_kit": {"installed": "1.0.0", "available": "2.0.0"},
                    "spec_kit": {"installed": "1.0.0", "available": "2.0.0"},
                    "backlog_md": {"installed": "1.0.0", "available": "2.0.0"},
                }
                with patch(
                    "specify_cli._upgrade_jp_spec_kit",
                    return_value=(True, "Already at latest"),
                ) as mock_jp:
                    with patch("specify_cli._upgrade_spec_kit") as mock_sk:
                        with patch("specify_cli._upgrade_backlog_md") as mock_bl:
                            result = runner.invoke(
                                app, ["upgrade-tools", "-c", "jp-spec-kit"]
                            )
                            assert result.exit_code == 0
                            mock_jp.assert_called_once()
                            mock_sk.assert_not_called()
                            mock_bl.assert_not_called()

    def test_spec_kit_component_upgrade(self):
        """Can upgrade spec-kit component with -c flag."""
        with patch("specify_cli.show_banner"):
            with patch("specify_cli.get_all_component_versions") as mock_versions:
                mock_versions.return_value = {
                    "jp_spec_kit": {"installed": "1.0.0", "available": "2.0.0"},
                    "spec_kit": {"installed": "1.0.0", "available": "2.0.0"},
                    "backlog_md": {"installed": "1.0.0", "available": "2.0.0"},
                }
                with patch("specify_cli._upgrade_jp_spec_kit") as mock_jp:
                    with patch(
                        "specify_cli._upgrade_spec_kit",
                        return_value=(True, "Upgraded"),
                    ) as mock_sk:
                        with patch("specify_cli._upgrade_backlog_md") as mock_bl:
                            result = runner.invoke(
                                app, ["upgrade-tools", "-c", "spec-kit"]
                            )
                            assert result.exit_code == 0
                            mock_jp.assert_not_called()
                            mock_sk.assert_called_once()
                            mock_bl.assert_not_called()


class TestUpgradeRepoCommand:
    """Tests for 'specify upgrade-repo' command."""

    def test_help_shows_correct_description(self):
        """Help text explains the command upgrades repository templates."""
        result = runner.invoke(app, ["upgrade-repo", "--help"])
        assert result.exit_code == 0
        assert "repository templates" in result.output.lower()
        assert "upgrade-tools" in result.output

    def test_source_repo_detection(self):
        """Detects jp-spec-kit source repository and blocks upgrade."""
        import os
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source repo marker
            marker_path = os.path.join(tmpdir, ".jp-spec-kit-source")
            with open(marker_path, "w") as f:
                f.write("")

            old_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                with patch("specify_cli.show_banner"):
                    result = runner.invoke(app, ["upgrade-repo"])
                    assert result.exit_code == 1
                    assert "Source Repository Detected" in result.output
            finally:
                os.chdir(old_cwd)


class TestUpgradeCommand:
    """Tests for 'specify upgrade' dispatcher command."""

    def test_help_shows_options(self):
        """Help text shows --tools, --repo, and --all options."""
        result = runner.invoke(app, ["upgrade", "--help"])
        assert result.exit_code == 0
        # Strip ANSI codes because Rich/Typer adds color codes that split option names
        output = strip_ansi(result.output)
        assert "--tools" in output
        assert "--repo" in output
        assert "--all" in output

    def test_tools_flag_delegates(self):
        """--tools flag delegates to upgrade-tools."""
        with patch("specify_cli.show_banner"):
            with patch("specify_cli._run_upgrade_tools") as mock_run:
                result = runner.invoke(app, ["upgrade", "--tools"])
                assert result.exit_code == 0
                mock_run.assert_called_once_with(dry_run=False)

    def test_repo_flag_delegates(self):
        """--repo flag delegates to upgrade-repo info."""
        with patch("specify_cli.show_banner"):
            with patch("specify_cli._run_upgrade_repo") as mock_run:
                result = runner.invoke(app, ["upgrade", "--repo"])
                assert result.exit_code == 0
                mock_run.assert_called_once_with(dry_run=False)

    def test_all_flag_calls_both(self):
        """--all flag calls both upgrade-tools and upgrade-repo."""
        with patch("specify_cli.show_banner"):
            with patch("specify_cli._run_upgrade_tools") as mock_tools:
                with patch("specify_cli._run_upgrade_repo") as mock_repo:
                    result = runner.invoke(app, ["upgrade", "--all"])
                    assert result.exit_code == 0
                    mock_tools.assert_called_once()
                    mock_repo.assert_called_once()

    def test_non_interactive_requires_flag(self):
        """Non-interactive mode requires explicit flag."""
        with patch("specify_cli.show_banner"):
            with patch("sys.stdin") as mock_stdin:
                mock_stdin.isatty.return_value = False
                result = runner.invoke(app, ["upgrade"])
                assert result.exit_code == 1
                assert "Non-interactive" in result.output


class TestVersionHint:
    """Tests for version upgrade hint in version display."""

    def test_version_hint_says_upgrade_tools(self):
        """Version hint points to upgrade-tools command."""
        with patch("specify_cli.get_all_component_versions") as mock_versions:
            mock_versions.return_value = {
                "jp_spec_kit": {"installed": "1.0.0", "available": "2.0.0"},
                "spec_kit": {"installed": "1.0.0", "available": "2.0.0"},
                "backlog_md": {"installed": "1.0.0", "available": "2.0.0"},
            }
            # version command (no --detail flag, it shows detailed by default)
            result = runner.invoke(app, ["version"])
            assert result.exit_code == 0
            assert "upgrade-tools" in result.output
            # Should NOT say just "upgrade" without specifying tools
            # This is the key fix - the hint should be accurate
