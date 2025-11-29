"""Unit tests for VoiceBot pipeline implementation."""

import asyncio
import os
import signal
from unittest.mock import AsyncMock, Mock, patch

import pytest

from specify_cli.voice.bot import VoiceBot
from specify_cli.voice.config import (
    AssistantConfig,
    LLMConfig,
    PipelineConfig,
    STTConfig,
    TTSConfig,
    VoiceConfig,
)
from specify_cli.voice.exceptions import VoiceServiceError


@pytest.fixture(scope="function", autouse=True)
def mock_env_vars():
    """Mock environment variables for all tests."""
    with patch.dict(
        os.environ,
        {
            "DEEPGRAM_API_KEY": "test-deepgram-key",
            "OPENAI_API_KEY": "test-openai-key",
            "CARTESIA_API_KEY": "test-cartesia-key",
            "DAILY_API_KEY": "test-daily-key",
        },
    ):
        yield


@pytest.fixture
def mock_config():
    """Create a mock VoiceConfig for testing."""
    return VoiceConfig(
        assistant=AssistantConfig(
            name="Test Assistant",
            system_prompt="You are a test assistant.",
            first_message="Hello from tests!",
            last_message="Goodbye from tests!",
        ),
        pipeline=PipelineConfig(
            stt=STTConfig(provider="deepgram", model="nova-3", language="en"),
            llm=LLMConfig(
                provider="openai",
                model="gpt-4o",
                temperature=0.7,
                max_tokens=1000,
            ),
            tts=TTSConfig(
                provider="cartesia",
                voice_id="test-voice",
                output_format="pcm_16000",
            ),
        ),
    )


@pytest.fixture
def mock_transport():
    """Create a mock transport for testing."""
    transport = Mock()
    transport.input = Mock(return_value=Mock())
    transport.output = Mock(return_value=Mock())
    return transport


class TestVoiceBotInitialization:
    """Test suite for VoiceBot initialization."""

    @patch("specify_cli.voice.bot.DeepgramSTTService")
    @patch("specify_cli.voice.bot.OpenAILLMService")
    @patch("specify_cli.voice.bot.CartesiaTTSService")
    def test_init_success(
        self, mock_tts, mock_llm, mock_stt, mock_config, mock_transport
    ):
        """Test successful VoiceBot initialization."""
        bot = VoiceBot(mock_config, transport=mock_transport)

        assert bot is not None
        assert bot.config == mock_config
        assert bot.transport == mock_transport
        assert not bot.is_running
        assert bot.pipeline is None  # Not built until start

    @patch("specify_cli.voice.bot.DeepgramSTTService")
    @patch("specify_cli.voice.bot.OpenAILLMService")
    @patch("specify_cli.voice.bot.CartesiaTTSService")
    def test_init_without_transport(self, mock_tts, mock_llm, mock_stt, mock_config):
        """Test VoiceBot initialization without transport (for testing)."""
        bot = VoiceBot(mock_config)

        assert bot is not None
        assert bot.transport is None
        assert not bot.is_running

    @patch("specify_cli.voice.bot.DeepgramSTTService")
    @patch("specify_cli.voice.bot.OpenAILLMService")
    @patch("specify_cli.voice.bot.CartesiaTTSService")
    def test_init_builds_pipeline(self, mock_tts, mock_llm, mock_stt, mock_config):
        """Test that initialization builds the pipeline."""
        VoiceBot(mock_config)

        # Verify services were initialized
        mock_stt.from_config.assert_called_once()
        mock_llm.assert_called_once()
        mock_tts.from_config.assert_called_once()

    @patch("specify_cli.voice.bot.DeepgramSTTService")
    @patch("specify_cli.voice.bot.OpenAILLMService")
    @patch("specify_cli.voice.bot.CartesiaTTSService")
    def test_init_service_failure(self, mock_tts, mock_llm, mock_stt, mock_config):
        """Test initialization fails gracefully when service init fails."""
        mock_stt.from_config.side_effect = Exception("STT initialization failed")

        with pytest.raises(VoiceServiceError) as exc_info:
            VoiceBot(mock_config)

        assert "Failed to initialize voice services" in str(exc_info.value)
        assert exc_info.value.code == "INITIALIZATION_ERROR"

    @patch("specify_cli.voice.bot.DeepgramSTTService")
    @patch("specify_cli.voice.bot.OpenAILLMService")
    @patch("specify_cli.voice.bot.CartesiaTTSService")
    def test_signal_handlers_registered(
        self, mock_tts, mock_llm, mock_stt, mock_config
    ):
        """Test that SIGINT and SIGTERM handlers are registered."""
        with patch("signal.signal") as mock_signal:
            VoiceBot(mock_config)

            # Verify signal handlers were registered
            assert mock_signal.call_count >= 2
            # Check for SIGINT
            calls = [call.args for call in mock_signal.call_args_list]
            sig_nums = [call[0] for call in calls]
            assert signal.SIGINT in sig_nums
            assert signal.SIGTERM in sig_nums


class TestVoiceBotPipeline:
    """Test suite for VoiceBot pipeline assembly."""

    @patch("specify_cli.voice.bot.DeepgramSTTService")
    @patch("specify_cli.voice.bot.OpenAILLMService")
    @patch("specify_cli.voice.bot.CartesiaTTSService")
    @patch("specify_cli.voice.bot.OpenAILLMContext")
    def test_pipeline_assembly(
        self, mock_context, mock_tts, mock_llm, mock_stt, mock_config
    ):
        """Test that pipeline is assembled with correct processors."""
        VoiceBot(mock_config)

        # Verify context was created with system prompt
        mock_context.assert_called_once()
        context_messages = mock_context.call_args[1]["messages"]
        assert len(context_messages) == 1
        assert context_messages[0]["role"] == "system"
        assert context_messages[0]["content"] == mock_config.assistant.system_prompt

    @patch("specify_cli.voice.bot.DeepgramSTTService")
    @patch("specify_cli.voice.bot.OpenAILLMService")
    @patch("specify_cli.voice.bot.CartesiaTTSService")
    def test_pipeline_processors_order(self, mock_tts, mock_llm, mock_stt, mock_config):
        """Test that pipeline processors are in correct order."""
        bot = VoiceBot(mock_config)

        # Verify processors list exists and has correct order
        assert hasattr(bot, "_processors")
        assert len(bot._processors) == 3
        # Order: STT, LLM, TTS
        assert bot._processors[0] == mock_stt.from_config.return_value
        assert bot._processors[1] == mock_llm.return_value
        assert bot._processors[2] == mock_tts.from_config.return_value


class TestVoiceBotLifecycle:
    """Test suite for VoiceBot lifecycle management."""

    @pytest.mark.asyncio
    @patch("specify_cli.voice.bot.DeepgramSTTService")
    @patch("specify_cli.voice.bot.OpenAILLMService")
    @patch("specify_cli.voice.bot.CartesiaTTSService")
    @patch("specify_cli.voice.bot.Pipeline")
    @patch("specify_cli.voice.bot.PipelineTask")
    @patch("specify_cli.voice.bot.PipelineRunner")
    async def test_start_success(
        self,
        mock_runner_class,
        mock_task_class,
        mock_pipeline_class,
        mock_tts,
        mock_llm,
        mock_stt,
        mock_config,
        mock_transport,
    ):
        """Test successful pipeline start."""
        # Setup mocks
        mock_runner = AsyncMock()
        mock_runner_class.return_value = mock_runner
        mock_task = Mock()
        mock_task.queue_frame = AsyncMock()
        mock_task_class.return_value = mock_task

        # Mock runner.run to complete quickly
        async def mock_run(task):
            await asyncio.sleep(0.1)

        mock_runner.run = AsyncMock(side_effect=mock_run)

        bot = VoiceBot(mock_config, transport=mock_transport)

        # Start bot in background and stop it quickly
        start_task = asyncio.create_task(bot.start())
        await asyncio.sleep(0.05)  # Let it start
        await bot.stop()
        await start_task

        # Verify pipeline was created
        mock_pipeline_class.assert_called_once()

    @pytest.mark.asyncio
    @patch("specify_cli.voice.bot.DeepgramSTTService")
    @patch("specify_cli.voice.bot.OpenAILLMService")
    @patch("specify_cli.voice.bot.CartesiaTTSService")
    async def test_start_without_transport(
        self, mock_tts, mock_llm, mock_stt, mock_config
    ):
        """Test that start fails without transport."""
        bot = VoiceBot(mock_config)

        with pytest.raises(RuntimeError) as exc_info:
            await bot.start()

        assert "Cannot start bot without transport" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch("specify_cli.voice.bot.DeepgramSTTService")
    @patch("specify_cli.voice.bot.OpenAILLMService")
    @patch("specify_cli.voice.bot.CartesiaTTSService")
    @patch("specify_cli.voice.bot.Pipeline")
    @patch("specify_cli.voice.bot.PipelineTask")
    @patch("specify_cli.voice.bot.PipelineRunner")
    async def test_start_already_running(
        self,
        mock_runner_class,
        mock_task_class,
        mock_pipeline_class,
        mock_tts,
        mock_llm,
        mock_stt,
        mock_config,
        mock_transport,
    ):
        """Test that start fails if already running."""
        bot = VoiceBot(mock_config, transport=mock_transport)
        bot._running = True  # Simulate already running

        with pytest.raises(RuntimeError) as exc_info:
            await bot.start()

        assert "already running" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch("specify_cli.voice.bot.DeepgramSTTService")
    @patch("specify_cli.voice.bot.OpenAILLMService")
    @patch("specify_cli.voice.bot.CartesiaTTSService")
    async def test_stop_when_not_running(
        self, mock_tts, mock_llm, mock_stt, mock_config
    ):
        """Test that stop is idempotent when not running."""
        bot = VoiceBot(mock_config)

        # Should not raise
        await bot.stop()

    @pytest.mark.asyncio
    @patch("specify_cli.voice.bot.DeepgramSTTService")
    @patch("specify_cli.voice.bot.OpenAILLMService")
    @patch("specify_cli.voice.bot.CartesiaTTSService")
    async def test_stop_cleans_up_resources(
        self, mock_tts, mock_llm, mock_stt, mock_config
    ):
        """Test that stop properly cleans up all resources."""
        bot = VoiceBot(mock_config)

        # Simulate running state
        mock_task = AsyncMock()
        mock_task.cancel = AsyncMock()
        bot._task = mock_task
        bot._running = True

        await bot.stop()

        # Verify cleanup was called
        mock_task.cancel.assert_called_once()
        assert not bot.is_running


class TestVoiceBotSignalHandling:
    """Test suite for signal handling."""

    @pytest.mark.asyncio
    @patch("specify_cli.voice.bot.DeepgramSTTService")
    @patch("specify_cli.voice.bot.OpenAILLMService")
    @patch("specify_cli.voice.bot.CartesiaTTSService")
    @patch("specify_cli.voice.bot.Pipeline")
    @patch("specify_cli.voice.bot.PipelineTask")
    @patch("specify_cli.voice.bot.PipelineRunner")
    async def test_sigint_triggers_shutdown(
        self,
        mock_runner_class,
        mock_task_class,
        mock_pipeline_class,
        mock_tts,
        mock_llm,
        mock_stt,
        mock_config,
        mock_transport,
    ):
        """Test that SIGINT signal triggers graceful shutdown."""
        # Setup mocks
        mock_runner = AsyncMock()
        mock_runner_class.return_value = mock_runner
        mock_task = Mock()
        mock_task.queue_frame = AsyncMock()
        mock_task.cancel = AsyncMock()
        mock_task_class.return_value = mock_task

        # Mock runner to run indefinitely
        async def mock_run(task):
            await asyncio.sleep(10)

        mock_runner.run = AsyncMock(side_effect=mock_run)

        bot = VoiceBot(mock_config, transport=mock_transport)

        # Start bot in background
        start_task = asyncio.create_task(bot.start())
        await asyncio.sleep(0.05)  # Let it start

        # Trigger shutdown event (simulating signal)
        bot._shutdown_event.set()

        # Wait for bot to stop
        await asyncio.wait_for(start_task, timeout=2.0)

        # Verify bot stopped
        assert not bot.is_running

    @pytest.mark.asyncio
    @patch("specify_cli.voice.bot.DeepgramSTTService")
    @patch("specify_cli.voice.bot.OpenAILLMService")
    @patch("specify_cli.voice.bot.CartesiaTTSService")
    async def test_shutdown_timeout_forces_cleanup(
        self, mock_tts, mock_llm, mock_stt, mock_config
    ):
        """Test that shutdown timeout triggers force cleanup."""
        bot = VoiceBot(mock_config)

        # Simulate slow cleanup
        async def slow_cleanup():
            await asyncio.sleep(10)  # Longer than 5s timeout

        # Mock task that won't cancel quickly
        mock_task = AsyncMock()
        mock_task.cancel = AsyncMock(side_effect=slow_cleanup)
        bot._task = mock_task
        bot._running = True

        # Stop should timeout and force cleanup
        await bot.stop()

        # Verify force cleanup was called (task is None)
        assert bot._task is None
        assert not bot.is_running


class TestVoiceBotLogging:
    """Test suite for logging behavior."""

    @patch("specify_cli.voice.bot.DeepgramSTTService")
    @patch("specify_cli.voice.bot.OpenAILLMService")
    @patch("specify_cli.voice.bot.CartesiaTTSService")
    @patch("specify_cli.voice.bot.logger")
    def test_initialization_logging(
        self, mock_logger, mock_tts, mock_llm, mock_stt, mock_config
    ):
        """Test that initialization logs at INFO level."""
        VoiceBot(mock_config)

        # Verify INFO level logs were called
        info_calls = [call for call in mock_logger.info.call_args_list]
        assert len(info_calls) >= 2

        # Check for key log messages
        log_messages = [str(call.args[0]) for call in info_calls]
        assert any("Initializing voice services" in msg for msg in log_messages)
        assert any("initialized successfully" in msg for msg in log_messages)

    @pytest.mark.asyncio
    @patch("specify_cli.voice.bot.DeepgramSTTService")
    @patch("specify_cli.voice.bot.OpenAILLMService")
    @patch("specify_cli.voice.bot.CartesiaTTSService")
    @patch("specify_cli.voice.bot.logger")
    async def test_stop_logging(
        self, mock_logger, mock_tts, mock_llm, mock_stt, mock_config
    ):
        """Test that stop logs pipeline stages at INFO level."""
        bot = VoiceBot(mock_config)
        bot._running = True
        mock_task = AsyncMock()
        mock_task.cancel = AsyncMock()
        bot._task = mock_task

        await bot.stop()

        # Verify INFO level logs for cleanup stages
        info_calls = [call for call in mock_logger.info.call_args_list]
        log_messages = [str(call.args[0]) for call in info_calls]

        # Check for stage transition logs
        assert any("Stopping VoiceBot" in msg for msg in log_messages)
        assert any("stopped successfully" in msg for msg in log_messages)


class TestVoiceBotProperties:
    """Test suite for VoiceBot properties."""

    @patch("specify_cli.voice.bot.DeepgramSTTService")
    @patch("specify_cli.voice.bot.OpenAILLMService")
    @patch("specify_cli.voice.bot.CartesiaTTSService")
    def test_is_running_property(self, mock_tts, mock_llm, mock_stt, mock_config):
        """Test is_running property."""
        bot = VoiceBot(mock_config)

        assert not bot.is_running

        bot._running = True
        assert bot.is_running

        bot._running = False
        assert not bot.is_running

    @patch("specify_cli.voice.bot.DeepgramSTTService")
    @patch("specify_cli.voice.bot.OpenAILLMService")
    @patch("specify_cli.voice.bot.CartesiaTTSService")
    def test_pipeline_property(self, mock_tts, mock_llm, mock_stt, mock_config):
        """Test pipeline property."""
        bot = VoiceBot(mock_config)

        # Initially None
        assert bot.pipeline is None

        # After setting
        mock_pipeline = Mock()
        bot._pipeline = mock_pipeline
        assert bot.pipeline == mock_pipeline
