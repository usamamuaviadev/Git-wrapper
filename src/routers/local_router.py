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
        
        if "error" in result:
            raise Exception(f"Ollama API error: {result['error']}")
        
        response_text = result.get("response", "")
        if not response_text:
            raise Exception("Ollama returned empty response. Check if the model is loaded correctly.")
        
        return response_text.strip()
    
    except requests.exceptions.ConnectionError:
        raise Exception(
            f"Could not connect to Ollama at {host}:{port}. "
            "Make sure Ollama is running:\n"
            "  - On Linux/macOS: ollama serve\n"
            "  - On Ubuntu: sudo systemctl start ollama\n"
            "  - Verify with: curl http://localhost:11434/api/tags"
        )
    except requests.exceptions.Timeout:
        raise Exception(
            "Ollama request timed out after 120 seconds. "
            "Try a shorter prompt or check your system resources. "
            "Large models may need more time."
        )
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise Exception(
                f"Model '{model_name}' not found in Ollama. "
                f"Available models: ollama list\n"
                f"Pull the model with: ollama pull {model_name}"
            )
        else:
            raise Exception(f"Ollama HTTP error {e.response.status_code}: {str(e)}")
    except Exception as e:
        raise Exception(f"Ollama error: {str(e)}")

