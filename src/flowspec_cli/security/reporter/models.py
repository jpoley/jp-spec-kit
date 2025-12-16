"""Data models for security audit reports."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class SecurityPosture(Enum):
    """Overall security posture assessment."""

    SECURE = "secure"  # No critical/high findings, low FP rate
    CONDITIONAL = "conditional"  # Some high findings, manageable risk
    AT_RISK = "at_risk"  # Critical findings or systemic issues


class ComplianceStatus(Enum):
    """OWASP compliance status."""

    COMPLIANT = "compliant"  # No findings for this category
    PARTIAL = "partial"  # Some findings, not critical
    NON_COMPLIANT = "non_compliant"  # Critical findings in this category


@dataclass
class OWASPCategory:
    """OWASP Top 10 category with compliance status."""

    id: str  # e.g., "A01:2021"
    name: str  # e.g., "Broken Access Control"
    status: ComplianceStatus
    finding_count: int
    critical_count: int
    cwes: list[str]  # CWEs mapped to this category

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "finding_count": self.finding_count,
            "critical_count": self.critical_count,
            "cwes": self.cwes,
        }


@dataclass
class FindingSummary:
    """Summary of security findings."""

    total: int
    critical: int
    high: int
    medium: int
    low: int
    info: int
    true_positives: int
    false_positives: int
    needs_investigation: int

    @property
    def actionable(self) -> int:
        """Number of findings requiring action."""
        return self.true_positives

    @property
    def false_positive_rate(self) -> float:
        """Calculate FP rate."""
        if self.total == 0:
            return 0.0
        return self.false_positives / self.total

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "total": self.total,
            "critical": self.critical,
            "high": self.high,
            "medium": self.medium,
            "low": self.low,
            "info": self.info,
            "true_positives": self.true_positives,
            "false_positives": self.false_positives,
            "needs_investigation": self.needs_investigation,
            "actionable": self.actionable,
            "false_positive_rate": round(self.false_positive_rate * 100, 1),
        }


@dataclass
class Remediation:
    """Remediation recommendation."""

    finding_id: str
    priority: int  # 1 = highest
    title: str
    description: str
    fix_guidance: str
    estimated_effort: str  # e.g., "1 hour", "1 day"
    cwe_id: str | None = None

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "finding_id": self.finding_id,
            "priority": self.priority,
            "title": self.title,
            "description": self.description,
            "fix_guidance": self.fix_guidance,
            "estimated_effort": self.estimated_effort,
            "cwe_id": self.cwe_id,
        }


@dataclass
class AuditReport:
    """Complete security audit report."""

    project_name: str
    scan_date: datetime
    posture: SecurityPosture
    summary: FindingSummary
    owasp_compliance: list[OWASPCategory]
    remediations: list[Remediation]
    scanners_used: list[str]
    files_scanned: int
    metadata: dict = field(default_factory=dict)

    @property
    def compliance_score(self) -> float:
        """Calculate OWASP compliance score (0-100)."""
        if not self.owasp_compliance:
            return 100.0

        compliant = sum(
            1 for c in self.owasp_compliance if c.status == ComplianceStatus.COMPLIANT
        )
        partial = sum(
            1 for c in self.owasp_compliance if c.status == ComplianceStatus.PARTIAL
        )

        # Full compliance = 10 pts, partial = 5 pts
        score = (compliant * 10 + partial * 5) / len(self.owasp_compliance)
        return round(score * 10, 1)  # Scale to 100

    @property
    def top_remediations(self) -> list[Remediation]:
        """Get top 5 priority remediations."""
        return sorted(self.remediations, key=lambda r: r.priority)[:5]

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "project_name": self.project_name,
            "scan_date": self.scan_date.isoformat(),
            "posture": self.posture.value,
            "compliance_score": self.compliance_score,
            "summary": self.summary.to_dict(),
            "owasp_compliance": [c.to_dict() for c in self.owasp_compliance],
            "remediations": [r.to_dict() for r in self.remediations],
            "scanners_used": self.scanners_used,
            "files_scanned": self.files_scanned,
            "metadata": self.metadata,
        }
