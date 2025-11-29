"""Tests for Deepgram STT service wrapper."""

import os
from unittest.mock import patch

import pytest

from specify_cli.voice.services.stt import DeepgramSTTService, STTServiceError


class MockSTTConfig:
    """Mock STTConfig for testing."""

    def __init__(self, provider="deepgram", model="nova-3", language="en"):
        self.provider = provider
        self.model = model
        self.language = language


class TestSTTServiceError:
    """Tests for STTServiceError exception."""

    def test_error_with_message_only(self):
        """Test error creation with message only."""
        error = STTServiceError("Connection failed")
        assert error.message == "Connection failed"
        assert error.retry_hint is None
        assert str(error) == "Connection failed"

    def test_error_with_retry_hint(self):
        """Test error creation with retry hint."""
        error = STTServiceError(
            "API key invalid", retry_hint="Check DEEPGRAM_API_KEY variable"
        )
        assert error.message == "API key invalid"
        assert error.retry_hint == "Check DEEPGRAM_API_KEY variable"
        assert "Retry hint:" in str(error)
        assert "Check DEEPGRAM_API_KEY variable" in str(error)


class TestDeepgramSTTService:
    """Tests for DeepgramSTTService wrapper."""

    @patch("specify_cli.voice.services.stt.PipecatDeepgramSTT.__init__")
    def test_init_with_valid_api_key(self, mock_parent_init):
        """Test initialization with valid API key."""
        mock_parent_init.return_value = None

        DeepgramSTTService(api_key="test-key-123")

        mock_parent_init.assert_called_once_with(
            api_key="test-key-123",
            model="nova-3",
            language="en",
        )

    @patch("specify_cli.voice.services.stt.PipecatDeepgramSTT.__init__")
    def test_init_with_custom_model(self, mock_parent_init):
        """Test initialization with custom model."""
        mock_parent_init.return_value = None

        DeepgramSTTService(api_key="test-key-123", model="nova-2", language="es")

        mock_parent_init.assert_called_once_with(
            api_key="test-key-123",
            model="nova-2",
            language="es",
        )

    def test_init_without_api_key(self):
        """Test initialization fails without API key."""
        with pytest.raises(STTServiceError) as exc_info:
            DeepgramSTTService(api_key="")

        assert "Deepgram API key is required" in str(exc_info.value)
        assert exc_info.value.retry_hint is not None
        assert "DEEPGRAM_API_KEY" in exc_info.value.retry_hint

    @patch("specify_cli.voice.services.stt.PipecatDeepgramSTT.__init__")
    def test_init_with_connection_error(self, mock_parent_init):
        """Test initialization handles connection errors."""
        mock_parent_init.side_effect = ConnectionError("Network unreachable")

        with pytest.raises(STTServiceError) as exc_info:
            DeepgramSTTService(api_key="test-key-123")

        assert "Failed to initialize" in str(exc_info.value)
        assert exc_info.value.retry_hint is not None
        assert "network connectivity" in exc_info.value.retry_hint.lower()

    @patch("specify_cli.voice.services.stt.PipecatDeepgramSTT.__init__")
    @patch.dict(os.environ, {"DEEPGRAM_API_KEY": "env-test-key"})
    def test_from_config(self, mock_parent_init):
        """Test from_config class method."""
        mock_parent_init.return_value = None
        config = MockSTTConfig(provider="deepgram", model="nova-3", language="en")

        DeepgramSTTService.from_config(config)

        mock_parent_init.assert_called_once_with(
            api_key="env-test-key",
            model="nova-3",
            language="en",
        )

    @patch.dict(os.environ, {}, clear=True)
    def test_from_config_missing_api_key(self):
        """Test from_config fails when env var is missing."""
        config = MockSTTConfig()

        with pytest.raises(STTServiceError) as exc_info:
            DeepgramSTTService.from_config(config)

        assert "DEEPGRAM_API_KEY environment variable is not set" in str(exc_info.value)
        assert exc_info.value.retry_hint is not None

    @patch("specify_cli.voice.services.stt.PipecatDeepgramSTT.__init__")
    @patch.dict(os.environ, {"DEEPGRAM_API_KEY": "env-test-key"})
    def test_from_env_defaults(self, mock_parent_init):
        """Test from_env with default parameters."""
        mock_parent_init.return_value = None

        DeepgramSTTService.from_env()

        mock_parent_init.assert_called_once_with(
            api_key="env-test-key",
            model="nova-3",
            language="en",
        )

    @patch("specify_cli.voice.services.stt.PipecatDeepgramSTT.__init__")
    @patch.dict(os.environ, {"DEEPGRAM_API_KEY": "env-test-key"})
    def test_from_env_custom_params(self, mock_parent_init):
        """Test from_env with custom model and language."""
        mock_parent_init.return_value = None

        DeepgramSTTService.from_env(model="nova-2", language="fr")

        mock_parent_init.assert_called_once_with(
            api_key="env-test-key",
            model="nova-2",
            language="fr",
        )

    @patch.dict(os.environ, {}, clear=True)
    def test_from_env_missing_api_key(self):
        """Test from_env fails when DEEPGRAM_API_KEY is not set."""
        with pytest.raises(STTServiceError) as exc_info:
            DeepgramSTTService.from_env()

        assert "DEEPGRAM_API_KEY environment variable is not set" in str(exc_info.value)
        assert "Export DEEPGRAM_API_KEY" in exc_info.value.retry_hint

    @patch("specify_cli.voice.services.stt.PipecatDeepgramSTT.__init__")
    @patch.dict(os.environ, {"DEEPGRAM_API_KEY": "test-key"})
    def test_from_config_with_custom_language(self, mock_parent_init):
        """Test from_config respects custom language setting."""
        mock_parent_init.return_value = None
        config = MockSTTConfig(provider="deepgram", model="nova-3", language="es")

        DeepgramSTTService.from_config(config)

        mock_parent_init.assert_called_once_with(
            api_key="test-key",
            model="nova-3",
            language="es",
        )

    @patch("specify_cli.voice.services.stt.PipecatDeepgramSTT.__init__")
    def test_init_with_extra_kwargs(self, mock_parent_init):
        """Test initialization passes through extra kwargs."""
        mock_parent_init.return_value = None

        DeepgramSTTService(
            api_key="test-key",
            model="nova-3",
            language="en",
            sample_rate=16000,
            encoding="linear16",
        )

        mock_parent_init.assert_called_once_with(
            api_key="test-key",
            model="nova-3",
            language="en",
            sample_rate=16000,
            encoding="linear16",
        )
