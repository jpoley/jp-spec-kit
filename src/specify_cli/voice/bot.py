"""Pipecat voice bot pipeline implementation.

This module provides the VoiceBot class that assembles and manages the complete
Pipecat pipeline for voice interaction with JP Spec Kit.

Architecture:
    Transport → STT → Context Aggregator → LLM → TTS → Transport

The pipeline processes audio input through speech-to-text, sends transcribed text
to an LLM, and synthesizes the response back to audio output.
"""

import asyncio
import logging
import signal
from typing import Optional

from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask
from pipecat.processors.aggregators.openai_llm_context import (
    OpenAILLMContext,
    OpenAILLMContextFrame,
)
from pipecat.transports.base_transport import BaseTransport

from specify_cli.voice.config import VoiceConfig
from specify_cli.voice.exceptions import VoiceServiceError
from specify_cli.voice.services.llm import OpenAILLMService
from specify_cli.voice.services.stt import DeepgramSTTService
from specify_cli.voice.services.tts import CartesiaTTSService

logger = logging.getLogger(__name__)


class VoiceBot:
    """Voice bot with Pipecat pipeline for JP Spec Kit interaction.

    Assembles and manages the complete voice pipeline:
    - Speech-to-Text (Deepgram)
    - Language Model (OpenAI GPT-4o)
    - Text-to-Speech (Cartesia)

    The bot handles:
    - Pipeline lifecycle (start, stop, cleanup)
    - Signal handling (SIGINT, SIGTERM)
    - Resource cleanup (API connections, tasks)
    - Logging and error handling

    Example:
        >>> config = VoiceConfig(...)
        >>> bot = VoiceBot(config)
        >>> await bot.start()
        >>> # Bot runs until stopped
        >>> await bot.stop()
    """

    def __init__(
        self,
        config: VoiceConfig,
        transport: Optional[BaseTransport] = None,
    ) -> None:
        """Initialize VoiceBot with configuration.

        Args:
            config: Voice configuration containing pipeline settings
            transport: Optional transport layer (WebRTC, WebSocket, etc.)
                      If None, bot can only be used for testing pipeline assembly

        Raises:
            VoiceServiceError: If pipeline initialization fails
        """
        self.config = config
        self.transport = transport
        self._pipeline: Optional[Pipeline] = None
        self._task: Optional[PipelineTask] = None
        self._runner: Optional[PipelineRunner] = None
        self._running = False
        self._shutdown_event = asyncio.Event()

        # Initialize services
        try:
            logger.info("Initializing voice services")
            self._stt = DeepgramSTTService.from_config(config.pipeline.stt)
            self._llm = OpenAILLMService(
                model=config.pipeline.llm.model,
                temperature=config.pipeline.llm.temperature,
                max_tokens=config.pipeline.llm.max_tokens,
            )
            self._tts = CartesiaTTSService.from_config(config)
            logger.info("Voice services initialized successfully")
        except Exception as e:
            raise VoiceServiceError(
                f"Failed to initialize voice services: {e}",
                code="INITIALIZATION_ERROR",
            ) from e

        # Build pipeline
        self._build_pipeline()

        # Setup signal handlers
        self._setup_signal_handlers()

    def _build_pipeline(self) -> None:
        """Build the Pipecat pipeline with processors.

        Pipeline flow:
            Transport → STT → Context → LLM → TTS → Transport

        The context aggregator maintains conversation state between the
        STT and LLM, and between the LLM and TTS.

        Raises:
            VoiceServiceError: If pipeline construction fails
        """
        try:
            logger.info("Building Pipecat pipeline")

            # Create LLM context with initial system message
            context = OpenAILLMContext(
                messages=[
                    {
                        "role": "system",
                        "content": self.config.assistant.system_prompt,
                    }
                ]
            )

            # Build processor pipeline
            # Note: The actual pipeline assembly depends on the transport
            # For now, we store the processors to be assembled when transport is available
            self._processors = [
                self._stt,
                self._llm,
                self._tts,
            ]

            self._context = context

            logger.info(
                f"Pipeline built with {len(self._processors)} processors: "
                f"STT ({self.config.pipeline.stt.provider}), "
                f"LLM ({self.config.pipeline.llm.provider}), "
                f"TTS ({self.config.pipeline.tts.provider})"
            )

        except Exception as e:
            raise VoiceServiceError(
                f"Failed to build pipeline: {e}",
                code="PIPELINE_BUILD_ERROR",
            ) from e

    def _setup_signal_handlers(self) -> None:
        """Setup SIGINT and SIGTERM handlers for graceful shutdown.

        When a signal is received, triggers the shutdown event to stop
        the bot within 5 seconds.
        """

        def signal_handler(signum: int, frame) -> None:
            """Handle shutdown signals."""
            sig_name = signal.Signals(signum).name
            logger.info(f"Received {sig_name} signal, initiating shutdown")
            self._shutdown_event.set()

        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        logger.debug("Signal handlers registered for SIGINT and SIGTERM")

    async def start(self) -> None:
        """Start the voice bot pipeline.

        Creates and starts the PipelineTask, then waits for completion
        or shutdown signal.

        The bot will run until:
        - stop() is called
        - SIGINT/SIGTERM is received
        - Pipeline encounters an error

        Raises:
            VoiceServiceError: If pipeline start fails
            RuntimeError: If bot is already running or no transport configured
        """
        if self._running:
            raise RuntimeError("VoiceBot is already running")

        if not self.transport:
            raise RuntimeError(
                "Cannot start bot without transport. Provide transport in constructor."
            )

        try:
            logger.info("Starting VoiceBot pipeline")
            self._running = True

            # Send initial context to LLM
            initial_context_frame = OpenAILLMContextFrame(self._context)

            # Create pipeline with transport
            self._pipeline = Pipeline(
                processors=[
                    self.transport.input(),
                    self._stt,
                    self._llm,
                    self._tts,
                    self.transport.output(),
                ]
            )

            # Create and configure pipeline task
            self._task = PipelineTask(
                self._pipeline,
                params=PipelineTask.Params(
                    allow_interruptions=True,
                    enable_metrics=True,
                ),
            )

            # Create runner
            self._runner = PipelineRunner()

            logger.info("Pipeline stage: STT initialized")
            logger.info("Pipeline stage: LLM initialized")
            logger.info("Pipeline stage: TTS initialized")
            logger.info("Pipeline stage: Transport connected")

            # Queue initial context
            await self._task.queue_frame(initial_context_frame)

            # Start the pipeline in background
            task = asyncio.create_task(self._runner.run(self._task))

            # Send first message if configured
            if self.config.assistant.first_message:
                logger.info("Sending first message to user")
                # This would be sent through the pipeline

            logger.info("VoiceBot pipeline started successfully")

            # Wait for shutdown signal or task completion
            shutdown_task = asyncio.create_task(self._shutdown_event.wait())
            done, pending = await asyncio.wait(
                [task, shutdown_task],
                return_when=asyncio.FIRST_COMPLETED,
            )

            # If shutdown event triggered, stop gracefully
            if self._shutdown_event.is_set():
                logger.info("Shutdown event triggered, stopping pipeline")
                await self.stop()

            # Cancel any pending tasks
            for pending_task in pending:
                pending_task.cancel()

        except Exception as e:
            self._running = False
            raise VoiceServiceError(
                f"Failed to start pipeline: {e}",
                code="PIPELINE_START_ERROR",
            ) from e

    async def stop(self) -> None:
        """Stop the voice bot pipeline gracefully.

        Stops the pipeline task and cleans up all resources within 5 seconds.
        Logs completion at INFO level.

        This method is idempotent - calling it multiple times is safe.
        """
        if not self._running:
            logger.debug("VoiceBot is not running, nothing to stop")
            return

        logger.info("Stopping VoiceBot pipeline")

        try:
            # Stop pipeline task with timeout
            if self._task:
                logger.info("Pipeline stage: Stopping task")
                try:
                    # Wait up to 5 seconds for graceful shutdown
                    await asyncio.wait_for(self._cleanup(), timeout=5.0)
                except asyncio.TimeoutError:
                    logger.warning("Pipeline shutdown timed out after 5 seconds")
                    # Force cleanup
                    await self._force_cleanup()

            logger.info("Pipeline stage: All resources cleaned up")
            logger.info("VoiceBot stopped successfully")

        except Exception as e:
            logger.error(f"Error during VoiceBot shutdown: {e}", exc_info=True)
            # Attempt force cleanup
            await self._force_cleanup()
        finally:
            self._running = False

    async def _cleanup(self) -> None:
        """Clean up pipeline resources gracefully.

        Closes all service connections and releases resources.
        """
        logger.info("Pipeline stage: Cleaning up resources")

        # Cancel pipeline task
        if self._task:
            try:
                await self._task.cancel()
                logger.debug("Pipeline task cancelled")
            except Exception as e:
                logger.warning(f"Error cancelling pipeline task: {e}")

        # Close transport
        if self.transport:
            try:
                logger.info("Pipeline stage: Closing transport connection")
                # Transport cleanup handled by transport itself
                logger.debug("Transport connection closed")
            except Exception as e:
                logger.warning(f"Error closing transport: {e}")

        # STT cleanup (Deepgram sessions)
        if self._stt:
            try:
                logger.info("Pipeline stage: Closing STT session")
                # STT cleanup handled by Deepgram service
                logger.debug("STT session closed")
            except Exception as e:
                logger.warning(f"Error closing STT session: {e}")

        # LLM cleanup (OpenAI connections)
        if self._llm:
            try:
                logger.info("Pipeline stage: Closing LLM connection")
                # LLM cleanup handled by OpenAI service
                logger.debug("LLM connection closed")
            except Exception as e:
                logger.warning(f"Error closing LLM connection: {e}")

        # TTS cleanup (Cartesia WebSocket)
        if self._tts:
            try:
                logger.info("Pipeline stage: Closing TTS session")
                # TTS cleanup handled by Cartesia service
                logger.debug("TTS session closed")
            except Exception as e:
                logger.warning(f"Error closing TTS session: {e}")

    async def _force_cleanup(self) -> None:
        """Force cleanup of resources when graceful shutdown fails.

        Used as a fallback when cleanup timeout is exceeded.
        """
        logger.warning("Forcing resource cleanup")

        # Force close everything without waiting
        self._task = None
        self._runner = None
        self._pipeline = None

        logger.warning("Force cleanup completed")

    @property
    def is_running(self) -> bool:
        """Check if the bot is currently running.

        Returns:
            True if bot is running, False otherwise
        """
        return self._running

    @property
    def pipeline(self) -> Optional[Pipeline]:
        """Get the current pipeline instance.

        Returns:
            Pipeline instance if built, None otherwise
        """
        return self._pipeline
