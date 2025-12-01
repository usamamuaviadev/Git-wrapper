# 🏗️ System Overview - GPT Wrapper

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                           │
│                    (CLI / Script / Future: Web/API)              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │   main.py      │
                    │  Entry Point   │
                    └────────┬───────┘
                             │
                             ▼
              ┌───────────────────────────────┐
              │    Router Manager             │
              │  • Loads config (settings.yaml)│
              │  • Model selection logic      │
              │  • Routes to appropriate API  │
              └───────────┬───────────────────┘
                          │
            ┌─────────────┼─────────────┐
            │             │             │
            ▼             ▼             ▼
      ┌──────────┐  ┌──────────┐  ┌──────────┐
      │ OpenAI   │  │  Ollama  │  │  Future  │
      │ Router   │  │  Router  │  │ Providers│
      └────┬─────┘  └────┬─────┘  └──────────┘
           │             │
           ▼             ▼
      ┌──────────┐  ┌──────────┐
      │ OpenAI   │  │  Local   │
      │   API    │  │  Ollama  │
      └────┬─────┘  └────┬─────┘
           │             │
           └──────┬──────┘
                  │
                  ▼
         ┌─────────────────┐
         │   Response      │
         │   Processing    │
         └────────┬────────┘
                  │
        ┌─────────┼─────────┐
        │         │         │
        ▼         ▼         ▼
   ┌────────┐ ┌──────┐ ┌────────┐
   │ Memory │ │Voice │ │ Image  │
   │ Layer  │ │Layer │ │ Layer  │
   └────────┘ └──────┘ └────────┘
        │         │         │
        ▼         ▼         ▼
   ┌────────┐ ┌──────┐ ┌────────┐
   │ Vector │ │TTS/  │ │Storage │
   │  DB    │ │STT   │ │ & CDN  │
   └────────┘ └──────┘ └────────┘
```

## System Layers

### 🔌 **Router Layer** (Current - Milestone 1)
- **Purpose**: Route prompts to appropriate LLM provider
- **Components**:
  - `router_manager.py`: Central routing logic, config loading
  - `openai_router.py`: OpenAI API integration
  - `local_router.py`: Ollama HTTP API integration
- **Configuration**: YAML-based model selection (`settings.yaml`)
- **Status**: ✅ Fully implemented

### 🧠 **Memory Layer** (Planned - Milestone 2)
- **Purpose**: Context-aware conversations using embedding-based semantic search
- **Components**:
  - `memory_handler.py`: Memory management interface (stub)
  - Embedding generation: sentence-transformers
  - Vector database: ChromaDB or Pinecone
- **Features**:
  - Store conversation history with embeddings
  - Retrieve relevant context for improved responses
  - Semantic search across past interactions
  - Configurable context window (top_k retrieval)
- **Status**: 🚧 Stub implemented, full integration pending

### 🎤 **Voice Layer** (Planned - Milestone 3)
- **Purpose**: Speech-to-text and text-to-speech capabilities
- **Components**:
  - Speech-to-Text: OpenAI Whisper API or local Whisper
  - Text-to-Speech: ElevenLabs, Azure Cognitive Services, or local TTS
  - Audio processing pipeline
- **Features**:
  - Voice input via microphone
  - Audio output via speakers
  - Multi-language support
  - Voice cloning (future)
- **Status**: 🚧 Planned

### 🎨 **Image Layer** (Planned - Milestone 4)
- **Purpose**: Text-to-image generation and image processing
- **Components**:
  - DALL-E integration (OpenAI)
  - Stable Diffusion (local/API)
  - Image storage and CDN
  - Image post-processing
- **Features**:
  - Generate images from text prompts
  - Image editing and manipulation
  - Batch generation
  - Image retrieval and storage
- **Status**: 🚧 Planned

### ⚙️ **Policy Layer** (Planned - Future)
- **Purpose**: Governance, rate limiting, and usage policies
- **Components**:
  - Rate limiting per user/model
  - Cost tracking and budgets
  - Content filtering and moderation
  - Usage analytics and reporting
  - Access control and authentication
- **Features**:
  - Token usage tracking
  - Cost per request monitoring
  - Request throttling
  - Policy enforcement engine
- **Status**: 🚧 Planned

## Data Flow

1. **User Input** → CLI argument or interactive prompt
2. **Router Manager** → Reads `settings.yaml`, selects model
3. **Model Router** → Formats request, calls API (OpenAI/Ollama)
4. **Response** → Raw model output returned
5. **Post-Processing** → (Future) Memory storage, voice synthesis, image generation
6. **Output** → Formatted response to user

## Configuration Hierarchy

```
settings.yaml (primary)
    ↓
Environment Variables (.env)
    ↓
Code Defaults (fallback)
```

## Current Status

| Layer | Status | Implementation |
|-------|--------|----------------|
| Router | ✅ Complete | OpenAI + Ollama routing |
| Memory | 🚧 Stub | Placeholder class ready |
| Voice | 📋 Planned | Not started |
| Image | 📋 Planned | Not started |
| Policy | 📋 Planned | Not started |

## Technology Stack

- **Core**: Python 3.8+
- **LLM APIs**: OpenAI SDK, Ollama HTTP API
- **Config**: YAML (PyYAML)
- **Logging**: Python logging module
- **Future**: sentence-transformers, ChromaDB, ElevenLabs SDK

---

**Version**: 0.1.0 (Milestone 1)  
**Last Updated**: 2025
