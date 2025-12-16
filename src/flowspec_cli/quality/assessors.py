"""Individual assessment functions for spec quality dimensions."""

import re
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class AssessmentResult:
    """Result of a single quality assessment dimension."""

    score: float  # 0-100
    findings: List[str]
    details: Dict[str, Any] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}


def assess_completeness(
    spec_content: str, required_sections: List[str]
) -> AssessmentResult:
    """
    Assess completeness based on presence of required sections.

    Args:
        spec_content: The specification file content
        required_sections: List of required section headers

    Returns:
        AssessmentResult with score 0-100 and findings
    """
    findings = []
    missing_sections = []

    for section in required_sections:
        # Look for section header (case-insensitive, allowing for markdown variations)
        pattern = re.escape(section).replace(r"\#", r"#*")
        if not re.search(pattern, spec_content, re.IGNORECASE | re.MULTILINE):
            missing_sections.append(section)

    # Score: 100 if all present, proportional reduction for missing
    if not required_sections:
        score = 100.0
    else:
        found_count = len(required_sections) - len(missing_sections)
        score = (found_count / len(required_sections)) * 100

    if missing_sections:
        findings.append(
            f"Missing {len(missing_sections)} section(s): {', '.join(missing_sections)}"
        )
    else:
        findings.append("All required sections present")

    return AssessmentResult(
        score=score, findings=findings, details={"missing_sections": missing_sections}
    )


def assess_clarity(spec_content: str, vague_terms: List[str]) -> AssessmentResult:
    """
    Assess clarity by detecting vague terms and passive voice.

    Args:
        spec_content: The specification file content
        vague_terms: List of vague terms to detect

    Returns:
        AssessmentResult with score 0-100 and findings
    """
    findings = []
    issues = []

    # Count vague terms (case-insensitive, whole word matches)
    vague_count = 0
    vague_locations = []
    for term in vague_terms:
        pattern = r"\b" + re.escape(term) + r"\b"
        matches = list(re.finditer(pattern, spec_content, re.IGNORECASE))
        if matches:
            vague_count += len(matches)
            # Find line numbers
            for match in matches:
                line_num = spec_content[: match.start()].count("\n") + 1
                vague_locations.append(f"'{term}' on line {line_num}")

    # Detect passive voice patterns (simplified heuristic)
    passive_patterns = [
        r"\b(is|are|was|were|be|been|being)\s+\w+ed\b",
        r"\b(is|are|was|were|be|been|being)\s+\w+en\b",
    ]
    passive_count = 0
    for pattern in passive_patterns:
        passive_count += len(re.findall(pattern, spec_content, re.IGNORECASE))

    # Scoring: Start at 100, deduct for issues
    score = 100.0

    # Deduct for vague terms (up to -40 points)
    if vague_count > 0:
        vague_penalty = min(vague_count * 5, 40)
        score -= vague_penalty
        findings.append(f"{vague_count} vague term(s) found")
        issues.extend(vague_locations[:5])  # Show first 5
        if len(vague_locations) > 5:
            issues.append(f"... and {len(vague_locations) - 5} more")

    # Deduct for passive voice (up to -30 points)
    if passive_count > 0:
        passive_penalty = min(passive_count * 3, 30)
        score -= passive_penalty
        findings.append(f"{passive_count} potential passive voice pattern(s)")

    # Check for measurable criteria (bonus points)
    # Look for numbers, percentages, specific values
    measurable_patterns = [
        r"\b\d+%",  # percentages
        r"\b\d+\s*(ms|seconds?|sec|minutes?|min|hours?|hour|days?|day|MB|GB|KB)\b",  # units
        r"\b\d+\s*(users?|requests?|transactions?|records?)\b",  # countable items
    ]
    measurable_count = sum(
        len(re.findall(p, spec_content)) for p in measurable_patterns
    )
    if measurable_count >= 3:
        findings.append(
            f"Good use of measurable criteria ({measurable_count} instances)"
        )
        score = min(score + 5, 100)  # Small bonus

    score = max(0, min(100, score))

    if not findings:
        findings.append("No clarity issues detected")

    return AssessmentResult(
        score=score,
        findings=findings,
        details={
            "vague_count": vague_count,
            "passive_count": passive_count,
            "measurable_count": measurable_count,
            "issues": issues,
        },
    )


def assess_traceability(
    spec_path: Path, spec_content: str, plan_path: Path = None, tasks_path: Path = None
) -> AssessmentResult:
    """
    Assess traceability between spec, plan, and tasks.

    Args:
        spec_path: Path to the spec file
        spec_content: The specification content
        plan_path: Path to the plan file (optional)
        tasks_path: Path to the tasks file (optional)

    Returns:
        AssessmentResult with score 0-100 and findings
    """
    findings = []
    score = 100.0

    # Auto-detect plan and tasks if not provided
    if spec_path:
        spec_dir = spec_path.parent
        if plan_path is None:
            plan_path = spec_dir / "plan.md"
        if tasks_path is None:
            tasks_path = spec_dir / "tasks.md"

    # Check if plan exists
    plan_exists = plan_path and plan_path.exists()
    tasks_exist = tasks_path and tasks_path.exists()

    # Extract acceptance criteria from spec
    ac_pattern = r"(?:##\s*Acceptance Criteria|AC\s*\d+)(.*?)(?=##|\Z)"
    ac_matches = re.findall(ac_pattern, spec_content, re.DOTALL | re.IGNORECASE)
    has_acceptance_criteria = len(ac_matches) > 0

    if not plan_exists and not tasks_exist:
        findings.append("No plan.md or tasks.md found for traceability check")
        return AssessmentResult(
            score=80.0,  # Partial score - not necessarily bad
            findings=findings,
            details={
                "plan_exists": False,
                "tasks_exist": False,
                "has_acceptance_criteria": has_acceptance_criteria,
                "plan_references_spec": False,
                "tasks_reference_artifacts": False,
            },
        )

    # Check plan references spec
    plan_references_spec = False
    if plan_exists:
        plan_content = plan_path.read_text()
        # Look for references to acceptance criteria, user story, or spec
        if re.search(
            r"(acceptance criteria|user story|spec|requirement)",
            plan_content,
            re.IGNORECASE,
        ):
            plan_references_spec = True
            findings.append("Plan references specification")
        else:
            findings.append("Plan does not clearly reference spec")
            score -= 20

    # Check tasks reference plan or spec
    tasks_reference_artifacts = False
    if tasks_exist:
        tasks_content = tasks_path.read_text()
        # Look for task structure with acceptance criteria
        if re.search(
            r"(acceptance criteria|AC\s*#|\[ \])", tasks_content, re.IGNORECASE
        ):
            tasks_reference_artifacts = True
            findings.append("Tasks include acceptance criteria")
        else:
            findings.append("Tasks lack clear acceptance criteria linkage")
            score -= 20

    # Bonus: Check for explicit IDs or references
    if tasks_exist:
        tasks_content = tasks_path.read_text()
        if re.search(r"(task-\d+|#\d+|T\d+)", tasks_content, re.IGNORECASE):
            findings.append("Tasks have explicit IDs")

    if has_acceptance_criteria and (plan_references_spec or tasks_reference_artifacts):
        findings.append("Good traceability chain")
    elif not has_acceptance_criteria:
        findings.append("Spec lacks clear acceptance criteria")
        score -= 30

    score = max(0, min(100, score))

    return AssessmentResult(
        score=score,
        findings=findings,
        details={
            "plan_exists": plan_exists,
            "tasks_exist": tasks_exist,
            "has_acceptance_criteria": has_acceptance_criteria,
            "plan_references_spec": plan_references_spec,
            "tasks_reference_artifacts": tasks_reference_artifacts,
        },
    )


def assess_constitutional_compliance(
    spec_content: str, constitutional_patterns: List[str]
) -> AssessmentResult:
    """
    Assess constitutional compliance by checking for required tools/patterns.

    Args:
        spec_content: The specification content
        constitutional_patterns: List of required tool/pattern mentions

    Returns:
        AssessmentResult with score 0-100 and findings
    """
    findings = []
    found_patterns = []
    missing_patterns = []

    for pattern in constitutional_patterns:
        # Case-insensitive search for tool mentions
        if re.search(r"\b" + re.escape(pattern) + r"\b", spec_content, re.IGNORECASE):
            found_patterns.append(pattern)
        else:
            missing_patterns.append(pattern)

    # Score based on percentage of required patterns found
    if constitutional_patterns:
        score = (len(found_patterns) / len(constitutional_patterns)) * 100
    else:
        score = 100.0

    if found_patterns:
        findings.append(
            f"Uses {len(found_patterns)} required tool(s): {', '.join(found_patterns)}"
        )

    if missing_patterns:
        findings.append(
            f"Missing {len(missing_patterns)} tool mention(s): {', '.join(missing_patterns)}"
        )

    # Check for DCO sign-off mention
    if re.search(r"(DCO|sign-off|git commit -s)", spec_content, re.IGNORECASE):
        findings.append("Includes DCO sign-off requirement")
        score = min(score + 5, 100)

    return AssessmentResult(
        score=score,
        findings=findings,
        details={
            "found_patterns": found_patterns,
            "missing_patterns": missing_patterns,
        },
    )


def assess_ambiguity(
    spec_content: str, ambiguity_markers: List[str]
) -> AssessmentResult:
    """
    Assess ambiguity by detecting uncertainty markers.

    Args:
        spec_content: The specification content
        ambiguity_markers: List of ambiguity markers to detect

    Returns:
        AssessmentResult with score 0-100 and findings
    """
    findings = []
    marker_locations = []

    for marker in ambiguity_markers:
        # Case-insensitive search
        pattern = re.escape(marker)
        matches = list(re.finditer(pattern, spec_content, re.IGNORECASE))
        if matches:
            for match in matches:
                line_num = spec_content[: match.start()].count("\n") + 1
                marker_locations.append(f"'{marker}' on line {line_num}")

    # Score: Start at 100, deduct for each marker
    total_markers = len(marker_locations)
    if total_markers == 0:
        score = 100.0
        findings.append("No ambiguity markers detected")
    else:
        # Each marker reduces score by 10 points, minimum 0
        score = max(0, 100 - (total_markers * 10))
        findings.append(f"{total_markers} ambiguity marker(s) found")
        findings.extend(marker_locations[:5])  # Show first 5
        if len(marker_locations) > 5:
            findings.append(f"... and {len(marker_locations) - 5} more")

    return AssessmentResult(
        score=score,
        findings=findings,
        details={"marker_count": total_markers, "markers": marker_locations},
    )
