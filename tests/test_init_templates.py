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
        """Generate .mcp.json with Python-specific servers for Python projects."""
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
