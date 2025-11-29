"""Tests for Cartesia TTS service wrapper."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from specify_cli.voice.services.tts import CartesiaTTSService, TTSServiceError


class TestTTSServiceError:
    """Tests for TTSServiceError exception."""

    def test_error_basic(self) -> None:
        """Test error with message only."""
        error = TTSServiceError("Test error")
        assert error.message == "Test error"
        assert error.provider == "cartesia"
        assert error.original_error is None
        assert str(error) == "[cartesia] Test error"

    def test_error_with_provider(self) -> None:
        """Test error with custom provider."""
        error = TTSServiceError("Test error", provider="elevenlabs")
        assert error.provider == "elevenlabs"
        assert str(error) == "[elevenlabs] Test error"

    def test_error_with_original_error(self) -> None:
        """Test error with original exception."""
        original = ValueError("Original")
        error = TTSServiceError("Wrapped", original_error=original)
        assert error.original_error is original


class TestCartesiaTTSServiceInit:
    """Tests for CartesiaTTSService initialization."""

    @patch("specify_cli.voice.services.tts.PipecatCartesiaTTS.__init__")
    def test_init_with_valid_api_key(self, mock_init: MagicMock) -> None:
        """Test initialization with valid API key and voice_id."""
        mock_init.return_value = None
        service = CartesiaTTSService(api_key="valid-key", voice_id="test-voice")
        assert service.voice_id == "test-voice"
        assert service.model == "sonic-3"
        assert service.sample_rate == 16000
        assert service.encoding == "pcm_s16le"
        mock_init.assert_called_once()

    @patch("specify_cli.voice.services.tts.PipecatCartesiaTTS.__init__")
    def test_init_with_custom_voice_id(self, mock_init: MagicMock) -> None:
        """Test initialization with custom voice ID."""
        mock_init.return_value = None
        service = CartesiaTTSService(api_key="key", voice_id="custom-voice")
        assert service.voice_id == "custom-voice"

    @patch("specify_cli.voice.services.tts.PipecatCartesiaTTS.__init__")
    def test_init_with_custom_sample_rate(self, mock_init: MagicMock) -> None:
        """Test initialization with custom sample rate."""
        mock_init.return_value = None
        service = CartesiaTTSService(api_key="key", voice_id="voice", sample_rate=24000)
        assert service.sample_rate == 24000

    @patch("specify_cli.voice.services.tts.PipecatCartesiaTTS.__init__")
    def test_init_with_custom_model(self, mock_init: MagicMock) -> None:
        """Test initialization with custom model."""
        mock_init.return_value = None
        service = CartesiaTTSService(api_key="key", voice_id="voice", model="sonic-2")
        assert service.model == "sonic-2"

    def test_init_without_api_key(self) -> None:
        """Test initialization fails without API key."""
        with pytest.raises(TTSServiceError) as exc_info:
            CartesiaTTSService(api_key="", voice_id="voice")
        assert "API key is required" in str(exc_info.value)

    def test_init_with_none_api_key(self) -> None:
        """Test initialization fails with None API key."""
        with pytest.raises(TTSServiceError) as exc_info:
            CartesiaTTSService(api_key=None, voice_id="voice")  # type: ignore[arg-type]
        assert "API key is required" in str(exc_info.value)

    def test_init_with_whitespace_api_key(self) -> None:
        """Test initialization fails with whitespace API key."""
        with pytest.raises(TTSServiceError) as exc_info:
            CartesiaTTSService(api_key="   ", voice_id="voice")
        assert "cannot be empty or whitespace" in str(exc_info.value)

    def test_init_with_non_string_api_key(self) -> None:
        """Test initialization fails with non-string API key."""
        with pytest.raises(TTSServiceError) as exc_info:
            CartesiaTTSService(api_key=12345, voice_id="voice")  # type: ignore[arg-type]
        assert "must be a string" in str(exc_info.value)

    def test_init_without_voice_id(self) -> None:
        """Test initialization fails without voice_id."""
        with pytest.raises(TTSServiceError) as exc_info:
            CartesiaTTSService(api_key="valid-key", voice_id="")
        assert "Voice ID is required" in str(exc_info.value)

    @patch("specify_cli.voice.services.tts.PipecatCartesiaTTS.__init__")
    def test_init_handles_parent_exception(self, mock_init: MagicMock) -> None:
        """Test that parent initialization errors are wrapped."""
        mock_init.side_effect = Exception("Connection failed")
        with pytest.raises(TTSServiceError) as exc_info:
            CartesiaTTSService(api_key="valid-key", voice_id="voice")
        assert "Failed to initialize" in str(exc_info.value)
        assert exc_info.value.original_error is not None


class TestCartesiaTTSServiceFromConfig:
    """Tests for CartesiaTTSService.from_config."""

    @patch("specify_cli.voice.services.tts.PipecatCartesiaTTS.__init__")
    @patch.dict("os.environ", {"CARTESIA_API_KEY": "test-key"})
    def test_from_config_success(self, mock_init: MagicMock) -> None:
        """Test creating service from config."""
        mock_init.return_value = None
        config = MagicMock()
        config.provider = "cartesia"
        config.voice_id = "my-voice"
        config.output_format = "pcm_16000"

        service = CartesiaTTSService.from_config(config)
        assert service.voice_id == "my-voice"
        assert service.sample_rate == 16000

    @patch("specify_cli.voice.services.tts.PipecatCartesiaTTS.__init__")
    @patch.dict("os.environ", {"CARTESIA_API_KEY": "test-key"})
    def test_from_config_parses_sample_rate(self, mock_init: MagicMock) -> None:
        """Test from_config parses sample rate from output_format."""
        mock_init.return_value = None
        config = MagicMock()
        config.provider = "cartesia"
        config.voice_id = "my-voice"
        config.output_format = "pcm_24000"

        service = CartesiaTTSService.from_config(config)
        assert service.sample_rate == 24000

    def test_from_config_none(self) -> None:
        """Test from_config fails with None config."""
        with pytest.raises(TTSServiceError) as exc_info:
            CartesiaTTSService.from_config(None)  # type: ignore[arg-type]
        assert "cannot be None" in str(exc_info.value)

    def test_from_config_wrong_provider(self) -> None:
        """Test from_config fails with wrong provider."""
        config = MagicMock()
        config.provider = "elevenlabs"

        with pytest.raises(TTSServiceError) as exc_info:
            CartesiaTTSService.from_config(config)
        assert "Expected provider 'cartesia'" in str(exc_info.value)

    @patch.dict("os.environ", {}, clear=True)
    def test_from_config_missing_env_key(self) -> None:
        """Test from_config fails when env key is missing."""
        import os

        os.environ.pop("CARTESIA_API_KEY", None)

        config = MagicMock()
        config.provider = "cartesia"
        config.voice_id = "default"
        config.output_format = "pcm_16000"

        with pytest.raises(TTSServiceError) as exc_info:
            CartesiaTTSService.from_config(config)
        assert "not set" in str(exc_info.value)
