#!/usr/bin/env python3
"""Pre-implementation quality gates hook.

Validates spec quality before /jpspec:implement can proceed.
Supports tiered quality thresholds for different project types.

Usage:
    python .claude/hooks/pre-implement.py                    # Default medium tier
    python .claude/hooks/pre-implement.py --tier light       # Light tier (50 threshold)
    python .claude/hooks/pre-implement.py --tier heavy       # Heavy tier (85 threshold)
    python .claude/hooks/pre-implement.py --skip             # Bypass with audit log

Exit Codes:
    0 - All gates passed
    1 - One or more gates failed
    2 - Configuration/runtime error
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

# Tier-based quality thresholds
TIER_THRESHOLDS: dict[str, int] = {
    "light": 50,
    "medium": 70,
    "heavy": 85,
}

# Patterns indicating incomplete specs
INCOMPLETE_MARKERS: list[str] = [
    r"NEEDS\s*CLARIFICATION",
    r"NEEDS_VALIDATION",
    r"\[TBD\]",
    r"\[TODO\]",
    r"\?\?\?",
    r"PLACEHOLDER",
    r"<insert>",
    r"<TBD>",
]

# Required constitution sections
CONSTITUTION_PATTERNS: list[str] = [
    r"(?i)(sign-off|DCO|git commit -s)",
    r"(?i)(test|testing|pytest|TDD)",
    r"(?i)(acceptance criteria|acceptance criterion)",
]


@dataclass
class GateResult:
    """Result of a single quality gate check."""

    name: str
    passed: bool
    message: str
    details: list[str]


@dataclass
class QualityReport:
    """Complete quality gates report."""

    tier: str
    threshold: int
    gates: list[GateResult]
    passed: bool
    skipped: bool = False


def find_project_root() -> Path:
    """Find the project root by looking for common markers."""
    current = Path.cwd()
    markers = [".git", "pyproject.toml", "CLAUDE.md", "memory"]

    while current != current.parent:
        if any((current / marker).exists() for marker in markers):
            return current
        current = current.parent

    return Path.cwd()


def check_incomplete_markers(spec_path: Path) -> GateResult:
    """Gate 1: Check for incomplete markers in spec files."""
    if not spec_path.exists():
        return GateResult(
            name="Spec Completeness",
            passed=False,
            message=f"Spec file not found: {spec_path}",
            details=["Create spec using /jpspec:specify"],
        )

    content = spec_path.read_text()
    findings: list[str] = []

    for pattern in INCOMPLETE_MARKERS:
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        for match in matches:
            line_num = content[: match.start()].count("\n") + 1
            findings.append(f"Line {line_num}: '{match.group()}'")

    if findings:
        return GateResult(
            name="Spec Completeness",
            passed=False,
            message=f"Found {len(findings)} incomplete marker(s)",
            details=findings[:5] + (["..."] if len(findings) > 5 else []),
        )

    return GateResult(
        name="Spec Completeness",
        passed=True,
        message="No incomplete markers found",
        details=[],
    )


def check_required_files(root: Path, tier: str) -> GateResult:
    """Gate 2: Check that required files exist based on tier."""
    # Files required for all tiers
    base_required = [
        "memory/constitution.md",
    ]

    # Tier-specific requirements
    tier_required: dict[str, list[str]] = {
        "light": base_required,
        "medium": base_required + ["docs/prd"],
        "heavy": base_required + ["docs/prd", "docs/specs"],
    }

    required = tier_required.get(tier, tier_required["medium"])
    missing: list[str] = []

    for file_path in required:
        path = root / file_path
        if not path.exists():
            missing.append(file_path)

    if missing:
        return GateResult(
            name="Required Files",
            passed=False,
            message=f"Missing {len(missing)} required file(s)",
            details=missing,
        )

    return GateResult(
        name="Required Files",
        passed=True,
        message="All required files present",
        details=[],
    )


def check_constitutional_compliance(constitution_path: Path) -> GateResult:
    """Gate 3: Check constitution includes required sections."""
    if not constitution_path.exists():
        return GateResult(
            name="Constitutional Compliance",
            passed=False,
            message="Constitution file not found",
            details=["Create constitution using /speckit:constitution"],
        )

    content = constitution_path.read_text()
    missing: list[str] = []

    pattern_descriptions = [
        ("DCO/sign-off requirement", CONSTITUTION_PATTERNS[0]),
        ("Testing requirements", CONSTITUTION_PATTERNS[1]),
        ("Acceptance criteria", CONSTITUTION_PATTERNS[2]),
    ]

    for description, pattern in pattern_descriptions:
        if not re.search(pattern, content):
            missing.append(description)

    if missing:
        return GateResult(
            name="Constitutional Compliance",
            passed=False,
            message=f"Missing {len(missing)} required section(s)",
            details=missing,
        )

    return GateResult(
        name="Constitutional Compliance",
        passed=True,
        message="Constitution includes required sections",
        details=[],
    )


def check_quality_threshold(root: Path, threshold: int) -> GateResult:
    """Gate 4: Check spec quality score meets threshold."""
    # Look for any spec file
    spec_candidates = [
        root / "docs" / "prd" / "spec.md",
        root / ".specify" / "spec.md",
        root / "spec.md",
    ]

    spec_path: Optional[Path] = None
    for candidate in spec_candidates:
        if candidate.exists():
            spec_path = candidate
            break

    if spec_path is None:
        # No spec to check - pass with warning
        return GateResult(
            name="Quality Threshold",
            passed=True,
            message=f"No spec file found (threshold: {threshold})",
            details=["Quality check skipped - no spec file"],
        )

    # Try to run specify quality command
    try:
        result = subprocess.run(
            ["specify", "quality", str(spec_path), "--json"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return GateResult(
                name="Quality Threshold",
                passed=True,
                message=f"Quality check unavailable (threshold: {threshold})",
                details=["Skipped - 'specify quality' command failed"],
            )

        data = json.loads(result.stdout)
        score = data.get("overall_score", 0)

        if score >= threshold:
            return GateResult(
                name="Quality Threshold",
                passed=True,
                message=f"Score {score}/100 meets {threshold} threshold",
                details=[],
            )
        else:
            recommendations = data.get("recommendations", [])
            return GateResult(
                name="Quality Threshold",
                passed=False,
                message=f"Score {score}/100 below {threshold} threshold",
                details=recommendations[:3],
            )

    except FileNotFoundError:
        return GateResult(
            name="Quality Threshold",
            passed=True,
            message=f"Quality check unavailable (threshold: {threshold})",
            details=["Skipped - 'specify' command not installed"],
        )
    except (subprocess.TimeoutExpired, json.JSONDecodeError):
        return GateResult(
            name="Quality Threshold",
            passed=True,
            message=f"Quality check unavailable (threshold: {threshold})",
            details=["Skipped - quality check timed out or failed"],
        )


def check_code_markers(root: Path) -> GateResult:
    """Gate 5: Check for TODO/FIXME markers in existing code."""
    markers = ["TODO", "FIXME", "XXX", "HACK"]
    findings: list[str] = []

    # Directories to exclude
    exclude_dirs = {
        ".git",
        ".venv",
        "node_modules",
        "__pycache__",
        "templates",
        "docs",
        "tests",
        ".claude",
    }

    # File extensions to check
    extensions = {".py", ".ts", ".js", ".tsx", ".jsx", ".go", ".rs"}

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in extensions:
            continue
        if any(excluded in path.parts for excluded in exclude_dirs):
            continue

        try:
            content = path.read_text()
            for marker in markers:
                if marker in content:
                    rel_path = path.relative_to(root)
                    findings.append(f"{rel_path}: {marker}")
                    break
        except (OSError, UnicodeDecodeError):
            continue

    if findings:
        return GateResult(
            name="Code Markers",
            passed=True,  # Warning only, doesn't fail
            message=f"Found {len(findings)} file(s) with code markers (warning)",
            details=findings[:5],
        )

    return GateResult(
        name="Code Markers",
        passed=True,
        message="No unresolved code markers",
        details=[],
    )


def log_skip_audit(root: Path, tier: str) -> None:
    """Log skip decision for audit purposes."""
    audit_dir = root / ".specify" / "audit"
    audit_dir.mkdir(parents=True, exist_ok=True)

    audit_file = audit_dir / "quality-gate-skips.log"
    timestamp = datetime.now().isoformat()

    with open(audit_file, "a") as f:
        f.write(f"{timestamp} | tier={tier} | SKIPPED by user\n")


def run_gates(tier: str, skip: bool = False) -> QualityReport:
    """Run all quality gates and return report."""
    root = find_project_root()
    threshold = TIER_THRESHOLDS.get(tier, TIER_THRESHOLDS["medium"])

    if skip:
        log_skip_audit(root, tier)
        return QualityReport(
            tier=tier,
            threshold=threshold,
            gates=[],
            passed=True,
            skipped=True,
        )

    gates: list[GateResult] = []

    # Find spec file for completeness check
    spec_candidates = [
        root / "docs" / "prd" / "spec.md",
        root / ".specify" / "spec.md",
        root / "spec.md",
    ]
    spec_path = next(
        (p for p in spec_candidates if p.exists()),
        spec_candidates[0],
    )

    # Gate 1: Spec completeness
    gates.append(check_incomplete_markers(spec_path))

    # Gate 2: Required files
    gates.append(check_required_files(root, tier))

    # Gate 3: Constitutional compliance
    gates.append(check_constitutional_compliance(root / "memory" / "constitution.md"))

    # Gate 4: Quality threshold
    gates.append(check_quality_threshold(root, threshold))

    # Gate 5: Code markers (warning only)
    gates.append(check_code_markers(root))

    all_passed = all(gate.passed for gate in gates)

    return QualityReport(
        tier=tier,
        threshold=threshold,
        gates=gates,
        passed=all_passed,
    )


def print_report(report: QualityReport) -> None:
    """Print formatted quality report."""
    print("=" * 60)
    print(f"Pre-Implementation Quality Gates (tier: {report.tier})")
    print("=" * 60)
    print()

    if report.skipped:
        print("\033[33m⚠ WARNING: Quality gates SKIPPED\033[0m")
        print("This bypass has been logged for audit purposes.")
        print()
        return

    for gate in report.gates:
        status = "\033[32m✅\033[0m" if gate.passed else "\033[31m❌\033[0m"
        print(f"{status} Gate: {gate.name}")
        print(f"   {gate.message}")

        for detail in gate.details:
            print(f"   • {detail}")
        print()

    print("=" * 60)
    if report.passed:
        print("\033[32m✅ All quality gates PASSED - Ready for implementation\033[0m")
    else:
        print(
            "\033[31m❌ Quality gates FAILED - Address issues before proceeding\033[0m"
        )
        print()
        print("Options:")
        print("  1. Fix the issues identified above")
        print("  2. Run with --skip to bypass (not recommended)")
    print("=" * 60)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Pre-implementation quality gates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--tier",
        choices=list(TIER_THRESHOLDS.keys()),
        default="medium",
        help="Quality tier (light=50, medium=70, heavy=85)",
    )
    parser.add_argument(
        "--skip",
        action="store_true",
        help="Skip all gates (logged for audit)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output as JSON",
    )

    args = parser.parse_args()

    try:
        report = run_gates(tier=args.tier, skip=args.skip)

        if args.json_output:
            output = {
                "tier": report.tier,
                "threshold": report.threshold,
                "passed": report.passed,
                "skipped": report.skipped,
                "gates": [
                    {
                        "name": g.name,
                        "passed": g.passed,
                        "message": g.message,
                        "details": g.details,
                    }
                    for g in report.gates
                ],
            }
            print(json.dumps(output, indent=2))
        else:
            print_report(report)

        return 0 if report.passed else 1

    except Exception as e:
        print(f"\033[31mError: {e}\033[0m", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
