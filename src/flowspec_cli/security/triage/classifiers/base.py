"""Base classifier interface for vulnerability classification.

This module defines the abstract FindingClassifier interface that all
specialized classifiers must implement. Follows the Strategy Pattern.
"""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from flowspec_cli.security.models import Finding
from flowspec_cli.security.triage.models import Classification

logger = logging.getLogger(__name__)


class LLMClient(Protocol):
    """Protocol for LLM client implementations."""

    def complete(self, prompt: str) -> str:
        """Send prompt to LLM and return response."""
        ...


@dataclass
class ClassificationResult:
    """Result of AI classification."""

    classification: Classification
    confidence: float  # 0.0-1.0
    reasoning: str  # LLM's explanation


class FindingClassifier(ABC):
    """Abstract base class for finding classifiers.

    Each specialized classifier analyzes a specific type of vulnerability
    (e.g., SQL Injection, XSS) and determines if it's a true positive,
    false positive, or needs investigation.
    """

    def __init__(self, llm_client: LLMClient | None = None):
        """Initialize classifier with optional LLM client.

        Args:
            llm_client: LLM client for AI-powered classification.
                       If None, uses heuristic-based classification.
        """
        self.llm = llm_client

    @abstractmethod
    def classify(self, finding: Finding) -> ClassificationResult:
        """Classify finding as TP/FP/NI with confidence score.

        Args:
            finding: Security finding to classify.

        Returns:
            ClassificationResult with classification, confidence, and reasoning.
        """
        pass

    @property
    @abstractmethod
    def supported_cwes(self) -> list[str]:
        """Return list of CWE IDs this classifier handles."""
        pass

    def get_code_context(self, finding: Finding, context_lines: int = 5) -> str:
        """Extract code context around finding.

        Args:
            finding: Finding to get context for.
            context_lines: Number of lines before/after to include.

        Returns:
            Code snippet with surrounding context.
        """
        file_path = Path(finding.location.file)

        if not file_path.exists():
            return finding.location.code_snippet or ""

        try:
            with open(file_path) as f:
                lines = f.readlines()

            line_start = max(0, finding.location.line_start - context_lines - 1)
            line_end = min(len(lines), finding.location.line_end + context_lines)

            context = lines[line_start:line_end]
            return "".join(context)
        except OSError:
            return finding.location.code_snippet or ""

    def _parse_llm_response(self, response: str) -> ClassificationResult:
        """Parse LLM JSON response into ClassificationResult.

        Expected format:
        {
            "classification": "TP" | "FP" | "NI",
            "confidence": 0.0-1.0,
            "reasoning": "explanation"
        }
        """
        try:
            # Try to extract JSON from response
            response = response.strip()

            # Handle markdown code blocks
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                response = response[start:end].strip()

            data = json.loads(response)

            classification = Classification(data.get("classification", "NI"))
            confidence = float(data.get("confidence", 0.5))
            reasoning = data.get("reasoning", "No reasoning provided")

            # Clamp confidence to valid range
            confidence = max(0.0, min(1.0, confidence))

            return ClassificationResult(
                classification=classification,
                confidence=confidence,
                reasoning=reasoning,
            )
        except (json.JSONDecodeError, ValueError, KeyError) as exc:
            # Log the error for debugging LLM prompt issues
            logger.warning(
                "Failed to parse LLM classification response: %s - Error: %s",
                response[:200],
                exc,
            )
            # Default to needs investigation if parsing fails
            return ClassificationResult(
                classification=Classification.NEEDS_INVESTIGATION,
                confidence=0.3,
                reasoning=f"Failed to parse LLM response: {response[:200]}. Error: {exc}",
            )
