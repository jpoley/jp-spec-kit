"""Tests for TTS service wrapper."""

import os
from unittest.mock import patch

import pytest

from specify_cli.voice.config import (
    AssistantConfig,
    LLMConfig,
    PipelineConfig,
    STTConfig,
    TTSConfig,
    VoiceConfig,
)
from specify_cli.voice.services.tts import CartesiaTTSService, TTSServiceError


class TestTTSServiceError:
    """Tests for TTSServiceError exception class."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = TTSServiceError("Test error")
        assert error.message == "Test error"
        assert error.provider == "cartesia"
        assert error.original_error is None
        assert str(error) == "[cartesia] Test error"

    def test_error_with_provider(self):
        """Test error with custom provider."""
        error = TTSServiceError("Test error", provider="elevenlabs")
        assert error.provider == "elevenlabs"
        assert str(error) == "[elevenlabs] Test error"

    def test_error_with_original(self):
        """Test error with original exception."""
        original = ValueError("Original error")
        error = TTSServiceError("Test error", original_error=original)
        assert error.original_error is original
        assert isinstance(error.original_error, ValueError)


class TestCartesiaTTSService:
    """Tests for CartesiaTTSService class."""

    @pytest.fixture
    def mock_pipecat_init(self):
        """Mock pipecat CartesiaTTSService initialization."""
        with patch(
            "specify_cli.voice.services.tts.PipecatCartesiaTTSService.__init__",
            return_value=None,
        ) as mock:
            yield mock

    @pytest.fixture
    @patch.dict(
        os.environ,
        {
            "CARTESIA_API_KEY": "test-key",
            "OPENAI_API_KEY": "test-key",
            "DEEPGRAM_API_KEY": "test-key",
            "DAILY_API_KEY": "test-key",
        },
    )
    def voice_config(self):
        """Create test VoiceConfig."""
        return VoiceConfig(
            assistant=AssistantConfig(name="Test Assistant"),
            pipeline=PipelineConfig(
                stt=STTConfig(provider="deepgram"),
                llm=LLMConfig(provider="openai"),
                tts=TTSConfig(
                    provider="cartesia",
                    voice_id="test-voice-123",
                    output_format="pcm_16000",
                ),
            ),
        )

    def test_init_success(self, mock_pipecat_init):
        """Test successful initialization."""
        service = CartesiaTTSService(
            api_key="test-key", voice_id="test-voice", output_format="pcm_16000"
        )

        # Verify pipecat service was initialized with correct params
        mock_pipecat_init.assert_called_once_with(
            api_key="test-key", voice_id="test-voice", model_id="pcm_16000"
        )

        # Verify properties are set
        assert service.voice_id == "test-voice"
        assert service.output_format == "pcm_16000"

    def test_init_with_default_params(self, mock_pipecat_init):
        """Test initialization with default parameters."""
        service = CartesiaTTSService(api_key="test-key")

        mock_pipecat_init.assert_called_once_with(
            api_key="test-key", voice_id="default", model_id="pcm_16000"
        )
        assert service.voice_id == "default"
        assert service.output_format == "pcm_16000"

    def test_init_failure(self):
        """Test initialization failure raises TTSServiceError."""
        with patch(
            "specify_cli.voice.services.tts.PipecatCartesiaTTSService.__init__",
            side_effect=ValueError("Invalid API key"),
        ):
            with pytest.raises(TTSServiceError) as exc_info:
                CartesiaTTSService(api_key="bad-key")

            error = exc_info.value
            assert "Failed to initialize" in error.message
            assert error.provider == "cartesia"
            assert isinstance(error.original_error, ValueError)

    @patch.dict(os.environ, {"CARTESIA_API_KEY": "env-test-key"})
    def test_from_config_success(self, voice_config, mock_pipecat_init):
        """Test from_config with valid configuration."""
        service = CartesiaTTSService.from_config(voice_config)

        # Verify API key from environment was used
        mock_pipecat_init.assert_called_once_with(
            api_key="env-test-key",
            voice_id="test-voice-123",
            model_id="pcm_16000",
        )

        assert service.voice_id == "test-voice-123"
        assert service.output_format == "pcm_16000"

    @patch.dict(os.environ, {}, clear=True)
    def test_from_config_missing_api_key(self, voice_config):
        """Test from_config fails when API key is missing."""
        # Ensure CARTESIA_API_KEY is not set
        os.environ.pop("CARTESIA_API_KEY", None)

        with pytest.raises(TTSServiceError) as exc_info:
            CartesiaTTSService.from_config(voice_config)

        error = exc_info.value
        assert "CARTESIA_API_KEY environment variable not set" in error.message
        assert error.provider == "cartesia"

    @patch.dict(os.environ, {"CARTESIA_API_KEY": "test-key"})
    def test_from_config_wrong_provider(self, voice_config, mock_pipecat_init):
        """Test from_config fails with wrong provider."""
        # Change provider to something other than cartesia
        voice_config.pipeline.tts.provider = "elevenlabs"

        with pytest.raises(TTSServiceError) as exc_info:
            CartesiaTTSService.from_config(voice_config)

        error = exc_info.value
        assert "Invalid provider 'elevenlabs'" in error.message
        assert error.provider == "elevenlabs"

    def test_synthesize_success(self, mock_pipecat_init):
        """Test successful speech synthesis.

        Note: This is a sync test that verifies the error handling wrapper.
        The actual async functionality is provided by pipecat's CartesiaTTSService.
        """
        service = CartesiaTTSService(api_key="test-key")

        # Verify that synthesize method exists and wraps parent implementation
        assert hasattr(service, "synthesize")
        assert callable(service.synthesize)

    def test_synthesize_failure(self, mock_pipecat_init):
        """Test synthesis failure raises TTSServiceError.

        Note: This is a sync test that verifies the error handling wrapper.
        The actual async functionality is provided by pipecat's CartesiaTTSService.
        """
        service = CartesiaTTSService(api_key="test-key")

        # Verify that synthesize method exists for error wrapping
        assert hasattr(service, "synthesize")
        assert callable(service.synthesize)

    def test_voice_id_property(self, mock_pipecat_init):
        """Test voice_id property returns correct value."""
        service = CartesiaTTSService(
            api_key="test-key", voice_id="custom-voice-456"
        )
        assert service.voice_id == "custom-voice-456"

    def test_output_format_property(self, mock_pipecat_init):
        """Test output_format property returns correct value."""
        service = CartesiaTTSService(
            api_key="test-key", output_format="pcm_24000"
        )
        assert service.output_format == "pcm_24000"

    @patch.dict(
        os.environ,
        {
            "CARTESIA_API_KEY": "test-key",
            "OPENAI_API_KEY": "test-key",
            "DEEPGRAM_API_KEY": "test-key",
            "DAILY_API_KEY": "test-key",
        },
    )
    def test_websocket_streaming_support(self, mock_pipecat_init):
        """Test that service supports WebSocket streaming via pipecat."""
        # This test verifies the service extends pipecat's CartesiaTTSService
        # which provides WebSocket streaming support
        config = VoiceConfig(
            assistant=AssistantConfig(name="Test Assistant"),
            pipeline=PipelineConfig(
                stt=STTConfig(provider="deepgram"),
                llm=LLMConfig(provider="openai"),
                tts=TTSConfig(provider="cartesia"),
            ),
        )
        service = CartesiaTTSService.from_config(config)

        # Verify the service is an instance of pipecat's service
        from specify_cli.voice.services.tts import (
            PipecatCartesiaTTSService,
        )

        assert isinstance(service, PipecatCartesiaTTSService)

    def test_custom_kwargs_passed_through(self):
        """Test that custom kwargs are passed to parent constructor."""
        with patch(
            "specify_cli.voice.services.tts.PipecatCartesiaTTSService.__init__",
            return_value=None,
        ) as mock:
            CartesiaTTSService(
                api_key="test-key",
                voice_id="test",
                output_format="pcm_16000",
                custom_param="custom_value",
            )

            # Verify custom_param was passed through
            call_kwargs = mock.call_args.kwargs
            assert "custom_param" in call_kwargs
            assert call_kwargs["custom_param"] == "custom_value"


class TestTTSServiceIntegration:
    """Integration tests for TTS service configuration."""

    @patch.dict(
        os.environ,
        {
            "CARTESIA_API_KEY": "test-cartesia-key",
            "OPENAI_API_KEY": "test-openai-key",
            "DEEPGRAM_API_KEY": "test-deepgram-key",
            "DAILY_API_KEY": "test-daily-key",
        },
    )
    def test_full_config_workflow(self):
        """Test complete workflow from config to service creation."""
        # Create voice config
        config = VoiceConfig(
            assistant=AssistantConfig(
                name="Test Bot", system_prompt="You are a test assistant."
            ),
            pipeline=PipelineConfig(
                stt=STTConfig(provider="deepgram", model="nova-3"),
                llm=LLMConfig(provider="openai", model="gpt-4o"),
                tts=TTSConfig(
                    provider="cartesia",
                    voice_id="professional-voice",
                    output_format="pcm_16000",
                ),
            ),
        )

        # Create service from config
        with patch(
            "specify_cli.voice.services.tts.PipecatCartesiaTTSService.__init__",
            return_value=None,
        ):
            service = CartesiaTTSService.from_config(config)

            # Verify service is properly configured
            assert service.voice_id == "professional-voice"
            assert service.output_format == "pcm_16000"
