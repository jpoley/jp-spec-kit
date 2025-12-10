"""
Tests for test_executor module.
"""

import subprocess
from unittest.mock import Mock, patch

from specify_cli.test_executor import (
    ACMapper,
    LintExecutor,
    TestExecutor,
    TestFrameworkDetector,
    TestOutputParser,
    TestResult,
)


class TestTestFrameworkDetector:
    """Tests for TestFrameworkDetector."""

    def test_detect_pytest_with_pytest_ini(self, tmp_path):
        """Test pytest detection with pytest.ini file."""
        (tmp_path / "pytest.ini").touch()
        assert TestFrameworkDetector.detect(tmp_path) == "pytest"

    def test_detect_pytest_with_pyproject_toml(self, tmp_path):
        """Test pytest detection with pyproject.toml containing pytest config."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[tool.pytest.ini_options]\ntestpaths = ['tests']")
        assert TestFrameworkDetector.detect(tmp_path) == "pytest"

    def test_detect_vitest_with_config(self, tmp_path):
        """Test vitest detection with config file."""
        (tmp_path / "vitest.config.ts").touch()
        assert TestFrameworkDetector.detect(tmp_path) == "vitest"

    def test_detect_jest_with_config(self, tmp_path):
        """Test jest detection with config file."""
        (tmp_path / "jest.config.js").touch()
        assert TestFrameworkDetector.detect(tmp_path) == "jest"

    def test_detect_go_test_with_go_mod(self, tmp_path):
        """Test go test detection with go.mod file."""
        (tmp_path / "go.mod").touch()
        assert TestFrameworkDetector.detect(tmp_path) == "go_test"

    def test_detect_cargo_test_with_cargo_toml(self, tmp_path):
        """Test cargo test detection with Cargo.toml file."""
        (tmp_path / "Cargo.toml").touch()
        assert TestFrameworkDetector.detect(tmp_path) == "cargo_test"

    def test_detect_from_package_json_vitest(self, tmp_path):
        """Test vitest detection from package.json devDependencies."""
        package_json = tmp_path / "package.json"
        package_json.write_text('{"devDependencies": {"vitest": "^0.34.0"}}')
        assert TestFrameworkDetector.detect(tmp_path) == "vitest"

    def test_detect_from_package_json_jest(self, tmp_path):
        """Test jest detection from package.json devDependencies."""
        package_json = tmp_path / "package.json"
        package_json.write_text('{"devDependencies": {"jest": "^29.0.0"}}')
        assert TestFrameworkDetector.detect(tmp_path) == "jest"

    def test_detect_from_package_json_scripts(self, tmp_path):
        """Test framework detection from package.json scripts."""
        package_json = tmp_path / "package.json"
        package_json.write_text('{"scripts": {"test": "vitest run"}}')
        assert TestFrameworkDetector.detect(tmp_path) == "vitest"

    def test_detect_no_framework(self, tmp_path):
        """Test when no framework is detected."""
        assert TestFrameworkDetector.detect(tmp_path) is None


class TestTestOutputParser:
    """Tests for TestOutputParser."""

    def test_parse_pytest_success(self):
        """Test parsing successful pytest output."""
        output = """
test_auth.py::test_user_can_login PASSED
test_auth.py::test_user_can_logout PASSED
====== 2 passed in 1.23s ======
"""
        results, stats = TestOutputParser.parse_pytest(output, 0)

        assert len(results) == 2
        assert results[0].name == "test_auth.py::test_user_can_login"
        assert results[0].status == "passed"
        assert stats["total"] == 2
        assert stats["passed"] == 2
        assert stats["failed"] == 0

    def test_parse_pytest_with_failures(self):
        """Test parsing pytest output with failures."""
        output = """
test_auth.py::test_user_can_login PASSED
test_auth.py::test_invalid_credentials FAILED
====== 1 passed, 1 failed in 1.23s ======
"""
        results, stats = TestOutputParser.parse_pytest(output, 1)

        assert len(results) == 2
        assert results[1].status == "failed"
        assert stats["passed"] == 1
        assert stats["failed"] == 1

    def test_parse_pytest_with_skipped(self):
        """Test parsing pytest output with skipped tests."""
        output = """
test_auth.py::test_user_can_login PASSED
test_auth.py::test_future_feature SKIPPED
====== 1 passed, 1 skipped in 1.23s ======
"""
        results, stats = TestOutputParser.parse_pytest(output, 0)

        assert len(results) == 2
        assert results[1].status == "skipped"
        assert stats["skipped"] == 1

    def test_parse_vitest_success(self):
        """Test parsing successful vitest output."""
        output = """
✓ user can login (5ms)
✓ user can logout (3ms)
Tests  2 passed (2)
"""
        results, stats = TestOutputParser.parse_vitest(output, 0)

        assert len(results) == 2
        assert results[0].status == "passed"
        assert stats["passed"] == 2

    def test_parse_jest_success(self):
        """Test parsing successful jest output."""
        output = """
✓ user can login (5 ms)
✓ user can logout (3 ms)
Tests: 2 passed, 2 total
"""
        results, stats = TestOutputParser.parse_jest(output, 0)

        assert len(results) == 2
        assert stats["total"] == 2
        assert stats["passed"] == 2

    def test_parse_go_test_success(self):
        """Test parsing successful go test output."""
        output = """
--- PASS: TestUserCanLogin (0.00s)
--- PASS: TestUserCanLogout (0.01s)
PASS
"""
        results, stats = TestOutputParser.parse_go_test(output, 0)

        assert len(results) == 2
        assert results[0].name == "TestUserCanLogin"
        assert results[0].status == "passed"
        assert stats["passed"] == 2


class TestTestExecutor:
    """Tests for TestExecutor."""

    def test_init_with_detected_framework(self, tmp_path):
        """Test initialization with framework detection."""
        (tmp_path / "pytest.ini").touch()
        executor = TestExecutor(tmp_path)
        assert executor.framework == "pytest"

    def test_init_without_framework(self, tmp_path):
        """Test initialization without detected framework."""
        executor = TestExecutor(tmp_path)
        assert executor.framework is None

    @patch("subprocess.run")
    def test_execute_pytest_success(self, mock_run, tmp_path):
        """Test successful pytest execution."""
        (tmp_path / "pytest.ini").touch()

        mock_result = Mock()
        mock_result.stdout = (
            "test_auth.py::test_login PASSED\n====== 1 passed in 1.23s ======\n"
        )
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        executor = TestExecutor(tmp_path, timeout=60)
        report = executor.execute()

        assert report.framework == "pytest"
        assert report.success is True
        assert report.total_tests == 1
        assert report.passed == 1
        assert report.failed == 0

    @patch("subprocess.run")
    def test_execute_with_timeout(self, mock_run, tmp_path):
        """Test execution with timeout."""
        (tmp_path / "pytest.ini").touch()
        mock_run.side_effect = subprocess.TimeoutExpired("pytest", 60)

        executor = TestExecutor(tmp_path, timeout=60)
        report = executor.execute()

        assert report.timed_out is True
        assert report.error_message is not None
        assert "timed out" in report.error_message.lower()

    def test_execute_no_framework(self, tmp_path):
        """Test execution when no framework detected."""
        executor = TestExecutor(tmp_path)
        report = executor.execute()

        assert report.framework == "unknown"
        assert report.error_message == "No test framework detected"

    @patch("subprocess.run")
    def test_execute_with_failures(self, mock_run, tmp_path):
        """Test execution with test failures."""
        (tmp_path / "pytest.ini").touch()

        mock_result = Mock()
        mock_result.stdout = """
test_auth.py::test_login PASSED
test_auth.py::test_logout FAILED
====== 1 passed, 1 failed in 1.23s ======
"""
        mock_result.stderr = ""
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        executor = TestExecutor(tmp_path, timeout=60)
        report = executor.execute()

        assert report.success is False
        assert report.failed == 1


class TestACMapper:
    """Tests for ACMapper."""

    def test_map_tests_to_acs_exact_match(self):
        """Test mapping with exact word matches."""
        test_results = [
            TestResult(name="test_user_can_login", status="passed"),
            TestResult(name="test_user_can_logout", status="passed"),
        ]
        acceptance_criteria = [
            (1, "User can login", False),
            (2, "User can logout", False),
        ]

        mappings = ACMapper.map_tests_to_acs(test_results, acceptance_criteria)

        assert len(mappings) == 2
        assert mappings[0].ac_index == 1
        assert mappings[0].test_status == "passed"
        assert mappings[0].confidence > 0.5

    def test_map_tests_to_acs_partial_match(self):
        """Test mapping with partial matches."""
        test_results = [
            TestResult(name="test_user_authentication_flow", status="passed"),
        ]
        acceptance_criteria = [
            (1, "User can authenticate successfully", False),
        ]

        mappings = ACMapper.map_tests_to_acs(test_results, acceptance_criteria)

        assert len(mappings) == 1
        assert mappings[0].confidence > 0.3

    def test_map_tests_to_acs_no_match(self):
        """Test mapping with no matches."""
        test_results = [
            TestResult(name="test_database_connection", status="passed"),
        ]
        acceptance_criteria = [
            (1, "User can login", False),
        ]

        mappings = ACMapper.map_tests_to_acs(test_results, acceptance_criteria)

        assert len(mappings) == 0

    def test_extract_words(self):
        """Test word extraction from test names."""
        words = ACMapper._extract_words("test_user_can_login")
        assert "user" in words
        assert "login" in words
        assert "test" not in words  # Should be filtered out

    def test_extract_words_from_camel_case(self):
        """Test word extraction from CamelCase."""
        words = ACMapper._extract_words("TestUserCanLogin")
        assert "user" in words
        assert "login" in words

    def test_calculate_match_confidence_high(self):
        """Test high confidence matching."""
        confidence = ACMapper._calculate_match_confidence(
            "test_user_can_login", "User can login"
        )
        assert confidence > 0.6

    def test_calculate_match_confidence_low(self):
        """Test low confidence matching."""
        confidence = ACMapper._calculate_match_confidence(
            "test_database_setup", "User can login"
        )
        assert confidence < 0.2

    def test_map_tests_to_acs_empty_tests(self):
        """Test mapping with empty test list."""
        test_results = []
        acceptance_criteria = [
            (1, "User can login", False),
        ]
        mappings = ACMapper.map_tests_to_acs(test_results, acceptance_criteria)
        assert len(mappings) == 0

    def test_map_tests_to_acs_empty_acs(self):
        """Test mapping with empty AC list."""
        test_results = [
            TestResult(name="test_user_can_login", status="passed"),
        ]
        acceptance_criteria = []
        mappings = ACMapper.map_tests_to_acs(test_results, acceptance_criteria)
        assert len(mappings) == 0

    def test_extract_words_with_special_chars(self):
        """Test word extraction with special characters."""
        words = ACMapper._extract_words("test_user's_login-flow")
        assert "user" in words
        assert "login" in words
        assert "flow" in words

    def test_extract_words_empty_string(self):
        """Test word extraction from empty string."""
        words = ACMapper._extract_words("")
        assert len(words) == 0

    def test_sequence_match_bonus_no_sequence(self):
        """Test sequence bonus with no matches."""
        bonus = ACMapper._sequence_match_bonus(["foo", "bar"], ["baz", "qux"])
        assert bonus == 0.0

    def test_sequence_match_bonus_full_sequence(self):
        """Test sequence bonus with full sequence match."""
        bonus = ACMapper._sequence_match_bonus(
            ["user", "can", "login"], ["user", "can", "login"]
        )
        assert bonus == 3 * ACMapper.SEQUENCE_BONUS_MULTIPLIER

    def test_sequence_match_bonus_partial_sequence(self):
        """Test sequence bonus with partial sequence match."""
        bonus = ACMapper._sequence_match_bonus(
            ["user", "login"], ["user", "can", "login"]
        )
        # Should match "user" then "login" (2 in sequence)
        assert bonus == 2 * ACMapper.SEQUENCE_BONUS_MULTIPLIER


class TestLintExecutor:
    """Tests for LintExecutor."""

    def test_detect_python_project(self, tmp_path):
        """Test Python project detection."""
        (tmp_path / "pyproject.toml").touch()
        assert LintExecutor.detect_project_type(tmp_path) == "python"

    def test_detect_javascript_project(self, tmp_path):
        """Test JavaScript project detection."""
        package_json = tmp_path / "package.json"
        package_json.write_text('{"name": "test-project"}')
        assert LintExecutor.detect_project_type(tmp_path) == "javascript"

    def test_detect_typescript_project(self, tmp_path):
        """Test TypeScript project detection."""
        package_json = tmp_path / "package.json"
        package_json.write_text('{"devDependencies": {"typescript": "^5.0.0"}}')
        assert LintExecutor.detect_project_type(tmp_path) == "typescript"

    def test_detect_go_project(self, tmp_path):
        """Test Go project detection."""
        (tmp_path / "go.mod").touch()
        assert LintExecutor.detect_project_type(tmp_path) == "go"

    def test_detect_unknown_project(self, tmp_path):
        """Test unknown project type."""
        assert LintExecutor.detect_project_type(tmp_path) is None

    @patch("subprocess.run")
    def test_run_linting_success(self, mock_run, tmp_path):
        """Test successful linting."""
        (tmp_path / "pyproject.toml").touch()

        mock_result = Mock()
        mock_result.stdout = "All checks passed!"
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = LintExecutor.run_linting(tmp_path)

        assert result is not None
        assert result.passed is True
        assert result.issues_count == 0

    @patch("subprocess.run")
    def test_run_linting_with_errors(self, mock_run, tmp_path):
        """Test linting with errors."""
        (tmp_path / "pyproject.toml").touch()

        mock_result = Mock()
        mock_result.stdout = "error: Line too long\nwarning: Unused import"
        mock_result.stderr = ""
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        result = LintExecutor.run_linting(tmp_path)

        assert result is not None
        assert result.passed is False
        assert result.issues_count == 2  # 1 error + 1 warning

    @patch("subprocess.run")
    def test_run_linting_timeout(self, mock_run, tmp_path):
        """Test linting timeout."""
        (tmp_path / "pyproject.toml").touch()
        mock_run.side_effect = subprocess.TimeoutExpired("ruff", 60)

        result = LintExecutor.run_linting(tmp_path)

        assert result is not None
        assert result.passed is False
        assert "timed out" in result.output.lower()

    @patch("subprocess.run")
    def test_run_linting_tool_not_found(self, mock_run, tmp_path):
        """Test when linting tool is not installed."""
        (tmp_path / "pyproject.toml").touch()
        mock_run.side_effect = FileNotFoundError()

        result = LintExecutor.run_linting(tmp_path)

        assert result is None


class TestIntegration:
    """Integration tests for the full workflow."""

    @patch("subprocess.run")
    def test_full_workflow_pytest(self, mock_run, tmp_path):
        """Test complete workflow with pytest."""
        (tmp_path / "pytest.ini").touch()
        (tmp_path / "pyproject.toml").touch()

        # Mock test execution
        test_result = Mock()
        test_result.stdout = """
test_auth.py::test_user_can_login PASSED
test_auth.py::test_user_can_logout PASSED
====== 2 passed in 1.23s ======
"""
        test_result.stderr = ""
        test_result.returncode = 0

        # Mock linting
        lint_result = Mock()
        lint_result.stdout = "All checks passed!"
        lint_result.stderr = ""
        lint_result.returncode = 0

        mock_run.side_effect = [test_result, lint_result]

        # Execute tests
        executor = TestExecutor(tmp_path, timeout=60)
        report = executor.execute()

        # Map to ACs
        acceptance_criteria = [
            (1, "User can login", False),
            (2, "User can logout", False),
        ]
        mappings = ACMapper.map_tests_to_acs(report.results, acceptance_criteria)

        # Run linting
        lint = LintExecutor.run_linting(tmp_path)

        # Verify results
        assert report.success is True
        assert len(mappings) == 2
        assert lint.passed is True

    @patch("subprocess.run")
    def test_full_workflow_with_failures(self, mock_run, tmp_path):
        """Test workflow with test failures."""
        (tmp_path / "pytest.ini").touch()

        test_result = Mock()
        test_result.stdout = """
test_auth.py::test_user_can_login PASSED
test_auth.py::test_user_can_logout FAILED
====== 1 passed, 1 failed in 1.23s ======
"""
        test_result.stderr = ""
        test_result.returncode = 1
        mock_run.return_value = test_result

        executor = TestExecutor(tmp_path, timeout=60)
        report = executor.execute()

        acceptance_criteria = [
            (1, "User can login", False),
            (2, "User can logout", False),
        ]
        mappings = ACMapper.map_tests_to_acs(report.results, acceptance_criteria)

        # Verify failure is captured
        assert report.success is False
        assert len(mappings) == 2
        assert mappings[1].test_status == "failed"
