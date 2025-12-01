#!/bin/bash
# Web UI startup script

cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null || true

echo "🚀 Starting GPT Wrapper Web UI..."
echo "📝 Make sure voice, image, and memory features are enabled in src/config/settings.yaml if you want to use them"
echo ""

# Check if streamlit is installed
python -c "import streamlit" 2>/dev/null || {
    echo "❌ Streamlit not installed. Installing..."
    pip install streamlit
}

streamlit run src/api/web_ui.py --server.port 8501

