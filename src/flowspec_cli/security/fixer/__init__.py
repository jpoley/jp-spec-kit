"""AI-powered vulnerability fix generation.

This module provides automated code patch generation for security findings.
It generates unified diffs that can be applied to fix vulnerabilities.

See ADR-006 for the AI triage engine that identifies vulnerabilities,
and this module for the fix generation that follows.
"""

from flowspec_cli.security.fixer.models import (
    FixResult,
    FixStatus,
    Patch,
    FixPattern,
)
from flowspec_cli.security.fixer.generator import FixGenerator
from flowspec_cli.security.fixer.patterns import FixPatternLibrary
from flowspec_cli.security.fixer.applicator import (
    ApplyResult,
    ApplyStatus,
    BatchApplyResult,
    PatchApplicator,
    PatchApplicatorConfig,
)

__all__ = [
    # Models
    "FixResult",
    "FixStatus",
    "Patch",
    "FixPattern",
    # Generator
    "FixGenerator",
    "FixPatternLibrary",
    # Applicator
    "ApplyResult",
    "ApplyStatus",
    "BatchApplyResult",
    "PatchApplicator",
    "PatchApplicatorConfig",
]
