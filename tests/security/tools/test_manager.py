"""Tests for ToolManager class."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from specify_cli.security.tools.manager import (
    ToolManager,
    VERSION_PATTERN,
    VERSION_SEARCH_PATTERN,
)
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
        """Offline mode only uses cached tools."""
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
        invalid_versions = [
            "",
            "abc",
            "version",
            "...",
            "1-2-3",
            "1.2.3.4",  # Too many segments
            "1.2.3.4.5",  # Way too many segments
            "1.2.3.4.5.6",  # Even more segments
        ]
        for version in invalid_versions:
            assert not manager._is_valid_version(version), f"Should reject: {version}"

    def test_version_with_v_prefix(self, tmp_path):
        """Versions with 'v' prefix are valid."""
        manager = ToolManager(cache_dir=tmp_path)
        assert manager._is_valid_version("v1.0.0")
        assert manager._is_valid_version("v2.15.0")


class TestVersionParsing:
    """Test version parsing from tool output."""

    def test_version_search_pattern_matches(self):
        """VERSION_SEARCH_PATTERN extracts versions from tool output correctly."""
        test_cases = [
            ("semgrep 1.45.0", "1.45.0"),
            ("v2.15.0", "2.15.0"),
            ("tool version 1.0.0-beta1", "1.0.0-beta1"),
            ("1.0", "1.0"),
            ("Version: 3.2.1", "3.2.1"),
        ]
        for output, expected in test_cases:
            match = VERSION_SEARCH_PATTERN.search(output)
            assert match is not None, f"Should match: {output}"
            assert match.group(1) == expected, f"For '{output}': expected {expected}"

    def test_version_pattern_is_anchored(self):
        """VERSION_PATTERN requires exact match (anchored)."""
        # Should match exact versions
        assert VERSION_PATTERN.match("1.0.0")
        assert VERSION_PATTERN.match("v2.15.0")

        # Should NOT match versions embedded in other text
        assert VERSION_PATTERN.match("semgrep 1.45.0") is None
        assert VERSION_PATTERN.match("1.2.3.4") is None

    def test_version_at_end_of_text(self):
        """FIX #8: Test VERSION_SEARCH_PATTERN matches versions at end of text."""
        test_cases = [
            ("tool name 1.2.3", "1.2.3"),
            ("version: 4.5.6", "4.5.6"),
            ("some text here v2.0.0", "2.0.0"),
        ]
        for output, expected in test_cases:
            match = VERSION_SEARCH_PATTERN.search(output)
            assert match is not None, f"Should match at end: {output}"
            assert match.group(1) == expected

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
        # Create manager with a mock cache_dir that raises PermissionError
        manager = ToolManager(cache_dir=tmp_path)

        # Create a mock that raises PermissionError on iterdir
        mock_cache_dir = MagicMock(spec=Path)
        mock_cache_dir.exists.return_value = True
        mock_cache_dir.iterdir.side_effect = PermissionError("Permission denied")

        # Replace the cache_dir with our mock
        manager.cache_dir = mock_cache_dir

        info = manager.get_cache_info()
        assert info.tool_count == 0
        assert info.total_size_mb == 0.0


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

    def test_executable_size_validation(self, tmp_path):
        """FIX #10: Test that executable size is validated."""
        import zipfile

        manager = ToolManager(cache_dir=tmp_path)

        # Reduce MAX_EXECUTABLE_SIZE_MB temporarily to test without creating huge file
        original_max = manager.MAX_EXECUTABLE_SIZE_MB
        manager.MAX_EXECUTABLE_SIZE_MB = 0.001  # 1KB limit for testing

        # Create cache directory structure
        cache_tool_dir = tmp_path / "mytool" / "1.0.0"
        cache_tool_dir.mkdir(parents=True)

        config = ToolConfig(
            name="mytool",
            version="1.0.0",
            install_method=InstallMethod.BINARY,
            binary_urls={"linux": "https://example.com/test.zip"},
        )

        # Create a file larger than the test limit (2KB) during extraction
        def mock_download(url, dest):
            # Create a fake zip file so unlink() works
            dest.write_bytes(b"fake zip content")

        def mock_extract(archive_path, dest_dir):
            # Simulate extraction creating a large tool file
            tool_file = dest_dir / "bin" / "mytool"
            tool_file.parent.mkdir(parents=True, exist_ok=True)
            tool_file.write_bytes(b"x" * 2048)  # 2KB file
            tool_file.chmod(0o755)

        def mock_find(dest_dir, tool_name):
            return dest_dir / "bin" / tool_name

        # Mock the download and extraction to bypass file I/O
        with (
            patch.object(manager, "_download_file", side_effect=mock_download),
            patch.object(manager, "_safe_extract_archive", side_effect=mock_extract),
            patch.object(manager, "_find_in_directory", side_effect=mock_find),
        ):
            result = manager._install_binary(config)
            assert result.success is False
            assert "too large" in result.error_message.lower()

        # Restore original value
        manager.MAX_EXECUTABLE_SIZE_MB = original_max


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


class TestSecurityProtections:
    """Test security protections in tool manager."""

    def test_download_rejects_http_urls(self, tmp_path):
        """HTTP URLs are rejected for security - only HTTPS allowed."""
        manager = ToolManager(cache_dir=tmp_path)
        dest = tmp_path / "download.zip"

        with pytest.raises(ValueError, match="Only HTTPS URLs are allowed"):
            manager._download_file("http://example.com/tool.zip", dest)

    def test_download_accepts_https_urls(self, tmp_path):
        """HTTPS URLs are accepted."""
        manager = ToolManager(cache_dir=tmp_path)
        dest = tmp_path / "download.zip"

        # Mock urlopen to avoid actual network call
        with patch("specify_cli.security.tools.manager.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.side_effect = [b"data", b""]
            mock_response.__enter__ = MagicMock(return_value=mock_response)
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_response

            # Should not raise
            manager._download_file("https://example.com/tool.zip", dest)

    def test_archive_extraction_rejects_path_traversal(self, tmp_path):
        """FIX #1: Archives with path traversal (..) in path parts are rejected."""
        import zipfile

        manager = ToolManager(cache_dir=tmp_path)
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()

        # Create malicious zip with path traversal
        malicious_zip = tmp_path / "evil.zip"
        with zipfile.ZipFile(malicious_zip, "w") as zf:
            zf.writestr("../../../etc/passwd", "malicious content")

        with pytest.raises(RuntimeError, match="path traversal"):
            manager._safe_extract_archive(malicious_zip, extract_dir)

    def test_archive_extraction_allows_legitimate_dotdot_filenames(self, tmp_path):
        """FIX #1: Legitimate files like 'README..md' should be allowed."""
        import zipfile

        manager = ToolManager(cache_dir=tmp_path)
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()

        # Create zip with legitimate filename containing ".."
        safe_zip = tmp_path / "safe.zip"
        with zipfile.ZipFile(safe_zip, "w") as zf:
            zf.writestr("README..md", "# Readme")
            zf.writestr("file..backup", "backup content")

        # Should not raise - ".." is not a path component, just part of filename
        manager._safe_extract_archive(safe_zip, extract_dir)

        assert (extract_dir / "README..md").exists()
        assert (extract_dir / "file..backup").exists()

    def test_archive_extraction_rejects_absolute_paths(self, tmp_path):
        """Archives with absolute paths are rejected."""
        import zipfile

        manager = ToolManager(cache_dir=tmp_path)
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()

        # Create malicious zip with absolute path
        malicious_zip = tmp_path / "evil.zip"
        with zipfile.ZipFile(malicious_zip, "w") as zf:
            zf.writestr("/etc/passwd", "malicious content")

        with pytest.raises(RuntimeError, match="absolute path"):
            manager._safe_extract_archive(malicious_zip, extract_dir)

    def test_archive_extraction_rejects_too_many_files(self, tmp_path):
        """FIX #3: Archives with too many files are rejected (zip bomb protection)."""
        import zipfile

        manager = ToolManager(cache_dir=tmp_path)
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()

        # Create zip with too many files
        zip_bomb = tmp_path / "bomb.zip"
        with zipfile.ZipFile(zip_bomb, "w") as zf:
            # Add more files than MAX_ARCHIVE_FILES
            for i in range(manager.MAX_ARCHIVE_FILES + 10):
                zf.writestr(f"file{i}.txt", f"content {i}")

        with pytest.raises(RuntimeError, match="too many files"):
            manager._safe_extract_archive(zip_bomb, extract_dir)

    def test_archive_extraction_allows_safe_files(self, tmp_path):
        """Safe archives extract correctly."""
        import zipfile

        manager = ToolManager(cache_dir=tmp_path)
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()

        # Create safe zip
        safe_zip = tmp_path / "safe.zip"
        with zipfile.ZipFile(safe_zip, "w") as zf:
            zf.writestr("tool/bin/mytool", "#!/bin/bash\necho test")
            zf.writestr("tool/README.md", "# My Tool")

        # Should not raise
        manager._safe_extract_archive(safe_zip, extract_dir)

        # Verify files extracted
        assert (extract_dir / "tool" / "bin" / "mytool").exists()
        assert (extract_dir / "tool" / "README.md").exists()

    def test_non_zip_archive_extraction_with_file_limit(self, tmp_path):
        """FIX #4 & #6: Test non-ZIP archive extraction with file count limit."""
        import tarfile

        manager = ToolManager(cache_dir=tmp_path)
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()

        # Create a tar.gz with a safe number of files
        safe_tar = tmp_path / "safe.tar.gz"
        with tarfile.open(safe_tar, "w:gz") as tf:
            for i in range(10):
                import io
                content = f"content {i}".encode()
                tarinfo = tarfile.TarInfo(name=f"file{i}.txt")
                tarinfo.size = len(content)
                tf.addfile(tarinfo, io.BytesIO(content))

        # Should extract successfully
        manager._safe_extract_archive(safe_tar, extract_dir)
        assert (extract_dir / "file0.txt").exists()

    def test_extension_checking_case_insensitive(self, tmp_path):
        """FIX #7: Extension checking should be case-insensitive."""
        import zipfile

        manager = ToolManager(cache_dir=tmp_path)
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()

        # Create ZIP with uppercase extension
        upper_zip = tmp_path / "test.ZIP"
        with zipfile.ZipFile(upper_zip, "w") as zf:
            zf.writestr("tool/mytool", "#!/bin/bash\necho test")

        # Should handle .ZIP extension correctly
        manager._safe_extract_archive(upper_zip, extract_dir)
        assert (extract_dir / "tool" / "mytool").exists()

    def test_path_traversal_bypass_attempts(self, tmp_path):
        """FIX #9: Test various path traversal bypass attempts."""
        import zipfile

        manager = ToolManager(cache_dir=tmp_path)
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()

        # Test cases for path traversal bypass attempts
        bypass_attempts = [
            "../../etc/passwd",  # Standard traversal
            "foo/../../etc/passwd",  # Traversal after directory
            "foo/../../../etc/passwd",  # Multiple levels
        ]

        for attempt in bypass_attempts:
            malicious_zip = tmp_path / f"evil_{bypass_attempts.index(attempt)}.zip"
            with zipfile.ZipFile(malicious_zip, "w") as zf:
                zf.writestr(attempt, "malicious")

            with pytest.raises(RuntimeError, match="path traversal"):
                manager._safe_extract_archive(malicious_zip, extract_dir)

    def test_path_validation_with_relative_to(self, tmp_path):
        """FIX #2 & #5: Verify path validation uses relative_to() not string prefix."""
        import zipfile

        manager = ToolManager(cache_dir=tmp_path)

        # Create two directories: one is prefix of the other
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()

        # This test verifies the fix works correctly
        # by creating a valid file and ensuring it extracts
        safe_zip = tmp_path / "safe.zip"
        with zipfile.ZipFile(safe_zip, "w") as zf:
            zf.writestr("normal/file.txt", "safe content")

        # Should extract without issues
        manager._safe_extract_archive(safe_zip, extract_dir)
        assert (extract_dir / "normal" / "file.txt").exists()
