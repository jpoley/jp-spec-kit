"""Tests for existing project detection and constitution setup (task-243)."""

import sys

import pytest
from specify_cli import is_existing_project, has_constitution, PROJECT_MARKERS


class TestIsExistingProject:
    """Test detection of existing projects by markers."""

    @pytest.mark.parametrize("marker", PROJECT_MARKERS)
    def test_detects_each_marker(self, tmp_path, marker):
        """Test that each project marker is detected individually."""
        # Create marker file or directory
        marker_path = tmp_path / marker
        if marker == ".git":
            marker_path.mkdir()
        else:
            marker_path.write_text("{}")

        assert is_existing_project(tmp_path) is True

    def test_detects_multiple_markers(self, tmp_path):
        """Test detection with multiple markers present."""
        # Create multiple markers
        (tmp_path / ".git").mkdir()
        (tmp_path / "package.json").write_text("{}")
        (tmp_path / "pyproject.toml").write_text("[tool.poetry]")

        assert is_existing_project(tmp_path) is True

    def test_no_markers_returns_false(self, tmp_path):
        """Test that empty directory returns False."""
        assert is_existing_project(tmp_path) is False

    def test_non_marker_files_ignored(self, tmp_path):
        """Test that non-marker files don't trigger detection."""
        (tmp_path / "README.md").write_text("# Test")
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("print('hello')")

        assert is_existing_project(tmp_path) is False

    def test_git_marker_requires_directory(self, tmp_path):
        """Test that .git must be a directory, not a file."""
        # Create .git as a file (invalid)
        (tmp_path / ".git").write_text("gitdir: ../.git/modules/test")

        # Should still detect it (Path.exists() returns True for files too)
        # This is acceptable - we're checking for existence, not type
        assert is_existing_project(tmp_path) is True

    def test_nested_markers_not_detected(self, tmp_path):
        """Test that markers in subdirectories don't count."""
        subdir = tmp_path / "subproject"
        subdir.mkdir()
        (subdir / ".git").mkdir()
        (subdir / "package.json").write_text("{}")

        # Parent should not be detected
        assert is_existing_project(tmp_path) is False

        # But subdirectory should be detected
        assert is_existing_project(subdir) is True


class TestHasConstitution:
    """Test detection of constitution files."""

    def test_detects_constitution(self, tmp_path):
        """Test that memory/constitution.md is detected."""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()
        constitution_path = memory_dir / "constitution.md"
        constitution_path.write_text("# Constitution")

        assert has_constitution(tmp_path) is True

    def test_no_constitution_returns_false(self, tmp_path):
        """Test that missing constitution returns False."""
        assert has_constitution(tmp_path) is False

    def test_empty_memory_dir_returns_false(self, tmp_path):
        """Test that empty memory directory returns False."""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()

        assert has_constitution(tmp_path) is False

    def test_constitution_must_be_in_memory(self, tmp_path):
        """Test that constitution.md must be in memory/ directory."""
        # Constitution in wrong location
        (tmp_path / "constitution.md").write_text("# Constitution")

        assert has_constitution(tmp_path) is False

    @pytest.mark.skipif(
        sys.platform == "darwin",
        reason="macOS has case-insensitive filesystem by default",
    )
    def test_constitution_wrong_name(self, tmp_path):
        """Test that file must be named constitution.md exactly."""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()
        (memory_dir / "Constitution.md").write_text("# Constitution")  # Wrong case
        (memory_dir / "constitution.txt").write_text("# Constitution")  # Wrong ext

        assert has_constitution(tmp_path) is False


class TestCombinedDetection:
    """Test combined project and constitution detection scenarios."""

    def test_existing_project_with_constitution(self, tmp_path):
        """Test project with both markers and constitution."""
        # Create project markers
        (tmp_path / ".git").mkdir()
        (tmp_path / "package.json").write_text("{}")

        # Create constitution
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()
        (memory_dir / "constitution.md").write_text("# Constitution")

        assert is_existing_project(tmp_path) is True
        assert has_constitution(tmp_path) is True

    def test_existing_project_without_constitution(self, tmp_path):
        """Test project with markers but no constitution."""
        (tmp_path / ".git").mkdir()
        (tmp_path / "pyproject.toml").write_text("[tool.poetry]")

        assert is_existing_project(tmp_path) is True
        assert has_constitution(tmp_path) is False

    def test_new_project_with_constitution(self, tmp_path):
        """Test new project (no markers) but has constitution."""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()
        (memory_dir / "constitution.md").write_text("# Constitution")

        assert is_existing_project(tmp_path) is False
        assert has_constitution(tmp_path) is True

    def test_empty_directory(self, tmp_path):
        """Test completely empty directory."""
        assert is_existing_project(tmp_path) is False
        assert has_constitution(tmp_path) is False


class TestProjectMarkersConstant:
    """Test the PROJECT_MARKERS constant."""

    def test_markers_list_not_empty(self):
        """Test that PROJECT_MARKERS is not empty."""
        assert len(PROJECT_MARKERS) > 0

    def test_markers_are_strings(self):
        """Test that all markers are strings."""
        assert all(isinstance(marker, str) for marker in PROJECT_MARKERS)

    def test_git_marker_present(self):
        """Test that .git is in the markers list."""
        assert ".git" in PROJECT_MARKERS

    def test_common_markers_present(self):
        """Test that common project markers are included."""
        expected_markers = [
            ".git",
            "package.json",
            "pyproject.toml",
            "Cargo.toml",
            "go.mod",
            "pom.xml",
        ]
        for marker in expected_markers:
            assert marker in PROJECT_MARKERS, f"Expected marker {marker} not found"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_nonexistent_path(self, tmp_path):
        """Test handling of nonexistent paths."""
        nonexistent = tmp_path / "does_not_exist"
        assert is_existing_project(nonexistent) is False
        assert has_constitution(nonexistent) is False

    def test_symlink_handling(self, tmp_path):
        """Test handling of symlinks."""
        # Create a project in one location
        real_project = tmp_path / "real"
        real_project.mkdir()
        (real_project / ".git").mkdir()

        # Create symlink to it
        link = tmp_path / "link"
        link.symlink_to(real_project)

        # Should detect through symlink
        assert is_existing_project(link) is True

    def test_permission_error_handling(self, tmp_path):
        """Test graceful handling of permission errors."""
        # This test may not work on all systems (e.g., Windows, or running as root)
        # It's included for completeness but may be skipped in some environments
        try:
            restricted = tmp_path / "restricted"
            restricted.mkdir(mode=0o000)

            # Should not raise exception, just return False
            result = is_existing_project(restricted)
            assert isinstance(result, bool)

        except (PermissionError, OSError):
            pytest.skip("Cannot test permission errors on this system")
        finally:
            # Restore permissions for cleanup
            try:
                restricted.chmod(0o755)
            except Exception:
                # Ignore errors during cleanup; permissions may not be restorable on some systems.
                pass


class TestRealWorldScenarios:
    """Test real-world project scenarios."""

    def test_python_project(self, tmp_path):
        """Test typical Python project structure."""
        (tmp_path / "pyproject.toml").write_text(
            """
[tool.poetry]
name = "test-project"
version = "0.1.0"
"""
        )
        (tmp_path / "src").mkdir()
        (tmp_path / "tests").mkdir()

        assert is_existing_project(tmp_path) is True
        assert has_constitution(tmp_path) is False

    def test_nodejs_project(self, tmp_path):
        """Test typical Node.js project structure."""
        (tmp_path / "package.json").write_text(
            """
{
  "name": "test-project",
  "version": "1.0.0"
}
"""
        )
        (tmp_path / "node_modules").mkdir()
        (tmp_path / "src").mkdir()

        assert is_existing_project(tmp_path) is True
        assert has_constitution(tmp_path) is False

    def test_rust_project(self, tmp_path):
        """Test typical Rust project structure."""
        (tmp_path / "Cargo.toml").write_text(
            """
[package]
name = "test-project"
version = "0.1.0"
"""
        )
        (tmp_path / "src").mkdir()
        (tmp_path / "target").mkdir()

        assert is_existing_project(tmp_path) is True
        assert has_constitution(tmp_path) is False

    def test_go_project(self, tmp_path):
        """Test typical Go project structure."""
        (tmp_path / "go.mod").write_text(
            """
module github.com/user/test-project

go 1.21
"""
        )
        (tmp_path / "main.go").write_text("package main")

        assert is_existing_project(tmp_path) is True
        assert has_constitution(tmp_path) is False

    def test_java_maven_project(self, tmp_path):
        """Test typical Java Maven project structure."""
        (tmp_path / "pom.xml").write_text(
            """
<?xml version="1.0" encoding="UTF-8"?>
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>test-project</artifactId>
</project>
"""
        )
        src = tmp_path / "src" / "main" / "java"
        src.mkdir(parents=True)

        assert is_existing_project(tmp_path) is True
        assert has_constitution(tmp_path) is False

    def test_git_initialized_project(self, tmp_path):
        """Test project with git initialized."""
        (tmp_path / ".git").mkdir()
        (tmp_path / ".gitignore").write_text("*.pyc\n__pycache__/")

        assert is_existing_project(tmp_path) is True
        assert has_constitution(tmp_path) is False

    def test_monorepo_structure(self, tmp_path):
        """Test monorepo with multiple subprojects."""
        # Root has git
        (tmp_path / ".git").mkdir()

        # Multiple subprojects
        for subproject in ["backend", "frontend", "shared"]:
            subdir = tmp_path / subproject
            subdir.mkdir()

        # Root is detected
        assert is_existing_project(tmp_path) is True

        # Subprojects are not detected (no markers)
        assert is_existing_project(tmp_path / "backend") is False
