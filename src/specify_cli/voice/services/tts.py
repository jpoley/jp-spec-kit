"""Text-to-Speech service wrapper using Cartesia.

This module provides a wrapper around pipecat-ai's Cartesia TTS service
with JP Spec Kit-specific configuration and error handling.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from specify_cli.voice.config import TTSConfig

from pipecat.services.cartesia.tts import CartesiaTTSService as PipecatCartesiaTTS


class TTSServiceError(Exception):
    """Error raised by TTS service operations.

    Attributes:
        message: Human-readable error description.
        provider: Name of the TTS provider.
        original_error: Original exception if wrapping another error.
    """

    def __init__(
        self,
        message: str,
        *,
        provider: str = "cartesia",
        original_error: Optional[Exception] = None,
    ) -> None:
        """Initialize TTS service error.

        Args:
            message: Error description.
            provider: TTS provider name.
            original_error: Original exception being wrapped.
        """
        super().__init__(message)
        self.message = message
        self.provider = provider
        self.original_error = original_error

    def __str__(self) -> str:
        """Return formatted error message."""
        return f"[{self.provider}] {self.message}"


class CartesiaTTSService(PipecatCartesiaTTS):
    """Cartesia TTS service wrapper with JP Spec Kit configuration.

    This class extends pipecat's CartesiaTTSService with:
    - Configuration validation at initialization
    - Factory method for loading from config
    - Custom error handling with provider context
    - WebSocket streaming for real-time audio output

    Example:
        >>> service = CartesiaTTSService(api_key="your-key", voice_id="voice-123")
        >>> # Or from config
        >>> service = CartesiaTTSService.from_config(tts_config)
    """

    def __init__(
        self,
        *,
        api_key: str,
        voice_id: str,
        model: str = "sonic-3",
        sample_rate: int = 16000,
        encoding: str = "pcm_s16le",
        **kwargs: object,
    ) -> None:
        """Initialize Cartesia TTS service.

        Args:
            api_key: Cartesia API key (required, non-empty).
            voice_id: Voice identifier (required).
            model: TTS model to use (default: sonic-3).
            sample_rate: Audio sample rate in Hz (default: 16000).
            encoding: Audio encoding format (default: pcm_s16le).
            **kwargs: Additional arguments passed to pipecat service.

        Raises:
            TTSServiceError: If api_key is missing or empty.
        """
        # DEFENSIVE: Validate inputs at boundary
        if not api_key:
            raise TTSServiceError(
                "Cartesia API key is required. Set CARTESIA_API_KEY environment variable."
            )
        if not isinstance(api_key, str):
            raise TTSServiceError(
                f"API key must be a string, got {type(api_key).__name__}"
            )
        api_key_stripped = api_key.strip()
        if not api_key_stripped:
            raise TTSServiceError("Cartesia API key cannot be empty or whitespace")

        if not voice_id:
            raise TTSServiceError("Voice ID is required for Cartesia TTS service")

        # Store configuration for properties
        self._voice_id = voice_id
        self._model = model
        self._sample_rate = sample_rate
        self._encoding = encoding

        # Initialize parent with validated parameters
        # Cartesia uses WebSocket streaming for real-time audio output
        try:
            super().__init__(
                api_key=api_key_stripped,
                voice_id=voice_id,
                model=model,
                sample_rate=sample_rate,
                encoding=encoding,
                **kwargs,
            )
        except Exception as e:
            raise TTSServiceError(
                f"Failed to initialize Cartesia service: {e}",
                original_error=e,
            ) from e

    @classmethod
    def from_config(cls, config: TTSConfig) -> "CartesiaTTSService":
        """Create service from TTSConfig.

        Args:
            config: TTS configuration object.

        Returns:
            Configured CartesiaTTSService instance.

        Raises:
            TTSServiceError: If config is invalid or API key missing.
        """
        # DEFENSIVE: Validate config
        if config is None:
            raise TTSServiceError("TTSConfig cannot be None")

        if config.provider != "cartesia":
            raise TTSServiceError(
                f"Expected provider 'cartesia', got '{config.provider}'"
            )

        api_key = os.getenv("CARTESIA_API_KEY")
        if not api_key:
            raise TTSServiceError("CARTESIA_API_KEY environment variable is not set")

        # Parse output_format to extract sample rate if present (e.g., "pcm_16000")
        sample_rate = 16000
        if config.output_format and "_" in config.output_format:
            try:
                rate_str = config.output_format.split("_")[1]
                sample_rate = int(rate_str)
            except (IndexError, ValueError):
                pass  # Use default if parsing fails

        return cls(
            api_key=api_key,
            voice_id=config.voice_id,
            sample_rate=sample_rate,
        )

    @property
    def voice_id(self) -> str:
        """Return the voice identifier."""
        return self._voice_id

    @property
    def model(self) -> str:
        """Return the TTS model."""
        return self._model

    @property
    def sample_rate(self) -> int:
        """Return the audio sample rate."""
        return self._sample_rate

    @property
    def encoding(self) -> str:
        """Return the audio encoding format."""
        return self._encoding
