"""Decision logger for recording significant decisions.

Logs decisions to JSONL files organized by date.
"""

import json
import logging
from datetime import date
from pathlib import Path
from typing import Optional

from flowspec_cli.logging.config import LoggingConfig, get_config
from flowspec_cli.logging.schemas import Decision, DecisionImpact, LogSource

logger = logging.getLogger(__name__)

# Re-export for convenience
__all__ = ["DecisionLogger", "Decision", "DecisionImpact", "LogSource"]


class DecisionLogger:
    """Logger for decision entries.

    Writes decisions to date-organized JSONL files in the configured
    decisions directory.

    Usage:
        >>> logger = DecisionLogger()
        >>> logger.log(
        ...     decision="Use PostgreSQL for persistence",
        ...     context="Evaluating database options for user data",
        ...     rationale="ACID compliance, JSON support, proven reliability",
        ...     alternatives=["SQLite", "MongoDB", "DynamoDB"],
        ...     impact=DecisionImpact.HIGH,
        ...     reversible=False,
        ... )
    """

    def __init__(self, config: Optional[LoggingConfig] = None) -> None:
        """Initialize the decision logger.

        Args:
            config: Logging configuration. Auto-detected if None.
        """
        self._config = config or get_config()
        self._ensure_dir()

    def _ensure_dir(self) -> None:
        """Ensure the decisions directory exists."""
        self._config.decisions_dir.mkdir(parents=True, exist_ok=True)

    def _get_log_file(self) -> Path:
        """Get the log file for today's date."""
        today = date.today().isoformat()
        return self._config.decisions_dir / f"{today}.jsonl"

    def log(
        self,
        decision: str,
        context: str,
        rationale: str,
        alternatives: Optional[list[str]] = None,
        impact: DecisionImpact = DecisionImpact.MEDIUM,
        reversible: bool = True,
        related_tasks: Optional[list[str]] = None,
        category: Optional[str] = None,
        source: LogSource = LogSource.AGENT,
    ) -> Decision:
        """Log a decision.

        Args:
            decision: What was decided.
            context: What prompted this decision.
            rationale: Why this choice was made.
            alternatives: Other options considered.
            impact: Impact level (low, medium, high, critical).
            reversible: Can this be easily changed later?
            related_tasks: Backlog task IDs affected.
            category: Decision category (architecture, implementation, etc).
            source: Who/what made the decision (agent, human, etc).

        Returns:
            The logged Decision object.
        """
        entry = Decision(
            decision=decision,
            context=context,
            rationale=rationale,
            alternatives=alternatives or [],
            impact=impact,
            reversible=reversible,
            related_tasks=related_tasks or [],
            category=category,
            _source_override=source,
        )

        self._write_entry(entry)
        return entry

    def log_entry(self, entry: Decision) -> None:
        """Log a pre-constructed Decision entry.

        Args:
            entry: The Decision to log.
        """
        self._write_entry(entry)

    def _write_entry(self, entry: Decision) -> None:
        """Write a decision entry to the log file.

        Args:
            entry: The Decision to write.
        """
        log_file = self._get_log_file()
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry.to_dict()) + "\n")
            logger.debug(f"Decision logged: {entry.decision[:50]}...")
        except OSError as e:
            logger.error(f"Failed to write decision log: {e}")

    def read_today(self) -> list[Decision]:
        """Read today's decisions.

        Returns:
            List of Decision entries from today.
        """
        return self.read_date(date.today())

    def read_date(self, log_date: date) -> list[Decision]:
        """Read decisions from a specific date.

        Args:
            log_date: The date to read.

        Returns:
            List of Decision entries from that date.
        """
        log_file = self._config.decisions_dir / f"{log_date.isoformat()}.jsonl"
        if not log_file.exists():
            return []

        decisions = []
        try:
            with open(log_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        data = json.loads(line)
                        # Convert string values back to enums
                        if "impact" in data:
                            data["impact"] = DecisionImpact(data["impact"])
                        # Handle source field - convert to _source_override
                        if "source" in data:
                            data["_source_override"] = LogSource(data.pop("source"))
                        # Preserve original timestamp and entry_id from log file
                        # by passing them as stored values for reconstruction
                        if "timestamp" in data:
                            data["_stored_timestamp"] = data.pop("timestamp")
                        if "entry_id" in data:
                            data["_stored_entry_id"] = data.pop("entry_id")
                        decisions.append(Decision(**data))
        except (OSError, json.JSONDecodeError) as e:
            logger.error(f"Failed to read decision log: {e}")

        return decisions

    @property
    def log_directory(self) -> Path:
        """Get the decisions log directory."""
        return self._config.decisions_dir

    @property
    def is_internal_dev(self) -> bool:
        """Check if logging to internal dev location."""
        return self._config.is_internal_dev
