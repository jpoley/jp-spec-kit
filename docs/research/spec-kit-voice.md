# spec-kit-voice: design document for voice I/O architecture (Phase 1)

**Date**: 2025-11-28  
**Status**: Draft – For Review  
**Confidence Level**: High (based on proven frameworks and research)

---

## Executive Summary

Phase 1 of **spec-kit-voice** introduces a cross-platform voice input/output capability to Flowspec. This enables users to interact with coding tools via natural speech, with AI-generated responses spoken back. Desktop clients use a Pipecat-based pipeline (Whisper + Piper); iOS clients use native STT/TTS APIs. Both communicate with a shared `/chat` endpoint for LLM interaction.

---

## Scope

- **Platforms**: Desktop (Pipecat) and iOS (native speech APIs)
- **Voice Workflow**:
  - Speech-to-Text (STT): Whisper (local) or Deepgram on desktop, `SFSpeechRecognizer` on iOS
  - Text-to-Speech (TTS): Piper (local) or Cartesia/ElevenLabs on desktop, `AVSpeechSynthesizer` on iOS
  - Shared backend API: `POST /chat` sends/receives text
- **Language**: English only (Phase 1)
- **Exclusions**: No wake-word, no Android/web clients, no multi-language

---

## Architecture Overview

### Desktop (Pipecat-based)

Pipecat runs a modular voice pipeline:

```
Input (mic) → WhisperSTT → LLM → PiperTTS → Output (speakers)
```

- Audio captured as `AudioRawFrame`
- STT outputs `TranscriptionFrame`
- LLM returns response text
- TTS turns response into `TTSAudioFrame`

### iOS (Native APIs)

- `SFSpeechRecognizer` for STT (on-device)
- Send text to backend `/chat`
- Receive text reply
- Use `AVSpeechSynthesizer` for TTS

### Shared Backend API

```
POST /chat
{
  "text": "string",
  "user_id": "string",
  "session_id": "string"
}
→
{
  "text_reply": "string"
}
```

Backend passes text to Claude Code, GitHub Copilot, or another LLM via simple proxy logic.

---

## Components & Responsibilities

| Component              | Responsibility                                             |
|------------------------|-------------------------------------------------------------|
| Pipecat CLI            | Runs audio pipeline on desktop                              |
| Whisper STT            | Transcribes English speech locally                          |
| Piper TTS              | Synthesizes voice locally on desktop                        |
| AVSpeechSynthesizer    | Native iOS speech output                                    |
| SFSpeechRecognizer     | Native iOS transcription                                    |
| `/chat` API            | Shared endpoint for receiving text and returning reply      |
| AI bridge              | Forwards queries to Claude Code, Copilot, etc.              |

---

## Failure Modes

| Failure              | Handling Strategy                                         |
|----------------------|------------------------------------------------------------|
| STT timeout          | Retry or prompt user to repeat                             |
| LLM unavailable      | Return fallback text (“I couldn’t process that.”)          |
| TTS failure          | Skip audio and display text                                |
| Network unavailable  | Fail gracefully on desktop; fall back to offline-only mode on iOS |
| Audio device error   | Fallback to CLI input/output, notify user                  |

---

## Implementation Notes

- Desktop stack = Python 3.11+, Pipecat, Whisper (faster-whisper), Piper
- iOS stack = Swift + Speech / AVFoundation
- Backend = FastAPI (or similar), no auth in Phase 1
- Configuration via `~/.spec-kit/config.yaml`
- End-to-end latency target: ~500–800ms

---

## Backlog Tasks

- [ ] Add `spec-kit-voice` CLI module
- [ ] Implement `WhisperSTTService` + `PiperTTSService` for Pipecat
- [ ] Add `/chat` FastAPI backend with Claude/Copilot bridge
- [ ] Build iOS Swift wrapper (STT + TTS)
- [ ] Error handling + logging
- [ ] Configuration support for models, voices, endpoint URLs
- [ ] Test harness with recorded voice samples

---

## Future Phases

- Android & browser clients
- Wake-word activation
- Multilingual support
- Full on-device processing

---

**Author**: ChatGPT, based on user requirements  
**Reviewed by**: _[pending]_

