"""Tests for voice configuration schema and loader."""

import json
from pathlib import Path

import pytest

from specify_cli.voice.config import (
    AssistantConfig,
    LLMConfig,
    PipelineConfig,
    STTConfig,
    TTSConfig,
    TransportConfig,
    VoiceConfig,
    VoiceSettings,
    load_config,
)


class TestVoiceSettings:
    """Tests for VoiceSettings dataclass."""

    def test_default_values(self):
        """Test default voice settings."""
        settings = VoiceSettings()
        assert settings.speed == 1.0
        assert settings.stability == 0.75

    def test_custom_values(self):
        """Test custom voice settings."""
        settings = VoiceSettings(speed=1.2, stability=0.9)
        assert settings.speed == 1.2
        assert settings.stability == 0.9


class TestAssistantConfig:
    """Tests for AssistantConfig dataclass."""

    def test_required_name(self):
        """Test assistant config with required name."""
        config = AssistantConfig(name="Test Assistant")
        assert config.name == "Test Assistant"
        assert config.system_prompt == "You are a helpful assistant for JP Spec Kit."

    def test_custom_values(self):
        """Test assistant config with custom values."""
        config = AssistantConfig(
            name="Custom",
            system_prompt="Custom prompt",
            first_message="Hi",
            last_message="Bye",
        )
        assert config.name == "Custom"
        assert config.system_prompt == "Custom prompt"
        assert config.first_message == "Hi"
        assert config.last_message == "Bye"


class TestSTTConfig:
    """Tests for STTConfig dataclass."""

    def test_required_provider(self):
        """Test STT config with required provider."""
        config = STTConfig(provider="deepgram")
        assert config.provider == "deepgram"
        assert config.model == "nova-3"
        assert config.language == "en"

    def test_custom_values(self):
        """Test STT config with custom values."""
        config = STTConfig(provider="openai", model="whisper-1", language="es")
        assert config.provider == "openai"
        assert config.model == "whisper-1"
        assert config.language == "es"


class TestLLMConfig:
    """Tests for LLMConfig dataclass."""

    def test_required_provider(self):
        """Test LLM config with required provider."""
        config = LLMConfig(provider="openai")
        assert config.provider == "openai"
        assert config.model == "gpt-4o"
        assert config.temperature == 0.7
        assert config.max_tokens == 1000

    def test_custom_values(self):
        """Test LLM config with custom values."""
        config = LLMConfig(
            provider="anthropic",
            model="claude-3.5",
            temperature=0.5,
            max_tokens=2000,
        )
        assert config.provider == "anthropic"
        assert config.model == "claude-3.5"
        assert config.temperature == 0.5
        assert config.max_tokens == 2000


class TestTTSConfig:
    """Tests for TTSConfig dataclass."""

    def test_required_provider(self):
        """Test TTS config with required provider."""
        config = TTSConfig(provider="cartesia")
        assert config.provider == "cartesia"
        assert config.voice_id == "default"
        assert config.output_format == "pcm_16000"

    def test_custom_values(self):
        """Test TTS config with custom values."""
        config = TTSConfig(
            provider="elevenlabs",
            voice_id="voice123",
            output_format="mp3_44100",
        )
        assert config.provider == "elevenlabs"
        assert config.voice_id == "voice123"
        assert config.output_format == "mp3_44100"


class TestTransportConfig:
    """Tests for TransportConfig dataclass."""

    def test_default_values(self):
        """Test default transport config."""
        config = TransportConfig()
        assert config.type == "daily"
        assert config.room_url is None
        assert config.token is None

    def test_custom_values(self):
        """Test custom transport config."""
        config = TransportConfig(
            type="websocket",
            room_url="wss://example.com",
            token="token123",
        )
        assert config.type == "websocket"
        assert config.room_url == "wss://example.com"
        assert config.token == "token123"


class TestPipelineConfig:
    """Tests for PipelineConfig dataclass."""

    def test_complete_pipeline(self):
        """Test complete pipeline configuration."""
        stt = STTConfig(provider="deepgram")
        llm = LLMConfig(provider="openai")
        tts = TTSConfig(provider="cartesia")
        pipeline = PipelineConfig(stt=stt, llm=llm, tts=tts)

        assert pipeline.stt.provider == "deepgram"
        assert pipeline.llm.provider == "openai"
        assert pipeline.tts.provider == "cartesia"


class TestVoiceConfig:
    """Tests for VoiceConfig dataclass."""

    def test_valid_config_with_api_keys(self, monkeypatch):
        """Test valid configuration with all required API keys."""
        # Set environment variables
        monkeypatch.setenv("DEEPGRAM_API_KEY", "dg_test_key")
        monkeypatch.setenv("OPENAI_API_KEY", "sk_test_key")
        monkeypatch.setenv("CARTESIA_API_KEY", "ca_test_key")
        monkeypatch.setenv("DAILY_API_KEY", "daily_test_key")

        assistant = AssistantConfig(name="Test Assistant")
        pipeline = PipelineConfig(
            stt=STTConfig(provider="deepgram"),
            llm=LLMConfig(provider="openai"),
            tts=TTSConfig(provider="cartesia"),
        )

        config = VoiceConfig(assistant=assistant, pipeline=pipeline)

        assert config.assistant.name == "Test Assistant"
        assert config.pipeline.stt.provider == "deepgram"
        assert config.api_keys["deepgram"] == "dg_test_key"
        assert config.api_keys["openai"] == "sk_test_key"
        assert config.api_keys["cartesia"] == "ca_test_key"
        assert config.api_keys["daily"] == "daily_test_key"

    def test_missing_assistant_name(self, monkeypatch):
        """Test validation error for missing assistant name."""
        monkeypatch.setenv("DEEPGRAM_API_KEY", "dg_test_key")
        monkeypatch.setenv("OPENAI_API_KEY", "sk_test_key")
        monkeypatch.setenv("CARTESIA_API_KEY", "ca_test_key")
        monkeypatch.setenv("DAILY_API_KEY", "daily_test_key")

        assistant = AssistantConfig(name="")
        pipeline = PipelineConfig(
            stt=STTConfig(provider="deepgram"),
            llm=LLMConfig(provider="openai"),
            tts=TTSConfig(provider="cartesia"),
        )

        with pytest.raises(ValueError, match="assistant.name is required"):
            VoiceConfig(assistant=assistant, pipeline=pipeline)

    def test_missing_stt_provider(self, monkeypatch):
        """Test validation error for missing STT provider."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk_test_key")
        monkeypatch.setenv("CARTESIA_API_KEY", "ca_test_key")
        monkeypatch.setenv("DAILY_API_KEY", "daily_test_key")

        assistant = AssistantConfig(name="Test")
        pipeline = PipelineConfig(
            stt=STTConfig(provider=""),
            llm=LLMConfig(provider="openai"),
            tts=TTSConfig(provider="cartesia"),
        )

        with pytest.raises(ValueError, match="pipeline.stt.provider is required"):
            VoiceConfig(assistant=assistant, pipeline=pipeline)

    def test_missing_llm_provider(self, monkeypatch):
        """Test validation error for missing LLM provider."""
        monkeypatch.setenv("DEEPGRAM_API_KEY", "dg_test_key")
        monkeypatch.setenv("CARTESIA_API_KEY", "ca_test_key")
        monkeypatch.setenv("DAILY_API_KEY", "daily_test_key")

        assistant = AssistantConfig(name="Test")
        pipeline = PipelineConfig(
            stt=STTConfig(provider="deepgram"),
            llm=LLMConfig(provider=""),
            tts=TTSConfig(provider="cartesia"),
        )

        with pytest.raises(ValueError, match="pipeline.llm.provider is required"):
            VoiceConfig(assistant=assistant, pipeline=pipeline)

    def test_missing_tts_provider(self, monkeypatch):
        """Test validation error for missing TTS provider."""
        monkeypatch.setenv("DEEPGRAM_API_KEY", "dg_test_key")
        monkeypatch.setenv("OPENAI_API_KEY", "sk_test_key")
        monkeypatch.setenv("DAILY_API_KEY", "daily_test_key")

        assistant = AssistantConfig(name="Test")
        pipeline = PipelineConfig(
            stt=STTConfig(provider="deepgram"),
            llm=LLMConfig(provider="openai"),
            tts=TTSConfig(provider=""),
        )

        with pytest.raises(ValueError, match="pipeline.tts.provider is required"):
            VoiceConfig(assistant=assistant, pipeline=pipeline)

    def test_missing_deepgram_api_key(self, monkeypatch):
        """Test validation error for missing Deepgram API key."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk_test_key")
        monkeypatch.setenv("CARTESIA_API_KEY", "ca_test_key")
        monkeypatch.setenv("DAILY_API_KEY", "daily_test_key")

        assistant = AssistantConfig(name="Test")
        pipeline = PipelineConfig(
            stt=STTConfig(provider="deepgram"),
            llm=LLMConfig(provider="openai"),
            tts=TTSConfig(provider="cartesia"),
        )

        with pytest.raises(ValueError, match="Missing required API keys.*DEEPGRAM"):
            VoiceConfig(assistant=assistant, pipeline=pipeline)

    def test_missing_openai_api_key(self, monkeypatch):
        """Test validation error for missing OpenAI API key."""
        monkeypatch.setenv("DEEPGRAM_API_KEY", "dg_test_key")
        monkeypatch.setenv("CARTESIA_API_KEY", "ca_test_key")
        monkeypatch.setenv("DAILY_API_KEY", "daily_test_key")

        assistant = AssistantConfig(name="Test")
        pipeline = PipelineConfig(
            stt=STTConfig(provider="deepgram"),
            llm=LLMConfig(provider="openai"),
            tts=TTSConfig(provider="cartesia"),
        )

        with pytest.raises(ValueError, match="Missing required API keys.*OPENAI"):
            VoiceConfig(assistant=assistant, pipeline=pipeline)

    def test_missing_cartesia_api_key(self, monkeypatch):
        """Test validation error for missing Cartesia API key."""
        monkeypatch.setenv("DEEPGRAM_API_KEY", "dg_test_key")
        monkeypatch.setenv("OPENAI_API_KEY", "sk_test_key")
        monkeypatch.setenv("DAILY_API_KEY", "daily_test_key")

        assistant = AssistantConfig(name="Test")
        pipeline = PipelineConfig(
            stt=STTConfig(provider="deepgram"),
            llm=LLMConfig(provider="openai"),
            tts=TTSConfig(provider="cartesia"),
        )

        with pytest.raises(ValueError, match="Missing required API keys.*CARTESIA"):
            VoiceConfig(assistant=assistant, pipeline=pipeline)

    def test_missing_daily_api_key(self, monkeypatch):
        """Test validation error for missing Daily API key."""
        monkeypatch.setenv("DEEPGRAM_API_KEY", "dg_test_key")
        monkeypatch.setenv("OPENAI_API_KEY", "sk_test_key")
        monkeypatch.setenv("CARTESIA_API_KEY", "ca_test_key")

        assistant = AssistantConfig(name="Test")
        pipeline = PipelineConfig(
            stt=STTConfig(provider="deepgram"),
            llm=LLMConfig(provider="openai"),
            tts=TTSConfig(provider="cartesia"),
        )

        with pytest.raises(ValueError, match="Missing required API keys.*DAILY"):
            VoiceConfig(assistant=assistant, pipeline=pipeline)

    def test_missing_multiple_api_keys(self, monkeypatch):
        """Test validation error listing all missing API keys."""
        # Don't set any API keys
        monkeypatch.delenv("DEEPGRAM_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("CARTESIA_API_KEY", raising=False)
        monkeypatch.delenv("DAILY_API_KEY", raising=False)

        assistant = AssistantConfig(name="Test")
        pipeline = PipelineConfig(
            stt=STTConfig(provider="deepgram"),
            llm=LLMConfig(provider="openai"),
            tts=TTSConfig(provider="cartesia"),
        )

        with pytest.raises(ValueError) as exc_info:
            VoiceConfig(assistant=assistant, pipeline=pipeline)

        error_msg = str(exc_info.value)
        assert "Missing required API keys" in error_msg
        assert "DEEPGRAM_API_KEY" in error_msg
        assert "OPENAI_API_KEY" in error_msg
        assert "CARTESIA_API_KEY" in error_msg
        assert "DAILY_API_KEY" in error_msg


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_valid_config(self, monkeypatch, tmp_path):
        """Test loading a valid configuration file."""
        # Set environment variables
        monkeypatch.setenv("DEEPGRAM_API_KEY", "dg_test_key")
        monkeypatch.setenv("OPENAI_API_KEY", "sk_test_key")
        monkeypatch.setenv("CARTESIA_API_KEY", "ca_test_key")
        monkeypatch.setenv("DAILY_API_KEY", "daily_test_key")

        # Create config file
        config_path = tmp_path / "voice-config.json"
        config_data = {
            "assistant": {
                "name": "Test Assistant",
                "system_prompt": "Test prompt",
                "first_message": "Hello test",
                "last_message": "Goodbye test",
                "voice_settings": {"speed": 1.2, "stability": 0.8},
            },
            "pipeline": {
                "stt": {"provider": "deepgram", "model": "nova-3", "language": "en"},
                "llm": {
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.7,
                    "max_tokens": 1000,
                },
                "tts": {
                    "provider": "cartesia",
                    "voice_id": "default",
                    "output_format": "pcm_16000",
                },
            },
            "transport": {"type": "daily", "room_url": None, "token": None},
        }

        with open(config_path, "w") as f:
            json.dump(config_data, f)

        config = load_config(config_path)

        assert config.assistant.name == "Test Assistant"
        assert config.assistant.system_prompt == "Test prompt"
        assert config.pipeline.stt.provider == "deepgram"
        assert config.pipeline.llm.provider == "openai"
        assert config.pipeline.tts.provider == "cartesia"

    def test_load_config_file_not_found(self):
        """Test error when config file doesn't exist."""
        config_path = Path("/nonexistent/config.json")

        with pytest.raises(FileNotFoundError, match="Configuration file not found"):
            load_config(config_path)

    def test_load_config_invalid_json(self, tmp_path):
        """Test error when config file is not valid JSON."""
        config_path = tmp_path / "invalid.json"
        config_path.write_text("{ invalid json }")

        with pytest.raises(json.JSONDecodeError):
            load_config(config_path)

    def test_load_config_with_defaults(self, monkeypatch, tmp_path):
        """Test loading config with minimal data using defaults."""
        monkeypatch.setenv("DEEPGRAM_API_KEY", "dg_test_key")
        monkeypatch.setenv("OPENAI_API_KEY", "sk_test_key")
        monkeypatch.setenv("CARTESIA_API_KEY", "ca_test_key")
        monkeypatch.setenv("DAILY_API_KEY", "daily_test_key")

        config_path = tmp_path / "minimal-config.json"
        config_data = {
            "assistant": {"name": "Minimal Assistant"},
            "pipeline": {
                "stt": {"provider": "deepgram"},
                "llm": {"provider": "openai"},
                "tts": {"provider": "cartesia"},
            },
        }

        with open(config_path, "w") as f:
            json.dump(config_data, f)

        config = load_config(config_path)

        # Check defaults are applied
        assert config.assistant.name == "Minimal Assistant"
        assert (
            config.assistant.system_prompt
            == "You are a helpful assistant for JP Spec Kit."
        )
        assert config.pipeline.stt.model == "nova-3"
        assert config.pipeline.llm.model == "gpt-4o"
        assert config.transport.type == "daily"
