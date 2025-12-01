#!/bin/bash
# API Server startup script

cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null || true

echo "🚀 Starting GPT Wrapper API Server..."
echo "📝 API docs will be available at http://localhost:8000/docs"
echo ""

# Check if fastapi/uvicorn are installed
python -c "import fastapi, uvicorn" 2>/dev/null || {
    echo "❌ FastAPI/uvicorn not installed. Installing..."
    pip install fastapi uvicorn[standard] python-multipart
}

python src/api/server.py

