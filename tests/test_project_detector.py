"""
Tests for project detection functionality.
"""

import pytest
from pathlib import Path
from specify_cli.detection import (
    ProjectDetector,
    is_existing_project,
    has_constitution,
)


@pytest.fixture
def temp_project_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for testing."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    return project_dir


class TestIsExistingProject:
    """Tests for is_existing_project function."""

    def test_git_project_detected(self, temp_project_dir: Path) -> None:
        """Test that .git directory indicates existing project."""
        git_dir = temp_project_dir / ".git"
        git_dir.mkdir()

        assert is_existing_project(temp_project_dir) is True

    def test_python_project_detected_pyproject(self, temp_project_dir: Path) -> None:
        """Test that pyproject.toml indicates existing Python project."""
        (temp_project_dir / "pyproject.toml").touch()

        assert is_existing_project(temp_project_dir) is True

    def test_python_project_detected_setup_py(self, temp_project_dir: Path) -> None:
        """Test that setup.py indicates existing Python project."""
        (temp_project_dir / "setup.py").touch()

        assert is_existing_project(temp_project_dir) is True

    def test_python_project_detected_requirements(self, temp_project_dir: Path) -> None:
        """Test that requirements.txt indicates existing Python project."""
        (temp_project_dir / "requirements.txt").touch()

        assert is_existing_project(temp_project_dir) is True

    def test_node_project_detected(self, temp_project_dir: Path) -> None:
        """Test that package.json indicates existing Node.js project."""
        (temp_project_dir / "package.json").touch()

        assert is_existing_project(temp_project_dir) is True

    def test_go_project_detected(self, temp_project_dir: Path) -> None:
        """Test that go.mod indicates existing Go project."""
        (temp_project_dir / "go.mod").touch()

        assert is_existing_project(temp_project_dir) is True

    def test_rust_project_detected(self, temp_project_dir: Path) -> None:
        """Test that Cargo.toml indicates existing Rust project."""
        (temp_project_dir / "Cargo.toml").touch()

        assert is_existing_project(temp_project_dir) is True

    def test_makefile_project_detected(self, temp_project_dir: Path) -> None:
        """Test that Makefile indicates existing project."""
        (temp_project_dir / "Makefile").touch()

        assert is_existing_project(temp_project_dir) is True

    def test_maven_project_detected(self, temp_project_dir: Path) -> None:
        """Test that pom.xml indicates existing Maven project."""
        (temp_project_dir / "pom.xml").touch()

        assert is_existing_project(temp_project_dir) is True

    def test_gradle_project_detected(self, temp_project_dir: Path) -> None:
        """Test that build.gradle indicates existing Gradle project."""
        (temp_project_dir / "build.gradle").touch()

        assert is_existing_project(temp_project_dir) is True

    def test_ruby_project_detected(self, temp_project_dir: Path) -> None:
        """Test that Gemfile indicates existing Ruby project."""
        (temp_project_dir / "Gemfile").touch()

        assert is_existing_project(temp_project_dir) is True

    def test_php_project_detected(self, temp_project_dir: Path) -> None:
        """Test that composer.json indicates existing PHP project."""
        (temp_project_dir / "composer.json").touch()

        assert is_existing_project(temp_project_dir) is True

    def test_empty_directory_not_detected(self, temp_project_dir: Path) -> None:
        """Test that empty directory is not detected as existing project."""
        assert is_existing_project(temp_project_dir) is False

    def test_directory_with_random_files_not_detected(
        self, temp_project_dir: Path
    ) -> None:
        """Test that directory with non-marker files is not detected."""
        (temp_project_dir / "README.md").touch()
        (temp_project_dir / "data.txt").touch()

        assert is_existing_project(temp_project_dir) is False

    def test_multiple_markers_detected(self, temp_project_dir: Path) -> None:
        """Test that project with multiple markers is detected."""
        (temp_project_dir / ".git").mkdir()
        (temp_project_dir / "package.json").touch()
        (temp_project_dir / "Makefile").touch()

        assert is_existing_project(temp_project_dir) is True


class TestHasConstitution:
    """Tests for has_constitution function."""

    def test_constitution_exists(self, temp_project_dir: Path) -> None:
        """Test detection when constitution exists."""
        memory_dir = temp_project_dir / "memory"
        memory_dir.mkdir()
        constitution_file = memory_dir / "constitution.md"
        constitution_file.write_text("# Constitution\n\nProject rules...")

        assert has_constitution(temp_project_dir) is True

    def test_constitution_missing(self, temp_project_dir: Path) -> None:
        """Test detection when constitution is missing."""
        assert has_constitution(temp_project_dir) is False

    def test_memory_dir_exists_but_no_constitution(
        self, temp_project_dir: Path
    ) -> None:
        """Test detection when memory directory exists but constitution doesn't."""
        memory_dir = temp_project_dir / "memory"
        memory_dir.mkdir()
        (memory_dir / "other_file.md").touch()

        assert has_constitution(temp_project_dir) is False

    def test_constitution_is_directory_not_file(self, temp_project_dir: Path) -> None:
        """Test that constitution must be a file, not a directory."""
        memory_dir = temp_project_dir / "memory"
        memory_dir.mkdir()
        (memory_dir / "constitution.md").mkdir()

        assert has_constitution(temp_project_dir) is False


class TestProjectDetector:
    """Tests for ProjectDetector class."""

    def test_detector_initialization(self, temp_project_dir: Path) -> None:
        """Test that ProjectDetector initializes correctly."""
        detector = ProjectDetector(temp_project_dir)
        assert detector.path == temp_project_dir.resolve()

    def test_detector_is_existing_project(self, temp_project_dir: Path) -> None:
        """Test ProjectDetector.is_existing_project method."""
        (temp_project_dir / ".git").mkdir()
        detector = ProjectDetector(temp_project_dir)

        assert detector.is_existing_project() is True

    def test_detector_has_constitution(self, temp_project_dir: Path) -> None:
        """Test ProjectDetector.has_constitution method."""
        memory_dir = temp_project_dir / "memory"
        memory_dir.mkdir()
        (memory_dir / "constitution.md").touch()

        detector = ProjectDetector(temp_project_dir)
        assert detector.has_constitution() is True

    def test_needs_constitution_prompt_true(self, temp_project_dir: Path) -> None:
        """Test that prompt is needed for existing project without constitution."""
        (temp_project_dir / ".git").mkdir()

        detector = ProjectDetector(temp_project_dir)
        assert detector.needs_constitution_prompt() is True

    def test_needs_constitution_prompt_false_has_constitution(
        self, temp_project_dir: Path
    ) -> None:
        """Test that prompt not needed when constitution exists."""
        (temp_project_dir / ".git").mkdir()
        memory_dir = temp_project_dir / "memory"
        memory_dir.mkdir()
        (memory_dir / "constitution.md").touch()

        detector = ProjectDetector(temp_project_dir)
        assert detector.needs_constitution_prompt() is False

    def test_needs_constitution_prompt_false_new_project(
        self, temp_project_dir: Path
    ) -> None:
        """Test that prompt not needed for new project."""
        detector = ProjectDetector(temp_project_dir)
        assert detector.needs_constitution_prompt() is False

    def test_get_detected_markers_empty(self, temp_project_dir: Path) -> None:
        """Test get_detected_markers returns empty list for new project."""
        detector = ProjectDetector(temp_project_dir)
        markers = detector.get_detected_markers()

        assert markers == []

    def test_get_detected_markers_single(self, temp_project_dir: Path) -> None:
        """Test get_detected_markers returns single marker."""
        (temp_project_dir / "package.json").touch()

        detector = ProjectDetector(temp_project_dir)
        markers = detector.get_detected_markers()

        assert markers == ["package.json"]

    def test_get_detected_markers_multiple(self, temp_project_dir: Path) -> None:
        """Test get_detected_markers returns multiple markers."""
        (temp_project_dir / ".git").mkdir()
        (temp_project_dir / "pyproject.toml").touch()
        (temp_project_dir / "Makefile").touch()

        detector = ProjectDetector(temp_project_dir)
        markers = detector.get_detected_markers()

        assert set(markers) == {".git", "pyproject.toml", "Makefile"}
        assert len(markers) == 3

    def test_detector_resolves_relative_paths(self, tmp_path: Path) -> None:
        """Test that ProjectDetector resolves relative paths."""
        project_dir = tmp_path / "nested" / "project"
        project_dir.mkdir(parents=True)

        # Use relative path
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            detector = ProjectDetector(Path("nested/project"))
            assert detector.path == project_dir.resolve()
        finally:
            os.chdir(original_cwd)


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_nonexistent_directory(self, tmp_path: Path) -> None:
        """Test behavior with nonexistent directory."""
        nonexistent = tmp_path / "does_not_exist"

        assert is_existing_project(nonexistent) is False
        assert has_constitution(nonexistent) is False

    def test_file_instead_of_directory(self, tmp_path: Path) -> None:
        """Test behavior when path is a file, not directory."""
        file_path = tmp_path / "file.txt"
        file_path.touch()

        assert is_existing_project(file_path) is False
        assert has_constitution(file_path) is False

    def test_symlink_to_project(self, temp_project_dir: Path) -> None:
        """Test detection works through symlinks."""
        (temp_project_dir / ".git").mkdir()

        symlink = temp_project_dir.parent / "symlink_project"
        symlink.symlink_to(temp_project_dir)

        try:
            assert is_existing_project(symlink) is True
        finally:
            symlink.unlink()

    def test_case_sensitive_markers(self, temp_project_dir: Path) -> None:
        """Test that marker detection is case-sensitive."""
        # Create uppercase version of marker
        (temp_project_dir / "MAKEFILE").touch()

        # Should not detect uppercase version
        assert is_existing_project(temp_project_dir) is False

        # Create correct lowercase version
        (temp_project_dir / "Makefile").touch()

        # Now should detect
        assert is_existing_project(temp_project_dir) is True
