"""Tests for pre-implementation quality gates.

Tests .claude/hooks/pre-implement.py functionality including:
- Required files validation
- Spec completeness checks
- Constitutional compliance
- Quality threshold scoring
- Tiered thresholds
"""

import importlib.util
import sys
from pathlib import Path

# Load pre-implement.py module directly by file path
_hooks_dir = Path(__file__).resolve().parent.parent / ".claude" / "hooks"
_module_path = _hooks_dir / "pre-implement.py"

spec = importlib.util.spec_from_file_location("pre_implement", _module_path)
pre_implement = importlib.util.module_from_spec(spec)
sys.modules["pre_implement"] = pre_implement
spec.loader.exec_module(pre_implement)

# Import symbols from loaded module
AMBIGUITY_MARKERS = pre_implement.AMBIGUITY_MARKERS
EXIT_FAILURE = pre_implement.EXIT_FAILURE
EXIT_SUCCESS = pre_implement.EXIT_SUCCESS
TIER_THRESHOLDS = pre_implement.TIER_THRESHOLDS
GateResult = pre_implement.GateResult
QualityReport = pre_implement.QualityReport
calculate_quality_score = pre_implement.calculate_quality_score
check_constitutional_compliance = pre_implement.check_constitutional_compliance
check_quality_threshold = pre_implement.check_quality_threshold
check_required_files = pre_implement.check_required_files
check_spec_completeness = pre_implement.check_spec_completeness
get_quality_recommendations = pre_implement.get_quality_recommendations
run_quality_gates = pre_implement.run_quality_gates


class TestTierThresholds:
    """Test tier threshold configuration."""

    def test_light_threshold(self):
        """Light tier has lowest threshold."""
        assert TIER_THRESHOLDS["light"] == 50

    def test_medium_threshold(self):
        """Medium tier has moderate threshold."""
        assert TIER_THRESHOLDS["medium"] == 70

    def test_heavy_threshold(self):
        """Heavy tier has highest threshold."""
        assert TIER_THRESHOLDS["heavy"] == 85

    def test_thresholds_are_ordered(self):
        """Thresholds increase from light to heavy."""
        assert TIER_THRESHOLDS["light"] < TIER_THRESHOLDS["medium"]
        assert TIER_THRESHOLDS["medium"] < TIER_THRESHOLDS["heavy"]


class TestGateResult:
    """Test GateResult dataclass."""

    def test_passed_gate(self):
        """Test creating a passed gate result."""
        result = GateResult(
            name="test_gate",
            passed=True,
            message="All good",
        )
        assert result.passed is True
        assert result.name == "test_gate"
        assert result.details == []

    def test_failed_gate_with_details(self):
        """Test creating a failed gate result with details."""
        result = GateResult(
            name="test_gate",
            passed=False,
            message="Something wrong",
            details=["Detail 1", "Detail 2"],
        )
        assert result.passed is False
        assert len(result.details) == 2


class TestQualityReport:
    """Test QualityReport dataclass."""

    def test_to_dict(self):
        """Test JSON serialization."""
        gate = GateResult(name="test", passed=True, message="OK")
        report = QualityReport(
            passed=True,
            gates=[gate],
            tier="medium",
            threshold=70,
        )

        result = report.to_dict()

        assert result["passed"] is True
        assert result["tier"] == "medium"
        assert result["threshold"] == 70
        assert len(result["gates"]) == 1
        assert result["gates"][0]["name"] == "test"

    def test_skipped_report(self):
        """Test skipped quality check report."""
        report = QualityReport(
            passed=True,
            gates=[],
            tier="medium",
            threshold=70,
            skipped=True,
        )

        result = report.to_dict()
        assert result["skipped"] is True


class TestRequiredFilesGate:
    """Test Gate 1: Required files validation."""

    def test_all_files_present(self, tmp_path):
        """Pass when all required files exist."""
        spec_dir = tmp_path / "docs" / "prd"
        adr_dir = tmp_path / "docs" / "adr"
        spec_dir.mkdir(parents=True)
        adr_dir.mkdir(parents=True)

        (spec_dir / "spec.md").write_text("# Spec")
        (adr_dir / "plan.md").write_text("# Plan")
        (tmp_path / "tasks.md").write_text("# Tasks")

        result = check_required_files(spec_dir, adr_dir, tmp_path / "tasks.md")

        assert result.passed is True
        assert result.name == "required_files"
        assert "present" in result.message.lower()

    def test_missing_spec(self, tmp_path):
        """Fail when spec.md is missing."""
        spec_dir = tmp_path / "docs" / "prd"
        adr_dir = tmp_path / "docs" / "adr"
        spec_dir.mkdir(parents=True)
        adr_dir.mkdir(parents=True)

        (adr_dir / "plan.md").write_text("# Plan")
        (tmp_path / "tasks.md").write_text("# Tasks")

        result = check_required_files(spec_dir, adr_dir, tmp_path / "tasks.md")

        assert result.passed is False
        assert "spec.md" in str(result.details)

    def test_missing_plan(self, tmp_path):
        """Fail when plan.md is missing."""
        spec_dir = tmp_path / "docs" / "prd"
        adr_dir = tmp_path / "docs" / "adr"
        spec_dir.mkdir(parents=True)
        adr_dir.mkdir(parents=True)

        (spec_dir / "spec.md").write_text("# Spec")
        (tmp_path / "tasks.md").write_text("# Tasks")

        result = check_required_files(spec_dir, adr_dir, tmp_path / "tasks.md")

        assert result.passed is False
        assert "plan.md" in str(result.details)

    def test_missing_tasks(self, tmp_path):
        """Fail when tasks.md is missing."""
        spec_dir = tmp_path / "docs" / "prd"
        adr_dir = tmp_path / "docs" / "adr"
        spec_dir.mkdir(parents=True)
        adr_dir.mkdir(parents=True)

        (spec_dir / "spec.md").write_text("# Spec")
        (adr_dir / "plan.md").write_text("# Plan")

        result = check_required_files(spec_dir, adr_dir, tmp_path / "tasks.md")

        assert result.passed is False
        assert "tasks.md" in str(result.details)

    def test_all_files_missing(self, tmp_path):
        """Fail with all details when no files exist."""
        spec_dir = tmp_path / "docs" / "prd"
        adr_dir = tmp_path / "docs" / "adr"
        spec_dir.mkdir(parents=True)
        adr_dir.mkdir(parents=True)

        result = check_required_files(spec_dir, adr_dir, tmp_path / "tasks.md")

        assert result.passed is False
        assert len(result.details) == 3


class TestSpecCompletenessGate:
    """Test Gate 2: Spec completeness check."""

    def test_clean_spec(self, tmp_path):
        """Pass when spec has no markers."""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(
            """# Feature Specification

## Overview
This is a complete specification.

## Requirements
- Requirement 1
- Requirement 2
"""
        )

        result = check_spec_completeness(spec_file)

        assert result.passed is True
        assert "no unresolved markers" in result.message.lower()

    def test_tbd_marker(self, tmp_path):
        """Fail when spec contains [TBD]."""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(
            """# Feature Specification

## Overview
[TBD] - Need to define this later.
"""
        )

        result = check_spec_completeness(spec_file)

        assert result.passed is False
        assert "1 unresolved" in result.message

    def test_todo_marker(self, tmp_path):
        """Fail when spec contains [TODO]."""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(
            """# Feature Specification

## Overview
[TODO] Add details here.
"""
        )

        result = check_spec_completeness(spec_file)

        assert result.passed is False

    def test_needs_clarification_marker(self, tmp_path):
        """Fail when spec contains NEEDS CLARIFICATION."""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(
            """# Feature Specification

## Overview
This section NEEDS CLARIFICATION from stakeholders.
"""
        )

        result = check_spec_completeness(spec_file)

        assert result.passed is False

    def test_question_marks_marker(self, tmp_path):
        """Fail when spec contains ???."""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(
            """# Feature Specification

## Overview
The timeout should be ??? seconds.
"""
        )

        result = check_spec_completeness(spec_file)

        assert result.passed is False

    def test_placeholder_marker(self, tmp_path):
        """Fail when spec contains PLACEHOLDER."""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(
            """# Feature Specification

## Overview
PLACEHOLDER for detailed requirements.
"""
        )

        result = check_spec_completeness(spec_file)

        assert result.passed is False

    def test_insert_marker(self, tmp_path):
        """Fail when spec contains <insert>."""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(
            """# Feature Specification

## Overview
<insert> description here.
"""
        )

        result = check_spec_completeness(spec_file)

        assert result.passed is False

    def test_multiple_markers(self, tmp_path):
        """Report multiple markers found."""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(
            """# Feature Specification

[TBD] First issue
[TODO] Second issue
??? Third issue
"""
        )

        result = check_spec_completeness(spec_file)

        assert result.passed is False
        assert "3 unresolved" in result.message

    def test_empty_spec(self, tmp_path):
        """Fail when spec is empty."""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text("")

        result = check_spec_completeness(spec_file)

        assert result.passed is False
        assert "empty" in result.message.lower()

    def test_missing_spec(self, tmp_path):
        """Fail when spec file doesn't exist."""
        spec_file = tmp_path / "nonexistent.md"

        result = check_spec_completeness(spec_file)

        assert result.passed is False
        assert "not found" in result.message.lower()


class TestConstitutionalComplianceGate:
    """Test Gate 3: Constitutional compliance check."""

    def test_fully_compliant_spec(self, tmp_path):
        """Pass when spec mentions all constitutional requirements."""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(
            """# Feature Specification

## Acceptance Criteria
- AC1: Feature works correctly
- AC2: Tests pass

## Testing
All changes require tests using pytest.

## Git Workflow
Use git commit -s for DCO sign-off on all commits.
"""
        )

        result = check_constitutional_compliance(spec_file)

        assert result.passed is True

    def test_missing_dco(self, tmp_path):
        """Fail when DCO/sign-off not mentioned."""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(
            """# Feature Specification

## Acceptance Criteria
- AC1: Feature works

## Testing
Run pytest for all tests.
"""
        )

        result = check_constitutional_compliance(spec_file)

        assert result.passed is False
        assert "DCO sign-off" in str(result.details)

    def test_missing_testing(self, tmp_path):
        """Fail when testing not mentioned."""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(
            """# Feature Specification

## Acceptance Criteria
- AC1: Feature works

## Git Workflow
Use DCO sign-off.
"""
        )

        result = check_constitutional_compliance(spec_file)

        assert result.passed is False
        assert "testing" in str(result.details).lower()

    def test_missing_acceptance_criteria(self, tmp_path):
        """Fail when acceptance criteria not mentioned."""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(
            """# Feature Specification

## Testing
Run pytest.

## Git
Use DCO sign-off.
"""
        )

        result = check_constitutional_compliance(spec_file)

        assert result.passed is False
        assert "acceptance criteria" in str(result.details).lower()

    def test_missing_spec_file(self, tmp_path):
        """Fail when spec file doesn't exist."""
        spec_file = tmp_path / "nonexistent.md"

        result = check_constitutional_compliance(spec_file)

        assert result.passed is False


class TestQualityScoreCalculation:
    """Test quality score calculation heuristics."""

    def test_minimal_spec_low_score(self):
        """Minimal content gets low score."""
        content = "# Spec\nShort."
        score = calculate_quality_score(content)
        assert score < 30

    def test_comprehensive_spec_high_score(self):
        """Comprehensive spec gets high score."""
        content = """# Feature Specification

## Overview
This is a comprehensive specification document that describes the feature
in detail with all necessary requirements clearly stated.

## Requirements
The system must handle the following:
- Requirement 1: User authentication with 30 second timeout
- Requirement 2: Data validation must pass 100% of test cases
- Requirement 3: Response time shall be under 500ms
- Requirement 4: System should support 1000 concurrent users
- Requirement 5: Error rate must be below 0.1%

## Technical Details
### Architecture
The system will use a microservices architecture.

### API Endpoints
- POST /api/v1/users - Create user
- GET /api/v1/users/{id} - Get user
- PUT /api/v1/users/{id} - Update user
- DELETE /api/v1/users/{id} - Delete user

### Data Model
The data model shall include:
- User table with 10 fields
- Session table with 5 fields
- Audit log with timestamps

## Acceptance Criteria
- AC1: All endpoints return within 200ms
- AC2: Authentication tokens expire after 3600 seconds
- AC3: Input validation must reject malformed data

## Testing Requirements
- Unit tests must cover 80% of code
- Integration tests must cover all API endpoints
- Performance tests must validate 1000 concurrent connections
"""
        score = calculate_quality_score(content)
        assert score >= 70

    def test_score_capped_at_100(self):
        """Score never exceeds 100."""
        content = "# " + "Very long content " * 1000
        score = calculate_quality_score(content)
        assert score <= 100


class TestQualityRecommendations:
    """Test quality improvement recommendations."""

    def test_recommendations_for_short_content(self):
        """Recommend more detail for short specs."""
        content = "# Spec\nShort content here."
        recommendations = get_quality_recommendations(content, 70)
        assert any("detail" in r.lower() for r in recommendations)

    def test_recommendations_for_few_headings(self):
        """Recommend more sections for flat specs."""
        content = "# Single Heading\n" + "Some content. " * 50
        recommendations = get_quality_recommendations(content, 70)
        assert any("section" in r.lower() for r in recommendations)

    def test_recommendations_sorted_by_impact(self):
        """Recommendations should be sorted by potential impact."""
        content = "# Spec\nMinimal."
        recommendations = get_quality_recommendations(content, 70)
        # All recommendations should have potential points
        assert len(recommendations) > 0
        for rec in recommendations:
            assert "pts potential" in rec


class TestQualityThresholdGate:
    """Test Gate 4: Quality threshold check."""

    def test_passes_light_threshold(self, tmp_path):
        """Pass when score meets light threshold."""
        spec_file = tmp_path / "spec.md"
        # Content designed to score >= 50 (light threshold)
        spec_file.write_text(
            """# Feature Specification

## Overview
This feature must handle user requests efficiently. The system shall process
incoming data and return responses within specified time limits. All error
conditions must be handled gracefully with appropriate logging.

## Requirements
- The system shall process 100 requests per second minimum throughput
- Response time should be under 200ms for 95th percentile
- Error handling must be comprehensive with retry logic
- Data validation must reject malformed inputs within 50ms
- Concurrent connections shall support 500 simultaneous users
- Memory usage should stay under 512MB during peak load

## Design Principles
The design will use standard patterns including dependency injection
and separation of concerns. Components must be loosely coupled.

## Implementation Notes
All changes require unit tests with 80% coverage minimum.
"""
        )

        result = check_quality_threshold(spec_file, TIER_THRESHOLDS["light"])

        assert result.passed is True

    def test_fails_heavy_threshold(self, tmp_path):
        """Fail when score doesn't meet heavy threshold."""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text("# Spec\nMinimal content.")

        result = check_quality_threshold(spec_file, TIER_THRESHOLDS["heavy"])

        assert result.passed is False
        assert "85" in result.message  # Heavy threshold

    def test_missing_spec_file(self, tmp_path):
        """Fail when spec file doesn't exist."""
        spec_file = tmp_path / "nonexistent.md"

        result = check_quality_threshold(spec_file, 70)

        assert result.passed is False


class TestRunQualityGates:
    """Test integrated quality gates runner."""

    def test_all_gates_pass(self, tmp_path):
        """All gates pass with proper setup."""
        # Create directory structure
        spec_dir = tmp_path / "docs" / "prd"
        adr_dir = tmp_path / "docs" / "adr"
        spec_dir.mkdir(parents=True)
        adr_dir.mkdir(parents=True)

        # Create files with compliant content that scores >= 50 (light threshold)
        (spec_dir / "spec.md").write_text(
            """# Feature Specification

## Overview
This feature must be implemented according to specifications. The system
shall handle all user requests within specified performance bounds. All
error conditions must be handled gracefully with proper logging.

## Acceptance Criteria
- AC1: Feature must work correctly under 100 concurrent users
- AC2: All tests must pass with 80% coverage minimum
- AC3: Response time shall be under 500ms for 95th percentile
- AC4: Memory usage should stay under 256MB during operation
- AC5: Error rate must be below 0.1% under normal load

## Testing Requirements
All changes require comprehensive testing with pytest. Unit tests
must cover all new code paths and integration tests must verify
end-to-end functionality.

## Git Workflow
All commits require DCO sign-off using git commit -s. Pull requests
must pass CI before merging.

## Requirements
- The system shall handle 100 requests per second
- Response time should be under 500ms
- The system must support 50 concurrent users
- Data validation must reject invalid inputs
- Logging must capture all errors with context
"""
        )
        (adr_dir / "plan.md").write_text("# Implementation Plan")
        (tmp_path / "tasks.md").write_text("# Tasks")

        report = run_quality_gates(
            project_root=tmp_path,
            tier="light",
        )

        assert report.passed is True
        assert len(report.gates) == 4
        assert all(g.passed for g in report.gates)

    def test_some_gates_fail(self, tmp_path):
        """Report fails when any gate fails."""
        # Create only partial structure
        spec_dir = tmp_path / "docs" / "prd"
        adr_dir = tmp_path / "docs" / "adr"
        spec_dir.mkdir(parents=True)
        adr_dir.mkdir(parents=True)

        # Missing plan.md and tasks.md
        (spec_dir / "spec.md").write_text("# Minimal Spec")

        report = run_quality_gates(project_root=tmp_path)

        assert report.passed is False
        failed_gates = [g for g in report.gates if not g.passed]
        assert len(failed_gates) > 0

    def test_tier_affects_threshold(self, tmp_path):
        """Different tiers use different thresholds."""
        spec_dir = tmp_path / "docs" / "prd"
        adr_dir = tmp_path / "docs" / "adr"
        spec_dir.mkdir(parents=True)
        adr_dir.mkdir(parents=True)

        # Create medium-quality spec
        (spec_dir / "spec.md").write_text(
            """# Feature Specification

## Overview
A moderately detailed specification with acceptance criteria.

## Acceptance Criteria
- AC1: Feature works
- AC2: Tests pass

## Testing
Use pytest for testing.

## Git Workflow
Use DCO sign-off on commits.
"""
        )
        (adr_dir / "plan.md").write_text("# Plan")
        (tmp_path / "tasks.md").write_text("# Tasks")

        # Light tier should pass
        light_report = run_quality_gates(project_root=tmp_path, tier="light")
        assert light_report.threshold == 50

        # Heavy tier may fail for same content
        heavy_report = run_quality_gates(project_root=tmp_path, tier="heavy")
        assert heavy_report.threshold == 85


class TestExitCodes:
    """Test exit code constants."""

    def test_exit_codes_defined(self):
        """Exit codes are properly defined."""
        assert EXIT_SUCCESS == 0
        assert EXIT_FAILURE == 1


class TestAmbiguityMarkers:
    """Test ambiguity marker patterns."""

    def test_marker_patterns_defined(self):
        """All expected markers are defined."""
        assert len(AMBIGUITY_MARKERS) >= 6

    def test_markers_are_regex_patterns(self):
        """Markers are valid regex patterns."""
        import re

        for marker in AMBIGUITY_MARKERS:
            # Should not raise
            re.compile(marker, re.IGNORECASE)
