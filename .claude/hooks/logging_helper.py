"""Logging helper for Claude Code hooks.

This module provides logging setup for hooks when FLOWSPEC_CAPTURE_HOOKS is enabled.
"""

import os
import logging
from pathlib import Path


def setup_hook_logging(hook_name: str):
    """Setup logging for hooks if FLOWSPEC_CAPTURE_HOOKS is enabled.

    Args:
        hook_name: Name of the hook (e.g., "pre-tool-use-git-safety")

    Returns:
        Logger instance if logging enabled, None otherwise
    """
    if os.getenv("FLOWSPEC_CAPTURE_HOOKS") != "true":
        return None

    log_dir = Path(os.getenv("LOG_DIR", ".logs"))
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        filename=log_dir / "hooks.log",
        level=logging.INFO,
        format="[%(asctime)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    logger = logging.getLogger(hook_name)
    logger.info(f"Hook started: {hook_name}")
    return logger
