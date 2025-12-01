#!/usr/bin/env python3
"""
API Server Startup Script

Run this to start the FastAPI server.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.api_server import run_server
from routers.router_manager import load_config


def main():
    """Main entry point for API server."""
    try:
        config = load_config()
        api_config = config.get("api", {})
        
        host = api_config.get("host", "0.0.0.0")
        port = api_config.get("port", 8000)
        
        run_server(host=host, port=port)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

