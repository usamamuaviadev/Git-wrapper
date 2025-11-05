# 🤖 GPT Wrapper

A modular Python wrapper for routing prompts between OpenAI API and local LLM models (via Ollama), with plans for memory, voice, and image generation integration.

## 📋 Features

### ✅ Current (Milestone 1)
- **Multi-Model Routing**: Switch between OpenAI API and local Ollama models via configuration
- **Modular Architecture**: Clean separation of concerns for easy extension
- **YAML Configuration**: Simple toggle between models without code changes
- **Comprehensive Logging**: Track all operations with detailed logs
- **Error Handling**: Robust error management for API failures

### 🚧 Planned (Future Milestones)
- **Embedding-Based Memory**: Context-aware conversations using vector databases
- **Voice Integration**: Text-to-speech and speech-to-text capabilities
- **Image Generation**: DALL-E and other image generation providers
- **Web UI**: User-friendly interface for interaction
- **API Server**: RESTful API for integration with other applications

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

1. Make sure your OpenAI API key is set in `.env` or `src/config/settings.yaml`
2. Run the wrapper:
```bash
python src/main.py "What is the capital of France?"
```

Or use interactive mode:
```bash
python src/main.py
# Then enter your prompt when asked
```

### Running with Ollama (Local)

1. Install Ollama from [ollama.ai](https://ollama.ai/)

2. Pull a model (e.g., llama2):
```bash
ollama pull llama2
```

3. Start Ollama server:
```bash
ollama serve
```

4. Update `src/config/settings.yaml`:
```yaml
active_model: local
```

5. Run the wrapper:
```bash
python src/main.py "Explain quantum computing in simple terms"
```

## 📁 Project Structure

```
gpt-wrapper/
│
├── src/
│   ├── main.py                 # Entry point
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── openai_router.py    # Routes to OpenAI API
│   │   ├── local_router.py     # Routes to Ollama
│   │   └── router_manager.py   # Model selection logic
│   │
│   ├── memory/
│   │   ├── __init__.py
│   │   └── memory_handler.py   # Memory stub (future)
│   │
│   ├── config/
│   │   └── settings.yaml       # Configuration file
│   │
│   └── utils/
│       └── logger.py           # Logging utility
│
├── docs/
│   └── system_overview.md      # Architecture documentation
│
├── .env.example                # API key template
├── requirements.txt            # Python dependencies
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

## 🧪 Usage Examples

### Command Line

```bash
# Single prompt
python src/main.py "Write a haiku about coding"

# Interactive mode
python src/main.py
```

### Python Script

```python
from src.routers.router_manager import route_prompt

prompt = "Explain the theory of relativity"
response = route_prompt(prompt)
print(response)
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
- [ ] **Milestone 2**: Embedding-based memory system
- [ ] **Milestone 3**: Voice input/output integration
- [ ] **Milestone 4**: Image generation capabilities
- [ ] **Milestone 5**: Web interface and API server

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

