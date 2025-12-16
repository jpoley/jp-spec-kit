"""Data models for the AI triage engine.

This module defines the core data structures for vulnerability triage:
- Classification: TP/FP/NI categorization
- TriageResult: Complete triage output for a finding
- ClusterType: Root cause clustering strategies
"""

from dataclasses import dataclass, field
from enum import Enum


class Classification(Enum):
    """Finding classification result from AI triage.

    TRUE_POSITIVE: Real vulnerability that should be fixed
    FALSE_POSITIVE: Not a real vulnerability (scanner noise)
    NEEDS_INVESTIGATION: Uncertain, requires human review
    """

    TRUE_POSITIVE = "TP"
    FALSE_POSITIVE = "FP"
    NEEDS_INVESTIGATION = "NI"


class ClusterType(Enum):
    """Root cause clustering strategy."""

    CWE = "cwe"  # Same CWE category
    FILE = "file"  # Same file/function
    PATTERN = "pattern"  # Same architectural pattern


@dataclass
class Explanation:
    """Plain-English vulnerability explanation.

    Follows the What/Why/How format for developer accessibility.
    """

    what: str  # 1-sentence description
    why_it_matters: str  # Security impact
    how_to_exploit: str | None  # Attack scenario (for TP only)
    how_to_fix: str  # Remediation approach


@dataclass
class TriageResult:
    """Result of AI triage for a single finding.

    Contains classification, risk scoring, explanation, and clustering
    information produced by the triage engine.
    """

    finding_id: str
    classification: Classification
    confidence: float  # 0.0-1.0
    risk_score: float  # Raptor formula result
    explanation: Explanation
    cluster_id: str | None = None  # Root cause cluster
    cluster_type: ClusterType | None = None
    ai_reasoning: str = ""  # LLM's reasoning (for debugging)
    metadata: dict = field(default_factory=dict)

    @property
    def is_actionable(self) -> bool:
        """Returns True if finding requires developer action."""
        return self.classification == Classification.TRUE_POSITIVE

    @property
    def requires_review(self) -> bool:
        """Returns True if finding requires human review."""
        return self.classification == Classification.NEEDS_INVESTIGATION

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "finding_id": self.finding_id,
            "classification": self.classification.value,
            "confidence": self.confidence,
            "risk_score": self.risk_score,
            "explanation": {
                "what": self.explanation.what,
                "why_it_matters": self.explanation.why_it_matters,
                "how_to_exploit": self.explanation.how_to_exploit,
                "how_to_fix": self.explanation.how_to_fix,
            },
            "cluster_id": self.cluster_id,
            "cluster_type": self.cluster_type.value if self.cluster_type else None,
            "ai_reasoning": self.ai_reasoning,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TriageResult":
        """Create from dictionary."""
        return cls(
            finding_id=data["finding_id"],
            classification=Classification(data["classification"]),
            confidence=data["confidence"],
            risk_score=data["risk_score"],
            explanation=Explanation(
                what=data["explanation"]["what"],
                why_it_matters=data["explanation"]["why_it_matters"],
                how_to_exploit=data["explanation"].get("how_to_exploit"),
                how_to_fix=data["explanation"]["how_to_fix"],
            ),
            cluster_id=data.get("cluster_id"),
            cluster_type=(
                ClusterType(data["cluster_type"]) if data.get("cluster_type") else None
            ),
            ai_reasoning=data.get("ai_reasoning", ""),
            metadata=data.get("metadata", {}),
        )


@dataclass
class RiskComponents:
    """Components of the Raptor risk scoring formula.

    Formula: risk_score = (impact × exploitability) / detection_time
    """

    impact: float  # 0-10 scale (CVSS or AI-estimated)
    exploitability: float  # 0-10 scale (AI-estimated)
    detection_time: int  # Days since code written (1-365+)

    @property
    def risk_score(self) -> float:
        """Calculate risk score using Raptor formula."""
        return round(
            (self.impact * self.exploitability) / max(self.detection_time, 1), 2
        )
