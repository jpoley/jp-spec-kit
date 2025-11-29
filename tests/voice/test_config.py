"""Unit tests for voice configuration module."""

import json
from pathlib import Path
from typing import Any, Dict

import pytest

from specify_cli.voice.config import (
    AssistantConfig,
    LLMConfig,
    PipelineConfig,
    STTConfig,
    TTSConfig,
    VoiceConfig,
    VoiceSettings,
    load_api_keys,
    load_config,
)


@pytest.fixture
def minimal_valid_config() -> Dict[str, Any]:
    """Minimal valid configuration for testing."""
    return {
        "assistant": {
            "name": "Test Assistant",
        },
        "pipeline": {
            "stt": {"provider": "deepgram"},
            "llm": {"provider": "openai"},
            "tts": {"provider": "cartesia"},
        },
    }


@pytest.fixture
def full_config() -> Dict[str, Any]:
    """Full configuration with all fields specified."""
    return {
        "assistant": {
            "name": "Full Test Assistant",
            "system_prompt": "Custom system prompt",
            "first_message": "Custom first message",
            "last_message": "Custom last message",
            "voice_settings": {"speed": 1.2, "stability": 0.8},
        },
        "pipeline": {
            "stt": {"provider": "deepgram", "model": "nova-2", "language": "es"},
            "llm": {
                "provider": "anthropic",
                "model": "claude-3",
                "temperature": 0.5,
                "max_tokens": 2000,
            },
            "tts": {
                "provider": "elevenlabs",
                "voice_id": "custom-voice",
                "output_format": "pcm_22050",
            },
        },
        "transport": {
            "type": "websocket",
            "room_url": "wss://example.com",
            "token": "test-token",
        },
    }


@pytest.fixture
def config_file(tmp_path: Path, minimal_valid_config: Dict[str, Any]) -> Path:
    """Create a temporary config file for testing."""
    config_path = tmp_path / "test-config.json"
    with open(config_path, "w") as f:
        json.dump(minimal_valid_config, f)
    return config_path


@pytest.fixture
def env_with_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set up environment with all API keys."""
    monkeypatch.setenv("DEEPGRAM_API_KEY", "test-deepgram-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("CARTESIA_API_KEY", "test-cartesia-key")
    monkeypatch.setenv("DAILY_API_KEY", "test-daily-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
    monkeypatch.setenv("ELEVENLABS_API_KEY", "test-elevenlabs-key")


@pytest.fixture
def env_no_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    """Clear all API keys from environment."""
    for key in [
        "DEEPGRAM_API_KEY",
        "OPENAI_API_KEY",
        "CARTESIA_API_KEY",
        "DAILY_API_KEY",
        "ANTHROPIC_API_KEY",
        "ELEVENLABS_API_KEY",
    ]:
        monkeypatch.delenv(key, raising=False)


class TestVoiceSettings:
    """Tests for VoiceSettings dataclass."""

    def test_default_values(self) -> None:
        """Test default voice settings values."""
        settings = VoiceSettings()
        assert settings.speed == 1.0
        assert settings.stability == 0.75

    def test_custom_values(self) -> None:
        """Test custom voice settings values."""
        settings = VoiceSettings(speed=1.5, stability=0.9)
        assert settings.speed == 1.5
        assert settings.stability == 0.9


class TestAssistantConfig:
    """Tests for AssistantConfig dataclass."""

    def test_required_name(self) -> None:
        """Test that name is required."""
        config = AssistantConfig(name="Test")
        assert config.name == "Test"

    def test_default_messages(self) -> None:
        """Test default message values."""
        config = AssistantConfig(name="Test")
        assert "JP Spec Kit" in config.system_prompt
        assert "Hello" in config.first_message
        assert "Goodbye" in config.last_message

    def test_custom_messages(self) -> None:
        """Test custom message values."""
        config = AssistantConfig(
            name="Test",
            system_prompt="Custom prompt",
            first_message="Custom first",
            last_message="Custom last",
        )
        assert config.system_prompt == "Custom prompt"
        assert config.first_message == "Custom first"
        assert config.last_message == "Custom last"

    def test_default_voice_settings(self) -> None:
        """Test default voice settings in assistant config."""
        config = AssistantConfig(name="Test")
        assert isinstance(config.voice_settings, VoiceSettings)
        assert config.voice_settings.speed == 1.0


class TestPipelineConfig:
    """Tests for pipeline configuration dataclasses."""

    def test_stt_config(self) -> None:
        """Test STTConfig dataclass."""
        config = STTConfig(provider="deepgram")
        assert config.provider == "deepgram"
        assert config.model == "nova-3"
        assert config.language == "en"

    def test_llm_config(self) -> None:
        """Test LLMConfig dataclass."""
        config = LLMConfig(provider="openai")
        assert config.provider == "openai"
        assert config.model == "gpt-4o"
        assert config.temperature == 0.7
        assert config.max_tokens == 1000

    def test_tts_config(self) -> None:
        """Test TTSConfig dataclass."""
        config = TTSConfig(provider="cartesia")
        assert config.provider == "cartesia"
        assert config.voice_id == "default"
        assert config.output_format == "pcm_16000"


class TestAPIKeys:
    """Tests for API key loading."""

    def test_load_api_keys_with_env(self, env_with_keys: None) -> None:
        """Test loading API keys from environment."""
        keys = load_api_keys()
        assert keys.deepgram == "test-deepgram-key"
        assert keys.openai == "test-openai-key"
        assert keys.cartesia == "test-cartesia-key"
        assert keys.daily == "test-daily-key"
        assert keys.anthropic == "test-anthropic-key"
        assert keys.elevenlabs == "test-elevenlabs-key"

    def test_load_api_keys_without_env(self, env_no_keys: None) -> None:
        """Test loading API keys when none are set."""
        keys = load_api_keys()
        assert keys.deepgram is None
        assert keys.openai is None
        assert keys.cartesia is None
        assert keys.daily is None
        assert keys.anthropic is None
        assert keys.elevenlabs is None


class TestVoiceConfigValidation:
    """Tests for VoiceConfig validation."""

    def test_validate_missing_assistant_name(self, env_with_keys: None) -> None:
        """Test validation fails when assistant name is missing."""
        config = VoiceConfig(
            assistant=AssistantConfig(name=""),
            pipeline=PipelineConfig(
                stt=STTConfig(provider="deepgram"),
                llm=LLMConfig(provider="openai"),
                tts=TTSConfig(provider="cartesia"),
            ),
            api_keys=load_api_keys(),
        )
        with pytest.raises(ValueError, match="assistant.name is required"):
            config.validate()

    def test_validate_missing_stt_provider(self, env_with_keys: None) -> None:
        """Test validation fails when STT provider is missing."""
        config = VoiceConfig(
            assistant=AssistantConfig(name="Test"),
            pipeline=PipelineConfig(
                stt=STTConfig(provider=""),
                llm=LLMConfig(provider="openai"),
                tts=TTSConfig(provider="cartesia"),
            ),
            api_keys=load_api_keys(),
        )
        with pytest.raises(ValueError, match="pipeline.stt.provider is required"):
            config.validate()

    def test_validate_missing_llm_provider(self, env_with_keys: None) -> None:
        """Test validation fails when LLM provider is missing."""
        config = VoiceConfig(
            assistant=AssistantConfig(name="Test"),
            pipeline=PipelineConfig(
                stt=STTConfig(provider="deepgram"),
                llm=LLMConfig(provider=""),
                tts=TTSConfig(provider="cartesia"),
            ),
            api_keys=load_api_keys(),
        )
        with pytest.raises(ValueError, match="pipeline.llm.provider is required"):
            config.validate()

    def test_validate_missing_tts_provider(self, env_with_keys: None) -> None:
        """Test validation fails when TTS provider is missing."""
        config = VoiceConfig(
            assistant=AssistantConfig(name="Test"),
            pipeline=PipelineConfig(
                stt=STTConfig(provider="deepgram"),
                llm=LLMConfig(provider="openai"),
                tts=TTSConfig(provider=""),
            ),
            api_keys=load_api_keys(),
        )
        with pytest.raises(ValueError, match="pipeline.tts.provider is required"):
            config.validate()

    def test_validate_missing_deepgram_key(self, env_no_keys: None) -> None:
        """Test validation fails when Deepgram key is missing."""
        config = VoiceConfig(
            assistant=AssistantConfig(name="Test"),
            pipeline=PipelineConfig(
                stt=STTConfig(provider="deepgram"),
                llm=LLMConfig(provider="openai"),
                tts=TTSConfig(provider="cartesia"),
            ),
            api_keys=load_api_keys(),
        )
        with pytest.raises(
            ValueError, match="Missing required API keys.*DEEPGRAM_API_KEY"
        ):
            config.validate()

    def test_validate_missing_openai_key(
        self, env_no_keys: None, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test validation fails when OpenAI key is missing."""
        monkeypatch.setenv("DEEPGRAM_API_KEY", "test")
        monkeypatch.setenv("CARTESIA_API_KEY", "test")
        monkeypatch.setenv("DAILY_API_KEY", "test")

        config = VoiceConfig(
            assistant=AssistantConfig(name="Test"),
            pipeline=PipelineConfig(
                stt=STTConfig(provider="deepgram"),
                llm=LLMConfig(provider="openai"),
                tts=TTSConfig(provider="cartesia"),
            ),
            api_keys=load_api_keys(),
        )
        with pytest.raises(
            ValueError, match="Missing required API keys.*OPENAI_API_KEY"
        ):
            config.validate()

    def test_validate_missing_multiple_keys(self, env_no_keys: None) -> None:
        """Test validation lists all missing keys."""
        config = VoiceConfig(
            assistant=AssistantConfig(name="Test"),
            pipeline=PipelineConfig(
                stt=STTConfig(provider="deepgram"),
                llm=LLMConfig(provider="openai"),
                tts=TTSConfig(provider="cartesia"),
            ),
            api_keys=load_api_keys(),
        )
        with pytest.raises(ValueError) as exc_info:
            config.validate()
        error_msg = str(exc_info.value)
        assert "DEEPGRAM_API_KEY" in error_msg
        assert "OPENAI_API_KEY" in error_msg
        assert "CARTESIA_API_KEY" in error_msg

    def test_validate_success(self, env_with_keys: None) -> None:
        """Test validation succeeds with all required fields and keys."""
        config = VoiceConfig(
            assistant=AssistantConfig(name="Test"),
            pipeline=PipelineConfig(
                stt=STTConfig(provider="deepgram"),
                llm=LLMConfig(provider="openai"),
                tts=TTSConfig(provider="cartesia"),
            ),
            api_keys=load_api_keys(),
        )
        # Should not raise
        config.validate()

    def test_validate_anthropic_llm(
        self, env_no_keys: None, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test validation with Anthropic LLM provider."""
        monkeypatch.setenv("DEEPGRAM_API_KEY", "test")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
        monkeypatch.setenv("CARTESIA_API_KEY", "test")
        monkeypatch.setenv("DAILY_API_KEY", "test")

        config = VoiceConfig(
            assistant=AssistantConfig(name="Test"),
            pipeline=PipelineConfig(
                stt=STTConfig(provider="deepgram"),
                llm=LLMConfig(provider="anthropic"),
                tts=TTSConfig(provider="cartesia"),
            ),
            api_keys=load_api_keys(),
        )
        # Should not raise
        config.validate()

    def test_validate_elevenlabs_tts(
        self, env_no_keys: None, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test validation with ElevenLabs TTS provider."""
        monkeypatch.setenv("DEEPGRAM_API_KEY", "test")
        monkeypatch.setenv("OPENAI_API_KEY", "test")
        monkeypatch.setenv("ELEVENLABS_API_KEY", "test")
        monkeypatch.setenv("DAILY_API_KEY", "test")

        config = VoiceConfig(
            assistant=AssistantConfig(name="Test"),
            pipeline=PipelineConfig(
                stt=STTConfig(provider="deepgram"),
                llm=LLMConfig(provider="openai"),
                tts=TTSConfig(provider="elevenlabs"),
            ),
            api_keys=load_api_keys(),
        )
        # Should not raise
        config.validate()


class TestLoadConfig:
    """Tests for configuration file loading."""

    def test_load_config_file_not_found(
        self, tmp_path: Path, env_with_keys: None
    ) -> None:
        """Test loading non-existent config file raises error."""
        non_existent = tmp_path / "does-not-exist.json"
        with pytest.raises(FileNotFoundError, match="Configuration file not found"):
            load_config(non_existent)

    def test_load_minimal_config(self, config_file: Path, env_with_keys: None) -> None:
        """Test loading minimal valid configuration."""
        config = load_config(config_file)
        assert config.assistant.name == "Test Assistant"
        assert config.pipeline.stt.provider == "deepgram"
        assert config.pipeline.llm.provider == "openai"
        assert config.pipeline.tts.provider == "cartesia"

    def test_load_full_config(
        self, tmp_path: Path, full_config: Dict[str, Any], env_with_keys: None
    ) -> None:
        """Test loading full configuration with all fields."""
        config_path = tmp_path / "full-config.json"
        with open(config_path, "w") as f:
            json.dump(full_config, f)

        config = load_config(config_path)
        assert config.assistant.name == "Full Test Assistant"
        assert config.assistant.system_prompt == "Custom system prompt"
        assert config.assistant.voice_settings.speed == 1.2
        assert config.pipeline.stt.model == "nova-2"
        assert config.pipeline.llm.temperature == 0.5
        assert config.transport.type == "websocket"

    def test_load_config_uses_defaults(
        self, config_file: Path, env_with_keys: None
    ) -> None:
        """Test that missing optional fields use default values."""
        config = load_config(config_file)
        assert (
            config.assistant.system_prompt
            == "You are a helpful assistant for JP Spec Kit."
        )
        assert config.pipeline.stt.model == "nova-3"
        assert config.pipeline.llm.temperature == 0.7
        assert config.transport.type == "daily"

    def test_load_config_validates(self, config_file: Path, env_no_keys: None) -> None:
        """Test that load_config validates the configuration."""
        with pytest.raises(ValueError, match="Missing required API keys"):
            load_config(config_file)

    def test_load_config_loads_api_keys(
        self, config_file: Path, env_with_keys: None
    ) -> None:
        """Test that load_config loads API keys from environment."""
        config = load_config(config_file)
        assert config.api_keys.deepgram == "test-deepgram-key"
        assert config.api_keys.openai == "test-openai-key"
        assert config.api_keys.cartesia == "test-cartesia-key"
        assert config.api_keys.daily == "test-daily-key"

    def test_load_invalid_json(self, tmp_path: Path, env_with_keys: None) -> None:
        """Test loading invalid JSON raises error."""
        invalid_file = tmp_path / "invalid.json"
        with open(invalid_file, "w") as f:
            f.write("{ invalid json }")

        with pytest.raises(json.JSONDecodeError):
            load_config(invalid_file)
