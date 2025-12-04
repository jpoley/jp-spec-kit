"""Tests for tool dependency management models."""

from pathlib import Path

from specify_cli.security.tools.models import (
    DEFAULT_TOOL_CONFIGS,
    CacheInfo,
    InstallMethod,
    InstallResult,
    ToolConfig,
    ToolInfo,
    ToolStatus,
)


class TestToolStatus:
    """Test ToolStatus enum."""

    def test_all_statuses_defined(self):
        """All expected statuses are defined."""
        statuses = [s.value for s in ToolStatus]
        assert "not_installed" in statuses
        assert "installed" in statuses
        assert "update_available" in statuses
        assert "license_required" in statuses
        assert "offline_only" in statuses


class TestInstallMethod:
    """Test InstallMethod enum."""

    def test_all_methods_defined(self):
        """All expected install methods are defined."""
        methods = [m.value for m in InstallMethod]
        assert "pip" in methods
        assert "binary" in methods
        assert "docker" in methods
        assert "system" in methods


class TestToolConfig:
    """Test ToolConfig dataclass."""

    def test_minimal_config(self):
        """Create config with minimal required fields."""
        config = ToolConfig(name="test")
        assert config.name == "test"
        assert config.version is None
        assert config.install_method == InstallMethod.PIP
        assert config.license_check is False

    def test_full_config(self):
        """Create config with all fields."""
        config = ToolConfig(
            name="codeql",
            version="2.15.0",
            install_method=InstallMethod.BINARY,
            license_check=True,
            license_url="https://example.com/license",
            binary_urls={"linux": "https://example.com/linux.zip"},
            pip_package="codeql-cli",
            size_estimate_mb=400,
        )
        assert config.name == "codeql"
        assert config.version == "2.15.0"
        assert config.install_method == InstallMethod.BINARY
        assert config.license_check is True
        assert config.size_estimate_mb == 400


class TestToolInfo:
    """Test ToolInfo dataclass."""

    def test_create_tool_info(self):
        """Create ToolInfo with all fields."""
        info = ToolInfo(
            name="semgrep",
            version="1.45.0",
            path=Path("/usr/bin/semgrep"),
            status=ToolStatus.INSTALLED,
            install_method=InstallMethod.SYSTEM,
            size_mb=50.5,
        )
        assert info.name == "semgrep"
        assert info.version == "1.45.0"
        assert info.path == Path("/usr/bin/semgrep")
        assert info.status == ToolStatus.INSTALLED
        assert info.size_mb == 50.5


class TestInstallResult:
    """Test InstallResult dataclass."""

    def test_successful_result(self):
        """Create successful install result."""
        info = ToolInfo(
            name="test",
            version="1.0",
            path=Path("/bin/test"),
            status=ToolStatus.INSTALLED,
            install_method=InstallMethod.PIP,
        )
        result = InstallResult(success=True, tool_info=info)
        assert result.success is True
        assert result.tool_info is not None
        assert result.error_message is None

    def test_failed_result(self):
        """Create failed install result."""
        result = InstallResult(
            success=False,
            error_message="Installation failed: network error",
        )
        assert result.success is False
        assert result.tool_info is None
        assert "network error" in result.error_message

    def test_license_required_result(self):
        """Create license required result."""
        result = InstallResult(
            success=False,
            license_required=True,
            error_message="License acceptance required",
        )
        assert result.success is False
        assert result.license_required is True


class TestCacheInfo:
    """Test CacheInfo dataclass."""

    def test_empty_cache_info(self):
        """Create info for empty cache."""
        info = CacheInfo(
            cache_dir=Path("/tmp/cache"),
            total_size_mb=0.0,
            tool_count=0,
            tools=[],
        )
        assert info.total_size_mb == 0.0
        assert info.tool_count == 0
        assert info.size_warning is False

    def test_cache_with_warning(self):
        """Create info with size warning."""
        info = CacheInfo(
            cache_dir=Path("/tmp/cache"),
            total_size_mb=600.0,
            tool_count=2,
            tools=[],
            size_warning=True,
            warning_threshold_mb=500,
        )
        assert info.size_warning is True
        assert info.warning_threshold_mb == 500


class TestDefaultToolConfigs:
    """Test default tool configurations."""

    def test_semgrep_config(self):
        """Semgrep has correct default config."""
        config = DEFAULT_TOOL_CONFIGS["semgrep"]
        assert config.name == "semgrep"
        assert config.install_method == InstallMethod.PIP
        assert config.pip_package == "semgrep"
        assert config.version is not None

    def test_codeql_config(self):
        """CodeQL has correct default config."""
        config = DEFAULT_TOOL_CONFIGS["codeql"]
        assert config.name == "codeql"
        assert config.install_method == InstallMethod.BINARY
        assert config.license_check is True
        assert "linux" in config.binary_urls
        assert "darwin" in config.binary_urls
        assert "win32" in config.binary_urls

    def test_bandit_config(self):
        """Bandit has correct default config."""
        config = DEFAULT_TOOL_CONFIGS["bandit"]
        assert config.name == "bandit"
        assert config.install_method == InstallMethod.PIP
        assert config.pip_package == "bandit"
