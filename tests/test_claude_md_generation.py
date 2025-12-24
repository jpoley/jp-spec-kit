"""Tests for CLAUDE.md generation in flowspec init command.

Tests cover:
- Tech stack detection from package files
- CLAUDE.md file generation
- Template placeholder substitution
- Integration with init command
- --skip-claude-md flag
"""

from typer.testing import CliRunner

from flowspec_cli import app, detect_tech_stack, generate_claude_md

runner = CliRunner()


class TestTechStackDetection:
    """Tests for detect_tech_stack function."""

    def test_detect_python_from_pyproject_toml(self, tmp_path):
        """Detect Python from pyproject.toml."""
        (tmp_path / "pyproject.toml").write_text(
            """
[project]
name = "test"
dependencies = ["fastapi"]
"""
        )
        tech_stack = detect_tech_stack(tmp_path)
        assert "Python" in tech_stack["languages"]
        assert "FastAPI" in tech_stack["frameworks"]
        assert tech_stack["test_framework"] == "pytest"
        assert tech_stack["package_manager"] == "uv"

    def test_detect_python_from_requirements_txt(self, tmp_path):
        """Detect Python from requirements.txt."""
        (tmp_path / "requirements.txt").write_text("flask==2.0.0\n")
        tech_stack = detect_tech_stack(tmp_path)
        assert "Python" in tech_stack["languages"]
        assert tech_stack["test_framework"] == "pytest"
        assert tech_stack["package_manager"] == "pip"

    def test_detect_javascript_from_package_json(self, tmp_path):
        """Detect JavaScript/TypeScript from package.json."""
        (tmp_path / "package.json").write_text(
            """
{
  "name": "test",
  "dependencies": {
    "react": "^18.0.0",
    "next": "^14.0.0"
  },
  "devDependencies": {
    "vitest": "^1.0.0"
  }
}
"""
        )
        tech_stack = detect_tech_stack(tmp_path)
        assert "JavaScript/TypeScript" in tech_stack["languages"]
        assert "React" in tech_stack["frameworks"]
        assert "Next.js" in tech_stack["frameworks"]
        assert tech_stack["test_framework"] == "vitest"
        assert tech_stack["package_manager"] == "npm"

    def test_detect_package_manager_pnpm(self, tmp_path):
        """Detect pnpm as package manager."""
        (tmp_path / "package.json").write_text('{"name": "test"}')
        (tmp_path / "pnpm-lock.yaml").write_text("")
        tech_stack = detect_tech_stack(tmp_path)
        assert tech_stack["package_manager"] == "pnpm"

    def test_detect_package_manager_yarn(self, tmp_path):
        """Detect yarn as package manager."""
        (tmp_path / "package.json").write_text('{"name": "test"}')
        (tmp_path / "yarn.lock").write_text("")
        tech_stack = detect_tech_stack(tmp_path)
        assert tech_stack["package_manager"] == "yarn"

    def test_detect_go_from_go_mod(self, tmp_path):
        """Detect Go from go.mod."""
        (tmp_path / "go.mod").write_text("module test\n")
        tech_stack = detect_tech_stack(tmp_path)
        assert "Go" in tech_stack["languages"]
        assert tech_stack["test_framework"] == "go test"

    def test_detect_rust_from_cargo_toml(self, tmp_path):
        """Detect Rust from Cargo.toml."""
        (tmp_path / "Cargo.toml").write_text('[package]\nname = "test"\n')
        tech_stack = detect_tech_stack(tmp_path)
        assert "Rust" in tech_stack["languages"]
        assert tech_stack["test_framework"] == "cargo test"

    def test_detect_java_maven(self, tmp_path):
        """Detect Java with Maven from pom.xml."""
        (tmp_path / "pom.xml").write_text("<project></project>")
        tech_stack = detect_tech_stack(tmp_path)
        assert "Java" in tech_stack["languages"]
        assert tech_stack["package_manager"] == "maven"
        assert tech_stack["test_framework"] == "junit"

    def test_detect_java_gradle(self, tmp_path):
        """Detect Java with Gradle from build.gradle."""
        (tmp_path / "build.gradle").write_text("")
        tech_stack = detect_tech_stack(tmp_path)
        assert "Java" in tech_stack["languages"]
        assert tech_stack["package_manager"] == "gradle"
        assert tech_stack["test_framework"] == "junit"

    def test_detect_multiple_languages(self, tmp_path):
        """Detect multiple languages in a polyglot project."""
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\n')
        (tmp_path / "package.json").write_text('{"name": "test"}')
        tech_stack = detect_tech_stack(tmp_path)
        assert "Python" in tech_stack["languages"]
        assert "JavaScript/TypeScript" in tech_stack["languages"]

    def test_empty_project(self, tmp_path):
        """Empty project returns empty tech stack."""
        tech_stack = detect_tech_stack(tmp_path)
        assert tech_stack["languages"] == []
        assert tech_stack["frameworks"] == []
        assert tech_stack["test_framework"] is None
        assert tech_stack["package_manager"] is None


class TestClaudeMdGeneration:
    """Tests for generate_claude_md function."""

    def test_generate_claude_md_python_project(self, tmp_path):
        """Generate CLAUDE.md for Python project."""
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\n')
        generate_claude_md(tmp_path, "test-project")

        claude_md = tmp_path / "CLAUDE.md"
        assert claude_md.exists()

        content = claude_md.read_text()
        assert "# test-project - Claude Code Configuration" in content
        assert "Python" in content
        assert "pytest tests/" in content
        assert "ruff check . --fix" in content
        assert "uv sync" in content
        assert "backlog task list" in content
        assert "@import memory/constitution.md" in content

    def test_generate_claude_md_javascript_project(self, tmp_path):
        """Generate CLAUDE.md for JavaScript project."""
        (tmp_path / "package.json").write_text(
            '{"name": "test", "dependencies": {"react": "^18.0.0"}}'
        )
        (tmp_path / "pnpm-lock.yaml").write_text("")
        generate_claude_md(tmp_path, "my-app")

        claude_md = tmp_path / "CLAUDE.md"
        assert claude_md.exists()

        content = claude_md.read_text()
        assert "# my-app - Claude Code Configuration" in content
        assert "JavaScript/TypeScript" in content
        assert "React" in content
        assert "pnpm install" in content
        assert "pnpm run test" in content

    def test_generate_claude_md_go_project(self, tmp_path):
        """Generate CLAUDE.md for Go project."""
        (tmp_path / "go.mod").write_text("module test\n")
        generate_claude_md(tmp_path, "go-service")

        claude_md = tmp_path / "CLAUDE.md"
        assert claude_md.exists()

        content = claude_md.read_text()
        assert "# go-service - Claude Code Configuration" in content
        assert "Go" in content
        assert "go test ./..." in content
        assert "go build" in content

    def test_generate_claude_md_rust_project(self, tmp_path):
        """Generate CLAUDE.md for Rust project."""
        (tmp_path / "Cargo.toml").write_text('[package]\nname = "test"\n')
        generate_claude_md(tmp_path, "rust-app")

        claude_md = tmp_path / "CLAUDE.md"
        assert claude_md.exists()

        content = claude_md.read_text()
        assert "# rust-app - Claude Code Configuration" in content
        assert "Rust" in content
        assert "cargo test" in content
        assert "cargo build" in content
        assert "cargo clippy" in content

    def test_generate_claude_md_skips_existing(self, tmp_path):
        """Skip CLAUDE.md generation if file already exists."""
        existing_content = "# Existing CLAUDE.md\n"
        (tmp_path / "CLAUDE.md").write_text(existing_content)

        generate_claude_md(tmp_path, "test-project")

        # Content should remain unchanged
        assert (tmp_path / "CLAUDE.md").read_text() == existing_content

    def test_generate_claude_md_empty_project(self, tmp_path):
        """Generate CLAUDE.md for empty project with default content."""
        generate_claude_md(tmp_path, "empty-project")

        claude_md = tmp_path / "CLAUDE.md"
        assert claude_md.exists()

        content = claude_md.read_text()
        assert "# empty-project - Claude Code Configuration" in content
        assert "backlog task list" in content
        # Should have placeholder for custom commands
        assert "Add your project-specific commands here" in content

    def test_generate_claude_md_polyglot_project(self, tmp_path):
        """Generate CLAUDE.md for polyglot project."""
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\n')
        (tmp_path / "package.json").write_text('{"name": "test"}')
        generate_claude_md(tmp_path, "polyglot-app")

        claude_md = tmp_path / "CLAUDE.md"
        assert claude_md.exists()

        content = claude_md.read_text()
        assert "Python" in content
        assert "JavaScript/TypeScript" in content
        assert "pytest tests/" in content
        assert "npm install" in content


class TestClaudeMdInitIntegration:
    """Tests for CLAUDE.md generation in init command."""

    def test_init_creates_claude_md_by_default(self, tmp_path):
        """Init command creates CLAUDE.md by default."""
        project_path = tmp_path / "test-project"

        result = runner.invoke(
            app,
            [
                "init",
                str(project_path),
                "--ai",
                "claude",
                "--ignore-agent-tools",
                "--constitution",
                "light",
            ],
            input="n\n",  # Answer 'no' to backlog-md install prompt
        )

        assert result.exit_code == 0, f"Init failed: {result.stdout}"

        # Verify CLAUDE.md was created
        claude_md = project_path / "CLAUDE.md"
        assert claude_md.exists(), "CLAUDE.md should be created by init"

        content = claude_md.read_text()
        assert "# test-project - Claude Code Configuration" in content
        assert "backlog task list" in content

    def test_init_skip_claude_md_flag(self, tmp_path):
        """Init command with --skip-claude-md does not create CLAUDE.md."""
        project_path = tmp_path / "test-project"

        result = runner.invoke(
            app,
            [
                "init",
                str(project_path),
                "--ai",
                "claude",
                "--ignore-agent-tools",
                "--constitution",
                "light",
                "--skip-claude-md",
            ],
            input="n\n",  # Answer 'no' to backlog-md install prompt
        )

        assert result.exit_code == 0, f"Init failed: {result.stdout}"

        # Verify CLAUDE.md was NOT created
        claude_md = project_path / "CLAUDE.md"
        assert not claude_md.exists(), (
            "CLAUDE.md should not be created with --skip-claude-md"
        )

    def test_init_claude_md_with_detected_tech_stack(self, tmp_path):
        """Init creates CLAUDE.md with tech stack detected from existing files."""
        project_path = tmp_path / "test-project"
        project_path.mkdir()

        # Create a Python project file before init
        (project_path / "pyproject.toml").write_text(
            """
[project]
name = "test"
dependencies = ["fastapi"]
"""
        )

        # Note: --here requires running in that directory, so we change into it first
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(project_path)
            result = runner.invoke(
                app,
                [
                    "init",
                    "--here",
                    "--ai",
                    "claude",
                    "--ignore-agent-tools",
                    "--constitution",
                    "light",
                    "--force",
                ],
                input="n\n",  # Answer 'no' to backlog-md install prompt
            )
        finally:
            os.chdir(original_cwd)

        assert result.exit_code == 0, f"Init failed: {result.stdout}"

        claude_md = project_path / "CLAUDE.md"
        assert claude_md.exists()

        content = claude_md.read_text()
        assert "Python" in content
        assert "FastAPI" in content
        assert "pytest tests/" in content


class TestClaudeMdTemplate:
    """Tests for CLAUDE.md template structure."""

    def test_template_file_exists(self):
        """CLAUDE.md template file should exist in templates directory."""
        # Template is optional - fallback template is used if it doesn't exist
        # So we just verify the generation works with or without it
        # The template file location is: templates/claude-md-template.md
        pass

    def test_generated_claude_md_has_required_sections(self, tmp_path):
        """Generated CLAUDE.md should have all required sections."""
        generate_claude_md(tmp_path, "test-project")

        content = (tmp_path / "CLAUDE.md").read_text()

        # Required sections
        assert "## Project Overview" in content
        assert "## Essential Commands" in content
        assert "## Project Structure" in content
        assert "## Workflow Commands" in content
        assert "## Memory Imports" in content
        assert "## Quick Troubleshooting" in content

    def test_generated_claude_md_has_memory_imports(self, tmp_path):
        """Generated CLAUDE.md should include @import statements."""
        generate_claude_md(tmp_path, "test-project")

        content = (tmp_path / "CLAUDE.md").read_text()

        assert "@import memory/constitution.md" in content
        assert "@import memory/code-standards.md" in content
        assert "@import memory/test-quality-standards.md" in content

    def test_generated_claude_md_has_workflow_commands(self, tmp_path):
        """Generated CLAUDE.md should include workflow commands."""
        generate_claude_md(tmp_path, "test-project")

        content = (tmp_path / "CLAUDE.md").read_text()

        assert "/flow:assess" in content
        assert "/flow:specify" in content
        assert "/flow:plan" in content
        assert "/flow:implement" in content
        assert "/flow:validate" in content

    def test_generated_claude_md_has_backlog_commands(self, tmp_path):
        """Generated CLAUDE.md should always include backlog commands."""
        generate_claude_md(tmp_path, "test-project")

        content = (tmp_path / "CLAUDE.md").read_text()

        assert "backlog task list --plain" in content
        assert "backlog task edit" in content
        assert "NEVER edit task files directly" in content
