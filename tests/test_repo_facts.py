"""Tests for write_repo_facts() function in specify_cli.

Tests cover:
- Language detection for each supported language
- CI/CD system detection
- Git repository detection
- File creation at correct path
- YAML frontmatter format
- Handling of projects with no detected languages or CI/CD
- Handling of multiple languages and CI/CD systems
"""

from specify_cli import write_repo_facts


class TestLanguageDetection:
    """Tests for language detection in write_repo_facts."""

    def test_detects_python_from_pyproject_toml(self, tmp_path):
        """Should detect Python from pyproject.toml."""
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'")
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "Python" in content

    def test_detects_python_from_requirements_txt(self, tmp_path):
        """Should detect Python from requirements.txt."""
        (tmp_path / "requirements.txt").write_text("pytest>=7.0.0")
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "Python" in content

    def test_detects_python_from_setup_py(self, tmp_path):
        """Should detect Python from setup.py."""
        (tmp_path / "setup.py").write_text("from setuptools import setup")
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "Python" in content

    def test_detects_python_from_pipfile(self, tmp_path):
        """Should detect Python from Pipfile."""
        (tmp_path / "Pipfile").write_text("[packages]\nrequests = '*'")
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "Python" in content

    def test_detects_javascript_from_package_json(self, tmp_path):
        """Should detect JavaScript/TypeScript from package.json."""
        (tmp_path / "package.json").write_text('{"name": "test"}')
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "JavaScript/TypeScript" in content

    def test_detects_javascript_from_yarn_lock(self, tmp_path):
        """Should detect JavaScript/TypeScript from yarn.lock."""
        (tmp_path / "yarn.lock").write_text("# yarn lockfile")
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "JavaScript/TypeScript" in content

    def test_detects_javascript_from_pnpm_lock(self, tmp_path):
        """Should detect JavaScript/TypeScript from pnpm-lock.yaml."""
        (tmp_path / "pnpm-lock.yaml").write_text("lockfileVersion: '6.0'")
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "JavaScript/TypeScript" in content

    def test_detects_go_from_go_mod(self, tmp_path):
        """Should detect Go from go.mod."""
        (tmp_path / "go.mod").write_text("module example.com/test")
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "Go" in content

    def test_detects_go_from_go_sum(self, tmp_path):
        """Should detect Go from go.sum."""
        (tmp_path / "go.sum").write_text("github.com/pkg/errors v0.9.1")
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "Go" in content

    def test_detects_rust_from_cargo_toml(self, tmp_path):
        """Should detect Rust from Cargo.toml."""
        (tmp_path / "Cargo.toml").write_text('[package]\nname = "test"')
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "Rust" in content

    def test_detects_rust_from_cargo_lock(self, tmp_path):
        """Should detect Rust from Cargo.lock."""
        (tmp_path / "Cargo.lock").write_text("# Cargo.lock")
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "Rust" in content

    def test_detects_java_from_pom_xml(self, tmp_path):
        """Should detect Java from pom.xml."""
        (tmp_path / "pom.xml").write_text("<project></project>")
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "Java" in content

    def test_detects_java_from_build_gradle(self, tmp_path):
        """Should detect Java from build.gradle."""
        (tmp_path / "build.gradle").write_text("plugins { id 'java' }")
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "Java" in content

    def test_detects_java_from_build_gradle_kts(self, tmp_path):
        """Should detect Java from build.gradle.kts."""
        (tmp_path / "build.gradle.kts").write_text('plugins { id("java") }')
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "Java" in content

    def test_detects_ruby_from_gemfile(self, tmp_path):
        """Should detect Ruby from Gemfile."""
        (tmp_path / "Gemfile").write_text("source 'https://rubygems.org'")
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "Ruby" in content

    def test_detects_ruby_from_gemfile_lock(self, tmp_path):
        """Should detect Ruby from Gemfile.lock."""
        (tmp_path / "Gemfile.lock").write_text("GEM\n  remote: https://rubygems.org/")
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "Ruby" in content

    def test_detects_php_from_composer_json(self, tmp_path):
        """Should detect PHP from composer.json."""
        (tmp_path / "composer.json").write_text('{"name": "test/test"}')
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "PHP" in content

    def test_detects_php_from_composer_lock(self, tmp_path):
        """Should detect PHP from composer.lock."""
        (tmp_path / "composer.lock").write_text('{"_readme": []}')
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "PHP" in content

    def test_detects_csharp_from_csproj(self, tmp_path):
        """Should detect C# from .csproj file."""
        (tmp_path / "MyProject.csproj").write_text("<Project></Project>")
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "C#" in content

    def test_detects_csharp_from_sln(self, tmp_path):
        """Should detect C# from .sln file."""
        (tmp_path / "MySolution.sln").write_text("Microsoft Visual Studio Solution")
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "C#" in content

    def test_detects_multiple_languages(self, tmp_path):
        """Should detect multiple languages in same project."""
        (tmp_path / "pyproject.toml").write_text("[project]")
        (tmp_path / "package.json").write_text('{"name": "test"}')
        (tmp_path / "go.mod").write_text("module test")
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "Python" in content
        assert "JavaScript/TypeScript" in content
        assert "Go" in content

    def test_no_duplicate_language_detection(self, tmp_path):
        """Should not list same language twice."""
        # Create multiple Python files
        (tmp_path / "pyproject.toml").write_text("[project]")
        (tmp_path / "requirements.txt").write_text("pytest")
        (tmp_path / "setup.py").write_text("from setuptools import setup")
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        # Count occurrences of "- Python" (list item)
        python_count = content.count("- Python")
        assert python_count == 1, f"Python listed {python_count} times, expected 1"


class TestCICDDetection:
    """Tests for CI/CD system detection in write_repo_facts."""

    def test_detects_github_actions(self, tmp_path):
        """Should detect GitHub Actions from .github/workflows directory."""
        workflows_dir = tmp_path / ".github" / "workflows"
        workflows_dir.mkdir(parents=True)
        (workflows_dir / "ci.yml").write_text("name: CI")
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "GitHub Actions" in content

    def test_github_actions_empty_workflows_not_detected(self, tmp_path):
        """Should not detect GitHub Actions if workflows directory is empty."""
        workflows_dir = tmp_path / ".github" / "workflows"
        workflows_dir.mkdir(parents=True)
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "GitHub Actions" not in content

    def test_detects_gitlab_ci(self, tmp_path):
        """Should detect GitLab CI from .gitlab-ci.yml."""
        (tmp_path / ".gitlab-ci.yml").write_text("stages: [build, test]")
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "GitLab CI" in content

    def test_detects_circleci(self, tmp_path):
        """Should detect CircleCI from .circleci/config.yml."""
        circleci_dir = tmp_path / ".circleci"
        circleci_dir.mkdir()
        (circleci_dir / "config.yml").write_text("version: 2.1")
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "CircleCI" in content

    def test_detects_travis_ci(self, tmp_path):
        """Should detect Travis CI from .travis.yml."""
        (tmp_path / ".travis.yml").write_text("language: python")
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "Travis CI" in content

    def test_detects_jenkins(self, tmp_path):
        """Should detect Jenkins from Jenkinsfile."""
        (tmp_path / "Jenkinsfile").write_text("pipeline { agent any }")
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "Jenkins" in content

    def test_detects_multiple_cicd_systems(self, tmp_path):
        """Should detect multiple CI/CD systems."""
        # GitHub Actions
        workflows_dir = tmp_path / ".github" / "workflows"
        workflows_dir.mkdir(parents=True)
        (workflows_dir / "ci.yml").write_text("name: CI")
        # GitLab CI
        (tmp_path / ".gitlab-ci.yml").write_text("stages: [test]")
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "GitHub Actions" in content
        assert "GitLab CI" in content


class TestGitRepoDetection:
    """Tests for git repository detection in write_repo_facts."""

    def test_detects_git_repo(self, tmp_path):
        """Should detect git repository when .git directory exists."""
        (tmp_path / ".git").mkdir()
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "git_repo: true" in content
        assert "Git repository: Yes" in content

    def test_detects_no_git_repo(self, tmp_path):
        """Should detect no git repository when .git directory missing."""
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "git_repo: false" in content
        assert "Git repository: No" in content


class TestFileCreation:
    """Tests for file creation in write_repo_facts."""

    def test_creates_memory_directory(self, tmp_path):
        """Should create memory directory if it doesn't exist."""
        assert not (tmp_path / "memory").exists()
        write_repo_facts(tmp_path)

        assert (tmp_path / "memory").exists()
        assert (tmp_path / "memory").is_dir()

    def test_creates_repo_facts_file(self, tmp_path):
        """Should create repo-facts.md file."""
        write_repo_facts(tmp_path)

        repo_facts_path = tmp_path / "memory" / "repo-facts.md"
        assert repo_facts_path.exists()
        assert repo_facts_path.is_file()

    def test_overwrites_existing_file(self, tmp_path):
        """Should overwrite existing repo-facts.md file."""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()
        existing_file = memory_dir / "repo-facts.md"
        existing_file.write_text("old content")

        write_repo_facts(tmp_path)

        content = existing_file.read_text()
        assert "old content" not in content
        assert "Repository Facts" in content


class TestYAMLFrontmatter:
    """Tests for YAML frontmatter format in write_repo_facts."""

    def test_frontmatter_starts_with_delimiter(self, tmp_path):
        """Should start with YAML frontmatter delimiter."""
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert content.startswith("---\n")

    def test_frontmatter_has_closing_delimiter(self, tmp_path):
        """Should have closing YAML frontmatter delimiter."""
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        lines = content.split("\n")
        # First line is opening delimiter, find closing
        closing_index = None
        for i, line in enumerate(lines[1:], start=1):
            if line == "---":
                closing_index = i
                break
        assert closing_index is not None, "Missing closing --- delimiter"

    def test_frontmatter_contains_generated_timestamp(self, tmp_path):
        """Should contain generated timestamp in frontmatter."""
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "generated:" in content

    def test_frontmatter_contains_languages(self, tmp_path):
        """Should contain languages in frontmatter."""
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "languages:" in content

    def test_frontmatter_contains_cicd(self, tmp_path):
        """Should contain cicd in frontmatter."""
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "cicd:" in content

    def test_frontmatter_contains_git_repo(self, tmp_path):
        """Should contain git_repo in frontmatter."""
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "git_repo:" in content


class TestNoDetection:
    """Tests for handling projects with no detected languages or CI/CD."""

    def test_no_languages_detected(self, tmp_path):
        """Should show Unknown when no languages detected."""
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "Unknown" in content
        assert "languages: [Unknown]" in content

    def test_no_cicd_detected(self, tmp_path):
        """Should show None detected when no CI/CD systems found."""
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "None detected" in content
        assert "cicd: [None detected]" in content


class TestMarkdownContent:
    """Tests for markdown content structure in write_repo_facts."""

    def test_contains_repository_facts_heading(self, tmp_path):
        """Should contain Repository Facts heading."""
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "# Repository Facts" in content

    def test_contains_languages_section(self, tmp_path):
        """Should contain Languages section."""
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "## Languages" in content

    def test_contains_cicd_section(self, tmp_path):
        """Should contain CI/CD section."""
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "## CI/CD" in content

    def test_contains_git_repository_section(self, tmp_path):
        """Should contain Git Repository section."""
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "## Git Repository" in content

    def test_contains_footer_note(self, tmp_path):
        """Should contain footer note about automatic generation."""
        write_repo_facts(tmp_path)

        content = (tmp_path / "memory" / "repo-facts.md").read_text()
        assert "automatically generated" in content
