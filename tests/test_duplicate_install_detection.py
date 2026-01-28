"""Tests for duplicate flowspec installation detection.

Tests cover:
- Detection of multiple flowspec installations
- Warning behavior when duplicates found
- UV_TOOL_BIN_DIR environment variable handling
- Pyenv shim path handling
"""

from unittest.mock import MagicMock

from flowspec_cli import (
    _detect_duplicate_flowspec_installations,
    _warn_duplicate_installations,
)


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
        monkeypatch.setattr("flowspec_cli.shutil.which", lambda x: None)
        monkeypatch.setattr(
            "flowspec_cli.subprocess.run",
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
        monkeypatch.setattr("flowspec_cli.shutil.which", lambda x: None)
        monkeypatch.setattr(
            "flowspec_cli.subprocess.run",
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
        monkeypatch.setattr("flowspec_cli.shutil.which", lambda x: None)
        monkeypatch.setattr(
            "flowspec_cli.subprocess.run",
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
        monkeypatch.setattr("flowspec_cli.shutil.which", lambda x: None)

        def mock_run(*args, **kwargs):
            if args[0] == ["pyenv", "which", "flowspec"]:
                raise FileNotFoundError("pyenv not found")
            return MagicMock(returncode=1, stdout="")

        monkeypatch.setattr("flowspec_cli.subprocess.run", mock_run)

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
        monkeypatch.setattr("flowspec_cli.shutil.which", lambda x: None)

        def mock_run(*args, **kwargs):
            if args[0] == ["pyenv", "which", "flowspec"]:
                return MagicMock(returncode=0, stdout=pyenv_path)
            return MagicMock(returncode=1, stdout="")

        monkeypatch.setattr("flowspec_cli.subprocess.run", mock_run)

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

        monkeypatch.setattr("flowspec_cli.shutil.which", mock_which)
        monkeypatch.setattr(
            "flowspec_cli.subprocess.run",
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
            "flowspec_cli.shutil.which", lambda x: "/Users/test/.pyenv/shims/flowspec"
        )

        def mock_run(*args, **kwargs):
            if args[0] == ["pyenv", "which", "flowspec"]:
                # pyenv resolves shim to actual path
                return MagicMock(
                    returncode=0,
                    stdout="/Users/test/.pyenv/versions/3.11.0/bin/flowspec",
                )
            return MagicMock(returncode=1, stdout="")

        monkeypatch.setattr("flowspec_cli.subprocess.run", mock_run)

        installations = _detect_duplicate_flowspec_installations()
        # Should only have the resolved pyenv path, not the shim
        paths = [inst[0] for inst in installations]
        assert "/Users/test/.pyenv/shims/flowspec" not in paths
        # Verify the resolved pyenv path is properly detected
        assert "/Users/test/.pyenv/versions/3.11.0/bin/flowspec" in paths
