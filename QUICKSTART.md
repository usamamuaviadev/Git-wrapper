# 🚀 Quick Start Guide

Get up and running with GPT Wrapper in 5 minutes!

## 📦 Installation Steps

### 1. Set up Python Environment

```bash
# Navigate to project directory
cd gpt-wrapper

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

Create a `.env` file in the project root:

```bash
# Create .env file
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

Or edit `src/config/settings.yaml` directly:

```yaml
openai:
  api_key: "sk-your-actual-key-here"
```

### 4. Choose Your Model

Edit `src/config/settings.yaml`:

```yaml
active_model: openai  # Use 'openai' or 'local'
```

## 🎯 Testing OpenAI

### Single-Shot Mode

```bash
# Simple test
python src/main.py "What is AI?"
```

Expected output:
```
🌐 Routing to OpenAI (gpt-4-turbo)...
================================================================================
RESPONSE:
================================================================================
[AI explanation from GPT-4]
================================================================================
```

### Interactive Mode

```bash
# Start interactive chat
python src/main.py --interactive

# With session memory
python src/main.py --session-id my-chat --interactive
```

In interactive mode:
- Type your messages and press Enter
- Type `/exit` or `/quit` to end the session
- Press `Ctrl+C` to interrupt and exit

## 🖥️ Testing Ollama (Local)

### Step 1: Install Ollama

```bash
# macOS
brew install ollama

# Linux
curl https://ollama.ai/install.sh | sh

# Windows: Download from ollama.ai
```

### Step 2: Pull a Model

```bash
ollama pull llama2
# or
ollama pull mistral
# or
ollama pull codellama
```

### Step 3: Start Ollama Server

```bash
ollama serve
```

### Step 4: Update Configuration

Edit `src/config/settings.yaml`:

```yaml
active_model: local

local:
  model_name: "llama2"  # Match the model you pulled
  port: 11434
```

### Step 5: Test

```bash
python src/main.py "Explain machine learning"
```

Expected output:
```
🖥️  Routing to Local Ollama (llama2)...
================================================================================
RESPONSE:
================================================================================
[Explanation from Llama2]
================================================================================
```

## 🔄 Switching Between Models

Just change one line in `src/config/settings.yaml`:

```yaml
active_model: openai  # Switch to OpenAI
# or
active_model: local   # Switch to Ollama
```

No code changes needed!

## 💾 Using Session Memory

### Enable Memory

Edit `src/config/settings.yaml`:

```yaml
memory:
  enabled: true
  max_history: 10  # Load last 10 turns as context
  storage_path: "data/sessions"
```

### Use with Session ID

```bash
# First prompt
python src/main.py --session-id my-session "What is Python?"

# Second prompt (has context from first)
python src/main.py --session-id my-session "Give me an example"

# Interactive mode with memory
python src/main.py --session-id my-session --interactive
```

Session files are saved to `data/sessions/{session-id}.jsonl`

## 🧪 Validation Checklist

Use this checklist to validate your setup:

- [ ] Python virtual environment activated
- [ ] Dependencies installed (`pip list` shows openai, requests, pyyaml)
- [ ] `.env` file created with OpenAI API key (for OpenAI)
- [ ] Ollama installed and running (for local)
- [ ] Model downloaded in Ollama (for local)
- [ ] `settings.yaml` configured with correct model choice
- [ ] Test prompt runs successfully
- [ ] Can switch between models by editing config
- [ ] Interactive mode works (`python src/main.py --interactive`)
- [ ] Session memory works (if enabled)

### Run Setup Validation

For a comprehensive check, run the validation script:

```bash
python validate_setup.py
```

This will test:
- Python environment
- Dependencies
- Configuration file
- API keys
- Route connectivity (OpenAI and Ollama)
- Module imports

## 🐛 Common Issues

### "OpenAI API key not found"
- Check `.env` file exists and contains valid key
- Or add key to `src/config/settings.yaml`
- Verify no extra spaces or quotes around key

### "Could not connect to Ollama"
- Run `ollama serve` in another terminal
- Check Ollama is running: `curl http://localhost:11434/api/version`
- Verify port 11434 is not blocked

### "Model not found" (Ollama)
- Pull the model: `ollama pull llama2`
- List available models: `ollama list`
- Update `model_name` in settings.yaml

### Import errors
- Activate virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

## 📚 Next Steps

1. **Explore different models**: Try gpt-4, gpt-3.5-turbo, mistral, etc.
2. **Adjust parameters**: Modify temperature, max_tokens in settings.yaml
3. **Review architecture**: Read `docs/system_overview.md`
4. **Plan integrations**: Memory, voice, and image features coming soon!

## 💡 Pro Tips

- Use `gpt-3.5-turbo` for faster, cheaper responses
- Use `gpt-4-turbo` for complex reasoning tasks
- Use local models for privacy and offline work
- Check logs for debugging (timestamps and error details)

---

**Need help?** Check the main [README.md](README.md) or [system_overview.md](docs/system_overview.md)

