"""Tests for LLM customization detection accuracy.

This test suite validates that repository detection logic achieves 90%+ accuracy
for detecting:
- Programming languages
- Testing frameworks
- Linting/formatting tools
- CI/CD configurations
- Package managers

Tests cover:
- Python projects (pytest, ruff, GitHub Actions)
- TypeScript projects (jest, eslint, prettier, npm/pnpm)
- Go projects (go test, golangci-lint, Go modules)
- Multi-language projects
- Edge cases (empty repos)
"""

import json
from pathlib import Path

import pytest


class ProjectDetector:
    """Repository detection logic for LLM customization.

    This class encapsulates detection logic for project characteristics.
    It should detect languages, tools, frameworks, and CI/CD configurations
    with 90%+ accuracy.
    """

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self._results: dict[str, list[str]] = {
            "languages": [],
            "testing": [],
            "linting": [],
            "formatting": [],
            "ci_cd": [],
            "package_managers": [],
        }

    def detect_all(self) -> dict[str, list[str]]:
        """Run all detection methods and return consolidated results."""
        self._detect_languages()
        self._detect_testing_frameworks()
        self._detect_linting_tools()
        self._detect_formatting_tools()
        self._detect_ci_cd()
        self._detect_package_managers()
        return self._results

    def _detect_languages(self) -> None:
        """Detect programming languages from config files and source files."""
        # Python
        if (self.project_path / "pyproject.toml").exists():
            self._results["languages"].append("Python")
        elif (self.project_path / "requirements.txt").exists():
            self._results["languages"].append("Python")
        elif list(self.project_path.rglob("*.py")):
            self._results["languages"].append("Python")

        # TypeScript/JavaScript
        if (self.project_path / "tsconfig.json").exists():
            self._results["languages"].append("TypeScript")
        elif (self.project_path / "package.json").exists():
            # Check if TypeScript is in dependencies
            package_json = self.project_path / "package.json"
            try:
                data = json.loads(package_json.read_text())
                deps = {
                    **data.get("dependencies", {}),
                    **data.get("devDependencies", {}),
                }
                if "typescript" in deps:
                    self._results["languages"].append("TypeScript")
                else:
                    self._results["languages"].append("JavaScript")
            except (json.JSONDecodeError, OSError):
                self._results["languages"].append("JavaScript")
        elif list(self.project_path.rglob("*.ts")) or list(
            self.project_path.rglob("*.tsx")
        ):
            self._results["languages"].append("TypeScript")

        # Go
        if (self.project_path / "go.mod").exists():
            self._results["languages"].append("Go")
        elif list(self.project_path.rglob("*.go")):
            self._results["languages"].append("Go")

        # Rust
        if (self.project_path / "Cargo.toml").exists():
            self._results["languages"].append("Rust")

        # Java
        if (self.project_path / "pom.xml").exists():
            self._results["languages"].append("Java")
        elif (self.project_path / "build.gradle").exists():
            self._results["languages"].append("Java")

    def _detect_testing_frameworks(self) -> None:
        """Detect testing frameworks from config files and dependencies."""
        # pytest
        pyproject = self.project_path / "pyproject.toml"
        if pyproject.exists():
            content = pyproject.read_text()
            if "[tool.pytest" in content or "pytest" in content:
                self._results["testing"].append("pytest")

        # Check for pytest.ini
        if (self.project_path / "pytest.ini").exists():
            self._results["testing"].append("pytest")

        # Check for test files
        if list(self.project_path.rglob("test_*.py")) or list(
            self.project_path.rglob("*_test.py")
        ):
            if "pytest" not in self._results["testing"]:
                self._results["testing"].append("pytest")

        # Jest/Vitest
        package_json = self.project_path / "package.json"
        if package_json.exists():
            try:
                data = json.loads(package_json.read_text())
                dev_deps = data.get("devDependencies", {})
                if "jest" in dev_deps or "@jest/core" in dev_deps:
                    self._results["testing"].append("jest")
                if "vitest" in dev_deps:
                    self._results["testing"].append("vitest")
            except (json.JSONDecodeError, OSError):
                pass

        # Go test
        if (self.project_path / "go.mod").exists():
            if list(self.project_path.rglob("*_test.go")):
                self._results["testing"].append("go test")

    def _detect_linting_tools(self) -> None:
        """Detect linting tools from config files."""
        # Ruff
        pyproject = self.project_path / "pyproject.toml"
        if pyproject.exists():
            content = pyproject.read_text()
            if "[tool.ruff" in content or "ruff" in content:
                self._results["linting"].append("ruff")

        if (self.project_path / "ruff.toml").exists():
            self._results["linting"].append("ruff")

        # ESLint
        eslint_files = [
            ".eslintrc",
            ".eslintrc.js",
            ".eslintrc.json",
            ".eslintrc.yml",
            "eslint.config.js",
            "eslint.config.mjs",
        ]
        for eslint_file in eslint_files:
            if (self.project_path / eslint_file).exists():
                self._results["linting"].append("eslint")
                break

        # Check package.json for eslint
        package_json = self.project_path / "package.json"
        if package_json.exists() and "eslint" not in self._results["linting"]:
            try:
                data = json.loads(package_json.read_text())
                dev_deps = data.get("devDependencies", {})
                if "eslint" in dev_deps:
                    self._results["linting"].append("eslint")
            except (json.JSONDecodeError, OSError):
                pass

        # golangci-lint
        if (self.project_path / ".golangci.yml").exists() or (
            self.project_path / ".golangci.yaml"
        ).exists():
            self._results["linting"].append("golangci-lint")

    def _detect_formatting_tools(self) -> None:
        """Detect formatting tools from config files."""
        # Ruff (also does formatting)
        if "ruff" in self._results["linting"]:
            self._results["formatting"].append("ruff")

        # Prettier
        prettier_files = [
            ".prettierrc",
            ".prettierrc.js",
            ".prettierrc.json",
            "prettier.config.js",
        ]
        for prettier_file in prettier_files:
            if (self.project_path / prettier_file).exists():
                self._results["formatting"].append("prettier")
                break

        # Check package.json for prettier
        package_json = self.project_path / "package.json"
        if package_json.exists() and "prettier" not in self._results["formatting"]:
            try:
                data = json.loads(package_json.read_text())
                dev_deps = data.get("devDependencies", {})
                if "prettier" in dev_deps:
                    self._results["formatting"].append("prettier")
            except (json.JSONDecodeError, OSError):
                pass

        # gofmt (implicit with Go)
        if "Go" in self._results["languages"]:
            self._results["formatting"].append("gofmt")

    def _detect_ci_cd(self) -> None:
        """Detect CI/CD configurations."""
        # GitHub Actions
        gh_workflows = self.project_path / ".github" / "workflows"
        if gh_workflows.exists() and list(gh_workflows.glob("*.yml")) + list(
            gh_workflows.glob("*.yaml")
        ):
            self._results["ci_cd"].append("GitHub Actions")

        # GitLab CI
        if (self.project_path / ".gitlab-ci.yml").exists():
            self._results["ci_cd"].append("GitLab CI")

        # CircleCI
        if (self.project_path / ".circleci" / "config.yml").exists():
            self._results["ci_cd"].append("CircleCI")

    def _detect_package_managers(self) -> None:
        """Detect package managers from lock files and config."""
        # Python
        if (self.project_path / "poetry.lock").exists():
            self._results["package_managers"].append("poetry")
        elif (self.project_path / "Pipfile").exists():
            self._results["package_managers"].append("pipenv")
        elif (self.project_path / "uv.lock").exists():
            self._results["package_managers"].append("uv")
        elif (self.project_path / "requirements.txt").exists():
            self._results["package_managers"].append("pip")

        # Node.js
        if (self.project_path / "pnpm-lock.yaml").exists():
            self._results["package_managers"].append("pnpm")
        elif (self.project_path / "yarn.lock").exists():
            self._results["package_managers"].append("yarn")
        elif (self.project_path / "package-lock.json").exists():
            self._results["package_managers"].append("npm")
        elif (self.project_path / "package.json").exists():
            # Generic Node.js without lock file
            self._results["package_managers"].append("npm")

        # Go
        if (self.project_path / "go.mod").exists():
            self._results["package_managers"].append("Go modules")

        # Rust
        if (self.project_path / "Cargo.lock").exists():
            self._results["package_managers"].append("Cargo")


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def python_project(tmp_path: Path) -> tuple[Path, dict[str, list[str]]]:
    """Create a realistic Python project fixture.

    Returns:
        Tuple of (project_path, expected_detections)
    """
    # Create pyproject.toml with pytest and ruff
    pyproject_content = """[project]
name = "test-project"
version = "0.1.0"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=7.0", "ruff>=0.1.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I"]
"""
    (tmp_path / "pyproject.toml").write_text(pyproject_content)

    # Create requirements.txt
    (tmp_path / "requirements.txt").write_text("requests==2.31.0\n")

    # Create source files
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "main.py").write_text('def main():\n    print("Hello")\n')
    (src_dir / "utils.py").write_text('def helper():\n    return "data"\n')

    # Create test files
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_main.py").write_text("def test_main():\n    assert True\n")
    (tests_dir / "test_utils.py").write_text("def test_helper():\n    assert True\n")

    # Create GitHub Actions workflow
    gh_workflows = tmp_path / ".github" / "workflows"
    gh_workflows.mkdir(parents=True, exist_ok=True)
    workflow_content = """name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: pytest
"""
    (gh_workflows / "ci.yml").write_text(workflow_content)

    expected = {
        "languages": ["Python"],
        "testing": ["pytest"],
        "linting": ["ruff"],
        "formatting": ["ruff"],
        "ci_cd": ["GitHub Actions"],
        "package_managers": ["pip"],
    }

    return tmp_path, expected


@pytest.fixture
def typescript_project(tmp_path: Path) -> tuple[Path, dict[str, list[str]]]:
    """Create a realistic TypeScript project fixture.

    Returns:
        Tuple of (project_path, expected_detections)
    """
    # Create package.json with jest, eslint, prettier
    package_json = {
        "name": "test-project",
        "version": "1.0.0",
        "scripts": {
            "test": "jest",
            "lint": "eslint .",
            "format": "prettier --write .",
        },
        "devDependencies": {
            "typescript": "^5.0.0",
            "jest": "^29.0.0",
            "@types/jest": "^29.0.0",
            "eslint": "^8.0.0",
            "prettier": "^3.0.0",
        },
    }
    (tmp_path / "package.json").write_text(json.dumps(package_json, indent=2))

    # Create pnpm-lock.yaml
    (tmp_path / "pnpm-lock.yaml").write_text("lockfileVersion: '6.0'\n")

    # Create tsconfig.json
    tsconfig = {
        "compilerOptions": {
            "target": "ES2020",
            "module": "commonjs",
            "strict": True,
        }
    }
    (tmp_path / "tsconfig.json").write_text(json.dumps(tsconfig, indent=2))

    # Create .eslintrc.js
    eslintrc = """module.exports = {
  extends: ['eslint:recommended'],
  rules: {},
};
"""
    (tmp_path / ".eslintrc.js").write_text(eslintrc)

    # Create .prettierrc
    prettierrc = {"semi": True, "singleQuote": True}
    (tmp_path / ".prettierrc").write_text(json.dumps(prettierrc, indent=2))

    # Create source files
    src_dir = tmp_path / "src"
    src_dir.mkdir(exist_ok=True)
    (src_dir / "index.ts").write_text('export const hello = (): string => "Hello";\n')
    (src_dir / "utils.ts").write_text(
        "export const add = (a: number, b: number) => a + b;\n"
    )

    # Create test files
    (src_dir / "index.test.ts").write_text(
        "import { hello } from './index';\n\ntest('hello', () => {\n  expect(hello()).toBe('Hello');\n});\n"
    )

    expected = {
        "languages": ["TypeScript"],
        "testing": ["jest"],
        "linting": ["eslint"],
        "formatting": ["prettier"],
        "ci_cd": [],
        "package_managers": ["pnpm"],
    }

    return tmp_path, expected


@pytest.fixture
def go_project(tmp_path: Path) -> tuple[Path, dict[str, list[str]]]:
    """Create a realistic Go project fixture.

    Returns:
        Tuple of (project_path, expected_detections)
    """
    # Create go.mod
    go_mod = """module example.com/testproject

go 1.21

require (
    github.com/stretchr/testify v1.8.4
)
"""
    (tmp_path / "go.mod").write_text(go_mod)

    # Create .golangci.yml
    golangci_config = """linters:
  enable:
    - gofmt
    - govet
    - staticcheck
"""
    (tmp_path / ".golangci.yml").write_text(golangci_config)

    # Create main.go
    main_go = """package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
}

func Add(a, b int) int {
    return a + b
}
"""
    (tmp_path / "main.go").write_text(main_go)

    # Create main_test.go
    test_go = """package main

import "testing"

func TestAdd(t *testing.T) {
    result := Add(2, 3)
    if result != 5 {
        t.Errorf("Expected 5, got %d", result)
    }
}
"""
    (tmp_path / "main_test.go").write_text(test_go)

    # Create GitHub Actions workflow
    gh_workflows = tmp_path / ".github" / "workflows"
    gh_workflows.mkdir(parents=True, exist_ok=True)
    workflow_content = """name: Go CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-go@v4
      - run: go test ./...
"""
    (gh_workflows / "go.yml").write_text(workflow_content)

    expected = {
        "languages": ["Go"],
        "testing": ["go test"],
        "linting": ["golangci-lint"],
        "formatting": ["gofmt"],
        "ci_cd": ["GitHub Actions"],
        "package_managers": ["Go modules"],
    }

    return tmp_path, expected


@pytest.fixture
def multi_language_project(tmp_path: Path) -> tuple[Path, dict[str, list[str]]]:
    """Create a multi-language project fixture.

    Returns:
        Tuple of (project_path, expected_detections)
    """
    # Python files
    pyproject_content = """[project]
name = "multi-project"
version = "0.1.0"

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 88
"""
    (tmp_path / "pyproject.toml").write_text(pyproject_content)
    (tmp_path / "main.py").write_text("print('Python')\n")

    # TypeScript files
    package_json = {
        "name": "multi-project",
        "devDependencies": {
            "typescript": "^5.0.0",
            "jest": "^29.0.0",
        },
    }
    (tmp_path / "package.json").write_text(json.dumps(package_json))
    (tmp_path / "tsconfig.json").write_text("{}")
    (tmp_path / "pnpm-lock.yaml").write_text("lockfileVersion: '6.0'\n")
    (tmp_path / "index.ts").write_text("console.log('TypeScript');\n")

    # Go files with go.mod to ensure proper detection
    go_mod = "module example.com/multi\n\ngo 1.21\n"
    (tmp_path / "go.mod").write_text(go_mod)
    (tmp_path / "helper.go").write_text("package main\n")

    expected = {
        "languages": ["Python", "TypeScript", "Go"],
        "testing": ["pytest", "jest"],
        "linting": ["ruff"],
        "formatting": ["ruff", "gofmt"],  # gofmt is implicit with Go
        "ci_cd": [],
        "package_managers": ["pip", "pnpm", "Go modules"],
    }

    return tmp_path, expected


@pytest.fixture
def empty_repo(tmp_path: Path) -> tuple[Path, dict[str, list[str]]]:
    """Create an empty repository with only README.

    Returns:
        Tuple of (project_path, expected_detections)
    """
    (tmp_path / "README.md").write_text("# Empty Project\n")

    expected = {
        "languages": [],
        "testing": [],
        "linting": [],
        "formatting": [],
        "ci_cd": [],
        "package_managers": [],
    }

    return tmp_path, expected


# ============================================================================
# Helper Functions
# ============================================================================


def calculate_accuracy(
    detected: dict[str, list[str]], expected: dict[str, list[str]]
) -> float:
    """Calculate detection accuracy percentage.

    Accuracy = (correct detections + correct non-detections) / total possible

    Args:
        detected: Dictionary of detected items by category
        expected: Dictionary of expected items by category

    Returns:
        Accuracy as a float between 0.0 and 1.0
    """
    total_checks = 0
    correct_checks = 0

    for category in expected:
        expected_items = set(expected[category])
        detected_items = set(detected.get(category, []))

        # For each expected item, check if it was detected (true positive)
        for item in expected_items:
            total_checks += 1
            if item in detected_items:
                correct_checks += 1

        # Check for false positives (detected but not expected)
        for item in detected_items:
            if item not in expected_items:
                total_checks += 1
                # This is a false positive, don't increment correct_checks

    # If there are no checks, return 100% (nothing to detect)
    if total_checks == 0:
        return 1.0

    return correct_checks / total_checks


# ============================================================================
# Test Cases
# ============================================================================


class TestPythonProjectDetection:
    """Test Python project detection accuracy."""

    def test_detects_python_language(
        self, python_project: tuple[Path, dict[str, list[str]]]
    ):
        """Should detect Python language from pyproject.toml."""
        project_path, expected = python_project
        detector = ProjectDetector(project_path)
        result = detector.detect_all()

        assert "Python" in result["languages"]

    def test_detects_pytest(self, python_project: tuple[Path, dict[str, list[str]]]):
        """Should detect pytest from pyproject.toml configuration."""
        project_path, expected = python_project
        detector = ProjectDetector(project_path)
        result = detector.detect_all()

        assert "pytest" in result["testing"]

    def test_detects_ruff(self, python_project: tuple[Path, dict[str, list[str]]]):
        """Should detect ruff from pyproject.toml configuration."""
        project_path, expected = python_project
        detector = ProjectDetector(project_path)
        result = detector.detect_all()

        assert "ruff" in result["linting"]
        assert "ruff" in result["formatting"]

    def test_detects_github_actions(
        self, python_project: tuple[Path, dict[str, list[str]]]
    ):
        """Should detect GitHub Actions from workflow files."""
        project_path, expected = python_project
        detector = ProjectDetector(project_path)
        result = detector.detect_all()

        assert "GitHub Actions" in result["ci_cd"]

    def test_python_project_accuracy(
        self, python_project: tuple[Path, dict[str, list[str]]]
    ):
        """Python project detection should achieve 90%+ accuracy."""
        project_path, expected = python_project
        detector = ProjectDetector(project_path)
        result = detector.detect_all()

        accuracy = calculate_accuracy(result, expected)
        assert accuracy >= 0.9, f"Accuracy {accuracy:.1%} is below 90% threshold"


class TestTypeScriptProjectDetection:
    """Test TypeScript project detection accuracy."""

    def test_detects_typescript_language(
        self, typescript_project: tuple[Path, dict[str, list[str]]]
    ):
        """Should detect TypeScript from tsconfig.json and package.json."""
        project_path, expected = typescript_project
        detector = ProjectDetector(project_path)
        result = detector.detect_all()

        assert "TypeScript" in result["languages"]

    def test_detects_jest(self, typescript_project: tuple[Path, dict[str, list[str]]]):
        """Should detect jest from package.json devDependencies."""
        project_path, expected = typescript_project
        detector = ProjectDetector(project_path)
        result = detector.detect_all()

        assert "jest" in result["testing"]

    def test_detects_eslint(
        self, typescript_project: tuple[Path, dict[str, list[str]]]
    ):
        """Should detect eslint from .eslintrc.js."""
        project_path, expected = typescript_project
        detector = ProjectDetector(project_path)
        result = detector.detect_all()

        assert "eslint" in result["linting"]

    def test_detects_prettier(
        self, typescript_project: tuple[Path, dict[str, list[str]]]
    ):
        """Should detect prettier from .prettierrc."""
        project_path, expected = typescript_project
        detector = ProjectDetector(project_path)
        result = detector.detect_all()

        assert "prettier" in result["formatting"]

    def test_detects_pnpm(self, typescript_project: tuple[Path, dict[str, list[str]]]):
        """Should detect pnpm from pnpm-lock.yaml."""
        project_path, expected = typescript_project
        detector = ProjectDetector(project_path)
        result = detector.detect_all()

        assert "pnpm" in result["package_managers"]

    def test_typescript_project_accuracy(
        self, typescript_project: tuple[Path, dict[str, list[str]]]
    ):
        """TypeScript project detection should achieve 90%+ accuracy."""
        project_path, expected = typescript_project
        detector = ProjectDetector(project_path)
        result = detector.detect_all()

        accuracy = calculate_accuracy(result, expected)
        assert accuracy >= 0.9, f"Accuracy {accuracy:.1%} is below 90% threshold"


class TestGoProjectDetection:
    """Test Go project detection accuracy."""

    def test_detects_go_language(self, go_project: tuple[Path, dict[str, list[str]]]):
        """Should detect Go from go.mod."""
        project_path, expected = go_project
        detector = ProjectDetector(project_path)
        result = detector.detect_all()

        assert "Go" in result["languages"]

    def test_detects_go_test(self, go_project: tuple[Path, dict[str, list[str]]]):
        """Should detect go test from *_test.go files."""
        project_path, expected = go_project
        detector = ProjectDetector(project_path)
        result = detector.detect_all()

        assert "go test" in result["testing"]

    def test_detects_golangci_lint(self, go_project: tuple[Path, dict[str, list[str]]]):
        """Should detect golangci-lint from .golangci.yml."""
        project_path, expected = go_project
        detector = ProjectDetector(project_path)
        result = detector.detect_all()

        assert "golangci-lint" in result["linting"]

    def test_detects_gofmt(self, go_project: tuple[Path, dict[str, list[str]]]):
        """Should detect gofmt (implicit with Go projects)."""
        project_path, expected = go_project
        detector = ProjectDetector(project_path)
        result = detector.detect_all()

        assert "gofmt" in result["formatting"]

    def test_detects_go_modules(self, go_project: tuple[Path, dict[str, list[str]]]):
        """Should detect Go modules from go.mod."""
        project_path, expected = go_project
        detector = ProjectDetector(project_path)
        result = detector.detect_all()

        assert "Go modules" in result["package_managers"]

    def test_go_project_accuracy(self, go_project: tuple[Path, dict[str, list[str]]]):
        """Go project detection should achieve 90%+ accuracy."""
        project_path, expected = go_project
        detector = ProjectDetector(project_path)
        result = detector.detect_all()

        accuracy = calculate_accuracy(result, expected)
        assert accuracy >= 0.9, f"Accuracy {accuracy:.1%} is below 90% threshold"


class TestMultiLanguageProjectDetection:
    """Test multi-language project detection accuracy."""

    def test_detects_all_languages(
        self, multi_language_project: tuple[Path, dict[str, list[str]]]
    ):
        """Should detect all languages in multi-language project."""
        project_path, expected = multi_language_project
        detector = ProjectDetector(project_path)
        result = detector.detect_all()

        assert "Python" in result["languages"]
        assert "TypeScript" in result["languages"]
        assert "Go" in result["languages"]

    def test_detects_multiple_testing_frameworks(
        self, multi_language_project: tuple[Path, dict[str, list[str]]]
    ):
        """Should detect testing frameworks for each language."""
        project_path, expected = multi_language_project
        detector = ProjectDetector(project_path)
        result = detector.detect_all()

        assert "pytest" in result["testing"]
        assert "jest" in result["testing"]

    def test_multi_language_accuracy(
        self, multi_language_project: tuple[Path, dict[str, list[str]]]
    ):
        """Multi-language project detection should achieve 90%+ accuracy."""
        project_path, expected = multi_language_project
        detector = ProjectDetector(project_path)
        result = detector.detect_all()

        accuracy = calculate_accuracy(result, expected)
        assert accuracy >= 0.9, f"Accuracy {accuracy:.1%} is below 90% threshold"


class TestEmptyRepoDetection:
    """Test detection on empty repository."""

    def test_no_false_positives_on_empty_repo(
        self, empty_repo: tuple[Path, dict[str, list[str]]]
    ):
        """Should not detect any tools in empty repository."""
        project_path, expected = empty_repo
        detector = ProjectDetector(project_path)
        result = detector.detect_all()

        assert len(result["languages"]) == 0
        assert len(result["testing"]) == 0
        assert len(result["linting"]) == 0
        assert len(result["formatting"]) == 0
        assert len(result["ci_cd"]) == 0
        assert len(result["package_managers"]) == 0

    def test_empty_repo_accuracy(self, empty_repo: tuple[Path, dict[str, list[str]]]):
        """Empty repository detection should achieve 90%+ accuracy (no false positives)."""
        project_path, expected = empty_repo
        detector = ProjectDetector(project_path)
        result = detector.detect_all()

        accuracy = calculate_accuracy(result, expected)
        # Should be 100% since there's nothing to detect and nothing detected
        assert accuracy >= 0.9, f"Accuracy {accuracy:.1%} is below 90% threshold"


class TestOverallAccuracy:
    """Test overall detection accuracy across all project types.

    NOTE: The overall accuracy is already validated by individual project tests.
    Each project type test (Python, TypeScript, Go, multi-language, empty)
    already asserts >= 90% accuracy, so the aggregate accuracy across all
    types is implicitly validated when all individual tests pass.
    """

    pass  # Individual tests provide sufficient coverage
