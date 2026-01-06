"""Tests for flowspec init template generation (MCP, VSCode extensions)."""

import json


class TestMCPJsonGeneration:
    """Test the MCP JSON generation functionality."""

    def test_generate_mcp_json_basic(self, tmp_path, monkeypatch):
        """Generate basic .mcp.json with backlog server."""
        from flowspec_cli import generate_mcp_json

        monkeypatch.chdir(tmp_path)
        result = generate_mcp_json(tmp_path)

        # Should return True when file is created
        assert result is True

        mcp_json = tmp_path / ".mcp.json"
        assert mcp_json.exists()

        config = json.loads(mcp_json.read_text())
        assert "mcpServers" in config
        assert "backlog" in config["mcpServers"]
        assert config["mcpServers"]["backlog"]["command"] == "backlog"

    def test_generate_mcp_json_python_project(self, tmp_path, monkeypatch):
        """Generate .mcp.json with the flowspec-security MCP server for Python projects."""
        from flowspec_cli import generate_mcp_json

        # Create a Python project marker
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")

        monkeypatch.chdir(tmp_path)
        result = generate_mcp_json(tmp_path)

        # Should return True when file is created
        assert result is True

        mcp_json = tmp_path / ".mcp.json"
        config = json.loads(mcp_json.read_text())

        assert "flowspec-security" in config["mcpServers"]
        assert config["mcpServers"]["flowspec-security"]["command"] == "uv"

    def test_generate_mcp_json_skips_existing(self, tmp_path, monkeypatch):
        """Skip .mcp.json generation if file already exists."""
        from flowspec_cli import generate_mcp_json

        # Create existing .mcp.json
        existing_config = {"mcpServers": {"custom": {"command": "custom"}}}
        mcp_json = tmp_path / ".mcp.json"
        mcp_json.write_text(json.dumps(existing_config))

        monkeypatch.chdir(tmp_path)
        result = generate_mcp_json(tmp_path)

        # Should return False when file already exists
        assert result is False

        # Should not be modified
        config = json.loads(mcp_json.read_text())
        assert "custom" in config["mcpServers"]
        assert "backlog" not in config["mcpServers"]


class TestUpdateMCPJson:
    """Test the update_mcp_json functionality for upgrade-repo."""

    def test_update_mcp_json_creates_new_file(self, tmp_path, monkeypatch):
        """Create .mcp.json with required servers when file doesn't exist."""
        from flowspec_cli import update_mcp_json

        monkeypatch.chdir(tmp_path)
        modified, changes = update_mcp_json(tmp_path)

        # Should return True when file is created
        assert modified is True

        # Check that required servers were added
        assert "backlog" in changes["added"]
        assert "github" in changes["added"]
        assert "serena" in changes["added"]

        # Verify file content
        mcp_json = tmp_path / ".mcp.json"
        assert mcp_json.exists()
        config = json.loads(mcp_json.read_text())
        assert "backlog" in config["mcpServers"]
        assert "github" in config["mcpServers"]
        assert "serena" in config["mcpServers"]

    def test_update_mcp_json_merges_with_existing(self, tmp_path, monkeypatch):
        """Merge required servers with existing .mcp.json, preserving custom config."""
        from flowspec_cli import update_mcp_json

        # Create existing .mcp.json with custom server
        existing_config = {
            "mcpServers": {
                "custom-server": {"command": "my-custom-command", "args": ["--flag"]},
                "backlog": {"command": "old-backlog", "args": []},  # Existing backlog
            }
        }
        mcp_json = tmp_path / ".mcp.json"
        mcp_json.write_text(json.dumps(existing_config))

        monkeypatch.chdir(tmp_path)
        modified, changes = update_mcp_json(tmp_path)

        # Should return True when new servers are added
        assert modified is True

        # Only github and serena should be added (backlog already exists)
        assert "github" in changes["added"]
        assert "serena" in changes["added"]
        assert "backlog" in changes["unchanged"]

        # Verify custom server is preserved
        config = json.loads(mcp_json.read_text())
        assert "custom-server" in config["mcpServers"]
        assert config["mcpServers"]["custom-server"]["command"] == "my-custom-command"

        # Existing backlog config should NOT be overwritten
        assert config["mcpServers"]["backlog"]["command"] == "old-backlog"

    def test_update_mcp_json_no_changes_when_complete(self, tmp_path, monkeypatch):
        """Return False when all required servers already exist."""
        from flowspec_cli import update_mcp_json, REQUIRED_MCP_SERVERS

        # Create .mcp.json with all required servers
        existing_config = {"mcpServers": dict(REQUIRED_MCP_SERVERS)}
        mcp_json = tmp_path / ".mcp.json"
        mcp_json.write_text(json.dumps(existing_config))

        monkeypatch.chdir(tmp_path)
        modified, changes = update_mcp_json(tmp_path)

        # Should return False when no changes needed
        assert modified is False
        assert len(changes["added"]) == 0
        assert "backlog" in changes["unchanged"]
        assert "github" in changes["unchanged"]
        assert "serena" in changes["unchanged"]

    def test_update_mcp_json_includes_recommended_servers(self, tmp_path, monkeypatch):
        """Include recommended servers when flag is set."""
        from flowspec_cli import update_mcp_json

        monkeypatch.chdir(tmp_path)
        modified, changes = update_mcp_json(tmp_path, include_recommended=True)

        assert modified is True

        # Check recommended servers were added
        assert "playwright-test" in changes["added"]
        assert "trivy" in changes["added"]
        assert "semgrep" in changes["added"]

        # Verify file content
        mcp_json = tmp_path / ".mcp.json"
        config = json.loads(mcp_json.read_text())
        assert "playwright-test" in config["mcpServers"]
        assert "trivy" in config["mcpServers"]
        assert "semgrep" in config["mcpServers"]

    def test_update_mcp_json_adds_python_server(self, tmp_path, monkeypatch):
        """Add flowspec-security server for Python projects."""
        from flowspec_cli import update_mcp_json

        # Create a Python project marker
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")

        monkeypatch.chdir(tmp_path)
        modified, changes = update_mcp_json(tmp_path)

        assert modified is True
        assert "flowspec-security" in changes["added"]

        # Verify file content
        mcp_json = tmp_path / ".mcp.json"
        config = json.loads(mcp_json.read_text())
        assert "flowspec-security" in config["mcpServers"]
        assert config["mcpServers"]["flowspec-security"]["command"] == "uv"

    def test_update_mcp_json_handles_corrupted_file(self, tmp_path, monkeypatch):
        """Handle corrupted .mcp.json gracefully by starting fresh."""
        from flowspec_cli import update_mcp_json

        # Create corrupted .mcp.json
        mcp_json = tmp_path / ".mcp.json"
        mcp_json.write_text("{ invalid json }")

        monkeypatch.chdir(tmp_path)
        modified, changes = update_mcp_json(tmp_path)

        # Should create valid config despite corrupted input
        assert modified is True
        assert "backlog" in changes["added"]

        # Verify valid JSON was written
        config = json.loads(mcp_json.read_text())
        assert "mcpServers" in config


class TestVSCodeExtensionsGeneration:
    """Test the VSCode extensions.json generation functionality."""

    def test_generate_vscode_extensions_basic(self, tmp_path, monkeypatch):
        """Generate basic extensions.json with base extensions."""
        from flowspec_cli import generate_vscode_extensions

        monkeypatch.chdir(tmp_path)
        result = generate_vscode_extensions(tmp_path)

        # Should return True when file is created
        assert result is True

        extensions_json = tmp_path / ".vscode" / "extensions.json"
        assert extensions_json.exists()

        config = json.loads(extensions_json.read_text())
        assert "recommendations" in config
        assert "github.copilot" in config["recommendations"]
        assert "github.copilot-chat" in config["recommendations"]

    def test_generate_vscode_extensions_python(self, tmp_path, monkeypatch):
        """Generate extensions.json with Python extensions for Python projects."""
        from flowspec_cli import generate_vscode_extensions

        # Create a Python project marker
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")

        monkeypatch.chdir(tmp_path)
        generate_vscode_extensions(tmp_path)

        extensions_json = tmp_path / ".vscode" / "extensions.json"
        config = json.loads(extensions_json.read_text())

        assert "ms-python.python" in config["recommendations"]
        assert "ms-python.vscode-pylance" in config["recommendations"]
        assert "charliermarsh.ruff" in config["recommendations"]

    def test_generate_vscode_extensions_javascript(self, tmp_path, monkeypatch):
        """Generate extensions.json with JS/TS extensions for JS projects."""
        from flowspec_cli import generate_vscode_extensions

        # Create a JS project marker
        (tmp_path / "package.json").write_text('{"name": "test"}\n')

        monkeypatch.chdir(tmp_path)
        generate_vscode_extensions(tmp_path)

        extensions_json = tmp_path / ".vscode" / "extensions.json"
        config = json.loads(extensions_json.read_text())

        assert "dbaeumer.vscode-eslint" in config["recommendations"]
        assert "esbenp.prettier-vscode" in config["recommendations"]

    def test_generate_vscode_extensions_docker(self, tmp_path, monkeypatch):
        """Generate extensions.json with Docker extension when Dockerfile exists."""
        from flowspec_cli import generate_vscode_extensions

        # Create a Dockerfile
        (tmp_path / "Dockerfile").write_text("FROM python:3.11\n")

        monkeypatch.chdir(tmp_path)
        generate_vscode_extensions(tmp_path)

        extensions_json = tmp_path / ".vscode" / "extensions.json"
        config = json.loads(extensions_json.read_text())

        assert "ms-azuretools.vscode-docker" in config["recommendations"]

    def test_generate_vscode_extensions_merges_existing(self, tmp_path, monkeypatch):
        """Merge with existing extensions.json recommendations."""
        from flowspec_cli import generate_vscode_extensions

        # Create existing extensions.json with custom extension
        vscode_dir = tmp_path / ".vscode"
        vscode_dir.mkdir()
        existing_config = {"recommendations": ["custom.extension"]}
        (vscode_dir / "extensions.json").write_text(json.dumps(existing_config))

        monkeypatch.chdir(tmp_path)
        result = generate_vscode_extensions(tmp_path)

        # Should return False when file already exists (was updated, not created)
        assert result is False

        extensions_json = tmp_path / ".vscode" / "extensions.json"
        config = json.loads(extensions_json.read_text())

        # Should have both custom and base extensions
        assert "custom.extension" in config["recommendations"]
        assert "github.copilot" in config["recommendations"]

    def test_generate_vscode_extensions_go(self, tmp_path, monkeypatch):
        """Generate extensions.json with Go extension for Go projects."""
        from flowspec_cli import generate_vscode_extensions

        # Create a Go project marker
        (tmp_path / "go.mod").write_text("module test\n")

        monkeypatch.chdir(tmp_path)
        generate_vscode_extensions(tmp_path)

        extensions_json = tmp_path / ".vscode" / "extensions.json"
        config = json.loads(extensions_json.read_text())

        assert "golang.go" in config["recommendations"]

    def test_generate_vscode_extensions_rust(self, tmp_path, monkeypatch):
        """Generate extensions.json with Rust extension for Rust projects."""
        from flowspec_cli import generate_vscode_extensions

        # Create a Rust project marker
        (tmp_path / "Cargo.toml").write_text('[package]\nname = "test"\n')

        monkeypatch.chdir(tmp_path)
        generate_vscode_extensions(tmp_path)

        extensions_json = tmp_path / ".vscode" / "extensions.json"
        config = json.loads(extensions_json.read_text())

        assert "rust-lang.rust-analyzer" in config["recommendations"]

    def test_generate_vscode_extensions_java(self, tmp_path, monkeypatch):
        """Generate extensions.json with Java extensions for Java projects."""
        from flowspec_cli import generate_vscode_extensions

        # Create a Java project marker (Maven)
        (tmp_path / "pom.xml").write_text(
            '<?xml version="1.0"?>\n<project></project>\n'
        )

        monkeypatch.chdir(tmp_path)
        generate_vscode_extensions(tmp_path)

        extensions_json = tmp_path / ".vscode" / "extensions.json"
        config = json.loads(extensions_json.read_text())

        assert "redhat.java" in config["recommendations"]
        assert "vscjava.vscode-java-pack" in config["recommendations"]

    def test_generate_vscode_extensions_docker_compose_yaml(
        self, tmp_path, monkeypatch
    ):
        """Generate extensions.json with Docker extension when docker-compose.yaml exists."""
        from flowspec_cli import generate_vscode_extensions

        # Create a docker-compose.yaml file (not .yml)
        (tmp_path / "docker-compose.yaml").write_text("version: '3'\n")

        monkeypatch.chdir(tmp_path)
        generate_vscode_extensions(tmp_path)

        extensions_json = tmp_path / ".vscode" / "extensions.json"
        config = json.loads(extensions_json.read_text())

        assert "ms-azuretools.vscode-docker" in config["recommendations"]

    def test_generate_vscode_extensions_docker_compose_yml(self, tmp_path, monkeypatch):
        """Generate extensions.json with Docker extension when docker-compose.yml exists."""
        from flowspec_cli import generate_vscode_extensions

        # Create a docker-compose.yml file (the common .yml variant)
        (tmp_path / "docker-compose.yml").write_text("version: '3'\n")

        monkeypatch.chdir(tmp_path)
        generate_vscode_extensions(tmp_path)

        extensions_json = tmp_path / ".vscode" / "extensions.json"
        config = json.loads(extensions_json.read_text())

        assert "ms-azuretools.vscode-docker" in config["recommendations"]
