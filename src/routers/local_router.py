"""
Local Router

Routes text to local Ollama instance and handles responses.
"""

import requests
from typing import Dict, Any


def query_ollama(prompt: str, config: Dict[str, Any]) -> str:
    """
    Send a prompt to local Ollama instance and return the response.
    
    Args:
        prompt: The user's input prompt
        config: Configuration dictionary with Ollama settings
        
    Returns:
        The model's response as a string
        
    Raises:
        Exception: If Ollama is not running or request fails
    """
    model_name = config.get("model_name", "llama2")
    port = config.get("port", 11434)
    host = config.get("host", "localhost")
    temperature = config.get("temperature", 0.7)
    
    url = f"http://{host}:{port}/api/generate"
    
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        return result.get("response", "").strip()
    
    except requests.exceptions.ConnectionError:
        raise Exception(
            f"Could not connect to Ollama at {host}:{port}. "
            "Make sure Ollama is running (try: ollama serve)"
        )
    except requests.exceptions.Timeout:
        raise Exception("Ollama request timed out. Try a shorter prompt or check your system resources.")
    except Exception as e:
        raise Exception(f"Ollama error: {str(e)}")

