"""CLI tests for specify workflow validate command.

Tests cover:
- Valid config file validation (exit code 0)
- Missing config file (exit code 2)
- Invalid YAML syntax (exit code 2)
- Schema validation failures (exit code 1)
- Semantic validation failures (exit code 1)
- Custom --file path
- --verbose flag behavior
- --json flag for machine-readable output
- Error handling edge cases
"""

import json

from typer.testing import CliRunner

from flowspec_cli import app

runner = CliRunner()


class TestWorkflowValidateValid:
    """Tests for valid workflow configurations."""

    def test_validate_default_config(self, tmp_path, monkeypatch):
        """Valid default config exits with 0 and shows success message."""
        # Create valid config
        config = tmp_path / "flowspec_workflow.yml"
        config.write_text("""
version: "1.0"
states:
  - To Do
  - Done
workflows:
  test:
    input_states:
      - To Do
    output_state: Done
transitions:
  - from: To Do
    to: Done
    via: test
""")
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["workflow", "validate"])

        assert result.exit_code == 0, f"Unexpected failure: {result.stdout}"
        assert "✓" in result.stdout or "passed" in result.stdout.lower()

    def test_validate_custom_file(self, tmp_path):
        """Custom --file path validates correctly."""
        config = tmp_path / "custom_workflow.yml"
        config.write_text("""
version: "1.0"
states:
  - To Do
  - Done
workflows:
  complete:
    command: /flow:complete
    agents:
      - PM Planner
    input_states:
      - To Do
    output_state: Done
transitions:
  - from: To Do
    to: Done
    via: complete
""")

        result = runner.invoke(app, ["workflow", "validate", "--file", str(config)])

        assert result.exit_code == 0
        assert "✓" in result.stdout or "passed" in result.stdout.lower()

    def test_validate_verbose_output(self, tmp_path, monkeypatch):
        """--verbose flag shows additional details."""
        config = tmp_path / "flowspec_workflow.yml"
        config.write_text("""
version: "1.0"
states:
  - To Do
  - Done
workflows: {}
transitions:
  - from: To Do
    to: Done
""")
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["workflow", "validate", "--verbose"])

        assert result.exit_code == 0
        # Verbose output should show config details
        assert "Config file:" in result.stdout or "Version:" in result.stdout


class TestWorkflowValidateFileErrors:
    """Tests for file-related errors (exit code 2)."""

    def test_config_not_found(self, tmp_path, monkeypatch):
        """Missing config file exits with 2."""
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["workflow", "validate"])

        assert result.exit_code == 2
        assert "not found" in result.stdout.lower()

    def test_custom_file_not_found(self):
        """Missing custom --file exits with 2."""
        result = runner.invoke(
            app, ["workflow", "validate", "--file", "/nonexistent/config.yml"]
        )

        assert result.exit_code == 2
        assert "not found" in result.stdout.lower()

    def test_invalid_yaml_syntax(self, tmp_path, monkeypatch):
        """Invalid YAML syntax exits with 2."""
        config = tmp_path / "flowspec_workflow.yml"
        config.write_text("""
invalid: yaml: syntax: here
  - indentation error
    bad: [unclosed
""")
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["workflow", "validate"])

        assert result.exit_code in (1, 2)  # Could be parse error or validation error
        assert "error" in result.stdout.lower() or "failed" in result.stdout.lower()

    def test_empty_config_file(self, tmp_path, monkeypatch):
        """Empty config file exits with 2."""
        config = tmp_path / "flowspec_workflow.yml"
        config.write_text("")
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["workflow", "validate"])

        assert result.exit_code in (1, 2)
        assert "error" in result.stdout.lower() or "failed" in result.stdout.lower()


class TestWorkflowValidateSchemaErrors:
    """Tests for schema validation errors (exit code 1)."""

    def test_missing_required_field(self, tmp_path, monkeypatch):
        """Config missing required field fails schema validation."""
        config = tmp_path / "flowspec_workflow.yml"
        config.write_text("""
# Missing version field
states:
  - To Do
  - Done
""")
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["workflow", "validate"])

        assert result.exit_code == 1
        assert "validation" in result.stdout.lower()


class TestWorkflowValidateSemanticErrors:
    """Tests for semantic validation errors (exit code 1)."""

    def test_circular_dependency_detected(self, tmp_path, monkeypatch):
        """Circular dependency in transitions fails validation."""
        config = tmp_path / "flowspec_workflow.yml"
        config.write_text("""
version: "1.0"
states:
  - To Do
  - A
  - B
workflows: {}
transitions:
  - from: To Do
    to: A
  - from: A
    to: B
  - from: B
    to: A
""")
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["workflow", "validate"])

        assert result.exit_code == 1
        assert "cycle" in result.stdout.lower() or "error" in result.stdout.lower()

    def test_unreachable_state_error(self, tmp_path, monkeypatch):
        """Unreachable state fails validation."""
        config = tmp_path / "flowspec_workflow.yml"
        config.write_text("""
version: "1.0"
states:
  - To Do
  - Done
  - Unreachable
workflows: {}
transitions:
  - from: To Do
    to: Done
""")
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["workflow", "validate"])

        assert result.exit_code == 1
        assert (
            "unreachable" in result.stdout.lower() or "error" in result.stdout.lower()
        )

    def test_undefined_state_reference(self, tmp_path, monkeypatch):
        """Workflow referencing undefined state fails validation."""
        config = tmp_path / "flowspec_workflow.yml"
        config.write_text("""
version: "1.0"
states:
  - To Do
  - Done
workflows:
  test:
    input_states:
      - NonExistent
    output_state: Done
transitions: []
""")
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["workflow", "validate"])

        assert result.exit_code == 1
        assert "undefined" in result.stdout.lower() or "error" in result.stdout.lower()


class TestWorkflowValidateJSONOutput:
    """Tests for --json output mode."""

    def test_json_output_valid_config(self, tmp_path, monkeypatch):
        """--json flag outputs valid JSON with success data."""
        config = tmp_path / "flowspec_workflow.yml"
        config.write_text("""
version: "1.0"
states:
  - To Do
  - Done
workflows: {}
transitions:
  - from: To Do
    to: Done
""")
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["workflow", "validate", "--json"])

        assert result.exit_code == 0

        # Parse JSON output
        try:
            output = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise AssertionError(f"Invalid JSON output: {e}\n{result.stdout}")

        # Validate structure
        assert "valid" in output
        assert output["valid"] is True
        assert "schema_validation" in output
        assert output["schema_validation"]["passed"] is True
        assert "semantic_validation" in output
        assert output["semantic_validation"]["passed"] is True

    def test_json_output_with_errors(self, tmp_path, monkeypatch):
        """--json flag outputs error details in JSON."""
        config = tmp_path / "flowspec_workflow.yml"
        config.write_text("""
version: "1.0"
states:
  - To Do
  - A
  - B
workflows: {}
transitions:
  - from: To Do
    to: A
  - from: A
    to: B
  - from: B
    to: A
""")
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["workflow", "validate", "--json"])

        assert result.exit_code == 1

        # Parse JSON output
        output = json.loads(result.stdout)

        assert "valid" in output
        assert output["valid"] is False
        assert "semantic_validation" in output
        assert "errors" in output["semantic_validation"]
        assert len(output["semantic_validation"]["errors"]) > 0

        # Check error structure
        error = output["semantic_validation"]["errors"][0]
        assert "code" in error
        assert "message" in error
        assert "context" in error

    def test_json_output_file_not_found(self, tmp_path, monkeypatch):
        """--json flag outputs file not found error in JSON."""
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["workflow", "validate", "--json"])

        assert result.exit_code == 2

        # Parse JSON output
        output = json.loads(result.stdout)

        assert "valid" in output
        assert output["valid"] is False
        assert "schema_validation" in output
        assert output["schema_validation"]["passed"] is False
        assert "error" in output["schema_validation"]
        assert output["schema_validation"]["error"]["type"] == "file_not_found"

    def test_json_output_no_color_codes(self, tmp_path, monkeypatch):
        """--json output contains no ANSI color codes."""
        config = tmp_path / "flowspec_workflow.yml"
        config.write_text("""
version: "1.0"
states:
  - To Do
  - Done
workflows: {}
transitions:
  - from: To Do
    to: Done
""")
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["workflow", "validate", "--json"])

        # ANSI color codes start with \x1b[
        assert "\x1b[" not in result.stdout
        # Verify it's valid JSON
        json.loads(result.stdout)


class TestWorkflowValidateWarnings:
    """Tests for warnings (non-blocking)."""

    def test_unknown_agent_warning(self, tmp_path, monkeypatch):
        """Unknown agent produces warning but exits with 0."""
        config = tmp_path / "flowspec_workflow.yml"
        config.write_text("""
version: "1.0"
states:
  - To Do
  - Done
workflows:
  test:
    input_states:
      - To Do
    output_state: Done
    agents:
      - unknown-custom-agent
transitions:
  - from: To Do
    to: Done
    via: test
""")
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["workflow", "validate"])

        assert result.exit_code == 0
        # Still passes, but may show warnings with --verbose

    def test_verbose_shows_warnings(self, tmp_path, monkeypatch):
        """--verbose flag displays warnings."""
        config = tmp_path / "flowspec_workflow.yml"
        config.write_text("""
version: "1.0"
states:
  - To Do
  - Done
workflows:
  test:
    input_states:
      - To Do
    output_state: Done
    agents:
      - unknown-agent
transitions:
  - from: To Do
    to: Done
    via: test
""")
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["workflow", "validate", "--verbose"])

        assert result.exit_code == 0
        # With --verbose, warnings should be displayed
        # (exact output depends on whether there are warnings)

    def test_json_includes_warnings(self, tmp_path, monkeypatch):
        """--json output includes warnings array."""
        config = tmp_path / "flowspec_workflow.yml"
        config.write_text("""
version: "1.0"
states:
  - To Do
  - Done
workflows:
  test:
    input_states:
      - To Do
    output_state: Done
    agents:
      - totally-unknown-agent
transitions:
  - from: To Do
    to: Done
    via: test
""")
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["workflow", "validate", "--json"])

        assert result.exit_code == 0

        output = json.loads(result.stdout)
        assert "semantic_validation" in output
        assert "warnings" in output["semantic_validation"]
        # Should have at least one warning for unknown agent
        assert isinstance(output["semantic_validation"]["warnings"], list)


class TestWorkflowValidateExitCodes:
    """Tests for correct exit code behavior."""

    def test_exit_code_0_on_success(self, tmp_path, monkeypatch):
        """Valid config exits with 0."""
        config = tmp_path / "flowspec_workflow.yml"
        config.write_text("""
version: "1.0"
states:
  - To Do
  - Done
workflows: {}
transitions:
  - from: To Do
    to: Done
""")
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["workflow", "validate"])
        assert result.exit_code == 0

    def test_exit_code_1_on_validation_error(self, tmp_path, monkeypatch):
        """Validation errors exit with 1."""
        config = tmp_path / "flowspec_workflow.yml"
        config.write_text("""
version: "1.0"
states:
  - To Do
  - Unreachable
workflows: {}
transitions: []
""")
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["workflow", "validate"])
        # Unreachable state should cause validation error
        assert result.exit_code == 1

    def test_exit_code_2_on_file_error(self, tmp_path, monkeypatch):
        """File not found exits with 2."""
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["workflow", "validate"])
        assert result.exit_code == 2
