"""Security finding models and exporters for JP Spec Kit.

This module implements the Unified Finding Format (UFFormat) for security
scanners, providing a canonical data model that all security tools can map to.

Key Components:
    - Finding: Core security finding dataclass
    - Location: Source code location for findings
    - Severity/Confidence: Enums for classification
    - Exporters: SARIF, Markdown, JSON export formats

See ADR-007 for design rationale and implementation details.
"""

from specify_cli.security.models import (
    Confidence,
    Finding,
    Location,
    Severity,
)

__all__ = [
    "Confidence",
    "Finding",
    "Location",
    "Severity",
]
