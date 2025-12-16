"""Tests for flowspec gate command."""

from typer.testing import CliRunner

from flowspec_cli import app


class TestGateCommand:
    """Test the flowspec gate command."""

    def test_gate_passes_high_quality_spec(self, tmp_path, monkeypatch):
        """Gate passes when spec quality is above threshold."""
        # Create a high-quality spec that includes all required sections
        specify_dir = tmp_path / ".specify"
        specify_dir.mkdir()
        spec = specify_dir / "spec.md"
        spec.write_text("""# Feature: User Authentication

## Description
This feature enables secure user authentication using email and password credentials
with session management capabilities.

## User Story
As a user, I need secure authentication so that I can safely access the system
and protect my account from unauthorized access.

## Problem Statement
Users need a secure authentication mechanism to access the system while ensuring
their credentials and sessions are properly protected.

## Technical Requirements
1. Email validation must check format using standard RFC 5322 pattern
2. Password strength must require minimum 8 characters including uppercase, lowercase, and numbers
3. Session tokens must use cryptographically secure random generation
4. Sessions must expire after 24 hours of inactivity
5. All authentication endpoints must be tested using pytest
6. Code must be formatted using ruff

## Acceptance Criteria
- [ ] Login form validates email format according to RFC 5322
- [ ] Password requires minimum 8 characters with mixed case and numbers
- [ ] Session token is cryptographically generated and stored securely
- [ ] Session expires after exactly 24 hours
- [ ] All endpoints have pytest test coverage
- [ ] Code is formatted with ruff
""")

        # Change to the tmp_path directory
        monkeypatch.chdir(tmp_path)

        runner = CliRunner()
        result = runner.invoke(app, ["gate"])
        assert result.exit_code == 0
        assert "PASSED" in result.output or "passed" in result.output.lower()

    def test_gate_fails_low_quality_spec(self, tmp_path, monkeypatch):
        """Gate fails when spec quality is below threshold."""
        specify_dir = tmp_path / ".specify"
        specify_dir.mkdir()
        spec = specify_dir / "spec.md"
        spec.write_text("# TODO\nSome vague stuff maybe later")

        monkeypatch.chdir(tmp_path)

        runner = CliRunner()
        result = runner.invoke(app, ["gate"])
        assert result.exit_code == 1
        assert "FAILED" in result.output or "failed" in result.output.lower()

    def test_gate_force_bypasses_failure(self, tmp_path, monkeypatch):
        """--force flag allows bypassing failed gate."""
        specify_dir = tmp_path / ".specify"
        specify_dir.mkdir()
        spec = specify_dir / "spec.md"
        spec.write_text("# TODO\nVague")

        monkeypatch.chdir(tmp_path)

        runner = CliRunner()
        result = runner.invoke(app, ["gate", "--force"])
        assert result.exit_code == 0
        assert "bypass" in result.output.lower() or "force" in result.output.lower()

    def test_gate_custom_threshold(self, tmp_path, monkeypatch):
        """--threshold flag overrides config threshold."""
        specify_dir = tmp_path / ".specify"
        specify_dir.mkdir()
        spec = specify_dir / "spec.md"
        spec.write_text("# Feature\nBasic description")

        monkeypatch.chdir(tmp_path)

        runner = CliRunner()
        # Very low threshold should pass
        result = runner.invoke(app, ["gate", "--threshold", "10"])
        assert result.exit_code == 0

    def test_gate_no_spec_file_error(self, tmp_path, monkeypatch):
        """Gate returns error code when spec.md doesn't exist."""
        monkeypatch.chdir(tmp_path)

        runner = CliRunner()
        result = runner.invoke(app, ["gate"])
        assert result.exit_code == 2  # Error code

    def test_gate_shows_recommendations_on_failure(self, tmp_path, monkeypatch):
        """Failed gate shows improvement recommendations."""
        specify_dir = tmp_path / ".specify"
        specify_dir.mkdir()
        spec = specify_dir / "spec.md"
        spec.write_text("# TODO")

        monkeypatch.chdir(tmp_path)

        runner = CliRunner()
        result = runner.invoke(app, ["gate"])
        assert result.exit_code == 1
        assert (
            "recommend" in result.output.lower() or "improve" in result.output.lower()
        )
