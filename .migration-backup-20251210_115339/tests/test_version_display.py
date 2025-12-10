"""Tests for version detection and display functionality.

Tests cover:
- Version detection functions (get_github_latest_release, get_npm_latest_version)
- Spec-kit version detection (get_spec_kit_installed_version)
- Component versions aggregation (get_all_component_versions)
- Upgrade detection (_has_upgrade)
- CLI version command and --version flag
- Version info display (show_version_info)
"""

import json
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from specify_cli import (
    _has_upgrade,
    app,
    get_all_component_versions,
    get_github_latest_release,
    get_npm_latest_version,
    get_spec_kit_installed_version,
    show_version_info,
)

runner = CliRunner()


class TestGetGithubLatestRelease:
    """Tests for GitHub releases API version fetching."""

    def test_successful_release_fetch(self):
        """Successfully fetches latest release version from GitHub."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"tag_name": "v1.2.3"}

        with patch("specify_cli.client.get", return_value=mock_response):
            result = get_github_latest_release("owner", "repo")
            assert result == "1.2.3"

    def test_strips_v_prefix(self):
        """Strips 'v' prefix from version tags."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"tag_name": "v0.0.311"}

        with patch("specify_cli.client.get", return_value=mock_response):
            result = get_github_latest_release("jpoley", "jp-spec-kit")
            assert result == "0.0.311"

    def test_handles_version_without_prefix(self):
        """Handles version tags without 'v' prefix."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"tag_name": "1.0.0"}

        with patch("specify_cli.client.get", return_value=mock_response):
            result = get_github_latest_release("owner", "repo")
            assert result == "1.0.0"

    def test_returns_none_on_404(self):
        """Returns None when repo has no releases (404)."""
        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch("specify_cli.client.get", return_value=mock_response):
            result = get_github_latest_release("owner", "no-releases")
            assert result is None

    def test_returns_none_on_timeout(self):
        """Returns None on timeout without raising."""
        import httpx

        with patch("specify_cli.client.get", side_effect=httpx.TimeoutException("")):
            result = get_github_latest_release("owner", "repo")
            assert result is None

    def test_returns_none_on_network_error(self):
        """Returns None on network errors without raising."""
        import httpx

        with patch(
            "specify_cli.client.get", side_effect=httpx.HTTPError("Network error")
        ):
            result = get_github_latest_release("owner", "repo")
            assert result is None

    def test_returns_none_on_missing_tag_name(self):
        """Returns None when response lacks tag_name."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}

        with patch("specify_cli.client.get", return_value=mock_response):
            result = get_github_latest_release("owner", "repo")
            assert result is None

    def test_returns_none_on_invalid_json(self):
        """Returns None when response contains invalid JSON."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid", "", 0)

        with patch("specify_cli.client.get", return_value=mock_response):
            result = get_github_latest_release("owner", "repo")
            assert result is None


class TestGetNpmLatestVersion:
    """Tests for npm registry version fetching."""

    def test_successful_version_fetch(self):
        """Successfully fetches latest version from npm registry."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"version": "1.26.4"}

        with patch("specify_cli.client.get", return_value=mock_response):
            result = get_npm_latest_version("backlog.md")
            assert result == "1.26.4"

    def test_returns_none_on_404(self):
        """Returns None when package not found."""
        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch("specify_cli.client.get", return_value=mock_response):
            result = get_npm_latest_version("nonexistent-package")
            assert result is None

    def test_returns_none_on_timeout(self):
        """Returns None on timeout without raising."""
        import httpx

        with patch("specify_cli.client.get", side_effect=httpx.TimeoutException("")):
            result = get_npm_latest_version("backlog.md")
            assert result is None

    def test_returns_none_on_missing_version(self):
        """Returns None when response lacks version field."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"name": "package"}

        with patch("specify_cli.client.get", return_value=mock_response):
            result = get_npm_latest_version("package")
            assert result is None

    def test_returns_none_on_invalid_json(self):
        """Returns None when response contains invalid JSON."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid", "", 0)

        with patch("specify_cli.client.get", return_value=mock_response):
            result = get_npm_latest_version("backlog.md")
            assert result is None


class TestGetSpecKitInstalledVersion:
    """Tests for spec-kit version detection from compatibility matrix."""

    def test_returns_version_from_cwd_matrix(self, tmp_path, monkeypatch):
        """Reads version from current directory's compatibility matrix."""
        matrix_file = tmp_path / ".spec-kit-compatibility.yml"
        matrix_file.write_text("""
jp-spec-kit:
  compatible_with:
    spec-kit:
      tested: "0.0.25"
""")
        monkeypatch.chdir(tmp_path)

        result = get_spec_kit_installed_version()
        assert result == "0.0.25"

    def test_falls_back_to_default(self, tmp_path, monkeypatch):
        """Falls back to default version when no matrix found."""
        monkeypatch.chdir(tmp_path)

        # Mock load_compatibility_matrix to return empty
        with patch("specify_cli.load_compatibility_matrix", return_value={}):
            result = get_spec_kit_installed_version()
            # Default fallback version (updated from 0.0.20 to 0.0.90)
            assert result == "0.0.90"

    def test_returns_string_not_none(self, tmp_path, monkeypatch):
        """Always returns a string, never None."""
        monkeypatch.chdir(tmp_path)

        with patch("specify_cli.load_compatibility_matrix", return_value={}):
            result = get_spec_kit_installed_version()
            assert isinstance(result, str)


class TestHasUpgrade:
    """Tests for upgrade detection helper."""

    def test_detects_upgrade_available(self):
        """Returns True when available > installed."""
        versions = {"installed": "1.0.0", "available": "2.0.0"}
        assert _has_upgrade(versions) is True

    def test_no_upgrade_when_current(self):
        """Returns False when versions are equal."""
        versions = {"installed": "1.0.0", "available": "1.0.0"}
        assert _has_upgrade(versions) is False

    def test_no_upgrade_when_ahead(self):
        """Returns False when installed > available."""
        versions = {"installed": "2.0.0", "available": "1.0.0"}
        assert _has_upgrade(versions) is False

    def test_no_upgrade_when_available_none(self):
        """Returns False when available is None."""
        versions = {"installed": "1.0.0", "available": None}
        assert _has_upgrade(versions) is False

    def test_no_upgrade_when_installed_none(self):
        """Returns False when installed is None."""
        versions = {"installed": None, "available": "1.0.0"}
        assert _has_upgrade(versions) is False

    def test_handles_missing_keys(self):
        """Returns False when keys are missing."""
        assert _has_upgrade({}) is False
        assert _has_upgrade({"installed": "1.0.0"}) is False
        assert _has_upgrade({"available": "1.0.0"}) is False


class TestGetAllComponentVersions:
    """Tests for component version aggregation."""

    def test_returns_all_components(self):
        """Returns dict with all three component versions."""
        with (
            patch(
                "specify_cli.get_github_latest_release",
                side_effect=[
                    "0.0.311",
                    "0.0.90",
                ],
            ),
            patch("specify_cli.get_npm_latest_version", return_value="1.26.4"),
            patch("specify_cli.get_spec_kit_installed_version", return_value="0.0.20"),
            patch("specify_cli.check_backlog_installed_version", return_value="1.23.0"),
        ):
            result = get_all_component_versions()

            assert "jp_spec_kit" in result
            assert "spec_kit" in result
            assert "backlog_md" in result

            assert "installed" in result["jp_spec_kit"]
            assert "available" in result["jp_spec_kit"]

    def test_handles_missing_backlog(self):
        """Handles case when backlog is not installed."""
        with (
            patch("specify_cli.get_github_latest_release", return_value="1.0.0"),
            patch("specify_cli.get_npm_latest_version", return_value="1.26.4"),
            patch("specify_cli.get_spec_kit_installed_version", return_value="0.0.20"),
            patch("specify_cli.check_backlog_installed_version", return_value=None),
        ):
            result = get_all_component_versions()
            assert result["backlog_md"]["installed"] is None


class TestVersionCliCommand:
    """Tests for the version CLI command."""

    def test_version_command_shows_table(self):
        """'specify version' shows detailed version table."""
        with (
            patch("specify_cli.get_github_latest_release", return_value="1.0.0"),
            patch("specify_cli.get_npm_latest_version", return_value="1.26.4"),
            patch("specify_cli.get_spec_kit_installed_version", return_value="0.0.20"),
            patch("specify_cli.check_backlog_installed_version", return_value="1.23.0"),
        ):
            result = runner.invoke(app, ["version"])

            assert result.exit_code == 0
            assert "jp-spec-kit" in result.stdout
            assert "spec-kit" in result.stdout
            assert "backlog.md" in result.stdout

    def test_version_flag_shows_simple_version(self):
        """'specify --version' shows simple version string."""
        result = runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert "jp-spec-kit" in result.stdout

    def test_version_flag_short_form(self):
        """'specify -v' shows simple version string."""
        result = runner.invoke(app, ["-v"])

        assert result.exit_code == 0
        assert "jp-spec-kit" in result.stdout


class TestVersionUpgradeIndicators:
    """Tests for upgrade indicators in version display."""

    def test_shows_upgrade_indicator_when_available(self, capsys):
        """Shows ↑ indicator when upgrade available."""
        with (
            patch(
                "specify_cli.get_github_latest_release",
                side_effect=["99.0.0", "99.0.0"],
            ),
            patch("specify_cli.get_npm_latest_version", return_value="99.0.0"),
            patch("specify_cli.get_spec_kit_installed_version", return_value="0.0.20"),
            patch("specify_cli.check_backlog_installed_version", return_value="1.23.0"),
        ):
            show_version_info(detailed=True)
            captured = capsys.readouterr()
            assert "↑" in captured.out

    def test_shows_upgrade_hint_when_available(self, capsys):
        """Shows upgrade hint when updates available."""
        with (
            patch(
                "specify_cli.get_github_latest_release",
                side_effect=["99.0.0", "99.0.0"],
            ),
            patch("specify_cli.get_npm_latest_version", return_value="99.0.0"),
            patch("specify_cli.get_spec_kit_installed_version", return_value="0.0.20"),
            patch("specify_cli.check_backlog_installed_version", return_value="1.23.0"),
        ):
            show_version_info(detailed=True)
            captured = capsys.readouterr()
            assert "upgrade" in captured.out.lower()

    def test_no_upgrade_hint_when_current(self, capsys):
        """No upgrade hint when all versions current."""
        with (
            patch("specify_cli.get_github_latest_release", return_value=None),
            patch("specify_cli.get_npm_latest_version", return_value=None),
            patch("specify_cli.get_spec_kit_installed_version", return_value="0.0.20"),
            patch("specify_cli.check_backlog_installed_version", return_value="1.23.0"),
        ):
            show_version_info(detailed=True)
            captured = capsys.readouterr()
            assert "upgrade" not in captured.out.lower()
