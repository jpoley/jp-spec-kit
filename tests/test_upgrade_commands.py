"""Tests for upgrade commands (upgrade, upgrade-tools, upgrade-repo).

Tests cover:
- upgrade-tools command for CLI tool upgrades
- upgrade-repo command for repository template upgrades
- upgrade command as interactive dispatcher
- Version hint in version display
- Component upgrade helper functions
"""

import re
import subprocess
import sys
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from flowspec_cli import (
    _detect_duplicate_flowspec_installations,
    UPGRADE_TOOLS_COMPONENTS,
    _get_installed_jp_spec_kit_version,
    _run_npm_global_install,
    _upgrade_backlog_md,
    _upgrade_jp_spec_kit,
    _upgrade_spec_kit,
    _warn_duplicate_installations,
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
        """flowspec is a valid component."""
        assert "flowspec" in UPGRADE_TOOLS_COMPONENTS

    def test_contains_backlog(self):
        """backlog is a valid component."""
        assert "backlog" in UPGRADE_TOOLS_COMPONENTS

    def test_contains_beads(self):
        """beads is a valid component."""
        assert "beads" in UPGRADE_TOOLS_COMPONENTS


class TestRunNpmGlobalInstall:
    """Tests for _run_npm_global_install helper function."""

    def test_no_package_manager_available(self):
        """Returns failure when no package manager is available."""
        with patch("flowspec_cli.get_available_package_managers", return_value=[]):
            success, message, pkg_mgr = _run_npm_global_install("backlog.md", "1.0.0")
            assert success is False
            assert "No Node.js package manager" in message
            assert pkg_mgr is None

    def test_npm_success(self):
        """Successfully installs with npm."""
        with patch("flowspec_cli.get_available_package_managers", return_value=["npm"]):
            mock_result = MagicMock()
            mock_result.returncode = 0
            with patch("subprocess.run", return_value=mock_result):
                success, message, pkg_mgr = _run_npm_global_install(
                    "backlog.md", "1.0.0"
                )
                assert success is True
                assert "npm" in message
                assert pkg_mgr == "npm"

    def test_pnpm_success(self):
        """Successfully installs with pnpm."""
        with patch(
            "flowspec_cli.get_available_package_managers", return_value=["pnpm"]
        ):
            mock_result = MagicMock()
            mock_result.returncode = 0
            with patch("subprocess.run", return_value=mock_result):
                success, message, pkg_mgr = _run_npm_global_install(
                    "@beads/bd", "0.30.0"
                )
                assert success is True
                assert "pnpm" in message
                assert pkg_mgr == "pnpm"

    def test_fallback_pnpm_to_npm(self):
        """Falls back to npm when pnpm fails."""
        with patch(
            "flowspec_cli.get_available_package_managers", return_value=["pnpm", "npm"]
        ):
            call_count = [0]

            def mock_run(cmd, **kwargs):
                call_count[0] += 1
                if cmd[0] == "pnpm":
                    # pnpm fails - CalledProcessError uses output= for stdout
                    e = subprocess.CalledProcessError(
                        1, cmd, output="pnpm error message"
                    )
                    e.stderr = ""
                    raise e
                else:
                    # npm succeeds
                    result = MagicMock()
                    result.returncode = 0
                    return result

            with patch("subprocess.run", side_effect=mock_run):
                success, message, pkg_mgr = _run_npm_global_install(
                    "backlog.md", "1.0.0"
                )
                assert success is True
                assert call_count[0] == 2  # pnpm tried, then npm
                assert pkg_mgr == "npm"

    def test_all_package_managers_fail(self):
        """Returns failure with combined error when all package managers fail."""
        with patch(
            "flowspec_cli.get_available_package_managers", return_value=["pnpm", "npm"]
        ):

            def mock_run(cmd, **kwargs):
                if cmd[0] == "pnpm":
                    e = subprocess.CalledProcessError(
                        1, cmd, output="pnpm config error"
                    )
                    e.stderr = ""
                    raise e
                else:
                    e = subprocess.CalledProcessError(1, cmd, output="")
                    e.stderr = "npm network error"
                    raise e

            with patch("subprocess.run", side_effect=mock_run):
                success, message, pkg_mgr = _run_npm_global_install(
                    "backlog.md", "1.0.0"
                )
                assert success is False
                assert "pnpm" in message
                assert "npm" in message
                assert pkg_mgr is None

    def test_captures_stdout_when_stderr_empty(self):
        """Captures stdout when stderr is empty (pnpm writes errors to stdout)."""
        with patch(
            "flowspec_cli.get_available_package_managers", return_value=["pnpm"]
        ):

            def mock_run(cmd, **kwargs):
                e = subprocess.CalledProcessError(
                    1,
                    cmd,
                    output="ERR_PNPM_NO_GLOBAL_BIN_DIR: Unable to find global bin",
                )
                e.stderr = ""
                raise e

            with patch("subprocess.run", side_effect=mock_run):
                success, message, _ = _run_npm_global_install("backlog.md", "1.0.0")
                assert success is False
                assert "ERR_PNPM_NO_GLOBAL_BIN_DIR" in message

    def test_file_not_found_graceful(self):
        """Handles FileNotFoundError gracefully."""
        with patch("flowspec_cli.get_available_package_managers", return_value=["npm"]):
            with patch("subprocess.run", side_effect=FileNotFoundError()):
                success, message, _ = _run_npm_global_install("backlog.md", "1.0.0")
                assert success is False
                assert "not found" in message.lower()


class TestGetInstalledFlowspecKitVersion:
    """Tests for _get_installed_jp_spec_kit_version helper function."""

    def test_parses_version_from_specify_output(self):
        """Extracts version number from 'specify version' output."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "flowspec 0.2.317\nspec-kit 0.1.0\n"

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


class TestUpgradeFlowspecKit:
    """Tests for _upgrade_jp_spec_kit helper function."""

    def test_already_at_latest_version(self):
        """Returns success when already at latest version."""
        with patch("flowspec_cli.__version__", "1.0.0"):
            with patch("flowspec_cli.get_github_latest_release", return_value="1.0.0"):
                success, message = _upgrade_jp_spec_kit(dry_run=False)
                assert success is True
                # Code returns "Already at version X" when current == target
                assert "Already at version" in message

    def test_dry_run_shows_would_upgrade(self):
        """Dry run shows what would be upgraded."""
        with patch("flowspec_cli.__version__", "1.0.0"):
            with patch("flowspec_cli.get_github_latest_release", return_value="2.0.0"):
                success, message = _upgrade_jp_spec_kit(dry_run=True)
                assert success is True
                # Code returns "Would install version X (current: Y)"
                assert "Would install" in message
                assert "1.0.0" in message
                assert "2.0.0" in message

    def test_handles_no_available_version(self):
        """Returns failure when available version cannot be determined."""
        with patch("flowspec_cli.__version__", "1.0.0"):
            with patch("flowspec_cli.get_github_latest_release", return_value=None):
                success, message = _upgrade_jp_spec_kit(dry_run=False)
                assert success is False
                assert "Could not determine latest version" in message

    def test_uv_upgrade_success_with_verification(self):
        """Successful uv tool upgrade verifies version changed."""
        with patch("flowspec_cli.__version__", "1.0.0"):
            with patch("flowspec_cli.get_github_latest_release", return_value="2.0.0"):
                mock_result = MagicMock()
                mock_result.returncode = 0
                with patch("subprocess.run", return_value=mock_result):
                    # Mock version verification to return new version
                    with patch(
                        "flowspec_cli._get_installed_jp_spec_kit_version",
                        return_value="2.0.0",
                    ):
                        success, message = _upgrade_jp_spec_kit(dry_run=False)
                        assert success is True
                        assert "Upgraded" in message
                        assert "2.0.0" in message

    def test_uv_upgrade_fallback_when_version_unchanged(self):
        """Upgrades directly via git install (no longer tries uv upgrade first)."""
        with patch("flowspec_cli.__version__", "1.0.0"):
            with patch("flowspec_cli.get_github_latest_release", return_value="2.0.0"):
                call_count = [0]

                def mock_subprocess_run(cmd, **kwargs):
                    call_count[0] += 1
                    result = MagicMock()
                    result.returncode = 0
                    return result

                with patch("subprocess.run", side_effect=mock_subprocess_run):
                    success, message = _upgrade_jp_spec_kit(dry_run=False)
                    assert success is True
                    # Should only call git install once (no longer tries uv upgrade)
                    assert call_count[0] == 1
                    assert "Upgraded from 1.0.0 to 2.0.0" in message

    def test_uv_not_found_fallback(self):
        """Returns error when uv tool install fails with FileNotFoundError."""
        with patch("flowspec_cli.__version__", "1.0.0"):
            with patch("flowspec_cli.get_github_latest_release", return_value="2.0.0"):
                # uv tool install raises FileNotFoundError
                def mock_subprocess_run(cmd, **kwargs):
                    raise FileNotFoundError()

                with patch("subprocess.run", side_effect=mock_subprocess_run):
                    success, message = _upgrade_jp_spec_kit(dry_run=False)
                    assert success is False
                    assert "uv not found" in message


class TestUpgradeBacklogMd:
    """Tests for _upgrade_backlog_md helper function."""

    def test_not_installed_installs(self):
        """Installs backlog-md when not installed."""
        with patch("flowspec_cli.check_backlog_installed_version") as mock_check:
            # First call returns None (not installed), second returns version (after install)
            mock_check.side_effect = [None, "1.0.0"]
            with patch("flowspec_cli.get_npm_latest_version", return_value="1.0.0"):
                with patch("flowspec_cli.detect_package_manager", return_value="npm"):
                    with patch("subprocess.run") as mock_run:
                        mock_run.return_value = MagicMock(returncode=0)
                        success, message = _upgrade_backlog_md(dry_run=False)
                        assert success is True
                        assert "Installed" in message

    def test_already_at_latest_version(self):
        """Returns success when already at latest version."""
        with patch(
            "flowspec_cli.check_backlog_installed_version", return_value="1.0.0"
        ):
            with patch("flowspec_cli.get_npm_latest_version", return_value="1.0.0"):
                success, message = _upgrade_backlog_md(dry_run=False)
                assert success is True
                assert "Already at latest version" in message

    def test_dry_run_shows_would_upgrade(self):
        """Dry run shows what would be upgraded."""
        with patch(
            "flowspec_cli.check_backlog_installed_version", return_value="1.0.0"
        ):
            with patch("flowspec_cli.get_npm_latest_version", return_value="2.0.0"):
                success, message = _upgrade_backlog_md(dry_run=True)
                assert success is True
                assert "Would upgrade" in message

    def test_handles_no_available_version(self):
        """Returns failure when available version cannot be determined."""
        with patch(
            "flowspec_cli.check_backlog_installed_version", return_value="1.0.0"
        ):
            with patch("flowspec_cli.get_npm_latest_version", return_value=None):
                success, message = _upgrade_backlog_md(dry_run=False)
                assert success is False
                assert "Could not determine latest version" in message

    def test_no_package_manager(self):
        """Returns failure when no package manager found."""
        with patch(
            "flowspec_cli.check_backlog_installed_version", return_value="1.0.0"
        ):
            with patch("flowspec_cli.get_npm_latest_version", return_value="2.0.0"):
                with patch(
                    "flowspec_cli.get_available_package_managers", return_value=[]
                ):
                    success, message = _upgrade_backlog_md(dry_run=False)
                    assert success is False
                    assert "No Node.js package manager" in message

    def test_package_manager_binary_removed(self):
        """Gracefully handles package manager binary removal after detection."""
        with patch(
            "flowspec_cli.check_backlog_installed_version", return_value="1.0.0"
        ):
            with patch("flowspec_cli.get_npm_latest_version", return_value="2.0.0"):
                with patch(
                    "flowspec_cli.get_available_package_managers", return_value=["npm"]
                ):
                    with patch("subprocess.run", side_effect=FileNotFoundError()):
                        success, message = _upgrade_backlog_md(dry_run=False)
                        assert success is False
                        assert "not found" in message.lower()
                        assert "npm" in message

    def test_uses_correct_package_name_npm(self):
        """Verifies npm install uses 'backlog.md' (with period, not hyphen)."""
        with patch(
            "flowspec_cli.check_backlog_installed_version", return_value="1.0.0"
        ):
            with patch("flowspec_cli.get_npm_latest_version", return_value="2.0.0"):
                with patch(
                    "flowspec_cli.get_available_package_managers", return_value=["npm"]
                ):
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
        with patch(
            "flowspec_cli.check_backlog_installed_version", return_value="1.0.0"
        ):
            with patch("flowspec_cli.get_npm_latest_version", return_value="2.0.0"):
                with patch(
                    "flowspec_cli.get_available_package_managers", return_value=["pnpm"]
                ):
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
        with patch("flowspec_cli.get_spec_kit_installed_version", return_value="1.0.0"):
            with patch("flowspec_cli.get_github_latest_release", return_value="1.0.0"):
                success, message = _upgrade_spec_kit(dry_run=False)
                assert success is True
                assert "Already at latest version" in message

    def test_dry_run_shows_would_upgrade(self):
        """Dry run shows what would be upgraded."""
        with patch("flowspec_cli.get_spec_kit_installed_version", return_value="1.0.0"):
            with patch("flowspec_cli.get_github_latest_release", return_value="2.0.0"):
                success, message = _upgrade_spec_kit(dry_run=True)
                assert success is True
                assert "Would upgrade" in message
                assert "1.0.0" in message
                assert "2.0.0" in message

    def test_handles_no_available_version(self):
        """Returns failure when available version cannot be determined."""
        with patch("flowspec_cli.get_spec_kit_installed_version", return_value="1.0.0"):
            with patch("flowspec_cli.get_github_latest_release", return_value=None):
                success, message = _upgrade_spec_kit(dry_run=False)
                assert success is False
                assert "Could not determine latest spec-kit version" in message

    def test_reinstall_from_git_success(self):
        """Successful spec-kit upgrade via flowspec reinstall."""
        with patch("flowspec_cli.get_spec_kit_installed_version") as mock_installed:
            # Return old version first, then new version after install
            mock_installed.side_effect = ["1.0.0", "2.0.0"]
            with patch("flowspec_cli.get_github_latest_release", return_value="2.0.0"):
                mock_result = MagicMock()
                mock_result.returncode = 0
                with patch("subprocess.run", return_value=mock_result):
                    success, message = _upgrade_spec_kit(dry_run=False)
                    assert success is True
                    assert "Upgraded" in message

    def test_uv_not_found(self):
        """Returns failure when uv tool is not installed."""
        with patch("flowspec_cli.get_spec_kit_installed_version", return_value="1.0.0"):
            with patch("flowspec_cli.get_github_latest_release", return_value="2.0.0"):
                with patch("subprocess.run", side_effect=FileNotFoundError()):
                    success, message = _upgrade_spec_kit(dry_run=False)
                    assert success is False
                    assert "uv not found" in message


class TestUpgradeToolsCommand:
    """Tests for 'flowspec upgrade-tools' command."""

    def test_help_shows_correct_description(self):
        """Help text explains the command manages CLI tools."""
        result = runner.invoke(app, ["upgrade-tools", "--help"])
        assert result.exit_code == 0
        assert "CLI tools" in result.output
        assert "flowspec" in result.output
        assert "backlog-md" in result.output
        assert "beads" in result.output

    def test_invalid_component_rejected(self):
        """Invalid component name is rejected."""
        with patch("flowspec_cli.show_banner"):
            result = runner.invoke(app, ["upgrade-tools", "-c", "invalid"])
            assert result.exit_code == 1
            assert "Unknown component" in result.output

    def test_dry_run_mode(self):
        """Dry run mode shows preview without making changes."""
        with patch("flowspec_cli.show_banner"):
            with patch("flowspec_cli.get_all_component_versions") as mock_versions:
                mock_versions.return_value = {
                    "jp_spec_kit": {"installed": "1.0.0", "available": "2.0.0"},
                    "spec_kit": {"installed": "1.0.0", "available": "2.0.0"},
                    "backlog_md": {"installed": "1.0.0", "available": "2.0.0"},
                    "beads": {"installed": "1.0.0", "available": "2.0.0"},
                }
                with patch(
                    "flowspec_cli._upgrade_jp_spec_kit",
                    return_value=(True, "Would upgrade"),
                ):
                    with patch(
                        "flowspec_cli._upgrade_backlog_md",
                        return_value=(True, "Would upgrade"),
                    ):
                        with patch(
                            "flowspec_cli._upgrade_beads",
                            return_value=(True, "Would upgrade"),
                        ):
                            result = runner.invoke(app, ["upgrade-tools", "--dry-run"])
                            assert result.exit_code == 0
                            assert "DRY RUN" in result.output

    def test_single_component_upgrade(self):
        """Can upgrade a single component with -c flag."""
        with patch("flowspec_cli.show_banner"):
            with patch("flowspec_cli.get_all_component_versions") as mock_versions:
                mock_versions.return_value = {
                    "jp_spec_kit": {"installed": "1.0.0", "available": "2.0.0"},
                    "spec_kit": {"installed": "1.0.0", "available": "2.0.0"},
                    "backlog_md": {"installed": "1.0.0", "available": "2.0.0"},
                    "beads": {"installed": "1.0.0", "available": "2.0.0"},
                }
                with patch(
                    "flowspec_cli._upgrade_jp_spec_kit",
                    return_value=(True, "Already at latest"),
                ) as mock_jp:
                    with patch("flowspec_cli._upgrade_backlog_md") as mock_bl:
                        with patch("flowspec_cli._upgrade_beads") as mock_bd:
                            result = runner.invoke(
                                app, ["upgrade-tools", "-c", "flowspec"]
                            )
                            assert result.exit_code == 0
                            mock_jp.assert_called_once()
                            mock_bl.assert_not_called()
                            mock_bd.assert_not_called()

    def test_beads_component_upgrade(self):
        """Can upgrade beads component with -c flag."""
        with patch("flowspec_cli.show_banner"):
            with patch("flowspec_cli.get_all_component_versions") as mock_versions:
                mock_versions.return_value = {
                    "jp_spec_kit": {"installed": "1.0.0", "available": "2.0.0"},
                    "spec_kit": {"installed": "1.0.0", "available": "2.0.0"},
                    "backlog_md": {"installed": "1.0.0", "available": "2.0.0"},
                    "beads": {"installed": "1.0.0", "available": "2.0.0"},
                }
                with patch("flowspec_cli._upgrade_jp_spec_kit") as mock_jp:
                    with patch("flowspec_cli._upgrade_backlog_md") as mock_bl:
                        with patch(
                            "flowspec_cli._upgrade_beads",
                            return_value=(True, "Upgraded"),
                        ) as mock_bd:
                            result = runner.invoke(
                                app, ["upgrade-tools", "-c", "beads"]
                            )
                            assert result.exit_code == 0
                            mock_jp.assert_not_called()
                            mock_bl.assert_not_called()
                            mock_bd.assert_called_once()


class TestUpgradeRepoCommand:
    """Tests for 'flowspec upgrade-repo' command."""

    def test_help_shows_correct_description(self):
        """Help text explains the command upgrades repository templates."""
        result = runner.invoke(app, ["upgrade-repo", "--help"])
        assert result.exit_code == 0
        assert "repository templates" in result.output.lower()
        assert "upgrade-tools" in result.output

    def test_source_repo_detection(self):
        """Detects flowspec source repository and blocks upgrade."""
        import os
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source repo marker
            marker_path = os.path.join(tmpdir, ".flowspec-source")
            with open(marker_path, "w") as f:
                f.write("")

            old_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                with patch("flowspec_cli.show_banner"):
                    result = runner.invoke(app, ["upgrade-repo"])
                    assert result.exit_code == 1
                    assert "Source Repository Detected" in result.output
            finally:
                os.chdir(old_cwd)


class TestUpgradeCommand:
    """Tests for 'flowspec upgrade' dispatcher command."""

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
        with patch("flowspec_cli.show_banner"):
            with patch("flowspec_cli._run_upgrade_tools") as mock_run:
                result = runner.invoke(app, ["upgrade", "--tools"])
                assert result.exit_code == 0
                mock_run.assert_called_once_with(dry_run=False)

    def test_repo_flag_delegates(self):
        """--repo flag delegates to upgrade-repo info."""
        with patch("flowspec_cli.show_banner"):
            with patch("flowspec_cli._run_upgrade_repo") as mock_run:
                result = runner.invoke(app, ["upgrade", "--repo"])
                assert result.exit_code == 0
                mock_run.assert_called_once_with(dry_run=False)

    def test_all_flag_calls_both(self):
        """--all flag calls both upgrade-tools and upgrade-repo."""
        with patch("flowspec_cli.show_banner"):
            with patch("flowspec_cli._run_upgrade_tools") as mock_tools:
                with patch("flowspec_cli._run_upgrade_repo") as mock_repo:
                    result = runner.invoke(app, ["upgrade", "--all"])
                    assert result.exit_code == 0
                    mock_tools.assert_called_once()
                    mock_repo.assert_called_once()

    def test_non_interactive_requires_flag(self):
        """Non-interactive mode requires explicit flag."""
        with patch("flowspec_cli.show_banner"):
            with patch("sys.stdin") as mock_stdin:
                mock_stdin.isatty.return_value = False
                result = runner.invoke(app, ["upgrade"])
                assert result.exit_code == 1
                assert "Non-interactive" in result.output


class TestVersionHint:
    """Tests for version upgrade hint in version display."""

    def test_version_hint_says_upgrade_tools(self):
        """Version hint points to upgrade-tools command."""
        with patch("flowspec_cli.get_all_component_versions") as mock_versions:
            mock_versions.return_value = {
                "jp_spec_kit": {"installed": "1.0.0", "available": "2.0.0"},
                "backlog_md": {"installed": "1.0.0", "available": "2.0.0"},
                "beads": {"installed": "1.0.0", "available": "2.0.0"},
            }
            # version command (no --detail flag, it shows detailed by default)
            result = runner.invoke(app, ["version"])
            assert result.exit_code == 0
            assert "upgrade-tools" in result.output
            # Should NOT say just "upgrade" without specifying tools
            # This is the key fix - the hint should be accurate


class TestVersionTrackingFile:
    """Tests for .flowspec/.version tracking file functions."""

    def test_write_creates_version_file(self, tmp_path):
        """write_version_tracking_file creates .flowspec/.version file."""
        # Import here to avoid top-level circular import issues
        from flowspec_cli import write_version_tracking_file

        write_version_tracking_file(
            tmp_path,
            flowspec_version="1.0.0",
            backlog_version="2.0.0",
            beads_version="3.0.0",
            is_upgrade=False,
        )

        version_file = tmp_path / ".flowspec" / ".version"
        assert version_file.exists()
        content = version_file.read_text()
        assert "[versions]" in content
        assert 'flowspec = "1.0.0"' in content
        assert 'backlog = "2.0.0"' in content
        assert 'beads = "3.0.0"' in content
        assert "[metadata]" in content
        assert "installed_at" in content

    def test_read_returns_parsed_data(self, tmp_path):
        """read_version_tracking_file returns parsed TOML data."""
        from flowspec_cli import read_version_tracking_file, write_version_tracking_file

        # Use explicit empty string to exclude beads (None triggers auto-detect)
        with patch("flowspec_cli.check_beads_installed_version", return_value=None):
            write_version_tracking_file(
                tmp_path,
                flowspec_version="1.0.0",
                backlog_version="2.0.0",
                beads_version=None,
                is_upgrade=False,
            )

        result = read_version_tracking_file(tmp_path)
        assert result is not None
        assert result["versions"]["flowspec"] == "1.0.0"
        assert result["versions"]["backlog"] == "2.0.0"
        assert (
            "beads" not in result["versions"]
        )  # Not included when auto-detect returns None
        assert "installed_at" in result["metadata"]

    def test_read_returns_none_for_missing_file(self, tmp_path):
        """read_version_tracking_file returns None when file doesn't exist."""
        from flowspec_cli import read_version_tracking_file

        result = read_version_tracking_file(tmp_path)
        assert result is None

    def test_upgrade_preserves_installed_at(self, tmp_path):
        """Upgrade preserves installed_at and adds upgraded_at."""
        from flowspec_cli import read_version_tracking_file, write_version_tracking_file

        # Initial install
        write_version_tracking_file(
            tmp_path,
            flowspec_version="1.0.0",
            backlog_version=None,
            beads_version=None,
            is_upgrade=False,
        )

        initial = read_version_tracking_file(tmp_path)
        original_installed_at = initial["metadata"]["installed_at"]

        # Upgrade
        write_version_tracking_file(
            tmp_path,
            flowspec_version="2.0.0",
            backlog_version=None,
            beads_version=None,
            is_upgrade=True,
        )

        upgraded = read_version_tracking_file(tmp_path)
        assert upgraded["versions"]["flowspec"] == "2.0.0"
        assert upgraded["metadata"]["installed_at"] == original_installed_at
        assert "upgraded_at" in upgraded["metadata"]
        assert upgraded["metadata"]["upgraded_at"] != original_installed_at

    def test_upgrade_sets_installed_at_if_missing(self, tmp_path):
        """Upgrade sets installed_at if not present (pre-existing repo)."""
        from flowspec_cli import read_version_tracking_file, write_version_tracking_file

        # Manually create version file without metadata section
        flowspec_dir = tmp_path / ".flowspec"
        flowspec_dir.mkdir(parents=True)
        version_file = flowspec_dir / ".version"
        version_file.write_text('[versions]\nflowspec = "1.0.0"\n\n[metadata]\n')

        # Upgrade should set installed_at since it's missing
        write_version_tracking_file(
            tmp_path,
            flowspec_version="2.0.0",
            backlog_version=None,
            beads_version=None,
            is_upgrade=True,
        )

        result = read_version_tracking_file(tmp_path)
        assert "installed_at" in result["metadata"]
        assert "upgraded_at" in result["metadata"]

    def test_timestamps_are_utc(self, tmp_path):
        """Timestamps should be UTC timezone-aware."""
        from flowspec_cli import read_version_tracking_file, write_version_tracking_file

        write_version_tracking_file(
            tmp_path,
            flowspec_version="1.0.0",
            backlog_version=None,
            beads_version=None,
            is_upgrade=False,
        )

        result = read_version_tracking_file(tmp_path)
        # UTC ISO format includes +00:00 or Z suffix
        installed_at = result["metadata"]["installed_at"]
        assert "+00:00" in installed_at or installed_at.endswith("Z")

    def test_read_handles_invalid_toml(self, tmp_path):
        """read_version_tracking_file returns None for invalid TOML."""
        from flowspec_cli import read_version_tracking_file

        flowspec_dir = tmp_path / ".flowspec"
        flowspec_dir.mkdir(parents=True)
        version_file = flowspec_dir / ".version"
        version_file.write_text("this is not valid TOML { broken")

        result = read_version_tracking_file(tmp_path)
        assert result is None

    @pytest.mark.skipif(
        sys.platform == "win32",
        reason="Unix file permissions not supported on Windows",
    )
    def test_write_error_does_not_raise(self, tmp_path):
        """write_version_tracking_file doesn't raise on write errors."""
        from flowspec_cli import write_version_tracking_file

        # Create read-only directory to cause write error
        flowspec_dir = tmp_path / ".flowspec"
        flowspec_dir.mkdir(parents=True, mode=0o444)

        # Should not raise, just log warning
        try:
            write_version_tracking_file(
                tmp_path,
                flowspec_version="1.0.0",
                backlog_version=None,
                beads_version=None,
                is_upgrade=False,
            )
        finally:
            # Restore permissions for cleanup
            flowspec_dir.chmod(0o755)


class TestDuplicateInstallationDetection:
    """Tests for duplicate flowspec installation detection."""

    def test_single_uv_installation_no_warning(self, tmp_path, monkeypatch):
        """No warning when only uv installation exists."""
        # Create fake uv installation
        uv_bin = tmp_path / ".local" / "bin"
        uv_bin.mkdir(parents=True)
        flowspec_bin = uv_bin / "flowspec"
        flowspec_bin.touch()

        monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
        monkeypatch.setenv("UV_TOOL_BIN_DIR", "")
        monkeypatch.setattr("shutil.which", lambda x: None)
        monkeypatch.setattr(
            "subprocess.run",
            lambda *args, **kwargs: MagicMock(returncode=1, stdout=""),
        )

        installations = _detect_duplicate_flowspec_installations()
        assert len(installations) == 1
        assert installations[0][1] == "uv"

    def test_no_installations_empty_list(self, tmp_path, monkeypatch):
        """Returns empty list when no flowspec installations found."""
        # Use empty tmp_path as home - no flowspec binary exists
        monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
        monkeypatch.setenv("UV_TOOL_BIN_DIR", "")
        monkeypatch.setattr("shutil.which", lambda x: None)
        monkeypatch.setattr(
            "subprocess.run",
            lambda *args, **kwargs: MagicMock(returncode=1, stdout=""),
        )

        installations = _detect_duplicate_flowspec_installations()
        assert len(installations) == 0

    def test_respects_uv_tool_bin_dir_env_var(self, tmp_path, monkeypatch):
        """Checks UV_TOOL_BIN_DIR environment variable for uv installation."""
        custom_bin = tmp_path / "custom" / "bin"
        custom_bin.mkdir(parents=True)
        flowspec_bin = custom_bin / "flowspec"
        flowspec_bin.touch()

        monkeypatch.setenv("UV_TOOL_BIN_DIR", str(custom_bin))
        monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path / "empty")
        monkeypatch.setattr("shutil.which", lambda x: None)
        monkeypatch.setattr(
            "subprocess.run",
            lambda *args, **kwargs: MagicMock(returncode=1, stdout=""),
        )

        installations = _detect_duplicate_flowspec_installations()
        assert len(installations) == 1
        assert str(custom_bin) in installations[0][0]
        assert installations[0][1] == "uv"

    def test_pyenv_not_installed_no_error(self, tmp_path, monkeypatch):
        """Handles pyenv not being installed gracefully."""
        monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
        monkeypatch.setenv("UV_TOOL_BIN_DIR", "")
        monkeypatch.setattr("shutil.which", lambda x: None)

        def mock_run(*args, **kwargs):
            if args[0] == ["pyenv", "which", "flowspec"]:
                raise FileNotFoundError("pyenv not found")
            return MagicMock(returncode=1, stdout="")

        monkeypatch.setattr("subprocess.run", mock_run)

        # Should not raise
        installations = _detect_duplicate_flowspec_installations()
        assert isinstance(installations, list)

    def test_duplicate_detection_with_pyenv(self, tmp_path, monkeypatch):
        """Detects both uv and pyenv installations."""
        # Create fake uv installation
        uv_bin = tmp_path / ".local" / "bin"
        uv_bin.mkdir(parents=True)
        (uv_bin / "flowspec").touch()

        pyenv_path = "/Users/test/.pyenv/versions/3.11.0/bin/flowspec"

        monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
        monkeypatch.setenv("UV_TOOL_BIN_DIR", "")
        monkeypatch.setattr("shutil.which", lambda x: None)

        def mock_run(*args, **kwargs):
            if args[0] == ["pyenv", "which", "flowspec"]:
                return MagicMock(returncode=0, stdout=pyenv_path)
            return MagicMock(returncode=1, stdout="")

        monkeypatch.setattr("subprocess.run", mock_run)

        installations = _detect_duplicate_flowspec_installations()
        assert len(installations) == 2
        sources = {inst[1] for inst in installations}
        assert "uv" in sources
        assert "pip/pyenv" in sources

    def test_warn_duplicate_returns_false_single_install(self, monkeypatch):
        """_warn_duplicate_installations returns False for single installation."""
        monkeypatch.setattr(
            "flowspec_cli._detect_duplicate_flowspec_installations",
            lambda: [("/path/to/flowspec", "uv")],
        )
        result = _warn_duplicate_installations()
        assert result is False

    def test_warn_duplicate_returns_true_multiple_installs(self, monkeypatch, capsys):
        """_warn_duplicate_installations returns True and prints warning."""
        monkeypatch.setattr(
            "flowspec_cli._detect_duplicate_flowspec_installations",
            lambda: [
                ("/path/uv/flowspec", "uv"),
                ("/path/pyenv/flowspec", "pip/pyenv"),
            ],
        )
        result = _warn_duplicate_installations()
        assert result is True

    def test_shutil_which_used_for_path_detection(self, tmp_path, monkeypatch):
        """Uses shutil.which for cross-platform PATH detection."""
        monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
        monkeypatch.setenv("UV_TOOL_BIN_DIR", "")

        which_called = []

        def mock_which(name):
            which_called.append(name)
            return "/usr/local/bin/flowspec"

        monkeypatch.setattr("shutil.which", mock_which)
        monkeypatch.setattr(
            "subprocess.run",
            lambda *args, **kwargs: MagicMock(returncode=1, stdout=""),
        )

        _detect_duplicate_flowspec_installations()
        assert "flowspec" in which_called

    def test_pyenv_shim_path_excluded(self, tmp_path, monkeypatch):
        """Pyenv shim paths are excluded from PATH detection to avoid duplicates."""
        monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
        monkeypatch.setenv("UV_TOOL_BIN_DIR", "")

        # shutil.which returns a pyenv shim path
        monkeypatch.setattr(
            "shutil.which", lambda x: "/Users/test/.pyenv/shims/flowspec"
        )

        def mock_run(*args, **kwargs):
            if args[0] == ["pyenv", "which", "flowspec"]:
                # pyenv resolves shim to actual path
                return MagicMock(
                    returncode=0,
                    stdout="/Users/test/.pyenv/versions/3.11.0/bin/flowspec",
                )
            return MagicMock(returncode=1, stdout="")

        monkeypatch.setattr("subprocess.run", mock_run)

        installations = _detect_duplicate_flowspec_installations()
        # Should only have the resolved pyenv path, not the shim
        paths = [inst[0] for inst in installations]
        assert "/Users/test/.pyenv/shims/flowspec" not in paths
        # Verify the resolved pyenv path is properly detected
        assert "/Users/test/.pyenv/versions/3.11.0/bin/flowspec" in paths
