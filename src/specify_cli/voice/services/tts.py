"""Text-to-Speech service wrapper using Cartesia.

Provides CartesiaTTSService class that wraps pipecat-ai's Cartesia integration
for low-latency speech synthesis with WebSocket streaming support.
"""

import os
from typing import Optional

from pipecat.services.cartesia.tts import CartesiaTTSService as PipecatCartesiaTTSService

from ..config import TTSConfig, VoiceConfig


class TTSServiceError(Exception):
    """Exception raised for TTS service errors.

    Attributes:
        message: Error message
        provider: TTS provider name (e.g., 'cartesia')
        original_error: Original exception from provider if available
    """

    def __init__(
        self,
        message: str,
        provider: str = "cartesia",
        original_error: Optional[Exception] = None,
    ):
        """Initialize TTSServiceError.

        Args:
            message: Error message describing the failure
            provider: Name of the TTS provider
            original_error: Original exception from the provider
        """
        self.message = message
        self.provider = provider
        self.original_error = original_error
        super().__init__(f"[{provider}] {message}")


class CartesiaTTSService(PipecatCartesiaTTSService):
    """Cartesia TTS service wrapper with custom configuration.

    Extends pipecat's CartesiaTTSService with JP Spec Kit configuration
    and error handling for low-latency speech synthesis.

    Features:
    - WebSocket streaming for real-time audio output
    - Configurable voice ID and output format
    - API key loaded from environment variable
    - Enhanced error handling with TTSServiceError

    Example:
        >>> config = VoiceConfig(...)
        >>> tts = CartesiaTTSService.from_config(config)
        >>> # Use in pipecat pipeline
    """

    def __init__(
        self,
        api_key: str,
        voice_id: str = "default",
        output_format: str = "pcm_16000",
        **kwargs,
    ):
        """Initialize Cartesia TTS service.

        Args:
            api_key: Cartesia API key
            voice_id: Voice identifier for synthesis
            output_format: Audio output format (default: pcm_16000)
            **kwargs: Additional arguments passed to pipecat CartesiaTTSService

        Raises:
            TTSServiceError: If initialization fails
        """
        try:
            # Initialize parent CartesiaTTSService with configuration
            # Map our parameters to pipecat's expected format
            super().__init__(
                api_key=api_key,
                voice_id=voice_id,
                # Cartesia uses 'model_id' for output format configuration
                model_id=output_format,
                **kwargs,
            )
            self._voice_id = voice_id
            self._output_format = output_format
        except Exception as e:
            raise TTSServiceError(
                f"Failed to initialize Cartesia TTS service: {e}",
                provider="cartesia",
                original_error=e,
            ) from e

    @classmethod
    def from_config(cls, config: VoiceConfig) -> "CartesiaTTSService":
        """Create CartesiaTTSService from VoiceConfig.

        Args:
            config: Voice configuration containing TTS settings

        Returns:
            Configured CartesiaTTSService instance

        Raises:
            TTSServiceError: If API key is missing or initialization fails
        """
        # Get API key from environment
        api_key = os.getenv("CARTESIA_API_KEY")
        if not api_key:
            raise TTSServiceError(
                "CARTESIA_API_KEY environment variable not set",
                provider="cartesia",
            )

        # Extract TTS configuration
        tts_config: TTSConfig = config.pipeline.tts

        # Validate provider
        if tts_config.provider.lower() != "cartesia":
            raise TTSServiceError(
                f"Invalid provider '{tts_config.provider}' for CartesiaTTSService. Expected 'cartesia'.",
                provider=tts_config.provider,
            )

        return cls(
            api_key=api_key,
            voice_id=tts_config.voice_id,
            output_format=tts_config.output_format,
        )

    async def synthesize(self, text: str) -> bytes:
        """Synthesize text to speech audio.

        Args:
            text: Text to synthesize

        Returns:
            Audio bytes in configured output format

        Raises:
            TTSServiceError: If synthesis fails
        """
        try:
            # Delegate to parent implementation
            return await super().synthesize(text)
        except Exception as e:
            raise TTSServiceError(
                f"Speech synthesis failed: {e}",
                provider="cartesia",
                original_error=e,
            ) from e

    @property
    def voice_id(self) -> str:
        """Get configured voice ID."""
        return self._voice_id

    @property
    def output_format(self) -> str:
        """Get configured output format."""
        return self._output_format
