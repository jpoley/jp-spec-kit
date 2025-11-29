"""Main quality scoring logic."""

from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass

from .config import QualityConfig
from .assessors import (
    assess_completeness,
    assess_clarity,
    assess_traceability,
    assess_constitutional_compliance,
    assess_ambiguity,
    AssessmentResult,
)


@dataclass
class QualityResult:
    """Overall quality assessment result."""

    overall_score: float
    completeness: AssessmentResult
    clarity: AssessmentResult
    traceability: AssessmentResult
    constitutional: AssessmentResult
    ambiguity: AssessmentResult
    config: QualityConfig

    def passes(self, threshold: Optional[int] = None) -> bool:
        """Check if overall score meets threshold."""
        if threshold is None:
            threshold = self.config.passing_threshold
        return self.overall_score >= threshold

    def is_excellent(self) -> bool:
        """Check if overall score meets excellence threshold."""
        return self.overall_score >= self.config.excellent_threshold

    def get_recommendations(self) -> List[str]:
        """Generate recommendations based on assessment results."""
        recommendations = []

        # Completeness recommendations
        if self.completeness.score < 80:
            missing = self.completeness.details.get("missing_sections", [])
            for section in missing:
                recommendations.append(f"Add missing section: {section}")

        # Clarity recommendations
        if self.clarity.score < 80:
            issues = self.clarity.details.get("issues", [])
            for issue in issues[:3]:  # Top 3 issues
                recommendations.append(f"Improve clarity: {issue}")

        # Traceability recommendations
        if self.traceability.score < 80:
            if not self.traceability.details.get("has_acceptance_criteria"):
                recommendations.append("Add clear acceptance criteria to specification")
            if not self.traceability.details.get("plan_references_spec"):
                recommendations.append("Ensure plan.md references spec requirements")

        # Constitutional recommendations
        if self.constitutional.score < 80:
            missing = self.constitutional.details.get("missing_patterns", [])
            for pattern in missing[:3]:
                recommendations.append(f"Mention required tool/pattern: {pattern}")

        # Ambiguity recommendations
        if self.ambiguity.score < 80:
            markers = self.ambiguity.details.get("markers", [])
            for marker in markers[:3]:
                recommendations.append(f"Resolve ambiguity: {marker}")

        if not recommendations:
            recommendations.append("Specification meets quality standards")

        return recommendations


class QualityScorer:
    """Quality scorer for specification files."""

    def __init__(self, config: Optional[QualityConfig] = None):
        """
        Initialize quality scorer.

        Args:
            config: Quality configuration (uses defaults if not provided)
        """
        self.config = config or QualityConfig()

        # Validate configuration
        if not self.config.validate_weights():
            raise ValueError("Quality config weights must sum to 1.0")

    def score_spec(
        self,
        spec_path: Path,
        plan_path: Optional[Path] = None,
        tasks_path: Optional[Path] = None,
    ) -> QualityResult:
        """
        Score a specification file.

        Args:
            spec_path: Path to the specification file
            plan_path: Optional path to plan.md
            tasks_path: Optional path to tasks.md

        Returns:
            QualityResult with scores and findings
        """
        # Read spec content
        if not spec_path.exists():
            raise FileNotFoundError(f"Specification file not found: {spec_path}")

        spec_content = spec_path.read_text()

        # Run assessments
        completeness = assess_completeness(spec_content, self.config.required_sections)

        clarity = assess_clarity(spec_content, self.config.vague_terms)

        traceability = assess_traceability(
            spec_path, spec_content, plan_path, tasks_path
        )

        constitutional = assess_constitutional_compliance(
            spec_content, self.config.constitutional_patterns
        )

        ambiguity = assess_ambiguity(spec_content, self.config.ambiguity_markers)

        # Calculate weighted overall score
        overall_score = (
            completeness.score * self.config.completeness_weight
            + clarity.score * self.config.clarity_weight
            + traceability.score * self.config.traceability_weight
            + constitutional.score * self.config.constitutional_weight
            + ambiguity.score * self.config.ambiguity_weight
        )

        return QualityResult(
            overall_score=round(overall_score, 1),
            completeness=completeness,
            clarity=clarity,
            traceability=traceability,
            constitutional=constitutional,
            ambiguity=ambiguity,
            config=self.config,
        )
