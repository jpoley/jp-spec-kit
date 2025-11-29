"""LLM service wrapper using OpenAI.

This module provides a wrapper around pipecat-ai's OpenAI LLM service
with JP Spec Kit-specific configuration and error handling.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from specify_cli.voice.config import LLMConfig

from pipecat.services.openai.base_llm import BaseOpenAILLMService
from pipecat.services.openai.llm import OpenAILLMService as PipecatOpenAILLM


class LLMServiceError(Exception):
    """Error raised by LLM service operations.

    Attributes:
        message: Human-readable error description.
        error_code: Optional error code from provider.
        provider: Name of the LLM provider.
    """

    def __init__(
        self,
        message: str,
        *,
        error_code: Optional[str] = None,
        provider: str = "openai",
    ) -> None:
        """Initialize LLM service error.

        Args:
            message: Error description.
            error_code: Provider-specific error code.
            provider: LLM provider name.
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.provider = provider

    def __str__(self) -> str:
        """Return formatted error message."""
        if self.error_code:
            return f"[{self.provider}:{self.error_code}] {self.message}"
        return f"[{self.provider}] {self.message}"


class OpenAILLMService(PipecatOpenAILLM):
    """OpenAI LLM service wrapper with JP Spec Kit configuration.

    This class extends pipecat's OpenAILLMService with:
    - Configuration validation at initialization
    - Factory method for loading from config
    - Custom error handling with error codes
    - Streaming responses for token-by-token delivery to TTS
    - Function calling support enabled by default

    Example:
        >>> service = OpenAILLMService(api_key="your-key")
        >>> # Or from config
        >>> service = OpenAILLMService.from_config(llm_config)
    """

    def __init__(
        self,
        *,
        api_key: str,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs: object,
    ) -> None:
        """Initialize OpenAI LLM service.

        Args:
            api_key: OpenAI API key (required, non-empty).
            model: Model name (default: gpt-4o).
            temperature: Sampling temperature 0.0-2.0 (default: 0.7).
            max_tokens: Maximum response tokens (default: 1000).
            **kwargs: Additional arguments passed to pipecat service.

        Raises:
            LLMServiceError: If validation fails.
        """
        # DEFENSIVE: Validate api_key
        if not api_key:
            raise LLMServiceError(
                "OpenAI API key is required. Set OPENAI_API_KEY environment variable.",
                error_code="missing_api_key",
            )
        if not isinstance(api_key, str):
            raise LLMServiceError(
                f"API key must be a string, got {type(api_key).__name__}",
                error_code="invalid_api_key_type",
            )
        api_key_stripped = api_key.strip()
        if not api_key_stripped:
            raise LLMServiceError(
                "OpenAI API key cannot be empty or whitespace",
                error_code="empty_api_key",
            )

        # DEFENSIVE: Validate temperature
        if not isinstance(temperature, (int, float)):
            raise LLMServiceError(
                f"Temperature must be a number, got {type(temperature).__name__}",
                error_code="invalid_temperature_type",
            )
        if not 0.0 <= temperature <= 2.0:
            raise LLMServiceError(
                f"Temperature must be between 0.0 and 2.0, got {temperature}",
                error_code="invalid_temperature",
            )

        # DEFENSIVE: Validate max_tokens
        if not isinstance(max_tokens, int):
            raise LLMServiceError(
                f"max_tokens must be an integer, got {type(max_tokens).__name__}",
                error_code="invalid_max_tokens_type",
            )
        if max_tokens <= 0:
            raise LLMServiceError(
                f"max_tokens must be positive, got {max_tokens}",
                error_code="invalid_max_tokens",
            )

        # Store configuration for properties
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens

        # Create InputParams with temperature and max_tokens for proper configuration
        # This enables streaming responses for token-by-token delivery to TTS
        params = BaseOpenAILLMService.InputParams(
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Initialize parent with validated values and params
        # Function calling is supported through the context/tools mechanism in pipecat
        try:
            super().__init__(
                api_key=api_key_stripped,
                model=model,
                params=params,
                **kwargs,
            )
        except Exception as e:
            # Extract error code if available
            error_code = None
            if hasattr(e, "code"):
                error_code = str(e.code)
            elif hasattr(e, "status_code"):
                error_code = str(e.status_code)

            raise LLMServiceError(
                f"Failed to initialize OpenAI service: {e}",
                error_code=error_code,
            ) from e

    @classmethod
    def from_config(cls, config: LLMConfig) -> "OpenAILLMService":
        """Create service from LLMConfig.

        Args:
            config: LLM configuration object.

        Returns:
            Configured OpenAILLMService instance.

        Raises:
            LLMServiceError: If config is invalid or API key missing.
        """
        # DEFENSIVE: Validate config
        if config is None:
            raise LLMServiceError(
                "LLMConfig cannot be None",
                error_code="null_config",
            )

        if config.provider != "openai":
            raise LLMServiceError(
                f"Expected provider 'openai', got '{config.provider}'",
                error_code="wrong_provider",
            )

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise LLMServiceError(
                "OPENAI_API_KEY environment variable is not set",
                error_code="missing_env_key",
            )

        return cls(
            api_key=api_key,
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )

    @property
    def model(self) -> str:
        """Return the model name."""
        return self._model

    @property
    def temperature(self) -> float:
        """Return the temperature setting."""
        return self._temperature

    @property
    def max_tokens(self) -> int:
        """Return the max tokens setting."""
        return self._max_tokens
