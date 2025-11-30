"""Feature assessment and workflow recommendation engine.

This module provides functionality to assess feature complexity, risk, and architecture
impact to recommend the appropriate development workflow (Full SDD, Spec-Light, Skip SDD).

The assessment uses a three-dimensional scoring system:
1. Complexity: effort, component count, integration points
2. Risk: security, compliance, data sensitivity
3. Architecture Impact: new patterns, breaking changes, dependencies

Based on scores, the system recommends:
- Full SDD: High complexity/risk/impact features (score >= 7 in any category OR total >= 18)
- Spec-Light: Medium complexity features (score >= 4 in any category OR total >= 10)
- Skip SDD: Low complexity features (all other cases)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class WorkflowRecommendation(Enum):
    """Recommended workflow path based on assessment.

    Attributes:
        FULL_SDD: Full Spec-Driven Development workflow (high complexity/risk/impact)
        SPEC_LIGHT: Lightweight specification mode (medium complexity)
        SKIP_SDD: Skip specification, proceed to implementation (low complexity)
    """

    FULL_SDD = "Full SDD"
    SPEC_LIGHT = "Spec-Light"
    SKIP_SDD = "Skip SDD"


class Confidence(Enum):
    """Confidence level in the recommendation.

    Attributes:
        HIGH: Clear indicators support the recommendation
        MEDIUM: Some ambiguity in the assessment
        LOW: Significant uncertainty in the recommendation
    """

    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass
class DimensionScore:
    """Score for a single dimension of assessment.

    Attributes:
        name: Dimension name (e.g., "Effort Days", "Security Implications")
        score: Score value (1-10 scale)
        rationale: Explanation of the score
        max_score: Maximum possible score (default: 10)
    """

    name: str
    score: int
    rationale: str
    max_score: int = 10

    def __post_init__(self) -> None:
        """Validate dimension score."""
        if not 1 <= self.score <= self.max_score:
            raise ValueError(
                f"Score must be between 1 and {self.max_score}, got {self.score}"
            )
        if not self.name:
            raise ValueError("Dimension name cannot be empty")
        if not self.rationale:
            raise ValueError("Rationale cannot be empty")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary with dimension fields.
        """
        return {
            "name": self.name,
            "score": self.score,
            "rationale": self.rationale,
            "max_score": self.max_score,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DimensionScore:
        """Create DimensionScore from dictionary.

        Args:
            data: Dictionary with dimension fields.

        Returns:
            DimensionScore instance.
        """
        return cls(
            name=data["name"],
            score=data["score"],
            rationale=data["rationale"],
            max_score=data.get("max_score", 10),
        )


@dataclass
class CategoryScore:
    """Aggregate score for a category of assessment.

    Categories include:
    - Complexity: effort, components, integrations
    - Risk: security, compliance, data sensitivity
    - Architecture Impact: patterns, breaking changes, dependencies

    Attributes:
        category: Category name (e.g., "Complexity", "Risk")
        dimensions: List of individual dimension scores
        weight: Weighting factor for this category (default: 1.0)
    """

    category: str
    dimensions: list[DimensionScore] = field(default_factory=list)
    weight: float = 1.0

    def __post_init__(self) -> None:
        """Validate category score."""
        if not self.category:
            raise ValueError("Category name cannot be empty")
        if self.weight <= 0:
            raise ValueError(f"Weight must be positive, got {self.weight}")

    @property
    def average_score(self) -> float:
        """Calculate average score across all dimensions.

        Returns:
            Average score (0.0 if no dimensions).
        """
        if not self.dimensions:
            return 0.0
        return sum(d.score for d in self.dimensions) / len(self.dimensions)

    @property
    def weighted_score(self) -> float:
        """Calculate weighted average score.

        Returns:
            Weighted average score.
        """
        return self.average_score * self.weight

    @property
    def max_dimension_score(self) -> int:
        """Get the highest score among all dimensions.

        Returns:
            Maximum dimension score (0 if no dimensions).
        """
        if not self.dimensions:
            return 0
        return max(d.score for d in self.dimensions)

    def add_dimension(self, name: str, score: int, rationale: str) -> None:
        """Add a dimension score to this category.

        Args:
            name: Dimension name.
            score: Score value (1-10).
            rationale: Explanation of the score.
        """
        self.dimensions.append(
            DimensionScore(name=name, score=score, rationale=rationale)
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary with category fields.
        """
        return {
            "category": self.category,
            "dimensions": [d.to_dict() for d in self.dimensions],
            "average_score": round(self.average_score, 1),
            "weight": self.weight,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CategoryScore:
        """Create CategoryScore from dictionary.

        Args:
            data: Dictionary with category fields.

        Returns:
            CategoryScore instance.
        """
        return cls(
            category=data["category"],
            dimensions=[
                DimensionScore.from_dict(d) for d in data.get("dimensions", [])
            ],
            weight=data.get("weight", 1.0),
        )


@dataclass
class FeatureAssessment:
    """Complete assessment of a feature's complexity, risk, and impact.

    This class encapsulates all assessment data and provides methods to:
    - Calculate overall scores
    - Generate recommendations
    - Export assessment reports
    - Support override modes

    Attributes:
        feature_name: Name of the feature being assessed
        description: Brief description of the feature
        complexity: Complexity category scores
        risk: Risk category scores
        architecture_impact: Architecture impact category scores
        override_mode: Optional override for recommendation (full/light/skip)
        assessed_by: Name/identifier of assessor (default: "Claude AI Agent")
        assessed_at: Timestamp of assessment (auto-generated)
    """

    feature_name: str
    description: str = ""
    complexity: CategoryScore | None = None
    risk: CategoryScore | None = None
    architecture_impact: CategoryScore | None = None
    override_mode: str | None = None
    assessed_by: str = "Claude AI Agent"
    assessed_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate feature assessment."""
        if not self.feature_name:
            raise ValueError("Feature name cannot be empty")

        # Initialize categories if not provided
        if self.complexity is None:
            self.complexity = CategoryScore(category="Complexity")
        if self.risk is None:
            self.risk = CategoryScore(category="Risk")
        if self.architecture_impact is None:
            self.architecture_impact = CategoryScore(category="Architecture Impact")

    @property
    def total_score(self) -> float:
        """Calculate total score across all categories.

        Returns:
            Sum of all category average scores.
        """
        return (
            (self.complexity.average_score if self.complexity else 0.0)
            + (self.risk.average_score if self.risk else 0.0)
            + (
                self.architecture_impact.average_score
                if self.architecture_impact
                else 0.0
            )
        )

    @property
    def max_category_score(self) -> float:
        """Get the highest score among all categories.

        Returns:
            Maximum category average score.
        """
        scores = []
        if self.complexity:
            scores.append(self.complexity.average_score)
        if self.risk:
            scores.append(self.risk.average_score)
        if self.architecture_impact:
            scores.append(self.architecture_impact.average_score)

        return max(scores) if scores else 0.0

    def get_recommendation(self) -> tuple[WorkflowRecommendation, Confidence]:
        """Determine workflow recommendation based on scores.

        Logic:
        - If override_mode is set, return that recommendation with MEDIUM confidence
        - If any category score >= 7 OR total >= 18: Full SDD (HIGH confidence)
        - If any category score >= 4 OR total >= 10: Spec-Light (MEDIUM confidence)
        - Otherwise: Skip SDD (HIGH confidence)

        Returns:
            Tuple of (recommendation, confidence).
        """
        # Handle override mode
        if self.override_mode:
            override_map = {
                "full": WorkflowRecommendation.FULL_SDD,
                "light": WorkflowRecommendation.SPEC_LIGHT,
                "skip": WorkflowRecommendation.SKIP_SDD,
            }
            recommendation = override_map.get(
                self.override_mode.lower(), WorkflowRecommendation.FULL_SDD
            )
            return (recommendation, Confidence.MEDIUM)

        # Score-based recommendation
        max_score = self.max_category_score
        total = self.total_score

        if max_score >= 7 or total >= 18:
            return (WorkflowRecommendation.FULL_SDD, Confidence.HIGH)
        elif max_score >= 4 or total >= 10:
            return (WorkflowRecommendation.SPEC_LIGHT, Confidence.MEDIUM)
        else:
            return (WorkflowRecommendation.SKIP_SDD, Confidence.HIGH)

    def get_rationale(self) -> str:
        """Generate rationale for the recommendation.

        Returns:
            Detailed explanation of why this recommendation was made.
        """
        recommendation, confidence = self.get_recommendation()

        if self.override_mode:
            return (
                f"Recommendation overridden to {recommendation.value} mode. "
                f"Assessment scoring was bypassed per user request."
            )

        total = self.total_score
        max_score = self.max_category_score

        if recommendation == WorkflowRecommendation.FULL_SDD:
            reasons = []
            if max_score >= 7:
                reasons.append(
                    f"at least one category scored {max_score:.1f}/10 (threshold: 7)"
                )
            if total >= 18:
                reasons.append(f"total score is {total:.1f}/30 (threshold: 18)")

            return (
                f"This feature requires the full SDD workflow because {' and '.join(reasons)}. "
                f"High complexity, risk, or architectural impact demands comprehensive planning, "
                f"validation, and coordination across multiple phases."
            )

        elif recommendation == WorkflowRecommendation.SPEC_LIGHT:
            reasons = []
            if max_score >= 4:
                reasons.append(
                    f"at least one category scored {max_score:.1f}/10 (threshold: 4)"
                )
            if total >= 10:
                reasons.append(f"total score is {total:.1f}/30 (threshold: 10)")

            return (
                f"This feature benefits from lightweight specification because {' and '.join(reasons)}. "
                f"Moderate complexity warrants some planning and documentation, but full SDD workflow "
                f"would be excessive overhead."
            )

        else:  # SKIP_SDD
            return (
                f"This feature has low complexity (total: {total:.1f}/30, max category: {max_score:.1f}/10) "
                f"and can proceed directly to implementation. The overhead of specification would "
                f"slow delivery without meaningful benefits."
            )

    def get_next_steps(self) -> str:
        """Generate next step instructions based on recommendation.

        Returns:
            Specific commands or actions to take next.
        """
        recommendation, _ = self.get_recommendation()

        if recommendation == WorkflowRecommendation.FULL_SDD:
            return f"/jpspec:specify {self.feature_name}"

        elif recommendation == WorkflowRecommendation.SPEC_LIGHT:
            slug = self.feature_name.lower().replace(" ", "-")
            return (
                f"Create lightweight spec at ./docs/prd/{slug}-spec.md\n"
                f"Include: problem statement, key requirements, acceptance criteria\n"
                f"Then proceed to implementation"
            )

        else:  # SKIP_SDD
            return (
                "Proceed directly to implementation\n"
                "Document architectural decisions in ADRs as needed"
            )

    def to_dict(self) -> dict[str, Any]:
        """Convert assessment to dictionary representation.

        Returns:
            Dictionary with all assessment data.
        """
        recommendation, confidence = self.get_recommendation()

        return {
            "feature_name": self.feature_name,
            "description": self.description,
            "assessed_by": self.assessed_by,
            "assessed_at": self.assessed_at.isoformat(),
            "override_mode": self.override_mode,
            "complexity": self.complexity.to_dict() if self.complexity else None,
            "risk": self.risk.to_dict() if self.risk else None,
            "architecture_impact": (
                self.architecture_impact.to_dict() if self.architecture_impact else None
            ),
            "total_score": round(self.total_score, 1),
            "max_category_score": round(self.max_category_score, 1),
            "recommendation": recommendation.value,
            "confidence": confidence.value,
            "rationale": self.get_rationale(),
            "next_steps": self.get_next_steps(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FeatureAssessment:
        """Create FeatureAssessment from dictionary.

        Args:
            data: Dictionary with assessment data.

        Returns:
            FeatureAssessment instance.
        """
        return cls(
            feature_name=data["feature_name"],
            description=data.get("description", ""),
            complexity=(
                CategoryScore.from_dict(data["complexity"])
                if data.get("complexity")
                else None
            ),
            risk=CategoryScore.from_dict(data["risk"]) if data.get("risk") else None,
            architecture_impact=(
                CategoryScore.from_dict(data["architecture_impact"])
                if data.get("architecture_impact")
                else None
            ),
            override_mode=data.get("override_mode"),
            assessed_by=data.get("assessed_by", "Claude AI Agent"),
            assessed_at=(
                datetime.fromisoformat(data["assessed_at"])
                if "assessed_at" in data
                else datetime.now()
            ),
        )

    def generate_report_markdown(self) -> str:
        """Generate markdown assessment report.

        Returns:
            Formatted markdown report as string.
        """
        recommendation, confidence = self.get_recommendation()

        # Build markdown sections
        sections = [
            f"# Feature Assessment: {self.feature_name}",
            "",
            f"**Date**: {self.assessed_at.strftime('%Y-%m-%d')}",
            f"**Assessed By**: {self.assessed_by}",
            "**Status**: Assessed",
            "",
        ]

        # Feature Overview
        if self.description:
            sections.extend(
                [
                    "## Feature Overview",
                    "",
                    self.description,
                    "",
                ]
            )

        # Override notice
        if self.override_mode:
            sections.extend(
                [
                    "## Override Mode",
                    "",
                    f"**Note**: This assessment was run in override mode (`--mode {self.override_mode}`). ",
                    "Scoring analysis was bypassed and the recommendation was manually specified.",
                    "",
                ]
            )

        # Scoring sections (only if not override)
        if not self.override_mode:
            sections.append("## Scoring Analysis")
            sections.append("")

            # Add each category
            for category in [self.complexity, self.risk, self.architecture_impact]:
                if category and category.dimensions:
                    sections.extend(self._format_category_markdown(category))

        # Overall Assessment
        sections.extend(
            [
                "## Overall Assessment",
                "",
                f"**Total Score**: {self.total_score:.1f}/30",
                f"**Recommendation**: {recommendation.value}",
                f"**Confidence**: {confidence.value}",
                "",
                "### Rationale",
                "",
                self.get_rationale(),
                "",
            ]
        )

        # Key Factors (only if not override)
        if not self.override_mode:
            sections.extend(
                [
                    "### Key Factors",
                    "",
                ]
            )
            if self.complexity:
                sections.append(
                    f"- **Complexity**: {self.complexity.average_score:.1f}/10 - "
                    f"{self._summarize_category(self.complexity)}"
                )
            if self.risk:
                sections.append(
                    f"- **Risk**: {self.risk.average_score:.1f}/10 - "
                    f"{self._summarize_category(self.risk)}"
                )
            if self.architecture_impact:
                sections.append(
                    f"- **Architecture Impact**: {self.architecture_impact.average_score:.1f}/10 - "
                    f"{self._summarize_category(self.architecture_impact)}"
                )
            sections.append("")

        # Next Steps
        sections.extend(
            [
                "## Next Steps",
                "",
                self._format_next_steps(recommendation),
                "",
            ]
        )

        # Override instructions
        sections.extend(
            [
                "## Override",
                "",
                "If this assessment doesn't match your needs, you can override:",
                "",
                "```bash",
                "# Force full SDD workflow",
                f"/jpspec:assess {self.feature_name} --mode full",
                "",
                "# Force spec-light mode",
                f"/jpspec:assess {self.feature_name} --mode light",
                "",
                "# Force skip SDD",
                f"/jpspec:assess {self.feature_name} --mode skip",
                "```",
                "",
                "---",
                "",
                "*Assessment generated by /jpspec:assess workflow*",
            ]
        )

        return "\n".join(sections)

    def _format_category_markdown(self, category: CategoryScore) -> list[str]:
        """Format a category as markdown table.

        Args:
            category: Category to format.

        Returns:
            List of markdown lines.
        """
        lines = [
            f"### {category.category} Score: {category.average_score:.1f}/10",
            "",
            "| Dimension | Score | Rationale |",
            "|-----------|-------|-----------|",
        ]

        for dim in category.dimensions:
            lines.append(f"| {dim.name} | {dim.score}/10 | {dim.rationale} |")

        lines.extend(
            [
                f"| **Average** | **{category.average_score:.1f}/10** | |",
                "",
            ]
        )

        return lines

    def _summarize_category(self, category: CategoryScore) -> str:
        """Generate one-line summary of a category.

        Args:
            category: Category to summarize.

        Returns:
            Summary string.
        """
        if not category.dimensions:
            return "No dimensions assessed"

        avg = category.average_score
        if avg >= 7:
            return "High impact requiring full workflow"
        elif avg >= 4:
            return "Moderate impact warranting lightweight planning"
        else:
            return "Low impact allowing direct implementation"

    def _format_next_steps(self, recommendation: WorkflowRecommendation) -> str:
        """Format next steps section based on recommendation.

        Args:
            recommendation: Workflow recommendation.

        Returns:
            Formatted next steps markdown.
        """
        if recommendation == WorkflowRecommendation.FULL_SDD:
            return (
                f"### Full SDD Path\n```bash\n/jpspec:specify {self.feature_name}\n```"
            )
        elif recommendation == WorkflowRecommendation.SPEC_LIGHT:
            slug = self.feature_name.lower().replace(" ", "-")
            return (
                "### Spec-Light Path\n"
                "```bash\n"
                f"# Create lightweight spec in ./docs/prd/{slug}-spec.md\n"
                "# Include: problem statement, key requirements, acceptance criteria\n"
                "# Then proceed to implementation\n"
                "```"
            )
        else:  # SKIP_SDD
            return (
                "### Skip SDD Path\n"
                "```bash\n"
                "# Proceed directly to implementation\n"
                "# Document decisions in ADRs as needed\n"
                "```"
            )

    def save_report(self, output_dir: Path | str) -> Path:
        """Save assessment report to file.

        Args:
            output_dir: Directory to save report (typically ./docs/assess/)

        Returns:
            Path to saved report file.

        Raises:
            OSError: If directory creation or file writing fails.
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        slug = self.feature_name.lower().replace(" ", "-")
        report_file = output_path / f"{slug}-assessment.md"

        report_file.write_text(self.generate_report_markdown(), encoding="utf-8")

        return report_file


def create_complexity_assessment(
    effort_score: int,
    effort_rationale: str,
    component_score: int,
    component_rationale: str,
    integration_score: int,
    integration_rationale: str,
) -> CategoryScore:
    """Create complexity category assessment.

    Args:
        effort_score: Effort days score (1-10)
        effort_rationale: Explanation of effort score
        component_score: Component count score (1-10)
        component_rationale: Explanation of component score
        integration_score: Integration points score (1-10)
        integration_rationale: Explanation of integration score

    Returns:
        CategoryScore for complexity.
    """
    category = CategoryScore(category="Complexity")
    category.add_dimension("Effort Days", effort_score, effort_rationale)
    category.add_dimension("Component Count", component_score, component_rationale)
    category.add_dimension(
        "Integration Points", integration_score, integration_rationale
    )
    return category


def create_risk_assessment(
    security_score: int,
    security_rationale: str,
    compliance_score: int,
    compliance_rationale: str,
    data_score: int,
    data_rationale: str,
) -> CategoryScore:
    """Create risk category assessment.

    Args:
        security_score: Security implications score (1-10)
        security_rationale: Explanation of security score
        compliance_score: Compliance requirements score (1-10)
        compliance_rationale: Explanation of compliance score
        data_score: Data sensitivity score (1-10)
        data_rationale: Explanation of data score

    Returns:
        CategoryScore for risk.
    """
    category = CategoryScore(category="Risk")
    category.add_dimension("Security Implications", security_score, security_rationale)
    category.add_dimension(
        "Compliance Requirements", compliance_score, compliance_rationale
    )
    category.add_dimension("Data Sensitivity", data_score, data_rationale)
    return category


def create_architecture_impact_assessment(
    patterns_score: int,
    patterns_rationale: str,
    breaking_score: int,
    breaking_rationale: str,
    dependencies_score: int,
    dependencies_rationale: str,
) -> CategoryScore:
    """Create architecture impact category assessment.

    Args:
        patterns_score: New patterns score (1-10)
        patterns_rationale: Explanation of patterns score
        breaking_score: Breaking changes score (1-10)
        breaking_rationale: Explanation of breaking score
        dependencies_score: Dependencies affected score (1-10)
        dependencies_rationale: Explanation of dependencies score

    Returns:
        CategoryScore for architecture impact.
    """
    category = CategoryScore(category="Architecture Impact")
    category.add_dimension("New Patterns", patterns_score, patterns_rationale)
    category.add_dimension("Breaking Changes", breaking_score, breaking_rationale)
    category.add_dimension(
        "Dependencies Affected", dependencies_score, dependencies_rationale
    )
    return category
