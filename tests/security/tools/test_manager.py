"""Tests for ToolManager class.

Tests tool dependency management including:
- Tool discovery
- Auto-installation with version pinning
- License compliance checking
- Cache size monitoring
- Offline mode
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

from specify_cli.security.tools.manager import ToolManager
from specify_cli.security.tools.models import (
    InstallMethod,
    ToolConfig,
    ToolStatus,
)


class TestToolManagerInit:
    """Test ToolManager initialization."""

    def test_default_cache_dir(self):
        """Default cache directory is ~/.specify/tools."""
        manager = ToolManager()
        assert manager.cache_dir == Path.home() / ".specify" / "tools"

    def test_custom_cache_dir(self, tmp_path):
        """Custom cache directory is respected."""
        cache_dir = tmp_path / "custom_cache"
        manager = ToolManager(cache_dir=cache_dir)
        assert manager.cache_dir == cache_dir
        assert cache_dir.exists()

    def test_offline_mode_default(self):
        """Offline mode is disabled by default."""
        manager = ToolManager()
        assert manager.offline_mode is False

    def test_offline_mode_enabled(self, tmp_path):
        """Offline mode can be enabled."""
        manager = ToolManager(cache_dir=tmp_path, offline_mode=True)
        assert manager.offline_mode is True

    def test_default_tool_configs(self):
        """Default tool configs include expected tools."""
        manager = ToolManager()
        assert "semgrep" in manager.tool_configs
        assert "codeql" in manager.tool_configs
        assert "bandit" in manager.tool_configs

    def test_custom_tool_configs(self, tmp_path):
        """Custom tool configs override defaults."""
        custom_config = {
            "mytool": ToolConfig(name="mytool", version="1.0.0"),
        }
        manager = ToolManager(cache_dir=tmp_path, tool_configs=custom_config)
        assert "mytool" in manager.tool_configs
        assert "semgrep" not in manager.tool_configs


class TestToolDiscovery:
    """Test tool discovery functionality."""

    def test_find_tool_in_path(self, tmp_path):
        """Find tool in system PATH."""
        manager = ToolManager(cache_dir=tmp_path)

        with patch("shutil.which") as mock_which:
            mock_which.return_value = "/usr/bin/semgrep"
            path = manager._find_tool("semgrep")
            assert path == Path("/usr/bin/semgrep")

    def test_find_tool_not_found(self, tmp_path):
        """Return None when tool not found anywhere."""
        manager = ToolManager(cache_dir=tmp_path)

        with patch("shutil.which", return_value=None):
            path = manager._find_tool("nonexistent")
            assert path is None

    def test_is_available_true(self, tmp_path):
        """is_available returns True when tool exists."""
        manager = ToolManager(cache_dir=tmp_path)

        with patch.object(manager, "_find_tool", return_value=Path("/usr/bin/tool")):
            assert manager.is_available("tool") is True

    def test_is_available_false(self, tmp_path):
        """is_available returns False when tool missing."""
        manager = ToolManager(cache_dir=tmp_path)

        with patch.object(manager, "_find_tool", return_value=None):
            assert manager.is_available("tool") is False


class TestGetToolInfo:
    """Test getting tool information."""

    def test_get_info_not_installed(self, tmp_path):
        """Return None for non-installed tool."""
        manager = ToolManager(cache_dir=tmp_path)

        with patch.object(manager, "_find_tool", return_value=None):
            info = manager.get_tool_info("nonexistent")
            assert info is None

    def test_get_info_installed(self, tmp_path):
        """Return ToolInfo for installed tool."""
        manager = ToolManager(cache_dir=tmp_path)
        tool_path = Path("/usr/bin/semgrep")

        with (
            patch.object(manager, "_find_tool", return_value=tool_path),
            patch.object(manager, "_get_tool_version", return_value="1.45.0"),
        ):
            info = manager.get_tool_info("semgrep")
            assert info is not None
            assert info.name == "semgrep"
            assert info.version == "1.45.0"
            assert info.path == tool_path


class TestInstallation:
    """Test tool installation."""

    def test_install_unknown_tool(self, tmp_path):
        """Fail gracefully for unknown tool."""
        manager = ToolManager(cache_dir=tmp_path)
        result = manager.install("unknown_tool")

        assert result.success is False
        assert "Unknown tool" in result.error_message

    def test_install_already_installed(self, tmp_path):
        """Skip installation if already installed."""
        manager = ToolManager(cache_dir=tmp_path)

        mock_info = MagicMock()
        mock_info.status = ToolStatus.INSTALLED

        with patch.object(manager, "get_tool_info", return_value=mock_info):
            result = manager.install("semgrep")
            assert result.success is True

    def test_install_offline_mode_not_cached(self, tmp_path):
        """Fail in offline mode when tool not cached."""
        manager = ToolManager(cache_dir=tmp_path, offline_mode=True)

        with patch.object(manager, "get_tool_info", return_value=None):
            result = manager.install("semgrep")
            assert result.success is False
            assert "Offline mode" in result.error_message

    def test_install_license_required(self, tmp_path):
        """Require license acceptance for licensed tools."""
        manager = ToolManager(cache_dir=tmp_path)

        with patch.object(manager, "get_tool_info", return_value=None):
            result = manager.install("codeql", accept_license=False)
            assert result.success is False
            assert result.license_required is True

    def test_install_license_accepted(self, tmp_path):
        """Proceed with installation when license accepted."""
        manager = ToolManager(cache_dir=tmp_path)

        with (
            patch.object(manager, "get_tool_info", return_value=None),
            patch.object(
                manager,
                "_install_binary",
                return_value=MagicMock(success=True),
            ),
        ):
            result = manager.install("codeql", accept_license=True)
            assert result.success is True


class TestPipInstallation:
    """Test pip-based installation."""

    def test_pip_install_success(self, tmp_path):
        """Successfully install via pip."""
        manager = ToolManager(cache_dir=tmp_path)
        config = ToolConfig(
            name="testtool",
            version="1.0.0",
            install_method=InstallMethod.PIP,
            pip_package="testtool",
        )

        mock_info = MagicMock()
        mock_info.name = "testtool"

        with (
            patch("subprocess.run") as mock_run,
            patch.object(manager, "_find_tool", return_value=Path("/usr/bin/testtool")),
            patch.object(manager, "get_tool_info", return_value=mock_info),
        ):
            mock_run.return_value = MagicMock(returncode=0)
            result = manager._install_pip(config)
            assert result.success is True

    def test_pip_install_failure(self, tmp_path):
        """Handle pip install failure."""
        manager = ToolManager(cache_dir=tmp_path)
        config = ToolConfig(name="testtool", pip_package="testtool")

        import subprocess

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                1, "pip", stderr=b"Error"
            )
            result = manager._install_pip(config)
            assert result.success is False
            assert "pip install failed" in result.error_message


class TestCacheManagement:
    """Test cache management functionality."""

    def test_get_cache_info_empty(self, tmp_path):
        """Get info for empty cache."""
        manager = ToolManager(cache_dir=tmp_path)
        info = manager.get_cache_info()

        assert info.cache_dir == tmp_path
        assert info.total_size_mb == 0.0
        assert info.tool_count == 0
        assert info.size_warning is False

    def test_get_cache_info_with_tools(self, tmp_path):
        """Get info with cached tools."""
        manager = ToolManager(cache_dir=tmp_path)

        # Create fake cached tool
        tool_dir = tmp_path / "semgrep"
        tool_dir.mkdir()
        (tool_dir / "binary").write_bytes(b"x" * 1024 * 1024)  # 1MB

        info = manager.get_cache_info()
        assert info.tool_count == 1
        assert info.total_size_mb > 0

    def test_cache_size_warning(self, tmp_path):
        """Warn when cache exceeds threshold."""
        manager = ToolManager(cache_dir=tmp_path)
        manager.CACHE_WARNING_THRESHOLD_MB = 1  # Set low for testing

        # Create large cached content
        tool_dir = tmp_path / "large_tool"
        tool_dir.mkdir()
        (tool_dir / "binary").write_bytes(b"x" * 2 * 1024 * 1024)  # 2MB

        info = manager.get_cache_info()
        assert info.size_warning is True


class TestUpdateChecking:
    """Test tool update checking."""

    def test_check_updates_not_installed(self, tmp_path):
        """No updates for non-installed tool."""
        manager = ToolManager(cache_dir=tmp_path)

        with patch.object(manager, "get_tool_info", return_value=None):
            has_update, version = manager.check_for_updates("semgrep")
            assert has_update is False

    def test_check_updates_up_to_date(self, tmp_path):
        """No updates when version matches."""
        manager = ToolManager(cache_dir=tmp_path)

        mock_info = MagicMock()
        mock_info.version = "1.45.0"  # Matches default config

        with patch.object(manager, "get_tool_info", return_value=mock_info):
            has_update, version = manager.check_for_updates("semgrep")
            assert has_update is False

    def test_check_updates_available(self, tmp_path):
        """Detect when update is available."""
        manager = ToolManager(cache_dir=tmp_path)

        mock_info = MagicMock()
        mock_info.version = "1.40.0"  # Older than config

        with patch.object(manager, "get_tool_info", return_value=mock_info):
            has_update, version = manager.check_for_updates("semgrep")
            assert has_update is True
            assert version == "1.45.0"


class TestOfflineMode:
    """Test offline mode functionality."""

    def test_offline_uses_cache_only(self, tmp_path):
        """Offline mode only uses cached tools."""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()

        # Create cached tool
        tool_dir = cache_dir / "semgrep" / "1.0.0"
        tool_dir.mkdir(parents=True)
        tool_exe = tool_dir / "semgrep"
        tool_exe.write_text("#!/bin/bash\necho 'semgrep'")
        tool_exe.chmod(0o755)

        manager = ToolManager(cache_dir=cache_dir, offline_mode=True)

        # Should find in cache even though not in PATH
        with patch("shutil.which", return_value=None):
            result = manager.install("semgrep")
            assert result.success is True
            assert result.tool_info.status == ToolStatus.OFFLINE_ONLY

    def test_offline_fails_if_not_cached(self, tmp_path):
        """Offline mode fails for uncached tools."""
        manager = ToolManager(cache_dir=tmp_path, offline_mode=True)

        result = manager.install("semgrep")
        assert result.success is False
        assert "Offline mode" in result.error_message


class TestPlatformDetection:
    """Test cross-platform support."""

    def test_linux_platform(self, tmp_path):
        """Detect Linux platform."""
        manager = ToolManager(cache_dir=tmp_path)

        with patch("platform.system", return_value="Linux"):
            assert manager._get_platform_key() == "linux"

    def test_macos_platform(self, tmp_path):
        """Detect macOS platform."""
        manager = ToolManager(cache_dir=tmp_path)

        with patch("platform.system", return_value="Darwin"):
            assert manager._get_platform_key() == "darwin"

    def test_windows_platform(self, tmp_path):
        """Detect Windows platform."""
        manager = ToolManager(cache_dir=tmp_path)

        with patch("platform.system", return_value="Windows"):
            assert manager._get_platform_key() == "win32"
