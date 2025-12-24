"""Tests for tool discovery module."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from flowspec_cli.security.adapters.discovery import ToolDiscovery


class TestToolDiscoveryInit:
    """Tests for ToolDiscovery initialization."""

    def test_initialization_default_cache(self):
        """Test initialization with default cache directory."""
        discovery = ToolDiscovery()

        expected = Path.home() / ".flowspec" / "tools"
        assert discovery.cache_dir == expected
        assert discovery.cache_dir.exists()

    def test_initialization_custom_cache(self, tmp_path):
        """Test initialization with custom cache directory."""
        custom_cache = tmp_path / "custom_cache"
        discovery = ToolDiscovery(cache_dir=custom_cache)

        assert discovery.cache_dir == custom_cache
        assert custom_cache.exists()

    def test_initialization_creates_cache_directory(self, tmp_path):
        """Test that cache directory is created if it doesn't exist."""
        cache_dir = tmp_path / "new" / "cache" / "dir"
        assert not cache_dir.exists()

        ToolDiscovery(cache_dir=cache_dir)

        assert cache_dir.exists()


class TestToolDiscoveryFindTool:
    """Tests for find_tool method."""

    def test_find_tool_in_system_path(self):
        """Test finding tool in system PATH."""
        discovery = ToolDiscovery()

        # Use 'python' which should always be available
        tool_path = discovery.find_tool("python")

        assert tool_path is not None
        assert tool_path.exists()

    def test_find_tool_not_found(self, tmp_path):
        """Test finding non-existent tool."""
        discovery = ToolDiscovery(cache_dir=tmp_path)

        with patch("shutil.which", return_value=None):
            tool_path = discovery.find_tool("nonexistent_tool_xyz")

        assert tool_path is None

    def test_find_tool_in_cache(self, tmp_path):
        """Test finding tool in cache directory."""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        tool_path = cache_dir / "mytool"
        tool_path.touch()

        discovery = ToolDiscovery(cache_dir=cache_dir)

        with patch("shutil.which", return_value=None):
            found_path = discovery.find_tool("mytool")

        assert found_path == tool_path

    def test_find_tool_in_venv(self, tmp_path):
        """Test finding tool in virtual environment."""
        # Create a mock venv structure
        venv_dir = tmp_path / ".venv"
        bin_dir = venv_dir / "bin"
        bin_dir.mkdir(parents=True)
        tool_path = bin_dir / "mytool"
        tool_path.touch()

        discovery = ToolDiscovery(cache_dir=tmp_path / "cache")

        with patch("shutil.which", return_value=None):
            with patch("pathlib.Path.cwd", return_value=tmp_path):
                found_path = discovery.find_tool("mytool")

        assert found_path == tool_path

    def test_find_tool_prefers_system_path(self, tmp_path):
        """Test that system PATH is checked before venv."""
        # Create tool in cache
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        cache_tool = cache_dir / "python"
        cache_tool.touch()

        discovery = ToolDiscovery(cache_dir=cache_dir)

        # Should find system python, not cache version
        tool_path = discovery.find_tool("python")

        assert tool_path is not None
        # System path should not be the cache path
        assert tool_path != cache_tool


class TestToolDiscoveryFindInVenv:
    """Tests for _find_in_venv method."""

    def test_find_in_venv_dotenv(self, tmp_path):
        """Test finding tool in .venv directory."""
        venv_dir = tmp_path / ".venv"
        bin_dir = venv_dir / "bin"
        bin_dir.mkdir(parents=True)
        tool_path = bin_dir / "mytool"
        tool_path.touch()

        discovery = ToolDiscovery()

        with patch("pathlib.Path.cwd", return_value=tmp_path):
            found_path = discovery._find_in_venv("mytool")

        assert found_path == tool_path

    def test_find_in_venv_regular_venv(self, tmp_path):
        """Test finding tool in venv directory."""
        venv_dir = tmp_path / "venv"
        bin_dir = venv_dir / "bin"
        bin_dir.mkdir(parents=True)
        tool_path = bin_dir / "mytool"
        tool_path.touch()

        discovery = ToolDiscovery()

        with patch("pathlib.Path.cwd", return_value=tmp_path):
            found_path = discovery._find_in_venv("mytool")

        assert found_path == tool_path

    def test_find_in_venv_windows_scripts(self, tmp_path):
        """Test finding tool in Scripts directory (Windows)."""
        venv_dir = tmp_path / ".venv"
        scripts_dir = venv_dir / "Scripts"
        scripts_dir.mkdir(parents=True)
        tool_path = scripts_dir / "mytool.exe"
        tool_path.touch()

        discovery = ToolDiscovery()

        with patch("pathlib.Path.cwd", return_value=tmp_path):
            found_path = discovery._find_in_venv("mytool.exe")

        assert found_path == tool_path

    def test_find_in_venv_not_found(self, tmp_path):
        """Test when tool is not in any venv."""
        discovery = ToolDiscovery()

        with patch("pathlib.Path.cwd", return_value=tmp_path):
            found_path = discovery._find_in_venv("nonexistent")

        assert found_path is None

    def test_find_in_venv_current_python_env(self, tmp_path):
        """Test finding tool in current Python environment via sys.prefix."""
        discovery = ToolDiscovery()

        # Create a fake current Python environment under tmp_path and point sys.prefix to it
        fake_prefix = tmp_path / "fake_prefix"
        bin_dir = fake_prefix / "bin"
        bin_dir.mkdir(parents=True)
        python_executable = bin_dir / "python3"
        python_executable.touch()

        # Patch both Path.cwd and sys.prefix so the function only checks our fake prefix
        fake_cwd = tmp_path / "fake_cwd"
        fake_cwd.mkdir()

        with (
            patch("pathlib.Path.cwd", return_value=fake_cwd),
            patch(
                "flowspec_cli.security.adapters.discovery.sys.prefix",
                str(fake_prefix),
            ),
            patch("shutil.which", return_value=None),
        ):
            # This test verifies that sys.prefix is checked
            found = discovery._find_in_venv("python3")

        assert found == python_executable


class TestToolDiscoveryEnsureAvailable:
    """Tests for ensure_available method."""

    def test_ensure_available_already_exists(self):
        """Test when tool is already available."""
        discovery = ToolDiscovery()

        tool_path = discovery.ensure_available("python", auto_install=False)

        assert tool_path is not None
        assert tool_path.exists()

    def test_ensure_available_not_found_no_install(self, tmp_path):
        """Test when tool not found and auto_install is False."""
        discovery = ToolDiscovery(cache_dir=tmp_path)

        with patch("shutil.which", return_value=None):
            tool_path = discovery.ensure_available("nonexistent", auto_install=False)

        assert tool_path is None

    def test_ensure_available_with_auto_install_success(self, tmp_path):
        """Test successful auto-installation."""
        discovery = ToolDiscovery(cache_dir=tmp_path)

        mock_tool_path = tmp_path / "installed_tool"
        mock_tool_path.touch()

        with patch.object(discovery, "find_tool") as mock_find:
            # First call: not found, second call: found after install
            mock_find.side_effect = [None, mock_tool_path]

            with patch.object(
                discovery, "_install_with_pip", return_value=mock_tool_path
            ):
                tool_path = discovery.ensure_available("mytool", auto_install=True)

        assert tool_path == mock_tool_path

    def test_ensure_available_with_auto_install_failure(self, tmp_path):
        """Test auto-installation failure."""
        discovery = ToolDiscovery(cache_dir=tmp_path)

        with patch.object(discovery, "find_tool", return_value=None):
            with patch.object(
                discovery, "_install_with_pip", side_effect=Exception("Install failed")
            ):
                with pytest.raises(RuntimeError, match="Failed to install mytool"):
                    discovery.ensure_available("mytool", auto_install=True)


class TestToolDiscoveryInstallWithPip:
    """Tests for _install_with_pip method."""

    def test_install_with_pip_success(self, tmp_path):
        """Test successful pip installation."""
        discovery = ToolDiscovery(cache_dir=tmp_path)

        mock_tool_path = tmp_path / "installed_tool"
        mock_tool_path.touch()

        with patch("subprocess.check_call"):
            with patch.object(discovery, "find_tool", return_value=mock_tool_path):
                result = discovery._install_with_pip("mytool")

        assert result == mock_tool_path

    def test_install_with_pip_subprocess_failure(self, tmp_path):
        """Test pip installation with subprocess error."""
        discovery = ToolDiscovery(cache_dir=tmp_path)

        mock_error = subprocess.CalledProcessError(
            returncode=1,
            cmd=["pip", "install", "mytool"],
            stderr=b"Error installing package",
        )

        with patch("subprocess.check_call", side_effect=mock_error):
            with pytest.raises(RuntimeError, match="pip install failed"):
                discovery._install_with_pip("mytool")

    def test_install_with_pip_tool_not_found_after_install(self, tmp_path):
        """Test when tool is not found after installation."""
        discovery = ToolDiscovery(cache_dir=tmp_path)

        with patch("subprocess.check_call"):
            with patch.object(discovery, "find_tool", return_value=None):
                with pytest.raises(
                    RuntimeError,
                    match="Installed mytool but could not locate executable",
                ):
                    discovery._install_with_pip("mytool")

    def test_install_with_pip_uses_current_python(self, tmp_path):
        """Test that installation uses current Python interpreter."""
        discovery = ToolDiscovery(cache_dir=tmp_path)

        mock_tool_path = tmp_path / "tool"
        mock_tool_path.touch()

        with patch("subprocess.check_call") as mock_check:
            with patch.object(discovery, "find_tool", return_value=mock_tool_path):
                discovery._install_with_pip("mytool")

        # Verify correct pip command
        mock_check.assert_called_once()
        args = mock_check.call_args[0][0]
        assert args[0] == sys.executable
        assert args[1:4] == ["-m", "pip", "install"]
        assert "mytool" in args


class TestToolDiscoveryIsAvailable:
    """Tests for is_available method."""

    def test_is_available_true(self):
        """Test when tool is available."""
        discovery = ToolDiscovery()

        assert discovery.is_available("python") is True

    def test_is_available_false(self, tmp_path):
        """Test when tool is not available."""
        discovery = ToolDiscovery(cache_dir=tmp_path)

        with patch("shutil.which", return_value=None):
            assert discovery.is_available("nonexistent_tool_xyz") is False

    def test_is_available_in_cache(self, tmp_path):
        """Test when tool is available in cache."""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        tool_path = cache_dir / "cached_tool"
        tool_path.touch()

        discovery = ToolDiscovery(cache_dir=cache_dir)

        with patch("shutil.which", return_value=None):
            assert discovery.is_available("cached_tool") is True


class TestToolDiscoveryEdgeCases:
    """Tests for edge cases and error handling."""

    def test_cache_dir_creation_with_nested_path(self, tmp_path):
        """Test cache directory creation with deeply nested path."""
        nested_cache = tmp_path / "a" / "b" / "c" / "d" / "cache"
        ToolDiscovery(cache_dir=nested_cache)

        assert nested_cache.exists()

    def test_find_tool_with_empty_string(self, tmp_path):
        """Test finding tool with empty string name.

        Note: Empty string can match directories (e.g., venv/bin/ + "" = venv/bin).
        This test verifies the function doesn't crash and returns a safe result.
        """
        discovery = ToolDiscovery(cache_dir=tmp_path)

        # Create isolated environment with no venv directories
        isolated_cwd = tmp_path / "isolated"
        isolated_cwd.mkdir()

        # Patch all paths that _find_in_venv checks
        with (
            patch("shutil.which", return_value=None),
            patch("pathlib.Path.cwd", return_value=isolated_cwd),
            patch(
                "flowspec_cli.security.adapters.discovery.sys.prefix",
                str(isolated_cwd),
            ),
        ):
            tool_path = discovery.find_tool("")

        # In isolated environment with no venv, empty string should return None
        assert tool_path is None

    def test_find_tool_cache_is_directory_not_file(self, tmp_path):
        """Test when cache entry is a directory, not a file."""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        tool_dir = cache_dir / "mytool"
        tool_dir.mkdir()  # Create as directory, not file

        discovery = ToolDiscovery(cache_dir=cache_dir)

        with patch("shutil.which", return_value=None):
            tool_path = discovery.find_tool("mytool")

        # Should not return directory as tool
        assert tool_path is None


class TestToolDiscoveryIntegration:
    """Integration tests for tool discovery."""

    def test_full_discovery_chain(self, tmp_path):
        """Test complete discovery chain: PATH -> venv -> cache."""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()

        # Create tool only in cache
        cache_tool = cache_dir / "special_tool"
        cache_tool.touch()

        discovery = ToolDiscovery(cache_dir=cache_dir)

        with patch("shutil.which", return_value=None):
            with patch("pathlib.Path.cwd", return_value=tmp_path):
                tool_path = discovery.find_tool("special_tool")

        # Should find in cache as last resort
        assert tool_path == cache_tool

    def test_venv_preference_over_cache(self, tmp_path):
        """Test that venv is preferred over cache."""
        # Create tool in both venv and cache
        venv_dir = tmp_path / ".venv"
        bin_dir = venv_dir / "bin"
        bin_dir.mkdir(parents=True)
        venv_tool = bin_dir / "mytool"
        venv_tool.touch()

        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        cache_tool = cache_dir / "mytool"
        cache_tool.touch()

        discovery = ToolDiscovery(cache_dir=cache_dir)

        with patch("shutil.which", return_value=None):
            with patch("pathlib.Path.cwd", return_value=tmp_path):
                tool_path = discovery.find_tool("mytool")

        # Should find in venv (higher priority than cache)
        assert tool_path == venv_tool
