"""Pipecat voice bot pipeline orchestrator.

This module provides the VoiceBot class that assembles and manages
the complete voice pipeline: Transport → STT → Context → LLM → TTS → Transport.
"""

from __future__ import annotations

import asyncio
import logging
import signal
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from pipecat.pipeline.pipeline import Pipeline
    from pipecat.pipeline.runner import PipelineRunner
    from pipecat.pipeline.task import PipelineTask
    from pipecat.transports.base_transport import BaseTransport

    from specify_cli.voice.config import VoiceConfig

from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext

from specify_cli.voice.services.llm import LLMServiceError, OpenAILLMService
from specify_cli.voice.services.stt import DeepgramSTTService, STTServiceError
from specify_cli.voice.services.tts import CartesiaTTSService, TTSServiceError

logger = logging.getLogger(__name__)

# Shutdown timeout in seconds
SHUTDOWN_TIMEOUT = 5.0


class VoiceBotError(Exception):
    """Error raised by VoiceBot operations."""

    def __init__(self, message: str, *, cause: Optional[Exception] = None) -> None:
        """Initialize VoiceBot error.

        Args:
            message: Error description.
            cause: Original exception if wrapping.
        """
        super().__init__(message)
        self.message = message
        self.cause = cause


class VoiceBot:
    """Pipecat voice bot pipeline orchestrator.

    This class assembles and manages the voice pipeline:
    Transport → STT (Deepgram) → Context Aggregator → LLM (OpenAI) → TTS (Cartesia) → Transport

    Example:
        >>> bot = VoiceBot(config, transport=daily_transport)
        >>> await bot.start()  # Runs until stopped or signaled
        >>> await bot.stop()   # Graceful shutdown
    """

    def __init__(
        self,
        config: VoiceConfig,
        *,
        transport: Optional[BaseTransport] = None,
    ) -> None:
        """Initialize VoiceBot.

        Args:
            config: Voice configuration object.
            transport: Optional transport (WebRTC, WebSocket, etc.).

        Raises:
            VoiceBotError: If initialization fails.
        """
        # DEFENSIVE: Validate config
        if config is None:
            raise VoiceBotError("VoiceConfig cannot be None")

        self._config = config
        self._transport = transport
        self._pipeline: Optional[Pipeline] = None
        self._task: Optional[PipelineTask] = None
        self._runner: Optional[PipelineRunner] = None
        self._running = False
        self._shutdown_event = asyncio.Event()

        # Initialize services
        logger.info("Initializing voice services")
        try:
            self._stt = self._create_stt_service()
            logger.info("Pipeline stage: STT initialized")

            self._llm = self._create_llm_service()
            logger.info("Pipeline stage: LLM initialized")

            self._tts = self._create_tts_service()
            logger.info("Pipeline stage: TTS initialized")
        except (STTServiceError, LLMServiceError, TTSServiceError) as e:
            raise VoiceBotError(f"Failed to initialize services: {e}", cause=e) from e

        # Build pipeline
        logger.info("Building Pipecat pipeline")
        self._build_pipeline()

        # Register signal handlers
        self._register_signal_handlers()

    def _create_stt_service(self) -> DeepgramSTTService:
        """Create STT service from config."""
        return DeepgramSTTService.from_config(self._config.pipeline.stt)

    def _create_llm_service(self) -> OpenAILLMService:
        """Create LLM service from config."""
        return OpenAILLMService.from_config(self._config.pipeline.llm)

    def _create_tts_service(self) -> CartesiaTTSService:
        """Create TTS service from config."""
        return CartesiaTTSService.from_config(self._config.pipeline.tts)

    def _build_pipeline(self) -> None:
        """Build the Pipecat pipeline."""
        # Create context with system prompt
        context = OpenAILLMContext(
            messages=[
                {
                    "role": "system",
                    "content": self._config.assistant.system_prompt,
                }
            ]
        )

        # Build processor list
        processors: list[Any] = []

        # Add transport input if available
        if self._transport:
            processors.append(self._transport.input())

        # Core pipeline: STT → Context → LLM → TTS
        processors.extend(
            [
                self._stt,
                context,
                self._llm,
                self._tts,
            ]
        )

        # Add transport output if available
        if self._transport:
            processors.append(self._transport.output())
            logger.info("Pipeline stage: Transport connected")

        # Create pipeline
        self._pipeline = Pipeline(processors)

    def _register_signal_handlers(self) -> None:
        """Register signal handlers for graceful shutdown."""
        try:
            loop = asyncio.get_running_loop()
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, self._handle_signal)
            logger.debug("Signal handlers registered")
        except RuntimeError:
            # Not in async context yet, will register later
            pass

    def _handle_signal(self) -> None:
        """Handle shutdown signals."""
        logger.info("Shutdown signal received")
        self._shutdown_event.set()

    @property
    def is_running(self) -> bool:
        """Return whether the bot is currently running."""
        return self._running

    @property
    def pipeline(self) -> Optional[Pipeline]:
        """Return the pipeline instance."""
        return self._pipeline

    async def start(self) -> None:
        """Start the voice bot pipeline.

        Raises:
            VoiceBotError: If transport is required but not set,
                          or if already running.
        """
        if self._running:
            raise VoiceBotError("VoiceBot is already running")

        if self._transport is None:
            raise VoiceBotError(
                "Transport is required to start the bot. "
                "Provide a transport (Daily, WebSocket, etc.) during initialization."
            )

        logger.info("Starting VoiceBot pipeline")
        self._running = True

        try:
            # Create task and runner
            self._task = PipelineTask(self._pipeline)
            self._runner = PipelineRunner()

            # Run until shutdown
            await self._runner.run(self._task)

        except Exception as e:
            logger.exception("Pipeline error: %s", e)
            raise VoiceBotError(f"Pipeline failed: {e}", cause=e) from e
        finally:
            self._running = False

    async def stop(self) -> None:
        """Stop the voice bot pipeline gracefully.

        Attempts graceful shutdown within SHUTDOWN_TIMEOUT seconds,
        then forces cleanup if needed.
        """
        if not self._running and self._task is None:
            logger.debug("VoiceBot already stopped")
            return

        logger.info("Stopping VoiceBot pipeline")

        try:
            # Cancel with timeout
            async with asyncio.timeout(SHUTDOWN_TIMEOUT):
                await self._cleanup_resources()
        except asyncio.TimeoutError:
            logger.warning("Graceful shutdown timed out, forcing cleanup")
            await self._force_cleanup()

        self._running = False
        logger.info("VoiceBot stopped successfully")

    async def _cleanup_resources(self) -> None:
        """Clean up pipeline resources gracefully."""
        logger.info("Pipeline stage: Cleaning up resources")

        # Cancel pipeline task
        if self._task:
            self._task.cancel()
            self._task = None

        # Close transport
        if self._transport:
            try:
                await self._transport.close()
            except Exception as e:
                logger.warning("Error closing transport: %s", e)

    async def _force_cleanup(self) -> None:
        """Force cleanup when graceful shutdown times out."""
        logger.warning("Forcing resource cleanup")

        self._task = None
        self._runner = None

        if self._transport:
            try:
                await self._transport.close()
            except Exception:
                pass  # Best effort
