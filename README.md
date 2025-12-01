# 🤖 GPT Wrapper

A comprehensive, production-ready Python wrapper for routing prompts between OpenAI API and local LLM models (via Ollama). Features session memory, vector-based semantic search, voice I/O, image generation, web UI, and REST API.

## 📋 Features

### ✅ Current Features (All Milestones Complete!)
- **Multi-Model Routing**: Switch between OpenAI API and local Ollama models via configuration
- **Session Memory**: Save conversation history to JSONL files with context loading
- **Vector Memory**: Embedding-based semantic search with ChromaDB for intelligent context retrieval
- **Interactive Chat Mode**: Continuous conversation with `/exit` or `/quit` support
- **Voice Support**: Text-to-speech (TTS) and speech-to-text (STT) using OpenAI APIs
- **Image Generation**: DALL-E 2 and DALL-E 3 integration for text-to-image generation
- **Web UI**: Beautiful Streamlit interface for all features
- **REST API**: FastAPI server with comprehensive endpoints
- **CLI Interface**: Full-featured command-line with flags for all features
- **Modular Architecture**: Clean separation of concerns for easy extension
- **YAML Configuration**: Simple toggle between models and features without code changes
- **Comprehensive Logging**: Track all operations with detailed logs
- **Error Handling**: Robust error management for API failures
- **Setup Validation**: Test all routes and features with detailed diagnostics

## 🏗️ Architecture

```
User Input
    ↓
[Router Manager] ← reads config
    ↓
┌─────────────┬─────────────┐
│  OpenAI API │  Ollama LLM │
└─────────────┴─────────────┘
    ↓
Response Return
```

See [docs/system_overview.md](docs/system_overview.md) for detailed architecture documentation.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- For OpenAI: API key from [OpenAI Platform](https://platform.openai.com/)
- For Local: [Ollama](https://ollama.ai/) installed and running

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd gpt-wrapper
```

2. **Create a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure API keys**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

5. **Configure model settings**
Edit `src/config/settings.yaml` to choose your model:
```yaml
active_model: openai  # or 'local' for Ollama
```

### Running with OpenAI

1. **Activate the virtual environment** (if not already activated):
```bash
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

2. Make sure your OpenAI API key is set in `.env` or `src/config/settings.yaml`

3. Run the wrapper:
```bash
python src/main.py "What is the capital of France?"
# Or use python3 if python is not available:
python3 src/main.py "What is the capital of France?"
```

### Interactive Chat Mode

Start an interactive conversation session:

```bash
# Basic interactive mode
python src/main.py --interactive

# With session memory (saves conversation history)
python src/main.py --session-id my-chat --interactive

# Exit interactive mode by typing /exit or /quit
```

### Session Memory

Enable memory in `src/config/settings.yaml`:

```yaml
memory:
  enabled: true
  max_history: 10  # Number of previous turns to load as context
  storage_path: "data/sessions"
```

Then use with a session ID:

```bash
# Single prompt with memory
python src/main.py --session-id test "What is Python?"

# Next prompt in same session (will have context)
python src/main.py --session-id test "Tell me more about it"
```

### Running with Ollama (Local)

#### Installing Ollama on Ubuntu

1. **Install Ollama using the official script:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

2. **Verify installation:**
```bash
ollama --version
```

3. **Start Ollama service (runs automatically after install, but you can verify):**
```bash
sudo systemctl status ollama
# If not running, start it with:
sudo systemctl start ollama
```

4. **Pull a model (e.g., mistral or llama2):**
```bash
ollama pull mistral
# or
ollama pull llama2
```

5. **Verify the model is available:**
```bash
ollama list
```

6. **Update `src/config/settings.yaml`:**
```yaml
active_model: local
local:
  model_name: "mistral"  # or "llama2" or any model you pulled
```

7. **Activate the virtual environment** (if not already activated):
```bash
source venv/bin/activate  # On macOS/Linux
```

8. **Run the wrapper:**
```bash
python src/main.py "Explain quantum computing in simple terms"
# Or use python3 if python is not available:
python3 src/main.py "Explain quantum computing in simple terms"
```

**Note:** On Ubuntu, Ollama runs as a system service, so you don't need to manually start `ollama serve`. The service runs automatically in the background.

## 📁 Project Structure

```
gpt-wrapper/
│
├── src/
│   ├── main.py                 # CLI entry point
│   │
│   ├── routers/                # Model routing
│   │   ├── router_manager.py   # Model selection logic
│   │   ├── openai_router.py    # OpenAI API integration
│   │   └── local_router.py     # Ollama integration
│   │
│   ├── memory/                 # Memory system
│   │   └── memory_handler.py   # Session + Vector memory
│   │
│   ├── voice/                  # Voice features
│   │   └── voice_handler.py    # TTS/STT with OpenAI
│   │
│   ├── image/                  # Image generation
│   │   └── image_handler.py    # DALL-E integration
│   │
│   ├── api/                    # Web services
│   │   ├── api_server.py       # FastAPI REST server
│   │   ├── web_ui.py           # Streamlit web interface
│   │   └── server.py           # API server entry point
│   │
│   ├── config/
│   │   └── settings.yaml       # Configuration file
│   │
│   └── utils/
│       └── logger.py           # Logging utility
│
├── data/                       # Generated data (gitignored)
│   ├── sessions/               # Session memory files
│   ├── images/                 # Generated images
│   ├── voice_output/           # Audio files
│   └── chroma_db/              # Vector database
│
├── docs/
│   └── system_overview.md      # Architecture documentation
│
├── run_api.sh                  # API server startup script
├── run_web_ui.sh               # Web UI startup script
├── .env.example                # API key template
├── requirements.txt            # Python dependencies
├── validate_setup.py           # Setup validation script
├── README.md                   # This file
└── LICENSE                     # MIT License
```

## ⚙️ Configuration

### settings.yaml Options

**OpenAI Configuration:**
```yaml
openai:
  api_key: ""                    # Leave empty to use env var
  model: "gpt-4-turbo"          # gpt-4, gpt-3.5-turbo, etc.
  temperature: 0.7              # 0.0 to 2.0
  max_tokens: 1000              # Response length limit
```

**Ollama Configuration:**
```yaml
local:
  model_name: "llama2"          # Model name in Ollama
  host: "localhost"             # Ollama host
  port: 11434                   # Ollama port
  temperature: 0.7              # 0.0 to 2.0
```

**Memory Configuration:**
```yaml
memory:
  enabled: false                # Enable session memory
  mode: "session"               # session or vector
  max_history: 10               # Number of previous turns to load
  storage_path: "data/sessions" # Directory for session files
  vector_store: "chroma"        # chroma or pinecone (future)
  embedding_model: "all-MiniLM-L6-v2"  # Sentence transformer model
```

**Voice Configuration:**
```yaml
voice:
  enabled: false                # Enable voice features
  provider: "openai"            # openai or elevenlabs (future)
  tts_model: "tts-1"            # tts-1 or tts-1-hd
  tts_voice: "alloy"            # alloy, echo, fable, onyx, nova, shimmer
  stt_model: "whisper-1"        # Speech-to-text model
  output_dir: "data/voice_output"
```

**Image Configuration:**
```yaml
image:
  enabled: false                # Enable image generation
  provider: "dalle"             # dalle or stable-diffusion (future)
  model: "dall-e-3"             # dall-e-2 or dall-e-3
  size: "1024x1024"             # 256x256, 512x512, 1024x1024
  quality: "standard"           # standard or hd (dall-e-3 only)
  output_dir: "data/images"
```

**API Server Configuration:**
```yaml
api:
  enabled: false
  host: "0.0.0.0"
  port: 8000
```

**Web UI Configuration:**
```yaml
web_ui:
  enabled: false
  port: 8501
```

## 🧪 Usage Examples

### Command Line

```bash
# Activate virtual environment first
source venv/bin/activate

# Single-shot mode (one prompt)
python src/main.py "Write a haiku about coding"
# Or: python3 src/main.py "Write a haiku about coding"

# Interactive chat mode
python src/main.py --interactive

# Interactive mode with session memory
python src/main.py --session-id my-session --interactive

# Single prompt with session memory
python src/main.py --session-id my-session "What is machine learning?"
python src/main.py --session-id my-session "Tell me more about it"  # Has context!
```

### Interactive Mode Commands

Once in interactive mode, you can:
- Type your message and press Enter
- Type `/exit` or `/quit` to end the session
- Press `Ctrl+C` to interrupt and exit

### Image Generation

```bash
# Enable image generation in settings.yaml first (image.enabled: true)
python src/main.py --image "A beautiful sunset over mountains"

# Images are saved to data/images/ directory
```

### Voice Features

```bash
# Text-to-speech (enable voice in settings.yaml first)
python src/main.py --tts "Hello, this is a test"

# Speech-to-text (transcribe an audio file)
python src/main.py --stt audio.wav
```

### Web UI

```bash
# Start the Streamlit web interface
./run_web_ui.sh
# Or manually:
streamlit run src/api/web_ui.py --server.port 8501

# Open http://localhost:8501 in your browser
# Features: Chat, image generation, voice playback, session management
```

### REST API Server

```bash
# Start the FastAPI server
./run_api.sh
# Or manually:
python src/api/server.py

# API documentation available at http://localhost:8000/docs
# Test with curl:
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello!", "session_id": "test"}'

# Generate image via API:
curl -X POST "http://localhost:8000/api/image/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A beautiful landscape"}'
```

### Python Script

```python
from src.routers.router_manager import route_prompt

prompt = "Explain the theory of relativity"
response, model_name = route_prompt(prompt)
print(response)
```

## 🧪 Smoke Tests

Quick verification tests to ensure both routes are working correctly:

### Test 1: OpenAI Route

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Set active model to OpenAI
sed -i '' 's/active_model:.*/active_model: openai/' src/config/settings.yaml  # macOS
# or on Linux: sed -i 's/active_model:.*/active_model: openai/' src/config/settings.yaml

# Run test prompt
python src/main.py "Say 'OpenAI route working' if you can read this"

# Expected: Response from OpenAI API confirming it received the message
```

### Test 2: Ollama Route

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Ensure Ollama is running and has a model
ollama list

# Set active model to local
sed -i '' 's/active_model:.*/active_model: local/' src/config/settings.yaml  # macOS
# or on Linux: sed -i 's/active_model:.*/active_model: local/' src/config/settings.yaml

# Run test prompt
python src/main.py "Say 'Ollama route working' if you can read this"

# Expected: Response from local Ollama model confirming it received the message
```

**Quick Toggle Script:**
```bash
# Switch to OpenAI (macOS)
sed -i '' 's/active_model:.*/active_model: openai/' src/config/settings.yaml && echo "Switched to OpenAI"
# On Linux: sed -i 's/active_model:.*/active_model: openai/' src/config/settings.yaml && echo "Switched to OpenAI"

# Switch to Ollama (macOS)
sed -i '' 's/active_model:.*/active_model: local/' src/config/settings.yaml && echo "Switched to Ollama"
# On Linux: sed -i 's/active_model:.*/active_model: local/' src/config/settings.yaml && echo "Switched to Ollama"
```

## 🔧 Troubleshooting

**OpenAI Issues:**
- Verify API key is correctly set
- Check your OpenAI account has credits
- Ensure model name is valid (gpt-4-turbo, gpt-4, etc.)

**Ollama Issues:**
- Verify Ollama is running: `ollama list`
- Check the model is downloaded: `ollama pull llama2`
- Ensure port 11434 is not blocked
- Try: `curl http://localhost:11434/api/generate -d '{"model":"llama2","prompt":"test"}'`

## 🗺️ Roadmap

- [x] **Milestone 1**: Core routing between OpenAI and Ollama
- [x] **Milestone 1.5**: Session memory and interactive chat mode
- [x] **Milestone 2**: Vector-based embedding memory system (ChromaDB + sentence-transformers)
- [x] **Milestone 3**: Voice input/output integration (OpenAI Whisper + TTS)
- [x] **Milestone 4**: Image generation capabilities (DALL-E integration)
- [x] **Milestone 5**: Web interface (Streamlit) and API server (FastAPI)

All milestones are now complete! 🎉

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 Additional Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [System Architecture](docs/system_overview.md)

## 🙏 Acknowledgments

Built with:
- OpenAI API for cloud-based LLMs
- Ollama for local LLM inference
- Python ecosystem for rapid development

