"""
Router Manager

Decides which model to call based on configuration settings.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from .openai_router import query_openai
from .local_router import query_ollama


def load_config() -> Dict[str, Any]:
    """Load configuration from settings.yaml file."""
    config_path = Path(__file__).parent.parent / "config" / "settings.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found at {config_path}. "
            "Please create src/config/settings.yaml"
        )
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    return config


def route_prompt(
    prompt: str, 
    session_id: Optional[str] = None,
    context: Optional[str] = None
) -> Tuple[str, str]:
    """
    Route the prompt to the appropriate model based on configuration.
    
    Args:
        prompt: The user's input prompt
        session_id: Optional session ID for memory tracking (unused in router, passed for compatibility)
        context: Optional context string to prepend to prompt
        
    Returns:
        Tuple of (response, model_name) where response is the model's response
        and model_name is the name of the model used
        
    Raises:
        ValueError: If an invalid model is specified in config
        Exception: If the model query fails
    """
    config = load_config()
    
    active_model = config.get("active_model", "openai")
    
    # Prepend context if provided
    full_prompt = prompt
    if context:
        full_prompt = f"{context}\n\nCurrent request: {prompt}"
    
    if active_model == "openai":
        model_name = config['openai'].get('model', 'gpt-4-turbo')
        print(f"🌐 Routing to OpenAI ({model_name})...")
        response = query_openai(full_prompt, config["openai"])
        return response, model_name
    elif active_model == "local":
        model_name = config['local'].get('model_name', 'llama2')
        print(f"🖥️  Routing to Local Ollama ({model_name})...")
        response = query_ollama(full_prompt, config["local"])
        return response, model_name
    else:
        raise ValueError(
            f"Invalid model '{active_model}' specified in config file. "
            "Valid options are: 'openai' or 'local'"
        )

