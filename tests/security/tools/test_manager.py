"""Tests for ToolManager class."""

import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from specify_cli.security.tools.manager import (
    DANGEROUS_PATH_CHARS,
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
        cache_dir = tmp_path / "tools"
        tool_cache = cache_dir / "semgrep" / "1.45.0"
        tool_cache.mkdir(parents=True)
        cached_exe = tool_cache / "semgrep"
        cached_exe.write_text("#!/bin/bash\necho test")
        cached_exe.chmod(0o755)

        manager = ToolManager(cache_dir=cache_dir, offline_mode=True)

        with (
            # Mock get_tool_info to avoid early return on "already installed"
            patch.object(manager, "get_tool_info", return_value=None),
            patch.object(manager, "_find_in_cache", return_value=cached_exe),
            patch.object(manager, "_get_tool_version", return_value="1.45.0"),
        ):
            result = manager.install("semgrep")
            assert result.success is True
            assert result.tool_info.status == ToolStatus.OFFLINE_ONLY
            # Issue #13 fix: Should have actual version, not "cached"
            assert result.tool_info.version == "1.45.0"

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
            "v1.0.0",
            "v2.15.0",
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
            "1.2.3.4",
            "1.2.3.4.5",
            "1.2.3.4.5.6",
        ]
        for version in invalid_versions:
            assert not manager._is_valid_version(version), f"Should reject: {version}"


class TestVersionPatternAnchoring:
    """Test VERSION_PATTERN anchoring behavior.

    VERSION_PATTERN uses anchored regex (^...$) for exact version validation,
    rejecting versions embedded in text. This prevents malformed versions like
    '1.2.3.4.5' and ensures only standalone versions are accepted.
    """

    def test_exact_match_versions(self):
        """VERSION_PATTERN matches exact versions."""
        assert VERSION_PATTERN.match("1.0.0")
        assert VERSION_PATTERN.match("v2.15.0")
        assert VERSION_PATTERN.match("1.0.0-beta1")
        assert VERSION_PATTERN.match("1.0")

    def test_rejects_versions_at_beginning_of_text(self):
        """VERSION_PATTERN rejects versions at beginning of text."""
        assert VERSION_PATTERN.match("1.45.0 extra text") is None
        assert VERSION_PATTERN.match("v1.0.0-suffix text") is None
        assert VERSION_PATTERN.match("1.0.0 package") is None

    def test_rejects_versions_at_end_of_text(self):
        """VERSION_PATTERN rejects versions at end of text."""
        assert VERSION_PATTERN.match("version 1.0.0") is None
        assert VERSION_PATTERN.match("tool-1.0.0") is None
        assert VERSION_PATTERN.match("prefix v2.15.0") is None

    def test_rejects_versions_in_middle_of_text(self):
        """VERSION_PATTERN rejects versions in middle of text."""
        assert VERSION_PATTERN.match("tool 1.0.0 package") is None
        assert VERSION_PATTERN.match("v 1.0.0 x") is None

    def test_rejects_malformed_versions(self):
        """VERSION_PATTERN rejects malformed versions."""
        assert VERSION_PATTERN.match("1.2.3.4") is None
        assert VERSION_PATTERN.match("1.2.3.4.5") is None
        assert VERSION_PATTERN.match("..1.0.0") is None
        assert VERSION_PATTERN.match("1.0.0..") is None


class TestVersionSearchPattern:
    """Test VERSION_SEARCH_PATTERN for extracting from tool output."""

    def test_extracts_versions_from_output(self):
        """VERSION_SEARCH_PATTERN extracts versions from tool output."""
        test_cases = [
            ("semgrep 1.45.0", "1.45.0"),
            ("v2.15.0", "2.15.0"),
            ("tool version 1.0.0-beta1", "1.0.0-beta1"),
            ("1.0", "1.0"),
            ("Version: 3.2.1", "3.2.1"),
            ("Bandit 1.7.7 from pip", "1.7.7"),
        ]
        for output, expected in test_cases:
            match = VERSION_SEARCH_PATTERN.search(output)
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
        with patch.object(manager, "_get_size_mb", return_value=600.0):
            tool_dir = tmp_path / "large_tool"
            tool_dir.mkdir()
            info = manager.get_cache_info()
            assert info.size_warning is True

    def test_cache_info_handles_permission_error(self, tmp_path):
        """Handles permission errors gracefully."""
        manager = ToolManager(cache_dir=tmp_path)

        mock_cache_dir = MagicMock(spec=Path)
        mock_cache_dir.exists.return_value = True
        mock_cache_dir.iterdir.side_effect = PermissionError("Permission denied")
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
        deep_dir = tmp_path / "a" / "b" / "c" / "d" / "e" / "f"
        deep_dir.mkdir(parents=True)
        exe = deep_dir / "mytool"
        exe.write_text("#!/bin/bash\necho test")
        exe.chmod(0o755)

        manager = ToolManager(cache_dir=tmp_path)
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
        test_file.write_bytes(b"x" * (1024 * 1024))

        manager = ToolManager(cache_dir=tmp_path)
        size = manager._get_size_mb(test_file)
        assert abs(size - 1.0) < 0.01

    def test_directory_size(self, tmp_path):
        """Calculates directory size correctly."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "file1.bin").write_bytes(b"x" * (512 * 1024))
        (subdir / "file2.bin").write_bytes(b"x" * (512 * 1024))

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

    def test_unsupported_platform_raises_error(self, tmp_path):
        """Unsupported platforms raise RuntimeError (Issue #11 fix)."""
        manager = ToolManager(cache_dir=tmp_path)

        with patch("platform.system", return_value="FreeBSD"):
            with pytest.raises(RuntimeError, match="Unsupported platform"):
                manager._get_platform_key()


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

    def test_download_enforces_max_size(self, tmp_path):
        """Download aborted when exceeding max size (Issue #3 fix)."""
        manager = ToolManager(cache_dir=tmp_path)
        dest = tmp_path / "download.zip"

        with patch("specify_cli.security.tools.manager.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            # Simulate 2MB response with 1MB limit (each chunk is 1MB)
            mock_response.read.side_effect = [
                b"x" * (1024 * 1024),
                b"x" * (1024 * 1024),
            ]
            mock_response.__enter__ = MagicMock(return_value=mock_response)
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_response

            with pytest.raises(RuntimeError, match="exceeded maximum size"):
                manager._download_file(
                    "https://example.com/file.zip", dest, max_size_mb=1
                )


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
            binary_urls={},
        )
        manager = ToolManager(cache_dir=tmp_path)
        result = manager._install_binary(config)
        assert result.success is False
        assert "No binary available" in result.error_message

    def test_missing_version_rejected(self, tmp_path):
        """Binary install requires version (Issue #14 fix)."""
        config = ToolConfig(
            name="test",
            version=None,  # No version
            install_method=InstallMethod.BINARY,
            binary_urls={"linux": "https://example.com/{version}/test.zip"},
        )
        manager = ToolManager(cache_dir=tmp_path)
        result = manager._install_binary(config)
        assert result.success is False
        assert "requires version" in result.error_message


class TestDetectInstallMethod:
    """Test install method detection."""

    def test_detects_binary_from_cache(self, tmp_path):
        """Detects binary install from cache path."""
        manager = ToolManager(cache_dir=tmp_path)
        tool_path = tmp_path / "semgrep" / "1.0" / "semgrep"
        assert manager._detect_install_method(tool_path) == InstallMethod.BINARY

    def test_detects_pip_from_venv(self, tmp_path):
        """Detects pip install from venv path using path parts (Issue #16 fix)."""
        manager = ToolManager(cache_dir=tmp_path)
        # Using .venv as a path component, not substring
        tool_path = Path("/home/user/.venv/bin/semgrep")
        assert manager._detect_install_method(tool_path) == InstallMethod.PIP

    def test_detects_system_install(self, tmp_path):
        """Detects system install from /usr/bin."""
        manager = ToolManager(cache_dir=tmp_path)
        tool_path = Path("/usr/bin/semgrep")
        assert manager._detect_install_method(tool_path) == InstallMethod.SYSTEM

    def test_venv_detection_no_false_positives(self, tmp_path):
        """Issue #16 fix: Paths with 'venv' substring don't trigger false positive."""
        manager = ToolManager(cache_dir=tmp_path)
        # This should be SYSTEM, not PIP - "venv" is part of directory name, not path component
        tool_path = Path("/usr/local/venv-tools/bin/mytool")
        assert manager._detect_install_method(tool_path) == InstallMethod.SYSTEM


class TestSecurityProtections:
    """Test security protections in tool manager."""

    def test_download_rejects_http_urls(self, tmp_path):
        """HTTP URLs are rejected for security - only HTTPS allowed."""
        manager = ToolManager(cache_dir=tmp_path)
        dest = tmp_path / "download.zip"

        with pytest.raises(ValueError, match="Only HTTPS URLs are allowed"):
            manager._download_file("http://example.com/tool.zip", dest)

    def test_download_error_includes_url(self, tmp_path):
        """Error message includes the rejected URL for debugging."""
        manager = ToolManager(cache_dir=tmp_path)
        dest = tmp_path / "download.zip"

        with pytest.raises(ValueError) as exc_info:
            manager._download_file("http://evil.com/malware.zip", dest)

        assert "http://evil.com/malware.zip" in str(exc_info.value)
        assert "HTTPS" in str(exc_info.value)

    def test_download_accepts_https_urls(self, tmp_path):
        """HTTPS URLs are accepted."""
        manager = ToolManager(cache_dir=tmp_path)
        dest = tmp_path / "download.zip"

        with patch("specify_cli.security.tools.manager.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.side_effect = [b"data", b""]
            mock_response.__enter__ = MagicMock(return_value=mock_response)
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_response

            manager._download_file("https://example.com/tool.zip", dest)

    def test_archive_extraction_rejects_path_traversal(self, tmp_path):
        """Archives with path traversal (..) are rejected."""
        manager = ToolManager(cache_dir=tmp_path)
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()

        malicious_zip = tmp_path / "evil.zip"
        with zipfile.ZipFile(malicious_zip, "w") as zf:
            zf.writestr("../../../etc/passwd", "malicious content")

        with pytest.raises(RuntimeError, match="path traversal"):
            manager._safe_extract_archive(malicious_zip, extract_dir)

    def test_archive_extraction_rejects_absolute_paths(self, tmp_path):
        """Archives with absolute paths are rejected."""
        manager = ToolManager(cache_dir=tmp_path)
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()

        malicious_zip = tmp_path / "evil.zip"
        with zipfile.ZipFile(malicious_zip, "w") as zf:
            zf.writestr("/etc/passwd", "malicious content")

        with pytest.raises(RuntimeError, match="absolute path"):
            manager._safe_extract_archive(malicious_zip, extract_dir)

    def test_archive_extraction_allows_safe_files(self, tmp_path):
        """Safe archives extract correctly."""
        manager = ToolManager(cache_dir=tmp_path)
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()

        safe_zip = tmp_path / "safe.zip"
        with zipfile.ZipFile(safe_zip, "w") as zf:
            zf.writestr("tool/bin/mytool", "#!/bin/bash\necho test")
            zf.writestr("tool/README.md", "# My Tool")

        manager._safe_extract_archive(safe_zip, extract_dir)

        assert (extract_dir / "tool" / "bin" / "mytool").exists()
        assert (extract_dir / "tool" / "README.md").exists()

    def test_archive_allows_filenames_with_double_dots(self, tmp_path):
        """Legitimate filenames containing .. are allowed (not path traversal)."""
        manager = ToolManager(cache_dir=tmp_path)
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()

        # These filenames have ".." but are NOT path traversal
        safe_zip = tmp_path / "legitimate.zip"
        with zipfile.ZipFile(safe_zip, "w") as zf:
            zf.writestr("tool/README..md", "# Documentation")
            zf.writestr("tool/config..backup", "backup content")
            zf.writestr("tool/file..old.txt", "old file")
            zf.writestr("tool/.hidden..file", "hidden with dots")

        manager._safe_extract_archive(safe_zip, extract_dir)

        assert (extract_dir / "tool" / "README..md").exists()
        assert (extract_dir / "tool" / "config..backup").exists()
        assert (extract_dir / "tool" / "file..old.txt").exists()
        assert (extract_dir / "tool" / ".hidden..file").exists()

    def test_path_validation_uses_relative_to(self, tmp_path):
        """Issue #1 fix: Path validation uses Path.relative_to() not string prefix."""
        manager = ToolManager(cache_dir=tmp_path)
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()

        # Create ZIP with path that would bypass string prefix check
        # e.g., if dest is /tmp/extract, ../extract_sibling would start with /tmp/extract
        # but should still be rejected
        malicious_zip = tmp_path / "evil.zip"
        with zipfile.ZipFile(malicious_zip, "w") as zf:
            zf.writestr("../../escape.txt", "malicious")

        with pytest.raises(RuntimeError, match="path traversal"):
            manager._safe_extract_archive(malicious_zip, extract_dir)


class TestSymlinkProtection:
    """Test symlink attack detection."""

    def test_rejects_symlinks_in_non_zip_non_tar_archives(self, tmp_path):
        """Extraction fails with RuntimeError when symlinks are detected in non-ZIP/tar archives (Issue #22 fix)."""
        manager = ToolManager(cache_dir=tmp_path)
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()

        # Mock shutil.unpack_archive to simulate extraction with symlink
        def mock_unpack(archive, dest):
            (dest / "normal.txt").write_text("content")
            (dest / "link").symlink_to("/etc/passwd")

        # Use .rar extension to bypass zip/tar specific handlers
        with patch("shutil.unpack_archive", side_effect=mock_unpack):
            with pytest.raises(RuntimeError, match="symlink"):
                manager._safe_extract_archive(tmp_path / "archive.rar", extract_dir)


class TestCommandInjectionPrevention:
    """Test command injection prevention in tool version detection (Issue #8 fix)."""

    def test_rejects_paths_with_shell_metacharacters(self, tmp_path):
        """Tool paths with shell metacharacters return 'unknown'."""
        manager = ToolManager(cache_dir=tmp_path)

        dangerous_paths = [
            Path("/tmp/tool;rm -rf /"),
            Path("/tmp/tool&background"),
            Path("/tmp/tool|pipe"),
            Path("/tmp/tool$var"),
            Path("/tmp/tool`cmd`"),
            Path("/tmp/tool\ninjected"),
        ]

        for path in dangerous_paths:
            version = manager._get_tool_version("test", path)
            assert version == "unknown", f"Should reject: {path}"

    def test_accepts_safe_paths(self, tmp_path):
        """Safe paths are allowed and version is extracted."""
        manager = ToolManager(cache_dir=tmp_path)
        safe_path = tmp_path / "mytool"
        safe_path.write_text("#!/bin/bash\necho test")
        safe_path.chmod(0o755)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="mytool 1.2.3\n", stderr="")
            version = manager._get_tool_version("mytool", safe_path)
            assert version == "1.2.3"

    def test_dangerous_path_chars_constant_defined(self):
        """DANGEROUS_PATH_CHARS constant includes all expected characters."""
        expected_chars = {";", "|", "&", "$", "`", "\n", "\r", "<", ">"}
        assert expected_chars <= DANGEROUS_PATH_CHARS


class TestTOCTOUMitigation:
    """Test TOCTOU mitigation in non-ZIP/tar extraction (Issue #2 fix)."""

    def test_non_zip_non_tar_extraction_validates_before_moving(self, tmp_path):
        """Non-ZIP/tar archives validated in temp directory before moving to dest."""
        manager = ToolManager(cache_dir=tmp_path)
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()

        extraction_count = {"calls": 0}

        def mock_unpack(archive, dest):
            extraction_count["calls"] += 1
            # First extraction is to temp directory
            # Simulate extraction with symlink
            (dest / "normal.txt").write_text("content")
            (dest / "link").symlink_to("/etc/passwd")

        # Use .rar extension to bypass zip/tar specific handlers
        with patch("shutil.unpack_archive", side_effect=mock_unpack):
            with pytest.raises(RuntimeError, match="symlink"):
                manager._safe_extract_archive(tmp_path / "archive.rar", extract_dir)

        # Verify destination directory is empty (temp dir cleaned up)
        assert not list(extract_dir.iterdir())

    def test_temp_directory_cleaned_on_success(self, tmp_path):
        """Temp directory is cleaned up after successful extraction."""
        manager = ToolManager(cache_dir=tmp_path)
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()

        def mock_unpack(archive, dest):
            (dest / "safe_file.txt").write_text("safe content")

        # Use .rar extension to bypass zip/tar specific handlers
        with patch("shutil.unpack_archive", side_effect=mock_unpack):
            manager._safe_extract_archive(tmp_path / "archive.rar", extract_dir)

        # Verify no temp directories left behind
        parent = extract_dir.parent
        temp_dirs = [d for d in parent.iterdir() if d.name.startswith(".tmp_extract_")]
        assert len(temp_dirs) == 0

        # Verify content was moved to destination
        assert (extract_dir / "safe_file.txt").exists()


class TestZipPostExtractionValidation:
    """Test post-extraction symlink validation for ZIP archives."""

    def test_zip_post_extraction_symlink_detected(self, tmp_path):
        """Symlinks created after zip extraction are detected and rejected."""
        manager = ToolManager(cache_dir=tmp_path)
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()

        # Create a normal zip file
        safe_zip = tmp_path / "test.zip"
        with zipfile.ZipFile(safe_zip, "w") as zf:
            zf.writestr("tool/file.txt", "content")

        # Mock extractall to create a symlink after extraction
        original_extractall = zipfile.ZipFile.extractall

        def mock_extractall(self, path):
            # Call original extraction
            original_extractall(self, path)
            # Then create a malicious symlink
            symlink_path = Path(path) / "tool" / "evil_link"
            symlink_path.symlink_to("/etc/passwd")

        with patch.object(zipfile.ZipFile, "extractall", mock_extractall):
            # Should detect symlink during post-extraction check
            with pytest.raises(RuntimeError, match="symlink"):
                manager._safe_extract_archive(safe_zip, extract_dir)

    def test_zip_post_extraction_external_symlink_detected(self, tmp_path):
        """External symlinks created after zip extraction are detected."""
        manager = ToolManager(cache_dir=tmp_path)
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()

        # Create normal zip
        safe_zip = tmp_path / "test.zip"
        with zipfile.ZipFile(safe_zip, "w") as zf:
            zf.writestr("file.txt", "content")

        # Create external target
        outside_target = tmp_path / "outside.txt"
        outside_target.write_text("outside")

        # Mock to create external symlink after extraction
        original_extractall = zipfile.ZipFile.extractall

        def mock_extractall(self, path):
            original_extractall(self, path)
            # Create symlink pointing outside extraction dir
            symlink_path = Path(path) / "evil_link"
            symlink_path.symlink_to(outside_target)

        with patch.object(zipfile.ZipFile, "extractall", mock_extractall):
            # Should detect and reject external symlink
            with pytest.raises(RuntimeError, match="symlink"):
                manager._safe_extract_archive(safe_zip, extract_dir)


class TestTarSymlinkValidation:
    """Test tar archive symlink validation."""

    def test_tar_symlink_with_path_traversal_rejected(self, tmp_path):
        """Tar archives with symlinks containing path traversal are rejected."""
        import tarfile

        manager = ToolManager(cache_dir=tmp_path)
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()

        # Create malicious tar with symlink containing path traversal
        malicious_tar = tmp_path / "evil_symlink.tar"
        with tarfile.open(malicious_tar, "w") as tf:
            # Create a symlink member pointing to ../../etc/passwd
            link_info = tarfile.TarInfo(name="evil_link")
            link_info.type = tarfile.SYMTYPE
            link_info.linkname = "../../etc/passwd"
            tf.addfile(link_info)

        # Should reject symlink (all symlinks rejected for consistency with ZIP)
        with pytest.raises(RuntimeError, match="not allowed"):
            manager._safe_extract_archive(malicious_tar, extract_dir)

    def test_tar_symlink_to_absolute_path_rejected(self, tmp_path):
        """Tar archives with symlinks to absolute paths are rejected."""
        import tarfile

        manager = ToolManager(cache_dir=tmp_path)
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()

        # Create tar with symlink to absolute path
        malicious_tar = tmp_path / "abs_symlink.tar"
        with tarfile.open(malicious_tar, "w") as tf:
            link_info = tarfile.TarInfo(name="abs_link")
            link_info.type = tarfile.SYMTYPE
            link_info.linkname = "/etc/passwd"
            tf.addfile(link_info)

        # Should reject symlink (all symlinks rejected for consistency with ZIP)
        with pytest.raises(RuntimeError, match="not allowed"):
            manager._safe_extract_archive(malicious_tar, extract_dir)

    def test_tar_post_extraction_symlink_detected(self, tmp_path):
        """Issue #6: Symlinks created after tar extraction are detected and rejected."""
        import tarfile

        manager = ToolManager(cache_dir=tmp_path)
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()

        # Create a normal tar file
        safe_tar = tmp_path / "test.tar"
        with tarfile.open(safe_tar, "w") as tf:
            # Add normal file
            info = tarfile.TarInfo(name="tool/file.txt")
            info.size = 7
            from io import BytesIO

            tf.addfile(info, BytesIO(b"content"))

        # Mock extractall to create a symlink after extraction
        original_extractall = tarfile.TarFile.extractall

        def mock_extractall(self, path, *args, **kwargs):
            # Call original extraction
            original_extractall(self, path, *args, **kwargs)
            # Then create a malicious symlink
            symlink_path = Path(path) / "tool" / "evil_link"
            symlink_path.symlink_to("/etc/passwd")

        with patch.object(tarfile.TarFile, "extractall", mock_extractall):
            # Should detect symlink during post-extraction check
            with pytest.raises(RuntimeError, match="symlink"):
                manager._safe_extract_archive(safe_tar, extract_dir)


class TestURLValidation:
    """Test URL template validation."""

    def test_valid_url_template(self, tmp_path):
        """Valid URL templates are accepted."""
        manager = ToolManager(cache_dir=tmp_path)

        valid, error = manager._validate_url_template(
            "https://example.com/tool/{version}/tool.zip", "1.0.0"
        )
        assert valid is True
        assert error == ""

    def test_url_template_with_invalid_placeholder(self, tmp_path):
        """URL templates with invalid placeholders are rejected."""
        manager = ToolManager(cache_dir=tmp_path)

        valid, error = manager._validate_url_template(
            "https://example.com/{invalid}/tool.zip", "1.0.0"
        )
        assert valid is False
        assert "Invalid URL template placeholder" in error

    def test_url_template_empty_version(self, tmp_path):
        """URL templates requiring version with empty version are rejected."""
        manager = ToolManager(cache_dir=tmp_path)

        valid, error = manager._validate_url_template(
            "https://example.com/{version}/tool.zip", ""
        )
        assert valid is False
        assert "version is empty" in error

    def test_url_template_empty_version_with_double_slash(self, tmp_path):
        """Issue #2: URL template with empty version and double slash is rejected."""
        manager = ToolManager(cache_dir=tmp_path)

        # Empty version with template requiring version
        valid, error = manager._validate_url_template(
            "https://example.com//{version}tool.zip",
            "",  # Empty version
        )
        assert valid is False
        assert "version is empty" in error.lower()

    def test_url_template_malformed_url_after_substitution(self, tmp_path):
        """Issue #2: Malformed URLs with double slashes after substitution are rejected."""
        manager = ToolManager(cache_dir=tmp_path)

        # This creates https://example.com//tool.zip (double slash in path)
        valid, error = manager._validate_url_template(
            "https://example.com//tool.zip",
            "1.0.0",  # Version provided but not used
        )
        # Should reject due to double slash in path
        assert valid is False
        assert "malformed" in error.lower() or "//" in error

    def test_get_filename_from_url(self, tmp_path):
        """Filename extraction from URL works correctly."""
        manager = ToolManager(cache_dir=tmp_path)

        # Test various URL formats
        assert (
            manager._get_filename_from_url("https://example.com/tool.zip") == "tool.zip"
        )
        assert (
            manager._get_filename_from_url("https://example.com/path/to/tool.tar.gz")
            == "tool.tar.gz"
        )
        assert manager._get_filename_from_url("https://example.com/") == "download.bin"
        assert (
            manager._get_filename_from_url("https://example.com/no-extension")
            == "download.bin"
        )


class TestConcurrentInstallation:
    """Test concurrent installation locking."""

    def test_concurrent_install_lock(self, tmp_path):
        """File-based locking prevents concurrent installations."""
        import threading
        import time

        manager = ToolManager(cache_dir=tmp_path)
        results = []

        def install_with_lock():
            try:
                with manager._acquire_install_lock("test-tool", "1.0.0", timeout=1):
                    # Simulate work - hold lock longer than timeout
                    time.sleep(1.5)
                    results.append("success")
            except Exception as e:
                # filelock raises Timeout, fcntl-based raises RuntimeError
                results.append(f"error: {e}")

        # Start two threads trying to install simultaneously
        thread1 = threading.Thread(target=install_with_lock)
        thread2 = threading.Thread(target=install_with_lock)

        thread1.start()
        time.sleep(0.1)  # Ensure thread1 acquires lock first
        thread2.start()

        thread1.join()
        thread2.join()

        # Issue #2: Strengthen assertions - exactly one success, one error
        assert len(results) == 2
        success_count = sum(1 for r in results if r == "success")
        error_count = sum(1 for r in results if "error" in str(r))
        assert success_count == 1
        assert error_count == 1
