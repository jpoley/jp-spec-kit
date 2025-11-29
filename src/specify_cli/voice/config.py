"""Voice configuration schema and loader.

Provides dataclasses for voice assistant and pipeline configuration,
with validation and environment variable loading for API keys.
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class VoiceSettings:
    """Voice synthesis settings."""

    speed: float = 1.0
    stability: float = 0.75


@dataclass
class AssistantConfig:
    """Voice assistant configuration."""

    name: str
    system_prompt: str = "You are a helpful assistant for JP Spec Kit."
    first_message: str = "Hello! I'm your JP Spec Kit assistant. How can I help?"
    last_message: str = "Goodbye! Let me know if you need anything else."
    voice_settings: VoiceSettings = field(default_factory=VoiceSettings)


@dataclass
class STTConfig:
    """Speech-to-Text configuration."""

    provider: str
    model: str = "nova-3"
    language: str = "en"


@dataclass
class LLMConfig:
    """Large Language Model configuration."""

    provider: str
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 1000


@dataclass
class TTSConfig:
    """Text-to-Speech configuration."""

    provider: str
    voice_id: str = "default"
    output_format: str = "pcm_16000"


@dataclass
class TransportConfig:
    """Transport layer configuration."""

    type: str = "daily"
    room_url: Optional[str] = None
    token: Optional[str] = None


@dataclass
class PipelineConfig:
    """Pipeline configuration for STT, LLM, and TTS."""

    stt: STTConfig
    llm: LLMConfig
    tts: TTSConfig


@dataclass
class VoiceConfig:
    """Complete voice assistant configuration.

    Validates required fields and loads API keys from environment.
    """

    assistant: AssistantConfig
    pipeline: PipelineConfig
    transport: TransportConfig = field(default_factory=TransportConfig)
    api_keys: dict[str, Optional[str]] = field(default_factory=dict)

    def __post_init__(self):
        """Validate configuration and load API keys from environment."""
        # Validate required fields
        if not self.assistant.name:
            raise ValueError("assistant.name is required")
        if not self.pipeline.stt.provider:
            raise ValueError("pipeline.stt.provider is required")
        if not self.pipeline.llm.provider:
            raise ValueError("pipeline.llm.provider is required")
        if not self.pipeline.tts.provider:
            raise ValueError("pipeline.tts.provider is required")

        # Load API keys from environment
        self.api_keys = {
            "deepgram": os.getenv("DEEPGRAM_API_KEY"),
            "openai": os.getenv("OPENAI_API_KEY"),
            "cartesia": os.getenv("CARTESIA_API_KEY"),
            "daily": os.getenv("DAILY_API_KEY"),
        }

        # Determine which API keys are required based on providers
        required_keys = set()
        if self.pipeline.stt.provider.lower() == "deepgram":
            required_keys.add("deepgram")
        if self.pipeline.llm.provider.lower() == "openai":
            required_keys.add("openai")
        if self.pipeline.tts.provider.lower() in ["cartesia", "elevenlabs"]:
            required_keys.add(self.pipeline.tts.provider.lower())
        if self.transport.type.lower() == "daily":
            required_keys.add("daily")

        # Check for missing required API keys
        missing_keys = [
            key.upper() + "_API_KEY"
            for key in required_keys
            if not self.api_keys.get(key)
        ]

        if missing_keys:
            raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")


def load_config(config_path: Path) -> VoiceConfig:
    """Load voice configuration from JSON file.

    Args:
        config_path: Path to JSON configuration file

    Returns:
        VoiceConfig instance with validated configuration

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config is invalid or missing required API keys
        json.JSONDecodeError: If config file is not valid JSON
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path) as f:
        data = json.load(f)

    # Parse nested configurations
    assistant_data = data.get("assistant", {})
    voice_settings_data = assistant_data.get("voice_settings", {})
    assistant = AssistantConfig(
        name=assistant_data.get("name", "JP Spec Kit Voice Assistant"),
        system_prompt=assistant_data.get(
            "system_prompt", "You are a helpful assistant for JP Spec Kit."
        ),
        first_message=assistant_data.get(
            "first_message",
            "Hello! I'm your JP Spec Kit assistant. How can I help?",
        ),
        last_message=assistant_data.get(
            "last_message", "Goodbye! Let me know if you need anything else."
        ),
        voice_settings=VoiceSettings(
            speed=voice_settings_data.get("speed", 1.0),
            stability=voice_settings_data.get("stability", 0.75),
        ),
    )

    pipeline_data = data.get("pipeline", {})
    stt_data = pipeline_data.get("stt", {})
    llm_data = pipeline_data.get("llm", {})
    tts_data = pipeline_data.get("tts", {})

    pipeline = PipelineConfig(
        stt=STTConfig(
            provider=stt_data.get("provider", "deepgram"),
            model=stt_data.get("model", "nova-3"),
            language=stt_data.get("language", "en"),
        ),
        llm=LLMConfig(
            provider=llm_data.get("provider", "openai"),
            model=llm_data.get("model", "gpt-4o"),
            temperature=llm_data.get("temperature", 0.7),
            max_tokens=llm_data.get("max_tokens", 1000),
        ),
        tts=TTSConfig(
            provider=tts_data.get("provider", "cartesia"),
            voice_id=tts_data.get("voice_id", "default"),
            output_format=tts_data.get("output_format", "pcm_16000"),
        ),
    )

    transport_data = data.get("transport", {})
    transport = TransportConfig(
        type=transport_data.get("type", "daily"),
        room_url=transport_data.get("room_url"),
        token=transport_data.get("token"),
    )

    return VoiceConfig(assistant=assistant, pipeline=pipeline, transport=transport)
