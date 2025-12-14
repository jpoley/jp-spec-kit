# Pipecat Voice Integration Summary for JP Flowspec

**Date**: 2025-11-28
**Status**: Research Complete - Ready for Task Generation
**Confidence Level**: High - Framework is production-ready, well-documented, and actively maintained

---

## Executive Summary

**Pipecat** is the recommended framework for adding real-time voice capabilities to JP Flowspec. It is an open-source Python framework (BSD-2-Clause license) specifically designed for building voice and multimodal conversational AI agents with ultra-low latency (<800ms end-to-end).

### Why Pipecat?

| Criteria | Assessment |
|----------|------------|
| **Language Compatibility** | Python 3.10+ (flowspec uses 3.11+) |
| **Maturity** | Production-ready (9.1k stars, 1.5k forks, active development) |
| **Documentation** | Comprehensive (docs.pipecat.ai) |
| **Integration Ecosystem** | 60+ service integrations (STT, TTS, LLM) |
| **Client SDKs** | JavaScript, React, React Native, Swift, Kotlin, C++, ESP32 |
| **Transport Options** | WebRTC (Daily), WebSocket, FastAPI, Local |
| **License** | BSD-2-Clause (permissive, commercial-friendly) |
| **Architecture** | Frame-based pipeline - modular, composable, testable |

---

## Feature Complexity Assessment

Based on the flowspec assessment framework:

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Lines of Code** | C (3) | 500-2000 lines for voice module + config |
| **Modules Affected** | C (3) | New voice module, CLI integration, config, tests |
| **External Integrations** | D (4) | Multiple: Pipecat, STT (Deepgram), LLM (OpenAI/Anthropic), TTS (multiple) |
| **Data Complexity** | B (2) | Configuration files, session state (minimal persistence) |
| **Team Size** | A (1) | Solo developer |
| **Cross-Functional** | B (2) | Engineering + UX (voice interaction design) |
| **Technical Uncertainty** | C (3) | New domain (real-time voice), multiple spikes needed |
| **Business Impact** | B (2) | Significant capability addition, non-critical path |

**Total Score: 20/32 (Medium-High Complexity)**

**Recommendation: Full SDD Workflow** - This is a significant new capability requiring architectural planning, research spikes, and phased implementation.

---

## Technical Architecture

### Pipecat Core Concepts

#### 1. Frames
The fundamental data unit in Pipecat. Frames represent discrete packets of information:
- `AudioRawFrame` - Raw audio chunks
- `TranscriptionFrame` - STT output text
- `LLMTextFrame` - LLM response tokens
- `TTSAudioFrame` - Synthesized speech
- `SystemFrame` - Control signals

#### 2. FrameProcessors
Building blocks that receive, transform, and emit frames:
```python
# Example: Custom processor
class MyProcessor(FrameProcessor):
    async def process_frame(self, frame: Frame):
        # Transform and forward
        await self.push_frame(transformed_frame)
```

#### 3. Pipelines
Directed graph of connected processors:
```
Input → STT → Context Aggregator → LLM → TTS → Output
```

#### 4. PipelineTask
Manages pipeline execution, lifecycle, health monitoring, and cleanup.

### Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PIPECAT PIPELINE                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐        │
│  │Transport │ → │   STT   │ → │Context  │ → │   LLM   │        │
│  │(WebRTC)  │   │Deepgram │   │Aggregator│   │OpenAI   │        │
│  └──────────┘   └─────────┘   └─────────┘   └─────────┘        │
│       ↑                                           │              │
│       │         ┌─────────────────────────────────┘              │
│       │         ↓                                                │
│       │   ┌─────────┐   ┌─────────┐                            │
│       └───│   TTS   │ ← │Context  │                            │
│           │ElevenLabs│   │Aggregator│                            │
│           └─────────┘   └─────────┘                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Latency Profile

| Stage | Typical Latency |
|-------|-----------------|
| Audio Capture | 20-50ms |
| STT Processing | 100-200ms |
| LLM Inference | 200-400ms |
| TTS Synthesis | 100-200ms |
| Audio Playback | 20-50ms |
| **End-to-End** | **500-800ms** |

---

## Service Provider Matrix

### Speech-to-Text (STT) - Recommended

| Provider | Model | Latency | Accuracy | Cost | Recommendation |
|----------|-------|---------|----------|------|----------------|
| **Deepgram** | Nova 2/3 | Low | High | Medium | **Primary** |
| **OpenAI** | Whisper | Medium | High | Low | Fallback |
| **Gladia** | whisper-large-v3 | Low | High | Medium | Alternative |
| **AssemblyAI** | Universal | Low | Very High | Higher | Enterprise |

**Primary Recommendation**: Deepgram Nova 3
- Best balance of latency, accuracy, and streaming support
- Native Pipecat integration
- Real-time transcription with word-level timing

### Text-to-Speech (TTS) - Recommended

| Provider | Quality | Latency | Voices | Cost | Recommendation |
|----------|---------|---------|--------|------|----------------|
| **ElevenLabs** | Excellent | Low | 100+ | Higher | **Premium** |
| **Cartesia** | Very Good | Very Low | Medium | Medium | **Primary** |
| **Rime** | Good | Low | Medium | Lower | Cost-effective |
| **OpenAI** | Very Good | Medium | 6 | Medium | Simple setup |
| **Piper** | Good | Very Low | Limited | Free | Self-hosted |

**Primary Recommendation**: Cartesia (low latency) or ElevenLabs (quality)
- Cartesia: WebSocket streaming, word-level timing, excellent latency
- ElevenLabs: Best voice quality, extensive voice library

### Large Language Models (LLM)

| Provider | Model | Latency | Quality | Function Calling |
|----------|-------|---------|---------|------------------|
| **OpenAI** | GPT-4o | Medium | Excellent | Full |
| **Anthropic** | Claude 3.5 | Medium | Excellent | Full |
| **Groq** | Llama/Mixtral | Very Low | Good | Limited |
| **Google** | Gemini 2.5 | Low | Very Good | Full |

**Primary Recommendation**: OpenAI GPT-4o or Anthropic Claude 3.5
- Both have excellent function calling support
- Streaming response for minimal latency
- Can route through OpenRouter for flexibility

---

## Integration Strategy for JP Flowspec

### Phase 1: Voice Assistant Foundation

**Goal**: Add voice interface to interact with JP Flowspec commands

```
User speaks → STT → LLM (with JP Flowspec context) → TTS → User hears
```

**Use Cases**:
1. "Run the specify command for authentication feature"
2. "Show me the current task status"
3. "Create a new task for implementing the login page"
4. "What's the plan for this sprint?"

### Phase 2: Agentic Voice Workflows

**Goal**: Voice-driven spec-driven development workflows

```
User: "I want to build a user registration system"
       ↓
Bot: Gathers requirements via conversation
       ↓
Bot: Generates spec.md, plan.md, tasks
       ↓
Bot: Confirms with user verbally
```

### Architecture Integration

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLOWSPEC + PIPECAT                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    VOICE LAYER (NEW)                      │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐     │   │
│  │  │Transport│  │   STT   │  │   LLM   │  │   TTS   │     │   │
│  │  │ (Daily) │  │Deepgram │  │ OpenAI  │  │Cartesia │     │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                            │                                     │
│                            ↓ Function Calls                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                 FLOWSPEC CORE (EXISTING)                  │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐               │   │
│  │  │  CLI     │  │  Slash   │  │ Backlog  │               │   │
│  │  │ specify  │  │ Commands │  │   .md    │               │   │
│  │  └──────────┘  └──────────┘  └──────────┘               │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Function Calling Integration

Pipecat's function calling will invoke JP Flowspec operations:

```python
# Function definitions for LLM
tools = [
    {
        "name": "run_specify_command",
        "description": "Generate a feature specification from requirements",
        "parameters": {
            "type": "object",
            "properties": {
                "feature_description": {
                    "type": "string",
                    "description": "Description of the feature to specify"
                }
            },
            "required": ["feature_description"]
        }
    },
    {
        "name": "list_backlog_tasks",
        "description": "List tasks from the backlog",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["To Do", "In Progress", "Done"],
                    "description": "Filter by task status"
                }
            }
        }
    },
    {
        "name": "update_task_status",
        "description": "Update a backlog task's status",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"},
                "status": {"type": "string", "enum": ["To Do", "In Progress", "Done"]}
            },
            "required": ["task_id", "status"]
        }
    }
]
```

---

## Configuration Architecture

Based on insights from the YouTube demo transcript, implement a JSON-based configuration system:

### Assistant Configuration Schema

```json
{
  "assistant": {
    "name": "JP Flowspec Voice Assistant",
    "system_prompt": "You are a helpful assistant for JP Flowspec...",
    "first_message": "Hello! I'm your JP Flowspec assistant. How can I help?",
    "last_message": "Goodbye! Let me know if you need anything else.",
    "voice_settings": {
      "speed": 1.0,
      "stability": 0.75
    }
  },
  "pipeline": {
    "stt": {
      "provider": "deepgram",
      "model": "nova-3",
      "language": "en"
    },
    "llm": {
      "provider": "openai",
      "model": "gpt-4o",
      "temperature": 0.7,
      "max_tokens": 1000
    },
    "tts": {
      "provider": "cartesia",
      "voice_id": "default",
      "output_format": "pcm_16000"
    }
  },
  "transport": {
    "type": "daily",
    "room_url": null,
    "token": null
  }
}
```

### Environment Variables (Secrets)

```bash
# .env file - API keys only
DEEPGRAM_API_KEY=your_key
OPENAI_API_KEY=your_key
CARTESIA_API_KEY=your_key
DAILY_API_KEY=your_key
ANTHROPIC_API_KEY=your_key  # Optional
ELEVENLABS_API_KEY=your_key  # Optional
```

---

## Implementation Plan

### Phase 1: Foundation (Sprint 1-2)

#### 1.1 Project Structure
```
src/specify_cli/
├── voice/                      # NEW: Voice module
│   ├── __init__.py
│   ├── bot.py                  # Main voice bot
│   ├── config.py               # Configuration loader
│   ├── processors/             # Custom frame processors
│   │   ├── __init__.py
│   │   └── flowspec_processor.py # JP Flowspec integration
│   ├── services/               # Service wrappers
│   │   ├── __init__.py
│   │   ├── stt.py
│   │   ├── tts.py
│   │   └── llm.py
│   └── tools/                  # Function call handlers
│       ├── __init__.py
│       ├── specify_tools.py
│       └── backlog_tools.py
├── __init__.py
└── ...existing...
```

#### 1.2 Dependencies to Add
```toml
# pyproject.toml additions
[project.optional-dependencies]
voice = [
    "pipecat-ai[daily,deepgram,openai,cartesia]>=0.0.50",
]
```

#### 1.3 Initial Tasks

| Task | Description | Acceptance Criteria |
|------|-------------|---------------------|
| Add pipecat dependency | Add pipecat-ai to optional dependencies | `uv add "pipecat-ai[daily,deepgram,openai,cartesia]"` succeeds |
| Create voice module structure | Set up directory structure | All files created, imports work |
| Implement basic bot | Create minimal working voice bot | Bot responds to "hello" with voice |
| Add configuration system | JSON config loading | Config loads, validates, applies |
| Add CLI command | `specify voice` command | Command starts voice bot |

### Phase 2: JP Flowspec Integration (Sprint 3-4)

#### 2.1 Function Calling Implementation

| Task | Description | Acceptance Criteria |
|------|-------------|---------------------|
| Define tool schemas | Create OpenAI function schemas | All JP Flowspec operations have schemas |
| Implement specify tools | Handle /speckit:specify via voice | Voice command creates spec.md |
| Implement backlog tools | Handle backlog operations | Voice can list/create/update tasks |
| Implement plan tools | Handle /speckit:plan via voice | Voice command creates plan.md |
| Add context aggregation | Maintain conversation context | Multi-turn conversations work |

#### 2.2 System Prompt Engineering

```python
SYSTEM_PROMPT = """
You are the JP Flowspec Voice Assistant, helping developers with Spec-Driven Development.

Your capabilities:
1. Generate feature specifications from verbal descriptions
2. Create technical implementation plans
3. Generate and manage backlog tasks
4. Answer questions about current project status
5. Guide users through the SDD workflow

When users describe features:
- Ask clarifying questions to understand requirements
- Use run_specify_command to generate specifications
- Confirm the generated content verbally

When users ask about tasks:
- Use list_backlog_tasks to show current status
- Use update_task_status to make changes
- Summarize results conversationally

Keep responses concise for voice - avoid long lists or technical jargon.
"""
```

### Phase 3: Production Hardening (Sprint 5-6)

| Task | Description | Acceptance Criteria |
|------|-------------|---------------------|
| Add error handling | Graceful failure modes | Bot recovers from API errors |
| Add timeout handling | LLM/STT/TTS timeouts | User informed of delays |
| Add interruption handling | Handle user interruptions | Bot stops speaking when interrupted |
| Add session management | Track conversation state | Context persists across turns |
| Add logging/observability | OpenTelemetry integration | Metrics and traces available |
| Add tests | Unit and integration tests | 80%+ coverage on voice module |
| Add documentation | User and developer docs | README, API docs, examples |

### Phase 4: Advanced Features (Future)

| Feature | Description | Priority |
|---------|-------------|----------|
| Multi-modal | Show specs/plans on screen while speaking | Medium |
| Voice cloning | Custom voice for assistant | Low |
| Telephony | Phone number integration (Twilio) | Low |
| Multi-language | Support non-English | Low |
| Wake word | "Hey JP Flowspec" activation | Low |

---

## API Key Requirements

### Required (MVP)

| Service | Purpose | Pricing Model | Free Tier |
|---------|---------|---------------|-----------|
| **Deepgram** | Speech-to-Text | Per minute | $200 credit |
| **OpenAI** | LLM + Whisper | Per token | $5 credit |
| **Cartesia** | Text-to-Speech | Per character | Limited |
| **Daily** | WebRTC Transport | Per minute | 10k mins/month free |

### Optional (Enhanced)

| Service | Purpose | When to Use |
|---------|---------|-------------|
| ElevenLabs | Premium TTS | Better voice quality |
| Anthropic | Claude LLM | Alternative to OpenAI |
| Gladia | Alternative STT | Deepgram alternative |

### Cost Estimation (Per Hour of Usage)

| Service | Unit Cost | Est. Usage/Hour | Cost/Hour |
|---------|-----------|-----------------|-----------|
| Deepgram Nova 3 | $0.0043/min | 30 min audio | $0.13 |
| OpenAI GPT-4o | $5/1M tokens | 50k tokens | $0.25 |
| Cartesia | $0.30/1M chars | 20k chars | $0.006 |
| Daily | Free tier | 60 min | $0.00 |
| **Total** | | | **~$0.40/hour** |

---

## Risk Assessment

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Service outages | Medium | High | Implement fallback providers |
| Latency issues | Medium | Medium | Optimize pipeline, use streaming |
| Context limits | Low | Medium | Implement context windowing |
| Audio quality | Medium | Medium | Support multiple input devices |

### Business Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| API cost overruns | Medium | Medium | Implement usage limits, monitoring |
| Vendor lock-in | Low | Medium | Abstract provider interfaces |
| Privacy concerns | Medium | High | Document data handling, offer local options |

---

## Success Metrics

### MVP Success Criteria

1. **Functionality**: Voice bot can execute all core JP Flowspec operations
2. **Latency**: End-to-end response < 2 seconds
3. **Reliability**: 95%+ successful interactions
4. **Usability**: Users can complete SDD workflow entirely by voice

### Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time to first byte (TTS) | < 500ms | Pipecat metrics |
| End-to-end latency | < 2s | User perception test |
| Transcription accuracy | > 95% | Manual sampling |
| Task completion rate | > 90% | User testing |

---

## Research Spikes Required

Before implementation, complete these research spikes:

### Spike 1: Pipecat Hello World (1 day)
- Clone pipecat-quickstart
- Run locally with Deepgram/OpenAI/Cartesia
- Document setup steps and gotchas

### Spike 2: Function Calling POC (2 days)
- Implement simple function (e.g., get_weather)
- Test function invocation from voice
- Document patterns and limitations

### Spike 3: Transport Options Evaluation (1 day)
- Test Daily WebRTC vs WebSocket
- Evaluate latency and complexity tradeoffs
- Recommend transport for MVP

### Spike 4: Provider Comparison (2 days)
- Test Deepgram vs OpenAI Whisper vs Gladia
- Test Cartesia vs ElevenLabs vs OpenAI TTS
- Document quality/latency/cost tradeoffs

---

## References

### Official Documentation
- [Pipecat Documentation](https://docs.pipecat.ai)
- [Pipecat GitHub](https://github.com/pipecat-ai/pipecat)
- [Pipecat Quickstart](https://github.com/pipecat-ai/pipecat-quickstart)

### Provider Documentation
- [Deepgram Docs](https://developers.deepgram.com/)
- [OpenAI API](https://platform.openai.com/docs)
- [Cartesia Docs](https://docs.cartesia.ai/)
- [Daily Docs](https://docs.daily.co/)

### Video Resources
- [AI Assisted Development Workflow Demo](https://www.youtube.com/watch?v=AG68VC_mOGY) - Demonstrates Pipecat with custom configuration

### Related Projects
- [Pipecat Flows](https://github.com/pipecat-ai/pipecat-flows) - Structured conversation management
- [Voice UI Kit](https://github.com/pipecat-ai/voice-ui-kit) - Pre-built UI components

---

## Next Steps

1. **Create backlog tasks** from this document using `/flow:tasks`
2. **Execute research spikes** to validate assumptions
3. **Begin Phase 1 implementation** after spike completion
4. **Track progress** via backlog board

---

## Appendix A: Demo Transcript Key Insights

From the YouTube demo transcript, key learnings for our implementation:

### Context Management
> "The missing piece is really the workflow that you build around them, which is where you teach it your own development processes."

**Implication**: Our voice assistant needs deep context about JP Flowspec's workflow.

### Sub-Agent Pattern
> "The sub agents aren't actually implementation sub agents. They are research sub agents. The idea is they're providing their recommendations to the main orchestrating agent."

**Implication**: Consider voice-driven research agents that gather information before acting.

### Configuration Architecture
> "I want there to be two main nodes. One for the assistant behavior such as the system prompt, first message, last message, and the assistant name. And there'll be another node for the technical pipeline configuration."

**Implication**: Separate assistant config from pipeline config in our JSON schema.

### Iterative Refinement
> "I like to see basically what the AI comes up with and then correct it. And then in doing this correction, I find that I naturally sort of explain where I want to get to with this project."

**Implication**: Design voice interactions to be conversational and iterative.

---

## Appendix B: Sample Voice Interaction Flows

### Flow 1: Creating a New Specification

```
User: "I want to create a specification for a user authentication system"

Bot: "Great! Let me help you create a specification for user authentication.
      What authentication methods should we support? For example,
      email/password, social login, or multi-factor authentication?"

User: "Email and password with optional two-factor auth"

Bot: "Got it. Should we include password reset functionality and
      account lockout after failed attempts?"

User: "Yes, both of those"

Bot: "I'll create the specification now."
     [Executes run_specify_command]
     "Done! I've created spec.md with user stories for email/password login,
      two-factor authentication, password reset, and account lockout.
      Would you like me to read the key requirements?"

User: "Yes please"

Bot: "The specification includes 4 user stories: As a user, I can register
      with email and password. As a user, I can enable two-factor
      authentication for additional security..."
```

### Flow 2: Checking Task Status

```
User: "What tasks are in progress?"

Bot: [Executes list_backlog_tasks with status="In Progress"]
     "You have 3 tasks in progress: Task 15, implementing the login API.
      Task 18, creating the authentication middleware. And Task 22,
      writing unit tests for the user service. Would you like details
      on any of these?"

User: "Mark task 15 as done"

Bot: [Executes update_task_status]
     "Done! Task 15 is now marked as complete. You now have 2 tasks
      in progress."
```

---

*Document Version: 1.0*
*Last Updated: 2025-11-28*
*Author: Claude (AI-assisted research)*
