"""Configuration loading for quality assessment."""

import json
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class QualityConfig:
    """Configuration for quality assessment."""

    # Thresholds
    passing_threshold: int = 70
    excellent_threshold: int = 90

    # Weights for each dimension (must sum to 1.0)
    completeness_weight: float = 0.30
    clarity_weight: float = 0.25
    traceability_weight: float = 0.20
    constitutional_weight: float = 0.15
    ambiguity_weight: float = 0.10

    # Required sections in spec
    required_sections: List[str] = field(
        default_factory=lambda: [
            "## Description",
            "## User Story",
            "## Acceptance Criteria",
            "## Technical Requirements",
        ]
    )

    # Vague terms to detect
    vague_terms: List[str] = field(
        default_factory=lambda: [
            "etc",
            "various",
            "some",
            "maybe",
            "possibly",
            "might",
            "could",
            "should",
            "probably",
            "potentially",
            "basically",
            "simply",
            "just",
            "easily",
            "obviously",
        ]
    )

    # Ambiguity markers
    ambiguity_markers: List[str] = field(
        default_factory=lambda: [
            "TBD",
            "TODO",
            "FIXME",
            "XXX",
            "unclear",
            "to be determined",
            "to be decided",
            "???",
        ]
    )

    # Constitutional requirements (tool/pattern mentions)
    constitutional_patterns: List[str] = field(
        default_factory=lambda: ["pytest", "ruff", "uv", "typer", "rich"]
    )

    @classmethod
    def load_from_file(cls, config_path: Path) -> "QualityConfig":
        """Load configuration from JSON file."""
        if not config_path.exists():
            return cls()

        with open(config_path, "r") as f:
            data = json.load(f)

        # Extract thresholds
        thresholds = data.get("thresholds", {})
        weights = data.get("weights", {})

        return cls(
            passing_threshold=thresholds.get("passing", 70),
            excellent_threshold=thresholds.get("excellent", 90),
            completeness_weight=weights.get("completeness", 0.30),
            clarity_weight=weights.get("clarity", 0.25),
            traceability_weight=weights.get("traceability", 0.20),
            constitutional_weight=weights.get("constitutional", 0.15),
            ambiguity_weight=weights.get("ambiguity", 0.10),
            required_sections=data.get("required_sections", cls().required_sections),
            vague_terms=data.get("vague_terms", cls().vague_terms),
            ambiguity_markers=data.get("ambiguity_markers", cls().ambiguity_markers),
            constitutional_patterns=data.get(
                "constitutional_patterns", cls().constitutional_patterns
            ),
        )

    @classmethod
    def find_config(cls, start_path: Optional[Path] = None) -> "QualityConfig":
        """Find and load quality config from .specify/ directory."""
        if start_path is None:
            start_path = Path.cwd()

        # Look for .specify/quality-config.json
        current = start_path.resolve()
        while current != current.parent:
            config_file = current / ".specify" / "quality-config.json"
            if config_file.exists():
                return cls.load_from_file(config_file)
            current = current.parent

        # Return default config if not found
        return cls()

    def validate_weights(self) -> bool:
        """Validate that weights sum to approximately 1.0."""
        total = (
            self.completeness_weight
            + self.clarity_weight
            + self.traceability_weight
            + self.constitutional_weight
            + self.ambiguity_weight
        )
        return abs(total - 1.0) < 0.01  # Allow small floating point error
