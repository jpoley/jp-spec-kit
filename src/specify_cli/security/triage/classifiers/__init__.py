"""Vulnerability classifiers for AI triage.

This module provides specialized classifiers for common vulnerability types.
Each classifier uses AI to determine if a finding is TP, FP, or NI.

See ADR-006 for the Strategy Pattern design.
"""

from specify_cli.security.triage.classifiers.base import (
    FindingClassifier,
    ClassificationResult,
)
from specify_cli.security.triage.classifiers.default import DefaultClassifier
from specify_cli.security.triage.classifiers.sql_injection import (
    SQLInjectionClassifier,
)
from specify_cli.security.triage.classifiers.xss import XSSClassifier
from specify_cli.security.triage.classifiers.path_traversal import (
    PathTraversalClassifier,
)
from specify_cli.security.triage.classifiers.hardcoded_secrets import (
    HardcodedSecretsClassifier,
)
from specify_cli.security.triage.classifiers.weak_crypto import WeakCryptoClassifier

__all__ = [
    "FindingClassifier",
    "ClassificationResult",
    "DefaultClassifier",
    "SQLInjectionClassifier",
    "XSSClassifier",
    "PathTraversalClassifier",
    "HardcodedSecretsClassifier",
    "WeakCryptoClassifier",
]
