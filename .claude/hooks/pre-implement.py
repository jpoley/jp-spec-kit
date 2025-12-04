#!/usr/bin/env python3
"""Pre-implementation quality gates for SDD workflow.

Validates spec quality before /jpspec:implement proceeds.
Supports tiered thresholds: light (50), medium (70), heavy (85).
"""

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Tier quality thresholds
TIER_THRESHOLDS = {
    "light": 50,
    "medium": 70,
    "heavy": 85,
}

# Markers indicating incomplete specs
AMBIGUITY_MARKERS = [
    r"NEEDS?\s*CLARIFICATION",
    r"\[TBD\]",
    r"\[TODO\]",
    r"\?\?\?",
    r"PLACEHOLDER",
    r"<insert>",
]

# Exit codes
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_ERROR = 2


@dataclass
class GateResult:
    """Result of a single quality gate check."""

    name: str
    passed: bool
    message: str
    details: list[str] = field(default_factory=list)


@dataclass
class QualityReport:
    """Complete quality gates report."""

    passed: bool
    gates: list[GateResult]
    tier: str
    threshold: int
    skipped: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON output."""
        return {
            "passed": self.passed,
            "tier": self.tier,
            "threshold": self.threshold,
            "skipped": self.skipped,
            "gates": [
                {
                    "name": g.name,
                    "passed": g.passed,
                    "message": g.message,
                    "details": g.details,
                }
                for g in self.gates
            ],
        }


def check_required_files(
    spec_dir: Path,
    adr_dir: Path,
    tasks_file: Path,
) -> GateResult:
    """Gate 1: Validate required files exist.

    Required files:
    - spec.md in spec_dir
    - plan.md in adr_dir
    - tasks.md in project root
    """
    missing = []
    spec_file = spec_dir / "spec.md"
    plan_file = adr_dir / "plan.md"

    if not spec_file.exists():
        missing.append(f"Missing: {spec_file} - Create with /jpspec:specify")

    if not plan_file.exists():
        missing.append(f"Missing: {plan_file} - Create with /jpspec:plan")

    if not tasks_file.exists():
        missing.append(f"Missing: {tasks_file} - Create with /speckit:tasks")

    if missing:
        return GateResult(
            name="required_files",
            passed=False,
            message="Required files missing",
            details=missing,
        )

    return GateResult(
        name="required_files",
        passed=True,
        message="All required files present",
    )


def check_spec_completeness(spec_file: Path) -> GateResult:
    """Gate 2: Check spec has no unresolved markers.

    Markers like [TBD], [TODO], ???, NEEDS CLARIFICATION indicate
    incomplete specifications that shouldn't proceed to implementation.
    """
    if not spec_file.exists():
        return GateResult(
            name="spec_completeness",
            passed=False,
            message="spec.md not found",
            details=["Create spec using /jpspec:specify"],
        )

    content = spec_file.read_text()

    if not content.strip():
        return GateResult(
            name="spec_completeness",
            passed=False,
            message="spec.md is empty",
            details=["Create spec using /jpspec:specify"],
        )

    found_markers = []
    lines = content.split("\n")

    for i, line in enumerate(lines, 1):
        for marker_pattern in AMBIGUITY_MARKERS:
            if re.search(marker_pattern, line, re.IGNORECASE):
                truncated = line.strip()[:80]
                found_markers.append(f"Line {i}: {truncated}")
                break  # Only report once per line

    if found_markers:
        return GateResult(
            name="spec_completeness",
            passed=False,
            message=f"Found {len(found_markers)} unresolved marker(s)",
            details=found_markers + ["Resolve all markers before implementation"],
        )

    return GateResult(
        name="spec_completeness",
        passed=True,
        message="No unresolved markers found",
    )


def check_constitutional_compliance(spec_file: Path) -> GateResult:
    """Gate 3: Check spec follows constitutional requirements.

    Constitutional requirements:
    - DCO sign-off mention
    - Testing requirements
    - Acceptance criteria
    """
    if not spec_file.exists():
        return GateResult(
            name="constitutional_compliance",
            passed=False,
            message="spec.md not found",
            details=["Create spec using /jpspec:specify"],
        )

    content = spec_file.read_text().lower()
    violations = []

    # Check for DCO/sign-off mention
    dco_patterns = ["sign-off", "dco", "git commit -s"]
    if not any(p in content for p in dco_patterns):
        violations.append("Missing DCO sign-off requirement mention")

    # Check for testing mention
    test_patterns = ["test", "testing", "pytest", "tdd"]
    if not any(p in content for p in test_patterns):
        violations.append("No mention of testing requirements")

    # Check for acceptance criteria
    ac_patterns = ["acceptance criteria", "acceptance criterion"]
    if not any(p in content for p in ac_patterns):
        violations.append("No acceptance criteria defined")

    if violations:
        return GateResult(
            name="constitutional_compliance",
            passed=False,
            message=f"{len(violations)} constitutional violation(s)",
            details=violations
            + ["Ensure spec follows memory/constitution.md requirements"],
        )

    return GateResult(
        name="constitutional_compliance",
        passed=True,
        message="Constitutional compliance verified",
    )


def check_quality_threshold(
    spec_file: Path,
    threshold: int,
) -> GateResult:
    """Gate 4: Check spec quality score meets threshold.

    Uses simple heuristics if specify CLI unavailable.
    """
    if not spec_file.exists():
        return GateResult(
            name="quality_threshold",
            passed=False,
            message="spec.md not found",
            details=["Create spec using /jpspec:specify"],
        )

    content = spec_file.read_text()

    # Simple quality heuristics (0-100 scale)
    score = calculate_quality_score(content)

    if score >= threshold:
        return GateResult(
            name="quality_threshold",
            passed=True,
            message=f"Quality score: {score}/100 (threshold: {threshold})",
        )

    recommendations = get_quality_recommendations(content, score, threshold)
    return GateResult(
        name="quality_threshold",
        passed=False,
        message=f"Quality score: {score}/100 (threshold: {threshold})",
        details=recommendations + ["Improve spec quality using /speckit:clarify"],
    )


def calculate_quality_score(content: str) -> int:
    """Calculate quality score based on spec content heuristics.

    Scoring factors:
    - Word count (25 points max)
    - Section headings (25 points max)
    - Lists/structure (25 points max)
    - Specificity indicators (25 points max)
    """
    score = 0

    # Word count (25 points max)
    words = len(content.split())
    score += min(25, words // 40)  # 1 point per 40 words, max 25

    # Section headings (25 points max)
    headings = len(re.findall(r"^#+\s+", content, re.MULTILINE))
    score += min(25, headings * 5)  # 5 points per heading, max 25

    # Lists/structure (25 points max)
    list_items = len(re.findall(r"^\s*[-*]\s+", content, re.MULTILINE))
    score += min(25, list_items * 2)  # 2 points per item, max 25

    # Specificity indicators (25 points max)
    specificity_markers = [
        r"\d+",  # Numbers
        r"must\s+",  # Requirements language
        r"shall\s+",
        r"will\s+",
        r"should\s+",
    ]
    specificity_count = sum(
        len(re.findall(p, content, re.IGNORECASE)) for p in specificity_markers
    )
    score += min(25, specificity_count)

    return min(100, score)


def get_quality_recommendations(content: str, score: int, threshold: int) -> list[str]:
    """Generate recommendations to improve quality score, prioritized by estimated impact."""
    recommendations = []
    gap = threshold - score

    words = len(content.split())
    # Estimate how many more words are needed for max points
    word_points = min(25, words // 40)
    if word_points < 25:
        missing_words = max(0, (25 - word_points) * 40)
        est_points = 25 - word_points
        recommendations.append((est_points, f"Add more detail (current: {words} words, est. +{est_points} pts by adding ~{missing_words} words)"))

    headings = len(re.findall(r"^#+\s+", content, re.MULTILINE))
    heading_points = min(25, headings * 5)
    if heading_points < 25:
        missing_headings = max(0, (5 - headings))
        est_points = min(25 - heading_points, missing_headings * 5)
        recommendations.append((est_points, f"Add more sections (current: {headings} headings, est. +{est_points} pts by adding {missing_headings} headings)"))

    list_items = len(re.findall(r"^[\s]*[-*]\s+", content, re.MULTILINE))
    list_points = min(25, list_items * 2)
    if list_points < 25:
        missing_items = max(0, (10 - list_items))
        est_points = min(25 - list_points, missing_items * 2)
        recommendations.append((est_points, f"Add structured lists for requirements (current: {list_items} items, est. +{est_points} pts by adding {missing_items} items)"))

    specificity_markers = [
        r"\d+",  # Numbers
        r"must\s+",  # Requirements language
        r"shall\s+",
        r"will\s+",
        r"should\s+",
    ]
    specificity_count = sum(
        len(re.findall(p, content, re.IGNORECASE)) for p in specificity_markers
    )
    specificity_points = min(25, specificity_count)
    if specificity_points < 25:
        est_points = 25 - specificity_points
        recommendations.append((est_points, f"Increase specificity (current: {specificity_count} markers, est. +{est_points} pts by adding more requirements language/numbers)"))

    if gap > 20:
        recommendations.append((0, "Consider using /speckit:clarify for guided improvement"))

    # Sort recommendations by estimated points descending
    recommendations.sort(reverse=True, key=lambda x: x[0])
    # Return only the recommendation text
    return [rec for _, rec in recommendations]


def run_quality_gates(
    project_root: Optional[Path] = None,
    tier: str = "medium",
    spec_dir: Optional[Path] = None,
    adr_dir: Optional[Path] = None,
) -> QualityReport:
    """Run all quality gates and return comprehensive report.

    Args:
        project_root: Project root directory (default: current directory)
        tier: Quality tier (light, medium, heavy)
        spec_dir: Override spec directory
        adr_dir: Override ADR directory

    Returns:
        QualityReport with all gate results
    """
    if project_root is None:
        project_root = Path.cwd()

    if spec_dir is None:
        spec_dir = project_root / "docs" / "prd"

    if adr_dir is None:
        adr_dir = project_root / "docs" / "adr"

    tasks_file = project_root / "tasks.md"
    spec_file = spec_dir / "spec.md"

    threshold = TIER_THRESHOLDS.get(tier, TIER_THRESHOLDS["medium"])

    gates = [
        check_required_files(spec_dir, adr_dir, tasks_file),
        check_spec_completeness(spec_file),
        check_constitutional_compliance(spec_file),
        check_quality_threshold(spec_file, threshold),
    ]

    all_passed = all(g.passed for g in gates)

    return QualityReport(
        passed=all_passed,
        gates=gates,
        tier=tier,
        threshold=threshold,
    )


def print_report(report: QualityReport, use_json: bool = False) -> None:
    """Print quality report to stdout."""
    if use_json:
        print(json.dumps(report.to_dict(), indent=2))
        return

    # ANSI colors
    green = "\033[0;32m"
    red = "\033[0;31m"
    yellow = "\033[1;33m"
    reset = "\033[0m"

    if report.skipped:
        print(f"{yellow}⚠ WARNING: Quality gates bypassed{reset}")
        print("This may lead to unclear requirements and implementation issues.")
        return

    print(f"Running pre-implementation quality gates (tier: {report.tier})...")
    print()

    for gate in report.gates:
        status = f"{green}✓{reset}" if gate.passed else f"{red}✗{reset}"
        print(f"{status} {gate.name}: {gate.message}")

        if not gate.passed and gate.details:
            for detail in gate.details:
                print(f"    {detail}")

    print()
    print("=" * 50)

    if report.passed:
        print(f"{green}✅ All quality gates passed.{reset}")
    else:
        print(f"{red}❌ Quality gates failed.{reset}")
        print()
        print(
            f"{yellow}Run with --skip-quality-gates to bypass (NOT RECOMMENDED).{reset}"
        )


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Pre-implementation quality gates for SDD workflow"
    )
    parser.add_argument(
        "--tier",
        choices=["light", "medium", "heavy"],
        default="medium",
        help="Quality tier (light=50, medium=70, heavy=85)",
    )
    parser.add_argument(
        "--skip-quality-gates",
        action="store_true",
        help="Bypass all quality gates (NOT RECOMMENDED)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        help="Project root directory (default: current directory)",
    )

    args = parser.parse_args()

    if args.skip_quality_gates:
        report = QualityReport(
            passed=True,
            gates=[],
            tier=args.tier,
            threshold=TIER_THRESHOLDS[args.tier],
            skipped=True,
        )
        print_report(report, args.json)
        return EXIT_SUCCESS

    report = run_quality_gates(
        project_root=args.project_root,
        tier=args.tier,
    )
    print_report(report, args.json)

    return EXIT_SUCCESS if report.passed else EXIT_FAILURE


if __name__ == "__main__":
    sys.exit(main())
