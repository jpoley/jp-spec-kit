"""Tests for check-mcp-servers.sh script.

Verifies AC compliance for task-194: Create MCP Health Check Script.
"""

import json
import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def script_path():
    """Return path to the check-mcp-servers.sh script."""
    return Path(__file__).parent.parent / "scripts" / "check-mcp-servers.sh"


@pytest.fixture
def project_mcp_config():
    """Return path to the project's .mcp.json file."""
    return Path(__file__).parent.parent / ".mcp.json"


@pytest.fixture
def temp_mcp_config(tmp_path):
    """Create a temporary .mcp.json for testing."""
    config = {
        "mcpServers": {
            "test-server": {
                "command": "echo",
                "args": ["test"],
                "env": {},
                "description": "Test server that always works",
            }
        }
    }
    config_path = tmp_path / ".mcp.json"
    config_path.write_text(json.dumps(config))
    return config_path


@pytest.fixture
def invalid_mcp_config(tmp_path):
    """Create an invalid .mcp.json for testing error handling."""
    config_path = tmp_path / ".mcp.json"
    config_path.write_text("{ invalid json }")
    return config_path


@pytest.fixture
def empty_mcp_config(tmp_path):
    """Create an empty servers .mcp.json for testing."""
    config = {"mcpServers": {}}
    config_path = tmp_path / ".mcp.json"
    config_path.write_text(json.dumps(config))
    return config_path


@pytest.fixture
def missing_command_config(tmp_path):
    """Create a .mcp.json with a missing command for testing."""
    config = {
        "mcpServers": {
            "missing-cmd-server": {
                "command": "nonexistent_command_12345",
                "args": [],
                "description": "Server with missing command",
            }
        }
    }
    config_path = tmp_path / ".mcp.json"
    config_path.write_text(json.dumps(config))
    return config_path


class TestScriptExists:
    """AC #1: Script created at scripts/check-mcp-servers.sh"""

    def test_script_file_exists(self, script_path):
        """Verify the script file exists at the expected location."""
        assert script_path.exists(), f"Script not found at {script_path}"

    def test_script_is_executable(self, script_path):
        """Verify the script is executable."""
        assert script_path.stat().st_mode & 0o111, "Script is not executable"

    def test_script_has_shebang(self, script_path):
        """Verify the script has a proper shebang."""
        content = script_path.read_text()
        assert content.startswith("#!/"), "Script missing shebang"
        assert "bash" in content.split("\n")[0], "Script should use bash"


class TestServerConnectivity:
    """AC #2: Script tests connectivity for all configured MCP servers"""

    def test_checks_all_servers_in_config(self, script_path, project_mcp_config):
        """Verify script checks all servers defined in .mcp.json."""
        # Get list of servers from config
        config = json.loads(project_mcp_config.read_text())
        server_names = list(config.get("mcpServers", {}).keys())

        # Run script and capture output
        result = subprocess.run(
            [str(script_path), "-c", str(project_mcp_config)],
            capture_output=True,
            text=True,
        )

        # Each server should appear in output
        for server in server_names:
            assert server in result.stdout, f"Server '{server}' not checked"

    def test_checks_command_availability(self, script_path, temp_mcp_config):
        """Verify script checks if command is available."""
        result = subprocess.run(
            [str(script_path), "-c", str(temp_mcp_config)],
            capture_output=True,
            text=True,
        )
        # Should pass for 'echo' command which exists everywhere
        assert result.returncode == 0

    def test_verbose_shows_command_paths(self, script_path, temp_mcp_config):
        """Verify verbose mode shows command paths."""
        result = subprocess.run(
            [str(script_path), "-v", "-c", str(temp_mcp_config)],
            capture_output=True,
            text=True,
        )
        assert "Command path:" in result.stdout


class TestStatusReporting:
    """AC #3: Script reports success/failure status for each server"""

    def test_reports_pass_for_valid_servers(self, script_path, temp_mcp_config):
        """Verify script reports PASS for valid servers."""
        result = subprocess.run(
            [str(script_path), "-c", str(temp_mcp_config)],
            capture_output=True,
            text=True,
        )
        assert "[PASS]" in result.stdout

    def test_reports_fail_for_missing_commands(
        self, script_path, missing_command_config
    ):
        """Verify script reports FAIL for servers with missing commands."""
        result = subprocess.run(
            [str(script_path), "-c", str(missing_command_config)],
            capture_output=True,
            text=True,
        )
        assert "[FAIL]" in result.stdout
        assert result.returncode == 1

    def test_prints_summary(self, script_path, temp_mcp_config):
        """Verify script prints a summary at the end."""
        result = subprocess.run(
            [str(script_path), "-c", str(temp_mcp_config)],
            capture_output=True,
            text=True,
        )
        assert "Summary" in result.stdout
        assert "Total:" in result.stdout
        assert "Passed:" in result.stdout
        assert "Failed:" in result.stdout

    def test_exit_code_zero_on_success(self, script_path, temp_mcp_config):
        """Verify script exits with 0 when all servers pass."""
        result = subprocess.run(
            [str(script_path), "-c", str(temp_mcp_config)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_exit_code_one_on_failure(self, script_path, missing_command_config):
        """Verify script exits with 1 when servers fail."""
        result = subprocess.run(
            [str(script_path), "-c", str(missing_command_config)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1

    def test_exit_code_two_on_config_error(self, script_path, invalid_mcp_config):
        """Verify script exits with 2 on configuration errors."""
        result = subprocess.run(
            [str(script_path), "-c", str(invalid_mcp_config)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2


class TestDocumentation:
    """AC #4: Script documented in CLAUDE.md"""

    def test_claude_md_documents_script(self):
        """Verify CLAUDE.md or imported memory files document the MCP health check script."""
        project_root = Path(__file__).parent.parent
        claude_md_path = project_root / "CLAUDE.md"
        mcp_config_path = project_root / "memory" / "mcp-configuration.md"

        assert claude_md_path.exists(), "CLAUDE.md not found"

        claude_content = claude_md_path.read_text()

        # CLAUDE.md imports mcp-configuration.md which has the documentation
        has_mcp_import = "mcp-configuration.md" in claude_content

        # Check if mcp-configuration.md exists and has the script documented
        if mcp_config_path.exists():
            mcp_content = mcp_config_path.read_text()
            has_script_doc = "check-mcp-servers" in mcp_content
        else:
            has_script_doc = "check-mcp-servers" in claude_content

        assert has_mcp_import or has_script_doc, (
            "CLAUDE.md should import MCP config or document the health check script"
        )

    def test_mcp_config_memory_documents_script(self):
        """Verify memory/mcp-configuration.md documents the script."""
        mcp_config_path = (
            Path(__file__).parent.parent / "memory" / "mcp-configuration.md"
        )

        if not mcp_config_path.exists():
            pytest.skip("memory/mcp-configuration.md not found")

        content = mcp_config_path.read_text()

        # Check for script documentation
        assert "check-mcp-servers" in content, (
            "mcp-configuration.md should document the health check script"
        )
        assert "Health Check" in content, (
            "mcp-configuration.md should have Health Check section"
        )
        assert "./scripts/check-mcp-servers.sh" in content, (
            "mcp-configuration.md should show correct script path"
        )


class TestErrorHandling:
    """Test defensive error handling."""

    def test_handles_missing_config_file(self, script_path, tmp_path):
        """Verify script handles missing config file gracefully."""
        nonexistent = tmp_path / "nonexistent.json"
        result = subprocess.run(
            [str(script_path), "-c", str(nonexistent)], capture_output=True, text=True
        )
        assert result.returncode == 2
        assert "not found" in result.stdout or "not found" in result.stderr

    def test_handles_invalid_json(self, script_path, invalid_mcp_config):
        """Verify script handles invalid JSON gracefully."""
        result = subprocess.run(
            [str(script_path), "-c", str(invalid_mcp_config)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2
        assert "Invalid JSON" in result.stdout

    def test_handles_empty_servers_list(self, script_path, empty_mcp_config):
        """Verify script handles empty servers list."""
        result = subprocess.run(
            [str(script_path), "-c", str(empty_mcp_config)],
            capture_output=True,
            text=True,
        )
        # Should succeed with 0 servers checked
        assert result.returncode == 0
        assert "Total:    0" in result.stdout


class TestCommandLineOptions:
    """Test command line argument handling."""

    def test_help_option(self, script_path):
        """Verify --help option works."""
        result = subprocess.run(
            [str(script_path), "--help"], capture_output=True, text=True
        )
        assert result.returncode == 0
        assert "Usage:" in result.stdout

    def test_verbose_option(self, script_path, temp_mcp_config):
        """Verify -v option shows more detail."""
        result = subprocess.run(
            [str(script_path), "-v", "-c", str(temp_mcp_config)],
            capture_output=True,
            text=True,
        )
        assert "Description:" in result.stdout

    def test_quiet_option(self, script_path, temp_mcp_config):
        """Verify -q option reduces output."""
        quiet_result = subprocess.run(
            [str(script_path), "-q", "-c", str(temp_mcp_config)],
            capture_output=True,
            text=True,
        )
        normal_result = subprocess.run(
            [str(script_path), "-c", str(temp_mcp_config)],
            capture_output=True,
            text=True,
        )
        # Quiet should have less output
        assert len(quiet_result.stdout) <= len(normal_result.stdout)

    def test_custom_config_path(self, script_path, temp_mcp_config):
        """Verify -c option accepts custom config path."""
        result = subprocess.run(
            [str(script_path), "-c", str(temp_mcp_config)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


class TestIntegration:
    """Integration tests with real project configuration."""

    def test_checks_project_mcp_servers(self, script_path, project_mcp_config):
        """Verify script runs successfully on project's .mcp.json."""
        if not project_mcp_config.exists():
            pytest.skip("Project .mcp.json not found")

        result = subprocess.run(
            [str(script_path), "-c", str(project_mcp_config)],
            capture_output=True,
            text=True,
            timeout=30,  # Timeout in case something hangs
        )

        # Script should complete without crashing
        assert result.returncode in [0, 1], (
            f"Unexpected return code: {result.returncode}"
        )
        assert "Summary" in result.stdout
