"""Voice module for JP Spec Kit - Real-time voice interface powered by Pipecat.

This module provides voice-driven interaction with JP Spec Kit functionality,
enabling users to create specifications, manage tasks, and execute workflows
through natural voice conversation.

Architecture:
- processors/: Custom Pipecat frame processors
- services/: Service wrappers for STT, TTS, LLM providers
- tools/: Function call handlers for JP Spec Kit operations
- flows/: Conversation flow definitions
"""

__version__ = "0.0.94"
