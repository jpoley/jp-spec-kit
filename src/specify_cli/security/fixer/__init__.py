"""AI-powered vulnerability fix generation.

This module provides automated code patch generation for security findings.
It generates unified diffs that can be applied to fix vulnerabilities.

See ADR-006 for the AI triage engine that identifies vulnerabilities,
and this module for the fix generation that follows.
"""

from specify_cli.security.fixer.models import (
    FixResult,
    FixStatus,
    Patch,
    FixPattern,
)
from specify_cli.security.fixer.generator import FixGenerator
from specify_cli.security.fixer.patterns import FixPatternLibrary
from specify_cli.security.fixer.applicator import (
    PatchApplicator,
    ApplyResult,
    ApplyStatus,
    ConfirmationHandler,
    DefaultConfirmationHandler,
)

__all__ = [
    "FixResult",
    "FixStatus",
    "Patch",
    "FixPattern",
    "FixGenerator",
    "FixPatternLibrary",
    "PatchApplicator",
    "ApplyResult",
    "ApplyStatus",
    "ConfirmationHandler",
    "DefaultConfirmationHandler",
]
