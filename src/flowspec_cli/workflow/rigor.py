"""
Rigor enforcement utilities for Flowspec workflows.

This module provides mandatory logging and tracking for:
- Decision logging (.logs/decisions/*.jsonl)
- Event logging (.logs/events/*.jsonl)
- Backlog integration (via MCP)
- Memory tracking (cross-session state)
- Constitution enforcement
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class RigorEnforcer:
    """Enforces rigor rules across all workflows (NO EXCEPTIONS)."""

    def __init__(self, workspace_root: Path, session_id: str):
        """
        Initialize rigor enforcer.

        Args:
            workspace_root: Project workspace root directory
            session_id: Unique session identifier (e.g., '001', '002')
        """
        self.workspace_root = workspace_root
        self.session_id = session_id
        self.decisions_dir = workspace_root / ".logs" / "decisions"
        self.events_dir = workspace_root / ".logs" / "events"

        # Ensure logging directories exist
        self.decisions_dir.mkdir(parents=True, exist_ok=True)
        self.events_dir.mkdir(parents=True, exist_ok=True)

        self.decisions_file = self.decisions_dir / f"session-{session_id}.jsonl"
        self.events_file = self.events_dir / f"session-{session_id}.jsonl"

    def log_decision(
        self,
        decision: str,
        context: str,
        reasoning: str,
        alternatives_considered: Optional[List[str]] = None,
        outcome: Optional[str] = None,
    ) -> None:
        """
        Log a decision to .logs/decisions/*.jsonl (REQUIRED).

        Args:
            decision: The decision that was made (e.g., "SCHEMA_UPDATED")
            context: Context explaining why this decision was needed
            reasoning: Reasoning behind the decision
            alternatives_considered: List of alternatives that were considered
            outcome: Outcome of the decision
        """
        entry = {
            "timestamp": datetime.now().astimezone().isoformat(),
            "session": self.session_id,
            "decision": decision,
            "context": context,
            "reasoning": reasoning,
            "alternatives_considered": alternatives_considered or [],
            "outcome": outcome or "",
        }

        with open(self.decisions_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

        logger.debug(f"Decision logged: {decision}")

    def log_event(
        self,
        event_type: str,
        event: str,
        details: Optional[Dict[str, Any]] = None,
        workflow: Optional[str] = None,
    ) -> None:
        """
        Log an event to .logs/events/*.jsonl (REQUIRED).

        Args:
            event_type: Type of event (e.g., "WORKFLOW_START", "STEP_COMPLETE")
            event: Human-readable event description
            details: Additional event details
            workflow: Name of the workflow this event belongs to
        """
        entry = {
            "timestamp": datetime.now().astimezone().isoformat(),
            "session": self.session_id,
            "event_type": event_type,
            "event": event,
            "workflow": workflow or "",
            "details": details or {},
        }

        with open(self.events_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

        logger.debug(f"Event logged: {event_type} - {event}")

    def validate_rigor_config(self, rigor_config: Dict[str, bool]) -> bool:
        """
        Validate that rigor configuration has all required fields set to true.

        Args:
            rigor_config: Rigor configuration from custom workflow

        Returns:
            True if valid, False otherwise

        Raises:
            ValueError: If any required rigor rule is not set to true
        """
        required_rules = [
            "log_decisions",
            "log_events",
            "backlog_integration",
            "memory_tracking",
            "follow_constitution",
        ]

        for rule in required_rules:
            if not rigor_config.get(rule, False):
                raise ValueError(
                    f"Rigor rule '{rule}' must be set to true. "
                    f"Rigor enforcement is MANDATORY with NO EXCEPTIONS."
                )

        logger.info("Rigor configuration validated successfully")
        return True


def create_rigor_enforcer(workspace_root: Path, session_id: str) -> RigorEnforcer:
    """
    Create a rigor enforcer instance.

    Args:
        workspace_root: Project workspace root directory
        session_id: Unique session identifier

    Returns:
        RigorEnforcer instance
    """
    return RigorEnforcer(workspace_root, session_id)
