"""Tests for constitution version command."""

import pytest
from pathlib import Path
from typer.testing import CliRunner
from specify_cli import app, CONSTITUTION_VERSION

runner = CliRunner()


@pytest.fixture
def temp_project(tmp_path: Path) -> Path:
    """Create a temporary project directory."""
    memory_dir = tmp_path / "memory"
    memory_dir.mkdir()
    return tmp_path


def test_constitution_version_no_file(tmp_path: Path):
    """Test version command when constitution doesn't exist."""
    nonexistent = tmp_path / "nonexistent" / "memory" / "constitution.md"
    result = runner.invoke(app, ["constitution", "version", "--path", str(nonexistent)])
    assert result.exit_code == 1
    assert "Constitution not found" in result.stdout


def test_constitution_version_light_tier(temp_project: Path):
    """Test version command with light tier constitution."""
    constitution_path = temp_project / "memory" / "constitution.md"
    constitution_path.write_text(
        """# Test Constitution
<!-- TIER: Light - Minimal controls for startups/hobby projects -->

**Version**: 1.0.0
**Ratified**: 2025-01-01
**Last Amended**: 2025-01-01
"""
    )

    result = runner.invoke(
        app, ["constitution", "version", "--path", str(constitution_path)]
    )

    assert result.exit_code == 0
    assert "Version" in result.stdout
    assert "1.0.0" in result.stdout
    assert "Light" in result.stdout
    assert "2025-01-01" in result.stdout


def test_constitution_version_medium_tier(temp_project: Path):
    """Test version command with medium tier constitution."""
    constitution_path = temp_project / "memory" / "constitution.md"
    constitution_path.write_text(
        """# Test Constitution
<!-- TIER: Medium - Standard controls for typical business projects -->

**Version**: 1.0.0
**Ratified**: 2025-01-15
**Last Amended**: 2025-02-01
"""
    )

    result = runner.invoke(
        app, ["constitution", "version", "--path", str(constitution_path)]
    )

    assert result.exit_code == 0
    assert "Medium" in result.stdout
    assert "2025-01-15" in result.stdout
    assert "2025-02-01" in result.stdout


def test_constitution_version_heavy_tier(temp_project: Path):
    """Test version command with heavy tier constitution."""
    constitution_path = temp_project / "memory" / "constitution.md"
    constitution_path.write_text(
        """# Test Constitution
<!-- TIER: Heavy - Strict controls for enterprise/regulated environments -->

**Version**: 1.0.0
**Ratified**: 2025-01-01
**Last Amended**: 2025-01-01
"""
    )

    result = runner.invoke(
        app, ["constitution", "version", "--path", str(constitution_path)]
    )

    assert result.exit_code == 0
    assert "Heavy" in result.stdout


def test_constitution_version_outdated(temp_project: Path):
    """Test upgrade warning when constitution version is outdated."""
    constitution_path = temp_project / "memory" / "constitution.md"
    constitution_path.write_text(
        """# Test Constitution
<!-- TIER: Medium -->

**Version**: 0.9.0
**Ratified**: 2024-01-01
**Last Amended**: 2024-01-01
"""
    )

    result = runner.invoke(
        app, ["constitution", "version", "--path", str(constitution_path)]
    )

    assert result.exit_code == 0
    assert "0.9.0" in result.stdout
    # Should show upgrade available message
    assert "available" in result.stdout or "Template" in result.stdout


def test_constitution_version_template_version_shown(temp_project: Path):
    """Test that template version is shown."""
    constitution_path = temp_project / "memory" / "constitution.md"
    constitution_path.write_text(
        """# Test Constitution
<!-- TIER: Light -->

**Version**: 1.0.0
**Ratified**: 2025-01-01
**Last Amended**: 2025-01-01
"""
    )

    result = runner.invoke(
        app, ["constitution", "version", "--path", str(constitution_path)]
    )

    assert result.exit_code == 0
    assert "Template Version" in result.stdout
    assert CONSTITUTION_VERSION in result.stdout


def test_constitution_version_missing_fields(temp_project: Path):
    """Test version command with missing version fields."""
    constitution_path = temp_project / "memory" / "constitution.md"
    constitution_path.write_text(
        """# Test Constitution
<!-- TIER: Medium -->

Some content without version fields.
"""
    )

    result = runner.invoke(
        app, ["constitution", "version", "--path", str(constitution_path)]
    )

    assert result.exit_code == 0
    assert "Unknown" in result.stdout


def test_constitution_version_current_directory(temp_project: Path, monkeypatch):
    """Test version command using current directory."""
    constitution_path = temp_project / "memory" / "constitution.md"
    constitution_path.write_text(
        """# Test Constitution
<!-- TIER: Light -->

**Version**: 1.0.0
**Ratified**: 2025-01-01
**Last Amended**: 2025-01-01
"""
    )

    # Change to temp project directory
    monkeypatch.chdir(temp_project)

    result = runner.invoke(app, ["constitution", "version"])

    assert result.exit_code == 0
    assert "1.0.0" in result.stdout
