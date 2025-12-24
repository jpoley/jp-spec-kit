"""Tests for repository characteristics detection and repo-facts generation (task-293).

Verifies that detect_repo_characteristics() and write_repo_facts() correctly detect:
- Languages (Python, TypeScript, Go, multi-language)
- Test frameworks (pytest, jest, go test)
- Linters (ruff, eslint, golangci-lint)
- Package managers (uv, npm, pnpm, go modules)
- CI/CD systems (GitHub Actions)

Target: 90%+ detection accuracy across all fixtures.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from flowspec_cli import detect_repo_characteristics, write_repo_facts


class TestLLMCustomizationAccuracy:
    """Test suite for LLM customization accuracy."""

    def test_python_project_detection(self, python_project_fixture: Path) -> None:
        """Test AC1: Python project detects pytest, ruff, GitHub Actions."""
        # Act
        result = detect_repo_characteristics(python_project_fixture)

        # Assert - Languages
        assert "Python" in result["languages"], "Failed to detect Python language"

        # Assert - Test frameworks
        assert "pytest" in result["test_frameworks"], "Failed to detect pytest"

        # Assert - Package managers
        assert "uv" in result["package_managers"], "Failed to detect uv package manager"

        # Assert - Linters
        assert "ruff" in result["linters"], "Failed to detect ruff linter"

        # Assert - CI/CD systems
        assert "GitHub Actions" in result["cicd"], "Failed to detect GitHub Actions"

        # Verify repo-facts generation
        write_repo_facts(python_project_fixture)
        repo_facts = python_project_fixture / "memory" / "repo-facts.md"
        assert repo_facts.exists(), "Failed to generate repo-facts.md"

        content = repo_facts.read_text()
        assert "Python" in content, "Python not in repo-facts.md"
        assert "GitHub Actions" in content, "GitHub Actions not in repo-facts.md"

    def test_typescript_project_detection(
        self, typescript_project_fixture: Path
    ) -> None:
        """Test AC2: TypeScript project detects jest, eslint, prettier, npm/pnpm."""
        # Act
        result = detect_repo_characteristics(typescript_project_fixture)

        # Assert - Languages
        assert "JavaScript/TypeScript" in result["languages"], (
            "Failed to detect TypeScript"
        )

        # Assert - Test frameworks
        assert "jest" in result["test_frameworks"], "Failed to detect jest"

        # Assert - Package managers
        assert "pnpm" in result["package_managers"], "Failed to detect pnpm"

        # Assert - Linters
        assert "eslint" in result["linters"], "Failed to detect eslint"
        assert "prettier" in result["linters"], "Failed to detect prettier"

        # Verify package.json parsing
        package_json = typescript_project_fixture / "package.json"
        assert package_json.exists()
        data = json.loads(package_json.read_text())
        assert "jest" in data["devDependencies"]
        assert "eslint" in data["devDependencies"]
        assert "prettier" in data["devDependencies"]

    def test_go_project_detection(self, go_project_fixture: Path) -> None:
        """Test AC3: Go project detects go test, golangci-lint, Go modules."""
        # Act
        result = detect_repo_characteristics(go_project_fixture)

        # Assert - Languages
        assert "Go" in result["languages"], "Failed to detect Go language"

        # Assert - Test frameworks
        assert "go test" in result["test_frameworks"], "Failed to detect go test"

        # Assert - Package managers
        assert "go modules" in result["package_managers"], "Failed to detect go modules"

        # Assert - Linters
        assert "golangci-lint" in result["linters"], "Failed to detect golangci-lint"

        # Verify go.mod exists
        go_mod = go_project_fixture / "go.mod"
        assert go_mod.exists(), "go.mod should exist"
        assert "module example.com/test" in go_mod.read_text()

        # Verify golangci-lint config exists
        golangci_config = go_project_fixture / ".golangci.yml"
        assert golangci_config.exists(), "golangci-lint config should exist"

    def test_multi_language_project_detection(
        self, multi_language_project_fixture: Path
    ) -> None:
        """Test AC4: Multi-language project detects all languages correctly."""
        # Act
        result = detect_repo_characteristics(multi_language_project_fixture)

        # Assert - Multiple languages detected
        assert "Python" in result["languages"], "Failed to detect Python"
        assert "JavaScript/TypeScript" in result["languages"], (
            "Failed to detect TypeScript"
        )
        assert len(result["languages"]) >= 2, "Should detect multiple languages"

        # Assert - Test frameworks
        assert len(result["test_frameworks"]) >= 1, (
            "Should detect at least one test framework"
        )
        assert (
            "pytest" in result["test_frameworks"]
            or "vitest" in result["test_frameworks"]
        ), "Should detect pytest or vitest"

        # Verify both package files exist
        assert (multi_language_project_fixture / "pyproject.toml").exists(), (
            "pyproject.toml missing"
        )
        assert (multi_language_project_fixture / "package.json").exists(), (
            "package.json missing"
        )

    def test_empty_repo_edge_case(self, empty_repo_fixture: Path) -> None:
        """Test AC5: Empty repo with only README handles gracefully."""
        # Act
        result = detect_repo_characteristics(empty_repo_fixture)

        # Assert - No languages detected
        assert result["languages"] == [], "Should detect no languages"
        assert result["test_frameworks"] == [], "Should detect no test frameworks"
        assert result["package_managers"] == [], "Should detect no package managers"
        assert result["linters"] == [], "Should detect no linters"

        # Verify repo-facts still generates
        write_repo_facts(empty_repo_fixture)
        repo_facts = empty_repo_fixture / "memory" / "repo-facts.md"
        assert repo_facts.exists(), "repo-facts.md should still be generated"

        content = repo_facts.read_text()
        assert "Unknown" in content or "None" in content, "Should indicate no languages"

    def test_detection_accuracy_aggregate(
        self,
        python_project_fixture: Path,
        typescript_project_fixture: Path,
        go_project_fixture: Path,
        multi_language_project_fixture: Path,
        empty_repo_fixture: Path,
    ) -> None:
        """Test AC6: 90%+ detection accuracy across all fixtures.

        Tracks detection success rate across all test criteria:
        - Language detection
        - Test framework detection
        - Package manager detection
        - CI/CD detection (via repo-facts)
        """
        fixtures = [
            ("python", python_project_fixture),
            ("typescript", typescript_project_fixture),
            ("go", go_project_fixture),
            ("multi_language", multi_language_project_fixture),
            ("empty", empty_repo_fixture),
        ]

        total_checks = 0
        passed_checks = 0

        for name, fixture in fixtures:
            result = detect_repo_characteristics(fixture)

            if name == "python":
                # 4 checks: language, test framework, package manager, linter
                total_checks += 4
                if "Python" in result["languages"]:
                    passed_checks += 1
                if "pytest" in result["test_frameworks"]:
                    passed_checks += 1
                if "uv" in result["package_managers"]:
                    passed_checks += 1
                if "ruff" in result["linters"]:
                    passed_checks += 1

            elif name == "typescript":
                # 5 checks: language, test framework, package manager, linters
                total_checks += 5
                if "JavaScript/TypeScript" in result["languages"]:
                    passed_checks += 1
                if "jest" in result["test_frameworks"]:
                    passed_checks += 1
                if "pnpm" in result["package_managers"]:
                    passed_checks += 1
                if "eslint" in result["linters"]:
                    passed_checks += 1
                if "prettier" in result["linters"]:
                    passed_checks += 1

            elif name == "go":
                # 4 checks: language, test framework, package manager, linter
                total_checks += 4
                if "Go" in result["languages"]:
                    passed_checks += 1
                if "go test" in result["test_frameworks"]:
                    passed_checks += 1
                if "go modules" in result["package_managers"]:
                    passed_checks += 1
                if "golangci-lint" in result["linters"]:
                    passed_checks += 1

            elif name == "multi_language":
                # 2 checks: both languages detected
                total_checks += 2
                if "Python" in result["languages"]:
                    passed_checks += 1
                if "JavaScript/TypeScript" in result["languages"]:
                    passed_checks += 1

            elif name == "empty":
                # 4 checks: no false positives
                total_checks += 4
                if result["languages"] == []:
                    passed_checks += 1
                if result["test_frameworks"] == []:
                    passed_checks += 1
                if result["package_managers"] == []:
                    passed_checks += 1
                if result["linters"] == []:
                    passed_checks += 1

        # Calculate accuracy
        accuracy = (passed_checks / total_checks) * 100 if total_checks > 0 else 0

        # Assert 90%+ accuracy
        assert accuracy >= 90.0, (
            f"Detection accuracy {accuracy:.1f}% is below 90% threshold (passed {passed_checks}/{total_checks})"
        )

        # Log results for debugging
        print("\n=== Detection Accuracy Report ===")
        print(f"Total checks: {total_checks}")
        print(f"Passed checks: {passed_checks}")
        print(f"Accuracy: {accuracy:.1f}%")

    def test_cicd_detection_github_actions(self, python_project_fixture: Path) -> None:
        """Test GitHub Actions detection in repo-facts."""
        # Act
        write_repo_facts(python_project_fixture)
        repo_facts = python_project_fixture / "memory" / "repo-facts.md"

        # Assert
        assert repo_facts.exists()
        content = repo_facts.read_text()
        assert "GitHub Actions" in content, "Failed to detect GitHub Actions"

    def test_repo_facts_yaml_frontmatter(self, python_project_fixture: Path) -> None:
        """Test repo-facts.md contains valid YAML frontmatter."""
        # Act
        write_repo_facts(python_project_fixture)
        repo_facts = python_project_fixture / "memory" / "repo-facts.md"

        # Assert
        content = repo_facts.read_text()
        lines = content.split("\n")

        # Verify frontmatter structure
        assert lines[0] == "---", "Should start with YAML frontmatter"
        assert "generated:" in content, "Should have generated timestamp"
        assert "languages:" in content, "Should have languages field"
        assert "cicd:" in content, "Should have cicd field"
        assert "git_repo:" in content, "Should have git_repo field"

        # Find closing frontmatter delimiter
        closing_idx = None
        for i, line in enumerate(lines[1:], start=1):
            if line == "---":
                closing_idx = i
                break
        assert closing_idx is not None, "Should have closing YAML frontmatter delimiter"


# === Fixtures ===


@pytest.fixture
def python_project_fixture(tmp_path: Path) -> Path:
    """Create Python project fixture with pytest, ruff, uv, GitHub Actions.

    Structure:
    - pyproject.toml (with pytest, ruff in dev-dependencies, [tool.uv] section)
    - uv.lock
    - .github/workflows/ci.yml
    - src/main.py
    """
    project_dir = tmp_path / "python_project"
    project_dir.mkdir()

    # Create pyproject.toml with pytest and ruff (in dev dependencies)
    toml_content = """[project]
name = "test-project"
version = "0.1.0"
dependencies = []

[project.optional-dependencies]
dev = ["pytest", "ruff"]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 88
select = ["E", "F", "I"]

[tool.uv]
dev-dependencies = ["pytest", "ruff"]
"""
    (project_dir / "pyproject.toml").write_text(toml_content)

    # Create uv.lock to indicate uv package manager
    (project_dir / "uv.lock").write_text("version = 1\n")

    # Create GitHub Actions workflow
    github_dir = project_dir / ".github" / "workflows"
    github_dir.mkdir(parents=True)
    ci_yml = """name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: pytest
"""
    (github_dir / "ci.yml").write_text(ci_yml)

    # Create source file
    src_dir = project_dir / "src"
    src_dir.mkdir()
    (src_dir / "main.py").write_text('def hello():\n    return "world"\n')

    return project_dir


@pytest.fixture
def typescript_project_fixture(tmp_path: Path) -> Path:
    """Create TypeScript project fixture with jest, eslint, prettier, pnpm.

    Structure:
    - package.json (with jest, eslint, prettier)
    - pnpm-lock.yaml
    - tsconfig.json
    - src/index.ts
    """
    project_dir = tmp_path / "typescript_project"
    project_dir.mkdir()

    # Create package.json with jest, eslint, prettier
    package_json = {
        "name": "test-typescript-project",
        "version": "1.0.0",
        "dependencies": {"typescript": "^5.0.0"},
        "devDependencies": {
            "jest": "^29.0.0",
            "eslint": "^8.0.0",
            "prettier": "^3.0.0",
            "@types/jest": "^29.0.0",
        },
        "scripts": {
            "test": "jest",
            "lint": "eslint .",
            "format": "prettier --write .",
        },
    }
    (project_dir / "package.json").write_text(json.dumps(package_json, indent=2))

    # Create pnpm-lock.yaml
    (project_dir / "pnpm-lock.yaml").write_text("lockfileVersion: '6.0'\n")

    # Create tsconfig.json
    tsconfig = {
        "compilerOptions": {
            "target": "ES2020",
            "module": "commonjs",
            "strict": True,
        }
    }
    (project_dir / "tsconfig.json").write_text(json.dumps(tsconfig, indent=2))

    # Create source file
    src_dir = project_dir / "src"
    src_dir.mkdir()
    (src_dir / "index.ts").write_text('export const hello = (): string => "world";\n')

    return project_dir


@pytest.fixture
def go_project_fixture(tmp_path: Path) -> Path:
    """Create Go project fixture with go.mod, golangci-lint.

    Structure:
    - go.mod
    - .golangci.yml
    - main.go
    - main_test.go
    """
    project_dir = tmp_path / "go_project"
    project_dir.mkdir()

    # Create go.mod
    go_mod = """module example.com/test

go 1.21

require (
    github.com/stretchr/testify v1.8.0
)
"""
    (project_dir / "go.mod").write_text(go_mod)

    # Create golangci-lint config
    golangci_yml = """linters:
  enable:
    - gofmt
    - golint
    - govet
"""
    (project_dir / ".golangci.yml").write_text(golangci_yml)

    # Create main.go
    main_go = """package main

func Hello() string {
    return "world"
}

func main() {}
"""
    (project_dir / "main.go").write_text(main_go)

    # Create test file
    test_go = """package main

import "testing"

func TestHello(t *testing.T) {
    if Hello() != "world" {
        t.Fail()
    }
}
"""
    (project_dir / "main_test.go").write_text(test_go)

    return project_dir


@pytest.fixture
def multi_language_project_fixture(tmp_path: Path) -> Path:
    """Create multi-language project (Python + TypeScript).

    Structure:
    - pyproject.toml (Python)
    - package.json (TypeScript)
    - src/backend/ (Python)
    - src/frontend/ (TypeScript)
    """
    project_dir = tmp_path / "multi_language_project"
    project_dir.mkdir()

    # Create Python config
    pyproject_content = """[project]
name = "multi-lang-backend"
version = "0.1.0"
dependencies = ["fastapi", "pytest"]
"""
    (project_dir / "pyproject.toml").write_text(pyproject_content)

    # Create TypeScript config
    package_json = {
        "name": "multi-lang-frontend",
        "version": "1.0.0",
        "dependencies": {"react": "^18.0.0"},
        "devDependencies": {"vitest": "^1.0.0"},
    }
    (project_dir / "package.json").write_text(json.dumps(package_json, indent=2))

    # Create source directories
    backend_dir = project_dir / "src" / "backend"
    backend_dir.mkdir(parents=True)
    (backend_dir / "main.py").write_text('def api():\n    return "hello"\n')

    frontend_dir = project_dir / "src" / "frontend"
    frontend_dir.mkdir(parents=True)
    (frontend_dir / "app.tsx").write_text(
        "export const App = () => <div>Hello</div>;\n"
    )

    return project_dir


@pytest.fixture
def empty_repo_fixture(tmp_path: Path) -> Path:
    """Create empty repo with only README.

    Structure:
    - README.md
    """
    project_dir = tmp_path / "empty_repo"
    project_dir.mkdir()

    # Create only README
    (project_dir / "README.md").write_text("# Empty Test Repository\n\nNo code here.\n")

    return project_dir
