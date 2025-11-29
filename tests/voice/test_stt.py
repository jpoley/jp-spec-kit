"""Tests for Deepgram STT service wrapper."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from specify_cli.voice.services.stt import DeepgramSTTService, STTServiceError


class TestSTTServiceError:
    """Tests for STTServiceError exception."""

    def test_error_message_only(self) -> None:
        """Test error with message only."""
        error = STTServiceError("Test error")
        assert error.message == "Test error"
        assert error.retry_hint is None
        assert str(error) == "Test error"

    def test_error_with_retry_hint(self) -> None:
        """Test error with retry hint."""
        error = STTServiceError("Test error", retry_hint="Try again")
        assert error.message == "Test error"
        assert error.retry_hint == "Try again"
        assert str(error) == "Test error (Hint: Try again)"


class TestDeepgramSTTServiceInit:
    """Tests for DeepgramSTTService initialization."""

    @patch("specify_cli.voice.services.stt.PipecatDeepgramSTT.__init__")
    def test_init_with_valid_api_key(self, mock_init: MagicMock) -> None:
        """Test initialization with valid API key."""
        mock_init.return_value = None
        service = DeepgramSTTService(api_key="valid-key")
        assert service.model == "nova-3"
        assert service.language == "en"
        mock_init.assert_called_once()

    @patch("specify_cli.voice.services.stt.PipecatDeepgramSTT.__init__")
    def test_init_with_custom_model(self, mock_init: MagicMock) -> None:
        """Test initialization with custom model."""
        mock_init.return_value = None
        service = DeepgramSTTService(api_key="key", model="nova-2")
        assert service.model == "nova-2"

    @patch("specify_cli.voice.services.stt.PipecatDeepgramSTT.__init__")
    def test_init_with_custom_language(self, mock_init: MagicMock) -> None:
        """Test initialization with custom language."""
        mock_init.return_value = None
        service = DeepgramSTTService(api_key="key", language="es")
        assert service.language == "es"

    def test_init_without_api_key(self) -> None:
        """Test initialization fails without API key."""
        with pytest.raises(STTServiceError) as exc_info:
            DeepgramSTTService(api_key="")
        assert "API key is required" in str(exc_info.value)
        assert exc_info.value.retry_hint is not None

    def test_init_with_none_api_key(self) -> None:
        """Test initialization fails with None API key."""
        with pytest.raises(STTServiceError) as exc_info:
            DeepgramSTTService(api_key=None)  # type: ignore[arg-type]
        assert "API key is required" in str(exc_info.value)

    def test_init_with_whitespace_api_key(self) -> None:
        """Test initialization fails with whitespace API key."""
        with pytest.raises(STTServiceError) as exc_info:
            DeepgramSTTService(api_key="   ")
        assert "cannot be empty or whitespace" in str(exc_info.value)

    def test_init_with_non_string_api_key(self) -> None:
        """Test initialization fails with non-string API key."""
        with pytest.raises(STTServiceError) as exc_info:
            DeepgramSTTService(api_key=12345)  # type: ignore[arg-type]
        assert "must be a string" in str(exc_info.value)

    @patch("specify_cli.voice.services.stt.PipecatDeepgramSTT.__init__")
    def test_init_handles_parent_exception(self, mock_init: MagicMock) -> None:
        """Test that parent initialization errors are wrapped."""
        mock_init.side_effect = Exception("Connection failed")
        with pytest.raises(STTServiceError) as exc_info:
            DeepgramSTTService(api_key="valid-key")
        assert "Failed to initialize" in str(exc_info.value)
        assert exc_info.value.retry_hint is not None


class TestDeepgramSTTServiceFromConfig:
    """Tests for DeepgramSTTService.from_config."""

    @patch("specify_cli.voice.services.stt.PipecatDeepgramSTT.__init__")
    @patch.dict("os.environ", {"DEEPGRAM_API_KEY": "test-key"})
    def test_from_config_success(self, mock_init: MagicMock) -> None:
        """Test creating service from config."""
        mock_init.return_value = None
        config = MagicMock()
        config.model = "nova-3"
        config.language = "en"

        service = DeepgramSTTService.from_config(config)
        assert service.model == "nova-3"
        assert service.language == "en"

    def test_from_config_none(self) -> None:
        """Test from_config fails with None config."""
        with pytest.raises(STTServiceError) as exc_info:
            DeepgramSTTService.from_config(None)  # type: ignore[arg-type]
        assert "cannot be None" in str(exc_info.value)

    @patch.dict("os.environ", {}, clear=True)
    def test_from_config_missing_env_key(self) -> None:
        """Test from_config fails when env key is missing."""
        # Clear the DEEPGRAM_API_KEY if it exists
        import os

        os.environ.pop("DEEPGRAM_API_KEY", None)

        config = MagicMock()
        config.model = "nova-3"
        config.language = "en"

        with pytest.raises(STTServiceError) as exc_info:
            DeepgramSTTService.from_config(config)
        assert "not set" in str(exc_info.value)


class TestDeepgramSTTServiceFromEnv:
    """Tests for DeepgramSTTService.from_env."""

    @patch("specify_cli.voice.services.stt.PipecatDeepgramSTT.__init__")
    @patch.dict("os.environ", {"DEEPGRAM_API_KEY": "test-key"})
    def test_from_env_success(self, mock_init: MagicMock) -> None:
        """Test creating service from environment."""
        mock_init.return_value = None
        service = DeepgramSTTService.from_env()
        assert service.model == "nova-3"
        assert service.language == "en"

    @patch("specify_cli.voice.services.stt.PipecatDeepgramSTT.__init__")
    @patch.dict("os.environ", {"DEEPGRAM_API_KEY": "test-key"})
    def test_from_env_custom_params(self, mock_init: MagicMock) -> None:
        """Test from_env with custom parameters."""
        mock_init.return_value = None
        service = DeepgramSTTService.from_env(model="nova-2", language="fr")
        assert service.model == "nova-2"
        assert service.language == "fr"

    @patch.dict("os.environ", {}, clear=True)
    def test_from_env_missing_key(self) -> None:
        """Test from_env fails when env key is missing."""
        import os

        os.environ.pop("DEEPGRAM_API_KEY", None)

        with pytest.raises(STTServiceError) as exc_info:
            DeepgramSTTService.from_env()
        assert "not set" in str(exc_info.value)
