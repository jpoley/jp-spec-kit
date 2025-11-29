"""Speech-to-Text service wrapper using Deepgram.

Provides a custom wrapper around pipecat-ai's DeepgramSTTService with
JP Spec Kit-specific configuration and error handling.
"""

import os
from typing import Optional

from pipecat.services.deepgram.stt import DeepgramSTTService as PipecatDeepgramSTT


class STTServiceError(Exception):
    """Exception raised for STT service errors.

    Attributes:
        message: Human-readable error description
        retry_hint: Optional suggestion for resolving the error
    """

    def __init__(self, message: str, retry_hint: Optional[str] = None):
        """Initialize STT service error.

        Args:
            message: Error description
            retry_hint: Optional suggestion for resolution
        """
        self.message = message
        self.retry_hint = retry_hint
        super().__init__(message)

    def __str__(self) -> str:
        """Format error message with retry hint if available."""
        if self.retry_hint:
            return f"{self.message}\nRetry hint: {self.retry_hint}"
        return self.message


class DeepgramSTTService(PipecatDeepgramSTT):
    """Deepgram Speech-to-Text service wrapper.

    Extends pipecat's DeepgramSTTService with custom configuration
    for optimal accuracy and streaming transcription using Nova 3 model.

    Features:
    - Streaming transcription with word-level timing
    - TranscriptionFrame output with high accuracy
    - Configurable model and language
    - Environment-based API key loading

    Example:
        >>> config = STTConfig(provider="deepgram", model="nova-3", language="en")
        >>> stt = DeepgramSTTService.from_config(config)
        >>> # Use in Pipecat pipeline
        >>> pipeline = Pipeline([stt, ...])
    """

    def __init__(
        self,
        *,
        api_key: str,
        model: str = "nova-3",
        language: str = "en",
        **kwargs,
    ):
        """Initialize Deepgram STT service.

        Args:
            api_key: Deepgram API key
            model: Deepgram model to use (default: "nova-3" for optimal accuracy)
            language: Language code (default: "en")
            **kwargs: Additional arguments passed to DeepgramSTTService

        Raises:
            STTServiceError: If API key is missing or connection fails
        """
        if not api_key:
            raise STTServiceError(
                "Deepgram API key is required",
                retry_hint="Set DEEPGRAM_API_KEY environment variable",
            )

        try:
            super().__init__(
                api_key=api_key,
                model=model,
                language=language,
                **kwargs,
            )
        except Exception as e:
            raise STTServiceError(
                f"Failed to initialize Deepgram STT service: {e}",
                retry_hint="Verify API key and network connectivity",
            ) from e

    @classmethod
    def from_config(cls, config) -> "DeepgramSTTService":
        """Create DeepgramSTTService from STTConfig.

        Args:
            config: STTConfig instance with provider, model, and language

        Returns:
            Configured DeepgramSTTService instance

        Raises:
            STTServiceError: If configuration is invalid or API key missing
        """
        api_key = os.getenv("DEEPGRAM_API_KEY")
        if not api_key:
            raise STTServiceError(
                "DEEPGRAM_API_KEY environment variable is not set",
                retry_hint="Export DEEPGRAM_API_KEY in your shell or .env file",
            )

        return cls(
            api_key=api_key,
            model=config.model,
            language=config.language,
        )

    @classmethod
    def from_env(
        cls, model: str = "nova-3", language: str = "en"
    ) -> "DeepgramSTTService":
        """Create DeepgramSTTService with environment-loaded API key.

        Args:
            model: Deepgram model to use (default: "nova-3")
            language: Language code (default: "en")

        Returns:
            Configured DeepgramSTTService instance

        Raises:
            STTServiceError: If DEEPGRAM_API_KEY is not set

        Example:
            >>> stt = DeepgramSTTService.from_env()
            >>> stt = DeepgramSTTService.from_env(model="nova-2", language="es")
        """
        api_key = os.getenv("DEEPGRAM_API_KEY")
        if not api_key:
            raise STTServiceError(
                "DEEPGRAM_API_KEY environment variable is not set",
                retry_hint="Export DEEPGRAM_API_KEY in your shell or .env file",
            )

        return cls(api_key=api_key, model=model, language=language)
