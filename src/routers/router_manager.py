"""
Router Manager

Decides which model to call based on configuration settings.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any

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


def route_prompt(prompt: str) -> str:
    """
    Route the prompt to the appropriate model based on configuration.
    
    Args:
        prompt: The user's input prompt
        
    Returns:
        The model's response as a string
        
    Raises:
        ValueError: If an invalid model is specified in config
        Exception: If the model query fails
    """
    config = load_config()
    
    active_model = config.get("active_model", "openai")
    
    if active_model == "openai":
        print(f"🌐 Routing to OpenAI ({config['openai']['model']})...")
        return query_openai(prompt, config["openai"])
    elif active_model == "local":
        print(f"🖥️  Routing to Local Ollama ({config['local']['model_name']})...")
        return query_ollama(prompt, config["local"])
    else:
        raise ValueError(
            f"Invalid model '{active_model}' specified in config file. "
            "Valid options are: 'openai' or 'local'"
        )

