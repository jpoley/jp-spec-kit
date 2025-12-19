"""Tests for template placeholder detection and replacement."""

import json
from datetime import datetime


from flowspec_cli.placeholders import (
    detect_languages_and_frameworks,
    detect_linting_tools,
    detect_project_metadata,
    detect_project_name,
    replace_placeholders,
)


class TestDetectProjectName:
    """Tests for detect_project_name function."""

    def test_from_pyproject_toml(self, tmp_path):
        """Should detect project name from pyproject.toml."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            """
[project]
name = "my-awesome-project"
version = "1.0.0"
"""
        )

        result = detect_project_name(tmp_path)
        assert result == "my-awesome-project"

    def test_from_pyproject_toml_regex_fallback(self, tmp_path):
        """Should parse pyproject.toml with regex if tomllib fails."""
        pyproject = tmp_path / "pyproject.toml"
        # Write TOML with name but outside [project] section (valid TOML, wrong structure)
        # This will parse as valid TOML but won't have project.name, triggering regex fallback
        pyproject.write_text(
            """
# Some config
name = "test-project"

[tool.something]
key = "value"
"""
        )

        result = detect_project_name(tmp_path)
        assert result == "test-project"

    def test_from_package_json(self, tmp_path):
        """Should detect project name from package.json."""
        package_json = tmp_path / "package.json"
        package_json.write_text(
            json.dumps({"name": "my-node-project", "version": "1.0.0"})
        )

        result = detect_project_name(tmp_path)
        assert result == "my-node-project"

    def test_from_cargo_toml(self, tmp_path):
        """Should detect project name from Cargo.toml."""
        cargo_toml = tmp_path / "Cargo.toml"
        cargo_toml.write_text(
            """
[package]
name = "my-rust-project"
version = "0.1.0"
"""
        )

        result = detect_project_name(tmp_path)
        assert result == "my-rust-project"

    def test_from_go_mod(self, tmp_path):
        """Should detect project name from go.mod."""
        go_mod = tmp_path / "go.mod"
        go_mod.write_text(
            """
module github.com/user/my-go-project

go 1.21
"""
        )

        result = detect_project_name(tmp_path)
        assert result == "my-go-project"

    def test_fallback_to_directory_name(self, tmp_path):
        """Should use directory name when no config files exist."""
        result = detect_project_name(tmp_path)
        assert result == tmp_path.name

    def test_priority_pyproject_over_package_json(self, tmp_path):
        """pyproject.toml should take priority over package.json."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "python-project"\n')

        package_json = tmp_path / "package.json"
        package_json.write_text(json.dumps({"name": "node-project"}))

        result = detect_project_name(tmp_path)
        assert result == "python-project"


class TestDetectLanguagesAndFrameworks:
    """Tests for detect_languages_and_frameworks function."""

    def test_python_detection(self, tmp_path):
        """Should detect Python from pyproject.toml."""
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\n')

        result = detect_languages_and_frameworks(tmp_path)
        assert "Python 3.11+" in result

    def test_fastapi_detection(self, tmp_path):
        """Should detect FastAPI from dependencies."""
        (tmp_path / "pyproject.toml").write_text(
            """
[project]
name = "test"
dependencies = ["fastapi", "uvicorn"]
"""
        )

        result = detect_languages_and_frameworks(tmp_path)
        assert "Python 3.11+" in result
        assert "FastAPI" in result

    def test_flask_detection(self, tmp_path):
        """Should detect Flask from dependencies."""
        (tmp_path / "pyproject.toml").write_text(
            """
[project]
name = "test"
dependencies = ["flask"]
"""
        )

        result = detect_languages_and_frameworks(tmp_path)
        assert "Flask" in result

    def test_typescript_detection(self, tmp_path):
        """Should detect TypeScript from package.json."""
        (tmp_path / "package.json").write_text(
            json.dumps({"name": "test", "devDependencies": {"typescript": "^5.0.0"}})
        )

        result = detect_languages_and_frameworks(tmp_path)
        assert "TypeScript" in result

    def test_react_detection(self, tmp_path):
        """Should detect React from package.json."""
        (tmp_path / "package.json").write_text(
            json.dumps({"name": "test", "dependencies": {"react": "^18.0.0"}})
        )

        result = detect_languages_and_frameworks(tmp_path)
        assert "React" in result

    def test_nextjs_detection(self, tmp_path):
        """Should detect Next.js from package.json."""
        (tmp_path / "package.json").write_text(
            json.dumps({"name": "test", "dependencies": {"next": "^14.0.0"}})
        )

        result = detect_languages_and_frameworks(tmp_path)
        assert "Next.js" in result

    def test_rust_detection(self, tmp_path):
        """Should detect Rust from Cargo.toml."""
        (tmp_path / "Cargo.toml").write_text('[package]\nname = "test"\n')

        result = detect_languages_and_frameworks(tmp_path)
        assert "Rust" in result

    def test_go_detection(self, tmp_path):
        """Should detect Go from go.mod."""
        (tmp_path / "go.mod").write_text("module test\n")

        result = detect_languages_and_frameworks(tmp_path)
        assert "Go" in result

    def test_no_languages_detected(self, tmp_path):
        """Should return TODO comment when no languages detected."""
        result = detect_languages_and_frameworks(tmp_path)
        assert "TODO" in result


class TestDetectLintingTools:
    """Tests for detect_linting_tools function."""

    def test_ruff_from_ruff_toml(self, tmp_path):
        """Should detect ruff from ruff.toml."""
        (tmp_path / "ruff.toml").write_text("line-length = 88\n")

        result = detect_linting_tools(tmp_path)
        assert "ruff" in result

    def test_ruff_from_pyproject_toml(self, tmp_path):
        """Should detect ruff from pyproject.toml."""
        (tmp_path / "pyproject.toml").write_text("[tool.ruff]\nline-length = 88\n")

        result = detect_linting_tools(tmp_path)
        assert "ruff" in result

    def test_black_detection(self, tmp_path):
        """Should detect black from pyproject.toml."""
        (tmp_path / "pyproject.toml").write_text("[tool.black]\nline-length = 88\n")

        result = detect_linting_tools(tmp_path)
        assert "black" in result

    def test_mypy_detection(self, tmp_path):
        """Should detect mypy from pyproject.toml."""
        (tmp_path / "pyproject.toml").write_text("[tool.mypy]\nstrict = true\n")

        result = detect_linting_tools(tmp_path)
        assert "mypy" in result

    def test_eslint_detection(self, tmp_path):
        """Should detect eslint from .eslintrc."""
        (tmp_path / ".eslintrc").write_text('{"extends": "eslint:recommended"}\n')

        result = detect_linting_tools(tmp_path)
        assert "eslint" in result

    def test_prettier_detection(self, tmp_path):
        """Should detect prettier from .prettierrc."""
        (tmp_path / ".prettierrc").write_text('{"semi": false}\n')

        result = detect_linting_tools(tmp_path)
        assert "prettier" in result

    def test_typescript_compiler_detection(self, tmp_path):
        """Should detect tsc from tsconfig.json."""
        (tmp_path / "tsconfig.json").write_text('{"compilerOptions": {}}\n')

        result = detect_linting_tools(tmp_path)
        assert "tsc" in result

    def test_rust_tools_detection(self, tmp_path):
        """Should detect rustfmt and clippy from Cargo.toml."""
        (tmp_path / "Cargo.toml").write_text('[package]\nname = "test"\n')

        result = detect_linting_tools(tmp_path)
        assert "rustfmt" in result
        assert "clippy" in result

    def test_go_tools_detection(self, tmp_path):
        """Should detect gofmt and golangci-lint from go.mod."""
        (tmp_path / "go.mod").write_text("module test\n")

        result = detect_linting_tools(tmp_path)
        assert "gofmt" in result
        assert "golangci-lint" in result

    def test_no_tools_detected(self, tmp_path):
        """Should return TODO comment when no tools detected."""
        result = detect_linting_tools(tmp_path)
        assert "TODO" in result


class TestDetectProjectMetadata:
    """Tests for detect_project_metadata function."""

    def test_detects_all_fields(self, tmp_path):
        """Should detect all metadata fields."""
        (tmp_path / "pyproject.toml").write_text(
            """
[project]
name = "test-project"
dependencies = ["fastapi"]

[tool.ruff]
line-length = 88
"""
        )

        metadata = detect_project_metadata(tmp_path)

        assert metadata["PROJECT_NAME"] == "test-project"
        assert "Python 3.11+" in metadata["LANGUAGES_AND_FRAMEWORKS"]
        assert "FastAPI" in metadata["LANGUAGES_AND_FRAMEWORKS"]
        assert "ruff" in metadata["LINTING_TOOLS"]
        assert "DATE" in metadata

        # Verify date format (YYYY-MM-DD)
        date_str = metadata["DATE"]
        datetime.strptime(date_str, "%Y-%m-%d")  # Will raise if invalid

    def test_uses_override_name(self, tmp_path):
        """Should use project_name_override if provided."""
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "original"\n')

        metadata = detect_project_metadata(tmp_path, project_name_override="override")

        assert metadata["PROJECT_NAME"] == "override"

    def test_date_format(self, tmp_path):
        """DATE should be in YYYY-MM-DD format."""
        metadata = detect_project_metadata(tmp_path)

        # Should not raise
        datetime.strptime(metadata["DATE"], "%Y-%m-%d")


class TestReplacePlaceholders:
    """Tests for replace_placeholders function."""

    def test_replaces_detected_placeholders(self):
        """Should replace placeholders with metadata values."""
        content = "# [PROJECT_NAME] Project\nLanguages: [LANGUAGES_AND_FRAMEWORKS]"
        metadata = {
            "PROJECT_NAME": "MyProject",
            "LANGUAGES_AND_FRAMEWORKS": "Python 3.11+, FastAPI",
        }

        result = replace_placeholders(content, metadata)

        assert "# MyProject Project" in result
        assert "Languages: Python 3.11+, FastAPI" in result

    def test_marks_undetected_placeholders(self):
        """Should mark undetected placeholders with TODO comments."""
        content = "Project: [PROJECT_NAME]\nOwner: [PROJECT_OWNER]"
        metadata = {"PROJECT_NAME": "MyProject"}

        result = replace_placeholders(content, metadata)

        assert "Project: MyProject" in result
        assert "<!-- TODO: Replace [PROJECT_OWNER] -->" in result
        assert "[PROJECT_OWNER]" in result

    def test_multiple_occurrences(self):
        """Should replace all occurrences of a placeholder."""
        content = "[PROJECT_NAME] is a great project. [PROJECT_NAME] rocks!"
        metadata = {"PROJECT_NAME": "Flowspec"}

        result = replace_placeholders(content, metadata)

        assert result.count("Flowspec") == 2
        assert "[PROJECT_NAME]" not in result

    def test_preserves_content_without_placeholders(self):
        """Should preserve content that doesn't have placeholders."""
        content = "This is normal text without any placeholders."
        metadata = {"PROJECT_NAME": "Test"}

        result = replace_placeholders(content, metadata)

        assert result == content

    def test_handles_empty_metadata(self):
        """Should handle empty metadata gracefully."""
        content = "Project: [PROJECT_NAME]"
        metadata = {}

        result = replace_placeholders(content, metadata)

        assert "<!-- TODO: Replace [PROJECT_NAME] -->" in result

    def test_replaces_date_placeholder(self):
        """Should replace DATE placeholder with current date."""
        content = "Created: [DATE]"
        metadata = {"DATE": "2025-12-19"}

        result = replace_placeholders(content, metadata)

        assert "Created: 2025-12-19" in result
        assert "[DATE]" not in result

    def test_does_not_double_mark_todos(self):
        """Should not add TODO comment if placeholder already has one."""
        content = "<!-- TODO: Fill this --> [CUSTOM_FIELD]"
        metadata = {}

        result = replace_placeholders(content, metadata)

        # Should only have one TODO comment (the existing one)
        assert result.count("TODO") == 1


class TestIntegration:
    """Integration tests for placeholder system."""

    def test_full_workflow_python_project(self, tmp_path):
        """Test complete workflow for a Python project."""
        # Set up a Python project
        (tmp_path / "pyproject.toml").write_text(
            """
[project]
name = "my-api"
dependencies = ["fastapi", "pydantic"]

[tool.ruff]
line-length = 100
"""
        )

        # Detect metadata
        metadata = detect_project_metadata(tmp_path)

        # Create a template
        template = """# [PROJECT_NAME] Constitution

## Languages
[LANGUAGES_AND_FRAMEWORKS]

## Linting
[LINTING_TOOLS]

## Custom Section
[CUSTOM_PRINCIPLE]

Created: [DATE]
"""

        # Replace placeholders
        result = replace_placeholders(template, metadata)

        # Verify replacements
        assert "# my-api Constitution" in result
        assert "Python 3.11+" in result
        assert "FastAPI" in result
        assert "ruff" in result
        assert "<!-- TODO: Replace [CUSTOM_PRINCIPLE] -->" in result
        assert metadata["DATE"] in result

    def test_full_workflow_typescript_project(self, tmp_path):
        """Test complete workflow for a TypeScript project."""
        # Set up a TypeScript project
        (tmp_path / "package.json").write_text(
            json.dumps(
                {
                    "name": "my-frontend",
                    "dependencies": {"react": "^18.0.0", "next": "^14.0.0"},
                    "devDependencies": {"typescript": "^5.0.0"},
                }
            )
        )
        (tmp_path / ".eslintrc").write_text("{}")
        (tmp_path / "tsconfig.json").write_text("{}")

        # Detect metadata
        metadata = detect_project_metadata(tmp_path)

        # Create a template
        template = "# [PROJECT_NAME]\nStack: [LANGUAGES_AND_FRAMEWORKS]\nTools: [LINTING_TOOLS]"

        # Replace placeholders
        result = replace_placeholders(template, metadata)

        # Verify replacements
        assert "# my-frontend" in result
        assert "TypeScript" in result
        assert "React" in result
        assert "Next.js" in result
        assert "eslint" in result
        assert "tsc" in result
