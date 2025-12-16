"""Tests for constitution validate command."""

import pytest
from pathlib import Path
from typer.testing import CliRunner
from flowspec_cli import app

runner = CliRunner()


@pytest.fixture
def temp_constitution(tmp_path: Path) -> Path:
    """Create a temporary constitution file."""
    memory_dir = tmp_path / "memory"
    memory_dir.mkdir()
    constitution_path = memory_dir / "constitution.md"
    return constitution_path


def test_validate_missing_constitution(tmp_path: Path, monkeypatch):
    """Test validation when constitution file doesn't exist."""
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(
        app,
        ["constitution", "validate"],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "Constitution not found" in result.stdout
    assert "flowspec init --here" in result.stdout


def test_validate_fully_validated_constitution(temp_constitution: Path, monkeypatch):
    """Test validation of a constitution with no NEEDS_VALIDATION markers."""
    # Create a constitution without markers
    temp_constitution.write_text(
        """# My Project Constitution

## Team Standards

Team size: 5 engineers
Deployment frequency: Daily

## Technical Stack

- Python 3.11+
- FastAPI
- PostgreSQL
"""
    )

    monkeypatch.chdir(temp_constitution.parent.parent)

    result = runner.invoke(
        app,
        ["constitution", "validate"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Validation Passed" in result.stdout
    assert "fully validated" in result.stdout
    assert "No NEEDS_VALIDATION markers found" in result.stdout


def test_validate_constitution_with_markers(temp_constitution: Path, monkeypatch):
    """Test validation of a constitution with NEEDS_VALIDATION markers."""
    # Create a constitution with markers
    temp_constitution.write_text(
        """# My Project Constitution

## Team Standards

<!-- NEEDS_VALIDATION: Update team size -->
Team size: [Your team size]

<!-- NEEDS_VALIDATION: Update deployment frequency -->
Deployment frequency: [Your deployment cadence]

## Technical Stack

<!-- NEEDS_VALIDATION: Specify programming language -->
Primary language: [Your language]
"""
    )

    monkeypatch.chdir(temp_constitution.parent.parent)

    result = runner.invoke(
        app,
        ["constitution", "validate"],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "Found 3 section(s) requiring validation" in result.stdout
    assert "Update team size" in result.stdout
    assert "Update deployment frequency" in result.stdout
    assert "Specify programming language" in result.stdout
    assert "Action Required" in result.stdout


def test_validate_constitution_single_marker(temp_constitution: Path, monkeypatch):
    """Test validation with a single NEEDS_VALIDATION marker."""
    temp_constitution.write_text(
        """# My Project Constitution

Team size: 5 engineers

<!-- NEEDS_VALIDATION: Update deployment frequency -->
Deployment frequency: [Your deployment cadence]
"""
    )

    monkeypatch.chdir(temp_constitution.parent.parent)

    result = runner.invoke(
        app,
        ["constitution", "validate"],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "Found 1 section(s) requiring validation" in result.stdout
    assert "Update deployment frequency" in result.stdout


def test_validate_custom_path(tmp_path: Path):
    """Test validation with custom constitution path."""
    custom_file = tmp_path / "custom-constitution.md"
    custom_file.write_text(
        """# Custom Constitution

<!-- NEEDS_VALIDATION: Update this -->
Value: [placeholder]
"""
    )

    result = runner.invoke(
        app,
        ["constitution", "validate", "--path", str(custom_file)],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "Found 1 section(s) requiring validation" in result.stdout
    assert "Update this" in result.stdout


def test_validate_custom_path_not_found(tmp_path: Path):
    """Test validation with custom path that doesn't exist."""
    result = runner.invoke(
        app,
        ["constitution", "validate", "--path", str(tmp_path / "nonexistent.md")],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "Constitution not found" in result.stdout


def test_validate_verbose_mode(temp_constitution: Path, monkeypatch):
    """Test validation with verbose flag."""
    temp_constitution.write_text(
        """# Constitution

<!-- NEEDS_VALIDATION: Update value -->
Value: [placeholder]
"""
    )

    monkeypatch.chdir(temp_constitution.parent.parent)

    result = runner.invoke(
        app,
        ["constitution", "validate", "--verbose"],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "Constitution location:" in result.stdout
    # Path might be wrapped in output by the terminal, so check for key components
    # Note: We don't check for ".md" as it may be split across lines in CI
    assert "memory/constitution" in result.stdout


def test_validate_verbose_mode_success(temp_constitution: Path, monkeypatch):
    """Test verbose mode when validation passes."""
    temp_constitution.write_text("# Constitution\n\nNo markers here.")

    monkeypatch.chdir(temp_constitution.parent.parent)

    result = runner.invoke(
        app,
        ["constitution", "validate", "--verbose"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "fully validated" in result.stdout


def test_validate_multiline_markers(temp_constitution: Path, monkeypatch):
    """Test that markers on multiple lines are all detected."""
    temp_constitution.write_text(
        """# Constitution

<!-- NEEDS_VALIDATION: First thing -->
Value 1: [placeholder]

Some content here.

<!-- NEEDS_VALIDATION: Second thing -->
Value 2: [placeholder]

More content.

<!-- NEEDS_VALIDATION: Third thing -->
Value 3: [placeholder]
"""
    )

    monkeypatch.chdir(temp_constitution.parent.parent)

    result = runner.invoke(
        app,
        ["constitution", "validate"],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "Found 3 section(s) requiring validation" in result.stdout
    assert "First thing" in result.stdout
    assert "Second thing" in result.stdout
    assert "Third thing" in result.stdout


def test_validate_marker_format_variations(temp_constitution: Path, monkeypatch):
    """Test different marker format variations."""
    temp_constitution.write_text(
        """# Constitution

<!-- NEEDS_VALIDATION: Simple description -->
Value: [placeholder]

<!-- NEEDS_VALIDATION: Multi-word description with spaces -->
Another value: [placeholder]

<!-- NEEDS_VALIDATION: Description with-hyphens and_underscores -->
Yet another: [placeholder]
"""
    )

    monkeypatch.chdir(temp_constitution.parent.parent)

    result = runner.invoke(
        app,
        ["constitution", "validate"],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "Found 3 section(s) requiring validation" in result.stdout


def test_validate_detects_markers_in_code_blocks(temp_constitution: Path, monkeypatch):
    """Test that markers in code examples are properly detected (not ignored)."""
    # Note: We DO want to detect markers even in code blocks, as they might be
    # placeholder code that needs updating
    temp_constitution.write_text(
        """# Constitution

Example:
```
<!-- NEEDS_VALIDATION: Update this code -->
code here
```
"""
    )

    monkeypatch.chdir(temp_constitution.parent.parent)

    result = runner.invoke(
        app,
        ["constitution", "validate"],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "Found 1 section(s) requiring validation" in result.stdout


def test_validate_partially_customized(temp_constitution: Path, monkeypatch):
    """Test constitution that's partially customized."""
    temp_constitution.write_text(
        """# Constitution

Team size: 5 engineers  # ✓ Already customized

<!-- NEEDS_VALIDATION: Update deployment frequency -->
Deployment frequency: [Your deployment cadence]  # ✗ Needs updating

Tech stack: Python, FastAPI, PostgreSQL  # ✓ Already customized

<!-- NEEDS_VALIDATION: Update CI/CD pipeline -->
CI/CD: [Your CI/CD tools]  # ✗ Needs updating
"""
    )

    monkeypatch.chdir(temp_constitution.parent.parent)

    result = runner.invoke(
        app,
        ["constitution", "validate"],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "Found 2 section(s) requiring validation" in result.stdout
    assert "Update deployment frequency" in result.stdout
    assert "Update CI/CD pipeline" in result.stdout


def test_validate_empty_constitution(temp_constitution: Path, monkeypatch):
    """Test validation of an empty constitution file."""
    temp_constitution.write_text("")

    monkeypatch.chdir(temp_constitution.parent.parent)

    result = runner.invoke(
        app,
        ["constitution", "validate"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "fully validated" in result.stdout


def test_validate_help_text():
    """Test that help text is comprehensive."""
    result = runner.invoke(
        app,
        ["constitution", "validate", "--help"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "NEEDS_VALIDATION" in result.stdout
    assert "Exit codes" in result.stdout
    assert "Examples" in result.stdout


def test_validate_short_verbose_flag(temp_constitution: Path, monkeypatch):
    """Test that -v short flag works for verbose."""
    temp_constitution.write_text(
        """<!-- NEEDS_VALIDATION: test -->
Value: [placeholder]
"""
    )

    monkeypatch.chdir(temp_constitution.parent.parent)

    result = runner.invoke(
        app,
        ["constitution", "validate", "-v"],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "Constitution location:" in result.stdout
