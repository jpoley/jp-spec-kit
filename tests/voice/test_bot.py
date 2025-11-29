"""Tests for VoiceBot pipeline orchestrator."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from specify_cli.voice.bot import VoiceBot, VoiceBotError


@pytest.fixture
def mock_config() -> MagicMock:
    """Create a mock VoiceConfig."""
    config = MagicMock()
    config.assistant.name = "Test Bot"
    config.assistant.system_prompt = "You are a test assistant."
    config.pipeline.stt.provider = "deepgram"
    config.pipeline.stt.model = "nova-3"
    config.pipeline.stt.language = "en"
    config.pipeline.llm.provider = "openai"
    config.pipeline.llm.model = "gpt-4o"
    config.pipeline.llm.temperature = 0.7
    config.pipeline.llm.max_tokens = 1000
    config.pipeline.tts.provider = "cartesia"
    config.pipeline.tts.voice_id = "default"
    config.pipeline.tts.output_format = "pcm_16000"
    return config


@pytest.fixture
def mock_transport() -> MagicMock:
    """Create a mock transport."""
    transport = MagicMock()
    transport.input.return_value = MagicMock()
    transport.output.return_value = MagicMock()
    transport.close = AsyncMock()
    return transport


class TestVoiceBotError:
    """Tests for VoiceBotError exception."""

    def test_error_basic(self) -> None:
        """Test error with message only."""
        error = VoiceBotError("Test error")
        assert error.message == "Test error"
        assert error.cause is None

    def test_error_with_cause(self) -> None:
        """Test error with cause."""
        cause = ValueError("Original")
        error = VoiceBotError("Wrapped", cause=cause)
        assert error.cause is cause


class TestVoiceBotInit:
    """Tests for VoiceBot initialization."""

    @patch("specify_cli.voice.bot.Pipeline")
    @patch("specify_cli.voice.bot.OpenAILLMContext")
    @patch("specify_cli.voice.bot.DeepgramSTTService.from_config")
    @patch("specify_cli.voice.bot.OpenAILLMService.from_config")
    @patch("specify_cli.voice.bot.CartesiaTTSService.from_config")
    def test_init_success(
        self,
        mock_tts: MagicMock,
        mock_llm: MagicMock,
        mock_stt: MagicMock,
        mock_context: MagicMock,
        mock_pipeline: MagicMock,
        mock_config: MagicMock,
        mock_transport: MagicMock,
    ) -> None:
        """Test successful initialization."""
        mock_stt.return_value = MagicMock()
        mock_llm.return_value = MagicMock()
        mock_tts.return_value = MagicMock()

        bot = VoiceBot(mock_config, transport=mock_transport)

        assert bot.is_running is False
        assert bot.pipeline is not None
        mock_stt.assert_called_once()
        mock_llm.assert_called_once()
        mock_tts.assert_called_once()

    @patch("specify_cli.voice.bot.Pipeline")
    @patch("specify_cli.voice.bot.OpenAILLMContext")
    @patch("specify_cli.voice.bot.DeepgramSTTService.from_config")
    @patch("specify_cli.voice.bot.OpenAILLMService.from_config")
    @patch("specify_cli.voice.bot.CartesiaTTSService.from_config")
    def test_init_without_transport(
        self,
        mock_tts: MagicMock,
        mock_llm: MagicMock,
        mock_stt: MagicMock,
        mock_context: MagicMock,
        mock_pipeline: MagicMock,
        mock_config: MagicMock,
    ) -> None:
        """Test initialization without transport."""
        mock_stt.return_value = MagicMock()
        mock_llm.return_value = MagicMock()
        mock_tts.return_value = MagicMock()

        bot = VoiceBot(mock_config)

        assert bot.pipeline is not None
        assert bot._transport is None

    def test_init_with_none_config(self) -> None:
        """Test initialization fails with None config."""
        with pytest.raises(VoiceBotError) as exc_info:
            VoiceBot(None)  # type: ignore[arg-type]
        assert "cannot be None" in str(exc_info.value)

    @patch("specify_cli.voice.bot.DeepgramSTTService.from_config")
    def test_init_stt_failure(
        self,
        mock_stt: MagicMock,
        mock_config: MagicMock,
    ) -> None:
        """Test initialization fails when STT service fails."""
        from specify_cli.voice.services.stt import STTServiceError

        mock_stt.side_effect = STTServiceError("STT failed")

        with pytest.raises(VoiceBotError) as exc_info:
            VoiceBot(mock_config)
        assert "Failed to initialize" in str(exc_info.value)

    @patch("specify_cli.voice.bot.DeepgramSTTService.from_config")
    @patch("specify_cli.voice.bot.OpenAILLMService.from_config")
    def test_init_llm_failure(
        self,
        mock_llm: MagicMock,
        mock_stt: MagicMock,
        mock_config: MagicMock,
    ) -> None:
        """Test initialization fails when LLM service fails."""
        from specify_cli.voice.services.llm import LLMServiceError

        mock_stt.return_value = MagicMock()
        mock_llm.side_effect = LLMServiceError("LLM failed")

        with pytest.raises(VoiceBotError) as exc_info:
            VoiceBot(mock_config)
        assert "Failed to initialize" in str(exc_info.value)


class TestVoiceBotLifecycle:
    """Tests for VoiceBot start/stop lifecycle."""

    @patch("specify_cli.voice.bot.Pipeline")
    @patch("specify_cli.voice.bot.OpenAILLMContext")
    @patch("specify_cli.voice.bot.DeepgramSTTService.from_config")
    @patch("specify_cli.voice.bot.OpenAILLMService.from_config")
    @patch("specify_cli.voice.bot.CartesiaTTSService.from_config")
    @pytest.mark.asyncio
    async def test_start_without_transport(
        self,
        mock_tts: MagicMock,
        mock_llm: MagicMock,
        mock_stt: MagicMock,
        mock_context: MagicMock,
        mock_pipeline: MagicMock,
        mock_config: MagicMock,
    ) -> None:
        """Test start fails without transport."""
        mock_stt.return_value = MagicMock()
        mock_llm.return_value = MagicMock()
        mock_tts.return_value = MagicMock()

        bot = VoiceBot(mock_config)

        with pytest.raises(VoiceBotError) as exc_info:
            await bot.start()
        assert "Transport is required" in str(exc_info.value)

    @patch("specify_cli.voice.bot.Pipeline")
    @patch("specify_cli.voice.bot.OpenAILLMContext")
    @patch("specify_cli.voice.bot.DeepgramSTTService.from_config")
    @patch("specify_cli.voice.bot.OpenAILLMService.from_config")
    @patch("specify_cli.voice.bot.CartesiaTTSService.from_config")
    @pytest.mark.asyncio
    async def test_start_already_running(
        self,
        mock_tts: MagicMock,
        mock_llm: MagicMock,
        mock_stt: MagicMock,
        mock_context: MagicMock,
        mock_pipeline: MagicMock,
        mock_config: MagicMock,
        mock_transport: MagicMock,
    ) -> None:
        """Test start fails when already running."""
        mock_stt.return_value = MagicMock()
        mock_llm.return_value = MagicMock()
        mock_tts.return_value = MagicMock()

        bot = VoiceBot(mock_config, transport=mock_transport)
        bot._running = True  # Simulate already running

        with pytest.raises(VoiceBotError) as exc_info:
            await bot.start()
        assert "already running" in str(exc_info.value)

    @patch("specify_cli.voice.bot.Pipeline")
    @patch("specify_cli.voice.bot.OpenAILLMContext")
    @patch("specify_cli.voice.bot.DeepgramSTTService.from_config")
    @patch("specify_cli.voice.bot.OpenAILLMService.from_config")
    @patch("specify_cli.voice.bot.CartesiaTTSService.from_config")
    @pytest.mark.asyncio
    async def test_stop_when_not_running(
        self,
        mock_tts: MagicMock,
        mock_llm: MagicMock,
        mock_stt: MagicMock,
        mock_context: MagicMock,
        mock_pipeline: MagicMock,
        mock_config: MagicMock,
    ) -> None:
        """Test stop is safe when not running."""
        mock_stt.return_value = MagicMock()
        mock_llm.return_value = MagicMock()
        mock_tts.return_value = MagicMock()

        bot = VoiceBot(mock_config)

        # Should not raise
        await bot.stop()

    @patch("specify_cli.voice.bot.Pipeline")
    @patch("specify_cli.voice.bot.OpenAILLMContext")
    @patch("specify_cli.voice.bot.DeepgramSTTService.from_config")
    @patch("specify_cli.voice.bot.OpenAILLMService.from_config")
    @patch("specify_cli.voice.bot.CartesiaTTSService.from_config")
    @pytest.mark.asyncio
    async def test_stop_cleans_up_transport(
        self,
        mock_tts: MagicMock,
        mock_llm: MagicMock,
        mock_stt: MagicMock,
        mock_context: MagicMock,
        mock_pipeline: MagicMock,
        mock_config: MagicMock,
        mock_transport: MagicMock,
    ) -> None:
        """Test stop cleans up transport."""
        mock_stt.return_value = MagicMock()
        mock_llm.return_value = MagicMock()
        mock_tts.return_value = MagicMock()

        bot = VoiceBot(mock_config, transport=mock_transport)
        bot._running = True
        bot._task = MagicMock()
        bot._task.cancel = MagicMock()

        await bot.stop()

        mock_transport.close.assert_called_once()
        assert bot.is_running is False


class TestVoiceBotProperties:
    """Tests for VoiceBot properties."""

    @patch("specify_cli.voice.bot.Pipeline")
    @patch("specify_cli.voice.bot.OpenAILLMContext")
    @patch("specify_cli.voice.bot.DeepgramSTTService.from_config")
    @patch("specify_cli.voice.bot.OpenAILLMService.from_config")
    @patch("specify_cli.voice.bot.CartesiaTTSService.from_config")
    def test_is_running_property(
        self,
        mock_tts: MagicMock,
        mock_llm: MagicMock,
        mock_stt: MagicMock,
        mock_context: MagicMock,
        mock_pipeline: MagicMock,
        mock_config: MagicMock,
    ) -> None:
        """Test is_running property."""
        mock_stt.return_value = MagicMock()
        mock_llm.return_value = MagicMock()
        mock_tts.return_value = MagicMock()

        bot = VoiceBot(mock_config)

        assert bot.is_running is False
        bot._running = True
        assert bot.is_running is True

    @patch("specify_cli.voice.bot.Pipeline")
    @patch("specify_cli.voice.bot.OpenAILLMContext")
    @patch("specify_cli.voice.bot.DeepgramSTTService.from_config")
    @patch("specify_cli.voice.bot.OpenAILLMService.from_config")
    @patch("specify_cli.voice.bot.CartesiaTTSService.from_config")
    def test_pipeline_property(
        self,
        mock_tts: MagicMock,
        mock_llm: MagicMock,
        mock_stt: MagicMock,
        mock_context: MagicMock,
        mock_pipeline: MagicMock,
        mock_config: MagicMock,
    ) -> None:
        """Test pipeline property."""
        mock_stt.return_value = MagicMock()
        mock_llm.return_value = MagicMock()
        mock_tts.return_value = MagicMock()

        bot = VoiceBot(mock_config)

        assert bot.pipeline is not None


class TestVoiceBotLogging:
    """Tests for VoiceBot logging."""

    @patch("specify_cli.voice.bot.Pipeline")
    @patch("specify_cli.voice.bot.OpenAILLMContext")
    @patch("specify_cli.voice.bot.DeepgramSTTService.from_config")
    @patch("specify_cli.voice.bot.OpenAILLMService.from_config")
    @patch("specify_cli.voice.bot.CartesiaTTSService.from_config")
    def test_init_logs_stages(
        self,
        mock_tts: MagicMock,
        mock_llm: MagicMock,
        mock_stt: MagicMock,
        mock_context: MagicMock,
        mock_pipeline: MagicMock,
        mock_config: MagicMock,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test initialization logs pipeline stages."""
        mock_stt.return_value = MagicMock()
        mock_llm.return_value = MagicMock()
        mock_tts.return_value = MagicMock()

        import logging

        with caplog.at_level(logging.INFO):
            VoiceBot(mock_config)

        log_messages = [record.message for record in caplog.records]
        assert any("Initializing voice services" in msg for msg in log_messages)
        assert any("STT initialized" in msg for msg in log_messages)
        assert any("LLM initialized" in msg for msg in log_messages)
        assert any("TTS initialized" in msg for msg in log_messages)
        assert any("Building Pipecat pipeline" in msg for msg in log_messages)
