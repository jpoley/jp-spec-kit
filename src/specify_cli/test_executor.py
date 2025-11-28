"""
Test execution module for automated validation of acceptance criteria.

This module detects project test frameworks, executes tests, parses results,
and maps test outcomes to acceptance criteria for automated validation.
"""

import json
import re
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class TestResult:
    """Represents a single test result."""

    name: str
    status: str  # "passed", "failed", "skipped"
    duration: float = 0.0
    error_message: Optional[str] = None
    file_path: Optional[str] = None


@dataclass
class LintResult:
    """Represents linting check results."""

    tool: str
    passed: bool
    issues_count: int
    issues: List[Dict[str, Any]] = field(default_factory=list)
    output: str = ""


@dataclass
class ACMapping:
    """Maps a test to an acceptance criterion."""

    ac_index: int
    ac_text: str
    test_name: str
    test_status: str
    confidence: float  # 0.0 to 1.0 matching confidence


@dataclass
class TestExecutionReport:
    """Comprehensive report of test execution and AC mapping."""

    framework: str
    command_run: str
    duration: float
    total_tests: int
    passed: int
    failed: int
    skipped: int
    results: List[TestResult] = field(default_factory=list)
    ac_mappings: List[ACMapping] = field(default_factory=list)
    lint_results: Optional[LintResult] = None
    success: bool = False
    error_message: Optional[str] = None
    timed_out: bool = False


class TestFrameworkDetector:
    """Detects the test framework used in a project."""

    FRAMEWORK_MARKERS = {
        "pytest": [
            "pytest.ini",
            "pyproject.toml",  # Check for [tool.pytest] section
            "setup.cfg",  # Check for [tool:pytest] section
            "tests/conftest.py",
        ],
        "vitest": [
            "vitest.config.ts",
            "vitest.config.js",
            "vitest.config.mjs",
        ],
        "jest": [
            "jest.config.js",
            "jest.config.ts",
            "jest.config.json",
        ],
        "go_test": [
            "go.mod",
        ],
        "cargo_test": [
            "Cargo.toml",
        ],
    }

    @staticmethod
    def detect(project_path: Path) -> Optional[str]:
        """
        Detect the test framework by checking for config files.

        Args:
            project_path: Root directory of the project

        Returns:
            Framework name or None if not detected
        """
        for framework, markers in TestFrameworkDetector.FRAMEWORK_MARKERS.items():
            for marker in markers:
                marker_path = project_path / marker
                if marker_path.exists():
                    # Additional validation for Python tools
                    if framework == "pytest" and marker == "pyproject.toml":
                        if not TestFrameworkDetector._has_pytest_config(marker_path):
                            continue
                    return framework

        # Fallback: check package.json for test scripts
        package_json = project_path / "package.json"
        if package_json.exists():
            return TestFrameworkDetector._detect_from_package_json(package_json)

        return None

    @staticmethod
    def _has_pytest_config(pyproject_path: Path) -> bool:
        """Check if pyproject.toml has pytest configuration."""
        try:
            content = pyproject_path.read_text()
            return "[tool.pytest" in content or "pytest" in content.lower()
        except Exception:
            # Safe to ignore: if pyproject.toml is missing or malformed,
            # pytest is not configured and we return False
            return False

    @staticmethod
    def _detect_from_package_json(package_json_path: Path) -> Optional[str]:
        """Detect framework from package.json scripts and dependencies."""
        try:
            with open(package_json_path) as f:
                data = json.load(f)

            # Check devDependencies
            dev_deps = data.get("devDependencies", {})
            if "vitest" in dev_deps:
                return "vitest"
            if "jest" in dev_deps or "@jest/core" in dev_deps:
                return "jest"

            # Check scripts
            scripts = data.get("scripts", {})
            test_script = scripts.get("test", "")
            if "vitest" in test_script:
                return "vitest"
            if "jest" in test_script:
                return "jest"

        except Exception:
            # Safe to ignore: if package.json is missing or malformed,
            # we cannot detect framework and will return None
            pass

        return None


class TestOutputParser:
    """Parses test output from different frameworks."""

    @staticmethod
    def parse_pytest(output: str, exit_code: int) -> Tuple[List[TestResult], Dict[str, int]]:
        """Parse pytest output."""
        results = []
        stats = {"total": 0, "passed": 0, "failed": 0, "skipped": 0}

        # Parse test results from output
        # pytest format: "test_file.py::test_name PASSED"
        test_pattern = re.compile(r"^(.+?)::(test_\w+)\s+(PASSED|FAILED|SKIPPED)", re.MULTILINE)
        for match in test_pattern.finditer(output):
            file_path, test_name, status = match.groups()
            results.append(TestResult(
                name=f"{file_path}::{test_name}",
                status=status.lower(),
                file_path=file_path,
            ))

        # Parse summary line: "====== 5 passed, 2 failed in 1.23s ======"
        summary_pattern = re.compile(
            r"=+\s*(?:(\d+)\s+passed)?(?:,\s*)?(?:(\d+)\s+failed)?(?:,\s*)?(?:(\d+)\s+skipped)?"
        )
        summary_match = summary_pattern.search(output)
        if summary_match:
            passed, failed, skipped = summary_match.groups()
            stats["passed"] = int(passed) if passed else 0
            stats["failed"] = int(failed) if failed else 0
            stats["skipped"] = int(skipped) if skipped else 0
            stats["total"] = stats["passed"] + stats["failed"] + stats["skipped"]

        return results, stats

    @staticmethod
    def parse_vitest(output: str, exit_code: int) -> Tuple[List[TestResult], Dict[str, int]]:
        """Parse vitest output."""
        results = []
        stats = {"total": 0, "passed": 0, "failed": 0, "skipped": 0}

        # Vitest format: "✓ test_name (5ms)"
        test_pattern = re.compile(r"^[✓×⊘]\s+(.+?)(?:\s+\(\d+ms\))?$", re.MULTILINE)
        for match in test_pattern.finditer(output):
            test_name = match.group(1).strip()
            status = "passed" if output[match.start()] == "✓" else "failed"
            results.append(TestResult(
                name=test_name,
                status=status,
            ))

        # Parse summary: "Test Files  2 passed (2)"
        summary_pattern = re.compile(r"Tests\s+(\d+)\s+passed.*?(?:(\d+)\s+failed)?")
        summary_match = summary_pattern.search(output)
        if summary_match:
            passed, failed = summary_match.groups()
            stats["passed"] = int(passed) if passed else 0
            stats["failed"] = int(failed) if failed else 0
            stats["total"] = stats["passed"] + stats["failed"]

        return results, stats

    @staticmethod
    def parse_jest(output: str, exit_code: int) -> Tuple[List[TestResult], Dict[str, int]]:
        """Parse jest output."""
        results = []
        stats = {"total": 0, "passed": 0, "failed": 0, "skipped": 0}

        # Jest format similar to vitest
        test_pattern = re.compile(r"^[✓×○]\s+(.+?)(?:\s+\(\d+\s*ms\))?$", re.MULTILINE)
        for match in test_pattern.finditer(output):
            test_name = match.group(1).strip()
            marker = output[match.start()]
            if marker == "✓":
                status = "passed"
            elif marker == "×":
                status = "failed"
            else:
                status = "skipped"

            results.append(TestResult(
                name=test_name,
                status=status,
            ))

        # Parse summary: "Tests: 5 passed, 5 total"
        summary_pattern = re.compile(
            r"Tests:\s+(?:(\d+)\s+passed)?(?:,\s*)?(?:(\d+)\s+failed)?(?:,\s*)?(?:(\d+)\s+skipped)?(?:,\s*)?(\d+)\s+total"
        )
        summary_match = summary_pattern.search(output)
        if summary_match:
            passed, failed, skipped, total = summary_match.groups()
            stats["passed"] = int(passed) if passed else 0
            stats["failed"] = int(failed) if failed else 0
            stats["skipped"] = int(skipped) if skipped else 0
            stats["total"] = int(total) if total else 0

        return results, stats

    @staticmethod
    def parse_go_test(output: str, exit_code: int) -> Tuple[List[TestResult], Dict[str, int]]:
        """Parse go test output."""
        results = []
        stats = {"total": 0, "passed": 0, "failed": 0, "skipped": 0}

        # Go test format: "--- PASS: TestName (0.00s)"
        test_pattern = re.compile(r"^---\s+(PASS|FAIL|SKIP):\s+(\w+)", re.MULTILINE)
        for match in test_pattern.finditer(output):
            status, test_name = match.groups()
            # Convert to standard status names
            if status == "PASS":
                status_normalized = "passed"
            elif status == "FAIL":
                status_normalized = "failed"
            else:  # SKIP
                status_normalized = "skipped"

            results.append(TestResult(
                name=test_name,
                status=status_normalized,
            ))

        # Count from results
        for result in results:
            stats["total"] += 1
            if result.status == "passed":
                stats["passed"] += 1
            elif result.status == "failed":
                stats["failed"] += 1
            elif result.status == "skipped":
                stats["skipped"] += 1

        return results, stats


class TestExecutor:
    """Executes tests and generates execution reports."""

    DEFAULT_TIMEOUT = 300  # 5 minutes

    FRAMEWORK_COMMANDS = {
        "pytest": ["python", "-m", "pytest", "-v"],
        "vitest": ["npx", "vitest", "run"],
        "jest": ["npx", "jest"],
        "go_test": ["go", "test", "-v", "./..."],
        "cargo_test": ["cargo", "test"],
    }

    def __init__(self, project_path: Path, timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize test executor.

        Args:
            project_path: Root directory of the project
            timeout: Maximum execution time in seconds
        """
        self.project_path = project_path
        self.timeout = timeout
        self.framework = TestFrameworkDetector.detect(project_path)

    def execute(self) -> TestExecutionReport:
        """
        Execute tests and generate report.

        Returns:
            TestExecutionReport with results and mappings
        """
        if not self.framework:
            return TestExecutionReport(
                framework="unknown",
                command_run="",
                duration=0.0,
                total_tests=0,
                passed=0,
                failed=0,
                skipped=0,
                error_message="No test framework detected",
            )

        # Run tests
        start_time = time.time()
        try:
            result = self._run_tests()
            duration = time.time() - start_time
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return TestExecutionReport(
                framework=self.framework,
                command_run=" ".join(self.FRAMEWORK_COMMANDS[self.framework]),
                duration=duration,
                total_tests=0,
                passed=0,
                failed=0,
                skipped=0,
                error_message=f"Test execution timed out after {self.timeout}s",
                timed_out=True,
            )

        # Parse results
        test_results, stats = self._parse_output(result.stdout + result.stderr, result.returncode)

        # Create report
        report = TestExecutionReport(
            framework=self.framework,
            command_run=" ".join(self.FRAMEWORK_COMMANDS[self.framework]),
            duration=duration,
            total_tests=stats["total"],
            passed=stats["passed"],
            failed=stats["failed"],
            skipped=stats["skipped"],
            results=test_results,
            success=(stats["failed"] == 0 and stats["passed"] > 0),
        )

        return report

    def _run_tests(self) -> subprocess.CompletedProcess:
        """Run test command and capture output."""
        command = self.FRAMEWORK_COMMANDS[self.framework]

        return subprocess.run(
            command,
            cwd=self.project_path,
            capture_output=True,
            text=True,
            timeout=self.timeout,
        )

    def _parse_output(self, output: str, exit_code: int) -> Tuple[List[TestResult], Dict[str, int]]:
        """Parse test output based on framework."""
        parser_map = {
            "pytest": TestOutputParser.parse_pytest,
            "vitest": TestOutputParser.parse_vitest,
            "jest": TestOutputParser.parse_jest,
            "go_test": TestOutputParser.parse_go_test,
            "cargo_test": TestOutputParser.parse_go_test,  # Cargo uses similar format
        }

        parser = parser_map.get(self.framework)
        if parser:
            return parser(output, exit_code)

        return [], {"total": 0, "passed": 0, "failed": 0, "skipped": 0}


class ACMapper:
    """Maps test results to acceptance criteria."""

    # Matching configuration constants
    MIN_CONFIDENCE_THRESHOLD = 0.3
    SEQUENCE_BONUS_MULTIPLIER = 0.1

    @staticmethod
    def map_tests_to_acs(
        test_results: List[TestResult],
        acceptance_criteria: List[Tuple[int, str, bool]]
    ) -> List[ACMapping]:
        """
        Map test results to acceptance criteria using fuzzy matching.

        Args:
            test_results: List of test results
            acceptance_criteria: List of (index, text, checked) tuples

        Returns:
            List of AC mappings with confidence scores
        """
        mappings = []

        for ac_index, ac_text, _ in acceptance_criteria:
            # Find best matching test
            best_match = None
            best_confidence = 0.0

            for test in test_results:
                confidence = ACMapper._calculate_match_confidence(test.name, ac_text)
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = test

            # Only create mapping if confidence is above threshold
            if best_match and best_confidence > ACMapper.MIN_CONFIDENCE_THRESHOLD:
                mappings.append(ACMapping(
                    ac_index=ac_index,
                    ac_text=ac_text,
                    test_name=best_match.name,
                    test_status=best_match.status,
                    confidence=best_confidence,
                ))

        return mappings

    @staticmethod
    def _calculate_match_confidence(test_name: str, ac_text: str) -> float:
        """
        Calculate matching confidence between test name and AC text.

        Uses fuzzy string matching algorithm with the following steps:
        1. Extract words from test name (strip test_, Test, etc.)
        2. Extract words from AC text
        3. Calculate word overlap ratio (common words / AC words)
        4. Add sequence bonus for consecutive word matches
        5. Return combined score capped at 1.0

        Algorithm:
        - overlap_ratio = len(common_words) / len(ac_words)
        - sequence_bonus = max_consecutive_matches * SEQUENCE_BONUS_MULTIPLIER
        - confidence = min(overlap_ratio + sequence_bonus, 1.0)

        Returns:
            Confidence score from 0.0 to 1.0
        """
        # Normalize test name
        test_words = ACMapper._extract_words(test_name)
        ac_words = ACMapper._extract_words(ac_text)

        if not test_words or not ac_words:
            return 0.0

        # Calculate word overlap
        common_words = set(test_words) & set(ac_words)
        if not common_words:
            return 0.0

        # Base confidence on word overlap ratio (using AC words as denominator)
        overlap_ratio = len(common_words) / len(ac_words)

        # Bonus for sequential matches
        sequence_bonus = ACMapper._sequence_match_bonus(test_words, ac_words)

        return min(overlap_ratio + sequence_bonus, 1.0)

    @staticmethod
    def _extract_words(text: str) -> List[str]:
        """Extract meaningful words from text."""
        # Remove common test prefixes/suffixes
        text = re.sub(r'^test_|_test$|^Test|Test$', '', text, flags=re.IGNORECASE)

        # Split CamelCase and snake_case into words
        # Insert space before capital letters
        text = re.sub(r'([A-Z])', r' \1', text)
        # Replace underscores with spaces
        text = text.replace('_', ' ')

        # Split on non-alphanumeric, convert to lowercase
        words = re.findall(r'[a-z0-9]+', text.lower())

        # Filter out very short words and common noise
        noise_words = {'a', 'an', 'the', 'is', 'are', 'be', 'to', 'of', 'in', 'on'}
        return [w for w in words if len(w) > 2 and w not in noise_words]

    @staticmethod
    def _sequence_match_bonus(words1: List[str], words2: List[str]) -> float:
        """Calculate bonus for sequential word matches."""
        max_sequence = 0
        current_sequence = 0

        i = 0
        for word in words1:
            if word in words2[i:]:
                current_sequence += 1
                # Fix index bug: search in remaining slice and adjust offset
                i = words2[i:].index(word) + i + 1
            else:
                max_sequence = max(max_sequence, current_sequence)
                current_sequence = 0

        max_sequence = max(max_sequence, current_sequence)
        return max_sequence * ACMapper.SEQUENCE_BONUS_MULTIPLIER


class LintExecutor:
    """Executes linting checks."""

    LINT_COMMANDS = {
        "python": ["ruff", "check", "."],
        "javascript": ["npx", "eslint", "."],
        "typescript": ["npx", "eslint", "."],
        "go": ["golangci-lint", "run"],
    }

    @staticmethod
    def detect_project_type(project_path: Path) -> Optional[str]:
        """Detect project type for linting."""
        if (project_path / "pyproject.toml").exists() or (project_path / "setup.py").exists():
            return "python"
        if (project_path / "package.json").exists():
            package_json = project_path / "package.json"
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    if "typescript" in data.get("devDependencies", {}):
                        return "typescript"
                    return "javascript"
            except Exception:
                # Safe to ignore: if package.json is malformed,
                # default to javascript as a reasonable fallback
                return "javascript"
        if (project_path / "go.mod").exists():
            return "go"
        return None

    @staticmethod
    def run_linting(project_path: Path) -> Optional[LintResult]:
        """
        Run linting checks for the project.

        Args:
            project_path: Root directory of the project

        Returns:
            LintResult or None if no linter available
        """
        project_type = LintExecutor.detect_project_type(project_path)
        if not project_type or project_type not in LintExecutor.LINT_COMMANDS:
            return None

        command = LintExecutor.LINT_COMMANDS[project_type]

        try:
            result = subprocess.run(
                command,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=60,  # 1 minute timeout for linting
            )

            output = result.stdout + result.stderr
            passed = result.returncode == 0

            # Count issues (simple heuristic)
            issues_count = output.count("error") + output.count("warning")

            return LintResult(
                tool=" ".join(command),
                passed=passed,
                issues_count=issues_count,
                output=output,
            )

        except subprocess.TimeoutExpired:
            return LintResult(
                tool=" ".join(command),
                passed=False,
                issues_count=0,
                output="Linting timed out",
            )
        except FileNotFoundError:
            # Linter not installed
            return None
