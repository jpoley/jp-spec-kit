"""Acceptance Criteria test coverage tracking.

This module provides tools to ensure all PRD acceptance criteria have corresponding tests:
- PRDScanner: Extract acceptance criteria from PRD markdown
- TestScanner: Find @pytest.mark.ac markers in test files
- ACCoverageReport: Generate ac-coverage.json manifest

The coverage report blocks workflow transitions if any ACs are uncovered.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class AcceptanceCriterion:
    """A single acceptance criterion from the PRD.

    Attributes:
        id: AC identifier (e.g., "AC1", "AC2").
        description: Full text description of the AC.
        user_story: Associated user story ID (e.g., "US1").
        tests: List of test paths that cover this AC.
        status: "covered" if tests exist, "uncovered" otherwise.
    """

    id: str
    description: str
    user_story: str = ""
    tests: list[str] = field(default_factory=list)
    status: str = "uncovered"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "description": self.description,
            "user_story": self.user_story,
            "tests": self.tests,
            "status": self.status,
        }


@dataclass
class CoverageSummary:
    """Summary statistics for AC coverage.

    Attributes:
        total_acs: Total number of acceptance criteria.
        covered: Number of ACs with tests.
        uncovered: Number of ACs without tests.
        coverage_percent: Percentage of ACs covered (0-100).
    """

    total_acs: int
    covered: int
    uncovered: int
    coverage_percent: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_acs": self.total_acs,
            "covered": self.covered,
            "uncovered": self.uncovered,
            "coverage_percent": self.coverage_percent,
        }


class PRDScanner:
    """Scanner to extract acceptance criteria from PRD markdown files.

    The scanner looks for sections titled "Acceptance Criteria" and extracts
    items in the format:
    - AC1: Description text
    - AC2: Another description

    Can also extract from markdown checklists:
    - [ ] AC1: Description
    - [x] AC2: Completed description
    """

    # Regex patterns for AC extraction
    AC_PATTERNS = [
        # Format: - AC1: Description
        re.compile(
            r"^[-*]\s+(?:\[[ x]\]\s+)?(?:#\d+\s+)?(AC\d+):\s+(.+)$", re.MULTILINE
        ),
        # Format: AC1: Description (without leading dash)
        re.compile(r"^(AC\d+):\s+(.+)$", re.MULTILINE),
    ]

    # Pattern to find user story associations (e.g., "User Story: US1")
    USER_STORY_PATTERN = re.compile(r"User Story:\s*(US\d+)", re.IGNORECASE)

    def __init__(self, prd_path: Path):
        """Initialize PRD scanner.

        Args:
            prd_path: Path to PRD markdown file.
        """
        self.prd_path = prd_path
        self._content = ""
        self._acs: list[AcceptanceCriterion] = []

    def scan(self) -> list[AcceptanceCriterion]:
        """Scan PRD and extract all acceptance criteria.

        Returns:
            List of AcceptanceCriterion objects.

        Raises:
            FileNotFoundError: If PRD file doesn't exist.
        """
        if not self.prd_path.exists():
            raise FileNotFoundError(f"PRD not found: {self.prd_path}")

        self._content = self.prd_path.read_text(encoding="utf-8")
        self._acs = []

        # Extract ACs using all patterns
        for pattern in self.AC_PATTERNS:
            for match in pattern.finditer(self._content):
                ac_id = match.group(1)
                description = match.group(2).strip()

                # Skip if we already have this AC (avoid duplicates)
                if any(ac.id == ac_id for ac in self._acs):
                    continue

                # Try to find associated user story
                user_story = self._find_user_story(ac_id)

                ac = AcceptanceCriterion(
                    id=ac_id,
                    description=description,
                    user_story=user_story,
                )
                self._acs.append(ac)

        # Sort ACs by ID
        self._acs.sort(key=lambda ac: int(ac.id[2:]))  # Sort by numeric part

        return self._acs

    def _find_user_story(self, ac_id: str) -> str:
        """Find user story associated with an AC.

        Args:
            ac_id: AC identifier to search for.

        Returns:
            User story ID (e.g., "US1") or empty string.
        """
        # Look for "User Story: US1" near the AC definition
        # This is a simple heuristic - could be improved
        ac_index = self._content.find(ac_id)
        if ac_index == -1:
            return ""

        # Search in the surrounding context (500 chars before/after)
        context_start = max(0, ac_index - 500)
        context_end = min(len(self._content), ac_index + 500)
        context = self._content[context_start:context_end]

        match = self.USER_STORY_PATTERN.search(context)
        if match:
            return match.group(1)

        return ""


class ACTestScanner:
    """Scanner to find AC markers in test files.

    Supports multiple testing frameworks:
    - Python: @pytest.mark.ac("AC1: Description")
    - TypeScript: // @ac AC1: Description
    - Go: // AC1: Description (in test comments)
    """

    # Regex patterns for test markers by language
    MARKER_PATTERNS = {
        "python": [
            # @pytest.mark.ac("AC1: Description")
            re.compile(r'@pytest\.mark\.ac\("(AC\d+).*?"\)', re.MULTILINE),
            # @pytest.mark.ac('AC1')
            re.compile(r"@pytest\.mark\.ac\('(AC\d+).*?'\)", re.MULTILINE),
        ],
        "typescript": [
            # // @ac AC1: Description
            re.compile(r"//\s*@ac\s+(AC\d+)", re.MULTILINE),
        ],
        "go": [
            # // AC1: Description
            re.compile(r"//\s*(AC\d+):", re.MULTILINE),
        ],
    }

    def __init__(self, test_dirs: list[Path]):
        """Initialize test scanner.

        Args:
            test_dirs: List of directories to scan for test files.
        """
        self.test_dirs = test_dirs
        self._ac_to_tests: dict[str, list[str]] = {}

    def scan(self) -> dict[str, list[str]]:
        """Scan test files and find AC markers.

        Returns:
            Dictionary mapping AC IDs to list of test file paths.
        """
        self._ac_to_tests = {}

        for test_dir in self.test_dirs:
            if not test_dir.exists():
                continue

            # Scan Python test files
            for test_file in test_dir.rglob("test_*.py"):
                self._scan_file(test_file, "python")
            for test_file in test_dir.rglob("*_test.py"):
                self._scan_file(test_file, "python")

            # Scan TypeScript test files
            for test_file in test_dir.rglob("*.test.ts"):
                self._scan_file(test_file, "typescript")
            for test_file in test_dir.rglob("*.spec.ts"):
                self._scan_file(test_file, "typescript")

            # Scan Go test files
            for test_file in test_dir.rglob("*_test.go"):
                self._scan_file(test_file, "go")

        return self._ac_to_tests

    def _scan_file(self, test_file: Path, language: str) -> None:
        """Scan a single test file for AC markers.

        Args:
            test_file: Path to test file.
            language: Programming language (python, typescript, go).
        """
        try:
            content = test_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return

        patterns = self.MARKER_PATTERNS.get(language, [])
        for pattern in patterns:
            for match in pattern.finditer(content):
                ac_id = match.group(1)

                # Store relative path from project root
                test_path = str(test_file)

                if ac_id not in self._ac_to_tests:
                    self._ac_to_tests[ac_id] = []

                if test_path not in self._ac_to_tests[ac_id]:
                    self._ac_to_tests[ac_id].append(test_path)


@dataclass
class ACCoverageReport:
    """AC coverage report with validation logic.

    Attributes:
        feature: Feature name slug.
        prd_path: Path to PRD file.
        acceptance_criteria: List of AcceptanceCriterion objects.
        summary: CoverageSummary statistics.
        generated_at: ISO-8601 timestamp of report generation.
    """

    feature: str
    prd_path: str
    acceptance_criteria: list[AcceptanceCriterion]
    summary: CoverageSummary
    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "feature": self.feature,
            "prd_path": self.prd_path,
            "generated_at": self.generated_at,
            "acceptance_criteria": [ac.to_dict() for ac in self.acceptance_criteria],
            "summary": self.summary.to_dict(),
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string.

        Args:
            indent: Number of spaces for indentation.

        Returns:
            JSON string representation.
        """
        return json.dumps(self.to_dict(), indent=indent)

    def save(self, output_path: Path) -> None:
        """Save report to file.

        Args:
            output_path: Path to save JSON report.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.to_json(), encoding="utf-8")

    @classmethod
    def load(cls, report_path: Path) -> ACCoverageReport:
        """Load report from JSON file.

        Args:
            report_path: Path to JSON report file.

        Returns:
            ACCoverageReport instance.

        Raises:
            FileNotFoundError: If report file doesn't exist.
            ValueError: If JSON is invalid.
        """
        if not report_path.exists():
            raise FileNotFoundError(f"Report not found: {report_path}")

        try:
            data = json.loads(report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {report_path}: {e}") from e

        # Reconstruct AcceptanceCriterion objects
        acs = [
            AcceptanceCriterion(
                id=ac_data["id"],
                description=ac_data["description"],
                user_story=ac_data.get("user_story", ""),
                tests=ac_data.get("tests", []),
                status=ac_data.get("status", "uncovered"),
            )
            for ac_data in data.get("acceptance_criteria", [])
        ]

        # Reconstruct CoverageSummary
        summary_data = data.get("summary", {})
        summary = CoverageSummary(
            total_acs=summary_data.get("total_acs", 0),
            covered=summary_data.get("covered", 0),
            uncovered=summary_data.get("uncovered", 0),
            coverage_percent=summary_data.get("coverage_percent", 0.0),
        )

        return cls(
            feature=data.get("feature", ""),
            prd_path=data.get("prd_path", ""),
            acceptance_criteria=acs,
            summary=summary,
            generated_at=data.get("generated_at", ""),
        )

    def is_fully_covered(self) -> bool:
        """Check if all ACs are covered by tests.

        Returns:
            True if coverage is 100%, False otherwise.
        """
        return self.summary.coverage_percent >= 100.0

    def get_uncovered_acs(self) -> list[AcceptanceCriterion]:
        """Get list of uncovered acceptance criteria.

        Returns:
            List of AcceptanceCriterion objects with status "uncovered".
        """
        return [ac for ac in self.acceptance_criteria if ac.status == "uncovered"]


def generate_coverage_report(
    feature: str,
    prd_path: Path,
    test_dirs: list[Path],
) -> ACCoverageReport:
    """Generate AC coverage report for a feature.

    Args:
        feature: Feature name slug.
        prd_path: Path to PRD markdown file.
        test_dirs: List of test directories to scan.

    Returns:
        ACCoverageReport with coverage analysis.
    """
    # Scan PRD for acceptance criteria
    prd_scanner = PRDScanner(prd_path)
    acs = prd_scanner.scan()

    # Scan test files for AC markers
    test_scanner = ACTestScanner(test_dirs)
    ac_to_tests = test_scanner.scan()

    # Map tests to ACs
    for ac in acs:
        if ac.id in ac_to_tests:
            ac.tests = ac_to_tests[ac.id]
            ac.status = "covered"
        else:
            ac.status = "uncovered"

    # Calculate summary
    total_acs = len(acs)
    covered = sum(1 for ac in acs if ac.status == "covered")
    uncovered = total_acs - covered
    coverage_percent = (covered / total_acs * 100.0) if total_acs > 0 else 100.0

    summary = CoverageSummary(
        total_acs=total_acs,
        covered=covered,
        uncovered=uncovered,
        coverage_percent=coverage_percent,
    )

    return ACCoverageReport(
        feature=feature,
        prd_path=str(prd_path),
        acceptance_criteria=acs,
        summary=summary,
    )


def validate_ac_coverage(
    report: ACCoverageReport,
    allow_partial: bool = False,
) -> tuple[bool, str]:
    """Validate AC coverage meets requirements.

    Args:
        report: ACCoverageReport to validate.
        allow_partial: If True, allow partial coverage (for exceptional cases).

    Returns:
        Tuple of (is_valid, error_message).
        If valid, error_message is empty.
    """
    if allow_partial:
        return (True, "")

    if report.is_fully_covered():
        return (True, "")

    # Build error message with uncovered ACs
    uncovered = report.get_uncovered_acs()
    error_lines = [
        "AC coverage requirement not met:",
        f"Coverage: {report.summary.coverage_percent:.1f}% "
        f"({report.summary.covered}/{report.summary.total_acs})",
        "",
        "Uncovered acceptance criteria:",
    ]

    for ac in uncovered:
        error_lines.append(f"  - {ac.id}: {ac.description}")

    error_lines.extend(
        [
            "",
            "To fix:",
            '1. Add @pytest.mark.ac("ACX: Description") to your test functions',
            "2. Ensure test files are in ./tests/ or configured test directories",
            "3. Run: specify ac-coverage --check",
            "",
            "Or use --allow-partial-coverage flag if exceptional case",
        ]
    )

    return (False, "\n".join(error_lines))
