"""Centralized logging module for flowspec.

This module provides structured logging for decisions and events with
dual-path support:
- User projects: ./logs/events and ./logs/decisions
- Internal dev (flowspec repo): .flowspec/logs/events and .flowspec/logs/decisions

Logs are always appended in JSONL format.
"""

from flowspec_cli.logging.config import LoggingConfig, get_config
from flowspec_cli.logging.decision_logger import DecisionLogger, Decision
from flowspec_cli.logging.event_logger import EventLogger, LogEvent

__all__ = [
    "LoggingConfig",
    "get_config",
    "DecisionLogger",
    "Decision",
    "EventLogger",
    "LogEvent",
]
