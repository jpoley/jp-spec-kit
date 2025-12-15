"""JSONL telemetry writer for flowspec.

This module provides a writer that appends telemetry events
to a JSONL (JSON Lines) file format.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .events import TelemetryEvent


class TelemetryWriter:
    """Writes telemetry events to a JSONL file.

    The writer appends events to a JSONL file, creating the file
    and parent directories if they don't exist.

    Attributes:
        telemetry_path: Path to the telemetry JSONL file
    """

    def __init__(self, telemetry_path: Path | str) -> None:
        """Initialize the telemetry writer.

        Args:
            telemetry_path: Path to the telemetry JSONL file
        """
        self.telemetry_path = Path(telemetry_path)

    def write_event(self, event: TelemetryEvent) -> bool:
        """Write a single event to the telemetry file.

        Args:
            event: The telemetry event to write

        Returns:
            True if the event was written successfully, False otherwise
        """
        try:
            # Ensure parent directory exists
            self.telemetry_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert event to JSON line
            event_dict = event.to_dict()
            json_line = json.dumps(event_dict, separators=(",", ":"))

            # Append to file (atomic append on most systems)
            with self.telemetry_path.open("a", encoding="utf-8") as f:
                f.write(json_line + "\n")

            return True
        except OSError as e:
            # Log error but don't fail - telemetry should be non-blocking
            if os.environ.get("FLOWSPEC_TELEMETRY_DEBUG"):
                print(f"Telemetry write error: {e}")
            return False

    def write_events(self, events: list[TelemetryEvent]) -> int:
        """Write multiple events to the telemetry file.

        Args:
            events: List of telemetry events to write

        Returns:
            Number of events successfully written
        """
        written = 0
        for event in events:
            if self.write_event(event):
                written += 1
        return written

    def read_events(self, limit: int = 100) -> list[dict]:
        """Read recent events from the telemetry file.

        Args:
            limit: Maximum number of events to read (from end of file)

        Returns:
            List of event dictionaries (most recent first)
        """
        if not self.telemetry_path.exists():
            return []

        try:
            with self.telemetry_path.open("r", encoding="utf-8") as f:
                lines = f.readlines()

            # Parse JSON lines from end
            events = []
            for line in reversed(lines[-limit:]):
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

            return events
        except OSError:
            return []

    def clear(self) -> bool:
        """Clear all telemetry data.

        Returns:
            True if cleared successfully, False otherwise
        """
        try:
            if self.telemetry_path.exists():
                self.telemetry_path.unlink()
            return True
        except OSError:
            return False

    def count_events(self) -> int:
        """Count the number of events in the telemetry file.

        Returns:
            Number of events (lines) in the file
        """
        if not self.telemetry_path.exists():
            return 0

        try:
            with self.telemetry_path.open("r", encoding="utf-8") as f:
                return sum(1 for line in f if line.strip())
        except OSError:
            return 0


__all__ = ["TelemetryWriter"]
