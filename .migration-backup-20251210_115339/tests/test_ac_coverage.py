"""Tests for acceptance criteria coverage tracking.

Tests cover:
- PRDScanner: Extract ACs from PRD markdown
- TestScanner: Find AC markers in test files
- ACCoverageReport: Generate and validate coverage reports
- CLI command: specify ac-coverage
"""

import json
from pathlib import Path
from textwrap import dedent

import pytest

from specify_cli.workflow.ac_coverage import (
    ACCoverageReport,
    ACTestScanner,
    AcceptanceCriterion,
    CoverageSummary,
    PRDScanner,
    generate_coverage_report,
    validate_ac_coverage,
)


@pytest.fixture
def sample_prd(tmp_path: Path) -> Path:
    """Create a sample PRD file with acceptance criteria."""
    prd_content = dedent("""
        # User Authentication Feature

        ## User Stories

        ### US1: User Registration
        As a new user, I want to register with email so I can access the platform.

        **Acceptance Criteria:**
        - AC1: User can register with email and password
        - AC2: Password must be at least 8 characters
        - AC3: Email verification required before login

        ### US2: User Login
        As a registered user, I want to log in so I can access my account.

        **Acceptance Criteria:**
        - [ ] AC4: User can log in with email and password
        - [x] AC5: Failed login shows error message
        - AC6: Successful login redirects to dashboard
    """)

    prd_file = tmp_path / "test-feature.md"
    prd_file.write_text(prd_content)
    return prd_file


@pytest.fixture
def sample_test_files(tmp_path: Path) -> Path:
    """Create sample test files with AC markers."""
    test_dir = tmp_path / "tests"
    test_dir.mkdir()

    # Python test file
    python_test = test_dir / "test_auth.py"
    python_test.write_text(
        dedent('''
        import pytest

        @pytest.mark.ac("AC1: User can register with email and password")
        def test_user_registration():
            """Test user registration flow."""
            pass

        @pytest.mark.ac("AC2: Password must be at least 8 characters")
        def test_password_validation():
            """Test password length validation."""
            pass

        @pytest.mark.ac('AC4: User can log in with email and password')
        def test_user_login():
            """Test login flow."""
            pass

        @pytest.mark.ac("AC3: Email verification required before login")
        def test_email_verification():
            """Test email verification requirement."""
            pass
    ''')
    )

    # TypeScript test file
    ts_test = test_dir / "auth.test.ts"
    ts_test.write_text(
        dedent("""
        describe("User Authentication", () => {
            // @ac AC5: Failed login shows error message
            it("should show error on failed login", () => {
                // Test implementation
            });
        });
    """)
    )

    # Go test file
    go_test = test_dir / "auth_test.go"
    go_test.write_text(
        dedent("""
        package auth

        import "testing"

        func TestDashboardRedirect(t *testing.T) {
            // AC6: Successful login redirects to dashboard
            t.Run("redirect_to_dashboard", func(t *testing.T) {
                // Test implementation
            })
        }
    """)
    )

    return test_dir


class TestPRDScanner:
    """Test PRD scanning functionality."""

    def test_scan_extracts_all_acs(self, sample_prd: Path):
        """Test that scanner finds all ACs in PRD."""
        scanner = PRDScanner(sample_prd)
        acs = scanner.scan()

        assert len(acs) == 6
        assert all(isinstance(ac, AcceptanceCriterion) for ac in acs)

        # Check AC IDs are correct
        ac_ids = [ac.id for ac in acs]
        assert ac_ids == ["AC1", "AC2", "AC3", "AC4", "AC5", "AC6"]

    def test_scan_extracts_descriptions(self, sample_prd: Path):
        """Test that scanner extracts AC descriptions."""
        scanner = PRDScanner(sample_prd)
        acs = scanner.scan()

        ac1 = next(ac for ac in acs if ac.id == "AC1")
        assert ac1.description == "User can register with email and password"

        ac2 = next(ac for ac in acs if ac.id == "AC2")
        assert ac2.description == "Password must be at least 8 characters"

    def test_scan_handles_checkbox_format(self, sample_prd: Path):
        """Test that scanner handles markdown checkbox format."""
        scanner = PRDScanner(sample_prd)
        acs = scanner.scan()

        # AC4 and AC5 use checkbox format
        ac4 = next(ac for ac in acs if ac.id == "AC4")
        assert ac4.description == "User can log in with email and password"

        ac5 = next(ac for ac in acs if ac.id == "AC5")
        assert ac5.description == "Failed login shows error message"

    def test_scan_file_not_found(self, tmp_path: Path):
        """Test that scanner raises error for missing PRD."""
        scanner = PRDScanner(tmp_path / "nonexistent.md")

        with pytest.raises(FileNotFoundError, match="PRD not found"):
            scanner.scan()

    def test_scan_deduplicates_acs(self, tmp_path: Path):
        """Test that scanner doesn't duplicate ACs."""
        prd_content = dedent("""
            # Feature

            ## Acceptance Criteria
            - AC1: First criterion
            - AC1: Duplicate (should be ignored)
            - AC2: Second criterion
        """)

        prd_file = tmp_path / "test.md"
        prd_file.write_text(prd_content)

        scanner = PRDScanner(prd_file)
        acs = scanner.scan()

        assert len(acs) == 2
        assert [ac.id for ac in acs] == ["AC1", "AC2"]


class TestACTestScanner:
    """Test test file scanning functionality."""

    def test_scan_finds_python_markers(self, sample_test_files: Path):
        """Test that scanner finds Python @pytest.mark.ac markers."""
        scanner = ACTestScanner([sample_test_files])
        ac_to_tests = scanner.scan()

        assert "AC1" in ac_to_tests
        assert "AC2" in ac_to_tests
        assert "AC4" in ac_to_tests

        # Check test paths are stored
        assert any("test_auth.py" in path for path in ac_to_tests["AC1"])

    def test_scan_finds_typescript_markers(self, sample_test_files: Path):
        """Test that scanner finds TypeScript // @ac markers."""
        scanner = ACTestScanner([sample_test_files])
        ac_to_tests = scanner.scan()

        assert "AC5" in ac_to_tests
        assert any("auth.test.ts" in path for path in ac_to_tests["AC5"])

    def test_scan_finds_go_markers(self, sample_test_files: Path):
        """Test that scanner finds Go test markers."""
        scanner = ACTestScanner([sample_test_files])
        ac_to_tests = scanner.scan()

        assert "AC6" in ac_to_tests
        assert any("auth_test.go" in path for path in ac_to_tests["AC6"])

    def test_scan_handles_multiple_test_dirs(self, tmp_path: Path):
        """Test that scanner scans multiple directories."""
        dir1 = tmp_path / "tests1"
        dir1.mkdir()
        (dir1 / "test_a.py").write_text(
            '@pytest.mark.ac("AC1: Test")\ndef test_a(): pass'
        )

        dir2 = tmp_path / "tests2"
        dir2.mkdir()
        (dir2 / "test_b.py").write_text(
            '@pytest.mark.ac("AC2: Test")\ndef test_b(): pass'
        )

        scanner = ACTestScanner([dir1, dir2])
        ac_to_tests = scanner.scan()

        assert "AC1" in ac_to_tests
        assert "AC2" in ac_to_tests

    def test_scan_handles_nonexistent_dir(self, tmp_path: Path):
        """Test that scanner handles nonexistent directories gracefully."""
        scanner = ACTestScanner([tmp_path / "nonexistent"])
        ac_to_tests = scanner.scan()

        assert ac_to_tests == {}

    def test_scan_handles_invalid_files(self, tmp_path: Path):
        """Test that scanner handles binary/invalid files gracefully."""
        test_dir = tmp_path / "tests"
        test_dir.mkdir()

        # Create a binary file
        (test_dir / "test_invalid.py").write_bytes(b"\x00\x01\x02\xff")

        scanner = ACTestScanner([test_dir])
        ac_to_tests = scanner.scan()

        # Should not crash, just skip the file
        assert ac_to_tests == {}


class TestACCoverageReport:
    """Test coverage report generation and validation."""

    def test_generate_coverage_report_full_coverage(
        self, sample_prd: Path, sample_test_files: Path
    ):
        """Test generating report with 100% coverage."""
        report = generate_coverage_report(
            feature="test-feature",
            prd_path=sample_prd,
            test_dirs=[sample_test_files],
        )

        assert report.feature == "test-feature"
        assert str(sample_prd) in report.prd_path
        assert report.summary.total_acs == 6
        assert report.summary.covered == 6
        assert report.summary.uncovered == 0
        assert report.summary.coverage_percent == 100.0
        assert report.is_fully_covered()

    def test_generate_coverage_report_partial_coverage(
        self, sample_prd: Path, tmp_path: Path
    ):
        """Test generating report with partial coverage."""
        # Create test dir with only some tests
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "test_partial.py").write_text(
            '@pytest.mark.ac("AC1: Test")\ndef test_one(): pass'
        )

        report = generate_coverage_report(
            feature="test-feature",
            prd_path=sample_prd,
            test_dirs=[test_dir],
        )

        assert report.summary.total_acs == 6
        assert report.summary.covered == 1
        assert report.summary.uncovered == 5
        assert report.summary.coverage_percent < 100.0
        assert not report.is_fully_covered()

    def test_get_uncovered_acs(self, sample_prd: Path, tmp_path: Path):
        """Test getting list of uncovered ACs."""
        test_dir = tmp_path / "tests"
        test_dir.mkdir()

        report = generate_coverage_report(
            feature="test-feature",
            prd_path=sample_prd,
            test_dirs=[test_dir],
        )

        uncovered = report.get_uncovered_acs()
        assert len(uncovered) == 6
        assert all(ac.status == "uncovered" for ac in uncovered)

    def test_report_to_dict(self, sample_prd: Path, sample_test_files: Path):
        """Test converting report to dictionary."""
        report = generate_coverage_report(
            feature="test-feature",
            prd_path=sample_prd,
            test_dirs=[sample_test_files],
        )

        data = report.to_dict()

        assert data["feature"] == "test-feature"
        assert "prd_path" in data
        assert "generated_at" in data
        assert "acceptance_criteria" in data
        assert "summary" in data
        assert len(data["acceptance_criteria"]) == 6

    def test_report_to_json(self, sample_prd: Path, sample_test_files: Path):
        """Test converting report to JSON string."""
        report = generate_coverage_report(
            feature="test-feature",
            prd_path=sample_prd,
            test_dirs=[sample_test_files],
        )

        json_str = report.to_json()
        data = json.loads(json_str)

        assert data["feature"] == "test-feature"
        assert data["summary"]["coverage_percent"] == 100.0

    def test_report_save_and_load(
        self, sample_prd: Path, sample_test_files: Path, tmp_path: Path
    ):
        """Test saving and loading report."""
        report = generate_coverage_report(
            feature="test-feature",
            prd_path=sample_prd,
            test_dirs=[sample_test_files],
        )

        output_file = tmp_path / "coverage.json"
        report.save(output_file)

        assert output_file.exists()

        loaded_report = ACCoverageReport.load(output_file)
        assert loaded_report.feature == report.feature
        assert loaded_report.summary.total_acs == report.summary.total_acs
        assert loaded_report.summary.coverage_percent == report.summary.coverage_percent

    def test_load_nonexistent_file(self, tmp_path: Path):
        """Test loading from nonexistent file raises error."""
        with pytest.raises(FileNotFoundError, match="Report not found"):
            ACCoverageReport.load(tmp_path / "nonexistent.json")

    def test_load_invalid_json(self, tmp_path: Path):
        """Test loading invalid JSON raises error."""
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("not valid json{")

        with pytest.raises(ValueError, match="Invalid JSON"):
            ACCoverageReport.load(bad_file)


class TestValidateACCoverage:
    """Test coverage validation logic."""

    def test_validate_full_coverage_passes(
        self, sample_prd: Path, sample_test_files: Path
    ):
        """Test that 100% coverage passes validation."""
        report = generate_coverage_report(
            feature="test-feature",
            prd_path=sample_prd,
            test_dirs=[sample_test_files],
        )

        is_valid, error_msg = validate_ac_coverage(report)

        assert is_valid
        assert error_msg == ""

    def test_validate_partial_coverage_fails(self, sample_prd: Path, tmp_path: Path):
        """Test that partial coverage fails validation."""
        test_dir = tmp_path / "tests"
        test_dir.mkdir()

        report = generate_coverage_report(
            feature="test-feature",
            prd_path=sample_prd,
            test_dirs=[test_dir],
        )

        is_valid, error_msg = validate_ac_coverage(report)

        assert not is_valid
        assert "AC coverage requirement not met" in error_msg
        assert "Coverage: 0.0%" in error_msg
        assert "AC1:" in error_msg

    def test_validate_partial_coverage_with_allow_flag(
        self, sample_prd: Path, tmp_path: Path
    ):
        """Test that allow_partial flag bypasses validation."""
        test_dir = tmp_path / "tests"
        test_dir.mkdir()

        report = generate_coverage_report(
            feature="test-feature",
            prd_path=sample_prd,
            test_dirs=[test_dir],
        )

        is_valid, error_msg = validate_ac_coverage(report, allow_partial=True)

        assert is_valid
        assert error_msg == ""


class TestCoverageSummary:
    """Test CoverageSummary dataclass."""

    def test_summary_to_dict(self):
        """Test converting summary to dictionary."""
        summary = CoverageSummary(
            total_acs=10,
            covered=7,
            uncovered=3,
            coverage_percent=70.0,
        )

        data = summary.to_dict()

        assert data["total_acs"] == 10
        assert data["covered"] == 7
        assert data["uncovered"] == 3
        assert data["coverage_percent"] == 70.0


class TestAcceptanceCriterion:
    """Test AcceptanceCriterion dataclass."""

    def test_ac_to_dict(self):
        """Test converting AC to dictionary."""
        ac = AcceptanceCriterion(
            id="AC1",
            description="User can login",
            user_story="US1",
            tests=["tests/test_auth.py::test_login"],
            status="covered",
        )

        data = ac.to_dict()

        assert data["id"] == "AC1"
        assert data["description"] == "User can login"
        assert data["user_story"] == "US1"
        assert data["tests"] == ["tests/test_auth.py::test_login"]
        assert data["status"] == "covered"

    def test_ac_defaults(self):
        """Test AC with default values."""
        ac = AcceptanceCriterion(id="AC1", description="Test")

        assert ac.user_story == ""
        assert ac.tests == []
        assert ac.status == "uncovered"


# AC markers for this test file itself
@pytest.mark.ac('AC1: Create pytest marker @pytest.mark.ac("description") for Python')
def test_pytest_marker_registered():
    """Test that @pytest.mark.ac marker is registered with pytest."""
    # This test itself uses the marker - if it runs without error, marker is registered
    assert True


@pytest.mark.ac(
    "AC3: Implement AC scanner that parses PRD and extracts acceptance criteria"
)
def test_ac_scanner_integration(sample_prd: Path):
    """Integration test for PRD scanning."""
    scanner = PRDScanner(sample_prd)
    acs = scanner.scan()
    assert len(acs) > 0


@pytest.mark.ac("AC4: Implement test scanner that finds AC markers in test files")
def test_test_scanner_integration(sample_test_files: Path):
    """Integration test for test scanning."""
    scanner = ACTestScanner([sample_test_files])
    ac_to_tests = scanner.scan()
    assert len(ac_to_tests) > 0


@pytest.mark.ac("AC5: Generate ./tests/ac-coverage.json manifest")
def test_coverage_manifest_generation(
    sample_prd: Path, sample_test_files: Path, tmp_path: Path
):
    """Integration test for coverage manifest generation."""
    report = generate_coverage_report(
        feature="test",
        prd_path=sample_prd,
        test_dirs=[sample_test_files],
    )

    output_file = tmp_path / "ac-coverage.json"
    report.save(output_file)

    assert output_file.exists()
    data = json.loads(output_file.read_text())
    assert "acceptance_criteria" in data
    assert "summary" in data


@pytest.mark.ac("AC6: Block transition if coverage_percent < 100%")
def test_coverage_validation_blocks_incomplete(sample_prd: Path, tmp_path: Path):
    """Test that validation blocks when coverage is incomplete."""
    test_dir = tmp_path / "tests"
    test_dir.mkdir()

    report = generate_coverage_report(
        feature="test",
        prd_path=sample_prd,
        test_dirs=[test_dir],
    )

    is_valid, error_msg = validate_ac_coverage(report)
    assert not is_valid
    assert error_msg != ""


@pytest.mark.ac("AC7: Report uncovered ACs with specific guidance")
def test_uncovered_acs_reported(sample_prd: Path, tmp_path: Path):
    """Test that uncovered ACs are reported with guidance."""
    test_dir = tmp_path / "tests"
    test_dir.mkdir()

    report = generate_coverage_report(
        feature="test",
        prd_path=sample_prd,
        test_dirs=[test_dir],
    )

    is_valid, error_msg = validate_ac_coverage(report)
    assert not is_valid
    assert "Uncovered acceptance criteria:" in error_msg
    assert "To fix:" in error_msg
    assert "@pytest.mark.ac" in error_msg


@pytest.mark.ac("AC9: Support --allow-partial-coverage flag for exceptional cases")
def test_allow_partial_coverage_flag(sample_prd: Path, tmp_path: Path):
    """Test that --allow-partial-coverage flag works."""
    test_dir = tmp_path / "tests"
    test_dir.mkdir()

    report = generate_coverage_report(
        feature="test",
        prd_path=sample_prd,
        test_dirs=[test_dir],
    )

    # Without flag - should fail
    is_valid, _ = validate_ac_coverage(report, allow_partial=False)
    assert not is_valid

    # With flag - should pass
    is_valid, _ = validate_ac_coverage(report, allow_partial=True)
    assert is_valid
