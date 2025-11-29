"""Speech-to-Text service wrapper using Deepgram.

This module provides a wrapper around pipecat-ai's Deepgram STT service
with JP Spec Kit-specific configuration and error handling.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from specify_cli.voice.config import STTConfig

from deepgram import LiveOptions
from pipecat.services.deepgram.stt import DeepgramSTTService as PipecatDeepgramSTT
from pipecat.transcriptions.language import Language


class STTServiceError(Exception):
    """Error raised by STT service operations.

    Attributes:
        message: Human-readable error description.
        retry_hint: Optional hint for resolving the error.
    """

    def __init__(self, message: str, *, retry_hint: Optional[str] = None) -> None:
        """Initialize STT service error.

        Args:
            message: Error description.
            retry_hint: Optional suggestion for resolution.
        """
        super().__init__(message)
        self.message = message
        self.retry_hint = retry_hint

    def __str__(self) -> str:
        """Return formatted error message with retry hint if available."""
        if self.retry_hint:
            return f"{self.message} (Hint: {self.retry_hint})"
        return self.message


class DeepgramSTTService(PipecatDeepgramSTT):
    """Deepgram STT service wrapper with JP Spec Kit configuration.

    This class extends pipecat's DeepgramSTTService with:
    - Configuration validation at initialization
    - Factory methods for loading from config or environment
    - Custom error handling with actionable messages

    Example:
        >>> service = DeepgramSTTService(api_key="your-key")
        >>> # Or from environment
        >>> service = DeepgramSTTService.from_env()
    """

    def __init__(
        self,
        *,
        api_key: str,
        model: str = "nova-3",
        language: str = "en",
        **kwargs: object,
    ) -> None:
        """Initialize Deepgram STT service.

        Args:
            api_key: Deepgram API key (required, non-empty).
            model: Deepgram model name (default: nova-3).
            language: Language code (default: en).
            **kwargs: Additional arguments passed to pipecat service.

        Raises:
            STTServiceError: If api_key is missing or empty.
        """
        # DEFENSIVE: Validate inputs at boundary
        if not api_key:
            raise STTServiceError(
                "Deepgram API key is required",
                retry_hint="Set DEEPGRAM_API_KEY environment variable",
            )
        if not isinstance(api_key, str):
            raise STTServiceError(
                f"API key must be a string, got {type(api_key).__name__}",
            )
        api_key_stripped = api_key.strip()
        if not api_key_stripped:
            raise STTServiceError(
                "Deepgram API key cannot be empty or whitespace",
                retry_hint="Set DEEPGRAM_API_KEY environment variable",
            )

        # Store configuration
        self._model = model
        self._language = language

        # Create LiveOptions for Deepgram configuration
        # This enables streaming transcription with word-level timing
        live_options = LiveOptions(
            model=model,
            language=Language(language) if language else Language.EN,
            encoding="linear16",
            channels=1,
            interim_results=True,  # Enable streaming transcription
            smart_format=True,  # Smart punctuation and formatting
            punctuate=True,
            profanity_filter=True,
        )

        # Initialize parent with validated key and options
        try:
            super().__init__(
                api_key=api_key_stripped,
                live_options=live_options,
                **kwargs,
            )
        except Exception as e:
            raise STTServiceError(
                f"Failed to initialize Deepgram service: {e}",
                retry_hint="Check your API key and network connection",
            ) from e

    @classmethod
    def from_config(cls, config: STTConfig) -> "DeepgramSTTService":
        """Create service from STTConfig.

        Args:
            config: STT configuration object.

        Returns:
            Configured DeepgramSTTService instance.

        Raises:
            STTServiceError: If API key is not in environment.
        """
        # DEFENSIVE: Validate config
        if config is None:
            raise STTServiceError("STTConfig cannot be None")

        api_key = os.getenv("DEEPGRAM_API_KEY")
        if not api_key:
            raise STTServiceError(
                "DEEPGRAM_API_KEY environment variable is not set",
                retry_hint="export DEEPGRAM_API_KEY=your-api-key",
            )

        return cls(
            api_key=api_key,
            model=config.model,
            language=config.language,
        )

    @classmethod
    def from_env(
        cls,
        *,
        model: str = "nova-3",
        language: str = "en",
    ) -> "DeepgramSTTService":
        """Create service from environment variables.

        Args:
            model: Deepgram model name (default: nova-3).
            language: Language code (default: en).

        Returns:
            Configured DeepgramSTTService instance.

        Raises:
            STTServiceError: If DEEPGRAM_API_KEY is not set.
        """
        api_key = os.getenv("DEEPGRAM_API_KEY")
        if not api_key:
            raise STTServiceError(
                "DEEPGRAM_API_KEY environment variable is not set",
                retry_hint="export DEEPGRAM_API_KEY=your-api-key",
            )

        return cls(api_key=api_key, model=model, language=language)

    @property
    def model(self) -> str:
        """Return the model name."""
        return self._model

    @property
    def language(self) -> str:
        """Return the language code."""
        return self._language
