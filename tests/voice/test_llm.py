"""Tests for OpenAI LLM service wrapper."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from specify_cli.voice.services.llm import LLMServiceError, OpenAILLMService


class TestLLMServiceError:
    """Tests for LLMServiceError exception."""

    def test_error_basic(self) -> None:
        """Test error with message only."""
        error = LLMServiceError("Test error")
        assert error.message == "Test error"
        assert error.error_code is None
        assert error.provider == "openai"
        assert str(error) == "[openai] Test error"

    def test_error_with_code(self) -> None:
        """Test error with error code."""
        error = LLMServiceError("Test error", error_code="rate_limit")
        assert error.error_code == "rate_limit"
        assert str(error) == "[openai:rate_limit] Test error"

    def test_error_with_provider(self) -> None:
        """Test error with custom provider."""
        error = LLMServiceError("Test error", provider="anthropic")
        assert error.provider == "anthropic"
        assert str(error) == "[anthropic] Test error"


class TestOpenAILLMServiceInit:
    """Tests for OpenAILLMService initialization."""

    @patch("specify_cli.voice.services.llm.PipecatOpenAILLM.__init__")
    def test_init_with_valid_api_key(self, mock_init: MagicMock) -> None:
        """Test initialization with valid API key."""
        mock_init.return_value = None
        service = OpenAILLMService(api_key="valid-key")
        assert service.model == "gpt-4o"
        assert service.temperature == 0.7
        assert service.max_tokens == 1000
        mock_init.assert_called_once()

    @patch("specify_cli.voice.services.llm.PipecatOpenAILLM.__init__")
    def test_init_with_custom_model(self, mock_init: MagicMock) -> None:
        """Test initialization with custom model."""
        mock_init.return_value = None
        service = OpenAILLMService(api_key="key", model="gpt-3.5-turbo")
        assert service.model == "gpt-3.5-turbo"

    @patch("specify_cli.voice.services.llm.PipecatOpenAILLM.__init__")
    def test_init_with_custom_temperature(self, mock_init: MagicMock) -> None:
        """Test initialization with custom temperature."""
        mock_init.return_value = None
        service = OpenAILLMService(api_key="key", temperature=0.5)
        assert service.temperature == 0.5

    @patch("specify_cli.voice.services.llm.PipecatOpenAILLM.__init__")
    def test_init_with_custom_max_tokens(self, mock_init: MagicMock) -> None:
        """Test initialization with custom max tokens."""
        mock_init.return_value = None
        service = OpenAILLMService(api_key="key", max_tokens=2000)
        assert service.max_tokens == 2000

    def test_init_without_api_key(self) -> None:
        """Test initialization fails without API key."""
        with pytest.raises(LLMServiceError) as exc_info:
            OpenAILLMService(api_key="")
        assert "API key is required" in str(exc_info.value)
        assert exc_info.value.error_code == "missing_api_key"

    def test_init_with_none_api_key(self) -> None:
        """Test initialization fails with None API key."""
        with pytest.raises(LLMServiceError) as exc_info:
            OpenAILLMService(api_key=None)  # type: ignore[arg-type]
        assert "API key is required" in str(exc_info.value)

    def test_init_with_whitespace_api_key(self) -> None:
        """Test initialization fails with whitespace API key."""
        with pytest.raises(LLMServiceError) as exc_info:
            OpenAILLMService(api_key="   ")
        assert "cannot be empty or whitespace" in str(exc_info.value)
        assert exc_info.value.error_code == "empty_api_key"

    def test_init_with_non_string_api_key(self) -> None:
        """Test initialization fails with non-string API key."""
        with pytest.raises(LLMServiceError) as exc_info:
            OpenAILLMService(api_key=12345)  # type: ignore[arg-type]
        assert "must be a string" in str(exc_info.value)
        assert exc_info.value.error_code == "invalid_api_key_type"

    def test_init_with_invalid_temperature_low(self) -> None:
        """Test initialization fails with temperature below 0."""
        with pytest.raises(LLMServiceError) as exc_info:
            OpenAILLMService(api_key="key", temperature=-0.1)
        assert "between 0.0 and 2.0" in str(exc_info.value)
        assert exc_info.value.error_code == "invalid_temperature"

    def test_init_with_invalid_temperature_high(self) -> None:
        """Test initialization fails with temperature above 2."""
        with pytest.raises(LLMServiceError) as exc_info:
            OpenAILLMService(api_key="key", temperature=2.1)
        assert "between 0.0 and 2.0" in str(exc_info.value)

    def test_init_with_invalid_temperature_type(self) -> None:
        """Test initialization fails with non-numeric temperature."""
        with pytest.raises(LLMServiceError) as exc_info:
            OpenAILLMService(api_key="key", temperature="hot")  # type: ignore[arg-type]
        assert "must be a number" in str(exc_info.value)
        assert exc_info.value.error_code == "invalid_temperature_type"

    def test_init_with_invalid_max_tokens_zero(self) -> None:
        """Test initialization fails with zero max tokens."""
        with pytest.raises(LLMServiceError) as exc_info:
            OpenAILLMService(api_key="key", max_tokens=0)
        assert "must be positive" in str(exc_info.value)
        assert exc_info.value.error_code == "invalid_max_tokens"

    def test_init_with_invalid_max_tokens_negative(self) -> None:
        """Test initialization fails with negative max tokens."""
        with pytest.raises(LLMServiceError) as exc_info:
            OpenAILLMService(api_key="key", max_tokens=-100)
        assert "must be positive" in str(exc_info.value)

    def test_init_with_invalid_max_tokens_type(self) -> None:
        """Test initialization fails with non-integer max tokens."""
        with pytest.raises(LLMServiceError) as exc_info:
            OpenAILLMService(api_key="key", max_tokens=1.5)  # type: ignore[arg-type]
        assert "must be an integer" in str(exc_info.value)
        assert exc_info.value.error_code == "invalid_max_tokens_type"

    @patch("specify_cli.voice.services.llm.PipecatOpenAILLM.__init__")
    def test_init_handles_parent_exception(self, mock_init: MagicMock) -> None:
        """Test that parent initialization errors are wrapped."""
        mock_init.side_effect = Exception("Connection failed")
        with pytest.raises(LLMServiceError) as exc_info:
            OpenAILLMService(api_key="valid-key")
        assert "Failed to initialize" in str(exc_info.value)

    @patch("specify_cli.voice.services.llm.PipecatOpenAILLM.__init__")
    def test_init_extracts_error_code(self, mock_init: MagicMock) -> None:
        """Test that error codes are extracted from exceptions."""
        exc = Exception("API error")
        exc.code = "invalid_api_key"  # type: ignore[attr-defined]
        mock_init.side_effect = exc
        with pytest.raises(LLMServiceError) as exc_info:
            OpenAILLMService(api_key="valid-key")
        assert exc_info.value.error_code == "invalid_api_key"


class TestOpenAILLMServiceFromConfig:
    """Tests for OpenAILLMService.from_config."""

    @patch("specify_cli.voice.services.llm.PipecatOpenAILLM.__init__")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_from_config_success(self, mock_init: MagicMock) -> None:
        """Test creating service from config."""
        mock_init.return_value = None
        config = MagicMock()
        config.provider = "openai"
        config.model = "gpt-4o"
        config.temperature = 0.5
        config.max_tokens = 500

        service = OpenAILLMService.from_config(config)
        assert service.model == "gpt-4o"
        assert service.temperature == 0.5
        assert service.max_tokens == 500

    def test_from_config_none(self) -> None:
        """Test from_config fails with None config."""
        with pytest.raises(LLMServiceError) as exc_info:
            OpenAILLMService.from_config(None)  # type: ignore[arg-type]
        assert "cannot be None" in str(exc_info.value)
        assert exc_info.value.error_code == "null_config"

    def test_from_config_wrong_provider(self) -> None:
        """Test from_config fails with wrong provider."""
        config = MagicMock()
        config.provider = "anthropic"

        with pytest.raises(LLMServiceError) as exc_info:
            OpenAILLMService.from_config(config)
        assert "Expected provider 'openai'" in str(exc_info.value)
        assert exc_info.value.error_code == "wrong_provider"

    @patch.dict("os.environ", {}, clear=True)
    def test_from_config_missing_env_key(self) -> None:
        """Test from_config fails when env key is missing."""
        import os
        os.environ.pop("OPENAI_API_KEY", None)

        config = MagicMock()
        config.provider = "openai"
        config.model = "gpt-4o"
        config.temperature = 0.7
        config.max_tokens = 1000

        with pytest.raises(LLMServiceError) as exc_info:
            OpenAILLMService.from_config(config)
        assert "not set" in str(exc_info.value)
        assert exc_info.value.error_code == "missing_env_key"
