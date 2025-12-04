"""Tests for ToolManager class."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from specify_cli.security.tools.manager import ToolManager, VERSION_PATTERN
from specify_cli.security.tools.models import (
    InstallMethod,
    ToolConfig,
    ToolStatus,
)


class TestToolManagerInit:
    """Test ToolManager initialization."""

    def test_default_cache_dir(self, tmp_path):
        """Default cache directory is in home directory."""
        with patch.object(Path, "home", return_value=tmp_path):
            manager = ToolManager(cache_dir=tmp_path / "tools")
            assert manager.cache_dir == tmp_path / "tools"

    def test_custom_cache_dir(self, tmp_path):
        """Can specify custom cache directory."""
        cache_dir = tmp_path / "custom_cache"
        manager = ToolManager(cache_dir=cache_dir)
        assert manager.cache_dir == cache_dir
        assert cache_dir.exists()

    def test_offline_mode(self, tmp_path):
        """Offline mode flag is stored."""
        manager = ToolManager(cache_dir=tmp_path, offline_mode=True)
        assert manager.offline_mode is True

    def test_custom_tool_configs(self, tmp_path):
        """Can provide custom tool configurations."""
        custom_configs = {"mytool": ToolConfig(name="mytool", version="1.0")}
        manager = ToolManager(cache_dir=tmp_path, tool_configs=custom_configs)
        assert "mytool" in manager.tool_configs
        assert "semgrep" not in manager.tool_configs

    def test_default_tool_configs(self, tmp_path):
        """Uses default tool configs when none provided."""
        manager = ToolManager(cache_dir=tmp_path)
        assert "semgrep" in manager.tool_configs
        assert "codeql" in manager.tool_configs
        assert "bandit" in manager.tool_configs


class TestIsAvailable:
    """Test is_available method."""

    def test_available_when_found(self, tmp_path):
        """Returns True when tool is found."""
        manager = ToolManager(cache_dir=tmp_path)
        with patch.object(manager, "_find_tool", return_value=Path("/usr/bin/semgrep")):
            assert manager.is_available("semgrep") is True

    def test_not_available_when_not_found(self, tmp_path):
        """Returns False when tool is not found."""
        manager = ToolManager(cache_dir=tmp_path)
        with patch.object(manager, "_find_tool", return_value=None):
            assert manager.is_available("nonexistent") is False


class TestGetToolInfo:
    """Test get_tool_info method."""

    def test_returns_none_when_not_found(self, tmp_path):
        """Returns None when tool is not installed."""
        manager = ToolManager(cache_dir=tmp_path)
        with patch.object(manager, "_find_tool", return_value=None):
            assert manager.get_tool_info("nonexistent") is None

    def test_returns_tool_info_when_found(self, tmp_path):
        """Returns ToolInfo when tool is installed."""
        manager = ToolManager(cache_dir=tmp_path)
        tool_path = Path("/usr/bin/semgrep")

        with (
            patch.object(manager, "_find_tool", return_value=tool_path),
            patch.object(manager, "_get_tool_version", return_value="1.45.0"),
            patch.object(manager, "_get_size_mb", return_value=100.0),
        ):
            info = manager.get_tool_info("semgrep")
            assert info is not None
            assert info.name == "semgrep"
            assert info.version == "1.45.0"
            assert info.path == tool_path


class TestInstall:
    """Test install method."""

    def test_unknown_tool_returns_error(self, tmp_path):
        """Unknown tool returns error result."""
        manager = ToolManager(cache_dir=tmp_path)
        result = manager.install("unknowntool")
        assert result.success is False
        assert "Unknown tool" in result.error_message

    def test_already_installed_returns_existing(self, tmp_path):
        """Already installed tool returns existing info."""
        manager = ToolManager(cache_dir=tmp_path)
        tool_path = Path("/usr/bin/semgrep")

        with (
            patch.object(manager, "_find_tool", return_value=tool_path),
            patch.object(manager, "_get_tool_version", return_value="1.45.0"),
            patch.object(manager, "_get_size_mb", return_value=100.0),
        ):
            result = manager.install("semgrep")
            assert result.success is True
            assert result.tool_info is not None

    def test_license_required_without_acceptance(self, tmp_path):
        """CodeQL requires license acceptance."""
        manager = ToolManager(cache_dir=tmp_path)
        with patch.object(manager, "_find_tool", return_value=None):
            result = manager.install("codeql", accept_license=False)
            assert result.success is False
            assert result.license_required is True

    def test_force_reinstall(self, tmp_path):
        """Force flag triggers reinstallation."""
        manager = ToolManager(cache_dir=tmp_path)
        tool_path = Path("/usr/bin/semgrep")

        with (
            patch.object(manager, "_find_tool", return_value=tool_path),
            patch.object(manager, "_get_tool_version", return_value="1.45.0"),
            patch.object(manager, "_get_size_mb", return_value=100.0),
            patch.object(manager, "_install_pip") as mock_pip,
        ):
            mock_pip.return_value = MagicMock(success=True)
            manager.install("semgrep", force=True)
            mock_pip.assert_called_once()


class TestOfflineMode:
    """Test offline mode behavior."""

    def test_offline_uses_cache_only(self, tmp_path):
        """Offline mode only uses cached tools.

        FIX #3: Proper mocking for offline mode test.
        """
        # Create a fake cached executable
        cache_dir = tmp_path / "tools"
        tool_cache = cache_dir / "semgrep" / "1.45.0"
        tool_cache.mkdir(parents=True)
        cached_exe = tool_cache / "semgrep"
        cached_exe.write_text("#!/bin/bash\necho test")
        cached_exe.chmod(0o755)

        manager = ToolManager(cache_dir=cache_dir, offline_mode=True)

        # Mock _find_in_cache to return our cached executable
        with patch.object(manager, "_find_in_cache", return_value=cached_exe):
            result = manager.install("semgrep")
            assert result.success is True
            assert result.tool_info.status == ToolStatus.OFFLINE_ONLY

    def test_offline_fails_when_not_cached(self, tmp_path):
        """Offline mode fails when tool is not in cache."""
        manager = ToolManager(cache_dir=tmp_path, offline_mode=True)

        with patch.object(manager, "_find_in_cache", return_value=None):
            result = manager.install("semgrep")
            assert result.success is False
            assert "Offline mode" in result.error_message


class TestVersionValidation:
    """Test version validation."""

    def test_valid_semantic_versions(self, tmp_path):
        """Valid semantic versions are accepted."""
        manager = ToolManager(cache_dir=tmp_path)
        valid_versions = [
            "1.0.0",
            "1.45.0",
            "2.15.0",
            "1.0",
            "1.0.0-beta1",
            "1.0.0-rc.1",
        ]
        for version in valid_versions:
            assert manager._is_valid_version(version), f"Should accept: {version}"

    def test_invalid_versions(self, tmp_path):
        """Invalid versions are rejected."""
        manager = ToolManager(cache_dir=tmp_path)
        invalid_versions = ["", "abc", "version", "...", "v", "1.2.3.4.5"]
        for version in invalid_versions:
            assert not manager._is_valid_version(version), f"Should reject: {version}"

    def test_version_with_v_prefix(self, tmp_path):
        """Versions with 'v' prefix are valid."""
        manager = ToolManager(cache_dir=tmp_path)
        assert manager._is_valid_version("v1.0.0")
        assert manager._is_valid_version("v2.15.0")


class TestVersionParsing:
    """Test version parsing from tool output."""

    def test_version_pattern_matches(self):
        """VERSION_PATTERN extracts versions correctly."""
        test_cases = [
            ("semgrep 1.45.0", "1.45.0"),
            ("v2.15.0", "2.15.0"),
            ("tool version 1.0.0-beta1", "1.0.0-beta1"),
            ("1.0", "1.0"),
            ("Version: 3.2.1", "3.2.1"),
        ]
        for output, expected in test_cases:
            match = VERSION_PATTERN.search(output)
            assert match is not None, f"Should match: {output}"
            assert match.group(1) == expected, f"For '{output}': expected {expected}"

    def test_get_tool_version_parses_output(self, tmp_path):
        """_get_tool_version correctly parses subprocess output."""
        manager = ToolManager(cache_dir=tmp_path)
        tool_path = tmp_path / "test_tool"
        tool_path.write_text("#!/bin/bash\necho 'test 1.2.3'")
        tool_path.chmod(0o755)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="semgrep 1.45.0\n", stderr="")
            version = manager._get_tool_version("semgrep", tool_path)
            assert version == "1.45.0"

    def test_get_tool_version_unknown_on_failure(self, tmp_path):
        """Returns 'unknown' when version cannot be determined."""
        manager = ToolManager(cache_dir=tmp_path)
        with patch("subprocess.run", side_effect=Exception("error")):
            version = manager._get_tool_version("test", Path("/nonexistent"))
            assert version == "unknown"


class TestCacheInfo:
    """Test cache information retrieval."""

    def test_empty_cache_info(self, tmp_path):
        """Returns zero counts for empty cache."""
        manager = ToolManager(cache_dir=tmp_path)
        info = manager.get_cache_info()
        assert info.total_size_mb == 0.0
        assert info.tool_count == 0
        assert info.size_warning is False

    def test_cache_with_tools(self, tmp_path):
        """Returns correct info for cached tools."""
        # Create fake cached tool
        tool_dir = tmp_path / "semgrep"
        tool_dir.mkdir()
        (tool_dir / "test_file").write_bytes(b"x" * 1024)

        manager = ToolManager(cache_dir=tmp_path)
        info = manager.get_cache_info()
        assert info.tool_count == 1
        assert info.total_size_mb > 0

    def test_cache_size_warning(self, tmp_path):
        """Size warning triggered at threshold."""
        manager = ToolManager(cache_dir=tmp_path)
        # Mock _get_size_mb to return large value
        with patch.object(manager, "_get_size_mb", return_value=600.0):
            tool_dir = tmp_path / "large_tool"
            tool_dir.mkdir()
            info = manager.get_cache_info()
            assert info.size_warning is True

    def test_cache_info_handles_permission_error(self, tmp_path):
        """Handles permission errors gracefully."""
        manager = ToolManager(cache_dir=tmp_path)

        # Create a directory we can't read
        bad_dir = tmp_path / "unreadable"
        bad_dir.mkdir()

        with patch.object(Path, "iterdir", side_effect=PermissionError("denied")):
            info = manager.get_cache_info()
            assert info.tool_count == 0


class TestFindInDirectory:
    """Test directory search for executables."""

    def test_finds_executable_at_root(self, tmp_path):
        """Finds executable at directory root."""
        exe = tmp_path / "mytool"
        exe.write_text("#!/bin/bash\necho test")
        exe.chmod(0o755)

        manager = ToolManager(cache_dir=tmp_path)
        result = manager._find_in_directory(tmp_path, "mytool")
        assert result == exe

    def test_finds_executable_in_subdirectory(self, tmp_path):
        """Finds executable in subdirectory."""
        subdir = tmp_path / "bin"
        subdir.mkdir()
        exe = subdir / "mytool"
        exe.write_text("#!/bin/bash\necho test")
        exe.chmod(0o755)

        manager = ToolManager(cache_dir=tmp_path)
        result = manager._find_in_directory(tmp_path, "mytool")
        assert result == exe

    def test_respects_max_depth(self, tmp_path):
        """Stops searching at max depth."""
        # Create deeply nested executable
        deep_dir = tmp_path / "a" / "b" / "c" / "d" / "e" / "f"
        deep_dir.mkdir(parents=True)
        exe = deep_dir / "mytool"
        exe.write_text("#!/bin/bash\necho test")
        exe.chmod(0o755)

        manager = ToolManager(cache_dir=tmp_path)
        # With max_depth=2, should not find it
        result = manager._find_in_directory(tmp_path, "mytool", max_depth=2)
        assert result is None

    def test_finds_windows_exe(self, tmp_path):
        """Finds .exe extension on Windows."""
        exe = tmp_path / "mytool.exe"
        exe.write_text("test")

        manager = ToolManager(cache_dir=tmp_path)
        result = manager._find_in_directory(tmp_path, "mytool")
        assert result == exe


class TestGetSizeMb:
    """Test size calculation."""

    def test_file_size(self, tmp_path):
        """Calculates file size correctly."""
        test_file = tmp_path / "test.bin"
        test_file.write_bytes(b"x" * (1024 * 1024))  # 1 MB

        manager = ToolManager(cache_dir=tmp_path)
        size = manager._get_size_mb(test_file)
        assert abs(size - 1.0) < 0.01

    def test_directory_size(self, tmp_path):
        """Calculates directory size correctly."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "file1.bin").write_bytes(b"x" * (512 * 1024))  # 0.5 MB
        (subdir / "file2.bin").write_bytes(b"x" * (512 * 1024))  # 0.5 MB

        manager = ToolManager(cache_dir=tmp_path)
        size = manager._get_size_mb(tmp_path)
        assert abs(size - 1.0) < 0.01


class TestPlatformKey:
    """Test platform detection."""

    def test_linux_platform(self, tmp_path):
        """Returns 'linux' for Linux systems."""
        manager = ToolManager(cache_dir=tmp_path)
        with patch("platform.system", return_value="Linux"):
            assert manager._get_platform_key() == "linux"

    def test_macos_platform(self, tmp_path):
        """Returns 'darwin' for macOS systems."""
        manager = ToolManager(cache_dir=tmp_path)
        with patch("platform.system", return_value="Darwin"):
            assert manager._get_platform_key() == "darwin"

    def test_windows_platform(self, tmp_path):
        """Returns 'win32' for Windows systems."""
        manager = ToolManager(cache_dir=tmp_path)
        with patch("platform.system", return_value="Windows"):
            assert manager._get_platform_key() == "win32"


class TestCheckForUpdates:
    """Test update checking."""

    def test_update_available(self, tmp_path):
        """Detects when update is available."""
        manager = ToolManager(cache_dir=tmp_path)
        tool_path = Path("/usr/bin/semgrep")

        with (
            patch.object(manager, "_find_tool", return_value=tool_path),
            patch.object(manager, "_get_tool_version", return_value="1.40.0"),
            patch.object(manager, "_get_size_mb", return_value=100.0),
        ):
            has_update, latest = manager.check_for_updates("semgrep")
            assert has_update is True
            assert latest == "1.45.0"

    def test_no_update_needed(self, tmp_path):
        """Detects when no update is needed."""
        manager = ToolManager(cache_dir=tmp_path)
        tool_path = Path("/usr/bin/semgrep")

        with (
            patch.object(manager, "_find_tool", return_value=tool_path),
            patch.object(manager, "_get_tool_version", return_value="1.45.0"),
            patch.object(manager, "_get_size_mb", return_value=100.0),
        ):
            has_update, latest = manager.check_for_updates("semgrep")
            assert has_update is False

    def test_unknown_tool(self, tmp_path):
        """Unknown tool returns no update."""
        manager = ToolManager(cache_dir=tmp_path)
        has_update, latest = manager.check_for_updates("unknowntool")
        assert has_update is False
        assert latest is None


class TestDownloadFile:
    """Test file downloading."""

    def test_download_with_timeout(self, tmp_path):
        """Download uses timeout."""
        manager = ToolManager(cache_dir=tmp_path)
        dest = tmp_path / "download.zip"

        with patch("specify_cli.security.tools.manager.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.side_effect = [b"data", b""]
            mock_response.__enter__ = MagicMock(return_value=mock_response)
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_response

            manager._download_file("https://example.com/file.zip", dest)

            mock_urlopen.assert_called_once_with(
                "https://example.com/file.zip",
                timeout=manager.DOWNLOAD_TIMEOUT_SECONDS,
            )

    def test_download_handles_url_error(self, tmp_path):
        """Raises RuntimeError on URL error."""
        from urllib.error import URLError

        manager = ToolManager(cache_dir=tmp_path)
        dest = tmp_path / "download.zip"

        with patch(
            "specify_cli.security.tools.manager.urlopen",
            side_effect=URLError("Connection refused"),
        ):
            with pytest.raises(RuntimeError, match="Download failed"):
                manager._download_file("https://example.com/file.zip", dest)


class TestInstallBinary:
    """Test binary installation."""

    def test_invalid_version_rejected(self, tmp_path):
        """Invalid version format is rejected."""
        config = ToolConfig(
            name="test",
            version="invalid-version-format",
            install_method=InstallMethod.BINARY,
            binary_urls={"linux": "https://example.com/{version}/test.zip"},
        )
        manager = ToolManager(cache_dir=tmp_path)
        result = manager._install_binary(config)
        assert result.success is False
        assert "Invalid version format" in result.error_message

    def test_missing_platform_binary(self, tmp_path):
        """Missing platform binary returns error."""
        config = ToolConfig(
            name="test",
            version="1.0.0",
            install_method=InstallMethod.BINARY,
            binary_urls={},  # No URLs
        )
        manager = ToolManager(cache_dir=tmp_path)
        result = manager._install_binary(config)
        assert result.success is False
        assert "No binary available" in result.error_message


class TestDetectInstallMethod:
    """Test install method detection."""

    def test_detects_binary_from_cache(self, tmp_path):
        """Detects binary install from cache path."""
        manager = ToolManager(cache_dir=tmp_path)
        tool_path = tmp_path / "semgrep" / "1.0" / "semgrep"
        assert manager._detect_install_method(tool_path) == InstallMethod.BINARY

    def test_detects_pip_from_venv(self, tmp_path):
        """Detects pip install from venv path."""
        manager = ToolManager(cache_dir=tmp_path)
        tool_path = Path("/home/user/.venv/bin/semgrep")
        assert manager._detect_install_method(tool_path) == InstallMethod.PIP

    def test_detects_system_install(self, tmp_path):
        """Detects system install from /usr/bin."""
        manager = ToolManager(cache_dir=tmp_path)
        tool_path = Path("/usr/bin/semgrep")
        assert manager._detect_install_method(tool_path) == InstallMethod.SYSTEM
